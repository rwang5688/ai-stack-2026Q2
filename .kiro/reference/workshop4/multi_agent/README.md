# Multi-Agent System with Amazon Bedrock

This directory contains the complete implementation of the multi-agent system using Strands Agents SDK with Amazon Bedrock model hosting. This follows the Teacher's Assistant pattern with intelligent query routing to specialized agents.

## Architecture

The system implements a **multi-agent coordination pattern** where specialized agents work together:

- **Teacher's Assistant**: Central orchestrator that routes queries to appropriate specialists
- **Math Assistant**: Handles mathematical calculations and concepts using calculator tool
- **English Assistant**: Processes grammar, writing, and literature using editor and file tools
- **Language Assistant**: Manages translations using HTTP request tool
- **Computer Science Assistant**: Handles programming using python_repl, shell, editor, and file tools
- **General Assistant**: Processes queries outside specialized domains (no specific tools)

## Key Features

- **Tool-Agent Pattern**: Agents wrapped as tools using `@tool` decorator
- **Natural Language Routing**: Intelligent query classification using Amazon Bedrock Nova Pro
- **Cross-Platform Compatibility**: Dynamic tool detection for Windows/Linux/macOS
- **Knowledge Base Integration**: Personal information storage and retrieval using Bedrock Knowledge Base
- **Clean Output Management**: Suppressed intermediate outputs for optimal user experience
- **Agent Type Selection**: Choose between Teacher Agent, Knowledge Base, or Auto-Route

## Files

- `app.py` - Streamlit web interface with agent selection and knowledge base integration
- `teachers_assistant.py` - CLI interface for direct agent interaction
- `math_assistant.py` - Mathematical specialist with calculator integration
- `english_assistant.py` - Language arts specialist with file operations
- `language_assistant.py` - Translation specialist with HTTP capabilities
- `computer_science_assistant.py` - Programming specialist with platform-aware tools
- `no_expertise.py` - General knowledge assistant
- `cross_platform_tools.py` - Cross-platform tool compatibility management

## Prerequisites

- Python 3.12+ with virtual environment activated
- AWS credentials configured with Amazon Bedrock permissions
- Access to Amazon Bedrock Nova Pro model (`us.amazon.nova-pro-v1:0`)
- Strands Agents SDK installed
- Environment variables configured (see setup below)

## Environment Setup

### Required Environment Variables

```bash
export AWS_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_SESSION_TOKEN="your-session-token"  # For temporary credentials
export BYPASS_TOOL_CONSENT="true"  # Skip tool consent prompts
export STRANDS_KNOWLEDGE_BASE_ID="your-knowledge-base-id"  # For knowledge base features
```

### Installation

```bash
# Navigate to workshop directory
cd workshop4

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# OR
source .venv/Scripts/activate  # Windows (Git Bash)

# Install dependencies (if not already done)
pip install -r requirements.txt
```

## Usage

### CLI Interface

```bash
cd workshop4/multi_agent_bedrock
python teachers_assistant.py
```

**Features:**
- Direct command-line interaction
- Clean terminal output with routing confirmation
- Type `exit` to quit

### Web Interface

```bash
cd workshop4/multi_agent_bedrock
streamlit run app.py
```

**Features:**
- User-friendly web interface at `http://localhost:8501`
- Agent type selection (Auto-Route, Teacher Agent, Knowledge Base)
- Conversation history and session management
- Knowledge base integration for personal information storage/retrieval

## Sample Interactions

### Educational Queries (Teacher Agent)

```
"Solve the quadratic equation x^2 + 5x + 6 = 0"
"Write a Python function to check if a string is a palindrome"
"Translate 'Hello, how are you?' to Spanish"
"Help me improve this essay paragraph"
```

### Knowledge Base Operations

```
Storage: "Remember that my birthday is July 25"
Retrieval: "What's my birthday?"
Storage: "My favorite subjects are history, literature, math"
Retrieval: "What are my favorite subjects?"
```

## Knowledge Base Behavior

**Normal AWS Bedrock Knowledge Base behavior:**
- **Store operations**: Complete immediately with success confirmation
- **Indexing delay**: 2-3 minutes for new data to become searchable
- **Retrieve operations**: Only work on fully indexed data
- **Workshop benefit**: Demonstrates real-world cloud service behavior

## Cross-Platform Compatibility

**Tool Availability:**
- **Windows**: Core tools (calculator, http_request, file operations, editor) ✓
- **Linux/macOS**: All tools available including python_repl and shell ✓

The system automatically detects platform capabilities and adapts accordingly.

## Model Configuration

Uses Amazon Bedrock Nova Pro model for enhanced reasoning:

```python
bedrock_model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    temperature=0.3,
)
```

## Troubleshooting

### Common Issues

1. **AWS Credentials**: Verify credentials with `aws sts get-caller-identity`
2. **Model Access**: Ensure access to Nova Pro model in your region
3. **Environment Variables**: Check variables are set with `env | grep AWS`
4. **Knowledge Base**: 2-3 minute delay for new data is normal behavior

### Error Resolution

- **Import Errors**: Ensure all packages installed with `pip install -r requirements.txt`
- **Tool Failures**: Individual tool errors are handled gracefully
- **Connection Errors**: Check internet connectivity and AWS region configuration

## Production Deployment

For production deployment, see the `../deploy_multi_agent_bedrock/` directory which contains:
- Docker containerization
- AWS CDK infrastructure
- ECS Fargate deployment
- Authentication integration

## Related Documentation

- [Main Workshop Guide](../MULTI_AGENT_BEDROCK.md) - Complete workshop documentation
- [Cross-Platform Guide](../CROSS_PLATFORM.md) - Platform compatibility details
- [Deployment Guide](../deploy_multi_agent_bedrock/README.md) - Production deployment