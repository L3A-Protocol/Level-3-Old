import os

from aws_cdk import (core as cdk,
                     aws_s3 as s3,
                     aws_ecs as ecs,
                     aws_ecr as ecr,
                     aws_logs as logs)

EXCHNAGE_NAME       = 'ByBit'
SERVICE_PREFIX      = 'bybit'
BIN_PATH            = "/app/lws-bybit"
REPO_ARN            = "arn:aws:ecr:us-west-1:381452754685:repository/bybit04"

class BybitConstruct(cdk.Construct):

    def __init__(self, scope: cdk.Construct, id: str, bucket: s3.Bucket, cluster: ecs.Cluster, topic: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        task_id = (f'{SERVICE_PREFIX}-td-{topic}').replace('.','-')
        log_id = f'{EXCHNAGE_NAME}ServicesLogGroup'
        log_group_name = (f'/ecs/{SERVICE_PREFIX}-{topic}-log-group').replace('.','-')
        container_id = (f'{SERVICE_PREFIX}-{topic}-container').replace('.','-')
        stream_prefix = "ecs"

        task_definition = ecs.FargateTaskDefinition( self, task_id,
                cpu=256, memory_limit_mib=512)

        repo = ecr.Repository.from_repository_arn(self, f'{SERVICE_PREFIX}-repo', REPO_ARN)

        image = ecs.ContainerImage.from_ecr_repository(repo)
        access_key_id       = os.environ["EXCHANGE_ACCESS_KEY_ID"]
        access_secret_key   = os.environ["EXCHANGE_SECRET_ACCESS_KEY"]
        environment = {
                    "EXCHANGE": EXCHNAGE_NAME,
                    "C_BINARY_PATH": BIN_PATH,
                    "TOPIC": topic,
                    "AWS_ACCESS_KEY_ID": access_key_id,
                    "AWS_SECRET_ACCESS_KEY": access_secret_key,
                    "BUCKET_NAME": bucket.bucket_name
                }
        
        logDetail = logs.LogGroup(self, log_id, log_group_name=log_group_name, retention=logs.RetentionDays.SIX_MONTHS, removal_policy=cdk.RemovalPolicy.DESTROY)
        logging = ecs.LogDriver.aws_logs(stream_prefix = stream_prefix, log_group=logDetail)
        container = task_definition.add_container( container_id, image=image,
                environment=environment,
                logging = logging
                )

        service = ecs.FargateService(self, id,
            task_definition=task_definition,
            assign_public_ip=True,
            cluster=cluster)