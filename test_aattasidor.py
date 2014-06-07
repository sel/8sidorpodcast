import unittest
import aattasidor


class TestFeedGeneration(unittest.TestCase):

    def test_generation(self):
        feed = aattasidor.genfeed(0, 'http://127.0.0.1:5000/')


if __name__ == '__main__':
    unittest.main()
