import unittest

try:
    from utils.read_microdata import read_data
    from utils.read_microdata import read_tree
except ImportError:
    from ..utils.read_microdata import read_data
    from ..utils.read_microdata import read_tree


class test_read_microdata(unittest.TestCase):
    """
    adult contains 32561 records, 30162 records
    do not contain missing values
    """

    def test_read_adult_data(self):
        data = read_data([0, 1, 4, 5, 6, 8, 9, 13], [False, True, False, True, True, True, True, True], -1,
                         'adult')
        self.assertEqual(len(data), 30162)

    def test_read_adult_data_missing(self):
        data = read_data([0, 1, 4, 5, 6, 8, 9, 13], [False, True, False, True, True, True, True, True], -1,
                         'adult', True)
        self.assertEqual(len(data), 32561)

    def test_read_adult_tree(self):
        att_trees = read_tree([0, 1, 4, 5, 6, 8, 9, 13], [False, True, False, True, True, True, True, True],
                         'adult')

        self.assertEqual(len(att_trees), 8)

    def test_read_musk_data(self):
        data = read_data(range(2,168), [False] * 168, -1,
                         'musk')
        self.assertEqual(len(data), 7074)

    def test_read_informs_data(self):
        data = read_data([3, 4, 6, 13, 16], [True, True, True, True, False, True], -1, 'informs', True)

    def test_read_informs_tree(self):
        data = read_tree([3, 4, 6, 13, 16], [True, True, True, True, False, True], 'informs', True)

if __name__ == '__main__':
    unittest.main()
