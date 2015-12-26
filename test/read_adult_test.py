import unittest

from utils.read_adult_data import read_data

class test_read_adult(unittest.TestCase):
    """
    adult contains 32561 records, 30162 records
    do not contain missing values
    """

    def test_read_missing(self):
        data = read_data(True)
        self.assertEqual(len(data), 32561)

    def test_read_normal(self):
        data = read_data()
        self.assertEqual(len(data), 30162)


if __name__ == '__main__':
    unittest.main()



