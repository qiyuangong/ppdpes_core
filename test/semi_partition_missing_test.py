import unittest

from algorithm.semi_partition_missing import semi_partition_missing
# from utils.read_data import read_data, read_tree
from models.gentree import GenTree
from models.numrange import NumRange
import random
import pdb

# Build a GenTree object
ATT_TREES = []


def init():
    global ATT_TREES
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


class functionTest(unittest.TestCase):
    def test_semi_partition(self):
        init()
        data = [['6', '1', 'haha'],
                ['6', '1', 'test'],
                ['8', '2', 'haha'],
                ['8', '2', 'test'],
                ['4', '1', 'hha'],
                ['4', '2', 'hha'],
                ['4', '3', 'hha'],
                ['4', '4', 'hha']]
        result, eval_r = semi_partition_missing(ATT_TREES, data, 2)
        # print result
        # print eval_r
        self.assertTrue(abs(eval_r[0] - 200.0 / 72) < 0.05)

    def test_semi_partition_balance(self):
        init()
        data = [['6', '1', 'haha'],
                ['6', '1', 'test'],
                ['8', '2', 'haha'],
                ['8', '2', 'test'],
                ['4', '1', 'hha'],
                ['4', '1', 'hha'],
                ['1', '1', 'hha'],
                ['2', '1', 'hha']]
        result, eval_r = semi_partition_missing(ATT_TREES, data, 2)
        # print result
        # print eval_r
        self.assertTrue(abs(eval_r[0] - 100.0 / 16) < 0.05)

    def test1_semi_partition_incompelte(self):
        init()
        data = [['6', '?', 'haha'],
                ['6', '?', 'test'],
                ['8', '2', 'haha'],
                ['8', '2', 'test'],
                ['4', '?', 'hha'],
                ['4', '?', 'hha'],
                ['4', '3', 'hha'],
                ['4', '4', 'hha']]
        result, eval_r = semi_partition_missing(ATT_TREES, data, 2)
        # print result
        # print eval_r
        self.assertTrue(abs(eval_r[0] - 200.0 / 144) < 0.05)

    def test2_semi_partition_incompelte(self):
        init()
        data = [['6', '?', 'haha'],
                ['6', '?', 'test'],
                ['8', '2', 'haha'],
                ['8', '2', 'test'],
                ['4', '?', 'hha'],
                ['4', '3', 'hha'],
                ['4', '1', 'hha'],
                ['4', '4', 'hha']]
        result, eval_r = semi_partition_missing(ATT_TREES, data, 2)
        # print result
        # print eval_r
        self.assertTrue(abs(eval_r[0] - 1100.0 / 144) < 0.05 or
                        abs(eval_r[0] - 1300.0 / 144) < 0.05 or
                        abs(eval_r[0] - 1300.0 / 144) < 0.05 or
                        abs(eval_r[0] - 1500.0 / 144) < 0.05)


if __name__ == '__main__':
    unittest.main()
