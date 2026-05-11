# Requirements Document

## Introduction

This feature enhances the code-server CloudFormation deployment to meet AWS internal security requirements and provide a clean workshop environment. The deployment will move EC2 instances from public subnets to private subnets with private IPs only, add NAT Gateway infrastructure for internet access, and remove pre-existing Strands SDK workshop sample code to provide participants with a fresh starting environment.

## Glossary

- **Code_Server**: The VS Code server application running on EC2 instances
- **EC2_Instance**: The Amazon EC2 virtual machine hosting the Code_Server
- **NAT_Gateway**: AWS Network Address Translation gateway enabling private subnet instances to access the internet
- **Private_Subnet**: VPC subnet without direct internet gateway route, using NAT Gateway for outbound traffic
- **Public_Subnet**: VPC subnet with direct internet gateway route for public internet access
- **Application_Load_Balancer**: AWS Elastic Load Balancer distributing traffic to EC2_Instance
- **Target_Group**: ALB target group containing EC2_Instance
- **ALB_Security_Group**: Security group controlling traffic to the Application_Load_Balancer
- **CloudFront_Distribution**: AWS CloudFront CDN distribution serving as the public endpoint
- **Security_Group**: AWS firewall rules controlling network traffic to EC2_Instance
- **Route_Table**: VPC routing configuration directing network traffic
- **Bootstrap_Process**: EC2 instance initialization via SSM document
- **Workshop_Directory**: The /home/ubuntu/workshop directory on EC2_Instance
- **Strands_SDK_Code**: Sample code from the agentic-ai-with-mcp-and-strands GitHub repository

## Requirements

### Requirement 1: Private Subnet Deployment

**User Story:** As a security administrator, I want EC2 instances deployed in private subnets with private IPs only, so that instances comply with AWS internal security policies.

#### Acceptance Criteria

1. THE EC2_Instance SHALL be deployed in a private subnet
2. THE EC2_Instance SHALL NOT have a public IP address assigned
3. THE EC2_Instance SHALL NOT have MapPublicIpOnLaunch enabled on its subnet
4. WHEN the CloudFormation stack is created, THE EC2_Instance SHALL use PrivateSubnetOne as its subnet

### Requirement 2: NAT Gateway Infrastructure

**User Story:** As a developer, I want NAT Gateway infrastructure provisioned, so that EC2 instances in private subnets can download dependencies from the internet.

#### Acceptance Criteria

1. THE CloudFormation_Template SHALL create a NAT Gateway resource in PublicSubnetOne
2. THE NAT_Gateway SHALL have an Elastic IP address allocated
3. THE CloudFormation_Template SHALL create a route table for private subnets
4. THE Private_Subnet_Route_Table SHALL include a default route (0.0.0.0/0) pointing to the NAT_Gateway
5. THE PrivateSubnetOne SHALL be associated with the Private_Subnet_Route_Table
6. THE PrivateSubnetTwo SHALL be associated with the Private_Subnet_Route_Table

### Requirement 3: Application Load Balancer

**User Story:** As a security administrator, I want an Application Load Balancer in public subnets fronting the private EC2 instance, so that CloudFront has a stable, highly available origin endpoint.

#### Acceptance Criteria

1. THE Application_Load_Balancer SHALL be deployed in PublicSubnetOne and PublicSubnetTwo
2. THE Application_Load_Balancer SHALL have a Target_Group configured to forward traffic to port 80 on the EC2_Instance
3. THE Target_Group SHALL have health checks configured to monitor EC2_Instance availability
4. THE Application_Load_Balancer SHALL have a listener on port 80 that forwards traffic to the Target_Group
5. THE ALB_Security_Group SHALL allow HTTP (port 80) ingress from the CloudFront prefix list
6. THE ALB_Security_Group SHALL allow outbound traffic to the EC2_Instance security group on port 80
7. THE EC2_Instance SHALL be registered as a target in the Target_Group

### Requirement 4: CloudFront Origin Configuration

