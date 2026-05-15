# Code Server Deployment Guide

## Overview
This guide provides instructions for deploying a secure, cloud-based VS Code development environment using private subnet architecture with CloudFront and Application Load Balancer.

## Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured
- Basic understanding of CloudFormation

## Quick Start

### 1. Deploy the Stack
```bash
aws cloudformation create-stack \
  --stack-name code-server \
  --template-body file://code-server.yaml \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

### 2. Monitor Deployment
```bash
aws cloudformation wait stack-create-complete \
  --stack-name code-server \
  --region us-east-1
```

### 3. Get Access Information
```bash
aws cloudformation describe-stacks \
  --stack-name code-server \
  --region us-east-1 \
  --query 'Stacks[0].Outputs'
```

## Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `InstanceType` | EC2 instance type (ARM64) | c7g.xlarge | No |
| `InstanceVolumeSize` | EBS volume size in GB | 30 | No |
| `HomeFolder` | Default workspace directory | /home/ubuntu/workshop/ | No |
| `DevServerPort` | Application development port | 8081 | No |

## Accessing Code-Server

### Via CloudFront (Only Method)
1. Get the CloudFront URL from stack outputs:
   ```bash
   aws cloudformation describe-stacks \
     --stack-name code-server \
     --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontURL`].OutputValue' \
     --output text
   ```
2. Navigate to: `https://<cloudfront-domain>/?folder=/home/ubuntu/workshop`
3. Login with password: Your AWS Account ID

**Note**: The EC2 instance is in a private subnet with no public IP address. All access must go through CloudFront → ALB → EC2.

## Troubleshooting

### Bootstrap Fails
1. Check SSM Association status in Systems Manager console
2. Review bootstrap logs in S3 bucket (check stack outputs for bucket name)
3. Connect via SSM Session Manager to investigate:
   ```bash
   # Get instance ID from stack outputs
   INSTANCE_ID=$(aws cloudformation describe-stacks \
     --stack-name code-server \
     --query 'Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue' \
     --output text)
   
   # Start SSM session
   aws ssm start-session --target $INSTANCE_ID
   
   # Once connected, check service status
   sudo systemctl status code-server@ubuntu
   sudo systemctl status nginx
   ```

### 504 Gateway Timeout
- **Cause**: Bootstrap process still running or failed
- **Solution**: Wait 10-15 minutes for bootstrap to complete, or check SSM logs via Session Manager

### Cannot Access Instance Directly
- **Expected Behavior**: EC2 instance is in a private subnet with no public IP
- **Solution**: This is by design for security. Use SSM Session Manager for debugging:
  ```bash
  aws ssm start-session --target <instance-id>
  ```

### Services Not Running
```bash
# Connect via SSM Session Manager
aws ssm start-session --target <instance-id>

# Check service status
sudo systemctl status code-server@ubuntu
sudo systemctl status nginx

# Restart services
sudo systemctl restart code-server@ubuntu
sudo systemctl restart nginx

# Check logs
sudo journalctl -u code-server@ubuntu -n 50
sudo tail -50 /var/log/nginx/error.log
```

### ALB Health Check Failing
1. Check ALB target group health in EC2 console
2. Verify EC2 security group allows traffic from ALB security group on port 80
3. Connect via SSM and test nginx locally:
   ```bash
   curl -I http://localhost
   ```

## Manual Bootstrap Execution

If the automatic bootstrap fails, you can manually execute the SSM document:

1. Go to AWS Systems Manager → Documents
2. Find the document (name in stack outputs)
3. Click "Run command"
4. Select your instance
5. Execute and monitor progress

Alternatively, use AWS CLI:
```bash
# Get document name from stack outputs
DOC_NAME=$(aws cloudformation describe-stacks \
  --stack-name code-server \
  --query 'Stacks[0].Outputs[?OutputKey==`SSMDocumentName`].OutputValue' \
  --output text)

# Get instance ID
INSTANCE_ID=$(aws cloudformation describe-stacks \
  --stack-name code-server \
  --query 'Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue' \
  --output text)

# Execute document
aws ssm send-command \
  --document-name "$DOC_NAME" \
  --targets "Key=InstanceIds,Values=$INSTANCE_ID"
```

## Architecture

### Private Subnet Security Architecture

