# Design Document: Code Server Private IP Deployment

## Overview

This design transforms the code-server CloudFormation deployment from a public-facing EC2 architecture to a secure, private subnet deployment that meets AWS internal security requirements. The solution introduces a multi-tier architecture with EC2 instances in private subnets, an Application Load Balancer (ALB) in public subnets, and CloudFront as the public-facing endpoint.

### Key Architectural Changes

1. **Network Isolation**: EC2 instances move from public subnets (10.0.1.0/24, 10.0.2.0/24) to private subnets (10.0.3.0/24, 10.0.4.0/24) with no public IP addresses
2. **Internet Access**: NAT Gateway in public subnet enables private instances to download dependencies while preventing inbound internet access
3. **Load Balancing**: Application Load Balancer provides a stable, highly available origin for CloudFront
4. **Security Layers**: Defense-in-depth with CloudFront → ALB → EC2 security group chain
5. **Clean Environment**: Bootstrap process simplified to remove pre-existing workshop code

### Design Goals

- Comply with AWS internal security policies requiring private IP-only EC2 instances
- Maintain existing code-server functionality and user experience
- Provide reliable internet access for dependency installation
- Enable secure access through CloudFront CDN
- Deliver clean workshop environment without sample code

## Architecture

### Network Topology

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

### VPC Configuration

The existing VPC (10.0.0.0/16) contains four subnets across two availability zones:

**Public Subnets** (existing, no changes):
- PublicSubnetOne: 10.0.1.0/24 (AZ-a) - hosts NAT Gateway and ALB
- PublicSubnetTwo: 10.0.2.0/24 (AZ-b) - hosts ALB

**Private Subnets** (existing, routing changes):
- PrivateSubnetOne: 10.0.3.0/24 (AZ-a) - hosts EC2 instance
- PrivateSubnetTwo: 10.0.4.0/24 (AZ-b) - reserved for future use

### Routing Architecture

**Public Subnet Routing** (unchanged):
- Route Table: PublicOneRouteTable, PublicTwoRouteTable
- Default Route: 0.0.0.0/0 → Internet Gateway
- Purpose: Direct internet access for ALB and NAT Gateway

**Private Subnet Routing** (new):
- Route Table: PrivateRouteTable (new resource)
- Default Route: 0.0.0.0/0 → NAT Gateway
- Purpose: Outbound-only internet access for EC2 instances
- Associations: PrivateSubnetOne, PrivateSubnetTwo

### NAT Gateway Design

**Resource**: NATGatewayEIP + NATGateway

**Placement**: PublicSubnetOne (10.0.1.0/24)

**Purpose**: 
- Enable private EC2 instances to initiate outbound connections to the internet
- Download dependencies (apt packages, npm modules, Python packages, Docker images)
- Access AWS service endpoints
- Block all inbound connections from the internet

**High Availability Considerations**:
- Single NAT Gateway in one AZ (cost-optimized for workshop environment)
- Production deployments should use NAT Gateway per AZ for fault tolerance
- EC2 instance deployed in same AZ as NAT Gateway to minimize cross-AZ data transfer

### Application Load Balancer Design

**Resource**: ApplicationLoadBalancer + ALBTargetGroup + ALBListener

**Placement**: Spans PublicSubnetOne and PublicSubnetTwo for high availability

**Configuration**:
- Scheme: internet-facing
- IP Address Type: ipv4
- Listener: HTTP port 80
- Target Type: instance
- Target: VSCodeInstanceEC2Instance on port 80
- Health Check: HTTP:80 / (path: /, interval: 30s, timeout: 5s, healthy threshold: 2, unhealthy threshold: 2)

**Purpose**:
- Provide stable DNS endpoint for CloudFront origin
- Decouple CloudFront from EC2 instance lifecycle
- Enable future horizontal scaling (multiple EC2 instances)
- Perform health checks and automatic failover

### Security Group Architecture

**ALBSecurityGroup** (new):
- Ingress: HTTP (80) from CloudFront prefix list (com.amazonaws.global.cloudfront.origin-facing)
- Egress: HTTP (80) to EC2SecurityGroup
- Purpose: Restrict ALB to accept only CloudFront traffic

**EC2SecurityGroup** (modified from existing SecurityGroup):
- Ingress Rules:
  - HTTP (80) from ALBSecurityGroup (replaces CloudFront prefix list)
  - TCP (8501-8600) from 0.0.0.0/0 (development server ports, unchanged)
- Egress: All traffic to 0.0.0.0/0 (unchanged)
- Purpose: Restrict EC2 to accept HTTP only from ALB, allow dev server access

**Security Group Chaining**:
```
CloudFront → ALBSecurityGroup → EC2SecurityGroup → EC2 Instance
```

This creates defense-in-depth where each layer validates the source of traffic.

### CloudFront Configuration

**Resource**: CloudFrontDistribution (modified)

**Origin Changes**:
- Old: EC2 instance public DNS name (e.g., ec2-x-x-x-x.compute.amazonaws.com)
- New: ALB DNS name (e.g., app-lb-xxxxxxxxx.region.elb.amazonaws.com)
- Protocol: HTTP-only (unchanged)

**Behavior**: All other CloudFront settings remain unchanged (cache policy, origin request policy, viewer protocol policy)

**Purpose**: Provide HTTPS endpoint for users while communicating with ALB over HTTP

