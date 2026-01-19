# Part 3: Production Deployment (Docker + AWS)

Deploy the multi-agent system to production using Docker containers, AWS CDK, and ECS Fargate. This guide covers building, testing, and deploying the application with full authentication and monitoring.

## Overview

The `deploy_multi_agent` directory contains the production-ready version of the application with:
- **Docker Containerization**: Packaged for consistent deployment
- **AWS CDK Infrastructure**: Automated infrastructure provisioning
- **ECS Fargate Hosting**: Serverless container hosting
- **Cognito Authentication**: Secure user authentication
- **CloudFront Distribution**: Global content delivery
- **Comprehensive Monitoring**: CloudWatch logs and metrics

**Time Investment**: 2-3 hours
**Prerequisites**: 
- [Part 2: Multi-Agent](PART-2-MULTI-AGENT.md) completed and tested
- AWS account with appropriate permissions
- AWS CDK installed

## Architecture

### Production Components

```
┌─────────────────────────────────────────────────────────────┐
│                        CloudFront                            │
│                    (Global CDN + HTTPS)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                Application Load Balancer                     │
│                  (Health Checks + Routing)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                     ECS Fargate                              │
│              (Serverless Container Hosting)                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Streamlit Multi-Agent Application            │  │
│  │  - Teacher's Assistant + 5 Specialized Agents        │  │
│  │  - Model Selection (Bedrock + SageMaker)             │  │
│  │  - Knowledge Base Integration                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼──────┐
│   Cognito    │  │   Bedrock   │  │  SageMaker │
│    (Auth)    │  │   (Models)  │  │  (Models)  │
└──────────────┘  └─────────────┘  └────────────┘
```

### Key Differences from Local Development

| Aspect | Local (`multi_agent`) | Production (`deploy_multi_agent`) |
|--------|----------------------|-----------------------------------|
| **Authentication** | None | Cognito user pool |
| **Hosting** | Local Streamlit | ECS Fargate containers |
| **HTTPS** | HTTP only | CloudFront + ACM certificate |
| **Scaling** | Single instance | Auto-scaling containers |
| **Monitoring** | Console logs | CloudWatch logs + metrics |
| **Configuration** | SSM Parameter Store | SSM Parameter Store |

## Prerequisites

### 1. Verify Local Application Works

Ensure Part 2 testing completed successfully:
```bash
cd ~/workspace/ai-stack-2026Q2/workshop4/multi_agent
streamlit run app.py
# Test all features work correctly
```

**Note**: Since you've already tested the application locally in Part 2, there's no need to test Docker locally. We'll deploy directly to ECS Fargate and test the actual container in production.

### 2. Install AWS CDK

```bash
npm install -g aws-cdk

# Verify installation
cdk --version
```

### 3. Bootstrap CDK (First Time Only)

```bash
cdk bootstrap aws://ACCOUNT-ID/REGION

# Example
cdk bootstrap aws://123456789012/us-east-1
```

## Step 1: Merge Local Code to Deployment Directory

Before deploying, you need to merge your tested local code from `multi_agent/` into `deploy_multi_agent/docker_app/`.

### Why Merge?

The `deploy_multi_agent/docker_app/` directory contains the production version with:
- Cognito authentication (lines 1-25 in app.py)
- Docker configuration
- Production environment settings

Your `multi_agent/` directory contains:
- Latest agent implementations
- Model factory pattern
- SSM Parameter Store integration
- All bug fixes and improvements

### Merge Strategy: Bulk Copy + Careful app.py Merge

**IMPORTANT**: Copy ALL Python files from `multi_agent/` to `deploy_multi_agent/docker_app/` EXCEPT `app.py`.

#### Step 1.1: Bulk Copy All Files (Except app.py)

