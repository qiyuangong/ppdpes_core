"""
main module of mondrian
"""
#!/usr/bin/env python
# coding=utf-8

# @InProceedings{LeFevre2006a,
#   Title = {Workload-aware Anonymization},
#   Author = {LeFevre, Kristen and DeWitt, David J. and Ramakrishnan, Raghu},
#   Booktitle = {Proceedings of the 12th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining},
#   Year = {2006},
#   Address = {New York, NY, USA},
#   Pages = {277--286},
#   Publisher = {ACM},
#   Series = {KDD '06},
#   Acmid = {1150435},
#   Doi = {10.1145/1150402.1150435},
#   ISBN = {1-59593-339-5},
#   Keywords = {anonymity, data recoding, predictive modeling, privacy},
#   Location = {Philadelphia, PA, USA},
#   Numpages = {10},
#   Url  = {http://doi.acm.org/10.1145/1150402.1150435}
# }

# 2014-10-12

import pdb
import time
try:
    from models.numrange import NumRange
    from models.gentree import GenTree
    from utils.utility import cmp_str
except ImportError:
    from ..models.numrange import NumRange
    from ..models.gentree import GenTree
    from ..utils.utility import cmp_str


__DEBUG = False
QI_LEN = 10
GL_K = 5
RESULT = []
ATT_TREES = []
QI_RANGE = []
IS_CAT = []


class Partition(object):

    """Class for Group, which is used to keep records
    Store tree node in instances.
    self.member: records in group
    self.width: width of this partition on each domain
    self.middle: save the generalization result of this partition
    self.allow: 0 donate that not allow to split, 1 donate can be split
    """

    def __init__(self, data, width, middle, is_missing=None):
        """
        initialize with data, width and middle
        """
        self.member = data[:]
        self.width = list(width)
        if is_missing is None:
            self.is_missing = [False] * QI_LEN
        else:
            self.is_missing = list(is_missing)
        self.middle = list(middle)
        self.allow = [1] * QI_LEN

    def add_record(self, record):
        """
        add record to partition
        """
        self.member.append(record)

    def __len__(self):
        """
        return the number of records in partition
        """
        return len(self.member)


def get_normalized_width(partition, index):
    """
    return Normalized width of partition
    similar to NCP
    """
    if partition.middle[index] == '*':
        return 1.0
    if IS_CAT[index] is False:
        low = partition.width[index][0]
        high = partition.width[index][1]
        width = float(ATT_TREES[index].sort_value[high]) - float(ATT_TREES[index].sort_value[low])
    else:
        width = partition.width[index]
    return width * 1.0 / QI_RANGE[index]


def choose_dimension(partition):
    """chooss dim with largest normlized Width
    return dim index.
    """
    max_witdh = -1
    max_dim = -1
    for i in range(QI_LEN):
        if partition.allow[i] == 0:
            continue
        norm_width = get_normalized_width(partition, i)
        if norm_width > max_witdh:
            max_witdh = norm_width
            max_dim = i
    if max_witdh > 1:
        print "Error: max_witdh > 1"
        pdb.set_trace()
    if max_dim == -1:
        print "cannot find the max dim"
        pdb.set_trace()
    return max_dim


def frequency_set(partition, dim):
    """get the frequency_set of partition on dim
    return dict{key: str values, values: count}
    """
    frequency = {}
    for record in partition.member:
        try:
            frequency[record[dim]] += 1
        except KeyError:
            frequency[record[dim]] = 1
    return frequency


def find_median(partition, dim):
    """find the middle of the partition
    return splitVal
    """
    frequency = frequency_set(partition, dim)
    splitVal = ''
    nextVal = ''
    value_list = frequency.keys()
    value_list.sort(cmp=cmp_str)
    total = sum(frequency.values())
    middle = total / 2
    if middle < GL_K or len(value_list) <= 1:
        return ('', '', value_list[0], value_list[-1])
    index = 0
    split_index = 0
    for i, qid_value in enumerate(value_list):
        index += frequency[qid_value]
        if index >= middle:
            splitVal = qid_value
            split_index = i
            break
    else:
        print "Error: cannot find splitVal"
    try:
        nextVal = value_list[split_index + 1]
    except IndexError:
        nextVal = splitVal
    return (splitVal, nextVal, value_list[0], value_list[-1])


