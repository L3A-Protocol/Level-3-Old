# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
import os

from aws_cdk import (core as cdk,
                     aws_s3 as s3,
                     aws_ec2 as ec2,
                     aws_ecs as ecs,
                     aws_ecr as ecr,
                     aws_logs as logs,
                     aws_ecs_patterns as ecs_patterns)

class GdaAwsCdkStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(self, "GDADataLake",
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True)

        vpc = ec2.Vpc(self, "GDADataLakeVpc", max_azs=3)     # default is all AZs in region

        cluster = ecs.Cluster(self, "GDADataLakeCluster", vpc=vpc)

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

        # port_mapping = ecs.PortMapping(container_port=8080, host_port=8080)
        # container.add_port_mappings(port_mapping)

        # binance_service = ecs.FargateService(self, "binance-service",
        #     task_definition=task_definition,
        #     assign_public_ip=True,
        #     cluster=cluster)