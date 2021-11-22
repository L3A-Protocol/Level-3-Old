import os

from aws_cdk import (core as cdk,
                     aws_s3 as s3,
                     aws_ecs as ecs)

from fargate.exchangebase import ExchangeBase

EXCHNAGE_NAME       = 'Binance'
BIN_PATH            = "/app/lws-binance"
REPO_ARN            = "arn:aws:ecr:us-west-1:381452754685:repository/binance03"
TOPIC               = 'binance'

class BinanceConstruct(ExchangeBase):

    def __init__(self, scope: cdk.Construct, id: str, bucket: s3.Bucket, cluster: ecs.Cluster, symbol:str, **kwargs):
        super().__init__(scope, id, EXCHNAGE_NAME, BIN_PATH, REPO_ARN, bucket, cluster, TOPIC, symbol, **kwargs)
