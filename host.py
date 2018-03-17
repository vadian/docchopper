from flask import Flask
from flask import request

app = Flask(__name__)


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
    print("Entering")
    try:
        pdf = request.get_data()
        print(pdf)
    except Exception as e:
        print(e)
        return 'Error!' + str(e)
    return 'Saving image...'


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
    try:
        pdfbytes = request.get_data()  # bytes class
        pdf = pdfbytes
        print(type(pdf))
    except Exception as e:
        print(e)
        return str(e)
    return 'Saving image...'


@app.route("/docrepo/<image>", methods=['GET'])
def get_pdf(image):
    print(image)
    return 'Returning an image...'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000, debug=True)
