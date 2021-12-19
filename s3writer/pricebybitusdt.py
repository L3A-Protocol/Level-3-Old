import datetime
from s3writer.log_json import log_json
from osbot_utils.utils.Json import str_to_json
from s3writer.pricebase import PriceBase

TOPIC_BYBIT_USDT_CANDLE = "candle.1"
TOPIC_BYBIT_USDT_OB200  = "orderBook_200.100ms"
TOPIC_BYBIT_USDT_TRADE  = "trade"

class PriceBybitUSDT(PriceBase):
    def __init__(self, topic, symbol):
        self.log = log_json()
        self.topic = topic
        self.symbol = symbol
        self.process_json_data = self.process_none

    # def process_candle(self, topic:str, json_data):
    #     retval = []

    #     if TOPIC_BYBIT_USDT_CANDLE    == topic:
    #         pass
    #     elif TOPIC_BYBIT_USDT_OB200      == topic:
    #         pass
    #     elif TOPIC_BYBIT_USDT_TRADE      == topic:
    #         pass

    #     # return self.getJson(symbol=symbol, price=price, timestamp=timestamp)
    #     return retval

if __name__ == '__main__':
    info = PriceBybitUSDT()

    json_data = {}

    # print(info.process_json_data(TOPIC_BYBIT_USDT_CANDLE,json_data))
    # print(info.process_json_data(TOPIC_BYBIT_USDT_OB200,json_data))
    # print(info.process_json_data(TOPIC_BYBIT_USDT_TRADE,json_data))

