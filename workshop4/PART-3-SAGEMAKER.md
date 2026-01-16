# Part 3: Multi-Agent with Amazon SageMaker AI

Build a sophisticated multi-agent system using Amazon SageMaker AI models, demonstrating flexibility in choosing reasoning LLMs and integrating team-trained predictive models.

## Overview

This track demonstrates how to implement a multi-agent architecture using Amazon SageMaker AI model hosting. You'll learn to integrate both reasoning models (for agent intelligence) and predictive models (for specialized tasks like loan prediction) into a unified multi-agent application.

**Status**: 🚧 **In Development** - Prerequisites validation available now
**Time Investment**: 6-8 hours total
**Prerequisites**: [Part 1: Foundational Modules](PART-1-FOUNDATIONS.md) completed

## Learning Journey

```
Step 1: Validate Endpoints → Step 2: Model Modules → Step 3: Multi-Agent App → Step 4: Production
   ↓                          ↓                      ↓                         ↓
Test Infrastructure        Bedrock + SageMaker    Model Selection UI      Docker + AWS CDK
Endpoint Validation       Model Wrappers         Loan Assistant          Full Deployment
```

## Prerequisites: Model Endpoint Validation

**⚠️ IMPORTANT**: Before building the multi-agent application, you must validate that your SageMaker endpoints are working correctly. This prevents wasting time on application development only to discover infrastructure issues later.

### Why Validate First?

The validation scripts serve as **prerequisites** that ensure:
- ✅ Your SageMaker endpoints are deployed and accessible
- ✅ Your AWS credentials have the correct permissions
- ✅ The endpoints respond to inference requests correctly
- ✅ You can proceed with confidence to build the application

### What You'll Validate

1. **Agent Model Endpoint**: The reasoning LLM that powers your Strands Agents
2. **XGBoost Model Endpoint**: The predictive model for loan acceptance prediction

---

## Step 1: Environment Setup

### 1.1 Navigate to Workshop Directory

```bash
cd workshop4
```

### 1.2 Run Environment Setup Script

This script creates a Python virtual environment and installs all required dependencies:

```bash
./setup-environment.sh
```

**What this does:**
- Creates a Python virtual environment in `venv/`
- Installs all required packages from `requirements.txt`
- Sets up the development environment

### 1.3 Activate Virtual Environment

**On Windows (GitBash):**
```bash
source venv/Scripts/activate
```

**On Linux/Mac:**
```bash
source venv/bin/activate
```

**Verify activation:**
You should see `(venv)` at the beginning of your command prompt.

### 1.4 Load Environment Variables

```bash
source ~/.bashrc
```

This loads any environment variables you've configured in your `.bashrc` file.

---

## Step 2: Configure AWS Credentials

### 2.1 Set AWS Temporary Credentials

You need to set AWS temporary credentials to access SageMaker endpoints. Follow your organization's process for obtaining temporary credentials.

**Typical process:**
1. Log in to your AWS SSO portal
2. Select your AWS account
3. Click "Command line or programmatic access"
4. Copy the temporary credentials
5. Paste them into your terminal

**Example (your actual values will differ):**
```bash
export AWS_ACCESS_KEY_ID="ASIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
export AWS_REGION="us-east-1"
```

### 2.2 Verify AWS Credentials

Test that your credentials are working:

```bash
aws sts get-caller-identity
```

**Expected output:**
```json
{
    "UserId": "AIDA...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-username"
}
```

---

## Step 3: Configure Endpoint Names

### 3.1 Set Agent Model Endpoint

Set the environment variable for your SageMaker agent model endpoint:

```bash
export SAGEMAKER_MODEL_ENDPOINT="your-agent-model-endpoint-name"
```

**How to find your endpoint name:**
1. Go to AWS Console → SageMaker → Endpoints
2. Find your deployed reasoning model endpoint
3. Copy the endpoint name (e.g., `my-gpt-oss-20b-1-1768457329`)

### 3.1.1 Set Inference Component Name (If Applicable)

If your endpoint uses **Inference Components** (multi-model endpoints), you also need to specify which component to use:

```bash
export SAGEMAKER_INFERENCE_COMPONENT="your-inference-component-name"
```

**How to find your inference component name:**

Run this command to list all inference components for your endpoint:

```bash
aws sagemaker list-inference-components --endpoint-name-equals $SAGEMAKER_MODEL_ENDPOINT --region $AWS_REGION --query 'InferenceComponents[*].[InferenceComponentName,InferenceComponentStatus]' --output table
```

**Example output:**
```
-----------------------------------------------------------------------|                       ListInferenceComponents                       |
+--------------------------------------------------------+------------+
|  base-llmft-gpt-oss-20b-seq4k-gpu-sft-lora-1768457350  |  InService |
|  adapter-my-gpt-oss-20b-1-1768457329-1768457350        |  InService |
+--------------------------------------------------------+------------+
```

