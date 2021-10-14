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
from botocore.client import Config

from threading import Timer, Thread, Lock
from time import time

# Variables

load_dotenv(override=True)
c_bin_path  = os.getenv("C_BINARY_PATH", None)
topic       = os.getenv("TOPIC", None)
bucket_name = os.getenv("BUCKET_NAME", None)

access_key_id       = os.getenv("AWS_ACCESS_KEY_ID", None)
access_secret_key   = os.getenv("AWS_SECRET_ACCESS_KEY", None)
feed_interval       = int(os.getenv("FEED_INTERVAL", 100))

s3 = boto3.resource(
    's3',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=access_secret_key,
    config=Config(signature_version='s3v4')
)

def get_current_timestamp():
    dt = datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    return utc_time.timestamp()

old_flush_timestamp = get_current_timestamp()
FIFO = f'/tmp/{topic}'
raw_lines = ''
number_of_lines = 0

mutex = Lock()

# Functions

def s3_bucket_folders(data, _symbol, year, month, day):
    return r'true-alpha/exchange=ByBit/'+data+r'/symbol='+_symbol+'/year='+str(year)+'/month=' + str(month) + '/day=' + str(day) + '/'

def s3_bucket_raw_data_folders(topic, year, month, day):
    return r'raw-data/exchange=ByBit/'+topic+r'/year='+str(year)+'/month=' + str(month) + '/day=' + str(day) + '/'

def verify_feed_frequency (number_of_lines, period):
    global feed_interval
    expected_feed = math.floor(period / feed_interval)

    log_line = {"period":period,"lines_read":number_of_lines,"expected":expected_feed}
    print(log_line)

    if expected_feed > number_of_lines:
        # Allert low feed frequency
        print(f'ERROR: low feed frequency: {number_of_lines}. Expected {expected_feed} for the period of {period} milliseconds')
    else:
        print(f'Expected feed frequency: {number_of_lines}. Expected {expected_feed} for the period of {period} milliseconds')

def process_raw_line(line):
    global raw_lines
    global number_of_lines

    mutex.acquire()
    try:
        raw_lines = raw_lines + line
        number_of_lines += 1
    finally:
        mutex.release()

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

def flush_thread_function():
    global raw_lines
    global number_of_lines
    global old_flush_timestamp

    mutex.acquire()
    try:
        Timer(int(time()/60)*60+60 - time(), flush_thread_function).start ()

        utc_timestamp = get_current_timestamp()
        print(utc_timestamp)

        year = datetime.utcfromtimestamp(utc_timestamp).strftime('%Y')
        month = datetime.utcfromtimestamp(utc_timestamp).strftime('%m')
        day = datetime.utcfromtimestamp(utc_timestamp).strftime('%d')

        seq = (int)(utc_timestamp * 1000000)

        folders = s3_bucket_raw_data_folders(topic, year, month, day)
        s3.Bucket(bucket_name).put_object(Key=f'{folders}{seq}', Body=raw_lines)

        period = math.floor((utc_timestamp - old_flush_timestamp) * 1000)
        verify_feed_frequency(number_of_lines, period)
        old_flush_timestamp = utc_timestamp

        raw_lines = ''
        number_of_lines = 0
    finally:
        mutex.release()

# Functional code

x = Thread(target=flush_thread_function, args=())
x.start()

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

