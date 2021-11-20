import datetime
from log_json import log_json
from osbot_utils.utils.Json import str_to_json

class PriceBase(object):
    def __init__(self):
        self.log = log_json()

    def getJson(self, symbol:str, price:float, timestamp:int):
        date = datetime.datetime.fromtimestamp(timestamp / 1e3).isoformat()
        return {
            "symbol"    : symbol,
            "price"     : price,
            "timestamp" : date
        }

    def process_json_data(self, topic:str, json_data):
        return []

