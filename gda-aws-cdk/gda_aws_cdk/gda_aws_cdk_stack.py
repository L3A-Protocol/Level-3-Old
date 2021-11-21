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

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(self, "GDADataLake",
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True)

        vpc = ec2.Vpc(self, "GDADataLakeVpc", max_azs=3)

        cluster = ecs.Cluster(self, "GDADataLakeCluster", vpc=vpc)

        # binance_construct       = BinanceConstruct(self, "binance-service", bucket=bucket, cluster=cluster)

        bybit_orderbook_200_btcusd     = BybitConstruct(self, 'bybit-orderbook-200-btcusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="orderBook_200.100ms",
                                    symbol="BTCUSD"
                                )

        bybit_orderbook_200_ethusd     = BybitConstruct(self, 'bybit-orderbook-200-ethusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="orderBook_200.100ms",
                                    symbol="ETHUSD"
                                )

        bybit_orderbook_200_eosusd     = BybitConstruct(self, 'bybit-orderbook-200-eosusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="orderBook_200.100ms",
                                    symbol="EOSUSD"
                                )

        bybit_orderbook_200_xrpusd     = BybitConstruct(self, 'bybit-orderbook-200-xrpusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="orderBook_200.100ms",
                                    symbol="XRPUSD"
                                )

        bybit_orderbook_200_dotusd     = BybitConstruct(self, 'bybit-orderbook-200-dotusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="orderBook_200.100ms",
                                    symbol="DOTUSD"
                                )

        bybit_insurance_btcusd  = BybitConstruct(self, 'bybit-insurance-btcusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="insurance",
                                    symbol='BTC'
                                )

        bybit_insurance_eth  = BybitConstruct(self, 'bybit-insurance-eth',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="insurance",
                                    symbol='ETH'
                                )

        bybit_insurance_eos  = BybitConstruct(self, 'bybit-insurance-eos',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="insurance",
                                    symbol='EOS'
                                )

        bybit_insurance_xrp  = BybitConstruct(self, 'bybit-insurance-xrp',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="insurance",
                                    symbol='XRP'
                                )

        bybit_insurance_dot  = BybitConstruct(self, 'bybit-insurance-dot',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="insurance",
                                    symbol='DOT'
                                )

# BTCUSD
# ETHUSD
# EOSUSD
# XRPUSD
# DOTUSD

# btcusd
# ethusd
# eosusd
# xrpusd
# dotusd

        # bybit_trade             = BybitConstruct(self, 'bybit-trade-',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="trade"
        #                         )

        # bybit_klinev21          = BybitConstruct(self, 'bybit-klinev21-',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="klineV2.1.BTCUSD"
        #                         )

        # bybitusdt_orderbook_200 = BybitUSDTConstruct(self, "bybitusdt-orderbook-200",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="orderBook_200.100ms.BTCUSDT"
        #                         )

        # bybitusdt_trade         = BybitUSDTConstruct(self, "bybitusdt-trade",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="trade.BTCUSDT"
        #                         )

        # bybitusdt_candle        = BybitUSDTConstruct(self, "bybitusdt-candle",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="candle.1.BTCUSDT"
        #                         )

        # coinbase_ethusd         = CoinbaseConstruct(self, "coinbase-ethusd",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="ETH-USD"
        #                         )

        # coinbase_btcusd         = CoinbaseConstruct(self, "coinbase-btcusd",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="BTC-USD"
        #                         )

        # task_switcher_lambda = _lambda.Function(
        #     self, 'TaskSwitcher',
        #     runtime=_lambda.Runtime.PYTHON_3_7,
        #     code=_lambda.Code.from_asset('lambda'),
        #     handler='task_switcher.handler',
        # )