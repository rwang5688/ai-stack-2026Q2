# Code Server CloudFormation Template Improvements

## Private Subnet Security Architecture (February 2026)

### Overview
The most significant security improvement: moved EC2 instances from public subnets to private subnets with no public IP addresses, implementing defense-in-depth security architecture that meets AWS internal security policies.

### Security Benefits

1. **No Public IP Address**: EC2 instances cannot be directly accessed from the internet
2. **Defense-in-Depth**: Three-layer security validation (CloudFront → ALB → EC2)
3. **Controlled Outbound Access**: NAT Gateway provides auditable internet access for dependency installation
4. **Security Group Chain**: Each layer validates traffic source before forwarding
5. **AWS Compliance**: Meets internal AWS security policies for EC2 deployments
6. **Stable CloudFront Origin**: ALB provides consistent endpoint (no IP changes on instance replacement)

### Architecture Changes

**New Resources Added** (10):
- **NATGatewayEIP**: Elastic IP for NAT Gateway outbound traffic
- **NATGateway**: Enables EC2 instances to download dependencies from internet
- **PrivateRouteTable**: Routes private subnet traffic to NAT Gateway
- **PrivateRoute**: Default route (0.0.0.0/0) pointing to NAT Gateway
- **PrivateSubnetOneRouteTableAssociation**: Links private subnet 1 to route table
- **PrivateSubnetTwoRouteTableAssociation**: Links private subnet 2 to route table
- **ALBSecurityGroup**: Controls inbound traffic from CloudFront prefix list
- **ApplicationLoadBalancer**: Internet-facing ALB spanning two availability zones
- **ALBTargetGroup**: Contains EC2 instance with health checking
- **ALBListener**: Forwards HTTP:80 traffic from ALB to EC2

**Modified Resources** (6):
- **PrivateSubnetOne**: Removed `MapPublicIpOnLaunch: true` (no public IPs assigned)
- **PrivateSubnetTwo**: Removed `MapPublicIpOnLaunch: true` (no public IPs assigned)
- **SecurityGroup → EC2SecurityGroup**: Changed ingress from CloudFront prefix list to ALB security group
- **VSCodeInstanceEC2Instance**: Moved from public subnet to PrivateSubnetOne, no public IP
- **CloudFrontDistribution**: Changed origin from EC2 public IP to ALB DNS name
- **VSCodeInstanceSSMDoc**: Removed sample code, empty workshop directory for clean start

### Traffic Flows

**Inbound (User → Code-Server)**:
1. User connects via HTTPS to CloudFront distribution
2. CloudFront terminates TLS, forwards HTTP:80 to ALB
3. ALB security group validates traffic from CloudFront prefix list
4. ALB forwards to EC2 instance in private subnet
5. EC2 security group validates traffic from ALB security group
6. Code-server responds through same path

**Outbound (EC2 → Internet)**:
1. EC2 initiates connection (apt-get, npm install, pip, docker pull)
2. Traffic routes via PrivateRouteTable to NAT Gateway
3. NAT Gateway translates private IP to Elastic IP
4. Traffic exits via Internet Gateway
5. Response returns via stateful NAT connection

### Cost Considerations

**Single NAT Gateway Design**:
- Optimized for workshop/hackathon use (~$32/month + data transfer)
- EC2 and NAT Gateway in same AZ to minimize cross-AZ charges
- ALB spans two AZs for high availability

**Production Recommendations**:
- Deploy NAT Gateway per availability zone for fault tolerance
- Consider NAT instances for lower-traffic scenarios
- Monitor data transfer costs through NAT Gateway

### Implementation Details

**Circular Dependency Resolution**:
The security groups have a circular dependency (ALB → EC2, EC2 → ALB). Resolved using separate `AWS::EC2::SecurityGroupIngress` and `AWS::EC2::SecurityGroupEgress` resources instead of inline rules.

**Health Checking**:
ALB target group performs health checks on EC2:80 every 30 seconds, ensuring traffic only routes to healthy instances.

**User Experience**:
No change to end users - they still access via CloudFront HTTPS URL with AWS Account ID as password.

**Debugging Access**:
Use AWS Systems Manager Session Manager instead of SSH:
```bash
aws ssm start-session --target <instance-id>
```

**Template Validation**:
Template passes cfn-lint validation with 0 warnings after fixing:
- Removed unnecessary DependsOn declarations (intrinsic functions create implicit dependencies)
- Replaced hardcoded partition "aws" with !Ref AWS::Partition for multi-partition support

## Key Issues Fixed

### 1. **Node.js Installation Reliability**
**Problem:** NodeSource repository URLs are frequently broken or outdated
**Solution:** Use official Node.js binary distribution instead of apt repository

**Original:**
```yaml
- curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
- apt-get install -y nodejs
```

**Improved:**
```yaml
- rm -f /etc/apt/sources.list.d/nodesource.list  # Clean up broken repos
- curl -fsSL https://nodejs.org/dist/v20.18.0/node-v20.18.0-linux-arm64.tar.xz -o /tmp/node.tar.xz
- tar -xJf /tmp/node.tar.xz -C /opt/
- ln -sf /opt/node-v20.18.0-linux-arm64/bin/node /usr/local/bin/node
```

### 2. **SSM Association Targeting**
**Problem:** Tag-based targeting can be unreliable during instance startup
**Solution:** Use direct InstanceIds targeting with proper dependencies