## Components and Interfaces

### New CloudFormation Resources

#### 1. NATGatewayEIP
```yaml
Type: AWS::EC2::EIP
Properties:
  Domain: vpc
```
Elastic IP address for NAT Gateway to provide stable public IP for outbound traffic.

#### 2. NATGateway
```yaml
Type: AWS::EC2::NatGateway
Properties:
  AllocationId: !GetAtt NATGatewayEIP.AllocationId
  SubnetId: !Ref PublicSubnetOne
DependsOn: NATGatewayEIP
```
NAT Gateway enabling private subnet instances to access the internet.

#### 3. PrivateRouteTable
```yaml
Type: AWS::EC2::RouteTable
Properties:
  VpcId: !Ref VPC
```
Route table for private subnets directing traffic to NAT Gateway.

#### 4. PrivateRoute
```yaml
Type: AWS::EC2::Route
Properties:
  RouteTableId: !Ref PrivateRouteTable
  DestinationCidrBlock: 0.0.0.0/0
  NatGatewayId: !Ref NATGateway
DependsOn: NATGateway
```
Default route sending all private subnet traffic through NAT Gateway.

#### 5. PrivateSubnetOneRouteTableAssociation
```yaml
Type: AWS::EC2::SubnetRouteTableAssociation
Properties:
  RouteTableId: !Ref PrivateRouteTable
  SubnetId: !Ref PrivateSubnetOne
```
Associates PrivateSubnetOne with the private route table.

#### 6. PrivateSubnetTwoRouteTableAssociation
```yaml
Type: AWS::EC2::SubnetRouteTableAssociation
Properties:
  RouteTableId: !Ref PrivateRouteTable
  SubnetId: !Ref PrivateSubnetTwo
```
Associates PrivateSubnetTwo with the private route table.

#### 7. ALBSecurityGroup
```yaml
Type: AWS::EC2::SecurityGroup
Properties:
  GroupDescription: Security group for Application Load Balancer
  VpcId: !Ref VPC
  SecurityGroupIngress:
    - Description: Allow HTTP from CloudFront
      IpProtocol: tcp
      FromPort: 80
      ToPort: 80
      SourcePrefixListId: !FindInMap [AWSRegions2PrefixListID, !Ref AWS::Region, PrefixList]
  SecurityGroupEgress:
    - Description: Allow HTTP to EC2 instances
      IpProtocol: tcp
      FromPort: 80
      ToPort: 80
      DestinationSecurityGroupId: !Ref EC2SecurityGroup
```
Security group controlling traffic to the Application Load Balancer.

#### 8. ApplicationLoadBalancer
```yaml
Type: AWS::ElasticLoadBalancingV2::LoadBalancer
Properties:
  Type: application
  Scheme: internet-facing
  IpAddressType: ipv4
  Subnets:
    - !Ref PublicSubnetOne
    - !Ref PublicSubnetTwo
  SecurityGroups:
    - !Ref ALBSecurityGroup
```
Application Load Balancer distributing traffic to EC2 instances.

#### 9. ALBTargetGroup
```yaml
Type: AWS::ElasticLoadBalancingV2::TargetGroup
Properties:
  VpcId: !Ref VPC
  Port: 80
  Protocol: HTTP
  TargetType: instance
  HealthCheckEnabled: true
  HealthCheckProtocol: HTTP
  HealthCheckPath: /
  HealthCheckIntervalSeconds: 30
  HealthCheckTimeoutSeconds: 5
  HealthyThresholdCount: 2
  UnhealthyThresholdCount: 2
  Targets:
    - Id: !Ref VSCodeInstanceEC2Instance
      Port: 80
```
Target group containing EC2 instance for ALB to route traffic.

#### 10. ALBListener
```yaml
Type: AWS::ElasticLoadBalancingV2::Listener
Properties:
  LoadBalancerArn: !Ref ApplicationLoadBalancer
  Port: 80
  Protocol: HTTP
  DefaultActions:
    - Type: forward
      TargetGroupArn: !Ref ALBTargetGroup
```
Listener on ALB forwarding HTTP traffic to target group.

### Modified CloudFormation Resources

#### 1. PrivateSubnetOne (property change)
```yaml
# REMOVE this property:
MapPublicIpOnLaunch: true

# Result: instances in this subnet will not receive public IPs
```

#### 2. PrivateSubnetTwo (property change)
```yaml
# REMOVE this property:
MapPublicIpOnLaunch: true

# Result: instances in this subnet will not receive public IPs
```

#### 3. SecurityGroup (rename to EC2SecurityGroup, modify ingress)
```yaml
# CHANGE ingress rule from:
SecurityGroupIngress:
  - Description: Allow HTTP from CloudFront
    IpProtocol: tcp
    FromPort: 80
    ToPort: 80
    SourcePrefixListId: !FindInMap [AWSRegions2PrefixListID, !Ref AWS::Region, PrefixList]

# TO:
SecurityGroupIngress:
  - Description: Allow HTTP from ALB
    IpProtocol: tcp
    FromPort: 80
    ToPort: 80
    SourceSecurityGroupId: !Ref ALBSecurityGroup
```

#### 4. VSCodeInstanceEC2Instance (property changes)
```yaml
# CHANGE subnet from:
SubnetId: !Ref PublicSubnetOne

# TO:
SubnetId: !Ref PrivateSubnetOne

# ADD dependency:
DependsOn:
  - PrivateSubnetOneRouteTableAssociation
```

