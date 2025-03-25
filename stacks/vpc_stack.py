from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_cloudformation as cfn,
    CfnOutput,
    Tags
)
from constructs import Construct

class VpcStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, config: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env_name = config.get("env_name", "dev")
        vpc_cidr = config.get("vpc_cidr", "10.30.80.0/16")
        tags = config.get("tags", {})
        subnets_cfg = config.get("subnets", {})

        # Create VPC using CfnVPC for full control
        self.vpc = ec2.CfnVPC(
            self, "MainVPC",
            cidr_block=vpc_cidr,
            enable_dns_support=True,
            enable_dns_hostnames=True
        )

        Tags.of(self.vpc).add("Name", f"{env_name}-vpc")
        for k, v in tags.items():
            Tags.of(self.vpc).add(k, v)

        CfnOutput(self, "VpcIdOutput", value=self.vpc.ref)

        azs = self.availability_zones
        self.public_subnets = []
        self.private_subnets = []
        self.data_subnets = []

        # Public Subnets
        for i, cidr in enumerate(subnets_cfg.get("public", [])):
            subnet = ec2.CfnSubnet(
                self, f"PublicSubnet{i+1}",
                vpc_id=self.vpc.ref,
                cidr_block=cidr,
                availability_zone=azs[i],
                map_public_ip_on_launch=True
            )
            Tags.of(subnet).add("Name", f"{env_name}-public-{azs[i]}")
            Tags.of(subnet).add("Tier", "Public")
            for k, v in tags.items():
                Tags.of(subnet).add(k, v)
            self.public_subnets.append(subnet)
            CfnOutput(self, f"PublicSubnetId{i+1}", value=subnet.ref)

        # Private Subnets
        for i, cidr in enumerate(subnets_cfg.get("private", [])):
            subnet = ec2.CfnSubnet(
                self, f"PrivateSubnet{i+1}",
                vpc_id=self.vpc.ref,
                cidr_block=cidr,
                availability_zone=azs[i],
                map_public_ip_on_launch=False
            )
            Tags.of(subnet).add("Name", f"{env_name}-private-{azs[i]}")
            Tags.of(subnet).add("Tier", "Private")
            for k, v in tags.items():
                Tags.of(subnet).add(k, v)
            self.private_subnets.append(subnet)
            CfnOutput(self, f"PrivateSubnetId{i+1}", value=subnet.ref)

        # Data Subnets
        for i, cidr in enumerate(subnets_cfg.get("data", [])):
            subnet = ec2.CfnSubnet(
                self, f"DataSubnet{i+1}",
                vpc_id=self.vpc.ref,
                cidr_block=cidr,
                availability_zone=azs[i],
                map_public_ip_on_launch=False
            )
            Tags.of(subnet).add("Name", f"{env_name}-data-{azs[i]}")
            Tags.of(subnet).add("Tier", "Data")
            for k, v in tags.items():
                Tags.of(subnet).add(k, v)
            self.data_subnets.append(subnet)
            CfnOutput(self, f"DataSubnetId{i+1}", value=subnet.ref)
