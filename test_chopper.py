import unittest
from chopper.Chopper import Chopper


class TestPDFConversion(unittest.TestCase):

    def setUp(self):
        self.filename = 'C:\\Users\\n0082\\Documents\\deep learning cheat sheet.pdf'

        binary = b''
        with open(self.filename, 'rb') as file:
            for byte in file:
                binary += byte
        self.pdf_bytes = binary

    def test_ctor(self):
        chop = Chopper(self.filename, self.pdf_bytes)
        self.assertEqual(chop._file, self.pdf_bytes)

    def test_page_iterator(self):
        chop = Chopper(self.filename, self.pdf_bytes)
        count = 0

        for page in chop.pages():
            count += 1
            self.assertEqual(page.getNumPages(), 1, 'ERROR: More than one page in PDF returned by page iterator')
            self.assertEqual(str(type(page)), '<class \'PyPDF2.pdf.PdfFileWriter\'>',
                             'ERROR: ' + str(type(page)) + ' not PyPDF2.pdf.PdfFileWriter')

        self.assertGreater(count, 0, 'ERROR: No pages returned by iterator')

    def test_image_iterator(self):
        chop = Chopper(self.filename, self.pdf_bytes)
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
        for image in Chopper(self.filename, self.pdf_bytes).images():
            with open('C:\\tmp\\'+str(count)+'.png', 'wb') as file:
                file.write(image)
            count += 1

    def test_hash(self):
        chop = Chopper(self.filename, self.pdf_bytes)
        chop2 = Chopper(self.filename, self.pdf_bytes)
        self.assertEqual(chop.get_file_key(), chop2.get_file_key())

        chop3 = Chopper(self.filename + 'Extra', self.pdf_bytes)
        self.assertNotEqual(chop.get_file_key(), chop3.get_file_key())


if __name__ == '__main__':
    unittest.main()