#### 5. CloudFrontDistribution (origin change)
```yaml
# CHANGE origin from:
Origins:
  - DomainName: !GetAtt VSCodeInstanceEC2Instance.PublicDnsName
    Id: !Sub CloudFront-${AWS::StackName}
    CustomOriginConfig:
      OriginProtocolPolicy: http-only

# TO:
Origins:
  - DomainName: !GetAtt ApplicationLoadBalancer.DNSName
    Id: !Sub CloudFront-${AWS::StackName}
    CustomOriginConfig:
      OriginProtocolPolicy: http-only

# ADD dependency:
DependsOn: ApplicationLoadBalancer
```

#### 6. VSCodeInstanceSSMDoc (bootstrap script changes)

**Remove these steps**:
- InstallPython step: Remove git clone command
- InstallPython2 step: Remove entirely (pip install from requirements.txt, playwright, streamlit)

**Modify InstallPython step**:
```yaml
# REMOVE this command:
- git clone https://github.com/VincentV89/agentic-ai-with-mcp-and-strands /home/ubuntu/workshop

# ADD this command:
- mkdir -p /home/ubuntu/workshop
- chown ubuntu:ubuntu /home/ubuntu/workshop
```

**Remove InstallPython2 step entirely** (the entire action block)

### Resource Dependency Graph

```
VPC
├─ InternetGateway
│  └─ GatewayAttachment
│     ├─ PublicSubnetOne
│     │  ├─ PublicOneRouteTable
│     │  │  ├─ PublicOneRoute (depends on GatewayAttachment)
│     │  │  └─ PublicOneRouteTableAssoc
│     │  ├─ NATGatewayEIP
│     │  │  └─ NATGateway (depends on NATGatewayEIP)
│     │  │     └─ PrivateRouteTable
│     │  │        ├─ PrivateRoute (depends on NATGateway)
│     │  │        ├─ PrivateSubnetOneRouteTableAssociation
│     │  │        └─ PrivateSubnetTwoRouteTableAssociation
│     │  └─ ALBSecurityGroup
│     │     └─ ApplicationLoadBalancer (depends on ALBSecurityGroup, PublicSubnetOne, PublicSubnetTwo)
│     │        ├─ ALBTargetGroup
│     │        │  └─ ALBListener
│     │        └─ CloudFrontDistribution (depends on ApplicationLoadBalancer)
│     └─ PublicSubnetTwo
│        ├─ PublicTwoRouteTable
│        │  ├─ PublicTwoRoute (depends on GatewayAttachment)
│        │  └─ PublicTwoRouteTableAssoc
│        └─ (ALB spans both public subnets)
├─ PrivateSubnetOne
│  └─ EC2SecurityGroup
│     └─ VSCodeInstanceEC2Instance (depends on PrivateSubnetOneRouteTableAssociation)
└─ PrivateSubnetTwo
```

### Interface Contracts

#### CloudFront → ALB
- Protocol: HTTP
- Port: 80
- Source Validation: CloudFront prefix list in ALBSecurityGroup
- Headers: All headers forwarded via origin request policy
- Cookies: All cookies forwarded
- Query Strings: All query strings forwarded

#### ALB → EC2
- Protocol: HTTP
- Port: 80
- Target Type: instance
- Health Check: GET / every 30s
- Deregistration Delay: 300s (default)
- Stickiness: None (single instance)

#### EC2 → Internet (via NAT)
- Direction: Outbound only
- Protocols: All (TCP, UDP, ICMP)
- Destinations: 0.0.0.0/0
- Use Cases: apt-get, npm, pip, docker pull, AWS API calls

#### User → CloudFront
- Protocol: HTTPS (allow-all viewer protocol policy)
- Authentication: code-server password (AWS Account ID)
- Session: Maintained via cookies

## Data Models

### Network Configuration

```yaml
VPC:
  CIDR: 10.0.0.0/16
  EnableDnsSupport: true
  EnableDnsHostnames: true

PublicSubnets:
  - Name: PublicSubnetOne
    CIDR: 10.0.1.0/24
    AvailabilityZone: AZ-a
    MapPublicIpOnLaunch: true
    RouteTable: PublicOneRouteTable
    Routes:
      - Destination: 0.0.0.0/0
        Target: InternetGateway
  
  - Name: PublicSubnetTwo
    CIDR: 10.0.2.0/24
    AvailabilityZone: AZ-b
    MapPublicIpOnLaunch: true
    RouteTable: PublicTwoRouteTable
    Routes:
      - Destination: 0.0.0.0/0
        Target: InternetGateway

PrivateSubnets:
  - Name: PrivateSubnetOne
    CIDR: 10.0.3.0/24
    AvailabilityZone: AZ-a
    MapPublicIpOnLaunch: false  # Changed from true
    RouteTable: PrivateRouteTable  # Changed from public route table
    Routes:
      - Destination: 0.0.0.0/0
        Target: NATGateway  # Changed from InternetGateway
  
  - Name: PrivateSubnetTwo
    CIDR: 10.0.4.0/24
    AvailabilityZone: AZ-b
    MapPublicIpOnLaunch: false  # Changed from true
    RouteTable: PrivateRouteTable  # Changed from public route table
    Routes:
      - Destination: 0.0.0.0/0
        Target: NATGateway  # Changed from InternetGateway
```

