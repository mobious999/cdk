from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    Tags
)
from constructs import Construct

class InterfaceEndpointStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.IVpc,
                 private_subnet_ids: list,
                 region: str,
                 env_name: str,
                 tags: dict = {},
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Security group for all interface endpoints
        sg = ec2.SecurityGroup(
            self, "EndpointSG",
            vpc=vpc,
            allow_all_outbound=True,
            security_group_name="sg_vpc_endpoint",
            description="Security group for VPC Interface Endpoints"
        )
        Tags.of(sg).add("Name", "sg_vpc_endpoint")
        for k, v in tags.items():
            Tags.of(sg).add(k, v)

        # Allow HTTPS inbound (port 443) from VPC
        sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS from VPC"
        )

        # Allow all outbound
        sg.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.all_traffic(),
            description="Allow all egress"
        )

        # List of common interface endpoint services
        services = [
            "ec2", "ssm", "ssmmessages", "ec2messages", "secretsmanager", "logs"
        ]

        for service in services:
            ec2.CfnVPCEndpoint(
                self, f"{service}Endpoint",
                vpc_id=vpc.vpc_id,
                service_name=f"com.amazonaws.{region}.{service}",
                vpc_endpoint_type="Interface",
                private_dns_enabled=True,
                subnet_ids=private_subnet_ids,
                security_group_ids=[sg.security_group_id],
                tags=[
                    ec2.CfnTag(key="Name", value=f"{env_name}-{service}-endpoint")
                ] + [ec2.CfnTag(key=k, value=v) for k, v in tags.items()]
            )
