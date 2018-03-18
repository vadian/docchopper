import json
from flask import Flask
from flask import request
from flask import Response
from chopper import Chopper
from storeybook import Storey
from xml.etree import ElementTree

app = Flask(__name__)

BASE_URL = 'http://localhost'
PORT = 4000
ENCODER = 'json'  # 'json' or 'xml', json only at the moment


@app.route("/")
def hello():
    return 'Hello there'


@app.route("/docrepo", methods=['POST'])
def post_pdf():
    """
    This method accepts a binary PDF file and attempts to save it.
    If the file already exists, this method will error.  Uniqueness is
    determined by a sha224 hash of the file, including metadata with modified timestamp
    :return: JSON-encoded dict of URIs keyed by page number
    """
    print('Entering')
    pdfbytes = request.get_data()
    doc = Chopper(pdfbytes)
    print('Made doc')
    if storey.contains_prefix(doc.get_file_key()):
        print('Key conflict')
        return build_response('Error!  Document already exists.', 400)
    print('Saving')
    return build_response(save(doc), 200)


@app.route("/docrepo", methods=['PUT'])
def put_pdf():
    """
    This method accepts a binary PDF file and attempts to save it.
    If the file exists, all pages of the existing file will be deleted
    and new files will be generated.  Uniqueness is determined by a sha224
    hash of the file, including metadata with modified timestamp.
    :return: JSON-encoded dict of URIs keyed by page number
    """
    print("Entering")
    pdfbytes = request.get_data()  # bytes class
    doc = Chopper(pdfbytes)
    conflicts = storey.list_by_prefix(doc.get_file_key())
    if len(conflicts) > 0:
        success = storey.delete_many(conflicts)
        if not success:
            # todo - should we perhaps silently let this go 'cause concurrency?
            print('Error!  Could not delete duplicates.')
            return build_response('Error!  Could not delete duplicates.', 400)

    return build_response(save(doc), 200)


@app.route("/docrepo/<image>", methods=['GET'])
def get_pdf_page(image):
    print(image)

    if not storey.contains_prefix(image):
        return build_response('ERROR! No key! Looked for: ' + image, 404)

    return build_response(storey.get(image), 200)


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
        page_urls.append(BASE_URL + ':' + str(PORT) + '/docrepo/' + page_key)
    print('Final list:' + str(page_urls))

    return {num+1: value for num, value in enumerate(page_urls)}


def build_response(input_obj, status):
    encoded = None
    encoder = None
    print(type(input_obj))

    if type(input_obj) is bytes:
        encoded = input_obj
        encoder = 'image/png'
    elif ENCODER == 'json':
        encoded = json.dumps(input_obj)
        encoder = 'application/json'
    elif ENCODER == 'xml':
        # todo - xml output
        pass
    return Response(encoded, status=status, mimetype=encoder)


storey = Storey()
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT, debug=True)