### Security Group Rules

```yaml
ALBSecurityGroup:
  Ingress:
    - Protocol: TCP
      Port: 80
      Source: CloudFront Prefix List (pl-XXXXXXXX)
      Description: "Allow HTTP from CloudFront"
  Egress:
    - Protocol: TCP
      Port: 80
      Destination: EC2SecurityGroup
      Description: "Allow HTTP to EC2 instances"

EC2SecurityGroup:
  Ingress:
    - Protocol: TCP
      Port: 80
      Source: ALBSecurityGroup
      Description: "Allow HTTP from ALB"
    - Protocol: TCP
      PortRange: 8501-8600
      Source: 0.0.0.0/0
      Description: "Allow development server access"
  Egress:
    - Protocol: All
      Port: All
      Destination: 0.0.0.0/0
      Description: "Allow all outbound traffic"
```

### Load Balancer Configuration

```yaml
ApplicationLoadBalancer:
  Type: application
  Scheme: internet-facing
  IpAddressType: ipv4
  Subnets:
    - PublicSubnetOne
    - PublicSubnetTwo
  SecurityGroups:
    - ALBSecurityGroup
  
  TargetGroup:
    Protocol: HTTP
    Port: 80
    TargetType: instance
    VpcId: VPC
    HealthCheck:
      Protocol: HTTP
      Path: /
      Port: traffic-port
      IntervalSeconds: 30
      TimeoutSeconds: 5
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 2
    Targets:
      - Id: VSCodeInstanceEC2Instance
        Port: 80
  
  Listener:
    Port: 80
    Protocol: HTTP
    DefaultAction:
      Type: forward
      TargetGroupArn: ALBTargetGroup
```

### CloudFront Distribution

```yaml
CloudFrontDistribution:
  Enabled: true
  HttpVersion: http2
  
  Origin:
    DomainName: ApplicationLoadBalancer.DNSName  # Changed from EC2 PublicDnsName
    Id: CloudFront-${StackName}
    CustomOriginConfig:
      OriginProtocolPolicy: http-only
      HTTPPort: 80
  
  DefaultCacheBehavior:
    TargetOriginId: CloudFront-${StackName}
    ViewerProtocolPolicy: allow-all
    AllowedMethods: [GET, HEAD, OPTIONS, PUT, PATCH, POST, DELETE]
    CachePolicyId: VSCodeInstanceCachePolicy
    OriginRequestPolicyId: 216adef6-5c7f-47e4-b989-5492eafa07d3  # Managed-AllViewer
```

### EC2 Instance Configuration

```yaml
VSCodeInstanceEC2Instance:
  InstanceType: c7g.xlarge
  ImageId: Ubuntu 22.04 ARM64 (from SSM parameter)
  SubnetId: PrivateSubnetOne  # Changed from PublicSubnetOne
  SecurityGroupIds:
    - EC2SecurityGroup
  IamInstanceProfile: VSCodeInstanceProfile
  BlockDeviceMappings:
    - DeviceName: /dev/sda1
      Ebs:
        VolumeSize: 50
        VolumeType: gp3
        Encrypted: true
        DeleteOnTermination: true
  UserData:
    - mkdir -p /home/ubuntu/workshop
    - chown ubuntu:ubuntu /home/ubuntu/workshop
  Tags:
    - Key: SSMBootstrap
      Value: true
  
  # No public IP assigned (MapPublicIpOnLaunch: false on subnet)
  # No PublicIp property
  # No AssociatePublicIpAddress property
```

### Bootstrap Process Changes

