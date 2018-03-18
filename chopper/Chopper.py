import PyPDF2
import io
from wand.image import Image
from wand.color import Color


class Chopper(object):

    def __init__(self, pdf_bytes):
        self._file = pdf_bytes

    def pages(self):
        binary_stream = io.BytesIO(self._file)
        pdf_file = PyPDF2.PdfFileReader(binary_stream)

        for pageNum in range(pdf_file.getNumPages()):
            page = pdf_file.getPage(pageNum)

            new_pdf = PyPDF2.PdfFileWriter()
            new_pdf.addPage(page)

            yield new_pdf

    def images(self, resolution=300):
        count = 0
        for page in self.pages():

            bytes_out = self._convert(page, resolution, count)
            count += 1

            yield bytes_out

    count = 0

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