**Original:**
```yaml
Targets:
  - Key: tag:SSMBootstrap
    Values:
      - true
```

**Improved:**
```yaml
Targets:
  - Key: InstanceIds
    Values:
      - !Ref VSCodeInstanceEC2Instance
DependsOn: 
  - VSCodeInstanceEC2Instance
  - WaitForInstanceReady
```

### 3. **Nginx Configuration Circular Dependency**
**Problem:** Nginx config references CloudFront domain before CloudFront is created
**Solution:** Use generic server_name that accepts any hostname

**Original:**
```yaml
server_name ${CloudFrontDistribution.DomainName};
```

**Improved:**
```yaml
server_name _;  # Accept any hostname
```

### 4. **SSM Session Manager Access for Debugging**
**Problem:** No way to troubleshoot when bootstrap fails in private subnet
**Solution:** Use AWS Systems Manager Session Manager for secure access

**Note:** With the private subnet architecture (February 2026), SSH access was removed. EC2 instances have no public IP addresses and cannot be accessed via SSH. Instead, use SSM Session Manager:

```bash
# Get instance ID from stack outputs
INSTANCE_ID=$(aws cloudformation describe-stacks \
  --stack-name code-server \
  --query 'Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue' \
  --output text)

# Start session
aws ssm start-session --target $INSTANCE_ID
```

**Benefits:**
- No need for SSH keys or bastion hosts
- Secure access without public IP addresses
- Audit trail in CloudTrail
- Works with private subnet architecture

### 5. **Explicit SSM Permissions**
**Problem:** AdministratorAccess should be enough but SSM needs explicit policy
**Solution:** Add AmazonSSMManagedInstanceCore policy explicitly

**Added:**
```yaml
ManagedPolicyArns:
  - !Sub arn:${AWS::Partition}:iam::aws:policy/AdministratorAccess
  - !Sub arn:${AWS::Partition}:iam::aws:policy/AmazonSSMManagedInstanceCore
```

### 6. **Better Error Handling**
**Problem:** Bootstrap continues even when steps fail
**Solution:** Add `set -e` to fail fast and proper timeouts

**Added to each step:**
```yaml
runCommand:
  - '#!/bin/bash'
  - set -e  # Exit on any error
  - # ... rest of commands
```

### 7. **Service Verification**
**Problem:** No verification that services actually started
**Solution:** Check service status at the end

**Added:**
```yaml
- systemctl is-active code-server@ubuntu
- systemctl is-active nginx
- echo "Bootstrap completed successfully!"
```

### 8. **Improved Code-Server Configuration**
**Problem:** Password configuration was complex and unreliable
**Solution:** Use AWS CLI to get Account ID dynamically

**Improved:**
```yaml
password: $(aws sts get-caller-identity --query Account --output text)
```

## Template Structure Improvements

### Simplified Parameters
- Reduced instance type options to commonly used ARM64 types
- Added debugging options
- Better parameter organization

### Better Resource Organization
- Clear section comments
- Logical grouping of resources
- Consistent naming conventions

### Enhanced Outputs
- Added direct IP access URL for debugging
- Clear password information
- SSM document reference for manual execution

## Reliability Improvements

1. **Dependency Management:** Proper CloudFormation dependencies ensure resources are created in the right order
2. **Timeout Handling:** Appropriate timeouts for each installation step
3. **Cleanup:** Remove broken repositories before installing new ones
4. **Verification:** Check that services are actually running before completing
5. **Fallback Options:** SSH access allows manual intervention when needed

## Testing Recommendations

1. **Test in Multiple Regions:** Ensure CloudFront prefix lists are correct
2. **Test Instance Types:** Verify ARM64 vs AMD64 compatibility
3. **Test Network Conditions:** Ensure bootstrap works with slow connections
4. **Test Failure Recovery:** Verify manual SSM execution works when association fails

These improvements make the template much more reliable and easier to troubleshoot when issues occur.

## Nginx Configuration Fix (December 17, 2025)

### Issue
Deployment succeeded but users were seeing the Nginx welcome page instead of code-server interface.

### Root Cause
The default nginx site (`/etc/nginx/sites-enabled/default`) was still enabled, taking precedence over the code-server configuration.

### Solution
Updated the CloudFormation template's `ConfigureCodeServer` step to:

1. **Remove default site**: `sudo rm -f /etc/nginx/sites-enabled/default`
2. **Add configuration validation**: `sudo nginx -t` before restart
3. **Maintain proper order**: Remove default → Enable code-server → Validate → Restart

### Code Changes
```yaml
# Before
- sudo systemctl restart code-server@ubuntu
- sudo ln -s ../sites-available/code-server /etc/nginx/sites-enabled/code-server
- sudo systemctl restart nginx

# After  
- sudo systemctl restart code-server@ubuntu
- sudo rm -f /etc/nginx/sites-enabled/default
- sudo ln -s ../sites-available/code-server /etc/nginx/sites-enabled/code-server
- sudo nginx -t
- sudo systemctl restart nginx
```

### Validation
Created `code_server/tests/nginx-config-test.py` to verify:
- Default site removal
- Configuration validation
- Proper proxy configuration
- WebSocket support

### Impact
- ✅ Fixes the "Nginx welcome page" issue
- ✅ Ensures code-server is properly accessible via CloudFront
- ✅ Adds configuration validation for reliability
- ✅ Maintains all existing functionality

This addresses **Requirements 1.1, 3.3** from the spec and implements **Property 5: Configuration Validation**.