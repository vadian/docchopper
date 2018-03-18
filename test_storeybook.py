import unittest
from storeybook import Storey


class TestStoreAndRetrieval(unittest.TestCase):
    FILE = 'C:\\Users\\n0082\\Documents\\deep learning cheat sheet.pdf'
    KEY = '12345679.pdf'

    def setUp(self):
        self.storey = Storey()

        binary = b''
        with open(self.FILE, 'rb') as file:
            for byte in file:
                binary += byte
        self.pdf_bytes = binary

    def test_list_buckets(self):
        x = self.storey.get_buckets()
        self.assertGreater(len(x), 0, 'No buckets found.')
        self.assertTrue('storeytime' in x, 'Could not find default bucket.')

    def test_upload(self):

        self.assertFalse(self.storey.contains_key(self.KEY), 'WARNING: Key already exists!')
        self.storey.save(self.KEY, self.pdf_bytes)
        self.assertTrue(self.storey.contains_key(self.KEY), 'ERROR!  Check for key after upload failed.')

    def test_upload_and_download(self):
        self.storey.save(self.KEY, self.pdf_bytes)
        returned_bytes = self.storey.get(self.KEY)
        self.assertEqual(returned_bytes, self.pdf_bytes)

    def test_delete(self):
        self.storey.save(self.KEY, self.pdf_bytes)
        self.assertTrue(self.storey.contains_key(self.KEY), 'ERROR!  Check for key after upload failed.')
        self.storey.delete(self.KEY)
        self.assertFalse(self.storey.contains_key(self.KEY), 'ERROR! Key exists after delete!')

    def tearDown(self):
        del self.storey.s3
        del self.storey


if __name__ == '__main__':
    unittest.main()
