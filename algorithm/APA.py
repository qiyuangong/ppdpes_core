#!/usr/bin/env python
#coding=utf-8

# by Qiyuan Gong
# qiyuangong@gmail.com
# http://github.com/qiyuangong
# http://cn.linkedin.com/pub/qiyuan-gong/6b/831/407/

from partition_for_transaction_index import partition, list_to_str
from anatomize_index import anatomize
import time, random
import pdb

_DEBUG = True


def check_diversity(data, group, L):
    """check if group satisfy l-diversity
    """
    SA_values = set()
    for index in group:
        str_value = list_to_str(data[index][-1], cmp)
        SA_values.add(str_value)
    if len(SA_values) >= L:
        return True
    return False


def mergeable(data, group1, group2, L):
    """check if group1 can merge with group2 to achieve l-diversity
    """
    return check_diversity(data, (group1 + group2), L)


def APA(att_tree, data, K=10, L=5):
    """Using Partition to anonymize SA (transaction) partition,
    while applying Anatomize to separate QID and SA
    """
    # Initialization
    if isinstance(att_tree, list):
        att_tree = att_tree[-1]
    start_time = time.time()
    result = []
    suppress = []
    print "size of dataset %d" % len(data)
    # Begin Anatomy
    print "Begin Anatomy"
    anatomy_index = anatomize(data, L)
    # Begin Partition
    trans = [t[-1] for t in data]
    trans_set = partition(att_tree, trans, K)
    for ttemp in trans_set:
        (index_list, tran_value) = ttemp
        for t in index_list:
            # generalization SA
            data[t][-1] = tran_value[:]
    # Merge groups to achieve l-diversity
    residue = []
    grouped_index = []
    for group in anatomy_index:
        if check_diversity(data, group, L):
            grouped_index.append(group[:])
        else:
            residue.append(group[:])
    while len(residue) > 0:
        g = residue.pop()
        for index, group in enumerate(residue):
            if mergeable(data, g, group, L):
                g = g + group
                grouped_index.append(g)
                residue.pop(index)
                break
        else:
            # add group element to random group, which alread satisfy l-diversity
            if len(grouped_index) > 0:
                seed = random.randrange(len(grouped_index))
                grouped_index[seed] = grouped_index[seed] + g
            else:
                print "Error: group cannot satisfy l-diversity"
                for index in g:
                    suppress.append(data[index])
    if _DEBUG:
        print 'NO. of Suppress after Group Merge = %d' % len(suppress)
        print 'NO. of groups = %d' % len(grouped_index)
    grouped_result = []
    for indexes in grouped_index:
        gtemp = []
        for index in indexes:
            gtemp.append(data[index])
        grouped_result.append(gtemp)
    rtime = time.time() - start_time
    print("--- %s seconds ---" % rtime)
    # transform anatmoized data to relational
    for index, group in enumerate(grouped_result):
        length = len(group)
        qi_dic = {}
        # sa will not duplciate
        sa_set = []
        for t in group:
            qi_key = ';'.join(t[:-1])
            sa_set.append(list(t[-1]))
            try:
                qi_dic[qi_key].append(t)
            except KeyError:
                qi_dic[qi_key] = [t]
        for k in qi_dic:
            temp = list(qi_dic[k][0][:-1])
            for i in range(length):
                result.append(temp + [sa_set[i]])
    return (result, (0, 0, rtime))
