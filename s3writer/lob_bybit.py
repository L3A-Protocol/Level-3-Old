from os import EX_CANTCREAT
from log_json import log_json
from s3connector import s3connector

LOB_BYBIT_EXCHANGE = 'ByBit'
LOB_BYBIT_TOPIC = 'orderBook_200.100ms'

class lob_bybit(object):
    def __init__(self, symbol:str):
        self.connector = s3connector(exchange=LOB_BYBIT_EXCHANGE, topic=LOB_BYBIT_TOPIC, symbol=symbol)
        self.log = log_json()

    def process_the_latest_s3_file(self):
        lines = []

        list = self.connector.get_latest_file_list()
        if list is None:
            print('Nothing in the list')
            return lines

        for key in list:
            lines.extend(self.connector.get_s3_object(key))
        return lines

if __name__ == "__main__":
    lob = lob_bybit(symbol='BTCUSD')
    lines = lob.process_the_latest_s3_file()
    for line in lines:
        print (line)
    print(f'lines printed {len(lines)}')


