# Workshop 1: Cloud Development Environment

Set up a secure, cloud-based VS Code development environment using AWS CloudFormation. This workshop introduces Infrastructure-as-Code concepts that carry forward into CDK deployments in Workshop 4.

## Topics Covered

- CloudFormation template authoring and deployment
- VPC networking (public/private subnets, NAT Gateway, security groups)
- Defense-in-depth architecture (CloudFront → ALB → EC2)
- SSM Session Manager for secure instance access
- Template validation with cfn-lint

## Contents

| Directory | Description |
|-----------|-------------|
| [code-server/](code-server/) | CloudFormation templates, deployment guide, and architecture documentation |

## Quick Start

```bash
aws cloudformation create-stack \
  --stack-name code-server \
  --template-body file://workshop1/code-server/code-server.yaml \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

See [code-server/DEPLOYMENT.md](code-server/DEPLOYMENT.md) for full instructions.

## Architecture

EC2 instance running code-server in a private subnet, accessed via CloudFront → ALB → EC2 with no public IP. NAT Gateway provides controlled outbound internet access for dependency installation.

## Note

This workshop is optional supplementary material. The code-server environment is pre-deployed for participants — this content is for those who want to understand the underlying infrastructure.
