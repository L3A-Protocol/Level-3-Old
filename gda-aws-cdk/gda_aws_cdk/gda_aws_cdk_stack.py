# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
import os

from aws_cdk import (core as cdk,
                     aws_s3 as s3,
                     aws_ec2 as ec2,
                     aws_ecs as ecs,
                     aws_lambda as _lambda,
                     aws_iam as iam,
                     )

from fargate.binance    import BinanceConstruct
from fargate.bybit      import BybitConstruct
from fargate.bybitusdt  import BybitUSDTConstruct
from fargate.coinbase   import CoinbaseConstruct


class GdaAwsCdkStack(cdk.Stack):

    def BinanceDeployment(self, bucket, vpc, cluster, role=None):
        # Binance @aggTrade

        binance_aggTrade_btcusdt = BinanceConstruct(self, "binance-aggTrade-btcusdt",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic='aggTrade',
                                    symbol='BTCUSDT',
                                    role=role
                                )

        binance_aggTrade_ethusdt = BinanceConstruct(self, "binance-aggTrade-ethusdt",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic='aggTrade',
                                    symbol='ETHUSDT',
                                    role=role
                                )

        # Binance @trade

        binance_trade_btcusdt = BinanceConstruct(self, "binance-trade-btcusdt",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic='trade',
                                    symbol='BTCUSDT',
                                    role=role
                                )

        binance_trade_ethusdt = BinanceConstruct(self, "binance-trade-ethusdt",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic='trade',
                                    symbol='ETHUSDT',
                                    role=role
                                )

        # Binance @kline

        # binance_kline_btcusdt = BinanceConstruct(self, "binance-kline-btcusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic='kline',
        #                             symbol='BTCUSDT',
        #                             role=role
        #                         )

        # binance_kline_ethusdt = BinanceConstruct(self, "binance-kline-ethusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic='kline',
        #                             symbol='ETHUSDT',
        #                             role=role
        #                         )

        # Binance @miniTicker

        # binance_miniTicker_btcusdt = BinanceConstruct(self, "binance-miniTicker-btcusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic='miniTicker',
        #                             symbol='BTCUSDT',
        #                             role=role
        #                         )

        # binance_miniTicker_ethusdt = BinanceConstruct(self, "binance-miniTicker-ethusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic='miniTicker',
        #                             symbol='ETHUSDT',
        #                             role=role
        #                         )

        # Binance @ticker

        # binance_ticker_btcusdt = BinanceConstruct(self, "binance-ticker-btcusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic='ticker',
        #                             symbol='BTCUSDT',
        #                             role=role
        #                         )

        # binance_ticker_ethusdt = BinanceConstruct(self, "binance-ticker-ethusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic='ticker',
        #                             symbol='ETHUSDT',
        #                             role=role
        #                         )

        # Binance @bookTicker

        # binance_bookTicker_btcusdt = BinanceConstruct(self, "binance-bookTicker-btcusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic='bookTicker',
        #                             symbol='BTCUSDT',
        #                             role=role
        #                         )

        # binance_bookTicker_ethusdt = BinanceConstruct(self, "binance-bookTicker-ethusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic='bookTicker',
        #                             symbol='ETHUSDT',
        #                             role=role
        #                         )

    def BybitDeployment(self, bucket, vpc, cluster, role=None):
# Bybit orderbook 200

        bybit_orderbook_200_btcusd  = BybitConstruct(self, 'bybit-orderbook-200-btcusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="orderBook_200.100ms",
                                    symbol="BTCUSD",
                                    role=role
                                )

        bybit_orderbook_200_ethusd  = BybitConstruct(self, 'bybit-orderbook-200-ethusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="orderBook_200.100ms",
                                    symbol="ETHUSD",
                                    role=role
                                )

        # bybit_orderbook_200_eosusd  = BybitConstruct(self, 'bybit-orderbook-200-eosusd',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="orderBook_200.100ms",
        #                             symbol="EOSUSD",
        #                             role=role
        #                         )

        # bybit_orderbook_200_xrpusd  = BybitConstruct(self, 'bybit-orderbook-200-xrpusd',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="orderBook_200.100ms",
        #                             symbol="XRPUSD",
        #                             role=role
        #                         )

        # bybit_orderbook_200_dotusd  = BybitConstruct(self, 'bybit-orderbook-200-dotusd',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="orderBook_200.100ms",
        #                             symbol="DOTUSD",
        #                             role=role
        #                         )

# Bybit insurance

        # bybit_insurance_btc  = BybitConstruct(self, 'bybit-insurance-btc',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="insurance",
        #                             symbol='BTC',
        #                             role=role
        #                         )

        # bybit_insurance_eth  = BybitConstruct(self, 'bybit-insurance-eth',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="insurance",
        #                             symbol='ETH',
        #                             role=role
        #                         )

        # bybit_insurance_eos  = BybitConstruct(self, 'bybit-insurance-eos',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="insurance",
        #                             symbol='EOS',
        #                             role=role
        #                         )

        # bybit_insurance_xrp  = BybitConstruct(self, 'bybit-insurance-xrp',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="insurance",
        #                             symbol='XRP',
        #                             role=role
        #                         )

        # bybit_insurance_dot  = BybitConstruct(self, 'bybit-insurance-dot',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="insurance",
        #                             symbol='DOT',
        #                             role=role
        #                         )

