import boto3

class Storey(object):

    def __init__(self):
        self.s3 = boto3.resource('s3')

    def save(self, key, binary_data, bucket_name='default'):
        self.s3.Bucket(bucket_name).put_object(Key=key, Body=binary_data)

    def get(self, key, bucket_name='default'):
        self.s3.Bucket(bucket_name).get_object(Key=key)

    def get_buckets(self):
        return list(bucket.name for bucket in self.s3.buckets.all())
