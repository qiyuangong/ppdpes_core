import unittest
from algorithm.AIM import AIM
import random
import pdb


class functionTest(unittest.TestCase):
    def test1_anatomize(self):
        data = [['6', '1', 'haha'],
                ['6', '1', 'test'],
                ['8', '*', 'aa'],
                ['8', '2', 't'],
                ['4', '1', 'a'],
                ['4', '*', 'b'],
                ['4', '3', 'c'],
                ['4', '4', 'd']]
        result = AIM(data, 2)
        try:
            self.assertEqual(len(result), 4)
        except AssertionError:
            print result
            self.assertEqual(0, 1)

if __name__ == '__main__':
    unittest.main()