Choose the appropriate inference component:
- **Base model**: Use the `base-*` component for the original model
- **Adapter/Fine-tuned**: Use the `adapter-*` component for fine-tuned variants

**Example:**
```bash
export SAGEMAKER_INFERENCE_COMPONENT="adapter-my-gpt-oss-20b-1-1768457329-1768457350"
```

**Note**: If your endpoint doesn't use inference components, you can skip this step. The validation script will work without it.

### 3.2 Set XGBoost Model Endpoint

Set the environment variable for your XGBoost model endpoint:

```bash
export XGBOOST_ENDPOINT_NAME="your-xgboost-endpoint-name"
```

**How to find your endpoint name:**
1. Go to AWS Console → SageMaker → Endpoints
2. Find your deployed XGBoost endpoint
3. Copy the endpoint name (e.g., `xgboost-loan-prediction-endpoint`)

### 3.3 Verify Environment Variables

Check that your environment variables are set correctly:

```bash
echo "Agent Model Endpoint: $SAGEMAKER_MODEL_ENDPOINT"
echo "Inference Component: $SAGEMAKER_INFERENCE_COMPONENT"
echo "XGBoost Endpoint: $XGBOOST_ENDPOINT_NAME"
echo "AWS Region: $AWS_REGION"
```

---

## Step 4: Validate Agent Model Endpoint

### 4.1 Navigate to SageMaker Directory

```bash
cd sagemaker
```

### 4.2 Run Agent Model Validation Script

```bash
uv run validate_agent_endpoint.py
```

**What this script does:**
1. Reads `SAGEMAKER_MODEL_ENDPOINT` and `SAGEMAKER_INFERENCE_COMPONENT` from environment variables
2. Creates a SageMaker Runtime client
3. Sends a test prompt: "What is the capital of France?"
4. Validates the endpoint responds correctly
5. Displays the response

### 4.3 Expected Output

**✅ Success (with inference component):**
```
============================================================
  Agent Model Endpoint Validation
============================================================

🔍 Validating Agent Model Endpoint: my-gpt-oss-20b-1-1768457329
   Region: us-east-1
   Inference Component: adapter-my-gpt-oss-20b-1-1768457329-1768457350
------------------------------------------------------------

📤 Sending test request...
   Prompt: What is the capital of France?
   Max tokens: 50

✅ SUCCESS: Endpoint is responding correctly!

📥 Response:
   {
     "generated_text": "The capital of France is Paris..."
   }

============================================================
✅ Agent model endpoint validation PASSED
============================================================
```

**✅ Success (without inference component):**
```
============================================================
  Agent Model Endpoint Validation
============================================================

🔍 Validating Agent Model Endpoint: your-agent-model-endpoint-name
   Region: us-east-1
------------------------------------------------------------

📤 Sending test request...
   Prompt: What is the capital of France?
   Max tokens: 50

✅ SUCCESS: Endpoint is responding correctly!

📥 Response:
   {
     "generated_text": "The capital of France is Paris..."
   }

============================================================
✅ Agent model endpoint validation PASSED
============================================================
```

**❌ Failure:**
```
============================================================
  Agent Model Endpoint Validation
============================================================

🔍 Validating Agent Model Endpoint: your-agent-model-endpoint-name
   Region: us-east-1
------------------------------------------------------------

📤 Sending test request...
   Prompt: What is the capital of France?
   Max tokens: 50

❌ FAILED: Error validating endpoint
   Error type: ValidationException
   Error message: Could not find endpoint "your-agent-model-endpoint-name"

============================================================
❌ Agent model endpoint validation FAILED
============================================================
```

### 4.4 Troubleshooting

**Common Issues:**

1. **Endpoint not found:**
   - Verify the endpoint name is correct
   - Check that the endpoint is deployed in the correct region
   - Ensure the endpoint status is "InService"

2. **Access denied:**
   - Verify your AWS credentials are valid
   - Check that your IAM role has `sagemaker:InvokeEndpoint` permission
   - Ensure you're using the correct AWS account

3. **Timeout errors:**
   - Check that the endpoint is in "InService" status
   - Verify the endpoint has sufficient capacity
   - Try again after a few minutes

---

## Step 5: Validate XGBoost Model Endpoint

### 5.1 Run XGBoost Validation Script

```bash
uv run validate_xgboost_endpoint.py
```

**What this script does:**
1. Reads `XGBOOST_ENDPOINT_NAME` from environment variables
2. Creates a SageMaker Runtime client
3. Sends sample customer data (59 features in CSV format)
4. Validates the endpoint responds with a prediction
5. Interprets the prediction (Accept/Reject)