**User Story:** As a workshop participant, I want to access the code-server through CloudFront, so that I can use the development environment securely.

#### Acceptance Criteria

1. THE CloudFront_Distribution SHALL use the Application_Load_Balancer DNS name as the origin domain
2. THE CloudFront_Distribution SHALL use HTTP protocol to communicate with the Application_Load_Balancer origin
3. WHEN a request is received, THE CloudFront_Distribution SHALL forward traffic to the Application_Load_Balancer
4. WHEN the Application_Load_Balancer receives traffic from CloudFront, THE Application_Load_Balancer SHALL forward it to the EC2_Instance

### Requirement 5: Network Security

**User Story:** As a security administrator, I want network access properly restricted, so that only authorized traffic reaches the EC2 instance.

#### Acceptance Criteria

1. THE ALB_Security_Group SHALL allow HTTP (port 80) ingress from the CloudFront prefix list
2. THE EC2_Instance Security_Group SHALL allow HTTP (port 80) ingress from the ALB_Security_Group
3. THE EC2_Instance Security_Group SHALL allow TCP ports 8501-8600 ingress from all IPs (for development server access)
4. THE EC2_Instance Security_Group SHALL allow all outbound traffic
5. THE EC2_Instance SHALL NOT be directly accessible from the public internet
6. WHEN traffic originates from CloudFront, THE ALB_Security_Group SHALL permit the connection to the Application_Load_Balancer

### Requirement 6: Infrastructure Dependencies

**User Story:** As a DevOps engineer, I want proper resource dependencies configured, so that the CloudFormation stack deploys reliably.

#### Acceptance Criteria

1. THE NAT_Gateway SHALL depend on the Elastic IP allocation
2. THE Private_Subnet_Route_Table SHALL depend on the NAT_Gateway creation
3. THE Application_Load_Balancer SHALL depend on the PublicSubnetOne and PublicSubnetTwo creation
4. THE Application_Load_Balancer SHALL depend on the ALB_Security_Group creation
5. THE Target_Group SHALL depend on the VPC creation
6. THE CloudFront_Distribution SHALL depend on the Application_Load_Balancer creation
7. THE EC2_Instance SHALL depend on the Private_Subnet_Route_Table association
8. WHEN the CloudFormation stack is deleted, THE resources SHALL be deleted in reverse dependency order
9. THE CloudFormation_Template SHALL use DependsOn attributes to enforce proper creation order

### Requirement 7: Remove Strands SDK Sample Code

**User Story:** As a workshop facilitator, I want the Strands SDK sample code removed from the bootstrap process, so that participants start with a clean environment.

#### Acceptance Criteria

1. THE Bootstrap_Process SHALL NOT clone the agentic-ai-with-mcp-and-strands GitHub repository
2. THE Bootstrap_Process SHALL create an empty Workshop_Directory
3. THE Bootstrap_Process SHALL NOT install Python dependencies from a requirements.txt file in the Workshop_Directory
4. THE Bootstrap_Process SHALL NOT execute pip install commands for workshop-specific packages (pyopenssl, playwright, streamlit)
5. THE Bootstrap_Process SHALL retain all other development tool installations (AWS CLI, Docker, Git, Node, Python, Java, CDK, Amazon Q CLI)

### Requirement 8: Maintain Existing Functionality

**User Story:** As a workshop participant, I want all existing code-server functionality preserved, so that I can use the development environment as intended.

#### Acceptance Criteria

1. THE Code_Server SHALL remain accessible through the CloudFront_Distribution URL
2. THE Code_Server SHALL use the AWS account ID as the password
3. THE Code_Server SHALL open the Workshop_Directory by default
4. THE Code_Server SHALL have all VS Code extensions installed (Amazon Q, auto-run-command, Java pack, live-server, Jupyter, Python, debugpy)
5. THE EC2_Instance SHALL have SSM Session Manager access enabled
6. THE nginx reverse proxy SHALL route traffic to code-server on port 8080 and the dev server on the configured port
