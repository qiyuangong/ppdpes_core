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
                         'adult', ['age', 'workclass', 'final_weight', 'education',
                          'education_num', 'marital_status', 'occupation', 'relationship',
                          'race', 'sex', 'capital_gain', 'capital_loss', 'hours_per_week',
                          'native_country', 'class'])
        self.assertEqual(len(data), 30162)

    def test_read_adult_data_missing(self):
        data = read_data([0, 1, 4, 5, 6, 8, 9, 13], [False, True, False, True, True, True, True, True], -1,
                         'adult', ['age', 'workclass', 'final_weight', 'education',
                                   'education_num', 'marital_status', 'occupation', 'relationship',
                                   'race', 'sex', 'capital_gain', 'capital_loss', 'hours_per_week',
                                   'native_country', 'class'], True)
        self.assertEqual(len(data), 32561)

    def test_read_adult_tree(self):
        att_trees = read_tree([0, 1, 4, 5, 6, 8, 9, 13], [False, True, False, True, True, True, True, True],
                         'adult', ['age', 'workclass', 'final_weight', 'education',
                                   'education_num', 'marital_status', 'occupation', 'relationship',
                                   'race', 'sex', 'capital_gain', 'capital_loss', 'hours_per_week',
                                   'native_country', 'class'])

        self.assertEqual(len(att_trees), 8)

    def test_read_musk_data(self):
        data = read_data(range(2,168), [False] * 168, -1,
                         'musk', [str(t) for t in range(168)])
        self.assertEqual(len(data), 7074)


if __name__ == '__main__':
    unittest.main()
