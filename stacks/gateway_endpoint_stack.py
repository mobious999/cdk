from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    Tags
)
from constructs import Construct

class GatewayEndpointStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.IVpc,
                 route_table_ids: list,
                 env_name: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 Gateway Endpoint
        s3_ep = ec2.CfnVPCEndpoint(
            self, "S3GatewayEndpoint",
            service_name=f"com.amazonaws.{self.region}.s3",
            vpc_id=vpc.vpc_id,
            route_table_ids=route_table_ids,
            vpc_endpoint_type="Gateway",
            policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:*",
                        "Resource": "*"
                    }
                ]
            }
        )
        Tags.of(s3_ep).add("Name", f"{env_name}-s3-endpoint")

        # DynamoDB Gateway Endpoint
        ddb_ep = ec2.CfnVPCEndpoint(
            self, "DynamoDBGatewayEndpoint",
            service_name=f"com.amazonaws.{self.region}.dynamodb",
            vpc_id=vpc.vpc_id,
            route_table_ids=route_table_ids,
            vpc_endpoint_type="Gateway",
            policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "dynamodb:*",
                        "Resource": "*"
                    }
                ]
            }
        )
        Tags.of(ddb_ep).add("Name", f"{env_name}-dynamodb-endpoint")
