
import json

from log_json import log_json
from s3connector import s3connector

LOB_BYBIT_EXCHANGE = 'ByBit'
LOB_BYBIT_TOPIC = 'orderBook_200.100ms'

class lob_bybit(object):
    def __init__(self, symbol:str):
        self.connector = s3connector(exchange=LOB_BYBIT_EXCHANGE, topic=LOB_BYBIT_TOPIC, symbol=symbol)
        self.log = log_json()

    def verify_json(self, line_json):
        return False

    def process_single_line(self, line):
        try:
            line_json = json.loads(line)
        except Exception as ex:
            print (ex)

    def process_the_latest_s3_file(self):
        lines = []

        list = self.connector.get_latest_file_list()
        if list is None:
            print('Nothing in the list')
            return lines

        for key in list:
            lines.extend(self.connector.get_s3_object(key))
        return lines

test_line = '{"topic":"orderBook_200.100ms.BTCUSD","type":"delta","data":{"delete":[{"price":"46951.00","symbol":"BTCUSD","id":469510000,"side":"Buy"},{"price":"47012.00","symbol":"BTCUSD","id":470120000,"side":"Sell"}],"update":[{"price":"46938.50","symbol":"BTCUSD","id":469385000,"side":"Buy","size":45010},{"price":"46999.00","symbol":"BTCUSD","id":469990000,"side":"Sell","size":48003}],"insert":[{"price":"46821.50","symbol":"BTCUSD","id":468215000,"side":"Buy","size":109},{"price":"47110.50","symbol":"BTCUSD","id":471105000,"side":"Sell","size":129}],"transactTimeE6":0},"cross_seq":11207659529,"timestamp_e6":1639760759681882}'

if __name__ == "__main__":
    lob = lob_bybit(symbol='BTCUSD')
    lines = lob.process_the_latest_s3_file()
    for line in lines:
        print (line)
    print(f'lines printed {len(lines)}')


