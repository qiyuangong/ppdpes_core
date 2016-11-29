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


import sys, copy, random, cProfile, ast
import json
import pdb

try:
    from algorithm.semi_partition import semi_partition
    from algorithm.semi_partition_missing import semi_partition_missing
    from algorithm.mondrian import mondrian
    from algorithm.KAIM import anon_kaim
    from algorithm.mondrian_missing import mondrian_split_missing
    from algorithm.clustering_based_k_anon import anon_k_member, anon_k_nn
    from algorithm.NEC_based_Anon import NEC_k_member, NEC_OKA
    from algorithm.PAA import PAA
    from algorithm.APA import APA
    from algorithm.m_generalization import m_generalization
    from algorithm.anatomize import anatomize
except ImportError:
    from .algorithm.semi_partition import semi_partition
    from .algorithm.semi_partition_missing import semi_partition_missing
    from .algorithm.mondrian import mondrian
    from .algorithm.KAIM import anon_kaim
    from .algorithm.clustering_based_k_anon import anon_k_member, anon_k_nn
    from .algorithm.NEC_based_Anon import NEC_k_member, NEC_OKA
    from .algorithm.m_generalization import m_generalization
    from .algorithm.PAA import PAA
    from .algorithm.anatomize import anatomize
try:
    from utils.file_utility import ftp_download, clear_dir
    from utils.read_microdata import read_data
    from utils.read_microdata import read_tree
except ImportError:
    from .utils.file_utility import ftp_download
    from .utils.read_microdata import read_data
    from .utils.read_microdata import read_tree


__DEBUG = True
DEFAULT_K = 10
# sys.setrecursionlimit(50000)


def get_result_one(alg, att_trees, data, k=DEFAULT_K, qi_index=None, rt=False):
    "run semi_partition for one time, with k=10"
    print "K=%d" % k
    data_back = copy.deepcopy(data)
    if qi_index is None:
        result, eval_result = alg(att_trees, data, k)
    else:
        # qi index
        # select_att_trees = [t for i, t in enumerate(att_trees) if i in qi_index]
        select_data = []
        for record in data:
            tmp = [t for i, t in enumerate(record) if i in qi_index]
            # sa part
            tmp.append(record[-1])
            select_data.append(tmp)
        result, eval_result = alg(att_trees, select_data, k)
    if not rt:
        print "NCP %0.2f" % eval_result[0] + "%"
        print "Running time %0.2f" % eval_result[1] + "seconds"
    else:
        print "RNCP %0.2f" % eval_result[0] + "%"
        print "TNCP %0.2f" % eval_result[1] + "%"
        print "Running time %0.2f" % eval_result[2] + "seconds"
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


def clear_tmp_files():
    # clear datasets dand tmp
    clear_dir('data/')
    clear_dir('gh/')
    clear_dir('tmp/')


def algorithm_selection(alg_str):
    # choose algorithm
    if alg_str == 'Mondrian':
        print "Mondrian"
        alg = mondrian
    elif alg_str == 'Semi-Partition':
        print "Semi-Partition"
        alg = semi_partition
    elif alg_str == 'NEC_OKA':
        print "NEC_OKA"
        alg = NEC_OKA
    elif alg_str == 'NEC_k-member':
        print "NEC_k-member"
        alg = NEC_k_member
    elif alg_str == 'KAIM':
        print "KAIM"
        alg = anon_kaim
    if alg_str == 'Ehanced-Mondrian':
        print "Ehanced-Mondrian"
        alg = mondrian_split_missing
    elif alg_str == 'Semi-Partition-Incomplete':
        print "Semi-Partition-Incomplete"
        alg = semi_partition_missing
    elif alg_str == 'APA':
        RT = True
        print "APA"
        alg = APA
    elif alg_str == 'PAA':
        RT = True
        print "PAA"
        alg = PAA
    elif alg_str == '1M-Generlization':
        RT = True
        print "1:M-Generlization"
        alg = m_generalization
    else:
        print "Mondrian"
        alg = mondrian
    print '#' * 30
    return alg


def dataset_handle(data_name, qi_index=None, is_cat=None, status=(0, 0, 0)):
    # Download data
    print data_name
    name = data_name.split('.')[0]
    ftp_download(data_name, 'data/')
    # gh download
    if qi_index is None:
        ftp_download(name + '_', 'gh/', False)
        qi_index = [0, 1, 2]
        is_cat = [0, 0, 0]
    else:
        for index, value in enumerate(qi_index):
            if is_cat[index] == 1:
                # download gh
                ftp_download(name + '_' + str(value), 'gh/', False)
        # rt sa
        if status[2] == 1:
            ftp_download(name + '_sa', 'gh/', False)
    # read data
    data = read_data(data_name, qi_index, is_cat, status=status)
    att_trees = read_tree(name, qi_index, is_cat, status[2])
    return data, att_trees


def universe_anonymizer(argv):
    print argv
    # if __DEBUG:
    #     print sys.argv
    clear_tmp_files()
    LEN_ARGV = len(argv)
    return_dict = {}
    k = 10
    # get value from argv
    try:
        data_str = argv[0]
        alg_str = argv[1]
        qi_index = ast.literal_eval(argv[2])
        qi_index = map(int, qi_index)
        is_cat = ast.literal_eval(argv[3])
        is_cat = map(int, is_cat)
        # sa_index = int(argv[4])
        # status = ast.literal_eval(argv[4])
        status = (0, 0, 0)
    except:
        data_str = 'adult.data'
        alg_str = 'Mondrain'
    # read dataset
    alg = algorithm_selection(alg_str)
    data, att_trees = dataset_handle(data_str, qi_index, is_cat)
    print '#' * 30
    if LEN_ARGV == 2:
        return_dict = get_result_one(alg, att_trees, data)
    elif LEN_ARGV > 2:
        if argv[4] == 'anon':
            print "Begin Anon on Specific parameters"
            parameter = argv[5]
            if isinstance(parameter, str):
                parameter = parameter.replace("'", "\"")
                parameter = json.loads(parameter)
            try:
                k = int(parameter['k'])
            except KeyError:
                k = DEFAULT_K
            try:
                data_size = int(parameter['data'])
            except KeyError:
                data_size = len(data)
            try:
                qi_index = parameter['d']
            except KeyError:
                qi_index = None
            return_dict = get_result_one(alg, att_trees, data[:data_size], k, qi_index, status[-1])
        else:
            for i in range(5, LEN_ARGV):
                FLAG = argv[i]
                print "Begin Eval " + FLAG
                if FLAG == 'k':
                    return_dict[FLAG] = get_result_k(alg, att_trees, data)
                elif FLAG == 'd':
                    return_dict[FLAG] = get_result_qi(alg, att_trees, data)
                elif FLAG == 'data':
                    return_dict[FLAG] = get_result_dataset(alg, att_trees, data)
                elif FLAG == '*':
                    return_dict[FLAG] = get_result_missing(alg, att_trees, data)
                else:
                    print "Usage: python anonymizer [a | i | m] [s | m | knn | kmember] [k | qi | data | missing]"
                    print "a: adult dataset, i: INFORMS dataset, m: musk dataset"
                    print "[s: semi_partition, m: mondrian, knn: k-nnn, kmember: k-member]"
                    print "K: varying k, qi: varying qi numbers, data: varying size of dataset, \
                            missing: varying missing rate of dataset"
    # print "Finish Anonymization!!"
    return return_dict


if __name__ == '__main__':
    result, eval_r = universe_anonymizer(sys.argv[1:])
    pdb.set_trace()
    clear_tmp_files()
