import datetime
from log_json import log_json
from osbot_utils.utils.Json import str_to_json
from pricebinance import PriceBinance, TOPIC_BINANCE_BINANCE

EX_BYBIT        = "ByBit"
EX_BYBIT_USDT   = "ByBit-USDT"
EX_BINANCE      = "Binanace"
EX_COINBASE     = "Coinbase"

TOPIC_BYBIT_INSURANCE   = "insurance"
TOPIC_BYBIT_KLINE       = "klineV2.1.BTCUSD"
TOPIC_BYBIT_OB200       = "orderBook_200.100ms.BTCUSD"
TOPIC_BYBIT_TRADE       = "trade"

TOPIC_BYBIT_USDT_CANDLE = "candle.1.BTCUSDT"
TOPIC_BYBIT_USDT_OB200  = "orderBook_200.100ms.BTCUSDT"
TOPIC_BYBIT_USDT_TRADE  = "trade.BTCUSDT"

TOPIC_COINBASE_BTCUSD   = "BTC-USD"
TOPIC_COINBASE_ETHUSD   = "ETH-USD"

class PriceInfo(object):
    def __init__(self):
        self.log = log_json()

    def getJson(self, symbol:str, price:float, timestamp:int):
        date = datetime.datetime.fromtimestamp(timestamp / 1e3).isoformat()
        return {
            "symbol"    : symbol,
            "price"     : price,
            "timestamp" : timestamp       
        }

    def process_raw_data(self, exchange:str, topic:str, data):
        json_data = {}
        try:
            json_data = str_to_json(data)
        except Exception as ex:
            self.log.create("ERROR", str(ex))
            return(None)

        # if EX_BYBIT         == exchange:        return self.process_bybit       (topic=topic, json_data=json_data)
        # if EX_BYBIT_USDT    == exchange:        return self.process_bybit_usdt  (topic=topic, json_data=json_data)
        # if EX_COINBASE      == exchange:        return self.process_coinbase    (topic=topic, json_data=json_data)
        if EX_BINANCE       == exchange:        return PriceBinance().process_json_data(topic=topic, json_data=json_data)

        self.log.create("ERROR", f'{exchange} EXCHANGE NOT SUPPOTED')
        return None
    
    def test_it():
        pass

if __name__ == '__main__':
    info = PriceInfo()

    raw_data = "\{\}"

    # print(info.process_raw_data(EX_BYBIT,TOPIC_BYBIT_INSURANCE,raw_data))
    # print(info.process_raw_data(EX_BYBIT,TOPIC_BYBIT_KLINE,raw_data))
    # print(info.process_raw_data(EX_BYBIT,TOPIC_BYBIT_OB200,raw_data))
    # print(info.process_raw_data(EX_BYBIT,TOPIC_BYBIT_TRADE,raw_data))

    # print(info.process_raw_data(EX_BYBIT_USDT,TOPIC_BYBIT_USDT_CANDLE,raw_data))
    # print(info.process_raw_data(EX_BYBIT_USDT,TOPIC_BYBIT_USDT_OB200,raw_data))
    # print(info.process_raw_data(EX_BYBIT_USDT,TOPIC_BYBIT_USDT_TRADE,raw_data))

    # print(info.process_raw_data(EX_COINBASE,TOPIC_COINBASE_BTCUSD,raw_data))
    # print(info.process_raw_data(EX_COINBASE,TOPIC_COINBASE_ETHUSD,raw_data))

    raw_data = "{\"stream\":\"btcusdt@aggTrade\",\"data\":{\"e\":\"aggTrade\",\"E\":1634390640539,\"a\":874355956,\"s\":\"BTCUSDT\",\"p\":\"60602.22\",\"q\":\"0.002\",\"f\":1546375311,\"l\":1546375311,\"T\":1634390640533,\"m\":false}}"
    print(info.process_raw_data(EX_BINANCE,TOPIC_BINANCE_BINANCE,raw_data))
