# Code Server CloudFormation Templates

## Template Files

### `code-server.yaml` (Current Production Template)
- **Purpose**: Production-ready template with private subnet security architecture
- **Usage**: Use for all deployments (workshops, hackathons, production)
- **Status**: Current template implementing secure private subnet deployment
- **Architecture**: EC2 in private subnet, accessed via CloudFront → ALB → EC2
- **Security**: No public IP on EC2, defense-in-depth security group chain

## Architecture

### Overview

The code-server deployment uses a secure, multi-tier architecture with EC2 instances in private subnets, accessed through CloudFront and an Application Load Balancer. This design provides defense-in-depth security while maintaining internet access for dependency installation.

### Architecture Diagram

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

### Key Components

1. **CloudFront Distribution**: Public HTTPS endpoint for users, provides TLS termination and global edge caching
2. **Application Load Balancer**: Internet-facing load balancer in public subnets, provides stable origin for CloudFront
3. **EC2 Instance**: Code-server running in private subnet with no public IP address
4. **NAT Gateway**: Enables outbound internet access for EC2 to download dependencies
5. **Security Groups**: Defense-in-depth with CloudFront → ALB → EC2 security chain

### Deployment

Deploy the stack using the AWS CLI:

```bash
aws cloudformation create-stack \
  --stack-name code-server \
  --template-body file://code-server.yaml \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

The stack name `code-server` is used throughout the workshop documentation. After deployment completes (approximately 10-15 minutes), retrieve the CloudFront URL from the stack outputs:

```bash
aws cloudformation describe-stacks \
  --stack-name code-server \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontURL`].OutputValue' \
  --output text
```

Access the code-server using your AWS Account ID as the password.

## Development Tools

### Installing Validation Tools

Install cfn-lint for CloudFormation template validation:

```bash
pip install -r requirements.txt
```

### Running Validation

Validate the CloudFormation template:

```bash
# Run cfn-lint to check for errors and warnings
cfn-lint code-server.yaml

# Run with specific rules
cfn-lint code-server.yaml --ignore-checks W3002

# Get detailed output
cfn-lint code-server.yaml --format detailed
```

## Update Workflow

When new versions of the template are needed:

1. **Review requirements**: Check if changes align with security architecture
2. **Update template**: Modify `code-server.yaml` while maintaining private subnet design
3. **Test deployment**: Verify template deploys successfully with all security controls
4. **Validate architecture**: Ensure CloudFront → ALB → EC2 flow works correctly

## Actual Fixes Applied

### 1. Private Subnet Security Architecture (February 2026)
The most significant improvement: moved EC2 instances from public subnets to private subnets with no public IP addresses, implementing defense-in-depth security.

**New Resources Added** (10):
- **NATGatewayEIP**: Elastic IP for NAT Gateway
- **NATGateway**: Enables outbound internet access from private subnets
- **PrivateRouteTable**: Route table directing traffic to NAT Gateway
- **PrivateRoute**: Default route (0.0.0.0/0) to NAT Gateway
- **PrivateSubnetOneRouteTableAssociation**: Links private subnet 1 to route table
- **PrivateSubnetTwoRouteTableAssociation**: Links private subnet 2 to route table
- **ALBSecurityGroup**: Controls inbound traffic from CloudFront prefix list
- **ApplicationLoadBalancer**: Internet-facing ALB in public subnets
- **ALBTargetGroup**: Contains EC2 instance for health checking
- **ALBListener**: Forwards HTTP:80 traffic to target group

**Modified Resources** (6):
- **PrivateSubnetOne**: Removed `MapPublicIpOnLaunch: true` (no public IPs)
- **PrivateSubnetTwo**: Removed `MapPublicIpOnLaunch: true` (no public IPs)
- **SecurityGroup → EC2SecurityGroup**: Changed ingress from CloudFront to ALB security group
- **VSCodeInstanceEC2Instance**: Moved from public subnet to PrivateSubnetOne
- **CloudFrontDistribution**: Changed origin from EC2 to ALB DNS name
- **VSCodeInstanceSSMDoc**: Removed sample code, empty workshop directory

**Security Benefits**:
- EC2 instances have no public IP addresses (cannot be directly accessed from internet)
- Security group chaining: CloudFront → ALB → EC2 (defense-in-depth)
- NAT Gateway provides controlled outbound access for dependency installation
- ALB provides health checking and stable CloudFront origin
- Circular dependency resolved using separate SecurityGroupIngress/Egress resources

### 2. YAML Parsing Issues (December 2025)
The original template had unquoted multi-line shell commands that caused CloudFormation to fail with "null values are not allowed in templates".

```yaml
# Original (causes null values error)
runCommand:
  - apt-get update && DEBIAN_FRONTEND=noninteractive apt-get
    install -y curl

# Fixed (properly quoted)
runCommand:
  - 'apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y curl'
```

### 3. SSM Association Reliability (December 2025)
Changed from tag-based targeting to instance ID targeting for more reliable bootstrap execution.

```yaml
# Original (less reliable)
Targets:
  - Key: tag:SSMBootstrap
    Values: [true]

# Fixed (more reliable)  
Targets:
  - Key: InstanceIds
    Values: [!Ref VSCodeInstanceEC2Instance]
```

## Design Philosophy

- **Minimal changes**: Preserve original structure and installation methods for easy maintenance
- **Deployment reliability**: Fix only critical issues that prevent deployment
- **Future compatibility**: Easy to merge upstream updates

## Related Documentation

- **Specification**: `.kiro/specs/workshop1/code-server/code-server-deployment/`
- **Session Notes**: `.kiro/session-notes/`
- **Project README**: `../../README.md`