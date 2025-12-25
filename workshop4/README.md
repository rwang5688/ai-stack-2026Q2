# Workshop 4: AI Application Development on AWS

This workshop provides hands-on experience with AI Application Development on AWS, featuring Strands Agents SDK, Amazon Bedrock, and Amazon SageMaker AI. The workshop is structured in three main components: foundational modules (1-6), and two advanced multi-agent implementations.

## Workshop Components

### 1. Foundational Modules (1-6)
Progressive learning from basic MCP tools to complex agent interactions, preparing students for advanced multi-agent implementations.

**Location**: `workshop4/modules/`
**Spec**: `.kiro/specs/workshop4-modules/`

### 2. Multi-Agent System using Strands Agents and Amazon Bedrock
4-step progressive implementation: CLI → Web UI → Knowledge Base → Production Deployment

**Location**: `workshop4/multi_agent_bedrock/` (planned)
**Spec**: `.kiro/specs/workshop4-multi-agent-bedrock/`

### 3. Multi-Agent System using Strands Agents and Amazon SageMaker AI
Side-by-side analog of the Bedrock version using SageMaker AI (JumpStart) models

**Location**: `workshop4/multi_agent_sagemaker_ai/` (planned)
**Spec**: `.kiro/specs/workshop4-multi-agent-sagemaker-ai/`

## Quick Start

### Prerequisites

- **All Operating Systems**: Python 3.12 or higher
- **Linux**: Git (typically pre-installed)
- **Windows**: Git for Windows (includes Git Bash terminal)

### Environment Setup

See [Cross-Platform Development Guide](CROSS_PLATFORM.md) for detailed information about environment setup and runtime execution across different platforms.

#### Option 1: Automated Setup (Recommended)

```bash
# Make setup script executable (Linux/Git Bash)
chmod +x setup-environment.sh

# Run setup script
./setup-environment.sh
```

#### Option 2: Manual Setup

**With UV (Recommended):**
```bash
# Install UV (same command for all platforms via Git Bash/Terminal)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart terminal

# Create virtual environment
uv venv

# Activate virtual environment (platform-specific)
# Linux/macOS:
source .venv/bin/activate
# Windows (Git Bash):
source .venv/Scripts/activate

# Install dependencies
uv pip install -r requirements.txt
```

**With Standard Python:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (platform-specific)
# Linux/macOS:
source venv/bin/activate
# Windows (Git Bash):
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation

```bash
python -c "import strands_agents; print('Strands Agents SDK installed successfully')"
```

## Workshop Architecture Overview

### Foundational Modules (1-6)

- **Module 1**: MCP Calculator - Basic tool creation and usage
- **Module 2**: Weather Agent - External API integration
- **Module 3**: Knowledge Base Agent - Document retrieval capabilities
- **Module 4**: Agent Workflows - Orchestration patterns
- **Module 5**: Memory Agent - Persistent state management
- **Module 6**: Meta-Tooling Agent - Dynamic tool creation

### Multi-Agent Implementations

Both multi-agent workshops follow the same 4-step progressive architecture:

#### Step 1: CLI Multi-Agent System
- **Teacher's Assistant Pattern**: Central orchestrator routing queries to specialized agents
- **5 Specialized Agents**: Math, English, Language, Computer Science, General
- **Tool-Agent Pattern**: Agents wrapped as tools using @tool decorator
- **Natural Language Routing**: Intelligent query classification and routing

#### Step 2: Streamlit Web Interface
- **Web UI Integration**: User-friendly interface for agent interactions
- **Response Formatting**: Proper display of agent responses
- **Error Handling**: Comprehensive error management and user feedback

#### Step 3: Knowledge Base Enhancement
- **Document Storage**: S3 integration (Bedrock) or compatible system (SageMaker)
- **Knowledge Retrieval**: Enhanced agent capabilities with document access
- **Augmented Responses**: Knowledge-enhanced agent responses

