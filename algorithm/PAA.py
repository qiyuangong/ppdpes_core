from partition_for_transaction_index import partition, list_to_str
from half_anatomize import anatomize
import time
import pdb


_DEBUG = True


def PAA(att_tree, data, K=10, L=5):
    """Using Partition to anonymize SA (transaction) partition,
    while applying Anatomize to separate QID and SA
    """
    if isinstance(att_tree, list):
        att_tree = att_tree[-1]
    start_time = time.time()
    print "size of dataset %d" % len(data)
    result = []
    trans = [t[-1] for t in data]
    trans_set = partition(att_tree, trans, K)
    grouped_data = []
    for ttemp in trans_set:
        (index_list, tran_value) = ttemp
        parent = list_to_str(tran_value, cmp)
        gtemp = []
        for t in index_list:
            temp = data[t][:]
            leaf = list_to_str(temp[-1], cmp)
            temp[-1] = tran_value[:]
            gtemp.append(temp)
        grouped_data.append(gtemp)
    print "Begin Anatomy"
    grouped_result = anatomize(grouped_data, L)
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
