from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    Tags
)
from constructs import Construct

class InternetGatewayStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.CfnVPC,
                 env_name: str,
                 tags: dict,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.igw = ec2.CfnInternetGateway(
            self, "InternetGateway"
        )
        Tags.of(self.igw).add("Name", f"{env_name}-igw")
        for k, v in tags.items():
            Tags.of(self.igw).add(k, v)

        ec2.CfnVPCGatewayAttachment(
            self, "IgwAttachment",
            internet_gateway_id=self.igw.ref,
            vpc_id=vpc.ref
        )
