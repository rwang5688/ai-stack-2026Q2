# Part 2: Multi-Agent Application (Local Development)

Run the multi-agent system locally with support for both Amazon Bedrock and Amazon SageMaker AI models. This guide walks you through testing, debugging, and using the Teacher's Assistant application.

## Overview

The `multi_agent` application is a Streamlit web interface that demonstrates:
- **Model Flexibility**: Choose between 5 different models (4 Bedrock + 1 SageMaker)
- **Agent Coordination**: Teacher's Assistant pattern with 5 specialized agents
- **Knowledge Base Integration**: Store and retrieve personal information
- **Agent Type Selection**: Auto-Route, Teacher Agent, or Knowledge Base modes

**Time Investment**: 2-3 hours
**Prerequisites**: 
- [Getting Started](GETTING-STARTED.md) completed (environment + validation)
- [Part 1: Foundations](PART-1-FOUNDATIONS.md) recommended (especially Module 3)

## Architecture

### Multi-Agent System Pattern

| Component | Purpose | Details |
|-----------|---------|---------|
| **Teacher's Assistant** | Central Orchestrator | Routes queries to appropriate specialists |
| **Math Assistant** | Mathematical Expert | Calculator tool for equations and calculations |
| **English Assistant** | Language Arts Expert | Editor and file tools for writing |
| **Language Assistant** | Translation Specialist | HTTP request tool for translations |
| **Computer Science Assistant** | Programming Expert | Python REPL, shell, editor, file tools |
| **General Assistant** | Knowledge Generalist | LLM-only for general knowledge |

### Model Selection

The application supports 5 models via dropdown:

| Model | Provider | Model ID | Use Case |
|-------|----------|----------|----------|
| Amazon Nova 2 Lite | Bedrock | `us.amazon.nova-2-lite-v1:0` | Cost-effective (default) |
| Amazon Nova Pro | Bedrock | `us.amazon.nova-pro-v1:0` | Enhanced reasoning |
| Claude Haiku 4.5 | Bedrock | `us.anthropic.claude-haiku-4-5-*` | Fast responses |
| Claude Sonnet 4.5 | Bedrock | `us.anthropic.claude-sonnet-4-5-*` | Advanced reasoning |
| Custom SageMaker Model | SageMaker | Endpoint-based | OpenaAI chat completion API compatible |

### Agent Type Selection

| Mode | Behavior | Use Case |
|------|----------|----------|
| **Auto-Route** | Automatically determines Teacher vs Knowledge Base | General use (recommended) |
| **Teacher Agent** | Always routes to educational specialists | Educational queries only |
| **Knowledge Base** | Always routes to memory storage/retrieval | Personal information only |

## Prerequisites Check

Before running the application, ensure validation passed:

```bash
cd ~/workspace/ai-stack-2026Q2/workshop4/validation

# 1. Validate SSM parameters
uv run validate_ssm_parameters.py

# 2. Validate SageMaker endpoint (if using SageMaker models)
uv run validate_sagemaker_endpoint.py

# 3. Validate XGBoost endpoint (if using loan assistant feature)
uv run validate_xgboost_endpoint.py
```

All three should show ✅ PASSED.

## Running the Application

### Step 1: Set Environment Variables

```bash
# Required environment variables
export TEACHERS_ASSISTANT_ENV=dev
export AWS_REGION=us-east-1

# AWS credentials (if not using AWS CLI profile)
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_SESSION_TOKEN="your-session-token"  # For temporary credentials

# Bypass tool consent prompts
export BYPASS_TOOL_CONSENT="true"
```

### Step 2: Navigate to Application Directory

```bash
cd ~/workspace/ai-stack-2026Q2/workshop4/multi_agent
```

### Step 3: Run the Application

```bash
streamlit run app.py
```

**Expected Output:**
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

### Step 4: Open in Browser

Navigate to `http://localhost:8501`

## Testing the Application

### Test 1: Model Selection

**Objective**: Verify all models work correctly

**Steps**:
1. Open sidebar → "Model Selection"
2. Select "Amazon Nova 2 Lite" (default)
3. Ask: "What is 2 + 2?"
4. Verify response
5. Repeat for each model:
   - Amazon Nova Pro
   - Claude Haiku 4.5
   - Claude Sonnet 4.5
   - Custom SageMaker Model (if SageMaker endpoint configured)

**Expected**: Each model should respond correctly

### Test 2: Specialized Agents

**Objective**: Verify agent routing works

**Math Assistant**:
```
Query: "Solve the quadratic equation x^2 + 5x + 6 = 0"
Expected: Mathematical solution with steps
```

**English Assistant**:
```
Query: "Help me improve this sentence: Me and him went to store"
Expected: Grammar corrections and suggestions
```

**Language Assistant**:
```
Query: "Translate 'Hello, how are you?' to Spanish"
Expected: "Hola, ¿cómo estás?"
```

**Computer Science Assistant**:
```
Query: "Write a Python function to check if a string is a palindrome"
Expected: Python code with explanation
```

**General Assistant**:
```
Query: "What is the capital of France?"
Expected: "Paris" with additional context
```

### Test 3: Agent Type Selection

**Objective**: Verify agent type modes work

**Auto-Route Mode** (default):
1. Select "Auto-Route" in sidebar
2. Ask: "What is 5 * 7?" → Should route to Teacher Agent
3. Ask: "Remember my birthday is July 25" → Should route to Knowledge Base

**Teacher Agent Mode**:
1. Select "Teacher Agent" in sidebar
2. Ask: "What is 5 * 7?" → Should route to Math Assistant
3. Ask: "Remember my birthday is July 25" → Should still route to Teacher (not Knowledge Base)

