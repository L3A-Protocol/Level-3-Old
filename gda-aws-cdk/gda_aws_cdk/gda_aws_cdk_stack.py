# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
import os

from aws_cdk import (core as cdk,
                     aws_s3 as s3,
                     aws_ec2 as ec2,
                     aws_ecs as ecs,
                     aws_lambda as _lambda)

from fargate.binance    import BinanceConstruct
from fargate.bybit      import BybitConstruct
from fargate.bybitusdt  import BybitUSDTConstruct
from fargate.coinbase   import CoinbaseConstruct


class GdaAwsCdkStack(cdk.Stack):

    def BinanceDeployment(self, bucket, vpc, cluster):
        # Binance @aggTrade

        binance_aggTrade_btcusdt = BinanceConstruct(self, "binance-aggTrade-btcusdt",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic='aggTrade',
                                    symbol='BTCUSDT'
                                )

        binance_aggTrade_ethusdt = BinanceConstruct(self, "binance-aggTrade-ethusdt",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic='aggTrade',
                                    symbol='ETHUSDT'
                                )

        # Binance @trade

        binance_trade_btcusdt = BinanceConstruct(self, "binance-trade-btcusdt",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic='trade',
                                    symbol='BTCUSDT'
                                )

        binance_trade_ethusdt = BinanceConstruct(self, "binance-trade-ethusdt",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic='trade',
                                    symbol='ETHUSDT'
                                )

        # Binance @kline

        # binance_kline_btcusdt = BinanceConstruct(self, "binance-kline-btcusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic='kline',
        #                             symbol='BTCUSDT'
        #                         )

        # binance_kline_ethusdt = BinanceConstruct(self, "binance-kline-ethusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic='kline',
        #                             symbol='ETHUSDT'
        #                         )

        # Binance @miniTicker

        # binance_miniTicker_btcusdt = BinanceConstruct(self, "binance-miniTicker-btcusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic='miniTicker',
        #                             symbol='BTCUSDT'
        #                         )

        # binance_miniTicker_ethusdt = BinanceConstruct(self, "binance-miniTicker-ethusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic='miniTicker',
        #                             symbol='ETHUSDT'
        #                         )

        # Binance @ticker

        # binance_ticker_btcusdt = BinanceConstruct(self, "binance-ticker-btcusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic='ticker',
        #                             symbol='BTCUSDT'
        #                         )

        # binance_ticker_ethusdt = BinanceConstruct(self, "binance-ticker-ethusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic='ticker',
        #                             symbol='ETHUSDT'
        #                         )

        # Binance @bookTicker

        # binance_bookTicker_btcusdt = BinanceConstruct(self, "binance-bookTicker-btcusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic='bookTicker',
        #                             symbol='BTCUSDT'
        #                         )

        # binance_bookTicker_ethusdt = BinanceConstruct(self, "binance-bookTicker-ethusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic='bookTicker',
        #                             symbol='ETHUSDT'
        #                         )

    def BybitDeployment(self, bucket, vpc, cluster):
# Bybit orderbook 200

        bybit_orderbook_200_btcusd  = BybitConstruct(self, 'bybit-orderbook-200-btcusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="orderBook_200.100ms",
                                    symbol="BTCUSD"
                                )

        bybit_orderbook_200_ethusd  = BybitConstruct(self, 'bybit-orderbook-200-ethusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="orderBook_200.100ms",
                                    symbol="ETHUSD"
                                )

        # bybit_orderbook_200_eosusd  = BybitConstruct(self, 'bybit-orderbook-200-eosusd',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="orderBook_200.100ms",
        #                             symbol="EOSUSD"
        #                         )

        # bybit_orderbook_200_xrpusd  = BybitConstruct(self, 'bybit-orderbook-200-xrpusd',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="orderBook_200.100ms",
        #                             symbol="XRPUSD"
        #                         )

        # bybit_orderbook_200_dotusd  = BybitConstruct(self, 'bybit-orderbook-200-dotusd',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="orderBook_200.100ms",
        #                             symbol="DOTUSD"
        #                         )

# Bybit insurance

        # bybit_insurance_btc  = BybitConstruct(self, 'bybit-insurance-btc',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="insurance",
        #                             symbol='BTC'
        #                         )

        # bybit_insurance_eth  = BybitConstruct(self, 'bybit-insurance-eth',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="insurance",
        #                             symbol='ETH'
        #                         )

        # bybit_insurance_eos  = BybitConstruct(self, 'bybit-insurance-eos',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="insurance",
        #                             symbol='EOS'
        #                         )

        # bybit_insurance_xrp  = BybitConstruct(self, 'bybit-insurance-xrp',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="insurance",
        #                             symbol='XRP'
        #                         )

        # bybit_insurance_dot  = BybitConstruct(self, 'bybit-insurance-dot',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="insurance",
        #                             symbol='DOT'
        #                         )

