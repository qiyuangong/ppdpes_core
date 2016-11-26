#!/usr/bin/env python
#coding=utf-8

# by Qiyuan Gong
# qiyuangong@gmail.com
# http://github.com/qiyuangong
# http://cn.linkedin.com/pub/qiyuan-gong/6b/831/407/

from partition_for_transaction_index import partition, list_to_str
from half_anatomize import anatomize
import time, random
import pdb

_DEBUG = True

gl_att_tree = []
gl_data = []


def get_range(att_tree, tran):
    """compute probability for generlized set
    For example, age value 10 is generlized to 10-20.
    So the probability is 1/10, which means that this
    range is 10 with probability 1/10.
    """
    # store the probability of each value
    prob = 1.0
    for t in tran:
        if len(att_tree[t]):
            support = len(att_tree[t])
            prob /= support
    return prob


def check_diversity(group, L):
    """check if group satisfy l-diversity
    """
    SA_values = set()
    for index in group:
        str_value = list_to_str(gl_data[index][-1], cmp)
        SA_values.add(str_value)
    if len(SA_values) >= L:
        return True
    return False


def mergeable(group1, group2, L):
    """check if group1 can merge with group2 to achieve l-diversity
    """
    return check_diversity((group1+group2), L)


def APA(att_tree, data, K=10, L=5):
    """Using Partition to anonymize SA (transaction) partition, 
    while applying Anatomize to separate QID and SA
    """
    # Initialization
    global gl_data
    if isinstance(att_tree, list):
        att_tree = att_tree[-1]
    gl_data = data
    start_time = time.time()
    result = []
    suppress = []
    tran_tree = {}
    print "size of dataset %d" % len(gl_data)
    # Begin Anatomy
    print "Begin Anatomy"
    anatomy_index = anatomize(gl_data, L)
    # Begin Partition
    trans = [t[-1] for t in gl_data]
    trans_set = partition(att_tree, trans, K)
    for ttemp in trans_set:
        (index_list, tran_value) = ttemp
        parent = list_to_str(tran_value, cmp)
        try:
            tran_tree[parent]
        except:
            tran_tree[parent] = set()
        for t in index_list:
            leaf = list_to_str(gl_data[t][-1], cmp)
            tran_tree[parent].add(leaf)
            gl_data[t][-1] = tran_value[:]
    # pdb.set_trace()
    # Merge groups to achieve l-diversity
    residue = []
    grouped_index = []
    for group in anatomy_index:
        if check_diversity(group, L):
            grouped_index.append(group[:])
        else:
            residue.append(group[:])
    while len(residue) > 0:
        g = residue.pop()
        for index, group in enumerate(residue):
            if mergeable(g, group, L):
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
                    suppress.append(gl_data[index])
    if _DEBUG:
        print 'NO. of Suppress after Group Merge = %d' % len(suppress)
        print 'NO. of groups = %d' % len(grouped_index)
    grouped_result = []
    for indexes in grouped_index:
        gtemp = []
        for index in indexes:
            gtemp.append(gl_data[index])
        grouped_result.append(gtemp)
    print("--- %s seconds ---" % (time.time()-start_time))
    # transform data format (QID1,.., QIDn, SA set, GroupID, 1/|group size|, SA_list (dict) :original SA (str) sets with prob)
    # 1/|group size|, original SA sets with prob (dict) will be used in evaluation
    for index, group in enumerate(grouped_result):
        length = len(group)
        leaf_list = []
        SA_list = {}
        parent_list = {}
        for t in group:
            parent = list_to_str(t[-1], cmp)
            gen_range = get_range(att_tree, t[-1])
            leaf_list = leaf_list + list(tran_tree[parent])
            parent_list[parent] = gen_range
        # all transactions covered by this group
        leaf_list = list(set(leaf_list))
        # pdb.set_trace()
        for temp in leaf_list:
            for p in parent_list.keys():
                if temp in tran_tree[p]:
                    try:
                        SA_list[temp] += parent_list[p]/length 
                    except:
                        SA_list[temp] = parent_list[p]/length
        # pdb.set_trace()
        for t in group:
            temp = t[:]
            temp.append(index)
            temp.append(1.0/length)
            temp.append(SA_list)
            result.append(temp)
    return result
