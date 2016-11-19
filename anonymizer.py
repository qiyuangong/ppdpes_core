# !/usr/bin/env python
# coding=utf-8

# ***********************************
# Qiyuan Gong
# qiyuangong@gmail.com
# 2016-11-19
# ***********************************
# Before you start using this program, please make sure
# you understand following information:
# ***********************************
# Data type:
# RT-data ['a1', ['a1', 'b1', 'b2']]
# Relational data [18, 'M', 'Married']
# Set-valued data ['a1', 'b1', 'b2']
# ***********************************
# Paramters:
# k, qi (also called d in my thesis), l, n (size of dataset)
# ***********************************
# Information Loss: NCP and ARE
# ***********************************
# About PPDPES
# ***********************************
# Anon:
# Anon means anonymized dataset with given parameters.
# This procedure runs anonymization only once and generates anoymized
# dataset from the raw dataset.
# ***********************************
# Eval:
# Eval means evaluted algorithm with given parameters.
# This procedure runs chosen algorithms mulitple times to get
# enough outputs on given parameters.
# ***********************************


import sys, copy, random, cProfile
try:
    from algorithm.semi_partition import semi_partition
    from algorithm.semi_partition_missing import semi_partition_missing
    from algorithm.mondrian import mondrian
    from algorithm.clustering_based_k_anon import anon_k_member, anon_k_nn
    from algorithm.Separation_Gen import Separation_Gen
    from algorithm.PAA import PAA
    from algorithm.anatomize import anatomize
except ImportError:
    from .algorithm.semi_partition import semi_partition
    from .algorithm.semi_partition_missing import semi_partition_missing
    from .algorithm.mondrian import mondrian
    from .algorithm.clustering_based_k_anon import anon_k_member, anon_k_nn
    from .algorithm.NEC_based_Anon import NEC_based_Anon
    from .algorithm.Separation_Gen import Separation_Gen
    from .algorithm.PAA import PAA
    from .algorithm.anatomize import anatomize
try:
    from utils.file_utility import ftp_download, clear_dir
    from utils.read_adult_data import read_data as read_adult
    from utils.read_adult_data import read_tree as read_adult_tree
    from utils.read_informs_data import read_data as read_informs
    from utils.read_informs_data import read_tree as read_informs_tree
    from utils.read_musk_data import read_data as read_musk
    from utils.read_musk_data import read_tree as read_musk_tree
except ImportError:
    from .utils.file_utility import ftp_download
    from .utils.read_adult_data import read_data as read_adult
    from .utils.read_adult_data import read_tree as read_adult_tree
    from .utils.read_informs_data import read_data as read_informs
    from .utils.read_informs_data import read_tree as read_informs_tree
    from .utils.read_musk_data import read_data as read_musk
    from .utils.read_musk_data import read_tree as read_musk_tree

__DEBUG = True
DATA_SELECT = 'i'
DEFAULT_K = 10
# sys.setrecursionlimit(50000)


def get_result_one(alg, att_trees, data, k=DEFAULT_K, qi_index=None):
    "run semi_partition for one time, with k=10"
    print "K=%d" % k
    data_back = copy.deepcopy(data)
    if qi_index is None:
        result, eval_result = alg(att_trees, data, k)
    else:
        # qi index
        select_att_trees = [t for i, t in enumerate(att_trees) if i in qi_index]
        select_data = []
        for record in data:
            select_data.append([t for i, t in enumerate(record) if i in qi_index])
        result, eval_result = alg(select_att_trees, select_data, k)
    print "NCP %0.2f" % eval_result[0] + "%"
    print "Running time %0.2f" % eval_result[1] + "seconds"
    return (result, eval_result)


def get_result_k(alg, att_trees, data):
    """
    change k, whle fixing QD and size of dataset
    """
    data_back = copy.deepcopy(data)
    all_ncp = []
    all_rtime = []
    all_k = []
    # for k in range(5, 105, 5):
    for k in [2, 5, 10, 25, 50, 100]:
        all_k.append(k)
        _, eval_result = alg(att_trees, data, k)
        data = copy.deepcopy(data_back)
        all_ncp.append(round(eval_result[0], 2))
        all_rtime.append(round(eval_result[1], 2))
        if __DEBUG:
            print '#' * 30
            print "K=%d" % k
            print "NCP %0.2f" % eval_result[0] + "%"
            print "Running time %0.2f" % eval_result[1] + "seconds"
    print "All NCP", all_ncp
    print "All Running time", all_rtime
    print '#' * 30
    return [all_k, all_ncp, all_rtime]


def get_result_dataset(alg, att_trees, data, k=DEFAULT_K, n=10, joint=5000):
    """
    fix k and QI, while changing size of dataset
    n is the proportion nubmber.
    """
    data_back = copy.deepcopy(data)
    length = len(data_back)
    print "K=%d" % k
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
        ncp = rtime = pollution = 0.0
        for j in range(n):
            temp = random.sample(data, pos)
            __, eval_result = alg(att_trees, temp, k)
            ncp += eval_result[0]
            rtime += eval_result[1]
            data = copy.deepcopy(data_back)
        ncp /= n
        rtime /= n
        if __DEBUG:
            print '#' * 30
            print "size of dataset %d" % pos
            print "Average NCP %0.2f" % ncp + "%"
            print "Running time %0.2f" % rtime + "seconds"
        all_ncp.append(round(ncp, 2))
        all_rtime.append(round(rtime, 2))
    print "All NCP", all_ncp
    print "All Running time", all_rtime
    print '#' * 30
    return [datasets, all_ncp, all_rtime]


