import os

from aws_cdk import (core as cdk,
                     aws_s3 as s3,
                     aws_ecs as ecs)

from fargate.exchangebase import ExchangeBase

EXCHNAGE_NAME       = 'ByBit-USDT'
BIN_PATH            = "/app/lws-bybit"
REPO_ARN            = "arn:aws:ecr:us-west-1:381452754685:repository/bybit-usdt"

class BybitUSDTConstruct(ExchangeBase):

    def __init__(self, scope: cdk.Construct, id: str, bucket: s3.Bucket, cluster: ecs.Cluster, topic: str, **kwargs):
        super().__init__(scope, id, EXCHNAGE_NAME, BIN_PATH, REPO_ARN, bucket, cluster, topic, **kwargs)
