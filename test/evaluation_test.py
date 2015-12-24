import unittest
from models.gentree import GenTree
try:
    from ..evaluation import count_query, est_query, get_result_cover, average_relative_error
except:
    from evaluation import count_query, est_query, get_result_cover, average_relative_error

# Build a GenTree object
ATT_TREE = {}


def init_tree():
    global ATT_TREE
    ATT_TREE = {}
    root = GenTree('*')
    ATT_TREE['*'] = root
    lt = GenTree('A', root)
    ATT_TREE['A'] = lt
    ATT_TREE['a1'] = GenTree('a1', lt, True)
    ATT_TREE['a2'] = GenTree('a2', lt, True)
    rt = GenTree('B', root)
    ATT_TREE['B'] = rt
    ATT_TREE['b1'] = GenTree('b1', rt, True)
    ATT_TREE['b2'] = GenTree('b2', rt, True)

class test_Apriori_based_Anon(unittest.TestCase):
    def test_get_result_cover(self):
        init_tree()
        att_trees = [ATT_TREE, ATT_TREE]
        result = [['a1', ['A', 'b1', 'b2']],
                  ['a1', ['A', 'b1']],
                  ['a2', ['A', 'b1', 'b2']],
                  ['a2', ['A', 'b2']]]
        gen_data = get_result_cover(att_trees, result)
        temp = [[{'a1': 1.0}, {'a1': 0.5, 'a2': 0.5, 'b1': 1.0, 'b2': 1.0}],
                [{'a1': 1.0}, {'a1': 0.5, 'a2': 0.5, 'b1': 1.0}],
                [{'a2': 1.0}, {'a1': 0.5, 'a2': 0.5, 'b1': 1.0, 'b2': 1.0}],
                [{'a2': 1.0}, {'a1': 0.5, 'a2': 0.5, 'b2': 1.0}]]
        self.assertEqual(gen_data, temp)

    def test_count_query(self):
        init_tree()
        att_trees = [ATT_TREE, ATT_TREE]
        data = [['a1', ['a1', 'b1', 'b2']],
                ['a1', ['a2', 'b1']],
                ['a2', ['a2', 'b1', 'b2']],
                ['a2', ['a1', 'a2', 'b2']]]
        count = count_query(data, [0, 1], [['a1', 'a2'], [['a2', 'b1'], ['a1', 'b1', 'b2']]])
        self.assertEqual(count, 2)

    def test_est_query(self):
        init_tree()
        att_trees = [ATT_TREE, ATT_TREE]
        result = [['a1', ['A', 'b1', 'b2']],
                  ['a1', ['A', 'b1']],
                  ['a2', ['A', 'b1', 'b2']],
                  ['a2', ['A', 'b2']]]
        gen_data = get_result_cover(att_trees, result)
        est = est_query(gen_data, [0, 1], [['a1', 'a2'], [['a2', 'b1'], ['a1', 'b1', 'b2']]])
        self.assertEqual(est, 2.5)

    def test_are(self):
        init_tree()
        att_trees = [ATT_TREE, ATT_TREE]
        data = [['a1', ['a1', 'b1', 'b2']],
                ['a1', ['a2', 'b1']],
                ['a2', ['a2', 'b1', 'b2']],
                ['a2', ['a1', 'a2', 'b2']]]
        result = [['a1', ['A', 'b1', 'b2']],
                  ['a1', ['A', 'b1']],
                  ['a2', ['A', 'b1', 'b2']],
                  ['a2', ['A', 'b2']]]
        are = average_relative_error(att_trees, data, result, 1, 5)
        # self.assertEqual(are, 0.5)