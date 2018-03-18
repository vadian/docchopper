import PyPDF2
import io
import hashlib
from wand.image import Image
from wand.color import Color


class Chopper(object):

    def __init__(self, file_name, pdf_bytes):
        self._file_name = file_name
        self._file = pdf_bytes
        self._binary_stream = io.BytesIO(self._file)
        self._pdf_file = PyPDF2.PdfFileReader(self._binary_stream)

    def pages(self):

        for pageNum in range(self._pdf_file.getNumPages()):
            page = self._pdf_file.getPage(pageNum)

            new_pdf = PyPDF2.PdfFileWriter()
            new_pdf.addPage(page)

            yield new_pdf

    def images(self, resolution=300):
        count = 0
        for page in self.pages():
            bytes_out = self._convert(page, resolution, count)
            count += 1

            yield bytes_out

    def get_file_key(self):
        """
        Returns a key for the file.  This is generated from a hash of the PDF info and is consistent
        for a given PDF that has not been modified.
        :return:
        """
        info = self._pdf_file.getDocumentInfo()
        x = self._file_name + ''.join(info.values())
        x_bytes = bytes(x, 'UTF8')
        return hashlib.sha224(x_bytes).hexdigest()

    @staticmethod
    def _convert(page, resolution, count):
        bytes_in = io.BytesIO()

        page.write(bytes_in)
        bytes_in.seek(0)

        img = Image(blob=bytes_in.getvalue(), format='pdf', resolution=resolution)

        img.transform_colorspace('rgb')
        img.format = 'png'
        img.background_color = Color("white")
        img.alpha_channel = 'remove'

        with open('C:\\tmp\\'+str(count)+'.png', 'wb') as outfile:
            img.save(file=outfile)

        return img.make_blob('png')