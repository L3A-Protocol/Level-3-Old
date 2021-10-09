import json
import sys
import time
import zlib
from datetime import datetime

import boto3
import pandas
import websocket
from botocore.client import Config
seq = 0
# TODO: Secure Keys
ACCESS_KEY_ID = 'AKIA5D5EI3WDT373UYSX'
ACCESS_SECRET_KEY = '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'
book = []

s3 = boto3.resource(
    's3',
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=ACCESS_SECRET_KEY,
    config=Config(signature_version='s3v4')
)

snap_shot = pandas.DataFrame
old_timestamp = datetime.now
# BTCUSDT PERP
if sys.argv[1] == 'BTC-USDT':
    symbol_ws = sys.argv[1]
if sys.argv[1] == 'ETH-USDT':
    symbol_ws = sys.argv[1]



def has_minute_increased(old_ts, new_ts):
    """
    compares the minute from the unix time stamp, if it increments returns true
    :param old_ts:
    :param new_ts:
    :return:
    """
    if old_ts == 0:
        return "Go"

    if new_ts.minute > old_ts.minute:
        return "Flush"
    else:
        return "Go"


def s3_bucket_folders(data, _symbol, year, month, day):
    return r'true-alpha/exchange=Okex/' + data + r'/symbol=' + symbol_ws + '/year=' + str(year) + '/month=' + str(month) + '/day=' + str(day) + '/'


# TODO: Ping pong web socket server, then on timeout stop microservice task


def start():
    print("start")
    global old_timestamp
    old_timestamp = datetime.utcnow()
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp('wss://real.okex.com:8443/ws/v3',
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(ping_interval=60, ping_timeout=40)


def on_message(ws, message):
    global old_timestamp
    global s3
    global book
    global seq
    now = datetime.utcnow()
    message = zlib.decompress(message, -zlib.MAX_WBITS)
    message = message.decode('utf-8')
    print(message)
    data = json.loads(message)
    book.append(data)

    seq = seq + 1#data['data']['microtimestamp']
    print(str(old_timestamp) + 'before flush ' + str(now))
    if has_minute_increased(old_timestamp, now) == "Flush":
        print(str(old_timestamp) + ' flush ' + str(now))
        book_json = json.dumps(book)
        folders = s3_bucket_folders('lob-snapshot', symbol_ws, now.year, now.month, now.day)
        s3.Bucket('btc.alpha').put_object(Key=folders + str(seq) + '.json', Body=str(book_json))
        book.clear()
        old_timestamp = now


def on_error(ws, error):
    print(error)
    # TODO: Need to close down Micro Service Task
    on_close(ws)

def on_close(ws):
    print("### closed ###")
    # TODO: Need to close down Micro Service Task
    time.sleep(2)
    ws.close()
    start()


def on_open(ws):
    """
    This feed will first give a snapshot the a stream of lob events
    :param ws:
    :return:
    """
    time.sleep(1)
    msg = \
        {"op": "subscribe", "args": ["spot/depth5:" + symbol_ws]}
    ws.send(json.dumps(msg))


if __name__ == "__main__":
    start()

