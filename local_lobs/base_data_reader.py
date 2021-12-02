import os

from datetime import datetime
from datetime import timezone
from dotenv import load_dotenv

import boto3
from botocore.client import Config

class base_data_reader(object):
    def __init__(self, exchange:str, topic:str, symbol:str):
        self.exchange = exchange
        self.topic = topic
        self.symbol = symbol

        access_key_id       = os.getenv("AWS_ACCESS_KEY_ID", None)
        access_secret_key   = os.getenv("AWS_SECRET_ACCESS_KEY", None)
        self.s3 = boto3.resource(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=access_secret_key,
            config=Config(signature_version='s3v4')
        )
    
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

        return  self.s3_bucket_raw_data_folders(year, month, day)
    
    def get_todays_path(self):
        return self.get_date_path(self.get_current_timestamp())

if __name__ == "__main__":
    reader = base_data_reader('Bybit','orderBook_200.100ms','BTCUSD')
    print(reader.get_todays_path())
