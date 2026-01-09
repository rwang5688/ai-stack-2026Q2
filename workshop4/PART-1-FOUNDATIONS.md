# Part 1: Foundational Modules

Master the building blocks of AI agent development through hands-on modules that teach core concepts, tools, and patterns. These foundational skills prepare you for building sophisticated multi-agent systems.

## Learning Path Overview

Complete these modules in order to build your expertise progressively:

```
Module 1 → Module 2 → Module 3 → Module 4 → Module 5 → Module 6 → Module 8
   ↓         ↓         ↓         ↓         ↓         ↓         ↓
  MCP     Weather   Knowledge  Workflow   Memory    Meta     MCPify
Calculator  Agent     Base      Agent     Agent   Tooling   Lambda
```

**Time Investment**: 6-8 hours total (1-2 hours per module)
**Prerequisites**: [Getting Started Guide](GETTING-STARTED.md) completed

## Module Progression

### 🧮 Module 1: MCP Calculator - Basic Tool Creation
**Focus**: Model Context Protocol (MCP) integration and tool usage
**Time**: 45-60 minutes
**Key Skills**: MCP server creation, agent-tool communication, cross-platform compatibility

Learn how to integrate Strands agents with external tools using the Model Context Protocol. Build a calculator agent that demonstrates the foundation of tool-based AI interactions.

**What You'll Build**: Calculator agent with MCP server providing mathematical operations
**Tools Introduced**: MCP server, FastMCP, calculator functions
**Cross-Platform**: Windows-compatible version available

[**Start Module 1** →](modules/module1/)

---

### 🌤️ Module 2: Weather Agent - External API Integration  
**Focus**: HTTP requests and external service integration
**Time**: 45-60 minutes
**Key Skills**: API integration, JSON processing, error handling, natural language responses

Build a weather forecasting agent that connects with external APIs to provide real-world information through natural language interactions.

**What You'll Build**: Weather agent using National Weather Service API
**Tools Introduced**: `http_request` tool, API workflow patterns
**Cross-Platform**: Works on all platforms without modification

[**Start Module 2** →](modules/module2/)

---

### 📚 Module 3: Knowledge Base Agent - Document Retrieval
**Focus**: Amazon Bedrock Knowledge Base integration and RAG patterns
**Time**: 90-120 minutes (includes AWS resource creation)
**Key Skills**: Knowledge base creation, document storage/retrieval, RAG implementation

Create and integrate Amazon Bedrock Knowledge Bases with Strands agents for document-enhanced responses and personal information storage.

**What You'll Build**: Knowledge base creation automation + retrieval agent
**Tools Introduced**: Bedrock Knowledge Base, S3 integration, memory tool
**AWS Resources**: Creates S3 bucket, OpenSearch Serverless, Knowledge Base

**⚠️ Prerequisites**: AWS credentials with Bedrock, S3, and IAM permissions

[**Start Module 3** →](modules/module3/)

---

### 🔄 Module 4: Workflow Agent - Multi-Agent Coordination
**Focus**: Agent-to-agent communication and workflow orchestration
**Time**: 60-90 minutes
**Key Skills**: Multi-agent architecture, workflow design, agent specialization

Demonstrate how specialized agents work together in sequence to perform complex information processing through coordinated workflows.

**What You'll Build**: Research workflow with Researcher, Analyst, and Writer agents
**Tools Introduced**: Agent coordination patterns, workflow orchestration
**Architecture**: Three-agent sequential processing pipeline

[**Start Module 4** →](modules/module4/)

---

### 🧠 Module 5: Memory Agent - Persistent State Management
**Focus**: Conversational memory and context persistence
**Time**: 60-75 minutes
**Key Skills**: Memory operations, context management, personalized responses

**⚠️ Known Issue**: mem0 library has critical bugs with AWS credential handling. Module works but has authentication limitations with non-default AWS profiles.

Build an agent that maintains context across conversations using persistent memory for personalized AI interactions.

**What You'll Build**: Personal assistant with memory capabilities
**Tools Introduced**: `mem0_memory` tool, semantic search, user isolation
**Memory Types**: Personal information, preferences, contextual data

