import pickle
try:
    from models.gentree import GenTree
    from models.numrange import NumRange
    from utils.utility import cmp_str
except ImportError:
    from ..models.gentree import GenTree
    from ..models.numrange import NumRange
    from ..utils.utility import cmp_str

__DEBUG = False

def read_tree(qi_index, is_cat, name, is_rt=False):
    """read tree from data/tree_*.txt, store them in att_tree
    """
    att_names = []
    att_trees = []
    for t in qi_index:
        att_names.append(name + '_' + str(t))
    for i in range(len(att_names)):
        if is_cat[i]:
            att_trees.append(read_tree_file(att_names[i], name))
        else:
            att_trees.append(read_pickle_file(att_names[i], name))
    if is_rt:
        # read sa gh
        att_trees.append(read_tree_file(name + '_sa', name))
    return att_trees


def read_tree_file(treename, name):
    """read tree data from treename
    """
    leaf_to_path = {}
    att_tree = {}
    postfix = ".txt"
    treefile = open('gh/' + treename + postfix, 'rU')
    att_tree['*'] = GenTree('*')
    if __DEBUG:
        print "Reading Tree" + treename
    for line in treefile:
        # delete \n
        if len(line) <= 1:
            break
        line = line.strip()
        temp = line.split(';')
        # copy temp
        temp.reverse()
        for i, t in enumerate(temp):
            isleaf = False
            if i == len(temp) - 1:
                isleaf = True
            # try and except is more efficient than 'in'
            try:
                att_tree[t]
            except:
                att_tree[t] = GenTree(t, att_tree[temp[i - 1]], isleaf)
    if __DEBUG:
        print "Nodes No. = %d" % att_tree['*'].support
    treefile.close()
    return att_tree

def read_pickle_file(att_name, name):
    """
    read pickle file for numeric attributes
    return numrange object
    """
    with open('tmp/' + att_name + '_static.pickle', 'rb') as static_file:
        (numeric_dict, sort_value) = pickle.load(static_file)
        result = NumRange(sort_value, numeric_dict)
        return result

#############################################################

def read_data(qi_index, is_cat, sa_index, name, missing=False, is_rt=False):
    """
    read microdata for *.txt and return read data
    """
    QI_num = len(qi_index)
    data = []
    numeric_dict = []
    for i in range(QI_num):
        numeric_dict.append(dict())
    # oder categorical attributes in intuitive order
    # here, we use the appear number
    data_file = open('data/' + name + '.data', 'rU')
    for line in data_file:
        line = line.strip()
        # remove empty and incomplete lines
        # only 30162 records will be kept
        if len(line) == 0:
            continue
        if missing is False and '?' in line:
            continue
        # remove double spaces
        line = line.replace(' ', '')
        temp = line.split(',')
        ltemp = []
        for i in range(QI_num):
            index = qi_index[i]
            if is_cat[i] is False:
                try:
                    numeric_dict[i][temp[index]] += 1
                except KeyError:
                    numeric_dict[i][temp[index]] = 1
            ltemp.append(temp[index])
        if is_rt:
            ltemp.append(temp[sa_index].split(';'))
        data.append(ltemp)
    # pickle numeric attributes and get NumRange
    for i in range(QI_num):
        if is_cat[i] is False:
            static_file = open('tmp/' + name +'_' + str(qi_index[i]) + '_static.pickle', 'wb')
            sort_value = list(numeric_dict[i].keys())
            sort_value.sort(cmp=cmp_str)
            pickle.dump((numeric_dict[i], sort_value), static_file)
            static_file.close()
    return data