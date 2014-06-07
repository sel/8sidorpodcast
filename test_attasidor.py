import unittest
import attasidor


class TestFeedGeneration(unittest.TestCase):

    def test_generation(self):
        feed = attasidor.genfeed(0)

if __name__ == '__main__':
    unittest.main()
