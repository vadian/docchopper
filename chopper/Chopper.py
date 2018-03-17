import PyPDF2
import io


def bin_to_iter(binary):
    for byte in binary:
        yield byte


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
        for page in self.pages():
            # convert to image
            # yield image
            pass

#    def _convert(self):
