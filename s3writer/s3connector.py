import os
import sys
import ntpath

from datetime import datetime
from datetime import timezone
from dotenv import load_dotenv

import boto3
from botocore.client import Config

from log_json import log_json

class s3connector(object):
    def __init__(self, exchange:str, topic:str, symbol:str):
        self.exchange = exchange
        self.topic = topic
        self.symbol = symbol
        self.log = log_json()
        self.last_datepath = ''

        access_key_id       = os.getenv("AWS_ACCESS_KEY_ID", None)
        access_secret_key   = os.getenv("AWS_SECRET_ACCESS_KEY", None)

        if not access_key_id:
            self.log.create ("ERROR", "AWS access key is not specified")
            sys.exit()

        if not access_secret_key:
            self.log.create ("ERROR", "AWS secret key is not specified")
            sys.exit()

        self.s3 = boto3.resource(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=access_secret_key,
            config=Config(signature_version='s3v4')
        )

        self.s3_client = boto3.client('s3')

        self.bucket_name = os.getenv("BUCKET_NAME", None)
    
    def get_current_timestamp(self):
        dt = datetime.now(timezone.utc)
        utc_time = dt.replace(tzinfo=timezone.utc)
        return utc_time.timestamp()

    def s3_bucket_raw_data_folders(self, year, month, day):
        return f'raw-data/exchange={self.exchange}/{self.topic}/symbol={self.symbol}/year={str(year)}/month={str(month)}/day={str(day)}/'

    def get_date_path(self, utc_timestamp):

        year = datetime.utcfromtimestamp(utc_timestamp).strftime('%Y')
        month = datetime.utcfromtimestamp(utc_timestamp).strftime('%m')
        day = datetime.utcfromtimestamp(utc_timestamp).strftime('%d')
        self.last_datepath = self.s3_bucket_raw_data_folders(year, month, day)
        return self.last_datepath
    
    def get_todays_path(self):
        return self.get_date_path(self.get_current_timestamp())

    def save_text_file(self, utc_timestamp, body:str):
        if not body:
            return

        seq = (int)(utc_timestamp * 1000000)
        folders = self.get_date_path(utc_timestamp)
        self.s3.Bucket(self.bucket_name).put_object(Key=f'{folders}{seq}', Body=body)

    def get_day_file_list(self, utc_timestamp):
        list = []
        bucket = self.s3.Bucket(self.bucket_name)
        prefix = self.get_date_path(utc_timestamp=utc_timestamp)
        for object in bucket.objects.filter(Prefix=prefix):
            list.append(object.key)
        return list

    def get_latest_file_list(self):
        list = []
        utc_timestamp = self.get_current_timestamp()
        bucket = self.s3.Bucket(self.bucket_name)
        prefix = f'{self.get_date_path(utc_timestamp=utc_timestamp)}{(int)((int)(utc_timestamp/10) / 6) * 6}'
        for object in bucket.objects.filter(Prefix=prefix):
            list.append(object.key)
        return list

    def get_s3_object(self, key):
        contents = ''
        try:
            data = self.s3_client.get_object(Bucket=self.bucket_name,Key=key)
            contents = data['Body'].read()
        except Exception as ex:
            print (ex)
        if not contents:
            return []
        return contents.decode("utf-8").split('\n')

if __name__ == "__main__":
    connector = s3connector(exchange='ByBit',topic='orderBook_200.100ms',symbol='BTCUSD')
    list = connector.get_latest_file_list()
    if list is None:
        print('Nothing in the list')
    else:
        for key in list:
            lines = connector.get_s3_object(key)
            for line in lines:
             print (line)