```bash
cd ~/workspace/ai-stack-2026Q2/workshop4

# Copy all Python files except app.py
cp multi_agent/config.py deploy_multi_agent/docker_app/
cp multi_agent/bedrock_model.py deploy_multi_agent/docker_app/
cp multi_agent/sagemaker_model.py deploy_multi_agent/docker_app/
cp multi_agent/model_factory.py deploy_multi_agent/docker_app/
cp multi_agent/teachers_assistant.py deploy_multi_agent/docker_app/
cp multi_agent/math_assistant.py deploy_multi_agent/docker_app/
cp multi_agent/english_assistant.py deploy_multi_agent/docker_app/
cp multi_agent/computer_science_assistant.py deploy_multi_agent/docker_app/
cp multi_agent/language_assistant.py deploy_multi_agent/docker_app/
cp multi_agent/loan_offering_assistant.py deploy_multi_agent/docker_app/
cp multi_agent/no_expertise.py deploy_multi_agent/docker_app/
cp multi_agent/cross_platform_tools.py deploy_multi_agent/docker_app/
```

**Why bulk copy?** All assistant files changed to use the model_factory pattern instead of hardcoded models. Copying everything ensures you don't miss any changes.

#### Step 1.2: Carefully Merge app.py

The `app.py` file requires special handling to preserve Cognito authentication.

**Preserve from deploy_multi_agent/docker_app/app.py**:
- Lines 1-25: Cognito authentication imports and setup
- Authentication UI section (login form, session state)

**Merge from multi_agent/app.py**:
- Model selection logic
- Agent initialization with model_factory
- Conversation handling
- All functional improvements

**Manual Merge Steps**:

1. Open both files side-by-side
2. Keep the Cognito authentication section (lines 1-25) from `deploy_multi_agent/docker_app/app.py`
3. Copy the model selection and agent logic from `multi_agent/app.py`
4. Ensure model_factory is used for all agent initializations
5. Verify authentication UI remains intact

**Key Sections to Preserve**:
```python
# From deploy_multi_agent/docker_app/app.py (KEEP THIS)
from utils.auth import check_authentication

# Authentication check
if not check_authentication():
    st.stop()
```

**Key Sections to Merge**:
```python
# From multi_agent/app.py (MERGE THIS)
from model_factory import create_model

# Model selection
selected_model = st.selectbox(...)
model = create_model(selected_model, config)

# Agent initialization with model
agent = TeachersAssistant(model=model, ...)
```

### Verification Checklist

After merging, verify:
- ✅ All 12 Python files copied from `multi_agent/` to `deploy_multi_agent/docker_app/`
- ✅ `app.py` has Cognito authentication preserved
- ✅ `app.py` uses model_factory for agent initialization
- ✅ All assistants use the model parameter (not hardcoded models)
- ✅ SSM Parameter Store configuration intact

## Step 2: Review Deployment Structure

### Directory Structure

```
deploy_multi_agent/
├── app.py                    # CDK application entry point
├── cdk/
│   ├── cdk_stack.py         # Infrastructure definition (IAM permissions updated)
│   └── __init__.py
├── docker_app/              # Application code (Docker container)
│   ├── app.py              # Streamlit application (merged with Cognito auth)
│   ├── Dockerfile          # Container definition
│   ├── docker-compose.yml  # Local Docker testing
│   ├── requirements.txt    # Python dependencies
│   ├── config.py           # Configuration module (from multi_agent)
│   ├── bedrock_model.py    # Bedrock model wrapper (from multi_agent)
│   ├── sagemaker_model.py  # SageMaker model wrapper (from multi_agent)
│   ├── model_factory.py    # Model factory pattern (from multi_agent)
│   ├── *_assistant.py      # Specialized agents (from multi_agent)
│   ├── cross_platform_tools.py  # Cross-platform utilities (from multi_agent)
│   └── utils/              # Utility modules
│       ├── auth.py         # Cognito authentication
│       └── llm.py          # Model creation
├── cdk.json                # CDK configuration
└── README.md               # Deployment documentation
```

### Key Files

**Infrastructure** (`cdk/cdk_stack.py`):
- VPC and networking
- ECS Fargate cluster and service
- Application Load Balancer
- Cognito user pool
- CloudFront distribution
- IAM roles and policies

**Application** (`docker_app/app.py`):
- Same multi-agent logic as local version
- Added Cognito authentication
- Environment-based configuration
- Production logging

## Step 3: Configure Deployment

### Update CDK Context

Edit `deploy_multi_agent/cdk.json`:

```json
{
  "context": {
    "environment": "dev",
    "vpc_cidr": "10.0.0.0/16",
    "container_port": 8501,
    "desired_count": 1,
    "cpu": 512,
    "memory": 1024
  }
}
```

### Review IAM Permissions

The CDK stack creates an ECS task role with permissions for:
- SSM Parameter Store read access
- Bedrock model invocation
- SageMaker endpoint invocation
- CloudWatch Logs write access

## Step 4: Deploy Infrastructure

### Synthesize CloudFormation Template

```bash
cd ~/workspace/ai-stack-2026Q2/workshop4/deploy_multi_agent

# Generate CloudFormation template
cdk synth
```

Review the generated template in `cdk.out/`.

### Deploy to AWS

```bash
# Deploy the stack
cdk deploy

# Confirm changes when prompted
# This will take 10-15 minutes
```

**Expected Output:**
```
✅  DeployMultiAgentStack

Outputs:
DeployMultiAgentStack.LoadBalancerDNS = multi-agent-lb-123456789.us-east-1.elb.amazonaws.com
DeployMultiAgentStack.CloudFrontURL = https://d1234567890abc.cloudfront.net
DeployMultiAgentStack.CognitoUserPoolId = us-east-1_ABC123DEF
DeployMultiAgentStack.CognitoClientId = 1234567890abcdefghijklmnop

Stack ARN:
arn:aws:cloudformation:us-east-1:123456789012:stack/DeployMultiAgentStack/...
```

### Save Outputs

Save the CloudFront URL and Cognito details for later use.

## Step 5: Create Cognito User

### Create User via AWS Console

1. Navigate to AWS Console → Cognito
2. Select the user pool (from CDK output)
3. Click "Create user"
4. Enter username and temporary password
5. Uncheck "Send email invitation"
6. Click "Create user"

### Create User via AWS CLI

```bash
aws cognito-idp admin-create-user \
  --user-pool-id <USER_POOL_ID> \
  --username testuser \
  --temporary-password TempPass123! \
  --message-action SUPPRESS
```

## Step 6: Test Deployed Application

### Access Application

Navigate to the CloudFront URL from CDK output:
```
https://d1234567890abc.cloudfront.net
```

### Login

1. Enter username and temporary password
2. Set new permanent password when prompted
3. Verify you're redirected to application

### Test Features

Run the same tests from Part 2:
1. ✅ Model selection
2. ✅ Specialized agents
3. ✅ Agent type selection
4. ✅ Knowledge base operations
5. ✅ Conversation history

## Step 7: Monitor Application

### CloudWatch Logs

```bash
# View ECS task logs
aws logs tail /ecs/multi-agent-app --follow

# Filter for errors
aws logs filter-log-events \
  --log-group-name /ecs/multi-agent-app \
  --filter-pattern "ERROR"
```

### CloudWatch Metrics

Navigate to AWS Console → CloudWatch → Metrics:
- ECS service CPU utilization
- ECS service memory utilization
- ALB request count
- ALB target response time

### ECS Service Health

```bash
# Check service status
aws ecs describe-services \
  --cluster multi-agent-cluster \
  --services multi-agent-service

# Check task status
aws ecs list-tasks \
  --cluster multi-agent-cluster \
  --service-name multi-agent-service
```

## Debugging Production Issues

### Issue 1: Container Won't Start

**Check ECS Task Logs**:
```bash
aws logs tail /ecs/multi-agent-app --follow
```

**Common Causes**:
- Missing environment variables
- SSM parameter access denied
- Docker image build errors

**Solutions**:
1. Verify IAM task role has SSM permissions
2. Check CloudFormation stack events for errors
3. Rebuild Docker image and redeploy

### Issue 2: Authentication Not Working

**Check Cognito Configuration**:
```bash
aws cognito-idp describe-user-pool --user-pool-id <USER_POOL_ID>
```

**Common Causes**:
- User not created
- Incorrect client ID
- Password policy not met

**Solutions**:
1. Create user via Console or CLI
2. Verify client ID in application configuration
3. Use strong password meeting policy requirements

### Issue 3: Application Slow or Timing Out

**Check ECS Service Scaling**:
```bash
aws ecs describe-services \
  --cluster multi-agent-cluster \
  --services multi-agent-service \
  --query 'services[0].desiredCount'
```