def split_numerical_value(numeric_value, splitVal, nextVal):
    """
    split numeric value on splitVal
    return sub ranges
    """
    split_result = numeric_value.split(',')
    if len(split_result) <= 1:
        return split_result[0], split_result[0]
    else:
        low = split_result[0]
        high = split_result[1]
        # Fix 2,2 problem
        if low == splitVal:
            lvalue = low
        else:
            lvalue = low + ',' + splitVal
        if high == nextVal:
            rvalue = high
        else:
            rvalue = nextVal + ',' + high
        return lvalue, rvalue


def split_missing(partition, dim, pwidth, pmiddle):
    """
    """
    nomissing = []
    missing = []
    isolated_partitions = []
    for record in partition.member:
        if record[dim] == '?' or record[dim] == '*':
            missing.append(record)
        else:
            nomissing.append(record)
    if len(missing) == 0:
        return []
    else:
        if len(nomissing) > 0:
            p_nomissing = Partition(nomissing, pwidth, pmiddle)
            isolated_partitions.append(p_nomissing)
        mhs = missing
        mhs_middle = pmiddle[:]
        mhs_middle[dim] = '*'
        mhs_width = pwidth[:]
        mhs_width[dim] = (0, 0)
        p_mhs = Partition(mhs, mhs_width, mhs_middle, partition.is_missing)
        p_mhs.is_missing[dim] = True
        isolated_partitions.append(p_mhs)
        return isolated_partitions


def split_numerical(partition, dim, pwidth, pmiddle):
    # numeric attributes
    sub_partitions = []
    isolated_partitions = split_missing(partition, dim, pwidth, pmiddle)
    mhs = []
    if len(isolated_partitions) > 0:
        mhs = isolated_partitions[-1]
        if len(isolated_partitions) > 1:
            partition = isolated_partitions[0]
        else:
            return [mhs]
    (splitVal, nextVal, low, high) = find_median(partition, dim)
    p_low = ATT_TREES[dim].dict[low]
    p_high = ATT_TREES[dim].dict[high]
    # update middle
    if low == high:
        pmiddle[dim] = low
    else:
        pmiddle[dim] = low + ',' + high
    pwidth[dim] = (p_low, p_high)
    if splitVal == '' or splitVal == nextVal:
        return isolated_partitions
    middle_pos = ATT_TREES[dim].dict[splitVal]
    lhs_middle = pmiddle[:]
    rhs_middle = pmiddle[:]
    lhs_middle[dim], rhs_middle[dim] = split_numerical_value(pmiddle[dim],
                                                             splitVal, nextVal)
    lhs = []
    rhs = []
    for record in partition.member:
        pos = ATT_TREES[dim].dict[record[dim]]
        if pos <= middle_pos:
            # lhs = [low, means]
            lhs.append(record)
        else:
            # rhs = (means, high]
            rhs.append(record)
    if lhs > 0 and lhs < GL_K:
        return []
    if rhs > 0 and rhs < GL_K:
        return []
    if mhs > 0 and mhs < GL_K:
        return []
    lhs_width = pwidth[:]
    rhs_width = pwidth[:]
    lhs_width[dim] = (pwidth[dim][0], middle_pos)
    rhs_width[dim] = (ATT_TREES[dim].dict[nextVal], pwidth[dim][1])
    sub_partitions.append(Partition(lhs, lhs_width, lhs_middle))
    sub_partitions.append(Partition(rhs, rhs_width, rhs_middle))
    if len(mhs) > 0:
        sub_partitions.append(mhs)
    return sub_partitions