### 5.2 Expected Output

**✅ Success:**
```
============================================================
  XGBoost Model Endpoint Validation
============================================================

🔍 Validating XGBoost Model Endpoint: your-xgboost-endpoint-name
   Region: us-east-1
------------------------------------------------------------

📤 Sending test request...
   Sample customer data (59 features)
   Format: CSV (text/csv)

✅ SUCCESS: Endpoint is responding correctly!

📥 Response:
   Raw prediction: 0.234567
   Prediction label: Reject
   Confidence: 23.46%

============================================================
✅ XGBoost model endpoint validation PASSED
============================================================
```

**❌ Failure:**
```
============================================================
  XGBoost Model Endpoint Validation
============================================================

🔍 Validating XGBoost Model Endpoint: your-xgboost-endpoint-name
   Region: us-east-1
------------------------------------------------------------

📤 Sending test request...
   Sample customer data (59 features)
   Format: CSV (text/csv)

❌ FAILED: Error validating endpoint
   Error type: ValidationException
   Error message: Could not find endpoint "your-xgboost-endpoint-name"

============================================================
❌ XGBoost model endpoint validation FAILED
============================================================
```

### 5.3 Understanding the Prediction

The XGBoost model returns a probability score between 0 and 1:
- **Score >= 0.5**: Customer will likely **Accept** the loan offer
- **Score < 0.5**: Customer will likely **Reject** the loan offer

The sample data used in validation represents a customer profile with specific attributes (age, job, marital status, etc.) that have been one-hot encoded into 59 features.

### 5.4 Troubleshooting

**Common Issues:**

1. **Endpoint not found:**
   - Verify the endpoint name is correct
   - Check that the endpoint is deployed as a serverless endpoint
   - Ensure the endpoint status is "InService"

2. **Invalid payload format:**
   - The XGBoost endpoint expects CSV format with exactly 59 features
   - Verify the endpoint was trained with the correct feature set
   - Check the endpoint configuration

3. **Unexpected response format:**
   - The endpoint should return a single float value
   - If you see a different format, check the endpoint's output configuration

---

## Step 6: Validation Complete! ✅

### 6.1 What You've Accomplished

Congratulations! You've successfully validated that:
- ✅ Your SageMaker agent model endpoint is working
- ✅ Your XGBoost model endpoint is working
- ✅ Your AWS credentials have the correct permissions
- ✅ You can invoke both endpoints programmatically

### 6.2 Next Steps

Now that your infrastructure is validated, you're ready to proceed with building the multi-agent application:

1. **Create Configuration Module** - Centralize environment variable management
2. **Build Model Wrappers** - Create Bedrock and SageMaker model modules
3. **Add Model Selection UI** - Implement dropdown to switch between models
4. **Implement Loan Assistant** - Build the loan prediction agent
5. **Deploy to Production** - Package and deploy the complete application

### 6.3 Save Your Configuration

Add your endpoint names to your `.bashrc` file so they persist across sessions:

```bash
echo 'export SAGEMAKER_MODEL_ENDPOINT="your-agent-model-endpoint-name"' >> ~/.bashrc
echo 'export XGBOOST_ENDPOINT_NAME="your-xgboost-endpoint-name"' >> ~/.bashrc
echo 'export AWS_REGION="us-east-1"' >> ~/.bashrc
source ~/.bashrc
```

---

## Architecture Overview

### Multi-Agent System with SageMaker

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Application                     │
│                         (app.py)                             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─────────────────────────────────────────────┐
                 │                                             │
        ┌────────▼────────┐                          ┌────────▼────────┐
        │  Teacher Agent  │                          │  Config Module  │
        │  (Orchestrator) │                          │   (config.py)   │
        └────────┬────────┘                          └─────────────────┘
                 │
                 │ Routes to specialized agents
                 │
    ┌────────────┼────────────┬──────────────┬──────────────┐
    │            │            │              │              │
┌───▼───┐  ┌────▼────┐  ┌────▼────┐  ┌─────▼─────┐  ┌─────▼─────┐
│ Math  │  │ English │  │Language │  │ Computer  │  │   Loan    │
│ Agent │  │  Agent  │  │  Agent  │  │  Science  │  │ Assistant │
└───────┘  └─────────┘  └─────────┘  └───────────┘  └─────┬─────┘
                                                            │
                                                            │
                                                   ┌────────▼────────┐
                                                   │  XGBoost Model  │
                                                   │   (SageMaker    │
                                                   │   Serverless)   │
                                                   └─────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Reasoning LLM Layer                             │
