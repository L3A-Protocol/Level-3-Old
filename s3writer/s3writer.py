import os
import sys
import errno
from dotenv import load_dotenv
from osbot_utils.utils.Files import file_exists, file_write, file_delete
from osbot_utils.utils.Json import str_to_json
from s3_storage import s3_storage
from datetime import datetime

import math
import boto3
import numpy as np
import pandas
from botocore.client import Config

def readline(fifo):
    line = ''
    try:
        while True:
            line += fifo.read(1)
            if line.endswith('\n'):
                break
    except:
        pass
    return line

load_dotenv(override=True)
c_bin_path  = os.getenv("C_BINARY_PATH", None)
topic       = os.getenv("TOPIC", None)
bucket_name = os.getenv("BUCKET_NAME", None)

access_key_id       = os.getenv("AWS_ACCESS_KEY_ID", None)
access_secret_key   = os.getenv("AWS_SECRET_ACCESS_KEY", None)

if not c_bin_path:
    print ("The binary path is not specified")
    sys.exit()

if not topic:
    print ("The topic is not specified")
    sys.exit()

if not bucket_name:
    print ("The bucket_name is not specified")
    sys.exit()

if not file_exists(c_bin_path):
    print (f"File {c_bin_path} does not exist")
    sys.exit()

if not access_key_id:
    print (f"AWS access key is not specified")
    sys.exit()

if not access_secret_key:
    print (f"AWS secret key is not specified")
    sys.exit()

s3 = boto3.resource(
    's3',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=access_secret_key,
    config=Config(signature_version='s3v4')
)

# global book
# global snap_shot

book = pandas.DataFrame
snap_shot = pandas.DataFrame
old_timestamp = 0

# S3 = s3_storage()

# if not S3.bucket_exists(bucket_name):
#     print (f"Bucket {bucket_name} cannot be found")
#     sys.exit()

FIFO = f'/tmp/{topic}'

"""
The goal here is to capture all LOB events accurately for all pairs.
Microservice for ByBit, Web Socket limit order book snapshot then events.
All messages a grouped together in minute buckets, using their timestamps
this is so the files are exactly replicated, and recombined later. This  is for
sake of data accuracy.
We are buffering with pandas in case we need stats in the future, and for data checks.
This article inspired this approach.
https://medium.com/floating-point-group/collecting-and-distributing-high-resolution-crypto-market-data-with-ecs-s3-athena-lambda-and-9f0bd5ab3452
:return:
"""

dtypes = np.dtype([
    ('ws_seq_id', np.uint64),
    ('seq_id', np.uint64),
    ('action_id', np.uint8),
    ('price', np.float32),
    ('size', np.float32),
    ('symbol', np.str),
    ('side', np.uint8),
    ('year', np.uint16),
    ('month', np.uint8),
    ('day', np.uint8),
    ('exchange_unix_time', np.uint64),
    ('our_unix_time', np.uint64)
])
data = np.zeros(0, dtype=dtypes)
book = pandas.DataFrame(data)
dtypes = np.dtype([
    ('ws_seq_id', np.uint64),
    ('seq_id', np.uint64),
    ('price', np.float32),
    ('size', np.float32),
    ('symbol', np.str),
    ('side', np.uint8),
    ('year', np.uint16),
    ('month', np.uint8),
    ('day', np.uint8),
    ('exchange_unix_time', np.uint64),
    ('our_unix_time', np.uint64)
])
data = np.zeros(0, dtype=dtypes)
snap_shot = pandas.DataFrame(data)

def has_minute_increased(old_ts, new_ts):
    """
    compares the minute from the unix time stamp, if it increments returns true
    :param old_ts:
    :param new_ts:
    :return:
    """
    if old_ts == 0:
        return "Go"
    old = datetime.fromtimestamp(int(old_ts) / 1000000)
    new = datetime.fromtimestamp(int(new_ts) / 1000000)
    if new.minute > old.minute:
        return "Flush"
    else:
        return "Go"

def s3_bucket_folders(data, _symbol, year, month, day):
    return r'true-alpha/exchange=ByBit/'+data+r'/symbol='+_symbol+'/year='+str(year)+'/month=' + str(month) + '/day=' + str(day) + '/'

symbol_ws = topic

