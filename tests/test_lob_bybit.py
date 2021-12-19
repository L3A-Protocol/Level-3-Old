import pytest
import json

from unittest import TestCase

from osbot_utils.utils.Dev import pprint

from s3writer.lob_bybit import lob_bybit

test_line = '{"topic":"orderBook_200.100ms.BTCUSD","type":"delta","data":{"delete":[{"price":"46951.00","symbol":"BTCUSD","id":469510000,"side":"Buy"},{"price":"47012.00","symbol":"BTCUSD","id":470120000,"side":"Sell"}],"update":[{"price":"46938.50","symbol":"BTCUSD","id":469385000,"side":"Buy","size":45010},{"price":"46999.00","symbol":"BTCUSD","id":469990000,"side":"Sell","size":48003}],"insert":[{"price":"46821.50","symbol":"BTCUSD","id":468215000,"side":"Buy","size":109},{"price":"47110.50","symbol":"BTCUSD","id":471105000,"side":"Sell","size":129}],"transactTimeE6":0},"cross_seq":11207659529,"timestamp_e6":1639760759681882}'

# @pytest.mark.skip('TBD: investigate later')
class test_lob_bybit(TestCase):

    def setUp(self) -> None:
        self.lob   = lob_bybit(symbol='BTCUSD')

    def test_verify_json(self):
        line_json = json.loads(test_line)
        assert self.lob.verify_json(line_json=line_json) is True

        pass

