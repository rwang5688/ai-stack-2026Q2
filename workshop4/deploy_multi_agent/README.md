# Multi-Agent Bedrock System - Production Deployment

This directory contains the production deployment infrastructure for the multi-agent system using Strands Agents SDK with Amazon Bedrock model hosting. It deploys a Streamlit web application with authentication, containerized using Docker and deployed on AWS ECS Fargate.

## Architecture

The deployment creates a production-ready multi-agent system with the following components:

* **Streamlit Multi-Agent App** in ECS/Fargate with Teacher's Assistant pattern and Bedrock Knowledge Base integration
* **Application Load Balancer (ALB)** for traffic distribution and health checks
* **CloudFront Distribution** for global content delivery and caching
* **Amazon Cognito User Pool** for user authentication and session management
* **Amazon Bedrock Integration** with comprehensive IAM permissions for Nova Pro model and Knowledge Base access
* **VPC and Security Groups** with proper network isolation and security controls

![Architecture diagram](img/archi_streamlit_cdk.png)

## Features

The deployed application includes all multi-agent capabilities:

* **Authentication** through Amazon Cognito with streamlit-cognito-auth integration
* **Multi-Agent System** with Teacher's Assistant orchestrator and 5 specialized agents
* **Amazon Bedrock Integration** using Nova Pro model (`us.amazon.nova-pro-v1:0`)
* **Knowledge Base Functionality** for personal information storage and retrieval
* **Agent Type Selection** (Auto-Route, Teacher Agent, Knowledge Base)
* **Cross-Platform Tool Support** with automatic capability detection
* **Conversation History** and session management
* **Enhanced UI Features** with model information display and agent selection 

## Architecture diagram

![Architecture diagram](img/archi_streamlit_cdk.png)

## Usage

In the docker_app folder, you will find the streamlit app. You can run it locally or with docker.

Note: for the docker version to run, you will need to give appropriate permissions to the container for bedrock access. This is not implemented yet.

In the main folder, you will find a cdk template to deploy the app on ECS / ALB.

## Prerequisites

* **Python** >= 3.12 (required for Strands Agents SDK)
* **Docker** for containerization
* **Chrome browser** for development and testing
* **Amazon Bedrock Access** with Nova Pro model (`us.amazon.nova-pro-v1:0`) activated in your AWS account
* **AWS CLI** and **AWS CDK** installed and configured
* **Strands Knowledge Base** (optional - will use demo KB if not configured)
* **Development Environment**: Tested on AWS Cloud9 m5.large with Amazon Linux 2023, macOS with Docker Desktop, and Windows with Docker Desktop

### AWS Permissions Required

The deployment requires comprehensive AWS permissions for:
- **Amazon Bedrock**: Model invocation, Knowledge Base operations, document ingestion
- **Amazon S3**: Knowledge Base storage bucket access
- **Amazon OpenSearch Serverless**: Knowledge Base indexing (if using custom KB)
- **ECS/Fargate**: Container deployment and management
- **CloudFront**: Content delivery network
- **Cognito**: User authentication
- **VPC/Networking**: Security groups and load balancers

**Note**: The CDK stack includes comprehensive IAM permissions (lines 136-194 in `cdk/cdk_stack.py`) that are intentionally broad for workshop reliability.

## Deployment Steps

### 1. Configure Application Settings

Edit `docker_app/config_file.py` and configure:
- `STACK_NAME`: Choose a unique stack name for your deployment
- `CUSTOM_HEADER_VALUE`: Set a custom header value for security
- `STRANDS_KNOWLEDGE_BASE_ID`: Set your Knowledge Base ID (optional - defaults to demo KB)

### 2. Prepare Local Application

Before deployment, ensure your local multi-agent application is working:

```bash
# Navigate to the local implementation
cd ../multi_agent_bedrock

# Test the application locally
streamlit run app.py
```

### 3. Merge Application Code

The deployment uses a template-based approach where you merge your local application with the authentication framework:

```bash
# Use the merge helper script
python merge_app.py

# Or manually follow the APP_MERGE_GUIDE.md instructions
```

