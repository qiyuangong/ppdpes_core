"""
run semi_partition with given parameters
"""

# !/usr/bin/env python
# coding=utf-8
from algorithm.semi_partition import semi_partition
from algorithm.semi_partition_missing import semi_partition_missing
from algorithm.mondrian import mondrian


from algorithm.Separation_Gen import Separation_Gen
from algorithm.PAA import PAA

from algorithm.anatomizer import anatomizer
from utils.read_adult_data import read_data as read_adult
from utils.read_adult_data import read_tree as read_adult_tree
from utils.read_informs_data import read_data as read_informs
from utils.read_informs_data import read_tree as read_informs_tree
import sys, copy, random

DATA_SELECT = 'i'
DEFAULT_K = 10
# sys.setrecursionlimit(50000)


def get_result_one(alg, att_trees, data, k=DEFAULT_K):
    "run anonymization algorithm for one time, with k=10"
    print "K=%d" % k
    data_back = copy.deepcopy(data)
    _, eval_result = alg(att_trees, data, k)
    print "NCP %0.2f" % eval_result[0] + "%"
    print "Running time %0.2f" % eval_result[1] + "seconds"


def get_result_k(alg, att_trees, data):
    """
    change k, whle fixing QD and size of dataset
    """
    data_back = copy.deepcopy(data)
    all_ncp = []
    all_rtime = []
    # for k in range(5, 105, 5):
    for k in [2, 5, 10, 25, 50, 100]:
        print '#' * 30
        print "K=%d" % k
        _, eval_result = alg(att_trees, data, k)
        data = copy.deepcopy(data_back)
        print "NCP %0.2f" % eval_result[0] + "%"
        all_ncp.append(round(eval_result[0], 2))
        print "Running time %0.2f" % eval_result[1] + "seconds"
        all_rtime.append(round(eval_result[1], 2))
    print "All NCP", all_ncp
    print "All Running time", all_rtime


def get_result_dataset(alg, att_trees, data, k=DEFAULT_K, n=10):
    """
    fix k and QI, while changing size of dataset
    n is the proportion nubmber.
    """
    data_back = copy.deepcopy(data)
    length = len(data_back)
    print "K=%d" % k
    joint = 5000
    datasets = []
    check_time = length / joint
    if length % joint == 0:
        check_time -= 1
    for i in range(check_time):
        datasets.append(joint * (i + 1))
    datasets.append(length)
    all_ncp = []
    all_rtime = []
    for pos in datasets:
        ncp = rtime = 0
        print '#' * 30
        print "size of dataset %d" % pos
        for j in range(n):
            temp = random.sample(data, pos)
            result, eval_result = alg(att_trees, temp, k)
            ncp += eval_result[0]
            rtime += eval_result[1]
            data = copy.deepcopy(data_back)
            # save_to_file((att_trees, temp, result, k, L))
        ncp /= n
        rtime /= n
        print "Average NCP %0.2f" % ncp + "%"
        all_ncp.append(round(ncp, 2))
        print "Running time %0.2f" % rtime + "seconds"
        all_rtime.append(round(rtime, 2))
    print '#' * 30
    print "All NCP", all_ncp
    print "All Running time", all_rtime


def get_result_qi(alg, att_trees, data, k=DEFAULT_K):
    """
    change nubmber of QI, whle fixing k and size of dataset
    """
    data_back = copy.deepcopy(data)
    ls = len(data[0])
    all_ncp = []
    all_rtime = []
    for i in reversed(range(1, ls)):
        print '#' * 30
        print "Number of QI=%d" % i
        _, eval_result = alg(att_trees, data, k, i)
        data = copy.deepcopy(data_back)
        print "NCP %0.2f" % eval_result[0] + "%"
        all_ncp.append(round(eval_result[0], 2))
        print "Running time %0.2f" % eval_result[1] + "seconds"
        all_rtime.append(round(eval_result[1], 2))
    print "All NCP", all_ncp
    print "All Running time", all_rtime


