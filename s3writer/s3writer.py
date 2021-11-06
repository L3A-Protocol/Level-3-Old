import os
import sys
import errno
import signal
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

from log_json import log_json

from opensearchclient import OpenSearchClient, Index

# Variables

load_dotenv(override=True)
exchange    = os.getenv("EXCHANGE", None)
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

stop_it = False
osclient = None
data_index = None

# Functions

def handler(signum, frame):
    global stop_it
    stop_it = True

    print("")
    print("==> Stopping the application. Please allow some time for the theads to finish up gracefully")
    print("")

    if osclient and osclient.enabled and data_index:
        osclient.delete_index(data_index.name)

    sys.exit()

def get_current_timestamp():
    dt = datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    return utc_time.timestamp()

def s3_bucket_folders(data, _symbol, year, month, day):
    return f'true-alpha/exchange={exchange}/{data}/symbol={_symbol}/year={str(year)}/month={str(month)}/day={str(day)}/'

def s3_bucket_raw_data_folders(topic, year, month, day):
    return f'raw-data/exchange={exchange}/{topic}/year={str(year)}/month={str(month)}/day={str(day)}/'

class s3writer(object):
    def __init__(self):
        self.raw_lines = ''
        self.number_of_lines = 0
        self.old_flush_timestamp = 0
        self.mutex = Lock()

    def readline(self, fifo):
        line = ''
        try:
            while True:
                line += fifo.read(1)
                if line.endswith('\n'):
                    break
        except:
            pass
        return line

    def submit_line_to_opensearch(self, line):
        global data_index

        try:
            document = str_to_json(line)
            assert data_index.add_document(document=document)
        except Exception as ex:
            print(ex)

    def process_raw_line(self, line):
        self.submit_line_to_opensearch(line)

        self.mutex.acquire()
        try:
            self.raw_lines = self.raw_lines + line
            self.number_of_lines += 1
        finally:
            self.mutex.release()

    def verify_feed_frequency (self, timestamp, period):
        global feed_interval
        log = log_json()

        expected_feed = math.floor(period / feed_interval)

        details = {"details":
                    {
                        "timestamp":    timestamp,
                        "period":       period,
                        "lines_read":   self.number_of_lines,
                        "expected":     expected_feed
                    }
                }

        log.create("INFO","Latest feed frequency", details)

        if expected_feed > self.number_of_lines:
            # Allert low feed frequency
            log.create("ERROR", 'Low feed frequency')

    def flush_thread_function(self):
        global stop_it
        global s3

        if stop_it:
            return

        self.mutex.acquire()
        try:
            Timer(int(time()/60)*60+60 - time(), self.flush_thread_function).start ()

            utc_timestamp = get_current_timestamp()

            year = datetime.utcfromtimestamp(utc_timestamp).strftime('%Y')
            month = datetime.utcfromtimestamp(utc_timestamp).strftime('%m')
            day = datetime.utcfromtimestamp(utc_timestamp).strftime('%d')

            seq = (int)(utc_timestamp * 1000000)

            folders = s3_bucket_raw_data_folders(topic, year, month, day)
            if self.raw_lines:
                s3.Bucket(bucket_name).put_object(Key=f'{folders}{seq}', Body=self.raw_lines)

            period = math.floor((utc_timestamp - self.old_flush_timestamp) * 1000)
            self.verify_feed_frequency(seq, period)
            self.old_flush_timestamp = utc_timestamp

            self.raw_lines = ''
            self.number_of_lines = 0
        finally:
            self.mutex.release()

    def run(self):
        global stop_it
        global osclient
        global data_index

        log = log_json()

        if not exchange:
            log.create("ERROR", "The exchange is not specified")
            sys.exit()

        if not c_bin_path:
            log.create("ERROR", "The binary path is not specified")
            sys.exit()

        if not topic:
            log.create ("ERROR", "The topic is not specified")
            sys.exit()

        if not bucket_name:
            log.create ("ERROR" "The bucket_name is not specified")
            sys.exit()

        if not file_exists(c_bin_path):
            log.create ("ERROR", f"File {c_bin_path} does not exist")
            sys.exit()

        if not access_key_id:
            log.create ("ERROR", "AWS access key is not specified")
            sys.exit()

        if not access_secret_key:
            log.create ("ERROR", "AWS secret key is not specified")
            sys.exit()

        osclient = OpenSearchClient()
        if not osclient or not osclient.server_online():
            log.create ("ERROR", "Cannot access the OpenSearch host")
            sys.exit()

        data_index = Index(osclient, 'data', exchange=exchange, topic=topic)
        if not data_index.create():
            log.create ("ERROR", "Cannot create OpenSearch index")
            sys.exit()

        self.old_flush_timestamp = get_current_timestamp()

        x = Thread(target=self.flush_thread_function, args=())
        x.start()

        try:
            os.system(f'{c_bin_path} --topic {topic} &')
        except OSError as oe:
            if oe.errno != errno.EEXIST:
                log.create ('ERROR', f'Failed to start {c_bin_path}')
                sys.exit()

        FIFO = f'/tmp/{topic}'
        try:
            os.mkfifo(FIFO)
        except OSError as oe:
            if oe.errno != errno.EEXIST:
                log.create ("ERROR", f"Failed to create the pipe: {FIFO}")
                sys.exit()

        with open(FIFO) as fifo:
            while True:
                if stop_it:
                    sys.exit()

                line = self.readline(fifo)

                if not line:
                    log.create("ERROR", "No line in FIFO")
                    continue

                try:
                    self.process_raw_line(line)
                except Exception as ex:
                    log.create ('ERROR', f'process_raw_line: {ex}')
                    continue

if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)
    s3writer().run()