The code-server deployment uses a secure, multi-tier architecture with EC2 instances in private subnets, accessed through CloudFront and an Application Load Balancer. This design provides defense-in-depth security while maintaining internet access for dependency installation.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    Internet Users                                    │
│                                   (HTTPS Traffic)                                    │
└──────────────────────────────────────┬──────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          CloudFront Distribution (HTTPS)                             │
│                         Domain: xxxxxx.cloudfront.net                                │
│                         Origin Protocol: HTTP-only                                   │
└──────────────────────────────────────┬──────────────────────────────────────────────┘
                                       │ HTTP:80
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                  VPC: 10.0.0.0/16                                    │
│                                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                            Internet Gateway                                  │   │
│  └────────────────────────────┬────────────────────────┬────────────────────────┘   │
│                               │                        │                            │
│  ┌────────────────────────────┼────────────────────────┼───────────────────────┐   │
│  │  Availability Zone A       │                        │  Availability Zone B  │   │
│  │                            │                        │                       │   │
│  │  ┌─────────────────────────▼──────────┐  ┌─────────▼──────────────────┐   │   │
│  │  │  Public Subnet 1: 10.0.1.0/24      │  │ Public Subnet 2: 10.0.2.0/24│  │   │
│  │  │  Route: 0.0.0.0/0 → IGW            │  │ Route: 0.0.0.0/0 → IGW      │  │   │
│  │  │                                     │  │                              │  │   │
│  │  │  ┌──────────────────────────────┐  │  │  ┌────────────────────────┐ │  │   │
│  │  │  │      NAT Gateway             │  │  │  │                        │ │  │   │
│  │  │  │  EIP: x.x.x.x                │  │  │  │                        │ │  │   │
│  │  │  └──────────────┬───────────────┘  │  │  │                        │ │  │   │
│  │  │                 │                   │  │  │                        │ │  │   │
│  │  │  ┌──────────────▼───────────────────────▼────────────────────────┐ │  │   │
│  │  │  │         Application Load Balancer (ALB)                       │ │  │   │
│  │  │  │         Scheme: internet-facing                               │ │  │   │
│  │  │  │         Listener: HTTP:80                                     │ │  │   │
│  │  │  │         Security Group: ALBSecurityGroup                      │ │  │   │
│  │  │  │         ┌─────────────────────────────────────────┐           │ │  │   │
│  │  │  │         │ Ingress: TCP:80 from CloudFront PL      │           │ │  │   │
│  │  │  │         │ Egress: TCP:80 to EC2SecurityGroup      │           │ │  │   │
│  │  │  │         └─────────────────────────────────────────┘           │ │  │   │
│  │  │  └──────────────────────────┬────────────────────────────────────┘ │  │   │
│  │  └─────────────────────────────┼──────────┘  └────────────────────────┘  │   │
│  │                                │                                          │   │
│  │                                │ HTTP:80                                  │   │
│  │                                │                                          │   │
│  │  ┌─────────────────────────────▼──────────┐                              │   │
│  │  │  Private Subnet 1: 10.0.3.0/24         │  ┌──────────────────────┐   │   │
│  │  │  Route: 0.0.0.0/0 → NAT Gateway        │  │ Private Subnet 2:    │   │   │
│  │  │  MapPublicIpOnLaunch: false            │  │ 10.0.4.0/24          │   │   │
│  │  │                                         │  │ (Reserved)           │   │   │
│  │  │  ┌───────────────────────────────────┐ │  └──────────────────────┘   │   │
│  │  │  │   EC2 Instance (c7g.xlarge)       │ │                              │   │
│  │  │  │   Private IP: 10.0.3.x            │ │                              │   │
│  │  │  │   No Public IP                    │ │                              │   │
│  │  │  │   Code-Server: HTTP:80            │ │                              │   │
│  │  │  │   Dev Servers: TCP:8501-8600      │ │                              │   │
│  │  │  │                                   │ │                              │   │
│  │  │  │   Security Group: EC2SecurityGroup│ │                              │   │
│  │  │  │   ┌─────────────────────────────┐ │ │                              │   │
│  │  │  │   │ Ingress: TCP:80 from ALB SG │ │ │                              │   │
│  │  │  │   │ Ingress: TCP:8501-8600 all  │ │ │                              │   │
│  │  │  │   │ Egress: All to 0.0.0.0/0    │ │ │                              │   │
│  │  │  │   └─────────────────────────────┘ │ │                              │   │
│  │  │  └───────────────┬───────────────────┘ │                              │   │
│  │  └──────────────────┼─────────────────────┘                              │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
│                        │                                                           │
│                        │ Outbound Traffic                                          │
│                        │ (apt, npm, pip, docker pull)                              │
│                        └──────────────► NAT Gateway ──────────► Internet           │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