```yaml
VSCodeInstanceSSMDoc:
  Steps:
    # Unchanged steps:
    - InstallAWSCLI
    - InstallQCLI
    - InstallDocker
    - InstallGit
    - InstallNode
    - InstallCDK
    - InstallJava
    - UpdateProfile
    - ConfigureCodeServer
    
    # Modified step:
    - InstallPython:
        Changes:
          Remove:
            - git clone https://github.com/VincentV89/agentic-ai-with-mcp-and-strands /home/ubuntu/workshop
          Add:
            - mkdir -p /home/ubuntu/workshop
            - chown ubuntu:ubuntu /home/ubuntu/workshop
    
    # Removed step:
    - InstallPython2: DELETED
        # Previously installed requirements.txt, pyopenssl, playwright, streamlit
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property Reflection

After analyzing all 46 acceptance criteria, I identified that the vast majority are specific configuration checks for the CloudFormation template (examples rather than universal properties). These criteria validate that specific resources exist with specific configurations. Since this is infrastructure-as-code, the "correctness" is primarily about template structure rather than runtime behavior across multiple inputs.

Key observations:
- Most criteria check for presence/absence of specific CloudFormation resources
- Many criteria check specific property values in the template
- Few criteria describe runtime behavior that varies across inputs
- Integration behavior (traffic flow) is inherent to AWS service configuration

Given this is a CloudFormation template modification, the correctness properties focus on template validation rather than property-based testing of runtime behavior. The testing strategy will emphasize:
1. Static template validation (linting, structure checks)
2. Deployment testing (stack creation succeeds)
3. Integration testing (end-to-end traffic flow)
4. Configuration verification (resources have correct properties)

### Template Structure Properties

Since all acceptance criteria are configuration checks, we consolidate them into logical groupings that can be validated through template analysis:

### Property 1: Private Subnet Isolation

For the EC2 instance resource in the CloudFormation template, it must be configured to deploy in a private subnet without public IP assignment.

Specifically:
- SubnetId property references PrivateSubnetOne
- PrivateSubnetOne has MapPublicIpOnLaunch set to false
- PrivateSubnetTwo has MapPublicIpOnLaunch set to false
- No AssociatePublicIpAddress property on the EC2 instance

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 5.5**

### Property 2: NAT Gateway Configuration Completeness

For the NAT Gateway infrastructure in the CloudFormation template, all required resources must be present and correctly configured.

Specifically:
- NATGatewayEIP resource exists with Domain: vpc
- NATGateway resource exists in PublicSubnetOne
- NATGateway references NATGatewayEIP via AllocationId
- PrivateRouteTable resource exists
- PrivateRoute resource exists with DestinationCidrBlock: 0.0.0.0/0 and NatGatewayId reference
- PrivateSubnetOneRouteTableAssociation exists linking PrivateSubnetOne to PrivateRouteTable
- PrivateSubnetTwoRouteTableAssociation exists linking PrivateSubnetTwo to PrivateRouteTable

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

### Property 3: Application Load Balancer Configuration Completeness

For the Application Load Balancer infrastructure in the CloudFormation template, all required resources must be present and correctly configured.

Specifically:
- ALBSecurityGroup resource exists
- ApplicationLoadBalancer resource exists with Subnets: [PublicSubnetOne, PublicSubnetTwo]
- ApplicationLoadBalancer references ALBSecurityGroup
- ALBTargetGroup resource exists with Port: 80, Protocol: HTTP, TargetType: instance
- ALBTargetGroup Targets includes VSCodeInstanceEC2Instance on Port: 80
- ALBTargetGroup has HealthCheckEnabled: true with valid health check configuration
- ALBListener resource exists with Port: 80, Protocol: HTTP
- ALBListener DefaultActions forwards to ALBTargetGroup

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.7**

### Property 4: Security Group Chain Configuration

For the security groups in the CloudFormation template, they must implement the CloudFront → ALB → EC2 security chain.

Specifically:
- ALBSecurityGroup ingress allows TCP port 80 from CloudFront prefix list
- ALBSecurityGroup egress allows TCP port 80 to EC2SecurityGroup
- EC2SecurityGroup ingress allows TCP port 80 from ALBSecurityGroup
- EC2SecurityGroup ingress allows TCP ports 8501-8600 from 0.0.0.0/0
- EC2SecurityGroup egress allows all traffic to 0.0.0.0/0

**Validates: Requirements 3.5, 3.6, 5.1, 5.2, 5.3, 5.4, 5.6**

### Property 5: CloudFront Origin Configuration

For the CloudFront distribution in the CloudFormation template, it must use the ALB as its origin.

Specifically:
- CloudFrontDistribution Origins[0].DomainName references ApplicationLoadBalancer.DNSName
- CloudFrontDistribution Origins[0].CustomOriginConfig.OriginProtocolPolicy is "http-only"

**Validates: Requirements 4.1, 4.2**

### Property 6: Resource Dependency Chain

For the CloudFormation template, explicit dependencies must be declared to ensure correct creation order.

Specifically:
- NATGateway has DependsOn: NATGatewayEIP
- PrivateRoute has DependsOn: NATGateway
- VSCodeInstanceEC2Instance has DependsOn: PrivateSubnetOneRouteTableAssociation
- CloudFrontDistribution has DependsOn: ApplicationLoadBalancer

**Validates: Requirements 6.1, 6.2, 6.6, 6.7, 6.9**

Note: Requirements 6.3, 6.4, 6.5 are satisfied implicitly by CloudFormation's automatic dependency resolution when using !Ref or !GetAtt.

### Property 7: Bootstrap Process Cleanup

For the SSM document in the CloudFormation template, workshop-specific code and dependencies must be removed.

Specifically:
- InstallPython step does NOT contain "git clone" command for agentic-ai-with-mcp-and-strands
- InstallPython step DOES contain "mkdir -p /home/ubuntu/workshop"
- InstallPython2 step does NOT exist in the document
- No step contains "pip install -r /home/ubuntu/workshop/requirements.txt"
- No step contains "pip install pyopenssl --upgrade"
- No step contains "playwright install"
- No step contains "pip install streamlit"

**Validates: Requirements 7.1, 7.2, 7.3, 7.4**

### Property 8: Development Tool Preservation

For the SSM document in the CloudFormation template, all essential development tools must remain installed.

Specifically:
- InstallAWSCLI step exists
- InstallQCLI step exists
- InstallDocker step exists
- InstallGit step exists
- InstallNode step exists
- InstallPython step exists (modified but present)
- InstallJava step exists
- InstallCDK step exists
- ConfigureCodeServer step exists with all extension installations

**Validates: Requirements 7.5**

### Property 9: Code Server Configuration Preservation

For the SSM document in the CloudFormation template, code-server configuration must remain unchanged.

Specifically:
- ConfigureCodeServer step creates /home/ubuntu/.config/code-server/config.yaml
- config.yaml contains hashed-password using AWS account ID
- settings.json contains terminal.integrated.cwd: "/home/ubuntu/workshop/"
- nginx configuration routes / to localhost:8080
- nginx configuration routes /${DevServerBasePath} to localhost:${DevServerPort}
- Extension installations include: amazon-q-vscode, auto-run-command, vscode-java-pack, live-server, jupyter, python, debugpy
- CloudFront output URL includes ?folder=/home/ubuntu/workshop

**Validates: Requirements 8.2, 8.3, 8.4, 8.6**

### Property 10: SSM Access Preservation

For the EC2 instance in the CloudFormation template, SSM Session Manager access must remain enabled.

Specifically:
- VSCodeInstanceProfile references VSCodeInstanceRole
- VSCodeInstanceRole has AdministratorAccess managed policy (includes SSM permissions)
- VSCodeInstanceEC2Instance has IamInstanceProfile: VSCodeInstanceProfile

**Validates: Requirements 8.5**

## Error Handling

### CloudFormation Stack Creation Failures

**NAT Gateway Creation Failure**:
- Cause: EIP allocation limit reached in region
- Detection: CloudFormation CREATE_FAILED event for NATGateway resource
- Mitigation: Request EIP limit increase via AWS Service Quotas
- Rollback: CloudFormation automatically deletes created resources

**ALB Creation Failure**:
- Cause: Insufficient subnets (requires 2 AZs), security group misconfiguration
- Detection: CloudFormation CREATE_FAILED event for ApplicationLoadBalancer resource
- Mitigation: Verify both public subnets exist in different AZs, check security group rules
- Rollback: CloudFormation automatically deletes created resources

**Dependency Ordering Issues**:
- Cause: Missing or incorrect DependsOn attributes
- Detection: Resources created in wrong order, EC2 instance launches before routing configured
- Mitigation: Add explicit DependsOn attributes per Property 6
- Impact: EC2 instance may fail to download dependencies if NAT Gateway not ready

### Bootstrap Process Failures

**SSM Document Execution Timeout**:
- Cause: Network connectivity issues, slow package downloads
- Detection: SSM Association status shows "Failed" or "TimedOut"
- Mitigation: Increase timeoutSeconds in SSM document steps, verify NAT Gateway routing
- Recovery: Re-run SSM Association or manually execute commands via Session Manager

**Package Installation Failures**:
- Cause: Repository unavailable, network issues, disk space
- Detection: SSM command output shows apt/npm/pip errors
- Mitigation: Verify NAT Gateway provides internet access, check disk space (50GB default)
- Recovery: SSH via Session Manager and manually install failed packages

**Code-Server Configuration Errors**:
- Cause: Incorrect file permissions, missing directories
- Detection: nginx fails to start, code-server service fails
- Mitigation: Ensure chown commands run correctly, verify directory creation
- Recovery: Fix permissions via Session Manager, restart services

### Runtime Errors

**Health Check Failures**:
- Cause: code-server not running, nginx misconfigured, EC2 instance unhealthy
- Detection: ALB Target Group shows "unhealthy" status
- Mitigation: Check code-server service status, verify nginx configuration, review EC2 system logs
- Impact: CloudFront returns 502/503 errors to users

**CloudFront 502/503 Errors**:
- Cause: ALB unhealthy, security group blocking traffic, origin timeout
- Detection: User reports access failures, CloudFront logs show origin errors
- Mitigation: Verify ALB target health, check security group rules, verify ALB listener configuration
- Recovery: Fix underlying issue (restart services, update security groups), CloudFront automatically retries

**NAT Gateway Connectivity Loss**:
- Cause: NAT Gateway failure (rare), EIP disassociation
- Detection: EC2 instance cannot reach internet, package updates fail
- Mitigation: Verify NAT Gateway status, check route table configuration
- Recovery: CloudFormation stack update to recreate NAT Gateway if necessary

### Security Errors

**CloudFront Prefix List Mismatch**:
- Cause: Incorrect prefix list ID for region, AWS updates prefix list
- Detection: ALB rejects CloudFront traffic, 403 errors
- Mitigation: Verify prefix list ID in AWSRegions2PrefixListID mapping matches region
- Recovery: Update security group with correct prefix list ID

**Security Group Circular Dependency**:
- Cause: ALBSecurityGroup egress references EC2SecurityGroup before it exists
- Detection: CloudFormation CREATE_FAILED with circular dependency error
- Mitigation: Use separate SecurityGroupEgress resource with DependsOn
- Prevention: Current design avoids this by creating EC2SecurityGroup first

**Missing IAM Permissions**:
- Cause: VSCodeInstanceRole lacks required permissions for SSM, AWS services
- Detection: SSM commands fail, AWS CLI commands fail in code-server
- Mitigation: Verify AdministratorAccess policy attached (current design)
- Recovery: Update IAM role with required permissions

### Validation Errors

**Template Syntax Errors**:
- Detection: CloudFormation validation fails during stack creation
- Mitigation: Use `aws cloudformation validate-template` before deployment
- Prevention: Use CloudFormation linter (cfn-lint) in CI/CD pipeline

**Resource Limit Exceeded**:
- Cause: AWS service quotas (EIPs, VPCs, security groups)
- Detection: CloudFormation CREATE_FAILED with quota error
- Mitigation: Request quota increase via AWS Service Quotas
- Prevention: Check quotas before deployment

**Parameter Validation Failures**:
- Cause: Invalid parameter values (instance type, AMI ID)
- Detection: CloudFormation validation error
- Mitigation: Verify parameter values against AllowedValues constraints
- Prevention: Use parameter validation in CloudFormation template

## Testing Strategy

### Static Template Validation

**CloudFormation Linting**:
- Tool: cfn-lint (CloudFormation Linter)
- Purpose: Validate template syntax, resource properties, best practices
- Execution: `cfn-lint code-server/code-server.yaml`
- Coverage: All CloudFormation resources and properties
- Validates: Template structure, resource types, property names, required properties

**Security Analysis**:
- Tool: cfn_nag
- Purpose: Identify security vulnerabilities and compliance issues
- Execution: `cfn_nag_scan --input-path code-server/code-server.yaml`
- Coverage: Security groups, IAM roles, encryption settings
- Validates: Security best practices, least privilege, encryption at rest

**Template Validation**:
- Tool: AWS CLI
- Purpose: Validate template against AWS CloudFormation service
- Execution: `aws cloudformation validate-template --template-body file://code-server/code-server.yaml`
- Coverage: Template syntax, resource references
- Validates: Template is parseable and deployable

