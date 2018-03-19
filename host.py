import io
import json
from concurrent import futures
from time import time
from flask import Flask
from flask import request
from flask import Response
from chopper import Chopper
from storeybook import Storey


app = Flask(__name__)

'''
Base configuration:
BASE_URL = host before routing
PORT = 4000
ENCODER = Support REST and SOAP with 'json' or 'xml'.  Currently, json implemented.
SAFE_MODE = Controls parallel processing and whether to ignore signs of concurrent data store access
MAX_WORKERS = Max number of worker threads if SAFE_MODE is False
'''
BASE_URL = 'http://localhost'
PORT = 4000
ENCODER = 'json'
SAFE_MODE = False
MAX_WORKERS = 8


@app.route("/")
def hello():
    """
    Generic Hello, World! method.  This should always return and do so safely.
    :return:
    """
    return build_response('Hello there', 200)


@app.route("/docrepo", methods=['POST'])
def post_pdf():
    """
    This method accepts a binary PDF file and attempts to save it.
    If the file already exists, this method will error.  Uniqueness is
    determined by a sha224 hash of the file, including metadata with modified timestamp
    :return: JSON-encoded dict of URIs keyed by page number
    """
    print('Entering post_pdf')
    pdfbytes = request.get_data()
    doc = Chopper(pdfbytes)
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
    print("Entering put_pdf")
    pdfbytes = request.get_data()  # bytes class
    doc = Chopper(pdfbytes)
    conflicts = storey.list_by_prefix(doc.get_file_key())
    if len(conflicts) > 0:
        success = storey.delete_many(conflicts)
        if not success and SAFE_MODE:
            print('Error!  Could not delete duplicates.')
            return build_response('Error!  Could not delete duplicates.', 400)

    return build_response(save(doc), 200)


@app.route("/docrepo/<image>", methods=['GET'])
def get_pdf_page(image):
    """
    Returns a requested image from storage.
    :param image: the file name of the image requested
    :return: Image (status 200) on success, encoded error (status 404) for other
    """
    print(image)
    try:
        return build_response(storey.get(image), 200)
    except:
        return build_response('ERROR! No image found for given key. Looked for: ' + image, 404)


def save(chop):
    """
    Simple method that determines whether to render and save using concurrency.  This theoretically
    achieves parallelism through external C rendering, though this is reliant on proper implementations in
    modules used.  This method is also an injection point for runtime optimization metrics.
    :param chop: An incoming PDF file represented in a Chopper class
    :return: Dictionary with keys representing page numbers and values representing URLs for future access
    """
    function = None
    if SAFE_MODE:
        function = save_linear
    else:
        function = save_async
    start = time()
    retval = function(chop)
    end = time()
    print("Timedelta: " + str(end - start))
    return retval


def save_linear(chop):
    """
    Consecutively generates 300-DPI images for each page and stores them in the data store.
    :param chop: PDF represented by Chopper class
    :return: Dictionary with keys representing page numbers and values representing URLs for future access
    """
    page_keys = chop.get_page_keys()
    for num, image in enumerate(chop.images(300)):
        storey.save(page_keys[num], image)
        print('Saved linearly: ' + page_keys[num])
    page_urls = [key_to_url(page_key) for page_key in page_keys]
    print('Final list:' + str(page_urls))

    return {num + 1: value for num, value in enumerate(page_urls)}


def save_async(chop):
    """
    Concurrently generated 300-DPI images for each page and stores them in the data store.
    :param chop: PDF represented by Chopper class
    :return: Dictionary with keys representing page numbers and values representing URLs for future access
    """
    page_keys = chop.get_page_keys()
    # spin up threads
    threadable = list()

    for num, page in enumerate(chop.pages()):
        bytes_in = io.BytesIO()
        page.write(bytes_in)
        bytes_in.seek(0)
        print(bytes_in)
        threadable.append((bytes_in, page_keys[num]))

    print('Starting threads...')
    workers = min(MAX_WORKERS, len(threadable))
    with futures.ThreadPoolExecutor(workers) as pool:
        pool.map(_save_async_worker, threadable)

    page_urls = [key_to_url(page_key) for page_key in page_keys]
    return {num + 1: value for num, value in enumerate(page_urls)}


def _save_async_worker(obj):
    """
    Internal worker method for async image generation and storage
    :param obj: Tuple(page,key) with page represented by bytes representation of PDF and key to store under
    :return: None
    """
    page, key = obj
    img = Chopper.convert_from_bytes(page, 300)
    storey.save(key, img)
    print('Stored image async: ' + key)
    return


def build_response(input_obj, status):
    """
    Helper method to generate the appropriate response data for a given request.
    :param input_obj: string or other serializable type
    :param status: int status code to return
    :return: Response object representing the given inputs
    """
    encoded = None
    encoder = None

    if type(input_obj) is str:
        input_obj = [input_obj, ]

    if type(input_obj) is bytes:
        encoded = input_obj
        encoder = 'image/png'
    elif ENCODER == 'json':
        encoded = json.dumps(input_obj)
        encoder = 'application/json'
    elif ENCODER == 'xml':
        # todo - xml output
        raise NotImplementedError
    return Response(encoded, status=status, mimetype=encoder)


def key_to_url(key):
    """
    Helper method to generate URL from given key and known host information
    :param key: string key for the object
    :return: string URL for given object
    """
    return BASE_URL + ':' + str(PORT) + '/docrepo/' + key


storey = Storey()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT, debug=True, threaded=True)