Traffic Flows:
═════════════

Inbound (User → Code-Server):
  1. User HTTPS → CloudFront (TLS termination)
  2. CloudFront HTTP:80 → ALB (via ALBSecurityGroup: CloudFront PL allowed)
  3. ALB HTTP:80 → EC2 (via EC2SecurityGroup: ALB SG allowed)
  4. EC2 responds with code-server interface

Outbound (EC2 → Internet):
  1. EC2 initiates connection (apt-get, npm install, etc.)
  2. Traffic routes via PrivateRouteTable → NAT Gateway
  3. NAT Gateway translates private IP to EIP
  4. Traffic exits via Internet Gateway
  5. Response returns via same path (stateful NAT)

Security Group Chain:
  CloudFront → ALBSecurityGroup → EC2SecurityGroup → EC2 Instance
  (Each layer validates source before forwarding)

High Availability:
  - ALB spans 2 AZs (AZ-a, AZ-b)
  - EC2 in AZ-a (same as NAT Gateway to minimize cross-AZ charges)
  - NAT Gateway single AZ (cost-optimized for workshop)
  - Production: Deploy NAT Gateway per AZ for fault tolerance
```

### Key Security Benefits

1. **No Public IP on EC2**: Instance cannot be directly accessed from the internet
2. **Defense-in-Depth**: Three-layer security (CloudFront → ALB → EC2)
3. **Controlled Outbound Access**: NAT Gateway provides auditable internet access
4. **AWS Security Compliance**: Meets internal AWS security policies for EC2 instances
5. **Stable Origin**: ALB provides consistent endpoint for CloudFront

### Key Components

1. **CloudFront Distribution**: Public HTTPS endpoint for users, provides TLS termination and global edge caching
2. **Application Load Balancer**: Internet-facing load balancer in public subnets, provides stable origin for CloudFront
3. **EC2 Instance**: Code-server running in private subnet with no public IP address
4. **NAT Gateway**: Enables outbound internet access for EC2 to download dependencies
5. **Security Groups**: Defense-in-depth with CloudFront → ALB → EC2 security chain

## Security Considerations

- **Private Subnet Architecture**: EC2 instances have no public IP addresses
- **CloudFront-only Access**: Security groups enforce CloudFront → ALB → EC2 traffic flow
- **Password Authentication**: AWS Account ID required for code-server access
- **No SSH Access**: Use SSM Session Manager for secure instance access
- **All EBS Volumes Encrypted**: Data at rest encryption enabled
- **HTTPS Enforced**: CloudFront provides TLS termination
- **Defense-in-Depth**: Three-layer security validation (CloudFront → ALB → EC2)
- **Controlled Outbound**: NAT Gateway provides auditable internet access

## Cost Optimization

- **Single NAT Gateway**: Optimized for workshop/hackathon use (production should use NAT per AZ)
- **Use smaller instance types**: Consider t4g.medium for lighter workloads
- **Stop instances when not in use**: Significant cost savings for non-production
- **Use spot instances**: For non-critical environments
- **Clean up old stacks**: Delete unused CloudFormation stacks to avoid charges
- **Monitor NAT Gateway costs**: Primary ongoing cost component (~$32/month + data transfer)

## Updating the Stack

```bash
aws cloudformation update-stack \
  --stack-name code-server \
  --template-body file://code-server.yaml \
  --parameters \
    ParameterKey=InstanceType,ParameterValue=c7g.large \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

## Deleting the Stack

```bash
aws cloudformation delete-stack \
  --stack-name code-server \
  --region us-east-1
```

**Note**: The NAT Gateway's Elastic IP will be automatically released when the stack is deleted.

## Support

For issues or questions:
1. Check session notes: `.kiro/session-notes/`
2. Review improvements: `IMPROVEMENTS.md`
3. Check spec documentation: `.kiro/specs/workshop1/code-server/code-server-deployment/`