# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.

from aws_cdk import (core as cdk,
                     aws_s3 as s3,
                     aws_ec2 as ec2,
                     aws_ecs as ecs,
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

        task_definition = ecs.FargateTaskDefinition.from_fargate_task_definition_arn(self, "binance-task",
            "arn:aws:ecs:us-west-1:381452754685:task-definition/binance-us-west-1:4")