[**Start Module 5** →](modules/module5/)

---

### 🛠️ Module 6: Meta-Tooling Agent - Dynamic Tool Creation
**Focus**: Runtime tool generation and meta-programming capabilities
**Time**: 75-90 minutes
**Key Skills**: Dynamic tool creation, code generation, runtime extension

**⚠️ Windows Compatibility**: Standard version fails on Windows due to Unix-only dependencies. Windows-compatible version provided.

Explore advanced meta-tooling where agents create new tools dynamically at runtime, expanding their capabilities on demand.

**What You'll Build**: Agent that creates, loads, and uses custom tools dynamically
**Tools Introduced**: `load_tool`, `editor`, dynamic tool generation
**Advanced Concept**: Meta-programming and runtime capability expansion

[**Start Module 6** →](modules/module6/)

---

### ⚡ Module 8: MCPify Lambda - Serverless MCP Tools
**Focus**: Serverless tool deployment and Lambda-based MCP servers
**Time**: 90-120 minutes
**Key Skills**: Serverless architecture, Lambda deployment, MCP server patterns

*Coming Soon* - Learn to deploy MCP tools as serverless Lambda functions for cost-effective, scalable tool execution.

**What You'll Build**: Lambda-based MCP server with AWS deployment
**Tools Introduced**: Serverless MCP patterns, Lambda deployment, cost optimization
**Architecture**: Serverless tool execution with AWS Lambda

*Module 8 will be available after documentation framework completion*

---

## Module Details

### Module 1: Building with Model Context Protocol (MCP)

