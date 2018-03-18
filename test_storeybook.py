import unittest
from storeybook import Storey


class TestStoreAndRetrieval(unittest.TestCase):

    def setUp(self):
        self.storey = Storey()

#    def test_ctor(self):
#        self.assertEqual(1, 0)

    def test_list_buckets(self):
        x = self.storey.get_buckets()
        print(x)


if __name__ == '__main__':
    unittest.main()
