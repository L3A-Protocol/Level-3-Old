import json
import sys
import time
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

lob_received = pandas.DataFrame
lob_open = pandas.DataFrame
lob_done = pandas.DataFrame
lob_match = pandas.DataFrame
lob_change = pandas.DataFrame

# TODO:
snap_shot = pandas.DataFrame
old_timestamp = datetime.now()

if sys.argv[1] == 'BTC-USD':
    symbol_ws = 'BTC-USD'

if sys.argv[1] == 'ETH-USD':
    symbol_ws = 'ETH-USD'


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
    if new_ts.minute == 0 and old_ts.minute == 59:
        print("Flush")
        return "Flush"
    if new_ts.minute > old_ts.minute:
        print("Flush")
        return "Flush"
    else:
        return "Go"


def s3_bucket_folders(data, _symbol, year, month, day, hour):
    return r'true-alpha/exchange=Coinbase/' + data + r'/symbol=' + symbol_ws + '/year=' + str(year) + '/month=' + str(month) + '/day=' + str(day) + '/hour='+str(hour)+'/'


# TODO: Ping pong web socket server, then on timeout stop microservice task


def start():
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
    websocket.enableTrace(True)
    print("websocket trying to start...")

    ws = websocket.WebSocketApp('wss://ws-feed.pro.coinbase.com',
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open

    ws.run_forever(ping_interval=240, ping_timeout=90)
    print("websocket running..")

    ## TODO: Maybe i will add activate event ???


def on_message(ws, message):
    global lob_received
    global lob_open
    global lob_done
    global lob_match
    global lob_change

    global old_timestamp
    global s3

    now = datetime.now()
    item = json.loads(message)

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


def on_error(ws, error):
    print("error start")
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
    time.sleep(1)
    param = {'type': 'subscribe', 'channels': [{"name": "full", "product_ids": [symbol_ws]}]}
    ws.send(json.dumps(param))


if __name__ == "__main__":
    print("start")
    start()
