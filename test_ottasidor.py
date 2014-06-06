import unittest
import ottasidor


class TestFeedGeneration(unittest.TestCase):

    def test_generation(self):
        feed = ottasidor.genfeed()

if __name__ == '__main__':
    unittest.main()
