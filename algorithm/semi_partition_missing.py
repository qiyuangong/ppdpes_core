"""
main module of Semi_Partition
"""

# !/usr/bin/env python
# coding=utf-8


import pdb
import random
try:
    from models.numrange import NumRange
    from models.gentree import GenTree
    from utils.utility import cmp_str
except ImportError:
    from ..models.numrange import NumRange
    from ..models.gentree import GenTree
    from ..utils.utility import cmp_str
import time


__DEBUG = False
QI_LEN = 10
GL_K = 0
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
    split_node = ATT_TREES[dim][pmiddle[dim]]
    # print "Partition", len(partition)
    # if len(partition) == 15:
    #     print "allow", partition.allow
    #     print "is_missing", partition.is_missing
    #     pdb.set_trace()
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
    # print "Partition", len(partition)
    # print "allow", partition.allow
    # print "is_missing", partition.is_missing
    # pdb.set_trace()
    if IS_CAT[dim] is False:
        return split_numerical(partition, dim, pwidth, pmiddle)
    else:
        return split_categorical(partition, dim, pwidth, pmiddle)


def balance_partition(sub_partitions, partition, dim):
    """
    balance partitions:
    Step 1: For partitions with less than k records, merge them to leftover partition.
    Step 2: If leftover partition has less than k records, then move some records
    from partitions with more than k records.
    Step 3: After Step 2, if the leftover partition does not satisfy
    k-anonymity, then merge a partitions with k records to the leftover partition.
    Final: Backtrace leftover partition to the partent node.
    """
    if len(sub_partitions) <= 1:
        return
    # leftover contains all records from subPartitons smaller than k
    # So the GH of leftover is the same as Parent.
    leftover = Partition([], partition.width, partition.middle)
    mhs = Partition([], partition.width, partition.middle, partition.is_missing)
    mhs.middle[dim] = '*'
    mhs.is_missing[dim] = True
    extra = 0
    check_list = []
    for sub_p in sub_partitions[:]:
        record_set = sub_p.member
        if sub_p.is_missing[dim]:
            mhs.member.extend(record_set)
            sub_partitions.remove(sub_p)
            continue
        if len(record_set) < GL_K:
            leftover.member.extend(record_set)
            sub_partitions.remove(sub_p)
        else:
            extra += len(record_set) - GL_K
            check_list.append(sub_p)
    # there is no record to balance
    if len(leftover) > 0:
        ls = len(leftover)
        if ls < GL_K:
            need_for_leftover = GL_K - ls
            if need_for_leftover > extra:
                if len(check_list) > 0:
                    min_p = 0
                    min_size = len(check_list[0])
                    for i, sub_p in enumerate(check_list):
                        if len(sub_p) < min_size:
                            min_size = len(sub_p)
                            min_p = i
                    sub_p = sub_partitions.pop(min_p)
                    leftover.member.extend(sub_p.member)
            else:
                while need_for_leftover > 0:
                    check_list = [t for t in sub_partitions if len(t) > GL_K]
                    for sub_p in check_list:
                        if need_for_leftover > 0:
                            t = sub_p.member.pop(random.randrange(len(sub_p)))
                            leftover.member.append(t)
                            need_for_leftover -= 1
        sub_partitions.append(leftover)
    if len(mhs) > 0:
        ls = len(mhs)
        if ls < GL_K:
            need_for_missing = GL_K - ls
            check_list = []
            extra = 0
            for sub_p in sub_partitions:
                if len(sub_p) >= GL_K:
                    extra += len(sub_p) - GL_K
                    check_list.append(sub_p)
            if need_for_missing > extra:
                if len(check_list) > 0:
                    min_p = 0
                    min_size = len(check_list[0])
                    for i, sub_p in enumerate(check_list):
                        if len(sub_p) < min_size:
                            min_size = len(sub_p)
                            min_p = i
                    sub_p = sub_partitions.pop(min_p)
                    mhs.member.extend(sub_p.member)
                else:
                    temp = sub_partitions.pop()
                    mhs.member.extend(temp.member)
            else:
                while need_for_missing > 0:
                    check_list = [t for t in sub_partitions if len(t) > GL_K]
                    for sub_p in check_list:
                        if need_for_missing > 0:
                            t = sub_p.member.pop(random.randrange(len(sub_p)))
                            mhs.member.append(t)
                            need_for_missing -= 1
        sub_partitions.append(mhs)


def anonymize(partition):
    """
    Main procedure of Half_Partition.
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
        raw_ls = len(sub_partitions)
        flag = False
        if sub_partitions[-1].is_missing[dim]:
            flag = True
            raw_ls -= 1
        if raw_ls == 0:
            partition.is_missing[dim] = True
            partition.middle[dim] = '*'
            partition.allow[dim] = 0
            anonymize(partition)
            return
        elif raw_ls == 1 and flag is False:
            anonymize(sub_partitions[0])
            return
        else:
            balance_partition(sub_partitions, partition, dim)
            end_ls = len(sub_partitions)
            if flag:
                end_ls -= 1
            if end_ls == 1:
                if flag:
                    sub_partitions[0].allow[dim] = 0
                    anonymize(sub_partitions[0])
                    anonymize(sub_partitions[-1])
                else:
                    partition.allow[dim] = 0
                    anonymize(partition)
                return
            elif end_ls == 0:
                anonymize(sub_partitions[-1])
                return
        # recursively partition
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
    reset all global variables
    """
    global GL_K, RESULT, QI_LEN, ATT_TREES, QI_RANGE, IS_CAT
    ATT_TREES = att_trees
    for t in att_trees:
        if isinstance(t, NumRange):
            IS_CAT.append(False)
        else:
            IS_CAT.append(True)
    if QI_num <= 0:
        QI_LEN = len(data[0]) - 1
    else:
        QI_LEN = QI_num
    GL_K = k
    RESULT = []
    QI_RANGE = []


def semi_partition_missing(att_trees, data, k, QI_num=-1):
    """
    Mondrian for l-diversity.
    This fuction support both numeric values and categoric values.
    For numeric values, each iterator is a mean split.
    For categoric values, each iterator is a split on GH.
    The final result is returned in 2-dimensional list.
    """
    init(att_trees, data, k, QI_num)
    result = []
    middle = []
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
        raw_missing = 0
        for i in range(QI_LEN):
            p_ncp.append(get_normalized_width(partition, i))
        temp = partition.middle
        for record in partition.member:
            result.append(temp[:] + [record[-1]])
            for i in range(QI_LEN):
                if record[i] == '?' or record[i] == '*':
                    raw_missing += 1
                    continue
                else:
                    r_ncp += p_ncp[i]
        ncp += r_ncp
        if raw_missing > 0:
            mp += raw_missing
    # covert to NCP percentage
    ncp /= QI_LEN
    ncp /= len(data)
    ncp *= 100
    mp /= QI_LEN
    mp /= len(data)
    mp *= 100
    if len(result) != len(data):
        print "Losing records during anonymization!!"
        pdb.set_trace()
    if __DEBUG:
        print "K=%d" % k
        print "size of partitions"
        print len(RESULT)
        temp = [len(t) for t in RESULT]
        print sorted(temp)
        print "NCP = %.2f %%" % ncp
        print "Missing Pollution = %.2f %%" % mp
    return (result, (ncp, rtime, mp))
