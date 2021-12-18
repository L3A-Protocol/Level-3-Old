
import json
import numpy as np
import pandas as pd

from log_json import log_json
from s3connector import s3connector

from osbot_utils.utils.Json import str_to_json, json_to_str, json_parse

LOB_BYBIT_EXCHANGE  = 'ByBit'
LOB_BYBIT_TOPIC     = 'orderBook_200.100ms'

JSON_FIELD_TOPIC        = 'topic'
JSON_FIELD_TYPE         = 'type'
JSON_FIELD_DATA         = 'data'
JSON_FIELD_TIMESTAMP    = 'timestamp_e6'
JSON_FIELD_CROSS_SEQ    = 'cross_seq'

ESPECTED_TOPIC_PREFIX   = 'orderBook_200.100ms.'
EXPECTED_TYPE           = 'delta'
DATA_DELETE             = 'delete'
DATA_UPDATE             = 'update'
DATA_INSERT             = 'insert'

class lob_bybit(object):
    def __init__(self, symbol:str):
        self.connector = s3connector(exchange=LOB_BYBIT_EXCHANGE, topic=LOB_BYBIT_TOPIC, symbol=symbol)
        self.symbol = symbol
        self.topic = ESPECTED_TOPIC_PREFIX + symbol
        self.log = log_json()

    def field_present(self, field, line_json):
        if field in line_json:
            return True
        print(f'Field {field} not found')
        return False

    def verify_json(self, line_json):
        if not self.field_present(JSON_FIELD_TOPIC, line_json):
            return False
        if not self.field_present(JSON_FIELD_TYPE, line_json):
            return False
        if not self.field_present(JSON_FIELD_DATA, line_json):
            return False
        if not self.field_present(JSON_FIELD_TIMESTAMP, line_json):
            return False
        if not self.field_present(JSON_FIELD_CROSS_SEQ, line_json):
            return False

        if line_json[JSON_FIELD_TOPIC] != self.topic:
            return False
        if line_json[JSON_FIELD_TYPE] != EXPECTED_TYPE:
            return False

        if DATA_DELETE in line_json[JSON_FIELD_DATA]:
            return True
        if DATA_UPDATE in line_json[JSON_FIELD_DATA]:
            return True
        if DATA_INSERT in line_json[JSON_FIELD_DATA]:
            return True

        return False

    def process_single_line(self, line):
        try:
            line_json = json.loads(line)
            if not self.verify_json(line_json=line_json):
                print ("the line cannot be verified")
                return {}
            return line_json[JSON_FIELD_DATA]
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
    # lines = lob.process_the_latest_s3_file()
    # for line in lines:
    #     print (line)
    # print(f'lines printed {len(lines)}')
    data = lob.process_single_line(test_line)
    for item in data:
        df = pd.read_json(json_to_str(data[item]))
        # print(data[item])
        print(df.to_string())