**AWS Workshop Link**: [Module 1: Building with Model Context Protocol (MCP)](https://catalog.workshops.aws/strands/en-US/module-1-building-calculator-agent-with-mcp-and-strands)

This module demonstrates how to integrate Strands agents with external tools using the Model Context Protocol (MCP). The example creates a simple MCP server that provides calculator functionality and shows how to connect a Strands agent to use these tools through natural language interactions.

**Key Concepts**:
- Creating an MCP server with FastMCP that provides calculator tools
- Starting the server in a background thread using Streamable HTTP transport
- Connecting a Strands agent to the MCP server using MCPClient
- Converting MCP tools into standard AgentTools that the agent can use
- Interactive command-line interface for natural language calculator queries

**How to Run**:
```bash
cd modules/module1
uv run mcp_calculator.py  # Standard version (Linux/macOS)
uv run mcp_calculator_windows.py  # Windows version (if connection issues)
```

**Sample Questions**:
- "What is 16 times 16?"
- "If I have $1000 and spend $246, how much do I have left?"
- "What is 24 multiplied by 7 divided by 3?"

### Module 2: Building Weather Agent with Strands

**AWS Workshop Link**: [Module 2: Building Weather Agent with Strands](https://catalog.workshops.aws/strands/en-US/module-2-building-weather-agent-with-strands)

This module demonstrates how to integrate Strands agents with external APIs using the built-in `http_request` tool. The example creates a weather forecasting agent that connects with the National Weather Service API.

**Key Concepts**:
- Creating an agent with HTTP capabilities using the `http_request` tool
- Multi-step API workflow (get coordinates, then forecast data)
- Processing JSON responses from external APIs
- Converting technical weather data into user-friendly language
- Error handling for HTTP requests and API responses

**How to Run**:
```bash
cd modules/module2
uv run weather_forecaster.py
```

**Sample Questions**:
- "What's the weather like in Seattle?"
- "Will it rain tomorrow in Miami?"
- "Compare the temperature in New York and Chicago this weekend"

### Module 3: Building Knowledge-Base Agent with Strands

**AWS Workshop Link**: [Module 3: Building Knowledge-Base Agent with Strands](https://catalog.workshops.aws/strands/en-US/module-3-building-knowledge-base-agent-with-strands)

This module demonstrates how to create and integrate Amazon Bedrock Knowledge Bases with Strands agents. The module consists of two main steps: first creating a Bedrock Knowledge Base using Python automation, then building a Strands agent that can query and interact with the knowledge base.

**Key Concepts**:
- Automated creation of Amazon Bedrock Knowledge Bases using Python
- S3 bucket creation and data synchronization
- Integration of knowledge bases with Strands agents
- Natural language querying of structured knowledge
- Retrieval-Augmented Generation (RAG) patterns with Bedrock

**Prerequisites**:
- AWS credentials with IAM permissions for Amazon Bedrock, S3, and related services
- Amazon Bedrock region support
- Python 3.12+ with uv package manager

**How to Run**:
```bash
cd modules/module3

# Step 1: Clean up existing resources (REQUIRED)
uv run python cleanup.py

# Step 2: Create new Knowledge Base
uv run create_knowledge_base.py

# Step 3: Configure environment variables
export STRANDS_KNOWLEDGE_BASE_ID=$(aws bedrock-agent list-knowledge-bases --region $AWS_REGION --query 'knowledgeBaseSummaries[].knowledgeBaseId' --output text)

# Step 4: Run the Knowledge Base Agent
uv run knowledge_base_agent.py
```

**Sample Interactions**:
- Store: "I am 41 years old"
- Retrieve: "What is my age?"
- Store: "My favorite color is blue"
- Retrieve: "What do you know about me?"

### Module 4: Building Workflow Agent with Strands

**AWS Workshop Link**: [Module 4: Building Workflow Agent with Strands](https://catalog.workshops.aws/strands/en-US/module-4-building-workflow-agent-with-strands)

This module demonstrates how to create a multi-agent workflow using Strands agents to perform web research, fact-checking, and report generation. The example shows specialized agent roles working together in sequence.

**Key Concepts**:
- Multi-Agent Architecture: Three specialized agents working in sequence
- Agent-to-Agent Communication: Passing information between agents programmatically
- Web Research Capabilities: Using `http_request` tool for information gathering
- Workflow Orchestration: Coordinated execution of multiple processing steps
- Specialized Roles: Researcher, Analyst, and Writer agents with distinct responsibilities

**Agent Architecture**:
- **Researcher Agent**: Information gathering using research tools
- **Analyst Agent**: Fact verification and key insights identification
- **Writer Agent**: Report generation based on analysis

**How to Run**:
```bash
cd modules/module4
uv run agents_workflow.py
```

**Sample Queries**:
- "What are quantum computers?"
- "Lemon cures cancer" (fact-checking)
- "Interest rates have been decreasing recently"

### Module 5: Building Memory Agent with Strands

**AWS Workshop Link**: [Module 5: Building Memory Agent with Strands](https://catalog.workshops.aws/strands/en-US/module-5-building-memory-agent-with-strands)

**⚠️ Known Issue**: This module has a critical bug with the mem0 library's Amazon Bedrock integration. The mem0_memory tool fails with authentication errors even when AWS credentials are properly configured. This affects any non-default credential setup including temporary credentials, named AWS profiles, EC2 instance profiles, AWS SSO authentication, and IAM roles.

This module demonstrates how to create a Strands agent that leverages memory to maintain context across conversations and provide personalized responses.

**Key Concepts**:
- Memory Operations: Storing, retrieving, and listing user-specific information
- Contextual Responses: Using retrieved memories to generate personalized answers
- Tool Chaining: Combining memory retrieval with LLM response generation
- Semantic Search: Finding relevant memories based on context and similarity
- User Isolation: Maintaining separate memory spaces for different users

**Prerequisites**:
- Completed Module 3 (Knowledge Base setup)
- Environment variables configured from Module 3

**How to Run**:
```bash
cd modules/module5
uv run memory_agent.py
```

**Sample Interactions**:
- Store: "My name is J, I am 34 years old, I like seafood, and I have a pet dog"
- Retrieve: "What is my age?"
- List: "Tell me everything that you know about me"

### Module 6: Building Meta Agent with Strands

**AWS Workshop Link**: [Module 6: Building Meta Agent with Strands](https://catalog.workshops.aws/strands/en-US/module-6-building-meta-agent-with-strands)

**⚠️ Windows Compatibility Issue**: The standard version fails on Windows due to Unix-only modules in the `shell` tool. A Windows-compatible version is provided that removes the shell tool while maintaining full meta-tooling functionality.

This module demonstrates Strands Agents' advanced meta-tooling capabilities - the ability of an agent to create, load, and use custom tools dynamically at runtime.

**Key Concepts**:
- Dynamic Tool Creation: Creating new tools at runtime based on natural language descriptions
- Tool Loading: Dynamically registering new tools with the agent's registry
- Code Generation: Automatically generating valid Python tool code following Strands specifications
- Tool Management: Loading, testing, and using newly created tools
- Runtime Extension: Expanding agent capabilities without restarting or reconfiguration

**How to Run**:
```bash
cd modules/module6
uv run meta_tooling.py  # Standard version (Linux/macOS)
uv run meta_tooling_windows.py  # Windows version
```

**Sample Interactions**:
- Create: "Create a tool that counts characters in text"
- Use: "Count the characters in 'Hello, Strands! How are you today?'"

## Cross-Platform Compatibility

### Windows Considerations

Several modules have Windows-specific considerations:

**Module 1**: Windows-compatible version available (`mcp_calculator_windows.py`)
- Uses 127.0.0.1 instead of localhost
- Includes longer startup delays for Windows networking
- Better error handling for connection issues

**Module 5**: mem0 library authentication issues affect all platforms but are more common with Windows credential setups

**Module 6**: Windows-compatible version available (`meta_tooling_windows.py`)
- Removes Unix-only `shell` tool
- Maintains full meta-tooling functionality
- Uses `editor` and `load_tool` for all operations

### Development Environment

**Recommended Setup**:
- **Windows**: Use Git Bash for Unix-like command experience
- **All Platforms**: Use UV package manager for consistent dependency management
- **Virtual Environment**: Shared `workshop4/.venv` for all modules

**Platform-Specific Commands**:
```bash
# Activate virtual environment (same for all platforms in Git Bash)
source .venv/bin/activate

# Windows PowerShell (if needed)
.venv\Scripts\Activate.ps1
```

## Learning Outcomes

After completing the foundational modules, you will have mastered:

### Core Skills
- ✅ **MCP Integration**: Connect agents with external tools and services
- ✅ **API Integration**: Work with external APIs and process JSON responses
- ✅ **Knowledge Management**: Create and query document-based knowledge systems
- ✅ **Workflow Design**: Orchestrate multi-agent collaborative processes
- ✅ **Memory Systems**: Implement persistent context and personalization
- ✅ **Meta-Programming**: Create tools dynamically at runtime

### Advanced Concepts
- ✅ **Cross-Platform Development**: Handle platform-specific compatibility issues
- ✅ **Error Handling**: Implement robust error handling and recovery
- ✅ **Tool Chaining**: Combine multiple tools for complex operations
- ✅ **Agent Specialization**: Design agents for specific domains and tasks
- ✅ **Natural Language Processing**: Convert between technical data and conversational responses

### Production Readiness
- ✅ **AWS Integration**: Work with AWS services (Bedrock, S3, Knowledge Bases)
- ✅ **Security Considerations**: Handle credentials and sensitive data properly
- ✅ **Performance Optimization**: Understand tool selection and efficiency
- ✅ **Debugging Skills**: Troubleshoot agent and tool issues effectively

## Next Steps

After completing the foundational modules, choose your advanced track:

### 🔷 **Bedrock Track** → [Part 2: Multi-Agent with Amazon Bedrock](PART-2-BEDROCK.md)
Build sophisticated multi-agent systems using Amazon Bedrock foundation models with the Teacher's Assistant pattern.

### 🔶 **SageMaker Track** → [Part 3: Multi-Agent with Amazon SageMaker AI](PART-3-SAGEMAKER.md) *(coming soon)*
Build the same multi-agent system using Amazon SageMaker AI (JumpStart) models for comparison and learning.

### 🔧 **Need Help?** → [Reference Guide](REFERENCE.md)
Comprehensive troubleshooting, cross-platform compatibility, and technical reference.

---

**Ready to Begin?** Start with [Module 1: MCP Calculator](modules/module1/) to build your first tool-integrated AI agent!

*These foundational modules provide the essential skills needed for advanced multi-agent system development. Each module builds upon the previous, creating a comprehensive learning experience from basic tool integration to sophisticated agent coordination patterns.*