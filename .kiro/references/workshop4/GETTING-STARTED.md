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

#### Run All Validations (REQUIRED)

Before running the multi-agent application, validate that your environment is properly configured. Since both the `multi_agent` and `deploy_multi_agent` applications support **both Bedrock and SageMaker models**, you should run **all three validation scripts**.

**Option 1: Run All Validations at Once (Recommended)**

```bash
# Navigate to validation directory
cd workshop4/validation

# Run comprehensive validation
uv run validate_all.py
```

This will run all three validations in sequence and provide a summary.

**Option 2: Run Individual Validations**

If you prefer to run validations individually:

```bash
# Navigate to validation directory
cd workshop4/validation

# 1. Validate SSM Parameter Store (REQUIRED)
uv run validate_ssm_parameters.py

# 2. Validate SageMaker Model Endpoint (REQUIRED)
uv run validate_sagemaker_endpoint.py

# 3. Validate XGBoost Model Endpoint (REQUIRED)
uv run validate_xgboost_endpoint.py
```

#### Expected Output

When running `validate_all.py`, you should see output similar to this:

```
======================================================================
  Comprehensive Validation - Multi-Agent Application
======================================================================

📋 Configuration:
   Environment: dev
   AWS Region: us-east-1
   Python: D:\Users\wangrob\workspace\ai-stack-2026Q2\workshop4\venv\Scripts\python.exe

----------------------------------------------------------------------

🔍 Running Validation 1 of 3...

======================================================================
  Validation 1: SSM Parameter Store
======================================================================

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
   sagemaker_model_endpoint                 = my-gpt-oss-20b-1-1768709790
   sagemaker_model_inference_component      = adapter-my-gpt-oss-20b-1-1768709790-1768709796
   strands_knowledge_base_id                = IMW46CITZE
   temperature                              = 0.3
   xgboost_model_endpoint                   = xgboost-serverless-ep2026-01-12-05-31-16
----------------------------------------------------------------------

======================================================================
✅ SSM Parameter Store validation PASSED
======================================================================

----------------------------------------------------------------------

🔍 Running Validation 2 of 3...

======================================================================
  Validation 2: SageMaker Model Endpoint
======================================================================

======================================================================
  SageMaker Model Endpoint Validation
======================================================================

📋 Environment: dev
   AWS Region: us-east-1
   Reading configuration from SSM Parameter Store...
   Parameter path: /teachers_assistant/dev/

🔍 Validating SageMaker Model Endpoint: my-gpt-oss-20b-1-1768709790
   Region: us-east-1
   Inference Component: adapter-my-gpt-oss-20b-1-1768709790-1768709796
------------------------------------------------------------

📤 Sending test request...
   Prompt: What is the capital of France?
   Max tokens: 50

✅ SUCCESS: Endpoint is responding correctly!

📥 Response:
   {"generated_text": "..."}

� Note: The response quality depends on the model type:
   - Base models may generate less coherent text
   - Instruction-tuned models will follow prompts better
   - The validation confirms the endpoint is operational

============================================================
✅ SageMaker model endpoint validation PASSED
============================================================

----------------------------------------------------------------------

🔍 Running Validation 3 of 3...

======================================================================
  Validation 3: XGBoost Model Endpoint
======================================================================

======================================================================
  XGBoost Model Endpoint Validation
======================================================================

� Environment: dev
   AWS Region: us-east-1
   Reading configuration from SSM Parameter Store...
   Parameter path: /teachers_assistant/dev/

🔍 Validating XGBoost Model Endpoint: xgboost-serverless-ep2026-01-12-05-31-16
   Region: us-east-1
------------------------------------------------------------

📤 Sending test request...
   Sample customer data (59 features)
   Format: CSV (text/csv)

   Feature values:
   29,2,999,0,1,0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,...

   First 10 features: 29, 2, 999, 0, 1, 0, 0.0, 1.0, 0.0, 0.0
   Last 10 features: 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0

✅ SUCCESS: Endpoint is responding correctly!

📥 Response:
   Raw prediction: 0.04957985132932663
   Prediction label: Reject
   Confidence: 4.96%

============================================================
✅ XGBoost model endpoint validation PASSED
============================================================

======================================================================
  Validation Summary
======================================================================

   SSM Parameter Store            ✅ PASSED
   SageMaker Model Endpoint       ✅ PASSED
   XGBoost Model Endpoint         ✅ PASSED

======================================================================
✅ ALL VALIDATIONS PASSED
======================================================================

🎉 Your environment is ready for the multi-agent application!

Next Steps:
   1. Review PART-2-MULTI-AGENT.md for local development
   2. Run: cd ../multi_agent && streamlit run app.py
   3. Test model selection and agent features
```

#### Why All Three Validations?

Both the `multi_agent` (local) and `deploy_multi_agent` (production) applications support:
- ✅ **Bedrock Models**: 4 models via cross-region inference profiles
- ✅ **SageMaker Models**: Custom trained models via endpoints
- ✅ **XGBoost Models**: Loan prediction assistant feature

Running all three validations ensures:
1. **SSM Parameter Store** is accessible and configured
2. **SageMaker endpoint** is operational for custom model selection
3. **XGBoost endpoint** is operational for loan prediction features

**Note**: If you only plan to use Bedrock models and skip the loan prediction feature, you can skip validations 2 and 3. However, running all three is recommended to verify your complete environment.

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