def get_result_qi(alg, att_trees, data, k=DEFAULT_K):
    """
    change nubmber of QI, whle fixing k and size of dataset
    """
    data_back = copy.deepcopy(data)
    ls = len(data[0])
    all_ncp = []
    all_rtime = []
    for i in range(1, ls):
        _, eval_result = alg(att_trees, data, k, i)
        data = copy.deepcopy(data_back)
        all_ncp.append(round(eval_result[0], 2))
        all_rtime.append(round(eval_result[1], 2))
        if __DEBUG:
            print '#' * 30
            print "Number of QI=%d" % i
            print "NCP %0.2f" % eval_result[0] + "%"
            print "Running time %0.2f" % eval_result[1] + "seconds"
    print "All NCP", all_ncp
    print "All Running time", all_rtime
    print '#' * 30
    return [range(1, ls), all_ncp, all_rtime]


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
            _, eval_result = alg(att_trees, data, k)
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
    return [datasets, all_ncp, all_rtime]


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


# TODO ARE
def are():
    """
    are for relational dataset
    """
    pass


# TODO ARE_1M
def are_1m():
    """
    are for 1:M dataset
    """
    pass


def universe_anonymizer(argv):
    LEN_ARGV = len(argv)
    return_dict = {}
    k = 10
    # get value from argv
    try:
        DATA_SELECT = argv[0]
        ALG_SELECT = argv[1]
    except:
        DATA_SELECT = 'a'
        ALG_SELECT = 'm'
    # read dataset
    if DATA_SELECT == 'a':
        print "Adult data"
        # dataset
        ftp_download('adult.data', 'data/')
        # gh
        ftp_download('adult_', 'gh/', False)
        RAW_DATA = read_adult()
        ATT_TREES = read_adult_tree()
    elif DATA_SELECT == 'i':
        print "INFORMS data"
        # dataset
        ftp_download('informs.txt', 'data/')
        # gh
        ftp_download('informs_', 'gh/', False)
        RAW_DATA = read_informs()
        ATT_TREES = read_informs_tree(1)
    elif DATA_SELECT == 'm':
        print "Musk data"
        # dataset
        ftp_download('musk.data', 'data/')
        # gh
        ftp_download('musk_', 'gh/', False)
        RAW_DATA = read_musk()
        ATT_TREES = read_musk_tree()
    else:
        print "Adult data"
        # dataset
        ftp_download('adult.data', 'data/')
        # gh
        ftp_download('adult_', 'gh/', False)
        RAW_DATA = read_adult()
        ATT_TREES = read_adult_tree()
    if __DEBUG:
        print sys.argv
    print '#' * 30
    # choose algorithm
    if ALG_SELECT == 'm':
        print "Mondrian"
        ALG = mondrian
    elif ALG_SELECT == 's':
        print "Semi-Partition"
        ALG = semi_partition
    elif ALG_SELECT == 'knn':
        print "k-nn"
        ALG = anon_k_nn
    elif ALG_SELECT == 'kmember':
        print "k-member"
        ALG = anon_k_member
    else:
        print "Mondrian"
        ALG = mondrian
    print '#' * 30
    if LEN_ARGV == 2:
        return_dict = get_result_one(ALG, ATT_TREES, RAW_DATA)
    elif LEN_ARGV > 2:
        if argv[2] == 'anon':
            print "Begin Anon on Specific parameters"
            parameter = argv[3]
            try:
                k = int(parameter['k'])
            except KeyError:
                k = DEFAULT_K
            try:
                data_size = int(parameter['data'])
            except KeyError:
                data_size = len(RAW_DATA)
            try:
                qi_index = parameter['qi']
            except KeyError:
                qi_index = None
            return_dict = get_result_one(ALG, ATT_TREES, RAW_DATA[:data_size], k, qi_index)
        else:
            for i in range(3, LEN_ARGV):
                FLAG = argv[i]
                print "Begin Eval " + FLAG
                if FLAG == 'k':
                    return_dict[FLAG] = get_result_k(ALG, ATT_TREES, RAW_DATA)
                elif FLAG == 'qi':
                    return_dict[FLAG] = get_result_qi(ALG, ATT_TREES, RAW_DATA)
                elif FLAG == 'data':
                    return_dict[FLAG] = get_result_dataset(ALG, ATT_TREES, RAW_DATA)
                elif FLAG == 'missing':
                    return_dict[FLAG] = get_result_missing(ALG, ATT_TREES, RAW_DATA)
                else:
                    print "Usage: python anonymizer [a | i | m] [s | m | knn | kmember] [k | qi | data | missing]"
                    print "a: adult dataset, i: INFORMS dataset, m: musk dataset"
                    print "[s: semi_partition, m: mondrian, knn: k-nnn, kmember: k-member]"
                    print "K: varying k, qi: varying qi numbers, data: varying size of dataset, \
                            missing: varying missing rate of dataset"
    # print "Finish Anonymization!!"
    return return_dict


if __name__ == '__main__':
    universe_anonymizer(sys.argv[1:])
    # clear datasets dand tmp
    # clear_dir('data/')
    # clear_dir('gh/')
    clear_dir('tmp/')
