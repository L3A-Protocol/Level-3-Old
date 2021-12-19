
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
LOB_ACTION_DELETE       = 'delete'
LOB_ACTION_UPDATE       = 'update'
LOB_ACTION_INSERT       = 'insert'

RAW_DATA_COLUMN_NAMES = ["side","id","price","symbol","lob_action","size","timestamp"]
# RAW_JSON = '[{"side":"Buy","id":0,"price":"00.00","symbol":"BTCUSD","lob_action":"None","size":0,"timestamp":0}]'
# INDEXED_DATA_COLUMN_NAMES = ["price","symbol","lob_action","size","timestamp"]

class lob_bybit(object):
    def __init__(self, symbol:str):
        self.connector = s3connector(exchange=LOB_BYBIT_EXCHANGE, topic=LOB_BYBIT_TOPIC, symbol=symbol)
        self.symbol = symbol
        self.topic = ESPECTED_TOPIC_PREFIX + symbol
        self.log = log_json()
        self.lob_df = None

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

        if LOB_ACTION_DELETE in line_json[JSON_FIELD_DATA]:
            return True
        if LOB_ACTION_UPDATE in line_json[JSON_FIELD_DATA]:
            return True
        if LOB_ACTION_INSERT in line_json[JSON_FIELD_DATA]:
            return True

        return False

    def get_lob_actions(self, data, lob_action, timestamp):
        df = pd.read_json(json_to_str(data[lob_action]))
        sLength = len(df['price'])
        df['lob_action'] = pd.Series(np.full(sLength, lob_action), index=df.index)
        df['timestamp'] = pd.Series(np.full(sLength, timestamp), index=df.index)
        return df

    def get_delete_lines(self, line):
        df = pd.DataFrame(columns=RAW_DATA_COLUMN_NAMES)
        try:
            line_json = json.loads(line)
            if self.verify_json(line_json=line_json):
                data = line_json[JSON_FIELD_DATA]
                df_delete = self.get_lob_actions(data, LOB_ACTION_DELETE, line_json[JSON_FIELD_TIMESTAMP])
                df = pd.concat([df, df_delete])
                # df.set_index(['side','id'],inplace=True)
        except Exception as ex:
            print (ex)
        return df

    def get_update_lines(self, line):
        df = pd.DataFrame(columns=RAW_DATA_COLUMN_NAMES)
        try:
            line_json = json.loads(line)
            if self.verify_json(line_json=line_json):
                data = line_json[JSON_FIELD_DATA]
                df_update = self.get_lob_actions(data, LOB_ACTION_UPDATE, line_json[JSON_FIELD_TIMESTAMP])
                df = pd.concat([df, df_update])
                # df.set_index(['side','id'],inplace=True)
        except Exception as ex:
            print (ex)
        return df

    def get_insert_lines(self, line):
        df = pd.DataFrame(columns=RAW_DATA_COLUMN_NAMES)
        try:
            line_json = json.loads(line)
            if self.verify_json(line_json=line_json):
                data = line_json[JSON_FIELD_DATA]
                df_insert = self.get_lob_actions(data, LOB_ACTION_INSERT, line_json[JSON_FIELD_TIMESTAMP])
                df = pd.concat([df, df_insert])
                # df.set_index(['side','id'],inplace=True)
        except Exception as ex:
            print (ex)
        return df

    def delete_lob_lines(self, df_delete):
        if self.lob_df is None:
            return
        self.lob_df = (pd.merge(self.lob_df,df_delete, indicator=True, how='outer')
                        .query('_merge=="left_only"')
                        .drop('_merge', axis=1))

    def update_lob_lines(self, df_update):
        self.insert_lob_lines(df_update)

    def insert_lob_lines(self, df_insert):
        if self.lob_df is None:
            self.lob_df = df_insert.copy(deep=True)
        self.lob_df = pd.concat([self.lob_df,df_insert]).drop_duplicates(['side','id'],keep='last') #.sort_values('Code')

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
    # df = lob.get_data_lines(test_line)
    # print(df)

    # df.set_index(['side','id'],inplace=True)
    # print(df)

    # lob.lob = pd.concat(lob.lob, df)
    # print(lob.lob)
    # df_empty = pd.concat(df_empty, df)
    # print(lob_df)


    # df.sort_index(level=0,ascending=True,inplace=True)
    # print(df)

    # df.drop(('Sell', 469990000), axis=0,inplace=True)
    # print(df)

    df_delete = lob.get_delete_lines(test_line)
    df_update = lob.get_update_lines(test_line)
    df_insert = lob.get_insert_lines(test_line)

    # print (df_delete)
    # print (df_update)
    # print (df_insert)

    print('')
    print (lob.lob_df)

    print('')
    lob.insert_lob_lines(df_insert)
    print (lob.lob_df)

    print('')
    lob.delete_lob_lines(df_delete)
    print (lob.lob_df)

    print('')
    lob.insert_lob_lines(df_delete)
    print (lob.lob_df)

    print('')
    lob.delete_lob_lines(df_insert)
    print (lob.lob_df)


    # lob.delete_lob_lines(df_insert)
    # print (lob.lob_df)



