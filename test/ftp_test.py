import unittest
from utils.file_utility import ftp_upload, ftp_download
import random
import time


class functionTest(unittest.TestCase):
    def test_upload(self):
        ftp_upload('README.md', '')
        time.sleep(10)
        ftp_download('README.md', '')
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
