import datetime
from log_json import log_json
from osbot_utils.utils.Json import str_to_json
from pricebase import PriceBase

TOPIC_BYBIT_USDT_CANDLE = "candle.1.BTCUSDT"
TOPIC_BYBIT_USDT_OB200  = "orderBook_200.100ms.BTCUSDT"
TOPIC_BYBIT_USDT_TRADE  = "trade.BTCUSDT"

class PriceBybitUSDT(PriceBase):

    def process_json_data(self, topic:str, json_data):
        retval = []

        if TOPIC_BYBIT_USDT_CANDLE    == topic:
            pass
        elif TOPIC_BYBIT_USDT_OB200      == topic:
            pass
        elif TOPIC_BYBIT_USDT_TRADE      == topic:
            pass

        # return self.getJson(symbol=symbol, price=price, timestamp=timestamp)
        return retval

if __name__ == '__main__':
    info = PriceBybitUSDT()

    json_data = {}

    print(info.process_json_data(TOPIC_BYBIT_USDT_CANDLE,json_data))
    print(info.process_json_data(TOPIC_BYBIT_USDT_OB200,json_data))
    print(info.process_json_data(TOPIC_BYBIT_USDT_TRADE,json_data))

