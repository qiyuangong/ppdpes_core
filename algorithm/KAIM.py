"""
main module for cluster_based_k_anon
"""
#!/usr/bin/env python
#coding=utf-8

try:
    from models.numrange import NumRange
    from models.gentree import GenTree
    from utils.utility import get_num_list_from_str, cmp_str, list_to_str
except ImportError:
    from ..models.numrange import NumRange
    from ..models.gentree import GenTree
    from ..utils.utility import get_num_list_from_str, cmp_str, list_to_str
import random
import time
import math
import pdb


__DEBUG = True
# att_tree store root node for each att
ATT_TREES = []
# databack store all reacord for dataset
LEN_DATA = 0
QI_LEN = 0
QI_RANGE = []
IS_CAT = []
# get_LCA, middle and NCP require huge running time, while most of the function are duplicate
# we can use cache to reduce the running time
LCA_CACHE = []
SUPPORTS = []
NCP_CACHE = {}


class Cluster(object):

    """Cluster is for cluster based k-anonymity
    middle denote generlized value for one cluster
    self.member: record list in cluster
    self.middle: middle node in cluster
    """

    def __init__(self, member, middle, information_loss=0.0):
        self.information_loss = information_loss
        self.member = member
        self.middle = middle[:]

    def add_record(self, record):
        """
        add record to cluster
        """
        self.member.append(record)
        self.update_middle(record)

    def update_middle(self, merge_middle):
        """
        update middle and information_loss after adding record or merging cluster
        :param merge_middle:
        :return:
        """
        self.middle = middle(self.middle, merge_middle)
        self.information_loss = len(self.member) * NCP(self.middle)

    def add_same_record(self, record):
        """
        add record with same qid to cluster
        """
        self.member.append(record)

    def merge_cluster(self, cluster):
        """merge cluster into self and do not delete cluster elements.
        update self.middle with middle
        """
        self.member.extend(cluster.member)
        self.update_middle(cluster.middle)

    def __getitem__(self, item):
        """
        :param item: index number
        :return: middle[item]
        """
        return self.middle[item]

    def __len__(self):
        """
        return number of records in cluster
        """
        return len(self.member)


def r_distance(source, target):
    """
    Return distance between source (cluster or record)
    and target (cluster or record). The distance is based on
    NCP (Normalized Certainty Penalty) on relational part.
    If source or target are cluster, func need to multiply
    source_len (or target_len).
    """
    source_mid = source
    target_mid = target
    source_len = 1
    target_len = 1
    # check if target is Cluster
    if isinstance(target, Cluster):
        target_mid = target.middle
        target_len = len(target)
    # check if souce is Cluster
    if isinstance(source, Cluster):
        source_mid = source.middle
        source_len = len(source)
    if source_mid == target_mid:
        return 0
    mid = middle(source_mid, target_mid)
    # len should be taken into account
    distance = (source_len + target_len) * NCP(mid)
    return distance


def diff_distance(record, cluster):
    """
    Return IL(cluster and record) - IL(cluster).
    """
    mid_after = middle(record, cluster.middle)
    return NCP(mid_after) * (len(cluster) + 1) - cluster.information_loss


def entropy_value(index, value):
    entropy = 0
    if IS_CAT[index]:
        if value == '*':
            temp = ATT_TREES[index].value

        else:
            temp = value.split(',')
        if len(temp) == 1:
            return 0
        low, high = temp[0], temp[1]
        for curr_num in range(int(low), int(high) + 1):
            try:
                p = SUPPORTS[index][str(curr_num)]
                entropy += abs(p * math.log10(p))
            except KeyError:
                pass
    else:
        if len(ATT_TREES[index][value]) == 0:
            return 0
        for leaf in ATT_TREES[index][value].cover.keys():
            try:
                p = SUPPORTS[index][leaf]
                entropy += abs(p * math.log10(p))
            except KeyError:
                pass
    return entropy