def get_result_missing(alg, att_trees, data, k=DEFAULT_K, n=10):
    """
    change nubmber of missing, whle fixing k, qi and size of dataset
    """
    data_back = copy.deepcopy(data)
    length = len(data_back)
    qi_len = len(data[0]) - 1
    raw_missing = raw_missing_record = 0
    print "K=%d" % k
    for record in data:
        flag = False
        for value in record:
            if value == '?' or value == '*':
                raw_missing += 1
                flag = True
        if flag:
            raw_missing_record += 1
    # print "Missing Percentage %.2f" % (raw_missing * 100.0 / (length * qi_len)) + '%%'
    # each evaluation varies add 5% missing values
    check_percentage = [5, 10, 25, 50, 75]
    datasets = []
    for p in check_percentage:
        joint = int(0.01 * p * length * qi_len) - raw_missing
        datasets.append(joint)
    all_ncp = []
    all_rtime = []
    all_pollution = []
    for i, joint in enumerate(datasets):
        ncp = rtime = pollution = 0.0
        for j in range(n):
            gen_missing_dataset(data, joint)
            missing_rate(data)
            _, eval_result = semi_partition(att_trees, data, k)
            data = copy.deepcopy(data_back)
            ncp += eval_result[0]
            rtime += eval_result[1]
            pollution += eval_result[2]
        ncp /= n
        rtime /= n
        pollution /= n
        if __DEBUG:
            print "check_percentage", check_percentage[i]
            print "Add missing %d" % joint
            print "Average NCP %0.2f" % ncp + "%"
            print "Running time %0.2f" % rtime + "seconds"
            print "Missing Pollution = %.2f" % pollution + "%"
            print '#' * 30
        all_ncp.append(round(ncp, 2))
        all_rtime.append(round(rtime, 2))
        all_pollution.append(round(pollution, 2))
    print "All NCP", all_ncp
    print "All Running time", all_rtime
    print "Missing Pollution", all_pollution
    print '#' * 30


def gen_missing_dataset(data, joint):
    """
    add missing values to dataset
    """
    length = len(data)
    qi_len = len(data[0]) - 1
    while(joint > 0):
        pos = random.randrange(length)
        for i in range(qi_len):
            col = random.randrange(qi_len)
            if data[pos][col] == '?' or data[pos][col] == '*':
                continue
            else:
                data[pos][col] = '?'
                break
        else:
            continue
        joint -= 1


if __name__ == '__main__':
    FLAG = ''
    LEN_ARGV = len(sys.argv)
    try:
        DATA_SELECT = sys.argv[1]
        FLAG = sys.argv[2]
    except:
        pass
    k = 10
    if DATA_SELECT == 'i':
        RAW_DATA = read_informs()
        ATT_TREES = read_informs_tree(1)
    else:
        RAW_DATA = read_adult()
        ATT_TREES = read_adult_tree()
    ALG = PAA
    ATT_TREES = ATT_TREES[-1]
    print '#' * 30
    if DATA_SELECT == 'a':
        print "Adult data"
    else:
        print "INFORMS data"
    print '#' * 30
    if FLAG == 'k':
        get_result_k(ALG, ATT_TREES, RAW_DATA)
    elif FLAG == 'qi':
        get_result_qi(ALG, ATT_TREES, RAW_DATA)
    elif FLAG == 'data':
        get_result_dataset(ALG, ATT_TREES, RAW_DATA)
    elif FLAG == 'one':
        if LEN_ARGV > 3:
            k = int(sys.argv[3])
            get_result_one(ALG, ATT_TREES, RAW_DATA, k)
        else:
            get_result_one(ALG, ATT_TREES, RAW_DATA)
    elif FLAG == '':
        get_result_one(ALG, ATT_TREES, RAW_DATA)
    else:
        print "Usage: python anonymizer [a | i] [k | qi | data | one]"
        print "a: adult dataset, 'i': INFORMS ataset"
        print "K: varying k, qi: varying qi numbers, data: varying size of dataset, \
                one: run only once"
    # anonymized dataset is stored in result
    print "Finish Anonymization!!"
