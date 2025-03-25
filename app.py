#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.vpc_stack import VpcStack
from stacks.nacl_stack import NaclStack
from stacks.prefixlist_stack import PrefixListStack

app = cdk.App()

vpc_config = {
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
    }
}

vpc_stack = VpcStack(app, "VpcStack", config=vpc_config)
NaclStack(app, "NaclStack",
          vpc=vpc_stack.vpc,
          public_subnets=vpc_stack.public_subnets,
          private_subnets=vpc_stack.private_subnets,
          data_subnets=vpc_stack.data_subnets,
          tags=vpc_config["tags"],
          env_name=vpc_config["env_name"]
)

prefix_config = {
    "env_name": "dr",
    "tags": {
        "Project": "DisasterRecovery"
    },
    "prefix_lists": {
        "monitoring": [
            {"cidr": "10.100.0.0/16", "description": "Monitoring Agents"},
            {"cidr": "10.200.0.0/16"}
        ],
        "office-range": [
            {"cidr": "203.0.113.0/24", "description": "Office 1"},
            {"cidr": "198.51.100.0/24", "description": "Office 2"}
        ]
    }
}

PrefixListStack(app, "PrefixListStack", config=prefix_config)

app.synth()