def split_categorical(partition, dim, pwidth, pmiddle):
    sub_partitions = []
    mhs = []
    # normal attributes
    # print "Partition", len(partition)
    # if len(partition) == 635:
    #     print "allow", partition.allow
    #     print "is_missing", partition.is_missing
    #     pdb.set_trace()
    split_node = ATT_TREES[dim][pmiddle[dim]]
    if len(split_node.child) == 0:
        return split_missing(partition, dim, pwidth, pmiddle)
    sub_node = [t for t in split_node.child]
    sub_groups = []
    for i in range(len(sub_node)):
        sub_groups.append([])
    for record in partition.member:
        qid_value = record[dim]
        if qid_value == '?' or qid_value == '*':
            mhs.append(record)
            continue
        for i, node in enumerate(sub_node):
            try:
                node.cover[qid_value]
                sub_groups[i].append(record)
                break
            except KeyError:
                continue
        else:
            print "Generalization hierarchy error!"
            pdb.set_trace()
    flag = True
    for index, sub_group in enumerate(sub_groups):
        if len(sub_group) == 0:
            continue
        if len(sub_group) < GL_K:
            flag = False
            break
    if len(mhs) > 0 and len(mhs) < GL_K:
        flag = False
    if flag:
        for i, sub_group in enumerate(sub_groups):
            if len(sub_group) == 0:
                continue
            wtemp = pwidth[:]
            mtemp = pmiddle[:]
            wtemp[dim] = len(sub_node[i])
            mtemp[dim] = sub_node[i].value
            sub_partitions.append(Partition(sub_group, wtemp, mtemp))
        if len(mhs) > 0:
            mhs_width = pwidth[:]
            mhs_middle = pmiddle[:]
            mhs_middle[dim] = '*'
            mhs_width[dim] = QI_RANGE[dim]
            p_mhs = Partition(mhs, mhs_width, mhs_middle, partition.is_missing)
            p_mhs.is_missing[dim] = True
            sub_partitions.append(p_mhs)
    return sub_partitions


def split_partition(partition, dim):
    """
    split partition and distribute records to different sub-partitions
    """
    pwidth = partition.width
    pmiddle = partition.middle
    if IS_CAT[dim] is False:
        return split_numerical(partition, dim, pwidth, pmiddle)
    else:
        return split_categorical(partition, dim, pwidth, pmiddle)


def anonymize(partition):
    """
    Main procedure of mondrian.
    recursively partition groups until not allowable.
    """
    if check_splitable(partition) is False:
        RESULT.append(partition)
        return
    # Choose dim
    dim = choose_dimension(partition)
    if dim == -1:
        print "Error: dim=-1"
        pdb.set_trace()
    if partition.is_missing[dim]:
        partition.allow[dim] = 0
        anonymize(partition)
        return
    sub_partitions = split_partition(partition, dim)
    if len(sub_partitions) == 0:
        partition.allow[dim] = 0
        anonymize(partition)
    else:
        for sub_p in sub_partitions:
            anonymize(sub_p)


def check_splitable(partition):
    """
    Check if the partition can be further splited while satisfying k-anonymity.
    """
    temp = sum(partition.allow)
    if temp == 0:
        return False
    return True


def init(att_trees, data, k, QI_num=-1):
    """
    resset global variables
    """
    global GL_K, RESULT, QI_LEN, ATT_TREES, QI_RANGE, IS_CAT
    ATT_TREES = att_trees
    if QI_num <= 0:
        QI_LEN = len(data[0]) - 1
    else:
        QI_LEN = QI_num
    for gen_tree in att_trees:
        if isinstance(gen_tree, NumRange):
            IS_CAT.append(False)
        else:
            IS_CAT.append(True)
    GL_K = k
    RESULT = []
    QI_RANGE = []


