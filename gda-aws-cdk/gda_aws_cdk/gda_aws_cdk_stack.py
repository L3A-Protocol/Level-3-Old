# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
import os

from aws_cdk import (core as cdk,
                     aws_s3 as s3,
                     aws_ec2 as ec2,
                     aws_ecs as ecs)

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

        binance_construct       = BinanceConstruct(self, "binance-service", bucket=bucket, cluster=cluster)

        bybit_orderbook_200     = BybitConstruct(self, 'bybit-orderbook-200-service',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="orderBook_200.100ms.BTCUSD"
                                )

        bybit_insurance         = BybitConstruct(self, 'bybit-insurance-service',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="insurance"
                                )

        bybit_trade             = BybitConstruct(self, 'bybit-trade-service',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="trade"
                                )

        bybit_klinev21          = BybitConstruct(self, 'bybit-klinev21-service',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="klineV2.1.BTCUSD"
                                )

        bybitusdt_orderbook_200 = BybitUSDTConstruct(self, "bybitusdt-orderbook-200",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="orderBook_200.100ms.BTCUSDT"
                                )

        bybitusdt_trade         = BybitUSDTConstruct(self, "bybitusdt-trade",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="trade.BTCUSDT"
                                )

        bybitusdt_candle        = BybitUSDTConstruct(self, "bybitusdt-candle",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="candle.1.BTCUSDT"
                                )

        coinbase_ethusd         = CoinbaseConstruct(self, "coinbase-ethusd",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="ETH-USD"
                                )

        coinbase_btcusd         = CoinbaseConstruct(self, "coinbase-btcusd",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="BTC-USD"
                                )