│  ┌──────────────────┐         �┌──────────────────┐         │
│  │  Bedrock Models  │         │ SageMaker Models │         │
│  │  ┌────────────┐  │         │  ┌────────────┐  │         │
│  │  │ Nova Pro   │  │         │  │ Custom LLM │  │         │
│  │  │ Nova Lite  │  │         │  │ Endpoint   │  │         │
│  │  │ Claude 4.5 │  │         │  └────────────┘  │         │
│  │  └────────────┘  │         │                  │         │
│  └──────────────────┘         └──────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Reasoning LLM Layer**: Supports both Bedrock and SageMaker models
2. **Teacher Agent**: Orchestrates routing to specialized agents
3. **Specialized Agents**: Math, English, Language, Computer Science, Loan Assistant
4. **Predictive Model**: XGBoost model for loan acceptance prediction
5. **Configuration Module**: Centralized environment variable management

---

## IMPORTANT: SageMaker Model Compatibility

### ⚠️ OpenAI-Compatible Chat Completion API Required

**The Strands Agents SDK `SageMakerAIModel` class requires SageMaker AI models that support OpenAI-compatible chat completion APIs.**

#### What This Means

Not all models deployed on SageMaker will work with Strands Agents. Your model must:

1. **Support Chat Completion Format**: The model must accept and respond to chat-formatted requests (system messages, user messages, assistant messages)
2. **Use OpenAI-Compatible API**: The model's inference endpoint must implement an OpenAI-compatible interface

#### Validated Models

During development and testing, the following models have been validated:

- ✅ **Mistral-Small-24B-Instruct-2501**: Demonstrated reliable performance across various conversational AI tasks with tool calling support

#### Models That Will NOT Work

- ❌ **Base Language Models** (e.g., Open Llama 7b V2): Will fail with "Template error: template not found" because they lack chat completion API compatibility
- ❌ **Models Without Chat Templates**: Any model that doesn't have a chat template configured

#### Tool Calling Support

Tool calling support varies by model:
- Models like **Mistral-Small-24B-Instruct-2501** have demonstrated reliable tool calling capabilities
- Not all models deployed on SageMaker support this feature
- **Verify your model's capabilities** before implementing tool-based workflows

#### How to Verify Compatibility

Before deploying your multi-agent application:

1. **Check Model Documentation**: Verify the model supports chat completion format
2. **Test with Validation Script**: Use `validate_agent_endpoint.py` to test your endpoint
3. **Review Model Card**: Check if the model explicitly mentions OpenAI compatibility or chat templates

#### Reference

For more information, see the official Strands Agents documentation:
- [SageMaker Model Provider Guide](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/sagemaker/)

---

---

## Reference: Validation Scripts

### Agent Model Validation Script

**Location**: `workshop4/sagemaker/validate_agent_endpoint.py`

**Purpose**: Validates that a SageMaker agent model endpoint is working correctly.

**Environment Variables:**
- `SAGEMAKER_MODEL_ENDPOINT`: Endpoint name (required)
- `AWS_REGION`: AWS region (default: us-east-1)

**Test Payload:**
```json
{
  "inputs": "What is the capital of France?",
  "parameters": {
    "max_new_tokens": 50
  }
}
```

### XGBoost Validation Script

**Location**: `workshop4/sagemaker/validate_xgboost_endpoint.py`

**Purpose**: Validates that a SageMaker XGBoost serverless endpoint is working correctly.

**Environment Variables:**
- `XGBOOST_ENDPOINT_NAME`: Endpoint name (required)
- `AWS_REGION`: AWS region (default: us-east-1)

**Test Payload:**
CSV format with 59 features representing a customer profile:
```
29,2,999,0,1,0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0
```

---

## Coming Soon

The following sections will be added as development progresses:

- **Step 7**: Create Configuration Module
- **Step 8**: Build Bedrock Model Module
- **Step 9**: Build SageMaker Model Module
- **Step 10**: Implement Model Selection UI
- **Step 11**: Build Loan Assistant
- **Step 12**: Integrate into Multi-Agent App
- **Step 13**: Deploy to Production

---

## Getting Help

### Common Issues

1. **"uv: command not found"**
   - Install uv: `pip install uv`
   - Or use: `python validate_agent_endpoint.py`

2. **"SAGEMAKER_MODEL_ENDPOINT environment variable is not set"**
   - Set the environment variable: `export SAGEMAKER_MODEL_ENDPOINT="your-endpoint-name"`

3. **"Could not find endpoint"**
   - Verify the endpoint name is correct
   - Check the endpoint is deployed in the correct region
   - Ensure the endpoint status is "InService"

### Additional Resources

- [SageMaker Endpoints Documentation](https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-model.html)
- [SageMaker Serverless Inference](https://docs.aws.amazon.com/sagemaker/latest/dg/serverless-endpoints.html)
- [Strands Agents Documentation](https://docs.strands.ai/)

---

**Next Steps**: Once validation is complete, proceed to building the configuration module and model wrappers!
