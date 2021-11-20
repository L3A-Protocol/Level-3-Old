import datetime
from log_json import log_json
from osbot_utils.utils.Json import str_to_json
from pricebase import PriceBase

TOPIC_BYBIT_INSURANCE   = "insurance"
TOPIC_BYBIT_KLINE       = "klineV2.1"
TOPIC_BYBIT_OB200       = "orderBook_200.100ms"
TOPIC_BYBIT_TRADE       = "trade"

class PriceBybit(PriceBase):
    def __init__(self, topic, symbol):
        self.log = log_json()
        self.topic = topic
        self.symbol = symbol
        self.process_json_data = self.process_none

        if TOPIC_BYBIT_INSURANCE    == topic:
            self.process_json_data = self.process_none
        elif TOPIC_BYBIT_KLINE      == topic:
            self.process_json_data = self.process_kline
        elif TOPIC_BYBIT_OB200      == topic:
            self.process_json_data = self.process_ob200
        elif TOPIC_BYBIT_TRADE      == topic:
            self.process_json_data = self.process_trade

    def verify_trade_structure(self, json_data):
        if not 'topic' in json_data:
            return False

        if not 'data' in json_data:
            return False

        data = json_data['data']

        for entry in data:
            if not "trade_time_ms" in entry:
                return False
            if not "symbol" in entry:
                return False
            if not "price" in entry:
                return False
            break

        return True

    def verify_ob200_structure(self, json_data):
        if not 'topic' in json_data:
            return False

        if not 'data' in json_data:
            return False

        if not 'timestamp_e6' in json_data:
            return False

        data = json_data['data']

        if not 'insert' in data:
            return False

        for entry in data['insert']:
            if not "symbol" in entry:
                return False
            if not "price" in entry:
                return False
            break

        return True

    def verify_kline_structure(self, json_data):
        if not 'topic' in json_data:
            return False

        if not 'data' in json_data:
            return False

        if not 'timestamp_e6' in json_data:
            return False

        for entry in json_data['data']:
            if not "close" in entry:
                return False
            break

        return True

    def process_kline(self, json_data):
        retval = []
        for entry in json_data['data']:
            price   = float(entry["close"])
            timestamp = int(json_data["timestamp_e6"]) / 1e3
            retval.append(self.getJson(symbol=self.symbol, price=price, timestamp=timestamp))
        return retval

    def process_ob200(self, json_data):
        retval = []
        if not self.verify_ob200_structure(json_data):
            return retval

        insert = json_data['data']['insert']
        for entry in insert:
            price   = float(entry["price"])
            timestamp = int(json_data["timestamp_e6"]) / 1e3
            retval.append(self.getJson(symbol=self.symbol, price=price, timestamp=timestamp))
        return retval

    def process_trade(self, json_data):
        retval = []
        if not  self.verify_trade_structure(json_data):
            return retval

        data = json_data['data']
        for entry in data:
            price   = float(entry["price"])
            timestamp = int(entry["trade_time_ms"])
            retval.append(self.getJson(symbol=self.symbol, price=price, timestamp=timestamp))
        return retval

    # def process_json_data(self, topic:str, json_data):
    #     return self.process_topic_data(json_data)

if __name__ == '__main__':
    info = PriceBybit()

    json_data = {"topic":"insurance.ETH","data":[{"currency":"ETH","timestamp":"2021-10-15T20:00:00Z","wallet_balance":4832029953542}]}
    print(info.process_json_data(json_data))

    json_data = {"topic":"klineV2.1.BTCUSD","data":[{"start":1636174500,"end":1636174560,"open":61271,"close":61271,"high":61271,"low":61270.5,"volume":32951,"turnover":0.5377931700000002,"timestamp":1636174529019904,"confirm":"false","cross_seq":10550389298}],"timestamp_e6":1636174529026740}
    print(info.process_json_data(json_data))

    json_data = {"topic":"orderBook_200.100ms.BTCUSD","type":"delta","data":{"delete":[{"price":"61177.00","symbol":"BTCUSD","id":611770000,"side":"Sell"},{"price":"60955.50","symbol":"BTCUSD","id":609555000,"side":"Buy"}],"update":[{"price":"61017.00","symbol":"BTCUSD","id":610170000,"side":"Buy","size":1929},{"price":"60965.50","symbol":"BTCUSD","id":609655000,"side":"Buy","size":10149},{"price":"61076.00","symbol":"BTCUSD","id":610760000,"side":"Sell","size":18},{"price":"60916.50","symbol":"BTCUSD","id":609165000,"side":"Buy","size":3500}],"insert":[{"price":"61051.50","symbol":"BTCUSD","id":610515000,"side":"Sell","size":20000},{"price":"60902.00","symbol":"BTCUSD","id":609020000,"side":"Buy","size":335024}],"transactTimeE6":0},"cross_seq":10548595035,"timestamp_e6":1636156902211277}
    print(info.process_json_data(json_data))

    json_data = {"topic":"trade.XRPUSD","data":[{"trade_time_ms":1634342763132,"timestamp":"2021-10-16T00:06:03.000Z","symbol":"XRPUSD","side":"Sell","size":1094,"price":1.1441,"tick_direction":"MinusTick","trade_id":"a6aa635a-89f7-5fd5-a29d-df9f0b13d937","cross_seq":3780829306},{"trade_time_ms":1634342763132,"timestamp":"2021-10-16T00:06:03.000Z","symbol":"XRPUSD","side":"Sell","size":200,"price":1.1441,"tick_direction":"ZeroMinusTick","trade_id":"ea2dcc4c-26f4-5a19-ba7b-2fc187b9b37b","cross_seq":3780829306},{"trade_time_ms":1634342763132,"timestamp":"2021-10-16T00:06:03.000Z","symbol":"XRPUSD","side":"Sell","size":4,"price":1.1441,"tick_direction":"ZeroMinusTick","trade_id":"aeaeaa83-79cb-5f80-887f-9e527153b6fb","cross_seq":3780829306},{"trade_time_ms":1634342763132,"timestamp":"2021-10-16T00:06:03.000Z","symbol":"XRPUSD","side":"Sell","size":9735,"price":1.1439,"tick_direction":"MinusTick","trade_id":"b3942a44-639c-5365-a82b-7ac67dd097e4","cross_seq":3780829306}]}
    print(info.process_json_data(json_data))

