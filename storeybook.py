import boto3
import io


class Storey(object):

    def __init__(self):
        self.s3 = boto3.resource('s3')

    def save(self, key, binary_data, bucket_name='storeytime'):
        self.s3.Bucket(bucket_name).put_object(Key=key, Body=binary_data)

    def get(self, key, bucket_name='storeytime'):
        fileobj = io.BytesIO()
        self.s3.Bucket(bucket_name).download_fileobj(key, fileobj)
        return fileobj.getvalue()

    def delete(self, key, bucket_name='storeytime'):
        todel = [{'Key': key}, ]
        retval = self.s3.Bucket(bucket_name).delete_objects(Delete={'Objects': todel})
        return key in (retkey['Key'] for retkey in retval['Deleted']) \
            and retval['ResponseMetadata']['HTTPStatusCode'] == 200

    def list_objects(self, bucket_name='storeytime'):
        all_objs = self.s3.Bucket(bucket_name).objects.all()
        return list(obj.key for obj in all_objs)

    def contains_key(self, key, bucket_name='storeytime'):
        return key in self.list_objects(bucket_name)

    def contains_prefix(self, prefix, bucket_name='storeytime'):
        all_objs = self.s3.Bucket(bucket_name).objects.filter(Prefix=prefix)
        return len(set(obj.key for obj in all_objs)) > 0

    def get_buckets(self):
        return list(bucket.name for bucket in self.s3.buckets.all())
