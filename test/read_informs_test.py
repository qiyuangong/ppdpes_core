import unittest

from utils.read_informs_data import read_data

class test_read_informs(unittest.TestCase):
    """
    informs dataset contains 58568 records
    """

    def test_read_normal(self):
        data = read_data()
        self.assertEqual(len(data), 58568)


if __name__ == '__main__':
    unittest.main()
