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

*Additional modules will be added as they are developed.*

---
