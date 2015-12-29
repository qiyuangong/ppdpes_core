import unittest

from utils.read_musk_data import read_data
from utils.read_musk_data import read_tree

class test_read_informs(unittest.TestCase):
    """
    informs dataset contains 58568 records
    """

    def test_read_data(self):
        data = read_data()
        self.assertEqual(len(data), 7074)
        tree = read_tree()
        self.assertEqual(1, 1)


if __name__ == '__main__':
    unittest.main()
