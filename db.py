import base64
from pymongo import MongoClient
import gridfs


def get_database():
    CONNECTION_STRING = "mongodb+srv://sarathadhithya:sarathadhithya@cluster0.thheici.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(CONNECTION_STRING)

    return client['Database']


dbname = get_database()
user_collection = dbname["users"]

job_collection = dbname["jobs"]


def write_new_pdf(path):
    db = get_database()
    fs = gridfs.GridFS(db)
    # Note, open with the "rb" flag for "read bytes"
    with open(path, "rb") as f:
        encoded_string = base64.b64encode(f.read())
    with fs.new_file(
            chunkSize=800000,
            filename=path) as fp:
        fp.write(encoded_string)


def read_pdf(filename):
    # Usual setup
    db = get_database()
    fs = gridfs.GridFS(db)
    # Standard query to Mongo
    data = fs.find_one(filter=dict(filename=filename))
    with open(filename, "wb") as f:
        f.write(base64.b64decode(data.read()))
