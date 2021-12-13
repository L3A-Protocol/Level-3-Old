import os

from aws_cdk import (core as cdk,
                     aws_s3 as s3,
                     aws_ecs as ecs,
                     aws_ecr as ecr,
                     aws_logs as logs)

DEFAULT_FEED_INTERVAL = '30000'

class ExchangeBase(cdk.Construct):

    def __init__(self, scope: cdk.Construct, id:str,
                exchnage_name:str,
                binary_path:str,
                repo_arn:str,
                bucket:s3.Bucket,
                cluster:ecs.Cluster,
                topic: str,
                symbol: str,
                feed_interval=DEFAULT_FEED_INTERVAL,
                **kwargs):
        super().__init__(scope, id, **kwargs)

        service_prefix = exchnage_name.lower()
        symbol_lower = symbol.lower()

        task_id = (f'{service_prefix}-td-{topic}').replace('.','-')
        log_id = f'{exchnage_name}ServicesLogGroup'
        log_group_name = (f'/ecs/{service_prefix}-{topic}-{symbol_lower}-log-group').replace('.','-')
        container_id = (f'{service_prefix}-{topic}-{symbol_lower}-container').replace('.','-')
        stream_prefix = "ecs"

        task_definition = ecs.FargateTaskDefinition( self, task_id,
                cpu=256, memory_limit_mib=512)

        repo = ecr.Repository.from_repository_arn(self, f'{service_prefix}-repo', repo_arn)

        image = ecs.ContainerImage.from_ecr_repository(repo)
        access_key_id           = os.environ["EXCHANGE_ACCESS_KEY_ID"]
        access_secret_key       = os.environ["EXCHANGE_SECRET_ACCESS_KEY"]

        # opensearch_host         = os.environ["OPENSEARCH_HOST"]
        # opensearch_port         = '443'
        # opensearch_user         = os.environ["OPENSEARCH_USER"]
        # opensearch_password     = os.environ["OPENSEARCH_PASSWORD"]

        elastic_host    = os.environ["ELASTIC_HOST"]
        elastic_port    = os.environ["ELASTIC_PORT"]
        elastic_schema  = os.environ["ELASTIC_SCHEMA"]
        kibana_port     = os.environ["KIBANA_PORT"]

        environment = {
                    "EXCHANGE"                  : exchnage_name,
                    "C_BINARY_PATH"             : binary_path,
                    "TOPIC"                     : topic,
                    "SYMBOL"                    : symbol,
                    "FEED_INTERVAL"             : feed_interval,
                    "AWS_ACCESS_KEY_ID"         : access_key_id,
                    "AWS_SECRET_ACCESS_KEY"     : access_secret_key,
                    "BUCKET_NAME"               : bucket.bucket_name,
                #     "OPENSEARCH_HOST"           : opensearch_host,
                #     "OPENSEARCH_PORT"           : opensearch_port,
                #     "OPENSEARCH_USER"           : opensearch_user,
                #     "OPENSEARCH_PASSWORD"       : opensearch_password,
                     "ELASTIC_HOST"              : elastic_host,
                     "ELASTIC_SCHEMA"            : elastic_schema,
                     "ELASTIC_PORT"              : elastic_port,
                     "KIBANA_PORT"               : kibana_port,
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