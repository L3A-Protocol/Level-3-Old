import os
import boto3
import botocore
from pathlib import Path
import logging as logger

from botocore.exceptions import ClientError
from osbot_utils.utils.Files import temp_folder, path_combine, file_exists, folder_create, file_write

class s3_storage:
    AWS_FOLDER = path_combine(Path.home(),'.aws')
    AWS_CREDENTIALS_PATH = path_combine(Path.home(),'.aws/credentials')
    S3_PROTOCOL_IDENTIFIER = 's3://'
    S3_NOT_CONNECTED = 's3 not connected'

    _instance = None
    def __new__(cls):                                               # singleton pattern
        if cls._instance is None:
            cls._instance = super(s3_storage, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'enabled') is False:                     # only set these values first time around
            self.enabled     = False
            self.s3          = None
            self.s3_resource = None
            self.buckets     = []
            self.init_s3_client()

    def create_aws_credentials_file(self):
        access_key = os.getenv("AWS_ACCESS_KEY_ID", '')
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", '')
        session_token = os.getenv("AWS_SESSION_TOKEN", '')
        if  access_key and len(access_key) == 20 and \
            secret_key and len(secret_key) == 40:
            access_key_string = f'aws_access_key_id={access_key}'
            secret_key_string = f'aws_secret_access_key={secret_key}'
            session_token_string = ''
            if session_token:
                session_token_string = f'aws_session_token={session_token}'
            folder_create(s3_storage.AWS_FOLDER)
            file_write(s3_storage.AWS_CREDENTIALS_PATH, f'[default]\n{access_key_string}\n{secret_key_string}\n{session_token_string}' )
            return True
        return False

    def is_connected(self):
        response = None
        if not self.s3:
            return None
        try:
            response = self.s3.list_buckets()
        except Exception as e:
            logger.error(f's3 failed to connect {e}')
            return None
        return response

    def init_s3_client(self):
        self.create_aws_credentials_file()
        if not file_exists(s3_storage.AWS_CREDENTIALS_PATH):
            return
        self.s3 = boto3.client('s3')
        self.s3_resource = boto3.resource('s3')
        response = self.is_connected()
        if response:
            self.enabled = True
            for bucket in response['Buckets']:
                self.buckets.append(bucket['Name'])

    def is_s3url(self, s3url):
        return len(s3url) > len(s3_storage.S3_PROTOCOL_IDENTIFIER) and s3url.startswith(s3_storage.S3_PROTOCOL_IDENTIFIER)

    def get_bucket(self, s3url):
        if not self.is_s3url(s3url):
            return None
        s3path_list = s3url.split('/')
        return s3path_list[2]

    def get_object_path(self, s3url):
        bucket = self.get_bucket(s3url)
        if not bucket:
            return None
        bucket_url = s3_storage.S3_PROTOCOL_IDENTIFIER + bucket
        if len(s3url) == len(bucket_url):
            # no prefix in the url
            return ""
        return s3url.replace(f'{bucket_url}/',"")

    def bucket_exists(self, bucket_name):
        if not self.enabled:
            return False
        return bucket_name in self.buckets

    def get_file_list(self, bucket_name, prefix = ''):
        if not self.enabled:
            return []
        if not self.bucket_exists(bucket_name):
            return []
        filelist = []
        bucket = self.s3_resource.Bucket(bucket_name)
        for object in bucket.objects.filter(Prefix=prefix):
            if object.key.endswith('/'):
                # this is a directory - do nothing
                continue
            filelist.append(f'{s3_storage.S3_PROTOCOL_IDENTIFIER}{bucket_name}/{object.key}')

        return filelist

    def get_file(self, bucket_name, object_name, file_path):
        if not self.enabled:
            return False

        if not self.bucket_exists(bucket_name):
            return False

        object_path = self.get_object_path(object_name)

        try:
            self.s3_resource.Bucket(bucket_name).download_file(object_path, file_path)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                logger.error(f'The object {object_name} does not exist.')
            return False

        return True

    def upload_file(self, bucket_name, object_path, file_path):
        if not file_exists(file_path):
            return False

        if not self.bucket_exists(bucket_name):
            return False

        try:
            self.s3.upload_file(file_path, bucket_name, object_path)
        except ClientError as e:
            logger.error(e)
            return False

        return True
