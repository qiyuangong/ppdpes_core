#!/usr/bin/env python
# coding=utf-8

# Read data and read tree fuctions for musk data

try:
    from models.numrange import NumRange
    from utils.utility import cmp_str
except ImportError:
    from ..models.numrange import NumRange
    from ..utils.utility import cmp_str
import pickle

import pdb
# Musk: [other(0, 1), f1-f166, class]
# f1-f166 as QID
# class as SA
QI_INDEX = range(2, 168)
SA_INDEX = -1
__DEBUG = False


def read_tree():
    """read tree from data/tree_*.txt, store them in att_tree
    """
    att_trees = []
    for i in range(len(QI_INDEX)):
        att_trees.append(read_pickle_file(str(QI_INDEX[i])))
    return att_trees


def read_data():
    """
    read microda for *.txt and return read data
    """
    QI_num = len(QI_INDEX)
    data = []
    numeric_dict = []
    for i in range(QI_num):
        numeric_dict.append(dict())
    # oder categorical attributes in intuitive order
    # here, we use the appear number
    data_file = open('data/musk.data', 'rU')
    for line in data_file:
        line = line.strip('.\n')
        line = line.replace(' ', '')
        temp = line.split(',')
        ltemp = []
        for i in range(QI_num):
            index = QI_INDEX[i]
            try:
                numeric_dict[i][temp[index]] += 1
            except KeyError:
                numeric_dict[i][temp[index]] = 1
            ltemp.append(temp[index])
        ltemp.append(temp[-1])
        data.append(ltemp)
    # pickle numeric attributes and get NumRange
    for i in range(QI_num):
        static_file = open('tmp/musk_' + str(QI_INDEX[i]) + '_static.pickle', 'wb')
        sort_value = list(numeric_dict[i].keys())
        sort_value.sort(cmp=cmp_str)
        pickle.dump((numeric_dict[i], sort_value), static_file)
        static_file.close()
    return data


def read_pickle_file(att_name):
    """
    read pickle file for numeric attributes
    return numrange object
    """
    try:
        static_file = open('tmp/musk_' + att_name + '_static.pickle', 'rb')
        (numeric_dict, sort_value) = pickle.load(static_file)
    except:
        print "Pickle file not exists!!"
    static_file.close()
    result = NumRange(sort_value, numeric_dict)
    return result
