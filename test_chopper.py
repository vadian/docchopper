import unittest
from chopper import Chopper


class TestPDFConversion(unittest.TestCase):

    def setUp(self):
        self.filename = 'test.pdf'

        with open(self.filename, 'rb') as file:
            self.pdf_bytes = file.read()

    def test_ctor(self):
        chop = Chopper(self.pdf_bytes)
        self.assertEqual(chop._file, self.pdf_bytes)

    def test_page_iterator(self):
        chop = Chopper(self.pdf_bytes)
        count = 0

        for page in chop.pages():
            count += 1
            self.assertEqual(page.getNumPages(), 1, 'ERROR: More than one page in PDF returned by page iterator')
            self.assertEqual(str(type(page)), '<class \'PyPDF2.pdf.PdfFileWriter\'>',
                             'ERROR: ' + str(type(page)) + ' not PyPDF2.pdf.PdfFileWriter')

        self.assertGreater(count, 0, 'ERROR: No pages returned by iterator')

    def test_image_iterator(self):
        chop = Chopper(self.pdf_bytes)
        count = 0

        for image in chop.images():
            count += 1
            self.assertEqual(str(type(image)), '<class \'bytes\'>',
                             'ERROR: ' + str(type(image)) + ' not bytes')
            self.assertGreater(len(image), 0, 'ERROR: Empty Byte String')

        self.assertGreater(count, 0, 'ERROR: No images returned by iterator')

    local = False

    def test_display(self):
        if not self.local:
            return

        count = 0
        for image in Chopper(self.pdf_bytes).images():
            with open('C:\\tmp\\'+str(count)+'.png', 'wb') as file:
                file.write(image)
            count += 1

    def test_hash(self):
        chop = Chopper(self.pdf_bytes)
        chop2 = Chopper(self.pdf_bytes)
        self.assertEqual(chop.get_file_key(), chop2.get_file_key())

        chop3 = Chopper(self.pdf_bytes + b'1234234897')
        self.assertNotEqual(chop.get_file_key(), chop3.get_file_key())

    def test_page_keys(self):
        chop = Chopper(self.pdf_bytes)
        file_key = chop.get_file_key()
        page_keys = chop.get_page_keys()
        count = 0
        for x in range(chop.num_pages()):
            count += 1
            key = file_key + '-' + str(count) + '.png'
            self.assertTrue(key in page_keys)
        self.assertTrue(count == chop.num_pages())


if __name__ == '__main__':
    unittest.main()
