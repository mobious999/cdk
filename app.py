from aws_cdk import App, Environment
from stacks.vpc_stack import VpcStack
from stacks.nacl_stack import NaclStack
from stacks.route_table_stack import RouteTableStack
from stacks.prefixlist_stack import PrefixListStack
from stacks.sg_stack import SecurityGroupStack
from stacks.gateway_endpoint_stack import GatewayEndpointStack
from stacks.interface_endpoint_stack import InterfaceEndpointStack
from stacks.flow_log_stack import FlowLogStack
from aws_cdk import aws_ec2 as ec2

app = App()

config = {
    "env_name": "dr",
    "vpc_cidr": "10.30.80.0/16",
    "tags": {
        "Project": "DisasterRecovery",
        "Environment": "DR",
        "Owner": "InfraTeam"
    },
    "subnets": {
        "public": ["10.30.80.0/26", "10.30.80.64/26"],
        "private": ["10.30.82.0/23", "10.30.84.0/23"],
        "data": ["10.30.92.0/24", "10.30.93.0/24"]
    },
    "prefix_lists": {
        "office-range": [
            {"cidr": "203.0.113.0/24", "description": "Office 1"},
            {"cidr": "198.51.100.0/24", "description": "Office 2"}
        ],
        "monitoring": [
            {"cidr": "10.100.0.0/16", "description": "Monitoring Agents"},
            {"cidr": "172.16.50.0/24"}
        ]
    },
    "security_groups": {
        "http": {
            "description": "Allow HTTP",
            "ingress": [
                {
                    "source": "pl-0123456789abcdef0",
                    "from_port": 80,
                    "to_port": 80,
                    "protocol": "tcp",
                    "description": "HTTP from office"
                }
            ]
        },
        "ssh": {
            "description": "Allow SSH",
            "ingress": [
                {
                    "source": "pl-0987654321fedcba0",
                    "from_port": 22,
                    "to_port": 22,
                    "protocol": "tcp",
                    "description": "SSH from VPN"
                }
            ]
        },
        "mysql": {
            "description": "Allow MySQL",
            "ingress": [
                {
                    "source": "pl-abc123abc123abc12",
                    "from_port": 3306,
                    "to_port": 3306,
                    "protocol": "tcp",
                    "description": "App to DB"
                }
            ]
        }
    }
}

# Define environment
env = Environment(account="123456789012", region="us-east-1")

# VPC and networking components
vpc_stack = VpcStack(app, "VpcStack", config=config, env=env)

# Internet Gateway and NATs must be created AFTER vpc_stack.vpc
igw = ec2.CfnInternetGateway(app, "InternetGateway", tags=[
    ec2.CfnTag(key="Name", value=f"{config['env_name']}-igw")
])
ec2.CfnVPCGatewayAttachment(app, "IgwAttachment",
    internet_gateway_id=igw.ref,
    vpc_id=vpc_stack.vpc.vpc_id
)

nat_gateways = []
for i, subnet in enumerate(vpc_stack.public_subnets):
    eip = ec2.CfnEIP(app, f"NatEip{i+1}", domain="vpc")
    nat = ec2.CfnNatGateway(app, f"NatGateway{i+1}",
        subnet_id=subnet.subnet_id,
        allocation_id=eip.attr_allocation_id,
        tags=[ec2.CfnTag(key="Name", value=f"{config['env_name']}-natgw-{i+1}")]
    )
    nat_gateways.append(nat)

nacl_stack = NaclStack(app, "NaclStack",
    vpc=vpc_stack.vpc,
    public_subnets=vpc_stack.public_subnets,
    private_subnets=vpc_stack.private_subnets,
    data_subnets=vpc_stack.data_subnets,
    tags=config["tags"],
    env_name=config["env_name"],
    env=env
)

route_table_stack = RouteTableStack(app, "RouteTableStack",
    vpc=vpc_stack.vpc,
    public_subnets=vpc_stack.public_subnets,
    private_subnets=vpc_stack.private_subnets,
    nat_gateways=nat_gateways,
    igw=igw,
    data_subnets=vpc_stack.data_subnets,
    tags=config["tags"],
    env_name=config["env_name"],
    env=env
)

prefix_list_stack = PrefixListStack(app, "PrefixListStack", config=config, env=env)

sg_stack = SecurityGroupStack(app, "SecurityGroupStack",
    vpc=vpc_stack.vpc,
    prefix_lists=prefix_list_stack.prefix_lists,
    config=config,
    env=env
)

gateway_ep_stack = GatewayEndpointStack(app, "GatewayEndpointStack",
    vpc=vpc_stack.vpc,
    route_table_ids=[rt.ref for rt in route_table_stack.node.find_all() if isinstance(rt, ec2.CfnRouteTable)],
    env_name=config["env_name"],
    env=env
)

interface_ep_stack = InterfaceEndpointStack(app, "InterfaceEndpointStack",
    vpc=vpc_stack.vpc,
    private_subnet_ids=[subnet.subnet_id for subnet in vpc_stack.private_subnets],
    region=env.region,
    env_name=config["env_name"],
    tags=config["tags"],
    env=env
)

flow_log_stack = FlowLogStack(app, "FlowLogStack",
    vpc=vpc_stack.vpc,
    env_name=config["env_name"],
    tags=config["tags"],
    env=env
)

app.synth()