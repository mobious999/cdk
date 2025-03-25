from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_logs as logs,
    aws_iam as iam,
    Tags
)
from constructs import Construct

class FlowLogStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.IVpc,
                 env_name: str,
                 tags: dict = {},
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create CloudWatch log group
        log_group = logs.LogGroup(
            self, "VpcFlowLogGroup",
            log_group_name=f"/aws/vpc/flowlogs/{env_name}",
            retention=logs.RetentionDays.ONE_MONTH
        )

        # Create IAM Role for Flow Logs
        flow_log_role = iam.Role(
            self, "VpcFlowLogRole",
            assumed_by=iam.ServicePrincipal("vpc-flow-logs.amazonaws.com")
        )

        flow_log_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            resources=["*"]
        ))

        # VPC Flow Log
        flow_log = ec2.CfnFlowLog(
            self, "VpcFlowLog",
            resource_id=vpc.vpc_id,
            resource_type="VPC",
            traffic_type="ALL",
            log_destination_type="cloud-watch-logs",
            log_group_name=log_group.log_group_name,
            deliver_logs_permission_arn=flow_log_role.role_arn
        )

        Tags.of(flow_log).add("Name", f"{env_name}-vpc-flow-logs")
        for k, v in tags.items():
            Tags.of(flow_log).add(k, v)