**Key Integration Points:**
- Keep the **AUTHENTICATION SECTION** at the top of `docker_app/app.py`
- Replace the **APPLICATION LOGIC SECTION** with your multi-agent code
- Ensure authentication UI remains in the sidebar
- Test that both authentication and multi-agent features work together

### 4. Install Dependencies and Deploy

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy the infrastructure
cdk deploy
```

**Deployment time**: 5-10 minutes

### 5. Configure Users and Access

1. **Note the deployment outputs**:
   - CloudFront distribution URL
   - Cognito User Pool ID

2. **Create users** in the Cognito User Pool via AWS Console

3. **Access the application**:
   - Navigate to the CloudFront distribution URL
   - Log in with your Cognito user credentials
   - Test all multi-agent features (Teacher Agent, Knowledge Base, Auto-Route)

## Local Development and Testing

### Testing in AWS Cloud9

After deploying the CDK template with Cognito authentication, you can test the multi-agent application directly in Cloud9:

1. **Deactivate deployment virtual environment** (if active):
```bash
deactivate
```

2. **Set up local development environment**:
```bash
cd docker_app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. **Configure environment variables**:
```bash
export AWS_REGION="us-east-1"
export BYPASS_TOOL_CONSENT="true"
export STRANDS_KNOWLEDGE_BASE_ID="your-kb-id"  # Optional
```

4. **Launch the Streamlit application**:
```bash
streamlit run app.py --server.port 8080
```

5. **Access the application**:
   - Click **Preview > Preview Running Application** in Cloud9
   - Click **Pop Out** to open in a new browser window
   - Configure browser to accept cross-site tracking cookies if needed

### Local Docker Testing

To test the containerized version locally:

```bash
# Build the Docker image
docker build -t multi-agent-bedrock .

# Run with environment variables
docker run -p 8501:8501 \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  -e STRANDS_KNOWLEDGE_BASE_ID=your-kb-id \
  multi-agent-bedrock
```

**Note**: Ensure the container has appropriate AWS permissions for Bedrock access.

## Application Features

The deployed multi-agent system includes:

### Core Multi-Agent Functionality
- **Teacher's Assistant Pattern**: Central orchestrator routing queries to 5 specialized agents
- **Specialized Agents**: Math, English, Language, Computer Science, and General assistants
- **Tool Integration**: Calculator, Python REPL, shell, HTTP requests, file operations
- **Cross-Platform Support**: Automatic tool detection and fallbacks

### Knowledge Base Integration
- **Personal Information Storage**: Store and retrieve personal facts and preferences
- **Bedrock Knowledge Base**: AWS-managed document storage with vector search
- **Intelligent Routing**: Auto-detection between educational and knowledge queries
- **Normal Indexing Behavior**: 2-3 minute delay for new data to become searchable

### Enhanced UI Features
- **Agent Type Selection**: Choose between Auto-Route, Teacher Agent, or Knowledge Base
- **Conversation History**: Persistent chat history during session
- **Service Information**: Display of Bedrock model and configuration details
- **Error Handling**: Comprehensive error management and user feedback

### Authentication and Security
- **Cognito Integration**: Secure user authentication and session management
- **User Management**: Admin control over user access and permissions
- **Session Security**: Proper session handling and logout functionality

## Monitoring and Maintenance

### CloudWatch Integration
- **Application Logs**: ECS task logs available in CloudWatch
- **Performance Metrics**: Container CPU, memory, and network usage
- **Custom Metrics**: Multi-agent interaction patterns and response times

### Cost Optimization
- **Bedrock Usage**: Monitor token consumption and model invocation costs
- **ECS Scaling**: Configure auto-scaling based on demand
- **CloudFront Caching**: Optimize static asset delivery

### Maintenance Tasks
- **User Management**: Regular review of Cognito user pool
- **Security Updates**: Keep container images and dependencies updated
- **Knowledge Base**: Monitor document storage and indexing performance

## Security Considerations and Limitations

### Network Security
* **HTTP between CloudFront and ALB**: Traffic between CloudFront and the ALB is unencrypted
* **Recommendation**: Configure HTTPS by bringing your own domain name and SSL/TLS certificate
* **Production Requirement**: Implement proper SSL/TLS termination for production workloads

