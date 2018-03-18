import boto3
import io


class Storey(object):

    def __init__(self, bucket_name='storeytime'):
        self.s3 = boto3.resource('s3')
        self._bucket_name = bucket_name
        self._bucket = self.s3.Bucket(bucket_name)

    def save(self, key, binary_data):
        self._bucket.put_object(Key=key, Body=binary_data)

    def save_many(self, input_dict):
        #todo - concurrency
        for key, value in input_dict.items():
            self._bucket.put_object(Key=key, Body=value)

    def get(self, key):
        fileobj = io.BytesIO()
        self._bucket.download_fileobj(key, fileobj)
        return fileobj.getvalue()

    def delete(self, key):

        return self.delete_many([key, ])

    def delete_many(self, keys):
        key_dict = [{'Key': key} for key in keys]

        retval = self._bucket.delete_objects(Delete={'Objects': key_dict})
        key_set = set(keys)
        deleted_keys = set(retkey['Key'] for retkey in retval['Deleted'])
        xor_set = key_set.symmetric_difference(deleted_keys)

        return len(xor_set) == 0 and retval['ResponseMetadata']['HTTPStatusCode'] == 200

    def list_all_objects(self):
        all_objs = self._bucket.objects.all()
        return list(obj.key for obj in all_objs)

#    def contains_key(self, key):
#        return key in self.list_all_objects()

    def list_by_prefix(self, prefix):
        filtered = self._bucket.objects.filter(Prefix=prefix)
        return list(obj.key for obj in filtered)

    def contains_prefix(self, prefix):
        return len(self.list_by_prefix(prefix)) > 0

    def get_buckets(self):
        return list(bucket.name for bucket in self.s3.buckets.all())
