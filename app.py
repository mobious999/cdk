#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.vpc_stack import VpcStack

app = cdk.App()

VpcStack(app, "VpcStack", env=cdk.Environment(
    account=cdk.Aws.ACCOUNT_ID,
    region=cdk.Aws.REGION
))

app.synth()