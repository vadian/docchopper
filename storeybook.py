import boto3
import io
import time
import threading
from queue import Queue

NUM_WORKER_THREADS = 4


class Storey(object):
    """
    This class serves to represent an abstraction layer between the front-end and
    AWS S3.  The purpose is to allow for easy future development of concurrency features,
    such as batch uploading, as well as provide a convenient caching layer.
    Apologies for the terrible pun.
    """

    def __init__(self, use_queue=False, bucket_name='storeytime'):
        """
        Instantiates a new Storey
        :param bucket_name: string name of AWS S3 bucket to use
        """
        self.s3 = boto3.resource('s3')
        self._bucket_name = bucket_name
        self._bucket = self.s3.Bucket(bucket_name)
        self.use_queue = use_queue

        if use_queue:
            threads = []
            for i in range(NUM_WORKER_THREADS):
                t = threading.Thread(target=_upload_worker, args=(bucket_name,))
                t.start()
                threads.append(t)

    def save(self, key, binary_data):
        """
        Save binary data under a given key to the selected bucket
        :param key: key under which to store this object in the selected bucket
        :param binary_data: bytes object containing the data to store
        :return: None
        """
        self.save_many({key: binary_data, })

    def save_many(self, input_dict):
        """
        This method is a stubbed location for future concurrent IO access development
        :param input_dict: dict of key, value pairs representing key to store under and a binary
        representation of the data to store as bytes object
        :return:
        """

        for key, value in input_dict.items():
            if self.use_queue:
                to_upload.put((key, value,))
            else:
                self._bucket.put_object(Key=key, Body=value)

    def get(self, key):
        """
        Retrieve object with given key from storage.  Throws exception if key is invalid.
        :param key: string key for object to retrieve
        :return: bytes object containing the given data from storage
        """
        fileobj = io.BytesIO()
        self._bucket.download_fileobj(key, fileobj)
        return fileobj.getvalue()

    def delete(self, key):
        """
        Thin wrapper for delete_many.
        :param key: Single key as a string of object to delete
        :return: Returns True if key was found and object was successfully deleted
        """
        return self.delete_many([key, ])

    def delete_many(self, keys):
        """
        Given a list of strings representing keys, delete all objects with those keys from storage.
        :param keys: list of strings
        :return: Returns True if all objects were found in storage and successfully deleted.
        """
        key_dict = [{'Key': key} for key in keys]

        retval = self._bucket.delete_objects(Delete={'Objects': key_dict})
        key_set = set(keys)
        deleted_keys = set(retkey['Key'] for retkey in retval['Deleted'])
        xor_set = key_set.symmetric_difference(deleted_keys)

        return len(xor_set) == 0 and retval['ResponseMetadata']['HTTPStatusCode'] == 200

    def list_all_objects(self):
        """
        List of all keys for a given bucket.  WARNING: In production, this method will likely experience
        high throughput and latency as the bucket grows.
        :return: List of strings representing keys for all objects in bucket
        """
        all_objs = self._bucket.objects.all()
        return list(obj.key for obj in all_objs)

    def list_by_prefix(self, prefix):
        """
        Returns a list of keys that start with the given prefix, inclusive of exact matches.
        :param prefix: string representing the key prefix to search
        :return: List of strings of keys that start with the given prefix
        """
        filtered = self._bucket.objects.filter(Prefix=prefix)
        return list(obj.key for obj in filtered)

    def contains_prefix(self, prefix):
        """
        Returns True if there are one are more objects in the store that start with the given key,
        inclusive of exact matches.
        :param prefix: string representing the key prefix to search
        :return: True if there is at least one key in the store that starts with or matches the prefix
        """
        return len(self.list_by_prefix(prefix)) > 0

    def get_buckets(self):
        """
        List all buckets for which the account in use has access.
        :return: List of strings representing the bucket names
        """
        return list(bucket.name for bucket in self.s3.buckets.all())


to_upload = Queue()


def _upload_worker(bucket_name):
    """
    When in queue mode, this internal worker method polls the queue for submissions to upload,
    and uploads them.
    :param bucket_name:
    :return:
    """
    bucket = boto3.resource('s3').Bucket(bucket_name)

    while True:
        item = to_upload.get()
        if item is None:
            time.sleep(1000)
            print('Nothing to upload.')
            continue
        print('Saving:' + str(item[0]))
        bucket.put_object(Key=item[0], Body=item[1])
        to_upload.task_done()