def process_message(message):
    global book
    global snap_shot
    global old_timestamp
    global s3

    now = datetime.utcnow()
    data = str_to_json(message)
    # print(f'on_message {data}')

    if not 'type' in data:
        print("type not found")
        return 1

    seq = data['cross_seq']
    timestamp_short = math.trunc(int(data['timestamp_e6'])/1000000)
    timestamp = data['timestamp_e6']
    year = datetime.utcfromtimestamp(timestamp_short).strftime('%Y')
    month = datetime.utcfromtimestamp(timestamp_short).strftime('%m')
    day = datetime.utcfromtimestamp(timestamp_short).strftime('%d')
    if data['type'] == 'delta':
        data = data['data']
        deletes = data['delete']
        updates = data['update']
        inserts = data['insert']
        if deletes:
            for delete in deletes:
                book = book.append({'ws_seq_id': seq,
                                    'seq_id': delete['id'],
                                    'action_id': 1,  # Delete
                                    'price': delete['price'],
                                    'size': 0,
                                    'symbol': symbol_ws,
                                    'side': 1 if delete['side'] == 'Buy' else 2,
                                    'year': int(year),
                                    'month': int(month),
                                    'day': int(day),
                                    'exchange_unix_time': timestamp,
                                     'our_unix_time': now}, ignore_index=True)
        if updates:
            for update in updates:
                book = book.append({'ws_seq_id': seq,
                                    'seq_id': update['id'],
                                    'action_id': 2,  # Update
                                    'price': update['price'],
                                    'size': update['size'],
                                    'symbol': symbol_ws,
                                    'side': 1 if update['side'] == 'Buy' else 2,
                                    'year': int(year),
                                    'month': int(month),
                                    'day': int(day),
                                    'exchange_unix_time': timestamp,
                                    'our_unix_time': now}, ignore_index=True)
        if inserts:
            for insert in inserts:
                book = book.append({'ws_seq_id': seq,
                                    'seq_id': insert['id'],
                                    'action_id': 3,  # Insert
                                    'price': insert['price'],
                                    'size': insert['size'],
                                    'symbol': symbol_ws,
                                    'side': 1 if insert['side'] == 'Buy' else 2,
                                    'year': int(year),
                                    'month': int(month),
                                    'day': int(day),
                                    'exchange_unix_time': timestamp,
                                    'our_unix_time': now}, ignore_index=True)
        # TODO: Finish s3 flush code for LOB
        if has_minute_increased(old_timestamp, timestamp) == "Flush":
            print(str(old_timestamp) + ' flush ' + str(timestamp))
            book_json = book.to_json(orient='records', lines=True)
            folders = s3_bucket_folders('lob_events', symbol_ws, year, month, day)
            s3.Bucket(bucket_name).put_object(Key=f'{folders}{seq}.json', Body=str(book_json))
            book.drop(book.index, inplace=True)
        old_timestamp = timestamp
    elif data['type'] == 'snapshot':
        data = data['data']
        limit_order_book = data['order_book']
        for price_level in limit_order_book:
            snap_shot = snap_shot.append({
                'ws_seq_id': seq,
                'seq_id': price_level['id'],
                'price': price_level['price'],
                'size': price_level['size'],
                'symbol': symbol_ws,
                'side': 1 if price_level['side'] == 'Buy' else 2,
                'year': int(year),
                'month': int(month),
                'day': int(day),
                'exchange_unix_time': timestamp,
                'our_unix_time': now}, ignore_index=True)
        snap_shot_json = snap_shot.to_json(orient='records', lines=True)
        folders = s3_bucket_folders('lob-snapshot', symbol_ws, year, month, day)
        s3.Bucket(bucket_name).put_object(Key=f'{folders}{seq}.json', Body=str(snap_shot_json))
        snap_shot.drop(snap_shot.index, inplace=True)  # Clear Snap Shot Buffer
    else:
        print("unknown - type!!!")
        # TODO: Need to close down Micro Service Task


try:
    os.system(f'{c_bin_path} --topic {topic} &')
except OSError as oe: 
    if oe.errno != errno.EEXIST:
        print (f'Failed to start {c_bin_path}')
        sys.exit()

try:
    os.mkfifo(FIFO)
except OSError as oe: 
    if oe.errno != errno.EEXIST:
        print (f"Failed to create the pipe: {FIFO}")
        sys.exit()

print("Opening FIFO...")
with open(FIFO) as fifo:
    print("FIFO opened")
    while True:
        line = readline(fifo)

        if not line:
            print("Writer closed")
            break

        if not line.endswith('}\n'):
            # not a valid JSON
            continue
        try:
            process_message(line)
        except Exception as ex:
            print (ex)