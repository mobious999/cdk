from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    Tags
)
from constructs import Construct

class RouteTableStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.IVpc,
                 public_subnets,
                 private_subnets,
                 nat_gateways,
                 igw,
                 tags: dict,
                 env_name: str,
                 data_subnets=None,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Public Route Table and associations
        public_route_table = ec2.CfnRouteTable(
            self, "PublicRouteTable",
            vpc_id=vpc.vpc_id
        )
        Tags.of(public_route_table).add("Name", f"{env_name}-public-rt")
        for k, v in tags.items():
            Tags.of(public_route_table).add(k, v)

        for idx, public_subnet in enumerate(public_subnets):
            ec2.CfnSubnetRouteTableAssociation(
                self, f"PublicRTAssoc{idx+1}",
                subnet_id=public_subnet.subnet_id,
                route_table_id=public_route_table.ref
            )

        ec2.CfnRoute(
            self, "PublicDefaultRoute",
            route_table_id=public_route_table.ref,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=igw.ref
        )

        # Private Route Tables and associations
        for i, private_subnet in enumerate(private_subnets):
            private_rt = ec2.CfnRouteTable(
                self, f"PrivateRouteTable{i+1}",
                vpc_id=vpc.vpc_id
            )
            Tags.of(private_rt).add("Name", f"{env_name}-private-rt-{i+1}")
            for k, v in tags.items():
                Tags.of(private_rt).add(k, v)

            ec2.CfnSubnetRouteTableAssociation(
                self, f"PrivateRTAssoc{i+1}",
                subnet_id=private_subnet.subnet_id,
                route_table_id=private_rt.ref
            )

            ec2.CfnRoute(
                self, f"PrivateDefaultRoute{i+1}",
                route_table_id=private_rt.ref,
                destination_cidr_block="0.0.0.0/0",
                nat_gateway_id=nat_gateways[i].ref
            )

        # Data Route Table (local route only)
        if data_subnets:
            data_rt = ec2.CfnRouteTable(
                self, "DataRouteTable",
                vpc_id=vpc.vpc_id
            )
            Tags.of(data_rt).add("Name", f"{env_name}-data-rt")
            for k, v in tags.items():
                Tags.of(data_rt).add(k, v)

            for i, data_subnet in enumerate(data_subnets):
                ec2.CfnSubnetRouteTableAssociation(
                    self, f"DataRTAssoc{i+1}",
                    subnet_id=data_subnet.subnet_id,
                    route_table_id=data_rt.ref
                )
