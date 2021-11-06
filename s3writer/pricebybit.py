import datetime
from log_json import log_json
from osbot_utils.utils.Json import str_to_json
from pricebase import PriceBase

TOPIC_BYBIT_INSURANCE   = "insurance"
TOPIC_BYBIT_KLINE       = "klineV2.1.BTCUSD"
TOPIC_BYBIT_OB200       = "orderBook_200.100ms.BTCUSD"
TOPIC_BYBIT_TRADE       = "trade"

class PriceBybit(PriceBase):
    def __init__(self):
        self.log = log_json()

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

    def process_json_data(self, topic:str, json_data):
        retval = None

        if TOPIC_BYBIT_INSURANCE    == topic:
            return retval
        elif TOPIC_BYBIT_KLINE      == topic:
            pass
        elif TOPIC_BYBIT_OB200      == topic:
            pass
        elif TOPIC_BYBIT_TRADE      == topic and self.verify_trade_structure(json_data):
            data = json_data['data']
            for entry in data:
                symbol  = entry["symbol"]
                price   = float(entry["price"])
                timestamp = float(entry["trade_time_ms"])
                retval = self.getJson(symbol=symbol, price=price, timestamp=timestamp)
                # TODO: process all entries
                break

        return retval

if __name__ == '__main__':
    info = PriceBybit()

    json_data = {"topic":"insurance.ETH","data":[{"currency":"ETH","timestamp":"2021-10-15T20:00:00Z","wallet_balance":4832029953542}]}
    print(info.process_json_data(TOPIC_BYBIT_INSURANCE,json_data))

    print(info.process_json_data(TOPIC_BYBIT_KLINE,json_data))

    print(info.process_json_data(TOPIC_BYBIT_OB200,json_data))

    json_data = {"topic":"trade.XRPUSD","data":[{"trade_time_ms":1634342763132,"timestamp":"2021-10-16T00:06:03.000Z","symbol":"XRPUSD","side":"Sell","size":1094,"price":1.1441,"tick_direction":"MinusTick","trade_id":"a6aa635a-89f7-5fd5-a29d-df9f0b13d937","cross_seq":3780829306},{"trade_time_ms":1634342763132,"timestamp":"2021-10-16T00:06:03.000Z","symbol":"XRPUSD","side":"Sell","size":200,"price":1.1441,"tick_direction":"ZeroMinusTick","trade_id":"ea2dcc4c-26f4-5a19-ba7b-2fc187b9b37b","cross_seq":3780829306},{"trade_time_ms":1634342763132,"timestamp":"2021-10-16T00:06:03.000Z","symbol":"XRPUSD","side":"Sell","size":4,"price":1.1441,"tick_direction":"ZeroMinusTick","trade_id":"aeaeaa83-79cb-5f80-887f-9e527153b6fb","cross_seq":3780829306},{"trade_time_ms":1634342763132,"timestamp":"2021-10-16T00:06:03.000Z","symbol":"XRPUSD","side":"Sell","size":9735,"price":1.1439,"tick_direction":"MinusTick","trade_id":"b3942a44-639c-5365-a82b-7ac67dd097e4","cross_seq":3780829306}]}
    print(info.process_json_data(TOPIC_BYBIT_TRADE,json_data))

