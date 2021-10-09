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

def initialize():
    print("start")
    global old_timestamp
    global lob_received

    dtypes = np.dtype([
        ('type', str),
        ('time', str),
        ('product_id', str),
        ('sequence', np.float64),
        ('order_id', str),
        ('size', np.float64),
        ('price', np.float64),
        ('side', str),
        ('order_type', str),
        ('now', str)
    ])
    data = np.zeros(0, dtype=dtypes)
    lob_received = pandas.DataFrame(data)

    global lob_open
    dtypes = np.dtype([
        ('type', str),
        ('time', str),
        ('product_id', str),
        ('sequence', np.float64),
        ('order_id', str),
        ('price', np.float64),
        ('remaining_size', np.float64),
        ('side', str),
        ('now', str)
    ])
    data = np.zeros(0, dtype=dtypes)
    lob_open = pandas.DataFrame(data)

    global lob_done
    dtypes = np.dtype([
        ('type', str),
        ('time', str),
        ('product_id', str),
        ('sequence', np.float64),
        ('price', np.float64),
        ('order_id', str),
        ('reason', str),  # cancelled or filled
        ('remaining_size', np.float64),  # has to be zero, end of the limit order life cycle
        ('side', str),
        ('now', str)
    ])
    data = np.zeros(0, dtype=dtypes)
    lob_done = pandas.DataFrame(data)

    global lob_match
    dtypes = np.dtype([
        ('type', str),
        ('time', str),
        ('trade_id', str),
        ('product_id', str),
        ('sequence', np.float64),
        ('maker_order_id', str),
        ('taker_order_id', str),
        ('price', np.float64),
        ('size', np.float64),
        ('side', str),
        ('now', str)
    ])
    data = np.zeros(0, dtype=dtypes)
    lob_match = pandas.DataFrame(data)
    # ignore change in funds not related to limit order book, come through in match
    global lob_change
    dtypes = np.dtype([
        ('type', str),
        ('time', str),
        ('product_id', str),
        ('sequence', np.float64),
        ('order_id', str),
        ('price', np.float64),
        ('new_size', np.float64),
        ('old_size', np.float64),
        ('side', str),
        ('now', str)
    ])
    data = np.zeros(0, dtype=dtypes)
    lob_change = pandas.DataFrame(data)

def process_json_data(json_string):
    global lob_received
    global lob_open
    global lob_done
    global lob_match
    global lob_change

    global old_timestamp
    global s3

    now = datetime.now()
    item = str_to_json(json_string)

    if 'type' in item:
        seq = item['sequence']
        pass
    else:
        return 1

    timestamp = now

    if item['type'] == 'received':
        lob_received = lob_received.append({'type': item['type'],
                                            'time': item['time'],
                                            'product_id': item['product_id'],
                                            'sequence': item['sequence'],
                                            'order_id': item['order_id'],
                                            'size': item['size'],
                                            'price': item['price'],
                                            'side': item['side'],
                                            'order_type': item['order_type'],
                                            'now': now
                                            }, ignore_index=True)

    elif item['type'] == 'open':
        lob_open = lob_open.append({'type': item['type'],
                                    'time': item['time'],
                                    'product_id': item['product_id'],
                                    'sequence': item['sequence'],
                                    'order_id': item['order_id'],
                                    'price': item['price'],
                                    'remaining_size': item['remaining_size'],
                                    'side': item['side'],
                                    'now': now
                                    }, ignore_index=True)

    elif item['type'] == 'done':
        #print("done")
        lob_done = lob_done.append({'type': item['type'],
                                    'time': item['time'],
                                    'product_id': item['product_id'],
                                    'sequence': item['sequence'],
                                    'order_id': item['order_id'],
                                    'remaining_size': item['remaining_size'],
                                    'price': item['price'],
                                    'side': item['side'],
                                    'reason': item['reason'],
                                    'now': now
                                    }, ignore_index=True)

    elif item['type'] == 'match':
        lob_match = lob_match.append({'type': item['type'],
                                      'time': item['time'],
                                      'trade_id': item['trade_id'],
                                      'product_id': item['product_id'],
                                      'sequence': item['sequence'],
                                      'maker_order_id': item['maker_order_id'],
                                      'taker_order_id': item['taker_order_id'],
                                      'price': item['price'],
                                      'size': item['size'],
                                      'side': item['side'],
                                      'now': now
                                      }, ignore_index=True)

    elif item['type'] == 'change':
        #print('change')
        lob_change = lob_change.append({'type': item['type'],
                                        'time': item['time'],
                                        'product_id': item['product_id'],
                                        'sequence': item['sequence'],
                                        'order_id': item['maker_order_id'],
                                        'price': item['price'],
                                        'new_size': item['new_size'],
                                        'old_size': item['old_size'],
                                        'side': item['side'],
                                        'now': now
                                        }, ignore_index=True)

    else:
        print("unknown - type!!!" + item['type'])
        # TODO: Need to close down Micro Service Task

    if has_minute_increased(old_timestamp, timestamp) == "Flush":
        print(str(old_timestamp) + ' flush ' + str(timestamp))
        lob_received_json = lob_received.to_json(orient='records', lines=True)
        lob_open_json = lob_open.to_json(orient='records', lines=True)
        lob_done_json = lob_done.to_json(orient='records', lines=True)
        lob_match_json = lob_match.to_json(orient='records', lines=True)
        lob_change_json = lob_change.to_json(orient='records', lines=True)
        folders = s3_bucket_folders('lob_events', symbol_ws, now.year, now.month, now.day, now.hour)
        s3.Bucket('btc.alpha').put_object(Key=folders + str(seq) + '_received.json', Body=str(lob_received_json))
        s3.Bucket('btc.alpha').put_object(Key=folders + str(seq) + '_open.json', Body=str(lob_open_json))
        s3.Bucket('btc.alpha').put_object(Key=folders + str(seq) + '_done.json', Body=str(lob_done_json))
        s3.Bucket('btc.alpha').put_object(Key=folders + str(seq) + '_match.json', Body=str(lob_match_json))
        s3.Bucket('btc.alpha').put_object(Key=folders + str(seq) + '_change.json', Body=str(lob_change_json))

        lob_received.drop(lob_received.index, inplace=True)
        lob_open.drop(lob_open.index, inplace=True)
        lob_done.drop(lob_done.index, inplace=True)
        lob_match.drop(lob_match.index, inplace=True)
        lob_change.drop(lob_change.index, inplace=True)

        old_timestamp = timestamp

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

initialize()

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

        if not line.endswith('}\n'):
            # not a valid JSON
            continue

        try:
            process_json_data(line)
        except Exception as ex:
            print (f'ERROR in process_json_data: {ex}')
            continue