### Unit Testing (Configuration Verification)

Unit tests verify specific template configurations match requirements. These are implemented as scripts that parse the YAML template and assert on specific values.

**Test Framework**: Python with PyYAML and pytest

**Test Cases**:

1. **test_private_subnet_configuration**: Validates Property 1
   - Assert PrivateSubnetOne.MapPublicIpOnLaunch == false
   - Assert PrivateSubnetTwo.MapPublicIpOnLaunch == false
   - Assert VSCodeInstanceEC2Instance.SubnetId references PrivateSubnetOne
   - Assert VSCodeInstanceEC2Instance has no AssociatePublicIpAddress property

2. **test_nat_gateway_resources**: Validates Property 2
   - Assert NATGatewayEIP resource exists with Domain: vpc
   - Assert NATGateway resource exists with SubnetId: PublicSubnetOne
   - Assert NATGateway.AllocationId references NATGatewayEIP
   - Assert PrivateRouteTable resource exists
   - Assert PrivateRoute has DestinationCidrBlock: 0.0.0.0/0 and NatGatewayId
   - Assert PrivateSubnetOneRouteTableAssociation exists
   - Assert PrivateSubnetTwoRouteTableAssociation exists

3. **test_alb_configuration**: Validates Property 3
   - Assert ApplicationLoadBalancer resource exists
   - Assert ALB.Subnets includes PublicSubnetOne and PublicSubnetTwo
   - Assert ALBTargetGroup.Port == 80 and Protocol == HTTP
   - Assert ALBTargetGroup.Targets includes VSCodeInstanceEC2Instance
   - Assert ALBTargetGroup.HealthCheckEnabled == true
   - Assert ALBListener.Port == 80 and Protocol == HTTP

