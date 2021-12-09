import os
import sys
import errno
import signal
import uuid
import select

from dotenv import load_dotenv
from osbot_utils.utils.Files import file_exists
from osbot_utils.utils.Json import str_to_json
from datetime import datetime
from datetime import timezone

import math

from threading import Timer, Thread, Lock
from time import time

from log_json import log_json
from opensearchclient import OpenSearchClient, Index
from priceinfo import PriceInfo, EX_BINANCE, EX_BYBIT, EX_BYBIT_USDT, EX_COINBASE
from sysinfo import SysInfo

from s3connector import s3connector

# Variables

load_dotenv(override=True)
exchange    = os.getenv("EXCHANGE", None)
c_bin_path  = os.getenv("C_BINARY_PATH", None)
topic       = os.getenv("TOPIC", None)
symbol      = os.getenv("SYMBOL", None)
bucket_name = os.getenv("BUCKET_NAME", None)
feed_interval = int(os.getenv("FEED_INTERVAL", 60000))

stop_it = False

# Functions

def handler(signum, frame):
    global stop_it
    stop_it = True

    print("")
    print("==> Stopping the application. Please allow some time for the theads to finish up gracefully")
    print("")

def get_current_timestamp():
    dt = datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    return utc_time.timestamp()

class s3writer(object):
    def __init__(self):
        self.raw_lines = ''
        self.number_of_lines = 0
        self.old_flush_timestamp = 0
        self.mutex = Lock()
        self.taskid = uuid.uuid4()
        self.verification_string = self.get_verification_string()
        self.topic_argument = self.get_topic_argument()
        self.priceinfo = PriceInfo(exchange, topic, symbol)
        self.connector = s3connector(exchange=exchange,topic=topic, symbol=symbol)
        self.osclient = OpenSearchClient()

        log = log_json()
        if not self.osclient or not self.osclient.server_online():
            log.create ("ERROR", "Cannot access the OpenSearch host")
            sys.exit()
        self.price_index = Index(self.osclient, 'price', exchange=exchange, topic=topic, taskid=self.taskid)

    def readline(self, fifo):
        line = ''
        try:
            while True:
                # verify FIFO is not empty
                # see https://stackoverflow.com/questions/21429369/read-file-with-timeout-in-python
                r, w, e = select.select([ fifo ], [], [], 0)
                if fifo in r:
                    line += fifo.read(1)
                    if line.endswith('\n'):
                        break
        except:
            pass
        if self.verification_string in line:
            return line
        return ''

    def get_verification_string(self):
        if EX_BYBIT == exchange:
            if 'orderBook_200.100ms' == topic:
                return f'"{topic}.{symbol}"'
            if 'trade' == topic:
                return f'"{topic}.{symbol}"'
            if 'klineV2.1' == topic:
                return f'"{topic}.{symbol}"'
            if 'insurance' == topic:
                return f'"{topic}.{symbol}"'

        if EX_BYBIT_USDT == exchange:
            if 'orderBook_200.100ms' == topic:
                return f'"{topic}.{symbol}"'
            if 'trade' == topic:
                return f'"{topic}.{symbol}"'
            if 'candle.1' == topic:
                return f'"{topic}.{symbol}"'

        if EX_COINBASE == exchange:
            return f'"{symbol}"'

        if EX_BINANCE == exchange:
            return f'"{symbol.lower()}@{topic}"'

        return f'"{symbol}"'

    def get_topic_argument(self):
        if EX_BYBIT == exchange:
            if 'orderBook_200.100ms' == topic:
                return f'{topic}.{symbol}'
            if 'klineV2.1' == topic:
                return f'{topic}.{symbol}'

        if EX_BYBIT_USDT == exchange:
            if 'orderBook_200.100ms' == topic:
                return f'{topic}.{symbol}'
            if 'candle.1' == topic:
                return f'{topic}.{symbol}'
            if 'trade' == topic:
                return f'{topic}.{symbol}'

        if EX_COINBASE == exchange:
            return f'{symbol}'

        if EX_BINANCE == exchange:
            return f'{symbol.lower()}@{topic}'

        return topic

    def update_policy_file(self):
        binance_policypath='/app/binance-policy.json'
        if EX_BINANCE == exchange:
            fin = open(binance_policypath, "rt")
            data = fin.read()
            data = data.replace('*-topic-*', self.topic_argument)
            fin.close()
            fin = open(binance_policypath, "wt")
            fin.write(data)
            fin.close()

    def submit_line_to_opensearch(self, line):
        try:
            price_data = self.priceinfo.process_raw_data(exchange=exchange, data=line)
            for item in price_data:
                if 'timestamp' in item:
                    # price_index.add_document(document=item, timestamp=item['timestamp'])
                    self.price_index.add_document(document=item)
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

        if stop_it:
            print('flush_thread stopped')
            return

        self.mutex.acquire()
        try:
            Timer(int(time()/60)*60+60 - time(), self.flush_thread_function).start ()

            utc_timestamp = self.connector.get_current_timestamp()

            self.connector.save_text_file(utc_timestamp=utc_timestamp, body=self.raw_lines)

            period = math.floor((utc_timestamp - self.old_flush_timestamp) * 1000)
            self.verify_feed_frequency(utc_timestamp, period)
            self.old_flush_timestamp = utc_timestamp

            self.raw_lines = ''
            self.number_of_lines = 0
        finally:
            self.mutex.release()

    def run(self):
        global stop_it

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

        if not symbol:
            log.create ("ERROR", "The symbol is not specified")
            sys.exit()

        if not bucket_name:
            log.create ("ERROR" "The bucket_name is not specified")
            sys.exit()

        if not file_exists(c_bin_path):
            log.create ("ERROR", f"File {c_bin_path} does not exist")
            sys.exit()

        self.old_flush_timestamp = get_current_timestamp()

        try:
            self.update_policy_file()
            os.system(f'{c_bin_path} --topic {self.topic_argument} &')
        except OSError as oe:
            if oe.errno != errno.EEXIST:
                log.create ('ERROR', f'Failed to start {c_bin_path}')
                sys.exit()

        FIFO = f'/tmp/{self.topic_argument}'
        try:
            os.mkfifo(FIFO)
        except OSError as oe:
            if oe.errno != errno.EEXIST:
                log.create ("ERROR", f"Failed to create the pipe: {FIFO}")
                sys.exit()

        sys_info = SysInfo(self.osclient, exchange, topic, self.taskid)
        sys_info.Start()

        data_thread = Thread(target=self.flush_thread_function, args=())
        data_thread.start()

        with open(FIFO) as fifo:
            while True:
                if stop_it:
                    print('FIFO reader stopped')
                    break

                line = self.readline(fifo)

                if not line:
                    continue

                try:
                    self.process_raw_line(line)
                except Exception as ex:
                    log.create ('ERROR', f'process_raw_line: {ex}')
                    continue

        data_thread.join()
        sys_info.Stop()

        self.price_index.delete()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)
    s3writer().run()