**Knowledge Base Mode**:
1. Select "Knowledge Base" in sidebar
2. Ask: "Remember my birthday is July 25" → Should store
3. Ask: "What's my birthday?" → Should retrieve

### Test 4: Knowledge Base Operations

**Objective**: Verify knowledge base storage and retrieval

**Store Information**:
```
1. "Remember that my birthday is July 25"
2. "My favorite color is blue"
3. "I live in Seattle"
```

**Expected**: "✅ I've stored this information in your knowledge base."

**Wait 2-3 Minutes** (for indexing)

**Retrieve Information**:
```
1. "What's my birthday?"
2. "What is my favorite color?"
3. "Where do I live?"
```

**Expected**: Correct information retrieved from knowledge base

**Note**: 2-3 minute indexing delay is normal AWS Bedrock Knowledge Base behavior.

### Test 5: Conversation History

**Objective**: Verify conversation persistence

**Steps**:
1. Ask several questions
2. Verify all appear in chat history
3. Click "Clear Conversation" button
4. Verify history is cleared

## Debugging Common Issues

### Issue 1: Application Won't Start

**Symptoms**: Import errors, module not found

**Solutions**:
```bash
# Verify virtual environment is activated
which python
# Should show: .venv/bin/python or .venv/Scripts/python

# Reinstall dependencies
cd ~/workspace/ai-stack-2026Q2/workshop4
uv pip install -r requirements.txt

# Try again
cd multi_agent
streamlit run app.py
```

### Issue 2: SSM Parameter Errors

**Symptoms**: "Parameter not found" errors

**Solutions**:
```bash
# Verify environment variables
echo $TEACHERS_ASSISTANT_ENV  # Should show: dev
echo $AWS_REGION              # Should show: us-east-1

# Re-run validation
cd ../validation
uv run validate_ssm_parameters.py

# Check CloudFormation stack exists
aws cloudformation describe-stacks --stack-name teachers-assistant-params-dev
```

### Issue 3: SageMaker Model Not Working

**Symptoms**: "SageMaker endpoint not configured" error

**Solutions**:
```bash
# Verify endpoint parameter is set
aws ssm get-parameter --name "/teachers_assistant/dev/sagemaker_model_endpoint"

# Should NOT show: my-sagemaker-model-endpoint (placeholder)
# Should show: your-actual-endpoint-name

# Update if needed
aws ssm put-parameter \
  --name "/teachers_assistant/dev/sagemaker_model_endpoint" \
  --value "your-actual-endpoint-name" \
  --overwrite

# Restart application
```

### Issue 4: Knowledge Base Not Working

**Symptoms**: "Knowledge base ID not found" errors

**Solutions**:
```bash
# Verify knowledge base parameter
aws ssm get-parameter --name "/teachers_assistant/dev/strands_knowledge_base_id"

# Should NOT show: my-strands-knowledge-base-id (placeholder)
# Should show: your-actual-kb-id (e.g., IMW46CITZE)

# Update if needed
aws ssm put-parameter \
  --name "/teachers_assistant/dev/strands_knowledge_base_id" \
  --value "your-actual-kb-id" \
  --overwrite

# Restart application
```

### Issue 5: Agent Not Responding

**Symptoms**: Queries hang or timeout

**Solutions**:
1. Check AWS credentials are valid: `aws sts get-caller-identity`
2. Verify Bedrock model access: `aws bedrock list-foundation-models --region $AWS_REGION`
3. Check CloudWatch logs for errors
4. Try a different model from dropdown
5. Restart application

## Application Features

### Sidebar Information

The sidebar displays:
- **Model Selection**: Dropdown to choose model
- **Active Model**: Current model provider and ID
- **AI Service Details**: Model provider, ID, temperature, knowledge base, region
- **Agent Type Selection**: Auto-Route, Teacher Agent, or Knowledge Base
- **Available Specialists**: List of 5 specialized agents
- **Sample Questions**: Example queries for each agent type

### Configuration

All configuration is managed via SSM Parameter Store:
- `default_model_id`: Default Bedrock model
- `temperature`: Model temperature (0.0-1.0)
- `sagemaker_model_endpoint`: SageMaker endpoint name
- `sagemaker_model_inference_component`: Inference component (if multi-model endpoint)
- `strands_knowledge_base_id`: Knowledge base ID
- `max_results`: Max KB query results
- `min_score`: Min KB relevance score
- `xgboost_model_endpoint`: XGBoost endpoint (for loan assistant)

Update parameters without restarting:
```bash
aws ssm put-parameter --name "/teachers_assistant/dev/temperature" --value "0.5" --overwrite
```

Application will pick up changes on next request.

## Next Steps

Once you've successfully tested the local application:

1. **Explore Features**: Try different models, agents, and knowledge base operations
2. **Customize**: Modify system prompts, add new agents, adjust parameters
3. **Deploy**: Proceed to [Part 3: Production Deployment](PART-3-DEPLOY-MULTI-AGENT.md)

## Key Learnings

### Model Flexibility
- Single codebase supports multiple model providers
- Dynamic model selection without code changes
- Graceful fallback when endpoints unavailable

### Agent Coordination
- Natural language routing to appropriate specialists
- Tool-Agent pattern for clean abstraction
- Cross-platform tool compatibility

### Knowledge Base Integration
- Dual functionality: teaching + memory
- Intelligent query routing (educational vs personal)
- Real-world cloud service behavior (indexing delay)

### Configuration Management
- SSM Parameter Store for centralized config
- Dynamic updates without restarts
- Environment-based parameter paths

---

**Application Testing Complete!** 🎉

You've successfully run and tested the multi-agent application locally. Proceed to [Part 3: Production Deployment](PART-3-DEPLOY-MULTI-AGENT.md) to deploy to AWS.
