# Implementation Plan: Code Server Private IP Deployment

## Overview

This implementation transforms the code-server CloudFormation template from a public-facing EC2 architecture to a secure, private subnet deployment. The work involves adding 10 new CloudFormation resources (NAT Gateway, ALB, security groups, route tables), modifying 6 existing resources (subnets, EC2, CloudFront, SSM document), and cleaning up the bootstrap process to remove pre-existing workshop code.

## Tasks

- [x] 1. Create NAT Gateway infrastructure for private subnet internet access
  - [x] 1.1 Add NATGatewayEIP resource with Domain: vpc
    - Create Elastic IP allocation for NAT Gateway
    - _Requirements: 2.2_
  
  - [x] 1.2 Add NATGateway resource in PublicSubnetOne
    - Reference NATGatewayEIP via AllocationId
    - Add DependsOn: NATGatewayEIP
    - _Requirements: 2.1, 6.1_
  
  - [x] 1.3 Add PrivateRouteTable resource
    - Create route table for private subnets
    - _Requirements: 2.3_
  
  - [x] 1.4 Add PrivateRoute resource with default route to NAT Gateway
    - Set DestinationCidrBlock: 0.0.0.0/0
    - Reference NATGateway via NatGatewayId
    - Add DependsOn: NATGateway
    - _Requirements: 2.4, 6.2_
  
  - [x] 1.5 Add PrivateSubnetOneRouteTableAssociation resource
    - Associate PrivateSubnetOne with PrivateRouteTable
    - _Requirements: 2.5_
  
  - [x] 1.6 Add PrivateSubnetTwoRouteTableAssociation resource
    - Associate PrivateSubnetTwo with PrivateRouteTable
    - _Requirements: 2.6_

- [x] 2. Create Application Load Balancer infrastructure
  - [x] 2.1 Add ALBSecurityGroup resource
    - Add ingress rule: TCP port 80 from CloudFront prefix list
    - Add egress rule: TCP port 80 to EC2SecurityGroup
    - _Requirements: 3.5, 3.6, 5.1, 5.6_
  
  - [x] 2.2 Add ApplicationLoadBalancer resource
    - Set Type: application, Scheme: internet-facing
    - Set Subnets: [PublicSubnetOne, PublicSubnetTwo]
    - Reference ALBSecurityGroup
    - _Requirements: 3.1, 6.3, 6.4_
  
  - [x] 2.3 Add ALBTargetGroup resource
    - Set Port: 80, Protocol: HTTP, TargetType: instance
    - Configure health checks (Path: /, IntervalSeconds: 30, TimeoutSeconds: 5, HealthyThresholdCount: 2, UnhealthyThresholdCount: 2)
    - Add VSCodeInstanceEC2Instance as target on Port: 80
    - _Requirements: 3.2, 3.3, 3.7, 6.5_
  
  - [x] 2.4 Add ALBListener resource
    - Set Port: 80, Protocol: HTTP
    - Configure DefaultActions to forward to ALBTargetGroup
    - _Requirements: 3.4_

- [x] 3. Modify existing resources for private subnet deployment
  - [x] 3.1 Remove MapPublicIpOnLaunch from PrivateSubnetOne
    - Delete MapPublicIpOnLaunch: true property
    - _Requirements: 1.3_
  
  - [x] 3.2 Remove MapPublicIpOnLaunch from PrivateSubnetTwo
    - Delete MapPublicIpOnLaunch: true property
    - _Requirements: 1.3_
  
  - [x] 3.3 Rename SecurityGroup resource to EC2SecurityGroup
    - Update all references throughout template
    - _Requirements: 5.2_
  
  - [x] 3.4 Modify EC2SecurityGroup ingress rules
    - Change HTTP port 80 ingress from CloudFront prefix list to ALBSecurityGroup
    - Keep TCP ports 8501-8600 ingress from 0.0.0.0/0
    - _Requirements: 5.2, 5.3_
  
  - [x] 3.5 Modify VSCodeInstanceEC2Instance subnet and dependencies
    - Change SubnetId from PublicSubnetOne to PrivateSubnetOne
    - Add DependsOn: PrivateSubnetOneRouteTableAssociation
    - _Requirements: 1.1, 1.4, 6.7_
  
  - [x] 3.6 Modify CloudFrontDistribution origin configuration
    - Change Origins[0].DomainName from EC2 PublicDnsName to ALB DNSName
    - Add DependsOn: ApplicationLoadBalancer
    - _Requirements: 4.1, 4.2, 6.6_

- [x] 4. Checkpoint - Validate template structure
  - Run cfn-lint to check template syntax
  - Run aws cloudformation validate-template
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Clean up bootstrap process to remove workshop sample code
  - [x] 5.1 Modify InstallPython step in VSCodeInstanceSSMDoc
    - Remove git clone command for agentic-ai-with-mcp-and-strands repository
    - Add mkdir -p /home/ubuntu/workshop command
    - Add chown ubuntu:ubuntu /home/ubuntu/workshop command
    - _Requirements: 7.1, 7.2_
  
  - [x] 5.2 Remove InstallPython2 step from VSCodeInstanceSSMDoc
    - Delete entire InstallPython2 action block
    - This removes pip install commands for requirements.txt, pyopenssl, playwright, streamlit
    - _Requirements: 7.3, 7.4_

- [ ]* 6. Create unit tests for template configuration validation
  - [ ]* 6.1 Write test_private_subnet_configuration
    - **Property 1: Private Subnet Isolation**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 5.5**
  
  - [ ]* 6.2 Write test_nat_gateway_resources
    - **Property 2: NAT Gateway Configuration Completeness**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**
  
  - [ ]* 6.3 Write test_alb_configuration
    - **Property 3: Application Load Balancer Configuration Completeness**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.7**
  
  - [ ]* 6.4 Write test_security_group_rules
    - **Property 4: Security Group Chain Configuration**
    - **Validates: Requirements 3.5, 3.6, 5.1, 5.2, 5.3, 5.4, 5.6**
  
  - [ ]* 6.5 Write test_cloudfront_origin
    - **Property 5: CloudFront Origin Configuration**
    - **Validates: Requirements 4.1, 4.2**
  
  - [ ]* 6.6 Write test_resource_dependencies
    - **Property 6: Resource Dependency Chain**
    - **Validates: Requirements 6.1, 6.2, 6.6, 6.7, 6.9**
  
  - [ ]* 6.7 Write test_bootstrap_cleanup
    - **Property 7: Bootstrap Process Cleanup**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4**
  
  - [ ]* 6.8 Write test_development_tools
    - **Property 8: Development Tool Preservation**
    - **Validates: Requirements 7.5**
  
  - [ ]* 6.9 Write test_code_server_config
    - **Property 9: Code Server Configuration Preservation**
    - **Validates: Requirements 8.2, 8.3, 8.4, 8.6**
  
  - [ ]* 6.10 Write test_ssm_access
    - **Property 10: SSM Access Preservation**
    - **Validates: Requirements 8.5**

- [x] 7. Final checkpoint - Ensure all tests pass
  - Run cfn-lint and cfn_nag for security analysis
  - Run unit tests: pytest tests/test_template_config.py -v
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Unit tests validate all 10 correctness properties from the design document
- Integration testing (actual stack deployment) should be performed manually after implementation
- The CloudFormation template uses YAML format with AWS intrinsic functions (!Ref, !GetAtt, !Sub)
- All security group references must be updated when renaming SecurityGroup to EC2SecurityGroup