4. **test_security_group_rules**: Validates Property 4
   - Assert ALBSecurityGroup ingress allows TCP 80 from CloudFront prefix list
   - Assert ALBSecurityGroup egress allows TCP 80 to EC2SecurityGroup
   - Assert EC2SecurityGroup ingress allows TCP 80 from ALBSecurityGroup
   - Assert EC2SecurityGroup ingress allows TCP 8501-8600 from 0.0.0.0/0
   - Assert EC2SecurityGroup egress allows all traffic

5. **test_cloudfront_origin**: Validates Property 5
   - Assert CloudFrontDistribution.Origins[0].DomainName references ALB.DNSName
   - Assert Origins[0].CustomOriginConfig.OriginProtocolPolicy == "http-only"

6. **test_resource_dependencies**: Validates Property 6
   - Assert NATGateway.DependsOn includes NATGatewayEIP
   - Assert PrivateRoute.DependsOn includes NATGateway
   - Assert VSCodeInstanceEC2Instance.DependsOn includes PrivateSubnetOneRouteTableAssociation
   - Assert CloudFrontDistribution.DependsOn includes ApplicationLoadBalancer

7. **test_bootstrap_cleanup**: Validates Property 7
   - Assert InstallPython step does not contain "git clone.*agentic-ai-with-mcp-and-strands"
   - Assert InstallPython step contains "mkdir -p /home/ubuntu/workshop"
   - Assert InstallPython2 step does not exist
   - Assert no step contains "pip install -r /home/ubuntu/workshop/requirements.txt"
   - Assert no step contains "pip install pyopenssl"
   - Assert no step contains "playwright install"
   - Assert no step contains "pip install streamlit"

8. **test_development_tools**: Validates Property 8
   - Assert InstallAWSCLI step exists
   - Assert InstallQCLI step exists
   - Assert InstallDocker step exists
   - Assert InstallGit step exists
   - Assert InstallNode step exists
   - Assert InstallPython step exists
   - Assert InstallJava step exists
   - Assert InstallCDK step exists

9. **test_code_server_config**: Validates Property 9
   - Assert ConfigureCodeServer creates config.yaml with hashed-password
   - Assert settings.json contains terminal.integrated.cwd: "/home/ubuntu/workshop/"
   - Assert nginx config routes / to localhost:8080
   - Assert nginx config routes /${DevServerBasePath} to localhost:${DevServerPort}
   - Assert extensions include amazon-q-vscode, auto-run-command, vscode-java-pack, live-server, jupyter, python, debugpy

