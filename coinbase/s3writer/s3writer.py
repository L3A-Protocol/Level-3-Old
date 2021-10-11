import os
import sys
import errno
from dotenv import load_dotenv
from osbot_utils.utils.Files import file_exists
from osbot_utils.utils.Json import str_to_json
from datetime import datetime
from datetime import timezone

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

lob_received = pandas.DataFrame
lob_open = pandas.DataFrame
lob_done = pandas.DataFrame
lob_match = pandas.DataFrame
lob_change = pandas.DataFrame

# TODO:
snap_shot = pandas.DataFrame
old_timestamp = 0
old_raw_data_timestamp = 0

FIFO = f'/tmp/{topic}'

raw_lines = ''

def has_minute_increased(old_ts, new_ts):
    """
    compares the minute from the unix time stamp, if it increments returns true
    :param old_ts:
    :param new_ts:
    :return:
    """
    if old_ts == 0:
        return "Go"

    old_min = datetime.utcfromtimestamp(old_ts).strftime('%M')
    new_min = datetime.utcfromtimestamp(new_ts).strftime('%M')

    if old_min != new_min:
        return "Flush"
    else:
        return "Go"

def s3_bucket_folders(data, _symbol, year, month, day):
    return r'true-alpha/exchange=Coinbase/'+data+r'/symbol='+_symbol+'/year='+str(year)+'/month=' + str(month) + '/day=' + str(day) + '/'

def s3_bucket_raw_data_folders(topic, year, month, day):
    return r'raw-data/exchange=Coinbase/'+topic+r'/year='+str(year)+'/month=' + str(month) + '/day=' + str(day) + '/'

symbol_ws = topic

def process_raw_line(line):
    global raw_lines
    global old_raw_data_timestamp

    raw_lines = raw_lines + line

    dt = datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()

    year = datetime.utcfromtimestamp(utc_timestamp).strftime('%Y')
    month = datetime.utcfromtimestamp(utc_timestamp).strftime('%m')
    day = datetime.utcfromtimestamp(utc_timestamp).strftime('%d')

    seq = (int)(utc_timestamp * 1000000)

    if has_minute_increased(old_raw_data_timestamp, utc_timestamp) == "Flush":
        # print(str(old_raw_data_timestamp) + ' flush ' + str(utc_timestamp))
        folders = s3_bucket_raw_data_folders(topic, year, month, day)
        s3.Bucket(bucket_name).put_object(Key=f'{folders}{seq}', Body=raw_lines)
        raw_lines = ''

    old_raw_data_timestamp = utc_timestamp

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

with open(FIFO) as fifo:
    print(f'FIFO {FIFO} opened')
    while True:
        line = readline(fifo)

        if not line:
            print("Writer closed")
            break

        try:
            process_raw_line(line)
        except Exception as ex:
            print (f'ERROR in process_raw_line: {ex}')
            continue