**Solutions**:
1. Increase desired task count in CDK
2. Increase CPU/memory allocation
3. Enable auto-scaling based on metrics

### Issue 4: SSM Parameters Not Found

**Verify Parameters Exist**:
```bash
aws ssm get-parameters-by-path \
  --path "/teachers_assistant/dev" \
  --recursive
```

**Solutions**:
1. Ensure CloudFormation stack deployed successfully
2. Verify TEACHERS_ASSISTANT_ENV environment variable set correctly
3. Check IAM task role has `ssm:GetParameter*` permissions

## Updating the Deployment

### Update Application Code

```bash
cd ~/workspace/ai-stack-2026Q2/workshop4/deploy_multi_agent

# Make code changes in docker_app/

# Rebuild and deploy
cdk deploy
```

CDK will:
1. Build new Docker image
2. Push to ECR
3. Update ECS service with new image
4. Perform rolling update (zero downtime)

### Update Infrastructure

```bash
# Modify cdk/cdk_stack.py

# Preview changes
cdk diff

# Deploy changes
cdk deploy
```

### Update SSM Parameters

```bash
# Update parameter value
aws ssm put-parameter \
  --name "/teachers_assistant/dev/temperature" \
  --value "0.5" \
  --overwrite

# Application picks up changes on next request (no restart needed)
```

## Cleanup

### Destroy Infrastructure

```bash
cd ~/workspace/ai-stack-2026Q2/workshop4/deploy_multi_agent

# Destroy all resources
cdk destroy

# Confirm when prompted
```

This will delete:
- ECS cluster and services
- Load balancer
- CloudFront distribution
- Cognito user pool
- VPC and networking
- IAM roles

**Note**: SSM parameters are NOT deleted (managed separately).

### Delete SSM Parameters

```bash
aws cloudformation delete-stack --stack-name teachers-assistant-params-dev
```

## Cost Optimization

### Development Environment

For development/testing, minimize costs:

```json
{
  "context": {
    "desired_count": 1,
    "cpu": 256,
    "memory": 512
  }
}
```

### Production Environment

For production workloads:

```json
{
  "context": {
    "desired_count": 2,
    "cpu": 1024,
    "memory": 2048,
    "enable_auto_scaling": true,
    "min_capacity": 2,
    "max_capacity": 10
  }
}
```

### Ephemeral SageMaker Endpoints

Delete SageMaker endpoints when not in use:

```bash
# Delete endpoint
aws sagemaker delete-endpoint --endpoint-name my-gpt-oss-20b-1-1768709790

# Recreate when needed
# Update SSM parameter with new endpoint name
aws ssm put-parameter \
  --name "/teachers_assistant/dev/sagemaker_model_endpoint" \
  --value "new-endpoint-name" \
  --overwrite
```

Application will use new endpoint automatically.

## Key Learnings

### Docker Containerization
- Consistent deployment across environments
- Isolated dependencies and runtime
- Easy local testing before deployment

### AWS CDK Infrastructure
- Infrastructure as code with TypeScript/Python
- Automated resource provisioning
- Version controlled infrastructure

### ECS Fargate Hosting
- Serverless container hosting
- No server management
- Auto-scaling based on demand

### Cognito Authentication
- Managed user authentication
- Secure password policies
- Easy integration with applications

### CloudWatch Monitoring
- Centralized logging
- Metrics and alarms
- Troubleshooting and debugging

---

**Production Deployment Complete!** 🎉

You've successfully deployed the multi-agent application to production with full authentication, monitoring, and scalability. The application is now accessible globally via CloudFront with enterprise-grade security and reliability.

## Next Steps

1. **Monitor**: Set up CloudWatch alarms for critical metrics
2. **Optimize**: Tune CPU/memory allocation based on usage
3. **Scale**: Enable auto-scaling for production workloads
4. **Customize**: Add new agents, modify prompts, enhance features
5. **Secure**: Implement additional security controls (WAF, Shield, etc.)

## Additional Resources

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [ECS Fargate Documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)
- [Cognito Documentation](https://docs.aws.amazon.com/cognito/)
- [CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [Strands Agents Documentation](https://strandsagents.com/)
