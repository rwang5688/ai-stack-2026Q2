# Agentic AI with Strands (Agents) SDK and (Amazon Bedrock) AgentCore Workshop Modules

This document provides detailed information, including sample code and queries, from the modules leading up to Module 7 in the [Agentic AI with Strands (Agents) SDK and (Amazon Bedrock AgentCore)](https://catalog.workshops.aws/strands/en-US) workshop.  These published workshop modules will teach you how to use Strands Agents SDK to build and deploy agentic AI systems.

---

## Environment Setup

See [Cross-Platform Develompent Guide](CROSS_PLATFORM.md) for detailed information about environment setup and runtime execution across different platforms.

**⚠️ AWS Credentials Required:** All examples require AWS credentials with Amazon Bedrock permissions. Ensure your runtime environment has proper IAM permissions to invoke Bedrock models.

**⚠️ Change working directory to the `workshop4` directory:** All examples assume you have changed your working directory to the `workshop4` directory.

---

## Module 1: Building with Model Context Protocol (MCP)

**AWS Workshop Link:** [Module 1: Building with Model Context Protocol (MCP)](https://catalog.workshops.aws/strands/en-US/module-1-building-calculator-agent-with-mcp-and-strands)

**Strands Agents Docs on GitHub Link:** [mcp_calculator.py](https://github.com/strands-agents/docs/blob/main/docs/examples/python/mcp_calculator.py)

### Description

This module demonstrates how to integrate Strands agents with external tools using the Model Context Protocol (MCP). The example creates a simple MCP server that provides calculator functionality (add, subtract, multiply, divide) and shows how to connect a Strands agent to use these tools through natural language interactions.

The code showcases:
- Creating an MCP server with FastMCP that provides calculator tools
- Starting the server in a background thread using Streamable HTTP transport
- Connecting a Strands agent to the MCP server using MCPClient
- Converting MCP tools into standard AgentTools that the agent can use
- Interactive command-line interface for natural language calculator queries

### How to Run

**Standard Version (Linux/macOS):**
```bash
cd modules/module1
uv run mcp_calculator.py
```

**Windows GitBash (if connection issues occur):**
```bash
cd modules/module1
uv run mcp_calculator_windows.py
```

### Sample Questions

Try these example queries when the calculator agent is running:

1. **Basic arithmetic:**
   ```
   What is 16 times 16?
   ```

2. **Word problems:**
   ```
   If I have $1000 and spend $246, how much do I have left?
   ```

3. **Mathematical expressions:**
   ```
   What is pi by 4?
   ```

4. **Complex calculations:**
   ```
   What is 24 multiplied by 7 divided by 3?
   ```

5. **Simple operations:**
   ```
   What is 125 plus 375?
   ```

Type `exit` to quit the application, or press `Ctrl+C` to stop the program.

### Windows Troubleshooting

If you encounter `ReadError` or `MCPClientInitializationError` on Windows:

1. **Use the Windows-compatible version** (recommended):
   ```bash
   uv run mcp_calculator_windows.py
   ```

2. **Check port availability**:
   ```bash
   netstat -an | findstr :8000
   ```

3. **Run as Administrator** if needed:
   - Right-click Git Bash → "Run as administrator"

4. **Windows Firewall**: Add Python to firewall exceptions if blocked

5. **Alternative troubleshooting**:
   - The Windows version uses 127.0.0.1 instead of localhost
   - Includes longer startup delays for Windows networking
   - Better error handling for connection issues

---

## Module 2: Building Weather Agent with Strands

**AWS Workshop Link:** [Module 2: Building Weather Agent with Strands](https://catalog.workshops.aws/strands/en-US/module-2-building-weather-agent-with-strands)

**Strands Agents Docs on GitHub Link:** [weather_forecaster.py](https://github.com/strands-agents/docs/blob/main/docs/examples/python/weather_forecaster.py)


### Description

This module demonstrates how to integrate Strands agents with external APIs using the built-in `http_request` tool. The example creates a weather forecasting agent that connects with the National Weather Service API to retrieve and present weather information through natural language interactions.

The code showcases:
- Creating an agent with HTTP capabilities using the `http_request` tool
- Multi-step API workflow (get coordinates, then forecast data)
- Processing JSON responses from external APIs
- Converting technical weather data into user-friendly language
- Error handling for HTTP requests and API responses
- Interactive command-line interface for weather queries

### How to Run

**All Platforms (Linux/macOS/Windows):**
```bash
cd modules/module2
uv run weather_forecaster.py
```

*Note: This example works cross-platform without modification as it uses the standard Strands `http_request` tool.*

### Sample Questions

Try these example queries when the weather agent is running:

1. **Basic location queries:**
   ```
   What's the weather like in Seattle?
   ```

2. **Future weather:**
   ```
   Will it rain tomorrow in Miami?
   ```

3. **Comparative queries:**
   ```
   Compare the temperature in New York and Chicago this weekend
   ```

4. **Specific conditions:**
   ```
   What's the forecast for San Francisco this week?
   ```

5. **General weather questions:**
   ```
   Should I bring an umbrella in Boston today?
   ```

### API Details

This example uses the **National Weather Service API**:
- **No API key required** - completely free to use
- **US locations only** - covers all United States locations
- **Multi-step process**: First gets coordinates/grid info, then retrieves forecast
- **Rich data**: Temperature, precipitation, wind, detailed conditions
- **Production ready**: Reliable government API service

### Technical Implementation

The agent handles a sophisticated multi-step workflow:

1. **Location Resolution**: Converts location names to coordinates using NWS points API
2. **Forecast Retrieval**: Uses returned forecast URL to get detailed weather data
3. **Data Processing**: Transforms technical weather data into conversational responses
4. **Natural Language**: Presents information in user-friendly format with context

Type `exit` to quit the application, or press `Ctrl+C` to stop the program.

---

## Module 3: Building Knowledge-Base Agent with Strands

**AWS Workshop Link:** [Module 3: Building Knowledge-Base Agent with Strands](https://catalog.workshops.aws/strands/en-US/module-3-building-knowledge-base-agent-with-strands)

### Description

This module demonstrates how to create and integrate Amazon Bedrock Knowledge Bases with Strands agents. The module consists of two main steps: first creating a Bedrock Knowledge Base using Python automation, then building a Strands agent that can query and interact with the knowledge base through natural language.

The module showcases:
- Automated creation of Amazon Bedrock Knowledge Bases using Python
- S3 bucket creation and data synchronization
- Integration of knowledge bases with Strands agents
- Natural language querying of structured knowledge
- Retrieval-Augmented Generation (RAG) patterns with Bedrock

### ⚠️ Prerequisites

- **AWS credentials** with IAM permissions for Amazon Bedrock, S3, and related services
- **Amazon Bedrock region support** - ensure you're in a region that supports Amazon Bedrock Knowledge Bases
- **Python 3.12+** with uv package manager
- **Processing Time**: Knowledge Base creation takes approximately 7-9 minutes to complete

### Step 1: Create Bedrock Knowledge Base with Python

This step automates the creation of an Amazon Bedrock Knowledge Base using a Python script that handles the entire setup process.

#### 🧹 Important: Cleanup First Workflow

**CRITICAL**: Always run cleanup before creating a new Knowledge Base to prevent IAM policy conflicts.

```bash
# Navigate to module directory
cd modules/module3

# STEP 1: Clean up any existing resources (REQUIRED)
uv run cleanup.py

# STEP 2: Create new Knowledge Base
uv run create_knowledge_base.py
```

**Why cleanup first?**
- Prevents "policy already exists" errors
- Ensures IAM roles and policies align with S3, OpenSearch, and Bedrock resources
- Removes orphaned policies from previous runs
- Guarantees clean resource state for reliable creation

**What cleanup removes:**
- Knowledge Bases and data sources
- S3 buckets (bedrock-kb-bucket-*)
- OpenSearch Serverless collections
- IAM roles (AmazonBedrockExecutionRoleForKnowledgeBase_*)
- IAM policies (AmazonBedrock*PolicyForKnowledgeBase_*)

#### What the Script Does:
- Downloads sample knowledge base files (pets-kb-files.zip)
- Creates an S3 bucket with random suffix for data storage
- Sets up an Amazon Bedrock Knowledge Base with custom data source
- Synchronizes the S3 bucket with the Knowledge Base
- Configures vector embeddings and search capabilities

#### How to Run:

If are not already in module directory, navigate to module directory.

**All Platforms (Linux/macOS/Windows):**
```bash
# Navigate to module directory
cd modules/module3
```

Once you have changed to module directory, run the knowledge base creation script.

**All Platforms (Linux/macOS/Windows):**
```bash
# Set AWS region (if not already set)
export AWS_DEFAULT_REGION="$AWS_REGION"

# Run the knowledge base creation script
uv run create_knowledge_base.py
```

### Step 2: Build Knowledge-Base Agent with Strands

This step demonstrates how to create a Strands agent that can intelligently store and retrieve information from the Amazon Bedrock Knowledge Base created in Step 1.

#### Setup Environment Variables

First, configure the required environment variables with the Knowledge Base ID and OpenSearch endpoint:

```bash
# Get Knowledge Base ID and OpenSearch details
export STRANDS_KNOWLEDGE_BASE_ID=$(aws bedrock-agent list-knowledge-bases --region $AWS_REGION --query 'knowledgeBaseSummaries[].knowledgeBaseId' --output text)
export OPENSEARCH_COLLECTION_ID=$(aws opensearchserverless list-collections --query "collectionSummaries[].id" --output text)
export OPENSEARCH_ENDPOINT=$(aws opensearchserverless batch-get-collection --ids $OPENSEARCH_COLLECTION_ID --query 'collectionDetails[].collectionEndpoint' --output text)
export OPENSEARCH_HOST="${OPENSEARCH_ENDPOINT#https://*}"

# Persist to bashrc for future sessions
echo "export STRANDS_KNOWLEDGE_BASE_ID=\"${STRANDS_KNOWLEDGE_BASE_ID}\"" >> ~/.bashrc
echo "export OPENSEARCH_HOST=\"$OPENSEARCH_HOST\"" >> ~/.bashrc
```

#### How to Run

**All Platforms (Linux/macOS/Windows):**
```bash
cd modules/module3
uv run knowledge_base_agent.py
```

#### What the Agent Does

The knowledge base agent demonstrates a **code-defined workflow** that:

1. **Intent Classification**: Uses LLM to determine if user wants to store or retrieve information
2. **Conditional Execution**: Routes to either storage or retrieval based on intent
3. **Tool Chaining**: For retrieval, combines memory search with LLM response generation

**Key Features:**
- **Deterministic behavior** through explicit code control
- **Optimized tool usage** with precise parameter tuning
- **Specialized prompts** for classification and response generation
- **Memory tool** for storing/retrieving with semantic similarity
- **LLM integration** for natural language processing

#### Sample Interactions

**Storing Information:**
```
User: I am 41 years old
Agent: I've stored this information.
```

**Retrieving Information:**
```
User: What is my age?
Agent: You're 41 years old.
```

**Other Examples:**
- Store: "My favorite color is blue"
- Store: "I work as a software engineer"
- Retrieve: "What do you know about me?"
- Retrieve: "Tell me about my preferences"

#### Technical Implementation

The agent uses two primary tools:

- **`memory`**: Store/retrieve information with semantic search capabilities
- **`use_llm`**: Intent classification and response generation

**Workflow Process:**
1. User query → Intent classification (store vs retrieve)
2. If store: Save content to knowledge base
3. If retrieve: Search knowledge base → Generate natural response

#### Troubleshooting

**If retrievals fail:**
- Decrease `min_score` value in the code for more lenient matching
- Increase `min_score` to reduce hallucinations and improve precision

**Verify setup:**
- Check environment variables: `echo $STRANDS_KNOWLEDGE_BASE_ID`
- Confirm Knowledge Base exists in Amazon Bedrock console
- Verify OpenSearch collection is accessible

### Troubleshooting

**Common Issues:**
- **Region Support**: Ensure your AWS region supports Amazon Bedrock Knowledge Bases
- **Permissions**: Verify IAM permissions for Amazon Bedrock, S3, and IAM operations
- **Timeout**: Knowledge Base creation can take 7-9 minutes - be patient
- **S3 Bucket Names**: Script handles random suffix generation to avoid naming conflicts

**Error Resolution:**
- Check AWS credentials: `aws sts get-caller-identity`
- Verify region: `echo $AWS_REGION`
- Check Amazon Bedrock availability in your region
- Review CloudTrail logs for detailed error information

---

## Module 4: Building Workflow Agent with Strands

**AWS Workshop Link:** [Module 4: Building Workflow Agent with Strands](https://catalog.workshops.aws/strands/en-US/module-4-building-workflow-agent-with-strands)

### Description

This module demonstrates how to create a multi-agent workflow using Strands agents to perform web research, fact-checking, and report generation. The example shows specialized agent roles working together in sequence to process complex information through agent-to-agent communication.

The module showcases:
- **Multi-Agent Architecture**: Three specialized agents working in sequence
- **Agent-to-Agent Communication**: Passing information between agents programmatically
- **Web Research Capabilities**: Using `http_request` tool for information gathering
- **Workflow Orchestration**: Coordinated execution of multiple processing steps
- **Output Management**: Clean user experience with suppressed intermediate outputs
- **Specialized Roles**: Researcher, Analyst, and Writer agents with distinct responsibilities

### Agent Architecture

The Research Assistant implements a **three-agent workflow** where each agent has a specific role:

| Agent | Role | Responsibility | Tools Used |
|-------|------|----------------|------------|
| **Researcher Agent** | Information Gathering | Gathers information from web sources using research tools | `http_request` |
| **Analyst Agent** | Fact Verification | Verifies facts and identifies key insights from research findings | None (LLM only) |
| **Writer Agent** | Report Generation | Creates final reports based on analysis | None (LLM only) |

### Key Features

- **Complexity**: Intermediate level multi-agent coordination
- **Interaction**: Command line interface with clean progress feedback
- **Tools**: HTTP request capabilities for web research
- **Communication**: Sequential agent-to-agent information passing
- **Output**: Suppressed intermediate outputs for clean user experience

### How to Run

**All Platforms (Linux/macOS/Windows):**
```bash
cd modules/module4
uv run agents_workflow.py
```

### Sample Queries and Expected Responses

#### Query 1: Research Questions
```
What are quantum computers?
```

**Expected Response Structure:**
- Fact-check confirmation of quantum computing claims
- Key insights about quantum mechanics utilization, qubits, and applications
- Current development stage and challenges
- Source reliability assessment
- Comprehensive summary with technical accuracy

#### Query 2: Fact-Checking Claims
```
Lemon cures cancer
```

**Expected Response Structure:**
- **Factual Claims Accuracy**: False rating with explanation
- **Key Insights**: Nutritional benefits vs. medical claims
- **Cancer Treatment**: Standard medical approaches
- **Misinformation Risks**: Dangers of unverified claims
- **Source Reliability**: References to authoritative health organizations

#### Query 3: Current Events Analysis
```
Interest rates have been decreasing recently
```

**Expected Response Structure:**
- **Claim Accuracy**: Verification with data corrections if needed
- **Research Insights**: Economic indicators and market implications
- **Source Reliability**: Federal Reserve data credibility assessment
- **Summary**: Contextualized findings with economic analysis

### Technical Implementation

#### 1. Agent Initialization
Each agent is created with specialized system prompts:

```python
# Researcher Agent with web capabilities
researcher_agent = Agent(
    system_prompt=(
        "You are a Researcher Agent that gathers information from the web. "
        "1. Determine if the input is a research query or factual claim "
        "2. Use your research tools (http_request, retrieve) to find relevant information "
        "3. Include source URLs and keep findings under 500 words"
    ),
    callback_handler=None,  # Suppresses intermediate output
    tools=[http_request]
)

# Analyst Agent for verification
analyst_agent = Agent(
    system_prompt=(
        "You are an Analyst Agent that verifies information. "
        "1. For factual claims: Rate accuracy from 1-5 and correct if needed "
        "2. For research queries: Identify 3-5 key insights "
        "3. Evaluate source reliability and keep analysis under 400 words"
    ),
    callback_handler=None
)

# Writer Agent for final reports
writer_agent = Agent(
    system_prompt=(
        "You are a Writer Agent that creates clear reports. "
        "1. For fact-checks: State whether claims are true or false "
        "2. For research: Present key insights in a logical structure "
        "3. Keep reports under 500 words with brief source mentions"
    ),
    callback_handler=None
)
```

#### 2. Workflow Orchestration
The workflow coordinates information flow between agents:

```python
def run_research_workflow(user_input):
    # Step 1: Research phase
    researcher_response = researcher_agent(
        f"Research: '{user_input}'. Use your available tools to gather information from reliable sources."
    )
    research_findings = str(researcher_response)
    
    # Step 2: Analysis phase
    analyst_response = analyst_agent(
        f"Analyze these findings about '{user_input}':\n\n{research_findings}"
    )
    analysis = str(analyst_response)
    
    # Step 3: Report generation
    final_report = writer_agent(
        f"Create a report on '{user_input}' based on this analysis:\n\n{analysis}"
    )
    
    return final_report
```

#### 3. Output Management
- **Suppressed Intermediate Outputs**: `callback_handler=None` prevents verbose agent outputs
- **Clean Progress Feedback**: Simple print statements show workflow progress
- **Final Result Only**: Users see only the Writer Agent's final report

### Tools Overview

#### `http_request` Tool
The `http_request` tool enables web information gathering:
- **HTTP Methods**: Supports GET, POST, PUT, DELETE
- **URL Encoding**: Handles proper URL formatting
- **Response Parsing**: Returns structured data from web sources
- **Error Handling**: Manages network timeouts and connection issues

*Note: Understanding implementation details is not crucial for grasping multi-agent workflow concepts.*

### Troubleshooting

#### Common Issues

**Network Errors:**
```
urllib3.exceptions.ProtocolError: Response ended prematurely
```
- **Cause**: API throttling or network connectivity issues
- **Solution**: Wait a moment and retry the query
- **Alternative**: Try a different, simpler query

**Connection Timeouts:**
- **Cause**: Slow network or overloaded web services
- **Solution**: Check internet connection and retry
- **Workaround**: Use shorter, more specific queries

#### Performance Tips
- **Query Length**: Keep queries concise for faster processing
- **Network**: Ensure stable internet connection for web research
- **Patience**: Complex research queries may take 30-60 seconds to complete

### Extending the Example

**Suggested Enhancements:**
1. **User Feedback Loop**: Allow users to request more detail after receiving reports
2. **Parallel Research**: Modify Researcher Agent to gather from multiple sources simultaneously
3. **Visual Content**: Enhance Writer Agent to include charts or structured data
4. **Web Interface**: Build a web UI for the workflow
5. **Session Memory**: Implement memory so the system remembers previous research sessions
6. **Source Validation**: Add additional fact-checking against multiple authoritative sources

### Usage Notes
- Type `exit` to quit the application
- Press `Ctrl+C` to stop the program
- Avoid entering sensitive or PII data in queries
- Be patient with complex research queries - they may take time to process

---

## Module 5: Building Memory Agent with Strands

**AWS Workshop Link:** [Module 5: Building Memory Agent with Strands](https://catalog.workshops.aws/strands/en-US/module-5-building-memory-agent-with-strands)

### Description

This module demonstrates how to create a Strands agent that leverages memory from mem0.ai to maintain context across conversations and provide personalized responses. The example showcases how to store, retrieve, and utilize memories to create more intelligent and contextual AI interactions with persistent memory capabilities.

The module showcases:
- **Memory Operations**: Storing, retrieving, and listing user-specific information
- **Contextual Responses**: Using retrieved memories to generate personalized answers
- **Tool Chaining**: Combining memory retrieval with LLM response generation
- **Semantic Search**: Finding relevant memories based on context and similarity
- **User Isolation**: Maintaining separate memory spaces for different users
- **Dual Memory Support**: Compatible with both mem0.ai and Amazon Bedrock AgentCore Memory

### Agent Architecture

The Memory Agent implements a **single agent with memory management** approach:

| Component | Role | Responsibility | Tools Used |
|-----------|------|----------------|------------|
| **Memory Agent** | Personal Assistant | Maintains context by remembering user details and preferences | `mem0_memory`, `use_agent` |

### Key Features

- **Complexity**: Intermediate level memory management
- **Interaction**: Command line interface with memory operations
- **Tools**: Memory storage/retrieval and LLM capabilities
- **Memory Types**: User-specific information, preferences, and contextual data
- **Persistence**: Information stored across conversation sessions

### How to Run

**Prerequisites:**
Ensure the `OPENSEARCH_HOST` environment variable is properly set:

```bash
# Check if environment variable is set
tail -3 ~/.bashrc
source ~/.bashrc
echo "OPENSEARCH_HOST=\"$OPENSEARCH_HOST\""

# Set user ID (optional, defaults to 'J')
export USER_ID="J"  # Feel free to change this to another name
```

**All Platforms (Linux/macOS/Windows):**
```bash
cd modules/module5
uv run memory_agent.py
```

### Sample Interactions

#### Interaction 1: Storing Information
```
User: My name is J, I am 34 years old, I like seafood, and I have a pet dog
Agent: Hello J! I've stored your information. How can I assist you further?
```

#### Interaction 2: Retrieving Information
```
User: What is my age?
Agent: You are 34 years old. Is there anything else you would like to know?
```

#### Interaction 3: Listing All Memories
```
User: Tell me everything that you know about me
Agent: Here's everything I know about you:
- Your name is J
- You are 34 years old
- You like seafood
- You have a pet dog
```

### Technical Implementation

#### Memory Operations Workflow

The agent supports multiple memory operations through the `mem0_memory` tool:

1. **Store**: Save new information with user association
2. **Retrieve**: Search for relevant memories using semantic similarity
3. **List**: Display all stored memories for a user
4. **Get**: Retrieve specific memory by ID
5. **Delete**: Remove specific memories
6. **History**: View memory modification history

#### Tool Chaining Process

The memory agent demonstrates sophisticated tool chaining:

```
┌───────────────┐     ┌───────────────────────┐     ┌───────────────┐
│               │     │                       │     │               │
│  User Query   │────▶│  memory() Retrieval   │────▶│  use_agent()  │────▶ Response
│               │     │                       │     │               │
└───────────────┘     └───────────────────────┘     └───────────────┘
                       (Finds relevant memories)     (Generates natural
                                                     language answer)
```

#### Memory Configuration

The agent supports multiple memory backends:

**mem0.ai Backend (Default):**
- Uses FAISS for local vector storage
- Configurable embeddings and LLM models
- Environment variable configuration

**Amazon Bedrock AgentCore Memory:**
- Enterprise-grade memory management
- Requires memory_id, actor_id, session_id, and namespace
- Integrated with AWS services

#### System Prompt Specialization

The agent uses specialized prompts for different operations:

```python
MEMORY_SYSTEM_PROMPT = """You are a personal assistant that maintains context by remembering user details.

Capabilities:
- Store new information using mem0_memory tool (action="store")
- Retrieve relevant memories (action="retrieve")
- List all memories (action="list")
- Provide personalized responses

Key Rules:
- Always include user_id in tool calls
- Be conversational and natural in responses
- Format output clearly
- Acknowledge stored information
- Only share relevant information
- Politely indicate when information is unavailable
"""
```

### Memory Requirements

**User/Agent Association:**
- Most operations require either `user_id` or `agent_id`
- Ensures proper data isolation between users
- Maintains privacy and context separation

**Required for:**
- Storing new memories
- Listing all memories
- Retrieving memories via semantic search

**Not required for:**
- Getting specific memory by ID
- Deleting specific memory
- Getting memory history

### Demo Mode

The agent includes a built-in demo with pre-populated memories:

```bash
# Run demo mode
> demo
```

**Demo memories include:**
- Personal information (name, age)
- Preferences (travel, accommodation)
- Hobbies (hiking, photography)
- Pets (dog named Max)
- Food preferences (Italian cuisine)

### Extending the Example

**Suggested Enhancements:**
1. **Memory Categories**: Implement tagging or categorization for better organization
2. **Memory Prioritization**: Add importance levels to emphasize critical information
3. **Memory Expiration**: Implement time-based relevance for changing information
4. **Multi-User Support**: Enhanced management for multiple simultaneous users
5. **Memory Visualization**: Create visual interface for browsing and managing memories
6. **Proactive Memory Usage**: Agent suggests relevant memories in conversations
7. **Memory Analytics**: Track memory usage patterns and effectiveness

### Usage Notes
- Type `exit` to quit the application
- Type `demo` to run the demonstration mode
- Press `Ctrl+C` to stop the program
- Avoid entering sensitive or PII data in queries
- Memory persists across sessions when properly configured

---

## Module 6: Building Meta Agent with Strands

**AWS Workshop Link:** [Module 6: Building Meta Agent with Strands](https://catalog.workshops.aws/strands/en-US/module-6-building-meta-agent-with-strands)

### Description

This module demonstrates Strands Agents' advanced meta-tooling capabilities - the ability of an agent to create, load, and use custom tools dynamically at runtime. Meta-tooling refers to an AI system's capability to create new tools on demand rather than being limited to a predefined set of capabilities.

The module showcases:
- **Dynamic Tool Creation**: Creating new tools at runtime based on natural language descriptions
- **Tool Loading**: Dynamically registering new tools with the agent's registry
- **Code Generation**: Automatically generating valid Python tool code following Strands specifications
- **Tool Management**: Loading, testing, and using newly created tools
- **Runtime Extension**: Expanding agent capabilities without restarting or reconfiguration
- **Intelligent Tool Detection**: Distinguishing between tool creation and tool usage requests

### Agent Architecture

The Meta-Tooling Agent implements a **single agent with dynamic capability expansion**:

| Component | Role | Responsibility | Tools Used |
|-----------|------|----------------|------------|
| **Meta Agent** | Tool Builder | Creates, loads, and manages custom tools dynamically | `load_tool`, `shell`, `editor` |

### Key Features

- **Complexity**: Advanced level meta-programming
- **Interaction**: Command line interface with tool creation capabilities
- **Core Concept**: Meta-Tooling (Dynamic Tool Creation)
- **Key Technique**: Runtime Tool Generation
- **Extensibility**: Unlimited capability expansion through tool creation

### How to Run

**All Platforms (Linux/macOS/Windows):**
```bash
cd modules/module6
uv run meta_tooling.py
```

### Tools Used Overview

The meta-tooling agent uses three primary tools to create and manage dynamic tools:

#### 1. `load_tool`
- **Purpose**: Dynamic loading of Python tools at runtime
- **Capabilities**: 
  - Registering new tools with agent's registry
  - Hot-reloading of capabilities
  - Validating tool specifications before loading

#### 2. `editor`
- **Purpose**: Creation and modification of tool code files
- **Capabilities**:
  - Syntax highlighting and code creation
  - Precise string replacements in existing tools
  - Code insertion at specific locations
  - Finding and navigating code sections
  - Creating backups with undo capability

#### 3. `shell`
- **Purpose**: Execute shell commands for tool management
- **Capabilities**:
  - Debug tool creation and execution problems
  - Sequential or parallel command execution
  - Working directory context management

### Meta-Tooling Implementation

#### Key Components

**1. Agent Initialization with Meta-Tools**
```python
agent = Agent(
    model=bedrock_model,
    system_prompt=TOOL_BUILDER_SYSTEM_PROMPT,
    tools=[load_tool, shell, editor]
)
```

**2. Standardized Tool Structure**
The system enforces a strict tool specification format:

```python
from typing import Any
from strands.types.tools import ToolUse, ToolResult

TOOL_SPEC = {
    "name": "tool_name",  # Must match function name
    "description": "What the tool does",
    "inputSchema": {  # Exact capitalization required
        "json": {
            "type": "object",
            "properties": {
                "param_name": {
                    "type": "string",
                    "description": "Parameter description"
                }
            },
            "required": ["param_name"]
        }
    }
}

def tool_name(tool_use: ToolUse, **kwargs: Any) -> ToolResult:
    tool_use_id = tool_use["toolUseId"]
    param_value = tool_use["input"]["param_name"]
    
    # Process inputs
    result = param_value  # Replace with actual processing
    
    return {
        "toolUseId": tool_use_id,
        "status": "success",
        "content": [{"text": f"Result: {result}"}]
    }
```

#### Tool Creation Workflow

**Autonomous Tool Creation Process:**
1. **Natural Language Analysis**: Parse user request to determine tool requirements
2. **Code Generation**: Generate complete Python code following Strands specifications
3. **File Creation**: Use `editor` tool to write code to appropriately named file
4. **Tool Loading**: Use `load_tool` to dynamically register the new tool
5. **Validation**: Confirm tool creation and availability
6. **Usage**: Demonstrate or use the newly created tool

#### System Prompt Guidelines

The `TOOL_BUILDER_SYSTEM_PROMPT` provides comprehensive instructions for:

- **Tool Naming Convention**: File name must match function name
- **Tool Creation vs. Usage**: Distinguish between creating new tools and using existing ones
- **Tool Structure**: Enforce standardized format for all generated tools
- **Autonomous Workflow**: Handle complete creation process without user intervention

### Sample Interactions

#### Step 1: Creating a Custom Tool

**Input:**
```
Create a tool that counts characters in text
```

**Expected Process:**
1. Agent analyzes the request and determines tool requirements
2. Generates Python code for character counting functionality
3. Creates file named `count_characters.py`
4. Loads the tool into the agent's registry
5. Confirms successful creation with "TOOL_CREATED: count_characters.py"

#### Step 2: Using the Custom Tool

**Input:**
```
Count the characters in "Hello, Strands! How are you today?"
```

**Expected Response:**
- Agent recognizes this as a usage request (not creation)
- Uses the existing `count_characters` tool
- Returns: "The text contains 34 characters"
- Explains why no new tool was created (existing tool handles the request)

### Technical Implementation Details

#### Tool Creation Intelligence

The agent demonstrates sophisticated decision-making:

**Creation Triggers:**
- "Create a tool that..."
- "Make a tool for..."
- "Build a tool to..."

**Usage Recognition:**
- Direct task requests without creation keywords
- Questions that existing tools can answer
- Specific operations on data

#### Error Handling and Validation

**Tool Specification Validation:**
- Ensures proper `inputSchema` format with "json" wrapper
- Validates function parameter access via `tool_use["input"]["param_name"]`
- Confirms return format with `toolUseId` and content structure

**Runtime Validation:**
- Tests tool loading before confirming creation
- Validates tool functionality with sample inputs
- Provides clear error messages for debugging

### Extending the Example

**Suggested Enhancements:**
1. **Tool Version Control**: Implement versioning for created tools to track changes
2. **Tool Testing**: Add automated testing for newly created tools
3. **Tool Improvement**: Create tools that enhance existing capabilities
4. **Tool Categories**: Organize tools by functionality or domain
5. **Tool Sharing**: Enable export/import of created tools
6. **Tool Analytics**: Track tool usage and effectiveness
7. **Tool Documentation**: Auto-generate documentation for created tools
8. **Tool Optimization**: Improve existing tools based on usage patterns

### Advanced Use Cases

**Complex Tool Creation Examples:**
- Data processing pipelines
- API integration tools
- File manipulation utilities
- Mathematical computation tools
- Text processing and analysis tools
- Format conversion utilities

### Usage Notes
- Type `exit` to quit the application
- Press `Ctrl+C` to stop the program
- Avoid entering sensitive or PII data in tool creation requests
- Created tools persist for the session duration
- Tool names must be unique within the session

---

*Additional modules will be added as they are developed.*
