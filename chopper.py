import PyPDF2
import io
import hashlib
from wand.image import Image
from wand.color import Color


class Chopper(object):
    """
    This class represents a PDF file in memory, and exposes methods to extract pages and convert them to PNGs.
    This class can be thought of as a kitchen slicer, initialized with a PDF.
    """
    def __init__(self, pdf_bytes):
        """
        :param pdf_bytes: Accepts an object of type bytes representing the PDF
        """
        self._file = pdf_bytes
        self._binary_stream = io.BytesIO(self._file)
        self._pdf_file = PyPDF2.PdfFileReader(self._binary_stream)

    def num_pages(self):
        """
        Human-readable 1-based count of pages, ideal for iterators and human output
        :return: int total number of pages
        """
        return self._pdf_file.getNumPages()

    def get_page_keys(self):
        """
        Returns a list of strings representing unique identifiers for each page in this
        document.  These are calculated by hashing the original document and appending the
        page number, therefore, there is a recognizable pattern between pages from a given
        document.  These terminate with .PNG to represent the final file extension.
        :return: list of strings of unique page identifiers (PNG filenames)
        """
        file_key = self.get_file_key()
        return [file_key + '-' + str(n+1) + '.png' for n in range(self.num_pages())]

    def get_page(self, num):
        """
        Returns a single-page PDF file representing a given page.  Note that the hash value
        for a single page will not match a parent document hash.
        :param num: A zero-indexed page number.
        :return: PyPDF2.PdfFileWriter representing the given page
        """
        page = self._pdf_file.getPage(num)
        new_pdf = PyPDF2.PdfFileWriter()
        new_pdf.addPage(page)
        return new_pdf

    def pages(self):
        """
        Returns an iterator for the pages in the document.
        :return: Generates each page in order from get_page method
        """
        for pageNum in range(self._pdf_file.getNumPages()):
            new_pdf = self.get_page(pageNum)

            yield new_pdf

    def images(self, resolution=300):
        """
        Returns an iterator that generates PNG images at the given resolution for each
        page in the document.
        :param resolution: int representing DPI, default 300
        :return: Generates each page in order as a PNG image
        """
        count = 0
        for page in self.pages():
            bytes_out = self.convert(page, resolution)
            count += 1

            yield bytes_out

    def get_file_key(self):
        """
        Returns a key for the file.  This is generated from a sha224 hash of the PDF file
        :return:
        """
        return hashlib.sha224(self._file).hexdigest()

    @classmethod
    def convert(cls, page, resolution):
        """
        Given a PyPDF2.PdfFileWriter, generates a PNG image at the given resolution.
        :param page: PyPDF2.PdfFileWriter representing a single page
        :param resolution: int representing DPI, default 300
        :return: Binary representation of PNG image
        """
        bytes_in = io.BytesIO()

        page.write(bytes_in)
        bytes_in.seek(0)

        return cls.convert_from_bytes(bytes_in, resolution)

    @staticmethod
    def convert_from_bytes(bytes_in, resolution):
        """
        Given a binary representation of a PDF page, generates a PNG image at the given resolution.
        :param bytes_in: bytes object containing a PDF page
        :param resolution: int representing DPI, default 300
        :return: Binary representation of PNG image
        """
        img = Image(blob=bytes_in.getvalue(), format='pdf', resolution=resolution)

        img.transform_colorspace('rgb')
        img.format = 'png'
        img.background_color = Color("white")
        img.alpha_channel = 'remove'

        return img.make_blob('png')