### Application Security
* **Demo Code**: This implementation is intended as a workshop demo and starting point, not production-ready
* **Third-Party Dependencies**: Thoroughly vet Streamlit, streamlit-cognito-auth, and Strands Agents SDK
* **Authentication Review**: Evaluate authentication and authorization mechanisms for production use
* **Security Testing**: Perform comprehensive security reviews before production deployment

### Cognito Configuration
* **Basic Setup**: Current Cognito configuration is simplified for workshop purposes
* **Production Enhancements**: 
  - Enforce strong password policies
  - Enable multi-factor authentication (MFA)
  - Set AdvancedSecurityMode to ENFORCED for malicious sign-in detection
  - Configure proper user pool policies and attributes

### AWS Security Services (Not Implemented)
* **Network Security**: Consider AWS WAF, network ACLs, and VPC security groups
* **DDoS Protection**: Implement AWS Shield for DDoS protection
* **Threat Detection**: Use Amazon GuardDuty for threat detection
* **Security Assessment**: Leverage Amazon Inspector for security assessments
* **Monitoring**: Implement comprehensive logging and monitoring with CloudTrail

### IAM Permissions
* **Broad Permissions**: CDK stack includes comprehensive IAM permissions for workshop reliability
* **Production Refinement**: Review and minimize permissions following least privilege principle
* **Regular Rotation**: Implement regular rotation of secrets and access keys (not included in demo)

### Data Protection
* **Sensitive Data**: Avoid entering sensitive or PII data in workshop demonstrations
* **Knowledge Base**: Personal information stored in Bedrock Knowledge Base should be non-sensitive
* **Encryption**: Ensure data encryption at rest and in transit for production workloads

## Troubleshooting

### Common Deployment Issues

1. **CDK Bootstrap Required**:
   ```
   Error: Need to perform AWS CDK bootstrap
   ```
   **Solution**: Run `cdk bootstrap` before deployment

2. **Bedrock Model Access**:
   ```
   Error: Access denied to model us.amazon.nova-pro-v1:0
   ```
   **Solution**: Request access to Nova Pro model in Bedrock console

3. **Knowledge Base Configuration**:
   ```
   Error: Knowledge Base not found
   ```
   **Solution**: Set `STRANDS_KNOWLEDGE_BASE_ID` or use default demo KB

4. **Docker Build Issues**:
   ```
   Error: Docker build failed
   ```
   **Solution**: Ensure Docker is running and has sufficient resources

### Runtime Issues

1. **Authentication Failures**:
   - Verify Cognito user pool configuration
   - Check user credentials and status
   - Ensure browser accepts cookies

2. **Multi-Agent Errors**:
   - Check AWS credentials and permissions
   - Verify Bedrock model availability
   - Review CloudWatch logs for detailed errors

3. **Knowledge Base Delays**:
   - Normal behavior: 2-3 minutes for indexing
   - Check environment variables are set correctly
   - Verify IAM permissions for Knowledge Base operations

### Performance Optimization

1. **ECS Task Resources**: Adjust CPU and memory allocation based on usage
2. **Auto-Scaling**: Configure ECS service auto-scaling for demand spikes
3. **CloudFront Caching**: Optimize cache policies for static assets
4. **Bedrock Costs**: Monitor token usage and consider model alternatives

## Related Documentation

- [Multi-Agent Implementation](../multi_agent_bedrock/README.md) - Local development guide
- [App Merge Guide](../APP_MERGE_GUIDE.md) - Authentication integration instructions
- [Authentication Analysis](../AUTHENTICATION_ANALYSIS.md) - Technical authentication details
- [Main Workshop Guide](../MULTI_AGENT_BEDROCK.md) - Complete workshop documentation

## Acknowledgments

This deployment infrastructure is based on:
* [Streamlit CDK Fargate](https://github.com/tzaffi/streamlit-cdk-fargate.git)
* [AWS Bedrock Workshop Samples](https://github.com/aws-samples/build-scale-generative-ai-applications-with-amazon-bedrock-workshop/)

Enhanced with multi-agent capabilities using Strands Agents SDK and comprehensive Bedrock integration.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This application is licensed under the MIT-0 License. See the LICENSE file.