from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    Tags
)
from constructs import Construct

class NaclStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.IVpc, public_subnets, private_subnets, data_subnets, tags: dict = {}, env_name: str = "dev", **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Public NACL with rules and subnet associations
        public_nacl = ec2.NetworkAcl(
            self, "PublicNACL",
            vpc=vpc
        )
        Tags.of(public_nacl).add("Name", f"{env_name}-public-nacl")
        for k, v in tags.items():
            Tags.of(public_nacl).add(k, v)

        for idx, subnet in enumerate(public_subnets):
            ec2.CfnSubnetNetworkAclAssociation(
                self, f"PublicNaclAssoc{idx+1}",
                subnet_id=subnet.subnet_id,
                network_acl_id=public_nacl.network_acl_id
            )

        public_nacl.add_entry("AllowHTTP",
            cidr=ec2.AclCidr.any_ipv4(),
            rule_number=100,
            traffic=ec2.AclTraffic.tcp_port(80),
            direction=ec2.TrafficDirection.INGRESS,
            rule_action=ec2.Action.ALLOW
        )

        public_nacl.add_entry("AllowAllEgress",
            cidr=ec2.AclCidr.any_ipv4(),
            rule_number=100,
            traffic=ec2.AclTraffic.all_traffic(),
            direction=ec2.TrafficDirection.EGRESS,
            rule_action=ec2.Action.ALLOW
        )

        # Private NACL with rules and subnet associations
        private_nacl = ec2.NetworkAcl(
            self, "PrivateNACL",
            vpc=vpc
        )
        Tags.of(private_nacl).add("Name", f"{env_name}-private-nacl")
        for k, v in tags.items():
            Tags.of(private_nacl).add(k, v)

        for idx, subnet in enumerate(private_subnets):
            ec2.CfnSubnetNetworkAclAssociation(
                self, f"PrivateNaclAssoc{idx+1}",
                subnet_id=subnet.subnet_id,
                network_acl_id=private_nacl.network_acl_id
            )

        private_nacl.add_entry("AllowAllEgress",
            cidr=ec2.AclCidr.any_ipv4(),
            rule_number=100,
            traffic=ec2.AclTraffic.all_traffic(),
            direction=ec2.TrafficDirection.EGRESS,
            rule_action=ec2.Action.ALLOW
        )

        # Data NACL with rules and subnet associations
        data_nacl = ec2.NetworkAcl(
            self, "DataNACL",
            vpc=vpc
        )
        Tags.of(data_nacl).add("Name", f"{env_name}-data-nacl")
        for k, v in tags.items():
            Tags.of(data_nacl).add(k, v)

        for idx, subnet in enumerate(data_subnets):
            ec2.CfnSubnetNetworkAclAssociation(
                self, f"DataNaclAssoc{idx+1}",
                subnet_id=subnet.subnet_id,
                network_acl_id=data_nacl.network_acl_id
            )

        data_nacl.add_entry("AllowMySQL",
            cidr=ec2.AclCidr.any_ipv4(),
            rule_number=100,
            traffic=ec2.AclTraffic.tcp_port(3306),
            direction=ec2.TrafficDirection.INGRESS,
            rule_action=ec2.Action.ALLOW
        )

        data_nacl.add_entry("AllowAllEgress",
            cidr=ec2.AclCidr.any_ipv4(),
            rule_number=100,
            traffic=ec2.AclTraffic.all_traffic(),
            direction=ec2.TrafficDirection.EGRESS,
            rule_action=ec2.Action.ALLOW
        )
