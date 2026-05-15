# Code Server Deployment Design

## Overview

This design implements a reliable, cloud-based VS Code development environment using AWS infrastructure. The system provides browser-based access to a fully functional VS Code instance through CloudFront distribution, with automated deployment via CloudFormation and robust error handling for common failure scenarios.

## Architecture

### High-Level Architecture

```
Internet → CloudFront → EC2 Instance (nginx → code-server)
                            ↓
                       SSM Bootstrap Process
                            ↓
                       S3 Logging & Monitoring
```

### Component Flow
1. **User Access**: Users access via CloudFront HTTPS URL
2. **Content Delivery**: CloudFront routes to EC2 instance origin
3. **Reverse Proxy**: nginx proxies requests to code-server on port 8080
4. **Development Environment**: code-server provides VS Code in browser
5. **Bootstrap**: SSM automates software installation and configuration
6. **Monitoring**: All bootstrap logs stored in S3 for debugging

## Components and Interfaces

### CloudFront Distribution
- **Purpose**: Global content delivery and HTTPS termination
- **Configuration**: Custom cache policy for interactive applications
- **Security**: Restricts origin access to CloudFront IP ranges only

### EC2 Instance
- **Type**: ARM64 instances (c7g family) for cost efficiency
- **OS**: Ubuntu 22.04 LTS with automated patching
- **Storage**: Encrypted EBS volumes with configurable size
- **Networking**: Public subnet with internet gateway access

### Security Groups
- **Inbound Rules**:
  - HTTP (80) from CloudFront prefix lists only
  - SSH (22) conditionally based on AllowSSHAccess parameter
  - Development ports (8501-8600) for application testing
- **Outbound Rules**: All traffic allowed for software downloads

### SSM Bootstrap System
- **Document**: Custom SSM document with modular installation steps
- **Association**: Instance ID targeting for reliability (more reliable than tag-based)
- **Logging**: All output captured to S3 bucket
- **Installation Strategy**: Conservative approach using original methods (NodeSource repos, standard package managers)
- **Error Handling**: Fail-fast approach with detailed error reporting
- **Error Handling**: Fail-fast approach with detailed error reporting

### Code-Server Configuration
- **Authentication**: Password-based using AWS Account ID
- **Workspace**: Default to workshop directory
- **Extensions**: Pre-installed development extensions
- **Settings**: Optimized for cloud development workflow

## Data Models

### CloudFormation Parameters
```yaml
Parameters:
  InstanceType: String (ARM64 instance types)
  InstanceVolumeSize: Number (EBS volume size in GB)
  EC2KeyPair: KeyPair name for SSH access
  AllowSSHAccess: Boolean for debugging access
  HomeFolder: String (default workspace path)
  DevServerPort: Number (application development port)
```

### SSM Document Structure
```yaml
mainSteps:
  - UpdateSystem: Base system packages
  - InstallNodeJS: Official binary distribution
  - InstallAWSCLI: Latest AWS CLI v2
  - InstallCDK: AWS CDK for infrastructure development
  - InstallDocker: Container runtime
  - InstallPython: Python 3.12 with development tools
  - SetupWorkshop: Clone and configure workspace
  - InstallCodeServer: VS Code server installation
  - ConfigureCodeServer: Authentication and settings
  - InstallNginx: Reverse proxy setup
  - ConfigureNginx: Proxy configuration
  - FinalSetup: Service verification and startup
```

### Configuration Files
- **Code-Server Config**: `/home/ubuntu/.config/code-server/config.yaml`
- **Nginx Config**: `/etc/nginx/sites-available/code-server`
- **VS Code Settings**: `/home/ubuntu/.local/share/code-server/User/settings.json`

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Bootstrap Completion Verification
*For any* EC2 instance launched with the bootstrap association, all critical services (nginx, code-server) should be running and accessible within the timeout period
**Validates: Requirements 2.2, 3.1**

### Property 2: Service Auto-Recovery
*For any* service failure scenario, the system should automatically restart failed services and restore functionality without manual intervention
**Validates: Requirements 3.4, 2.4**

### Property 3: Security Group Isolation
*For any* HTTP request not originating from CloudFront IP ranges, the security group should reject the connection
**Validates: Requirements 4.3, 2.5**

### Property 4: Authentication Enforcement
*For any* unauthenticated request to code-server, the system should redirect to login page and deny access to VS Code functionality
**Validates: Requirements 4.1**

### Property 5: Configuration Validation
*For any* nginx configuration change, the system should validate syntax before applying and reject invalid configurations
**Validates: Requirements 3.3**

### Property 6: Bootstrap Logging Completeness
*For any* bootstrap execution, all installation steps and their outcomes should be logged to S3 with sufficient detail for debugging
**Validates: Requirements 5.2, 5.4**

### Property 7: Node.js Installation Resilience
*For any* Node.js installation failure using primary method, the system should automatically attempt alternative installation methods
**Validates: Requirements 3.2**

### Property 8: Session State Persistence
*For any* established code-server session, browser refresh should maintain workspace state and open files
**Validates: Requirements 1.4**

## Error Handling

### Bootstrap Failure Recovery
- **Detection**: Each installation step includes error checking with `set -e`
- **Logging**: Detailed error messages captured to CloudWatch and S3
- **Access**: SSH access automatically enabled for manual intervention
- **Retry**: Manual SSM document execution available through console

### Service Failure Recovery
- **Monitoring**: systemd service monitoring with automatic restart
- **Health Checks**: Service status verification in bootstrap final step
- **Fallback**: Direct IP access option for bypassing CloudFront issues

### Network Connectivity Issues
- **Timeout Handling**: Appropriate timeouts for each installation step
- **Retry Logic**: Built-in retry for transient network failures
- **Alternative Sources**: Multiple download sources for critical components

## Testing Strategy

### Unit Testing
- CloudFormation template validation using cfn-lint
- SSM document syntax validation
- Configuration file template validation
- Security group rule verification

### Property-Based Testing
The system will use **AWS CloudFormation Guard** for policy-as-code testing with a minimum of 100 test iterations per property. Each property-based test will be tagged with comments explicitly referencing the correctness property in this design document.

**Property Test Requirements:**
- Each correctness property must be implemented by a single property-based test
- Tests must run against actual AWS resources in isolated environments
- Test data generators should create realistic infrastructure configurations
- All tests must be tagged with format: **Feature: code-server-deployment, Property {number}: {property_text}**

### Integration Testing
- End-to-end deployment testing in clean AWS accounts
- Multi-region deployment verification
- Bootstrap failure simulation and recovery testing
- Performance testing for bootstrap completion times

### Manual Testing Scenarios
- CloudFront access from multiple geographic locations
- SSH debugging access when bootstrap fails
- Service recovery after simulated failures
- Direct IP access for troubleshooting scenarios