# Bybit trade

        bybit_trade_btcusd      = BybitConstruct(self, 'bybit-trade-btcusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="trade",
                                    symbol='BTCUSD'
                                )

        bybit_trade_ethusd      = BybitConstruct(self, 'bybit-trade-ethusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="trade",
                                    symbol='ETHUSD'
                                )

        bybit_trade_eosusd      = BybitConstruct(self, 'bybit-trade-eosusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="trade",
                                    symbol='EOSUSD'
                                )

        bybit_trade_xrpusd      = BybitConstruct(self, 'bybit-trade-xrpusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="trade",
                                    symbol='XRPUSD'
                                )

        bybit_trade_dotusd      = BybitConstruct(self, 'bybit-trade-dotusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="trade",
                                    symbol='DOTUSD'
                                )

        # bybit_klinev21_btcusd   = BybitConstruct(self, 'bybit-klinev21-btcusd',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="klineV2.1",
        #                             symbol='BTCUSD'
        #                         )

        # bybit_klinev21_ethusd   = BybitConstruct(self, 'bybit-klinev21-ethusd',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="klineV2.1",
        #                             symbol='ETHUSD'
        #                         )

        # bybit_klinev21_eosusd   = BybitConstruct(self, 'bybit-klinev21-eosusd',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="klineV2.1",
        #                             symbol='EOSUSD'
        #                         )

        # bybit_klinev21_xrpusd   = BybitConstruct(self, 'bybit-klinev21-xrpusd',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="klineV2.1",
        #                             symbol='XRPUSD'
        #                         )

        # bybit_klinev21_dotusd   = BybitConstruct(self, 'bybit-klinev21-dotusd',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="klineV2.1",
        #                             symbol='DOTUSD'
        #                         )

    def BybitUSDTDeployment(self, bucket, vpc, cluster):
        bybitusdt_orderbook_200_btcusdt = BybitUSDTConstruct(self, 'bybitusdt-orderbook-200-btcusdt',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic='orderBook_200.100ms',
                                    symbol='BTCUSDT'
                                )

        bybitusdt_orderbook_200_ethusdt = BybitUSDTConstruct(self, 'bybitusdt-orderbook-200-ethusdt',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic='orderBook_200.100ms',
                                    symbol='ETHUSDT'
                                )

        bybitusdt_trade_btcusdt = BybitUSDTConstruct(self, "bybitusdt-trade-btcusdt",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="trade",
                                    symbol='BTCUSDT'
                                )

        bybitusdt_trade_ethusdt = BybitUSDTConstruct(self, "bybitusdt-trade-ethusdt",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="trade",
                                    symbol='ETHUSDT'
                                )

        # bybitusdt_candle_btcusdt = BybitUSDTConstruct(self, "bybitusdt-candle-btcusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="candle.1",
        #                             symbol='BTCUSDT'
        #                         )

        # bybitusdt_candle_ethusdt = BybitUSDTConstruct(self, "bybitusdt-candle-ethusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="candle.1",
        #                             symbol='ETHUSDT'
        #                         )

    def CoinbaseDeployment(self, bucket, vpc, cluster):
        coinbase_ethusd         = CoinbaseConstruct(self, "coinbase-ethusd",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="feed-pro",
                                    symbol="ETH-USD"
                                )

        coinbase_btcusd         = CoinbaseConstruct(self, "coinbase-btcusd",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="feed-pro",
                                    symbol="BTC-USD"
                                )

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(self, "GDADataLake",
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True)

        vpc = ec2.Vpc(self, "GDADataLakeVpc", max_azs=3)

        cluster = ecs.Cluster(self, "GDADataLakeCluster", vpc=vpc)

        self.BinanceDeployment  (bucket=bucket, vpc=vpc, cluster=cluster)
        self.BybitDeployment    (bucket=bucket, vpc=vpc, cluster=cluster)
        self.BybitUSDTDeployment(bucket=bucket, vpc=vpc, cluster=cluster)
        self.CoinbaseDeployment (bucket=bucket, vpc=vpc, cluster=cluster)


        # task_switcher_lambda = _lambda.Function(
        #     self, 'TaskSwitcher',
        #     runtime=_lambda.Runtime.PYTHON_3_7,
        #     code=_lambda.Code.from_asset('lambda'),
        #     handler='task_switcher.handler',
        # )