from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
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

        # Include Name tag for VPC directly in the tags dict
        tags["Name"] = f"{env_name}-vpc"

        # Create VPC using new ip_addresses method
        self.vpc = ec2.Vpc(
            self, "MainVPC",
            ip_addresses=ec2.IpAddresses.cidr(vpc_cidr),
            max_azs=2,
            nat_gateways=2,
            subnet_configuration=[]  # We'll define subnets manually
        )

        azs = self.availability_zones

        self.public_subnets = []
        self.private_subnets = []
        self.data_subnets = []

        # Create Public Subnets
        for i, cidr in enumerate(subnets_cfg.get("public", [])):
            subnet = ec2.Subnet(
                self, f"PublicSubnet{i+1}",
                vpc_id=self.vpc.vpc_id,
                cidr_block=cidr,
                availability_zone=azs[i % len(azs)],
                map_public_ip_on_launch=True
            )
            Tags.of(subnet).add("Tier", "Public")
            Tags.of(subnet).add("Name", f"{env_name}-public-{azs[i % len(azs)]}")
            for k, v in tags.items():
                Tags.of(subnet).add(k, v)
            self.public_subnets.append(subnet)

        # Create Private Subnets
        for i, cidr in enumerate(subnets_cfg.get("private", [])):
            subnet = ec2.Subnet(
                self, f"PrivateSubnet{i+1}",
                vpc_id=self.vpc.vpc_id,
                cidr_block=cidr,
                availability_zone=azs[i % len(azs)],
                map_public_ip_on_launch=False
            )
            Tags.of(subnet).add("Tier", "Private")
            Tags.of(subnet).add("Name", f"{env_name}-private-{azs[i % len(azs)]}")
            for k, v in tags.items():
                Tags.of(subnet).add(k, v)
            self.private_subnets.append(subnet)

        # Create Data Subnets
        for i, cidr in enumerate(subnets_cfg.get("data", [])):
            subnet = ec2.Subnet(
                self, f"DataSubnet{i+1}",
                vpc_id=self.vpc.vpc_id,
                cidr_block=cidr,
                availability_zone=azs[i % len(azs)],
                map_public_ip_on_launch=False
            )
            Tags.of(subnet).add("Tier", "Data")
            Tags.of(subnet).add("Name", f"{env_name}-data-{azs[i % len(azs)]}")
            for k, v in tags.items():
                Tags.of(subnet).add(k, v)
            self.data_subnets.append(subnet)

        for key, value in tags.items():
            Tags.of(self.vpc).add(key, value)
