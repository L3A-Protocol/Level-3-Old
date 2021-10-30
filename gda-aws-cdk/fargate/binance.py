import os

from aws_cdk import (core as cdk,
                     aws_s3 as s3,
                     aws_ecs as ecs,
                     aws_ecr as ecr,
                     aws_logs as logs)

class BinanceConstruct(cdk.Construct):

    def __init__(self, scope: cdk.Construct, id: str, bucket: s3.Bucket, cluster: ecs.Cluster, **kwargs):
        super().__init__(scope, id, **kwargs)

        task_definition = ecs.FargateTaskDefinition( self, "binance-td",
                cpu=256, memory_limit_mib=512)

        binance_repo = ecr.Repository.from_repository_arn(self, "binance-repo", "arn:aws:ecr:us-west-1:381452754685:repository/binance03")

        image = ecs.ContainerImage.from_ecr_repository(binance_repo)
        access_key_id       = os.environ["EXCHANGE_ACCESS_KEY_ID"]
        access_secret_key   = os.environ["EXCHANGE_SECRET_ACCESS_KEY"]
        environment = {
                    "EXCHANGE": "Binance",
                    "C_BINARY_PATH":"/app/lws-binance",
                    "TOPIC": "binance",
                    "AWS_ACCESS_KEY_ID": access_key_id,
                    "AWS_SECRET_ACCESS_KEY": access_secret_key,
                    "BUCKET_NAME": bucket.bucket_name
                }
        logDetail = logs.LogGroup(self, "BinanceServicesLogGroup", log_group_name="/ecs/binance-log-group", retention=logs.RetentionDays.SIX_MONTHS, removal_policy=cdk.RemovalPolicy.DESTROY)
        logging = ecs.LogDriver.aws_logs(stream_prefix = "ecs", log_group=logDetail)
        container = task_definition.add_container( "binance-container", image=image,
                environment=environment,
                logging = logging
                )

        binance_service = ecs.FargateService(self, id,
            task_definition=task_definition,
            assign_public_ip=True,
            cluster=cluster)