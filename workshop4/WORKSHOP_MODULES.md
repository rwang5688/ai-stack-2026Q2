# Agentic AI with Strands (Agents) SDK and (Amazon Bedrock) AgentCore Workshop Modules

This document provides detailed information, including sample code and queries, from the modules leading up to Module 7 in the [Agentic AI with Strands (Agents) SDK and (Amazon Bedrock AgentCore)](https://catalog.workshops.aws/strands/en-US) workshop.  These published workshop modules will teach you how to use Strands Agents SDK to build and deploy agentic AI systems.

**⚠️ AWS Credentials Required:** All examples require AWS credentials with Amazon Bedrock permissions. Ensure your runtime environment has proper IAM permissions to invoke Bedrock models.

---

## Environment Setup

See [Cross-Platform Develompent Guide](CROSS_PLATFORM.md) for detailed information about environment setup and runtime execution across different platforms.

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
cd workshop4/modules/module1
uv run mcp_calculator.py
```

**Windows GitBash (if connection issues occur):**
```bash
cd workshop4/modules/module1
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
cd workshop4/modules/module2
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
cd workshop4/modules/module3

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
cd workshop4/modules/module3
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
cd workshop4/modules/module3
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
cd workshop4/modules/module4
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

*Additional modules will be added as they are developed.*
