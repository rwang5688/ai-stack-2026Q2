# Workshop 4: AI Application Development on AWS

This workshop provides hands-on experience with AI Application Development on AWS, featuring Strands Agents SDK, Amazon Bedrock, and Amazon SageMaker AI. The workshop is structured in three main components: foundational modules (1-6), and two advanced multi-agent implementations.

## Workshop Components

### 1. Foundational Modules (1-6)
Progressive learning from basic MCP tools to complex agent interactions, preparing students for advanced multi-agent implementations.

**Location**: `workshop4/modules/`
**Spec**: `.kiro/specs/workshop4-modules/`
**Documentation**: [Strands Agents SDK Foundational Modules](FOUNDATIONAL_MODULES.md)

### 2. Multi-Agent System using Strands Agents and Amazon Bedrock
6-step progressive implementation: CLI → Web UI → Knowledge Base → Memory/Enhanced UI → Production Deployment → Documentation

**Location**: `workshop4/multi_agent_bedrock/`
**Spec**: `.kiro/specs/workshop4-multi-agent-bedrock/`
**Documentation**: [Building Multi-Agent with Strands Agents SDK using Amazon Bedrock](MULTI_AGENT_BEDROCK.md)

### 3. Multi-Agent System using Strands Agents and Amazon SageMaker AI
Side-by-side analog of the Bedrock version using SageMaker AI (JumpStart) models with 6-step progression

**Location**: `workshop4/multi_agent_sagemaker_ai/` (planned)
**Spec**: `.kiro/specs/workshop4-multi-agent-sagemaker-ai/`
**Documentation**: [Building Multi-Agent with Strands Agents SDK using Amazon SageMaker AI (JumpStart)](MULTI_AGENT_SAGEMAKER_AI.md)

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

Both multi-agent workshops follow the same 6-step progressive architecture:

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

#### Step 4: Memory Integration & Enhanced UI Features
- **Memory Agent Integration**: Session persistence and conversation history using OpenSearch backend
- **Model Selection**: Dropdown for multiple model options (Bedrock: Nova/Claude variants, SageMaker: JumpStart/Custom models)
- **Agent Customization**: Individual toggle controls for specialized teacher agents
- **Agent Type Selection**: Choose between Teacher, Knowledge Base, and Memory agents

#### Step 5: Production Deployment
- **Containerization**: Docker packaging for production deployment with enhanced features
- **AWS CDK Infrastructure**: ECS Fargate cluster with supporting services and memory backend support
- **Monitoring & Maintenance**: Production-ready operational procedures with cost optimization

#### Step 6: Documentation & Workshop Materials
- **Comprehensive Documentation**: Complete setup guides and tutorials for all 6 steps
- **Instructor Resources**: Teaching materials, presentation slides, and assessment criteria
- **Modular Components**: Reusable patterns and customization guides

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
- **Status**: ✅ STEP 3 COMPLETE - Knowledge Base integration implemented with intelligent dual routing
- **Step 1**: ✅ COMPLETED - CLI multi-agent system with 5 specialized agents (Linux/Windows compatible)
- **Step 2**: ✅ COMPLETED - Streamlit web interface
- **Step 3**: ✅ COMPLETED - Knowledge Base integration with personal information storage/retrieval
- **Step 4**: 🔄 READY TO IMPLEMENT - Memory integration & enhanced UI (model selection, agent toggles)
- **Step 5**: 📋 PLANNED - Production deployment (Docker + AWS CDK + ECS Fargate)
- **Step 6**: 📋 PLANNED - Documentation and workshop materials

### Multi-Agent SageMaker AI (workshop4-multi-agent-sagemaker-ai)
- **Status**: � SPECN COMPLETE - Ready for implementation with 6-step approach
- **Step 1**: 🔄 PLANNED - CLI Teacher's Assistant system with SageMaker models
- **Step 2**: 🔄 PLANNED - Streamlit web interface
- **Step 3**: 🔄 PLANNED - Knowledge base integration
- **Step 4**: 🔄 PLANNED - Memory integration & enhanced UI with SageMaker model selection
- **Step 5**: 🔄 PLANNED - Production deployment
- **Step 6**: 🔄 PLANNED - Documentation and workshop materials

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
- **Cross-platform tool compatibility** with dynamic platform detection
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

- Check [Cross-Platform Development Guide](CROSS_PLATFORM.md) for environment issues
- Review spec documents in `.kiro/specs/` for implementation details
- Verify all prerequisites are installed
- Ensure you're using Git Bash on Windows for consistent behavior

## Next Steps

1. **Complete Foundational Modules**: Work through modules 1-6 to build understanding
2. **Choose Implementation Track**: Select Bedrock or SageMaker AI for advanced multi-agent work
3. **Follow 6-Step Progression**: Build from CLI to production deployment with enhanced UI features
4. **Compare Approaches**: Explore both tracks to understand different model integration patterns