def enhanced_mondrian(att_trees, data, k, QI_num=-1):
    """
    Mondrian for k-anonymity.
    This fuction support both numeric values and categoric values.
    For numeric values, each iterator is a mean split.
    For categoric values, each iterator is a split on GH.
    The final result is returned in 2-dimensional list.
    """
    init(att_trees, data, k, QI_num)
    middle = []
    result = []
    wtemp = []
    for i in range(QI_LEN):
        if IS_CAT[i] is False:
            QI_RANGE.append(ATT_TREES[i].range)
            wtemp.append((0, len(ATT_TREES[i].sort_value) - 1))
            middle.append(ATT_TREES[i].value)
        else:
            QI_RANGE.append(len(ATT_TREES[i]['*']))
            wtemp.append(len(ATT_TREES[i]['*']))
            middle.append('*')
    whole_partition = Partition(data, wtemp, middle)
    start_time = time.time()
    anonymize(whole_partition)
    rtime = float(time.time() - start_time)
    ncp = 0.0
    mp = 0.0
    for partition in RESULT:
        p_ncp = []
        r_ncp = 0.0
        for i in range(QI_LEN):
            p_ncp.append(get_normalized_width(partition, i))
        temp = partition.middle
        raw_missing = 0
        for record in partition.member:
            result.append(temp[:] + [record[-1]])
            for i in range(QI_LEN):
                if record[i] == '*':
                    raw_missing += 1
                    continue
                else:
                    r_ncp += p_ncp[i]
        ncp += r_ncp
        if raw_missing > 0:
            mp += len(partition) - mp
    ncp /= QI_LEN
    ncp /= len(data)
    ncp *= 100
    mp /= QI_LEN
    mp /= len(data)
    mp *= 100
    if __DEBUG:
        print "K=%d" % k
        # If the number of raw data is not eual to number published data
        # there must be some problems.
        print "size of partitions", len(RESULT)
        print "Number of Raw Data", len(data)
        print "Number of Published Data", sum([len(t) for t in RESULT])
        # print [len(t) for t in RESULT]
        print "NCP = %.2f %%" % ncp
        print "Missing Pollution = %.2f %%" % mp
    if len(result) != len(data):
        print "Error: lose records"
        pdb.set_trace()
    return (result, (ncp, rtime, mp))


def mondrian_split_missing(att_trees, data, k, QI_num=-1):
    """
    Mondrian for k-anonymity.
    This fuction support both numeric values and categoric values.
    For numeric values, each iterator is a mean split.
    For categoric values, each iterator is a split on GH.
    The final result is returned in 2-dimensional list.
    """
    remain_data = []
    missing_data = []
    result = []
    eval_result = [0, 0, 0]
    for record in data:
        if '*' in record:
            missing_data.append(record)
        else:
            remain_data.append(record)
    missing_result, missing_eval = mondrian(att_trees, missing_data, k, QI_num)
    remain_result, remain_eval = mondrian(att_trees, remain_data, k, QI_num)
    result = missing_result + remain_result
    eval_result[0] = len(missing_data) * missing_eval[0] \
        + len(remain_data) * remain_eval[0]
    eval_result[0] = eval_result[0] * 1.0 / len(data)
    eval_result[1] = missing_eval[1] + remain_eval[1]
    eval_result[2] = missing_eval[2]
    return (result, eval_result)


def mondrian_delete_missing(att_trees, data, k, QI_num=-1):
    """
    Mondrian for k-anonymity.
    This fuction support both numeric values and categoric values.
    For numeric values, each iterator is a mean split.
    For categoric values, each iterator is a split on GH.
    The final result is returned in 2-dimensional list.
    """
    remain_data = []
    num_removed_record = 0
    eval_result = [0, 0, 0]
    for record in data:
        if '*' in record:
            num_removed_record += 1
            continue
        else:
            remain_data.append(record)
    # print "Number of remain records", len(remain_data)
    result, eval_r = mondrian(att_trees, remain_data, k, QI_num)
    eval_result[0] = (len(remain_data) * eval_r[0] + 100 * num_removed_record) / len(data)
    eval_result[1] = eval_r[1]
    eval_result[2] = eval_r[2]
    return result, eval_result