#### Step 4: Production Deployment
- **Memory Integration**: Session persistence and conversation history
- **Containerization**: Docker packaging for production deployment
- **AWS CDK Infrastructure**: ECS Fargate cluster with supporting services
- **Monitoring & Maintenance**: Production-ready operational procedures

## Development Workflow

1. **Always activate the virtual environment first:**
   ```bash
   # Linux/macOS:
   source .venv/bin/activate
   # Windows (Git Bash):
   source .venv/Scripts/activate
   ```

2. **All sample code in this directory shares the same virtual environment**

3. **Use Git Bash on Windows for consistent Linux-like commands**

## Current Implementation Status

### Foundational Modules (workshop4-modules)
- **Module 1**: ✅ COMPLETED - MCP Calculator
- **Module 2**: ✅ COMPLETED - Weather Agent  
- **Module 3**: ✅ COMPLETED - Knowledge Base Agent
- **Module 4**: ✅ COMPLETED - Agent Workflows
- **Module 5**: ✅ COMPLETED WITH KNOWN ISSUE - Memory Agent (mem0 auth issue)
- **Module 6**: ✅ COMPLETED - Meta-Tooling Agent (Windows compatibility resolved)

### Multi-Agent Bedrock (workshop4-multi-agent-bedrock)
- **Status**: 📋 SPEC COMPLETE - Ready for implementation
- **Step 1**: 🔄 PLANNED - CLI Teacher's Assistant system
- **Step 2**: 🔄 PLANNED - Streamlit web interface
- **Step 3**: 🔄 PLANNED - Bedrock Knowledge Base integration
- **Step 4**: 🔄 PLANNED - Production deployment

### Multi-Agent SageMaker AI (workshop4-multi-agent-sagemaker-ai)
- **Status**: 📋 SPEC COMPLETE - Ready for implementation
- **Step 1**: 🔄 PLANNED - CLI Teacher's Assistant system with SageMaker models
- **Step 2**: 🔄 PLANNED - Streamlit web interface
- **Step 3**: 🔄 PLANNED - Knowledge base integration
- **Step 4**: 🔄 PLANNED - Production deployment

## Key Learning Objectives

### Foundational Concepts
- Understanding Strands Agents SDK fundamentals
- MCP tool creation and integration
- Agent workflow orchestration
- Cross-platform development practices

### Advanced Multi-Agent Systems
- Teacher's Assistant pattern implementation
- Tool-Agent Pattern with @tool decorator
- Natural language query routing
- Web interface integration with Streamlit
- Knowledge base enhancement techniques
- Production deployment with AWS CDK, Docker, and ECS Fargate

### Model Integration Approaches
- **Bedrock Track**: Foundation model hosting and inference
- **SageMaker Track**: Custom model training and deployment with JumpStart

## Troubleshooting

### Common Issues

- **Python not found**: Ensure Python 3.12+ is installed and in PATH
- **Git Bash issues**: Install Git for Windows with Git Bash option
- **Package conflicts**: Try creating a fresh virtual environment
- **Module 5 (Memory Agent)**: Known issue with mem0 library and modern AWS auth
- **Module 6 (Windows)**: Use `meta_tooling_windows.py` for Windows compatibility

### Getting Help

- Check [Foundational Modules](MODULES.md) for detailed foundational modules information
- Check [Cross-Platform Development Guide](CROSS_PLATFORM.md) for environment issues
- Review spec documents in `.kiro/specs/` for implementation details
- Verify all prerequisites are installed
- Ensure you're using Git Bash on Windows for consistent behavior

## Next Steps

1. **Complete Foundational Modules**: Work through modules 1-6 to build understanding
2. **Choose Implementation Track**: Select Bedrock or SageMaker AI for advanced multi-agent work
3. **Follow 4-Step Progression**: Build from CLI to production deployment
4. **Compare Approaches**: Explore both tracks to understand different model integration patterns
