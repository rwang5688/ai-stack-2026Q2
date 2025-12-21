# Code Server Deployment Guide

## Overview
This guide provides instructions for deploying a reliable, cloud-based VS Code development environment using the improved CloudFormation template.

## Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured
- EC2 Key Pair created in target region
- Basic understanding of CloudFormation

## Quick Start

### 1. Deploy the Stack
```bash
aws cloudformation create-stack \
  --stack-name code-server-dev \
  --template-body file://code_server/code-server-improved.yaml \
  --parameters \
    ParameterKey=EC2KeyPair,ParameterValue=your-key-pair-name \
    ParameterKey=AllowSSHAccess,ParameterValue=true \
  --capabilities CAPABILITY_IAM \
  --region us-west-2
```

### 2. Monitor Deployment
```bash
aws cloudformation wait stack-create-complete \
  --stack-name code-server-dev \
  --region us-west-2
```

### 3. Get Access Information
```bash
aws cloudformation describe-stacks \
  --stack-name code-server-dev \
  --region us-west-2 \
  --query 'Stacks[0].Outputs'
```

## Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `EC2KeyPair` | EC2 key pair for SSH access | ws-default-keypair | Yes |
| `InstanceType` | EC2 instance type (ARM64) | c7g.xlarge | No |
| `InstanceVolumeSize` | EBS volume size in GB | 30 | No |
| `AllowSSHAccess` | Enable SSH for debugging | true | No |
| `HomeFolder` | Default workspace directory | /home/ubuntu/workshop/ | No |
| `DevServerPort` | Application development port | 8081 | No |

## Accessing Code-Server

### Via CloudFront (Recommended)
1. Get the CloudFront URL from stack outputs
2. Navigate to: `https://<cloudfront-domain>/?folder=/home/ubuntu/workshop`
3. Login with password: Your AWS Account ID

### Via Direct IP (Debugging Only)
1. Get the public IP from stack outputs
2. Navigate to: `http://<public-ip>`
3. Login with same password

## Troubleshooting

### Bootstrap Fails
1. Check SSM Association status in Systems Manager console
2. Review bootstrap logs in S3 bucket (check stack outputs for bucket name)
3. SSH into instance if AllowSSHAccess=true:
   ```bash
   ssh -i your-key.pem ubuntu@<public-ip>
   sudo systemctl status code-server@ubuntu
   sudo systemctl status nginx
   ```

### 504 Gateway Timeout
- **Cause**: Bootstrap process still running or failed
- **Solution**: Wait 10-15 minutes for bootstrap to complete, or check SSM logs

### Cannot SSH to Instance
- **Cause**: AllowSSHAccess parameter set to false
- **Solution**: Update stack with AllowSSHAccess=true

### Services Not Running
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@<public-ip>

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

## Manual Bootstrap Execution

If the automatic bootstrap fails, you can manually execute the SSM document:

1. Go to AWS Systems Manager → Documents
2. Find the document (name in stack outputs)
3. Click "Run command"
4. Select your instance
5. Execute and monitor progress

## Architecture

```
┌─────────────┐
│   Internet  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   CloudFront    │  HTTPS termination
└──────┬──────────┘  Global CDN
       │
       ▼
┌─────────────────┐
│  Security Group │  CloudFront IPs only
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   EC2 Instance  │  Ubuntu 22.04 ARM64
│                 │
│  ┌───────────┐  │
│  │   nginx   │  │  Reverse proxy :80
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │code-server│  │  VS Code :8080
│  └───────────┘  │
└─────────────────┘
```

## Security Considerations

- CloudFront-only access enforced via security groups
- Password authentication required for code-server
- SSH access optional and configurable
- All EBS volumes encrypted at rest
- HTTPS enforced via CloudFront

## Cost Optimization

- Use smaller instance types for development (t4g.medium)
- Stop instances when not in use
- Use spot instances for non-production environments
- Clean up old CloudFormation stacks

## Updating the Stack

```bash
aws cloudformation update-stack \
  --stack-name code-server-dev \
  --template-body file://code_server/code-server-improved.yaml \
  --parameters \
    ParameterKey=EC2KeyPair,UsePreviousValue=true \
    ParameterKey=InstanceType,ParameterValue=c7g.large \
  --capabilities CAPABILITY_IAM \
  --region us-west-2
```

## Deleting the Stack

```bash
aws cloudformation delete-stack \
  --stack-name code-server-dev \
  --region us-west-2
```

## Support

For issues or questions:
1. Check session notes: `.kiro/session-notes/20251218-session-notes.md`
2. Review improvements: `code_server/IMPROVEMENTS.md`
3. Check spec documentation: `.kiro/specs/code-server-deployment/`