10. **test_ssm_access**: Validates Property 10
    - Assert VSCodeInstanceEC2Instance.IamInstanceProfile references VSCodeInstanceProfile
    - Assert VSCodeInstanceProfile.Roles includes VSCodeInstanceRole
    - Assert VSCodeInstanceRole has AdministratorAccess managed policy

**Execution**: `pytest tests/test_template_config.py -v`

### Integration Testing (Deployment Verification)

Integration tests deploy the CloudFormation stack and verify runtime behavior.

**Test Environment**: Dedicated AWS account or isolated VPC

**Test Cases**:

1. **test_stack_creation_success**:
   - Deploy CloudFormation stack
   - Assert stack status reaches CREATE_COMPLETE within 15 minutes
   - Assert all resources created successfully
   - Cleanup: Delete stack after test

2. **test_ec2_private_ip_only**:
   - Deploy stack
   - Query EC2 instance details via AWS API
   - Assert instance has private IP address
   - Assert instance has no public IP address
   - Assert instance is in PrivateSubnetOne

3. **test_nat_gateway_connectivity**:
   - Deploy stack
   - Connect to EC2 instance via SSM Session Manager
   - Execute: `curl -I https://www.amazon.com`
   - Assert HTTP 200 response (internet connectivity via NAT)
   - Execute: `curl -I http://169.254.169.254/latest/meta-data/public-ipv4`
   - Assert 404 (no public IP)

4. **test_alb_health_checks**:
   - Deploy stack
   - Wait for SSM bootstrap to complete (code-server running)
   - Query ALB target group health via AWS API
   - Assert target status is "healthy"
   - Assert health check response code is 200

5. **test_cloudfront_to_alb_traffic**:
   - Deploy stack
   - Wait for CloudFront distribution to deploy
   - Execute: `curl -I https://<cloudfront-domain>/`
   - Assert HTTP 200 response
   - Assert response headers indicate code-server

6. **test_end_to_end_access**:
   - Deploy stack
   - Wait for bootstrap completion
   - Open CloudFront URL in browser
   - Enter password (AWS Account ID)
   - Assert code-server interface loads
   - Assert terminal opens in /home/ubuntu/workshop
   - Assert workshop directory is empty (no sample code)

7. **test_security_group_isolation**:
   - Deploy stack
   - Attempt direct HTTP connection to ALB from non-CloudFront IP
   - Assert connection refused or timeout (security group blocks)
   - Attempt direct connection to EC2 private IP
   - Assert connection fails (no route from internet)

8. **test_development_tools_installed**:
   - Deploy stack
   - Connect via SSM Session Manager
   - Execute: `aws --version`, `docker --version`, `git --version`, `node --version`, `python3 --version`, `java -version`, `cdk --version`, `q --version`
   - Assert all commands return version information

9. **test_workshop_directory_empty**:
   - Deploy stack
   - Connect via SSM Session Manager
   - Execute: `ls -la /home/ubuntu/workshop`
   - Assert directory exists and is empty (no sample code)

10. **test_stack_deletion_success**:
    - Deploy stack
    - Delete CloudFormation stack
    - Assert stack status reaches DELETE_COMPLETE within 10 minutes
    - Assert all resources deleted (no orphaned resources)

**Execution**: `pytest tests/test_integration.py -v --aws-region us-east-1`

### Manual Testing Checklist

After automated tests pass, perform manual verification:

- [ ] Deploy stack in target AWS account
- [ ] Access CloudFront URL in browser
- [ ] Log in with AWS Account ID password
- [ ] Verify code-server opens /home/ubuntu/workshop
- [ ] Verify workshop directory is empty
- [ ] Open terminal in code-server
- [ ] Run `aws sts get-caller-identity` (verify AWS CLI works)
- [ ] Run `docker ps` (verify Docker works)
- [ ] Run `git --version` (verify Git works)
- [ ] Run `node --version` (verify Node.js works)
- [ ] Run `python3 --version` (verify Python works)
- [ ] Run `java -version` (verify Java works)
- [ ] Run `cdk --version` (verify CDK works)
- [ ] Run `q --version` (verify Amazon Q CLI works)
- [ ] Verify Amazon Q extension appears in VS Code
- [ ] Create test file and verify auto-run-command opens terminal
- [ ] Test development server on port 8081 (access via CloudFront URL/app)
- [ ] Connect to EC2 via SSM Session Manager
- [ ] Verify EC2 has no public IP: `curl http://169.254.169.254/latest/meta-data/public-ipv4` (should fail)
- [ ] Verify internet access via NAT: `curl https://www.amazon.com` (should succeed)
- [ ] Delete stack and verify clean deletion

### Testing Summary

**Coverage**:
- Static validation: 100% of template structure
- Unit tests: All 10 correctness properties
- Integration tests: End-to-end deployment and runtime behavior
- Manual tests: User experience and edge cases

**Test Execution Order**:
1. Static validation (fast, catches syntax errors)
2. Unit tests (fast, validates configuration)
3. Integration tests (slow, validates deployment)
4. Manual tests (final verification before production)

**Continuous Integration**:
- Run static validation and unit tests on every commit
- Run integration tests on pull requests to main branch
- Require all tests to pass before merge

**Test Data**:
- Use dedicated AWS account for integration tests
- Clean up resources after each test run
- Use unique stack names to avoid conflicts

This testing strategy ensures comprehensive validation of the CloudFormation template changes while maintaining fast feedback loops for developers.
