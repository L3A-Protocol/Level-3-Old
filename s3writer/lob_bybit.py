from os import EX_CANTCREAT
from log_json import log_json
from s3connector import s3connector

LOB_BYBIT_EXCHANGE = 'ByBit'
LOB_BYBIT_TOPIC = 'orderBook_200.100ms'

class lob_bybit(object):
    def __init__(self, symbol:str):
        self.connector = s3connector(exchange=LOB_BYBIT_EXCHANGE, topic=LOB_BYBIT_TOPIC, symbol=symbol)
        self.log = log_json()

if __name__ == "__main__":
    lob = lob_bybit(symbol='BTCUSD')

