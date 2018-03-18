import unittest
from storeybook import Storey


class TestStoreAndRetrieval(unittest.TestCase):
    FILE = 'C:\\Users\\n0082\\Documents\\deep learning cheat sheet.pdf'
    KEY = '12345679.pdf'

    def setUp(self):
        self.storey = Storey()
        with open(self.FILE, 'rb') as file:
            self.pdf_bytes = file.read()

    def test_list_buckets(self):
        x = self.storey.get_buckets()
        self.assertGreater(len(x), 0, 'No buckets found.')
        self.assertTrue('storeytime' in x, 'Could not find default bucket.')

    def test_list_by_prefix(self):
        self.assertFalse(self.storey.contains_prefix(self.KEY), 'WARNING: Key already exists!')
        self.storey.save(self.KEY, self.pdf_bytes)
        prefix_list = self.storey.list_by_prefix(self.KEY)
        self.assertTrue(self.KEY in prefix_list, 'ERROR!  Check for key after upload failed.')
        self.assertTrue(len(prefix_list) == 1, 'Error, multiple objects with this prefix')
        self.storey.delete(self.KEY)

    def test_contains_prefix(self):
        self.assertFalse(self.storey.contains_prefix(self.KEY), 'WARNING: Key already exists!')
        self.storey.save(self.KEY, self.pdf_bytes)
        self.assertTrue(self.storey.contains_prefix(self.KEY), 'ERROR!  Check for key after upload failed.')
        self.storey.delete(self.KEY)

    def test_upload(self):
        self.assertFalse(self.storey.contains_prefix(self.KEY), 'WARNING: Key already exists!')
        self.storey.save(self.KEY, self.pdf_bytes)
        self.assertTrue(self.storey.contains_prefix(self.KEY), 'ERROR!  Check for key after upload failed.')
        self.storey.delete(self.KEY)

    def test_upload_many(self):
        key2 = self.KEY + 'alt'

        # create a dict of key, byte pairs
        upload = {self.KEY: self.pdf_bytes,
                  key2: self.pdf_bytes}

        self.storey.save_many(upload)
        self.assertTrue(self.storey.contains_prefix(self.KEY), 'ERROR!  Check for key after upload failed.')
        self.assertTrue(self.storey.contains_prefix(key2), 'ERROR!  Check for second key after upload failed.')
        self.storey.delete_many([self.KEY, key2])

    def test_upload_and_download(self):
        self.storey.save(self.KEY, self.pdf_bytes)
        returned_bytes = self.storey.get(self.KEY)
        self.assertEqual(returned_bytes, self.pdf_bytes)
        self.storey.delete(self.KEY)

    def test_delete(self):
        self.storey.save(self.KEY, self.pdf_bytes)
        self.assertTrue(self.storey.contains_prefix(self.KEY), 'ERROR!  Check for key after upload failed.')
        self.storey.delete(self.KEY)
        self.assertFalse(self.storey.contains_prefix(self.KEY), 'ERROR! Key exists after delete!')

    def test_delete_many(self):
        key2 = self.KEY + 'alt'

        # create a dict of key, byte pairs
        upload = {self.KEY: self.pdf_bytes,
                  key2: self.pdf_bytes}

        self.storey.save_many(upload)
        self.assertTrue(self.storey.contains_prefix(self.KEY), 'ERROR!  Check for key after upload failed.')
        self.assertTrue(self.storey.contains_prefix(key2), 'ERROR!  Check for second key after upload failed.')
        self.storey.delete_many([self.KEY, key2])
        self.assertFalse(self.storey.contains_prefix(self.KEY), 'ERROR! Key exists after delete!')
        self.assertFalse(self.storey.contains_prefix(key2), 'ERROR! Second key exists after delete!')

    def tearDown(self):
        del self.storey.s3
        del self.storey


if __name__ == '__main__':
    unittest.main()