# Bybit trade

        bybit_trade_btcusd      = BybitConstruct(self, 'bybit-trade-btcusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="trade",
                                    symbol='BTCUSD',
                                    role=role
                                )

        bybit_trade_ethusd      = BybitConstruct(self, 'bybit-trade-ethusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="trade",
                                    symbol='ETHUSD',
                                    role=role
                                )

        bybit_trade_eosusd      = BybitConstruct(self, 'bybit-trade-eosusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="trade",
                                    symbol='EOSUSD',
                                    role=role
                                )

        bybit_trade_xrpusd      = BybitConstruct(self, 'bybit-trade-xrpusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="trade",
                                    symbol='XRPUSD',
                                    role=role
                                )

        bybit_trade_dotusd      = BybitConstruct(self, 'bybit-trade-dotusd',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="trade",
                                    symbol='DOTUSD',
                                    role=role
                                )

        # bybit_klinev21_btcusd   = BybitConstruct(self, 'bybit-klinev21-btcusd',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="klineV2.1",
        #                             symbol='BTCUSD',
        #                             role=role
        #                         )

        # bybit_klinev21_ethusd   = BybitConstruct(self, 'bybit-klinev21-ethusd',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="klineV2.1",
        #                             symbol='ETHUSD',
        #                             role=role
        #                         )

        # bybit_klinev21_eosusd   = BybitConstruct(self, 'bybit-klinev21-eosusd',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="klineV2.1",
        #                             symbol='EOSUSD',
        #                             role=role
        #                         )

        # bybit_klinev21_xrpusd   = BybitConstruct(self, 'bybit-klinev21-xrpusd',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="klineV2.1",
        #                             symbol='XRPUSD',
        #                             role=role
        #                         )

        # bybit_klinev21_dotusd   = BybitConstruct(self, 'bybit-klinev21-dotusd',
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="klineV2.1",
        #                             symbol='DOTUSD',
        #                             role=role
        #                         )

    def BybitUSDTDeployment(self, bucket, vpc, cluster, role=None):
        bybitusdt_orderbook_200_btcusdt = BybitUSDTConstruct(self, 'bybitusdt-orderbook-200-btcusdt',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic='orderBook_200.100ms',
                                    symbol='BTCUSDT',
                                    role=role
                                )

        bybitusdt_orderbook_200_ethusdt = BybitUSDTConstruct(self, 'bybitusdt-orderbook-200-ethusdt',
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic='orderBook_200.100ms',
                                    symbol='ETHUSDT',
                                    role=role
                                )

        bybitusdt_trade_btcusdt = BybitUSDTConstruct(self, "bybitusdt-trade-btcusdt",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="trade",
                                    symbol='BTCUSDT',
                                    role=role
                                )

        bybitusdt_trade_ethusdt = BybitUSDTConstruct(self, "bybitusdt-trade-ethusdt",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="trade",
                                    symbol='ETHUSDT',
                                    role=role
                                )

        # bybitusdt_candle_btcusdt = BybitUSDTConstruct(self, "bybitusdt-candle-btcusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="candle.1",
        #                             symbol='BTCUSDT',
        #                             role=role
        #                         )

        # bybitusdt_candle_ethusdt = BybitUSDTConstruct(self, "bybitusdt-candle-ethusdt",
        #                             bucket=bucket,
        #                             cluster=cluster,
        #                             topic="candle.1",
        #                             symbol='ETHUSDT',
        #                             role=role
        #                         )

    def CoinbaseDeployment(self, bucket, vpc, cluster, role=None):
        coinbase_ethusd         = CoinbaseConstruct(self, "coinbase-ethusd",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="feed-pro",
                                    symbol="ETH-USD",
                                    role=role
                                )

        coinbase_btcusd         = CoinbaseConstruct(self, "coinbase-btcusd",
                                    bucket=bucket,
                                    cluster=cluster,
                                    topic="feed-pro",
                                    symbol="BTC-USD",
                                    role=role
                                )

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(self, "GDADataLake",
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True)

        vpc = ec2.Vpc(self, "GDADataLakeVpc", max_azs=3)

        cluster = ecs.Cluster(self, "GDADataLakeCluster", vpc=vpc)

        # Create a Role for ESC tasks
        ecs_tasks_role = iam.Role(self,
            id='ecs-s3-access-role',
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"))

        # Create and attach policy that gives permissions to write to the S3 bucket.
        iam.Policy(
            self, 's3_attr',
            policy_name='s3_access',
            statements=[iam.PolicyStatement(
                actions=['s3:*'],
                resources=['arn:aws:s3:::' + bucket.bucket_name + '/*'])],
                # resources=['*'])],
            roles=[ecs_tasks_role],
        )

        self.BinanceDeployment  (bucket=bucket, vpc=vpc, cluster=cluster)
        self.BybitDeployment    (bucket=bucket, vpc=vpc, cluster=cluster)
        self.BybitUSDTDeployment(bucket=bucket, vpc=vpc, cluster=cluster)
        self.CoinbaseDeployment (bucket=bucket, vpc=vpc, cluster=cluster, role=ecs_tasks_role)


        # task_switcher_lambda = _lambda.Function(
        #     self, 'TaskSwitcher',
        #     runtime=_lambda.Runtime.PYTHON_3_7,
        #     code=_lambda.Code.from_asset('lambda'),
        #     handler='task_switcher.handler',
        # )