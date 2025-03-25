# AWS CDK - Disaster Recovery VPC Stack

This project creates a complete 3-tier VPC architecture using AWS CDK (Python), including:

- VPC with public, private, and data subnets
- IGW and NAT Gateways
- Route Tables and NACLs
- Prefix Lists and Security Groups
- VPC Gateway and Interface Endpoints
- VPC Flow Logs to CloudWatch

## 🚀 Prerequisites

- AWS CLI configured (`aws configure`)
- Python 3.9+
- AWS CDK v2 (`npm install -g aws-cdk`)
- Bootstrap your environment once per account/region:

```bash
cdk bootstrap aws://<ACCOUNT_ID>/<REGION>