def entropy_diff(record, gen_record):
    entropy = 0
    for index in range(QI_LEN):
        v, v1 = record[index], gen_record[index]
        p = SUPPORTS[index][v]
        c = abs(p * math.log10(p))
        info_v1 = entropy_value(index, v1)
        info_v = entropy_value(index, v)
        entropy += info_v1 / (info_v + c)
    return entropy


def entropy_distance(record, cluster):
    mid_after = middle(record, cluster.middle)
    return entropy_diff(record, mid_after) +\
        len(cluster) * entropy_diff(cluster.middle, mid_after)


def NCP(mid):
    """Compute NCP (Normalized Certainty Penalty)
    when generate record to middle.
    """
    ncp = 0.0
    # exclude SA values(last one type [])
    list_key = list_to_str(mid)
    try:
        return NCP_CACHE[list_key]
    except KeyError:
        pass
    for i in range(QI_LEN):
        # if leaf_num of numerator is 1, then NCP is 0
        width = 0.0
        if IS_CAT[i] is False:
            try:
                float(mid[i])
            except ValueError:
                temp = mid[i].split(',')
                width = float(temp[1]) - float(temp[0])
        else:
            width = len(ATT_TREES[i][mid[i]]) * 1.0
        width /= QI_RANGE[i]
        ncp += width
    NCP_CACHE[list_key] = ncp
    return ncp


def get_LCA(index, item1, item2):
    """Get lowest commmon ancestor (including themselves)"""
    # get parent list from
    if item1 == item2:
        return item1
    try:
        return LCA_CACHE[index][item1 + item2]
    except KeyError:
        pass
    parent1 = ATT_TREES[index][item1].parent[:]
    parent2 = ATT_TREES[index][item2].parent[:]
    parent1.insert(0, ATT_TREES[index][item1])
    parent2.insert(0, ATT_TREES[index][item2])
    min_len = min(len(parent1), len(parent2))
    last_LCA = parent1[-1]
    # note here: when trying to access list reversely, take care of -0
    for i in range(1, min_len + 1):
        if parent1[-i].value == parent2[-i].value:
            last_LCA = parent1[-i]
        else:
            break
    LCA_CACHE[index][item1 + item2] = last_LCA.value
    return last_LCA.value


def middle(record1, record2):
    """
    Compute relational generalization result of record1 and record2
    """
    mid = []
    for i in range(QI_LEN):
        if IS_CAT[i] is False:
            split_number = []
            split_number.extend(get_num_list_from_str(record1[i]))
            split_number.extend(get_num_list_from_str(record2[i]))
            split_number = list(set(split_number))
            if len(split_number) == 1:
                mid.append(split_number[0])
            else:
                split_number.sort(cmp=cmp_str)
                mid.append(split_number[0] + ',' + split_number[-1])
        else:
            mid.append(get_LCA(i, record1[i], record2[i]))
    return mid


def middle_for_cluster(records):
    """
    calculat middle of records(list) recursively.
    Compute both relational middle for records (list).
    """
    len_r = len(records)
    mid = records[0]
    for i in range(1, len_r):
        mid = middle(mid, records[i])
    return mid


def find_best_cluster_kmember(record, clusters):
    """residual assignment. Find best cluster for record."""
    min_diff = 1000000000000
    min_index = 0
    best_cluster = clusters[0]
    for i, t in enumerate(clusters):
        IF_diff = diff_distance(record, t)
        if IF_diff < min_diff:
            min_distance = IF_diff
            min_index = i
            best_cluster = t
    # add record to best cluster
    return min_index


def find_furthest_record(record, data):
    """
    :param record: the latest record be added to cluster
    :param data: remain records in data
    :return: the index of the furthest record from r_index
    """
    max_distance = 0
    max_index = -1
    for index in range(len(data)):
        current_distance = r_distance(record, data[index])
        if current_distance >= max_distance:
            max_distance = current_distance
            max_index = index
    return max_index


