"""
run semi_partition with given parameters
"""

# !/usr/bin/env python
# coding=utf-8
from algorithm.semi_partition import semi_partition
from algorithm.mondrian import mondrian
from algorithm.Separation_Gen import Separation_Gen
from algorithm.anatomizer import anatomizer
from utils.read_adult_data import read_data as read_adult
from utils.read_adult_data import read_tree as read_adult_tree
from utils.read_informs_data import read_data as read_informs
from utils.read_informs_data import read_tree as read_informs_tree
import sys, copy, random

DATA_SELECT = 'I'
# sys.setrecursionlimit(50000)


def get_result_one(alg, att_trees, data, k=10):
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


def get_result_dataset(alg, att_trees, data, k=10, n=10):
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


def get_result_qi(alg, att_trees, data, k=10):
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
        ATT_TREES = read_informs_tree()
    else:
        RAW_DATA = read_adult()
        ATT_TREES = read_adult_tree()
    ALG = mondrian
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
