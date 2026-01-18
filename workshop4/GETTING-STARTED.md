# Getting Started Guide

Welcome to Workshop 4! This guide will help you set up your development environment and verify everything works correctly before diving into the AI agent development modules.

## Prerequisites

### System Requirements

- **Python**: 3.12.x or 3.13.x (recommended: 3.12.10)
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Memory**: 8GB RAM minimum, 16GB recommended
- **Storage**: 5GB free space for dependencies and virtual environments

### AWS Requirements

- **AWS Account**: Active AWS account with programmatic access
- **AWS Credentials**: Access key and secret key with appropriate permissions
- **AWS Region**: Region supporting Amazon Bedrock (recommended: `us-east-1` or `us-west-2`)
- **Bedrock Access**: Permissions to invoke Amazon Bedrock models

### Required AWS Permissions

Your AWS credentials need the following permissions:
- `bedrock:InvokeModel` - For AI model inference
- `bedrock-agent:*` - For Knowledge Base operations (Module 3+)
- `s3:*` - For Knowledge Base storage (Module 3+)
- `secretsmanager:GetSecretValue` - For deployed applications

## Environment Setup

### Step 1: Install Python

#### Windows
1. Download Python 3.12.x from [python.org](https://python.org)
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Install Visual Studio Build Tools for package compilation:
   - Download "Build Tools for Visual Studio 2022"
   - Select "Desktop development with C++" workload
   - Reboot after installation

#### macOS
```bash
# Using Homebrew (recommended)
brew install python@3.12

# Or download from python.org
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev
```

### Step 2: Install UV Package Manager

UV is a fast, cross-platform Python package manager that ensures consistent behavior across platforms.

```bash
# Install UV (same command for all platforms)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload your shell
source ~/.bashrc  # Linux/macOS
# Or restart your terminal
```

### Step 3: Clone and Setup Workshop

```bash
# Navigate to your development directory
cd ~/development  # or your preferred location

# Clone the workshop repository (if not already done)
# git clone <repository-url>
cd workshop4

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
source .venv/Scripts/activate  # Windows Git Bash

# Install dependencies
uv pip install -r requirements.txt
```

### Step 4: Configure AWS Credentials

#### Option 1: Environment Variables (Recommended for Development)

**Linux/macOS/Git Bash:**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_SESSION_TOKEN="your-session-token"  # For temporary credentials
export AWS_REGION="us-east-1"  # or us-west-2

# Make persistent (optional)
echo 'export AWS_REGION="us-east-1"' >> ~/.bashrc
source ~/.bashrc
```

### Step 5: Deploy SSM Parameter Store Configuration (For Multi-Agent Application)

The multi-agent application uses AWS Systems Manager (SSM) Parameter Store for centralized configuration management. This eliminates the need for environment variables and enables dynamic configuration updates without restarting the application.

#### Deploy Configuration Parameters

```bash
# Navigate to SSM configuration directory
cd workshop4/ssm

# Deploy CloudFormation stack with your configuration
aws cloudformation create-stack \
  --stack-name teachers-assistant-params-dev \
  --template-body file://teachers-assistant-params.yaml \
  --parameters ParameterKey=Environment,ParameterValue=dev

# Wait for stack creation to complete
aws cloudformation wait stack-create-complete \
  --stack-name teachers-assistant-params-dev

# Verify parameters were created
aws ssm get-parameters-by-path \
  --path "/teachers_assistant/dev" \
  --recursive
```

#### Set Environment Variables

After deploying the SSM parameters, you need to set TWO environment variables:

```bash
# Linux/macOS/Git Bash
export TEACHERS_ASSISTANT_ENV=dev
export AWS_REGION=us-east-1

# Make persistent (optional)
echo 'export TEACHERS_ASSISTANT_ENV=dev' >> ~/.bashrc
echo 'export AWS_REGION=us-east-1' >> ~/.bashrc
source ~/.bashrc
```

**Windows PowerShell:**
```powershell
$Env:TEACHERS_ASSISTANT_ENV="dev"
$Env:AWS_REGION="us-east-1"
```

#### Configuration Overview

The application uses two types of configuration:

**Environment Variables** (2 total):
| Variable | Default | Description |
|----------|---------|-------------|
| `TEACHERS_ASSISTANT_ENV` | `dev` | Environment name (dev, staging, prod) - determines which SSM parameter path to use |
| `AWS_REGION` | `us-east-1` | AWS region for all services (standard AWS SDK variable) |

**SSM Parameter Store** (8 parameters created by CloudFormation):
| Parameter | SSM Path | Default | Description |
|-----------|----------|---------|-------------|
| Default Model ID | `/teachers_assistant/dev/default_model_id` | `us.amazon.nova-2-lite-v1:0` | Default model ID (typically Bedrock cross-region profile) |
| Max Results | `/teachers_assistant/dev/max_results` | `9` | Maximum knowledge base search results |
| Min Score | `/teachers_assistant/dev/min_score` | `0.000001` | Minimum relevance score threshold |
| SageMaker Model Endpoint | `/teachers_assistant/dev/sagemaker_model_endpoint` | `my-sagemaker-model-endpoint` | SageMaker model endpoint name |
| SageMaker Model Inference Component | `/teachers_assistant/dev/sagemaker_model_inference_component` | `my-sagemaker-model-inference-component` | SageMaker model inference component (for multi-model endpoints) |
| Strands Knowledge Base ID | `/teachers_assistant/dev/strands_knowledge_base_id` | `my-strands-knowledge-base-id` | Strands Knowledge Base identifier (Framework requirement) |
| Temperature | `/teachers_assistant/dev/temperature` | `0.3` | Model temperature setting (0.0-1.0) |
| XGBoost Model Endpoint | `/teachers_assistant/dev/xgboost_model_endpoint` | `my-xgboost-model-endpoint` | XGBoost model endpoint name |

**Important Notes:**
- **Environment Variables**: `TEACHERS_ASSISTANT_ENV` and `AWS_REGION` must be set as environment variables (not in SSM)
- **SSM Parameters**: All other configuration is stored in SSM Parameter Store
- Values with `my-*` prefixes are placeholders. Deploy the CloudFormation template "as is" with these defaults, then update them via AWS Console or CLI with your actual AWS resource names.
- `sagemaker_model_inference_component` is only needed if your SageMaker endpoint uses inference components (multi-model endpoints).
- To find your inference component name: `aws sagemaker list-inference-components --endpoint-name-equals <endpoint-name>`
- Model provider (Bedrock vs SageMaker) is determined dynamically from the UI model selection, not stored as configuration.
- `strands_knowledge_base_id` must keep this exact naming as it's a Strands Agents framework requirement for Bedrock Knowledge Base integration.
- `AWS_REGION` is a standard AWS SDK environment variable - in EC2/ECS deployments, this is automatically detected from instance metadata.

#### Update Configuration Parameters

To update a parameter after deployment:

```bash
# Update a single parameter
aws ssm put-parameter \
  --name "/teachers_assistant/dev/default_model_id" \
  --value "us.amazon.nova-pro-v1:0" \
  --overwrite

# Note: CloudFormation stack updates CANNOT change parameter values
# You must update parameters directly in SSM Parameter Store
```

For detailed SSM deployment instructions, see `workshop4/ssm/README.md`.

### Step 6: Verify Setup

#### Test Python and Dependencies
```bash
# Check Python version
python --version
# Should show Python 3.12.x or 3.13.x

# Check UV installation
uv --version

# Verify virtual environment is activated
which python
# Should show path to .venv/bin/python or .venv/Scripts/python
```

#### Test AWS Connectivity
```bash
# Test AWS credentials
aws sts get-caller-identity

# Test Bedrock access
aws bedrock list-foundation-models --region $AWS_REGION
```

#### Validate SSM Parameters (REQUIRED)

Before running the multi-agent application, validate that all SSM parameters are accessible:

```bash
# Navigate to validation directory
cd workshop4/validation

# Run SSM parameter validation
python validate_ssm_parameters.py
```

**Expected Output:**
```
======================================================================
  SSM Parameter Store Validation
======================================================================

📋 Configuration:
   Environment: dev
   AWS Region: us-east-1
   Parameter Path: /teachers_assistant/dev/
----------------------------------------------------------------------

🔍 Fetching parameters from SSM Parameter Store...

📊 Validation Results:
   Expected parameters: 8
   Found parameters: 8
   Missing parameters: 0

✅ ALL PARAMETERS FOUND:
----------------------------------------------------------------------
   default_model_id                         = us.amazon.nova-2-lite-v1:0
   max_results                              = 9
   min_score                                = 0.000001
   sagemaker_model_endpoint                 = my-sagemaker-model-endpoint ⚠️  (placeholder - needs update)
   sagemaker_model_inference_component      = my-sagemaker-model-inference-component ⚠️  (placeholder - needs update)
   strands_knowledge_base_id                = my-strands-knowledge-base-id ⚠️  (placeholder - needs update)
   temperature                              = 0.3
   xgboost_model_endpoint                   = my-xgboost-model-endpoint ⚠️  (placeholder - needs update)
----------------------------------------------------------------------

⚠️  WARNING: 4 parameter(s) still have placeholder values:
   - sagemaker_model_endpoint
   - sagemaker_model_inference_component
   - strands_knowledge_base_id
   - xgboost_model_endpoint

💡 Update these parameters with your actual AWS resource names:
   1. Via AWS Console: Systems Manager → Parameter Store
   2. Via AWS CLI: aws ssm put-parameter --name <path> --value <value> --overwrite

======================================================================
✅ SSM Parameter Store validation PASSED
======================================================================
```

**Note**: Parameters with placeholder values (starting with `my-`) should be updated with your actual AWS resource names before running the application.

#### Validate SageMaker Endpoints (Optional)

If you're using SageMaker models, validate that your endpoints are operational:

```bash
# Still in workshop4/validation directory

# Validate SageMaker model endpoint
python validate_sagemaker_endpoint.py

# Validate XGBoost model endpoint
python validate_xgboost_endpoint.py
```

These validation scripts will:
- Read endpoint names from SSM Parameter Store
- Send test inference requests
- Verify endpoints are responding correctly

**Skip these if you're only using Bedrock models.**

#### Test Basic Strands Functionality
```bash
# Quick test of Strands Agents SDK
cd modules/module1
uv run -c "from strands.agents import Agent; print('Strands SDK loaded successfully!')"
```

## Platform-Specific Notes

### Windows Development

**Recommended Terminal**: Use Git Bash for the best cross-platform experience
- Download Git for Windows with Git Bash option
- Git Bash provides Unix-like commands that match the documentation

**PowerShell Users**: If you must use PowerShell:
- Environment variables only persist for the current session
- Use `$Env:VARIABLE_NAME="value"` syntax
- Run all commands in the same PowerShell session

**Common Windows Issues**:
- **Build Tools**: Some packages require Visual Studio Build Tools
- **Path Issues**: Ensure Python is in your PATH
- **Firewall**: Allow Python through Windows Firewall if needed

### macOS Development

**Xcode Command Line Tools**: Required for some package compilation
```bash
xcode-select --install
```

**Homebrew**: Recommended for Python installation
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Linux Development

**Build Dependencies**: Install development packages
```bash
# Ubuntu/Debian
sudo apt install build-essential python3-dev

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install python3-devel
```

## Troubleshooting

### Common Setup Issues

#### Python Version Issues
```bash
# Check available Python versions
python3 --version
python3.12 --version

# Use specific version if needed
python3.12 -m venv .venv
```

#### Package Installation Failures
```bash
# Clear UV cache
uv cache clean

# Reinstall with verbose output
uv pip install -r requirements.txt -v

# Windows: Ensure Build Tools are installed
```

#### AWS Credential Issues
```bash
# Verify credentials are set
env | grep AWS

# Test with specific profile
aws sts get-caller-identity --profile your-profile-name

# Check region configuration
echo $AWS_REGION
```

#### Virtual Environment Issues
```bash
# Deactivate and recreate
deactivate
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Getting Help

#### Check System Information
```bash
# Platform information
python -c "import platform; print(platform.platform())"

# Python path and version
python -c "import sys; print(sys.executable, sys.version)"

# Installed packages
uv pip list
```

#### Verify Workshop Structure
```bash
# Check directory structure
ls -la workshop4/
ls -la workshop4/modules/
```

## Next Steps

Once your environment is set up and verified:

1. **Start with Foundations**: Go to [Part 1: Foundational Modules](PART-1-FOUNDATIONS.md)
2. **Choose Your Track**: After foundations, pick [Bedrock](PART-2-BEDROCK.md) or [SageMaker](PART-3-SAGEMAKER.md)
3. **Get Help**: Use [Reference Guide](REFERENCE.md) for troubleshooting

## Quick Start Verification

Run this quick test to ensure everything is working:

```bash
# Navigate to workshop directory
cd workshop4

# Activate virtual environment
source .venv/bin/activate

# Test Module 1 (basic functionality)
cd modules/module1
uv run mcp_calculator.py

# Try a simple calculation
# Input: "What is 2 + 2?"
# Expected: Mathematical calculation with result

# Exit with: exit
```

If this works, you're ready to begin the workshop!

---

**Environment Setup Complete!** 🎉

Your development environment is now configured and ready for AI agent development. Proceed to [Part 1: Foundational Modules](PART-1-FOUNDATIONS.md) to begin your learning journey.