def find_best_record(cluster, data):
    """
    :param cluster: current
    :param data: remain dataset
    :return: index of record with min diff on information loss
    """
    # pdb.set_trace()
    min_diff = 1000000000000
    min_index = 0
    for index, record in enumerate(data):
        # IF_diff = diff_distance(record, cluster)
        # IL(cluster and record) and |cluster| + 1 is a constant
        # so IL(record, cluster.middle) is enough
        IF_diff = NCP(middle(record, cluster.middle))
        if IF_diff < min_diff:
            min_diff = IF_diff
            min_index = index
    return min_index


def clustering_kmember(data, k=25):
    """
    Group record according to NCP. K-member
    """
    clusters = []
    # randomly choose seed and find k-1 nearest records to form cluster with size k
    r_pos = random.randrange(len(data))
    r_i = data[r_pos]
    while len(data) >= k:
        r_pos = find_furthest_record(r_i, data)
        r_i = data.pop(r_pos)
        cluster = Cluster([r_i], r_i)
        while len(cluster) < k:
            r_pos = find_best_record(cluster, data)
            r_j = data.pop(r_pos)
            cluster.add_record(r_j)
        clusters.append(cluster)
        # pdb.set_trace()
    # residual assignment
    while len(data) > 0:
        t = data.pop()
        cluster_index = find_best_cluster_kmember(t, clusters)
        clusters[cluster_index].add_record(t)
    return clusters


def init(att_trees, data, QI_num=-1):
    """
    init global variables
    """
    global ATT_TREES, DATA_BACKUP, LEN_DATA, QI_RANGE, IS_CAT, QI_LEN,\
        LCA_CACHE, NCP_CACHE, SUPPORTS
    ATT_TREES = att_trees
    QI_RANGE = []
    IS_CAT = []
    LEN_DATA = len(data)
    LCA_CACHE = []
    NCP_CACHE = {}
    if QI_num <= 0:
        QI_LEN = len(data[0]) - 1
    else:
        QI_LEN = QI_num
    SUPPORTS = [{} for _ in range(QI_LEN)]
    for i in range(QI_LEN):
        LCA_CACHE.append(dict())
        if isinstance(ATT_TREES[i], NumRange):
            IS_CAT.append(False)
            QI_RANGE.append(ATT_TREES[i].range)
        else:
            IS_CAT.append(True)
            QI_RANGE.append(len(ATT_TREES[i]['*']))


def get_support(data):
    # leaf support
    for record in data:
        for index in range(QI_LEN):
            curr_value = record[index]
            try:
                SUPPORTS[index][curr_value] += 1.0 / LEN_DATA
            except KeyError:
                SUPPORTS[index][curr_value] = 1.0 / LEN_DATA
    # parents support
    for index in range(QI_LEN):
        if IS_CAT[index] is False:
            continue
        for key, value in ATT_TREES[index].items():
            if len(value) > 0:
                support = 0
                for leaf in value.cover.keys():
                    try:
                        support += SUPPORTS[index][leaf]
                    except KeyError:
                        pass
                SUPPORTS[index][key] = support


def anon_kaim(att_trees, data, k=10, QI_num=-1):
    """
    the main function of clustering based k-anon
    """
    init(att_trees, data, QI_num)
    get_support(data)
    result = []
    start_time = time.time()
    clusters = clustering_kmember(data, k)
    rtime = float(time.time() - start_time)
    ncp = 0.0
    for cluster in clusters:
        gen_result = []
        mid = cluster.middle
        for i in range(len(cluster)):
            gen_result.append(mid + [cluster.member[i][-1]])
        result.extend(gen_result)
        ncp += cluster.information_loss
    ncp /= LEN_DATA
    ncp /= QI_LEN
    ncp *= 100
    if __DEBUG:
        print "NCP=", ncp
    return (result, (ncp, rtime))
