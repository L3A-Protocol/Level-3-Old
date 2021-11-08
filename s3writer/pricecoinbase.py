import datetime
from log_json import log_json
from osbot_utils.utils.Json import str_to_json
from pricebase import PriceBase

TOPIC_COINBASE_BTCUSD   = "BTC-USD"
TOPIC_COINBASE_ETHUSD   = "ETH-USD"

class PriceCoinbase(PriceBase):

    def process_json_data(self, topic:str, json_data):
        retval = []

        if TOPIC_COINBASE_BTCUSD    == topic:
            pass
        elif TOPIC_COINBASE_ETHUSD  == topic:
            pass

        # return self.getJson(symbol=symbol, price=price, timestamp=timestamp)
        return retval

if __name__ == '__main__':
    info = PriceCoinbase()

    json_data = {}
    print(info.process_json_data(TOPIC_COINBASE_BTCUSD,json_data))
    print(info.process_json_data(TOPIC_COINBASE_ETHUSD,json_data))
