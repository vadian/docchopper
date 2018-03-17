import unittest
from chopper.Chopper import Chopper


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        filename = 'C:\\Users\\n0082\\Documents\\deep learning cheat sheet.pdf'

        binary = b''
        with open(filename, 'rb') as file:
            for byte in file:
                binary += byte
        self.pdf_bytes = binary

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

        for page in chop.images():
            count += 1
            self.assertEqual(str(type(page)), '<class \'PNGImage\'>',
                             'ERROR: ' + str(type(page)) + ' not PNGImage')

        self.assertGreater(count, 0, 'ERROR: No images returned by iterator')


if __name__ == '__main__':
    unittest.main()
