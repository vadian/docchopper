import PyPDF2
import io
from wand.image import Image
from wand.image import Color


class Chopper(object):

    def __init__(self, stream):
        self._file = stream

    def pages(self):
        binary_stream = io.BytesIO(self._file)
        pdf_file = PyPDF2.PdfFileReader(binary_stream)

        for pageNum in range(pdf_file.getNumPages()):
            page = pdf_file.getPage(pageNum)

            # generate image
            new_pdf = PyPDF2.PdfFileWriter()
            new_pdf.addPage(page)

            yield new_pdf

    def images(self):
        count = 0
        for page in self.pages():
            # convert to image
            bytes_out = self._convert(page, count)
            count += 1
            # yield image
            yield bytes_out

    count = 0

    @staticmethod
    def _convert(page, count):
        bytes_in = io.BytesIO()

        page.write(bytes_in)
        bytes_in.seek(0)

        img = Image(file=bytes_in, format='pdf', resolution=300)

        with open('C:\\tmp\\'+str(count)+'.pdf', 'wb') as outfile:
            img.save(file=outfile)

        print('Height:' + str(img.height) + ' Width: ' + str(img.width))
        print('Format: ' + img.format)
        print('BG Color: ' + img.background_color.string)

        img.format = 'png'
        img.background_color = Color("white")
        img.alpha_channel = 'remove'
        with open('C:\\tmp\\'+str(count)+'.png', 'wb') as outfile:
            img.save(file=outfile)

        print('Height:' + str(img.height) + ' Width: ' + str(img.width))
        print('Format: ' + img.format)
        print('BG Color: ' + img.background_color.string)
        return img.make_blob('png')
