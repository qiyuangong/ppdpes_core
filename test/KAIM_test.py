import unittest
from algorithm.KAIM import anon_kaim
from models.gentree import GenTree
from models.numrange import NumRange
import random
import pdb
import math

# Build a GenTree object
ATT_TREES = []
QI_LEN = 2
LEN_DATA = 8
SUPPORTS = []
IS_CAT = [True, False]


def init():
    global ATT_TREES, SUPPORTS
    ATT_TREES = []
    tree_temp = {}
    tree = GenTree('*')
    tree_temp['*'] = tree
    lt = GenTree('1,5', tree)
    tree_temp['1,5'] = lt
    rt = GenTree('6,10', tree)
    tree_temp['6,10'] = rt
    for i in range(1, 11):
        if i <= 5:
            t = GenTree(str(i), lt, True)
        else:
            t = GenTree(str(i), rt, True)
        tree_temp[str(i)] = t
    numrange = NumRange(['1', '2', '3', '4', '5',
                        '6', '7', '8', '9', '10'], dict())
    ATT_TREES.append(tree_temp)
    ATT_TREES.append(numrange)
    SUPPORTS = [{} for _ in range(QI_LEN)]


def get_support(data):
    # leaf support
    for record in data:
        for index in range(QI_LEN):
            curr_value = record[index]
            try:
                SUPPORTS[index][curr_value] += 1.0 / LEN_DATA
            except KeyError:
                SUPPORTS[index][curr_value] = 1.0 / LEN_DATA
    for index in range(QI_LEN):
        if IS_CAT[index] is False:
            continue
        for key, value in ATT_TREES[index].items():
            if len(value) > 0:
                support = 0
                for leaf in value.cover.keys():
                    try:
                        support += SUPPORTS[index][leaf]
                    except KeyError:
                        pass
                SUPPORTS[index][key] = support


def entropy_value(index, value):
    entropy = 0
    if IS_CAT[index] == False:
        if value == '*':
            temp = ATT_TREES[index].value

        else:
            temp = value.split(',')
        if len(temp) == 1:
            return 0
        low, high = temp[0], temp[1]
        for curr_num in range(int(low), int(high) + 1):
            try:
                p = SUPPORTS[index][str(curr_num)]
                entropy += abs(p * math.log10(p))
            except KeyError:
                pass
    else:
        if len(ATT_TREES[index][value]) == 0:
            return 0
        for leaf in ATT_TREES[index][value].cover.keys():
            try:
                p = SUPPORTS[index][leaf]
                entropy += abs(p * math.log10(p))
            except KeyError:
                pass
    return entropy


def entropy_diff(record, gen_record):
    entropy = 0
    for index in range(QI_LEN):
        v, v1 = record[index], gen_record[index]
        p = SUPPORTS[index][v]
        c = abs(p * math.log10(p))
        info_v1 = entropy_value(index, v1)
        info_v = entropy_value(index, v)
        entropy += info_v1 / (info_v + c)
    return entropy


class functionKAIM(unittest.TestCase):
    def test_get_support(self):
        init()
        data = [['6', '1', 'haha'],
                ['6', '1', 'test'],
                ['8', '2', 'haha'],
                ['8', '2', 'test'],
                ['4', '1', 'hha'],
                ['4', '1', 'hha'],
                ['4', '3', 'hha'],
                ['4', '3', 'hha']]
        get_support(data)
        self.assertEqual(SUPPORTS[0]['*'], 1)
        self.assertEqual(SUPPORTS[0]['1,5'], 0.5)


    def test_entropy(self):
        init()
        data = [['6', '1', 'haha'],
                ['6', '1', 'test'],
                ['8', '2', 'haha'],
                ['8', '2', 'test'],
                ['4', '1', 'hha'],
                ['4', '1', 'hha'],
                ['4', '3', 'hha'],
                ['4', '3', 'hha']]
        get_support(data)
        self.assertEqual(entropy_value(0, '6'), 0)
        self.assertEqual(entropy_value(1, '1'), 0)
        self.assertTrue(entropy_value(0, '1,5') - 0.3 < 0.01)
        self.assertTrue(entropy_value(1, '1,2') - 0.3 < 0.01)
        # print 'Entropy', entropy_value(0, '1,5')
        # print 'Entropy', entropy_value(1, '1,2')

    def test_entropy_diff(self):
        init()
        data = [['6', '1', 'haha'],
                ['6', '1', 'test'],
                ['8', '2', 'haha'],
                ['8', '2', 'test'],
                ['4', '1', 'hha'],
                ['4', '2', 'hha'],
                ['4', '3', 'hha'],
                ['4', '4', 'hha']]
        get_support(data)
        self.assertTrue(entropy_diff(['6', '1', 'haha'], ['6,10', '1,2', 'haha']) - 5.0 < 0.01)
        # print entropy_diff(['6', '1', 'haha'], ['6,10', '1,2', 'haha'])

    def test1_KAIM(self):
        init()
        data = [['6', '1', 'haha'],
                ['6', '1', 'test'],
                ['8', '2', 'haha'],
                ['8', '2', 'test'],
                ['4', '1', 'hha'],
                ['4', '1', 'hha'],
                ['4', '3', 'hha'],
                ['4', '3', 'hha']]
        result, eval_r = anon_kaim(ATT_TREES, data, 2)
        try:
            self.assertTrue(abs(eval_r[0] - 0) < 0.05)
        except AssertionError:
            print result
            print eval_r
            self.assertEqual(0, 1)

    def test2_KAIM(self):
        init()
        data = [['6', '1', 'haha'],
                ['6', '1', 'test'],
                ['8', '2', 'haha'],
                ['8', '2', 'test'],
                ['4', '1', 'hha'],
                ['4', '2', 'hha'],
                ['4', '3', 'hha'],
                ['4', '4', 'hha']]
        result, eval_r = anon_kaim(ATT_TREES, data, 2)
        try:
            self.assertTrue(abs(eval_r[0] - 2.77) < 0.05)
        except AssertionError:
            print result
            print eval_r
            self.assertEqual(0, 1)

if __name__ == '__main__':
    unittest.main()
