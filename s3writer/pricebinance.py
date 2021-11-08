import datetime
from log_json import log_json
from osbot_utils.utils.Json import str_to_json, json_to_str
from pricebase import PriceBase

TOPIC_BINANCE_BINANCE   = "binance"

class PriceBinance(PriceBase):
    def __init__(self):
        self.log = log_json()

    def verify_btcusdt_structure(self, json_data):
        if not 'stream' in json_data:
            return False

        if "btcusdt@aggTrade" != json_data['stream']:
            return False

        if not 'data' in json_data:
            return False

        data = json_data['data']

        if not "s" in data:
            return False

        if not "p" in data:
            return False

        if not "E" in data:
            return False

        if "BTCUSDT" != data["s"]:
            return False

        return True

    def process_json_data(self, topic:str, json_data):
        retval = []

        if TOPIC_BINANCE_BINANCE    == topic and self.verify_btcusdt_structure(json_data):
            symbol      = json_data["data"]["s"]
            price       = float(json_data["data"]["p"])
            timestamp   = int(json_data["data"]["E"])
            retval.append(self.getJson(symbol=symbol, price=price, timestamp=timestamp))

        return retval

if __name__ == '__main__':
    info = PriceBinance()

    json_data = {"stream":"btcusdt@aggTrade","data":{"e":"aggTrade","E":1634390640539,"a":874355956,"s":"BTCUSDT","p":"60602.22","q":"0.002","f":1546375311,"l":1546375311,"T":1634390640533,"m":"false"}}
    print(info.process_json_data(TOPIC_BINANCE_BINANCE,json_data))
