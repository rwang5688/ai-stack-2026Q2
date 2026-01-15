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

**Additional Environment Variables for Multi-Agent Application:**

Add these to your `~/.bashrc` or `~/.bash_profile` for the multi-agent application:

```bash
# Workshop4 Multi-Agent SageMaker AI - Environment Variables
export AWS_REGION="us-east-1"
export BEDROCK_MODEL_ID="us.amazon.nova-pro-v1:0"
export MAX_RESULTS="9"
export MIN_SCORE="0.000001"
export SAGEMAKER_INFERENCE_COMPONENT="my-llm-inference-component"  # Optional: only needed for multi-model endpoints
export SAGEMAKER_MODEL_ENDPOINT="my-llm-endpoint"
export STRANDS_KNOWLEDGE_BASE_ID="my-kb-id"
export STRANDS_MODEL_PROVIDER="bedrock"
export XGBOOST_ENDPOINT_NAME="my-xgboost-endpoint"
```

**Environment Variable Details:**

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AWS_REGION` | AWS region for services | `us-east-1` | Yes |
| `BEDROCK_MODEL_ID` | Bedrock model/inference profile | `us.amazon.nova-pro-v1:0` | When using Bedrock |
| `MAX_RESULTS` | Max knowledge base results | `9` | No |
| `MIN_SCORE` | Min relevance score threshold | `0.000001` | No |
| `SAGEMAKER_MODEL_ENDPOINT` | SageMaker endpoint name | `my-llm-endpoint` | When using SageMaker |
| `SAGEMAKER_INFERENCE_COMPONENT` | Inference component name | `my-llm-inference-component` | Only for multi-model endpoints |
| `STRANDS_KNOWLEDGE_BASE_ID` | Knowledge base ID | `my-kb-id` | For KB features |
| `STRANDS_MODEL_PROVIDER` | Model provider choice | `bedrock` | Yes |
| `XGBOOST_ENDPOINT_NAME` | XGBoost endpoint name | `my-xgboost-endpoint` | For loan assistant |

**Note:** 
- Values with `my-*` prefixes are placeholders. Replace them with your actual AWS resource names when you create them in later modules.
- `SAGEMAKER_INFERENCE_COMPONENT` is only needed if your SageMaker endpoint uses inference components (multi-model endpoints). Leave empty or unset for standard endpoints.
- To find your inference component name: `aws sagemaker list-inference-components --endpoint-name-equals <endpoint-name>`

**Windows PowerShell:**
```powershell
$Env:AWS_ACCESS_KEY_ID="your-access-key"
$Env:AWS_SECRET_ACCESS_KEY="your-secret-key"
$Env:AWS_SESSION_TOKEN="your-session-token"
$Env:AWS_REGION="us-east-1"
```

#### Option 2: AWS CLI Configuration

```bash
# Install AWS CLI if not already installed
pip install awscli

# Configure credentials
aws configure
# Enter your access key, secret key, region, and output format
```

### Step 5: Verify Setup

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