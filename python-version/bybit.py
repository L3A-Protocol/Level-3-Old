# 1
import json
import math
import time
import sys
from datetime import datetime

import boto3
import numpy as np
import pandas
import websocket
from botocore.client import Config

# TODO: Secure Keys
ACCESS_KEY_ID = 'AKIA5D5EI3WDT373UYSX'
ACCESS_SECRET_KEY = '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'

s3 = boto3.resource(
    's3',
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=ACCESS_SECRET_KEY,
    config=Config(signature_version='s3v4')
)

book = pandas.DataFrame
snap_shot = pandas.DataFrame
old_timestamp = 0
# BTCUSD ETHUSD BTCUSDT ETHUSDT
if sys.argv[1] == 'BTCUSD':
    symbol_ws = sys.argv[1]
elif sys.argv[1] == 'ETHUSD':
    symbol_ws = sys.argv[1]
elif sys.argv[1] == 'BTCUSDT':
    symbol_ws = sys.argv[1]
elif sys.argv[1] == 'ETHUSDT':
    symbol_ws = sys.argv[1]


# if sys.argv[2] == 'primary':
#     ingester = 'primary'
# elif sys.argv[2] == 'replica':
#     ingester = 'replica'


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
    return r'true-alpha/exchange=ByBit/'+data+r'/symbol='+symbol_ws+'/year='+str(year)+'/month=' + str(month) + '/day=' + str(day) + '/'

# TODO: Ping pong web socket server, then on timeout stop microservice task


def start():
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
    global book
    global snap_shot
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
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp('wss://stream.bybit.com/realtime_public',
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(ping_interval=60, ping_timeout=40)



def on_message(ws, message):
    global book
    global snap_shot
    global old_timestamp
    global s3

    now = datetime.utcnow()
    data = json.loads(message)

    if 'type' in data:
        pass
    else:
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
            s3.Bucket('btc.alpha').put_object(Key=folders+seq+'.json', Body=str(book_json))
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
        s3.Bucket('btc.alpha').put_object(Key=folders+seq+'.json', Body=str(snap_shot_json))
        snap_shot.drop(snap_shot.index, inplace=True)  # Clear Snap Shot Buffer
    else:
        print("unknown - type!!!")
        # TODO: Need to close down Micro Service Task


def on_error(ws, error):
    print(error)
    # TODO: Need to close down Micro Service Task
    on_close(ws)

def on_close(ws):
    print("### closed ###")
    # TODO: Need to close down Micro Service Task
    ws.close()
    time.sleep(2)
    start()

def on_open(ws):
    """
    This feed will first give a snapshot the a stream of lob events
    :param ws:
    :return:
    """
    print('open')
    time.sleep(1)
    param = {'op': 'subscribe', 'args': ['orderBookL2_25.' + symbol_ws]}
    ws.send(json.dumps(param))


if __name__ == "__main__":
    start()

