from flask import Flask
from flask import request
from flask import make_response

from chopper.Chopper import Chopper
from storeybook import Storey

app = Flask(__name__)

BASE_URL = 'http://localhost'

@app.route("/")
def hello():
    return 'Hello there'


@app.route("/docrepo", methods=['POST'])
def post_pdf():
    """
    This method accepts a binary PDF file and attempts to save it.
    If the file already exists, this method will error.  Uniqueness is
    determined by....
    todo: fill this in
    :return: JSON-encoded dict of URIs keyed by page number
    """
    print('Entering')
    pdfbytes = request.get_data()
    doc = Chopper('', pdfbytes)
    print('Made doc')
    if storey.has_prefix(doc.get_file_key()):
        print('Key conflict')
        return 'Error!'
    print('Saving')
    return save(doc)


@app.route("/docrepo", methods=['PUT'])
def put_pdf():
    """
    This method accepts a binary PDF file and attempts to save it.
    If the file exists, all pages of the existing file will be deleted
    and new files will be generated.  Uniqueness is determined by...
    todo: same, fill this in
    :return: JSON-encoded dict of URIs keyed by page number
    """
    print("Entering")
    pdfbytes = request.get_data()  # bytes class
    doc = Chopper('', pdfbytes)
    conflicts = storey.list_objects(doc.get_file_key())
    if len(conflicts) > 0:
        success = storey.delete_all(conflicts)
        if not success:
            #todo - should we perhaps silently let this go 'cause concurrency?
            print('Error!  Could not delete duplicates.')
            return 'Error!  Could not delete duplicates.'

    return save(doc)


@app.route("/docrepo/<image>", methods=['GET'])
def get_pdf(image):
    print(image)

    if not storey.contains_key(image):
        return 'ERROR! No key! Looked for: ' + image

    return storey.get(image)



def save(chop):
    print('Entering save')
    doc_key = chop.get_file_key()
    page = 0
    page_urls = list()
    print('Chopping...')
    for image in chop.images(300):
        page += 1
        page_key = doc_key + '-' + str(page) + '.png'
        print('Chopped one.')
        storey.save(page_key, image)
        print('Saved')
        page_urls.append(BASE_URL + '/' + page_key)
    print('Final list:' + str(page_urls))
    return page_urls


storey = Storey()
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000, debug=True)
