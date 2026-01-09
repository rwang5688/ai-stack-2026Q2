# Building Multi-Agent with Strands Agents SDK using Amazon Bedrock

**AWS Workshop Link:** [Module 7: Building Multi-Agent with Strands](https://catalog.workshops.aws/strands/en-US/module-7-building-multi-agent-with-strands)

**Strands Agents Docs on GitHub Link:** [teachers_assistant.py](https://github.com/strands-agents/docs/blob/main/docs/examples/python/multi_agent_example/teachers_assistant.py)

## Description

This module demonstrates how to implement a multi-agent architecture using Strands Agents with Amazon Bedrock model hosting, where specialized agents work together under the coordination of a central orchestrator. The system uses natural language routing to direct queries to the most appropriate specialized agent based on subject matter expertise, showcasing the **Teacher's Assistant Pattern** and **Tool-Agent Pattern**.

The module follows a **4-step progressive implementation**:
- **Step 1**: CLI Multi-Agent System (Command-line interface)
- **Step 2**: Streamlit Web Interface (Web-based user interface)
- **Step 3**: Knowledge Base Integration (Document-enhanced responses)
- **Step 4**: Production Deployment (Docker + AWS CDK)

The module showcases:
- **Multi-Agent Architecture**: Central orchestrator coordinating 5 specialized agents
- **Tool-Agent Pattern**: Strands agents wrapped as tools using the `@tool` decorator
- **Natural Language Routing**: Intelligent query classification and agent selection
- **Domain Specialization**: Each agent optimized for specific subject areas with targeted tools
- **Cross-Platform Compatibility**: Dynamic tool detection and fallbacks for Windows/Linux/macOS
- **Clean Output Management**: Suppressed intermediate outputs for optimal user experience
- **Amazon Bedrock Integration**: Using AWS Nova Pro model (`us.amazon.nova-pro-v1:0`) for enhanced AI capabilities

## Agent Architecture

The Teacher's Assistant implements a **multi-agent coordination pattern** where specialized agents work together:

| Agent | Role | Responsibility | Tools Used |
|-------|------|----------------|------------|
| **Teacher's Assistant** | Central Orchestrator | Analyzes queries and routes to appropriate specialists | All specialized agents as tools |
| **Math Assistant** | Mathematical Expert | Handles calculations, equations, and mathematical concepts | `calculator` |
| **English Assistant** | Language Arts Expert | Processes grammar, writing, and literature queries | `editor`, `file_read`, `file_write` |
| **Language Assistant** | Translation Specialist | Manages translations and language-related queries | `http_request` |
| **Computer Science Assistant** | Programming Expert | Handles coding, algorithms, and technical concepts | `python_repl`, `shell`, `editor`, `file_read`, `file_write` |
| **General Assistant** | Knowledge Generalist | Processes queries outside specialized domains | None (LLM only) |

## Key Features

- **Complexity**: Intermediate level multi-agent coordination
- **Interfaces**: Both command-line (Step 1) and web-based (Step 2) interfaces
- **Key Technique**: Dynamic Query Routing with Tool-Agent Pattern
- **Cross-Platform**: Works on Windows, Linux, and macOS with automatic tool detection
- **Model Integration**: Amazon Bedrock Nova Pro (`us.amazon.nova-pro-v1:0`) for enhanced reasoning
- **Tools Used**: calculator, python_repl, shell, http_request, editor, file operations, memory
- **Output Management**: Clean user experience with suppressed agent intermediates
- **Progressive Learning**: 4-step implementation from CLI to production deployment
- **Knowledge Base Integration**: Personal information storage and retrieval (Step 3)
- **Intelligent Routing**: Automatic determination between educational and knowledge queries

## Architecture Diagram

```
Teacher's Assistant (Orchestrator) + Knowledge Base Router
├── Central coordinator that routes queries to specialists OR knowledge base
├── Query Classification & Routing (Educational vs Knowledge)
│
├── EDUCATIONAL SPECIALISTS:
├── Math Assistant ──────────── Calculator Tool
│   └── Handles mathematical calculations and concepts
│
├── English Assistant ──────── Editor & File Tools  
│   └── Processes grammar and language comprehension
│
├── Language Assistant ─────── HTTP Request Tool
│   └── Manages translations and language-related queries
│
├── Computer Science Assistant ── Python REPL, Shell & File Tools
│   └── Handles programming and technical concepts
│
├── General Assistant ──────── No Specialized Tools
│   └── Processes queries outside specialized domains
│
└── KNOWLEDGE BASE SYSTEM:
    ├── Knowledge Base Agent ─── Memory Tool + Use Agent Tool
    │   ├── Store Action: "Remember that my birthday is July 25"
    │   └── Retrieve Action: "What's my birthday?"
    └── Strands Knowledge Base ── Document Storage & Retrieval
```

## How to Run

**Prerequisites:**
- AWS credentials configured with Amazon Bedrock permissions
- Python 3.12+ with virtual environment activated
- Access to Amazon Bedrock Nova Pro model (`us.amazon.nova-pro-v1:0`)
- Streamlit installed (included in requirements.txt)

### Environment Setup

**The Proper Way (Git Bash/Linux/macOS):**

Set your environment variables in `~/.bashrc`:

```bash
export STRANDS_KNOWLEDGE_BASE_ID="IMW46CITZE"
export AWS_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_SESSION_TOKEN="your-session-token"  # For temporary credentials
export BYPASS_TOOL_CONSENT="true"  # Skip tool consent prompts
```

Then source it: `source ~/.bashrc`

**The Unfortunately Necessary PowerShell Way:**

If you're using Kiro IDE (which is based on VS Code) on Windows, you're forced to use PowerShell. Follow these steps in order:

**Step 1: Activate the virtual environment**
```powershell
# Activate the virtual environment (PowerShell way)
venv\Scripts\Activate.ps1
```

**Step 2: Run the PowerShell script (hold your nose)**
```powershell
# Allow script execution (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run the environment setup script
.\set-env.ps1
```

**Step 3: Set AWS temporary credentials manually**
```powershell
# Copy and paste your actual AWS temporary credentials
$Env:AWS_ACCESS_KEY_ID="your-access-key-here"
$Env:AWS_SECRET_ACCESS_KEY="your-secret-key-here"
$Env:AWS_SESSION_TOKEN="your-session-token-here"
```

**Step 4: Run the Streamlit application (CRITICAL: Same terminal session!)**
```powershell
# IMPORTANT: Run this in the SAME PowerShell terminal where you set the credentials
# Do NOT open a new terminal or the credentials will be lost!
uv run streamlit run multi_agent_bedrock/app.py
```

**CRITICAL WARNING:**
- All commands must be run in the SAME PowerShell terminal session
- If you open a new terminal, the environment variables (including AWS credentials) will be lost
- PowerShell environment variables only exist for the current session
- This is why PowerShell sucks compared to proper Unix terminals

**Why This Painful Process Exists:**
- Kiro IDE is based on VS Code, which defaults to PowerShell on Windows
- VS Code/Kiro doesn't give you a proper Unix terminal option
- Temporary credentials should never be hardcoded in scripts
- Each session requires fresh temporary credentials

**Note:** The PowerShell script only sets variables for the current session. Use Git Bash whenever possible for a better development experience.

### Step 1: CLI Multi-Agent System

**Command-line interface for direct agent interaction:**

```bash
# Navigate to the multi-agent directory
cd workshop4/multi_agent_bedrock

# Run the CLI version
uv run teachers_assistant.py
```

**Features:**
- Direct command-line interaction
- Clean terminal output with routing confirmation
- Cross-platform tool compatibility
- Type `exit` to quit

### Step 2: Streamlit Web Interface

**Web-based interface with enhanced user experience:**

```bash
# Navigate to the multi-agent directory
cd workshop4/multi_agent_bedrock

# Run the Streamlit web app
streamlit run app.py
```

**Features:**
- User-friendly web interface at `http://localhost:8501`
- Conversation history and session management
- Visual service information (Amazon Bedrock + Nova Pro model)
- Sidebar with specialist descriptions and sample questions
- Enhanced error handling and loading indicators
- Clear conversation button

**Choose Your Interface:**
- **CLI (Step 1)**: Best for direct testing, scripting, or terminal-based workflows
- **Web UI (Step 2)**: Best for interactive use, demonstrations, or user-friendly access

### Step 3: Knowledge Base Integration

**Enhanced web interface with knowledge base capabilities for storing and retrieving personal information:**

#### Prerequisites for Step 3

In addition to the basic prerequisites, Step 3 requires:
- **Strands Knowledge Base ID**: Environment variable configuration
- **Memory tool access**: Enabled through environment variable

#### Environment Setup

**Option 1: Set environment variable in your shell session (temporary):**

```bash
# For current session only
export AWS_REGION="us-east-1"
export BYPASS_TOOL_CONSENT="true"
export STRANDS_KNOWLEDGE_BASE_ID="your_knowledge_base_id_here"

# Verify the environment variables are set
echo "AWS_REGION: $AWS_REGION"
echo "BYPASS_TOOL_CONSENT: $BYPASS_TOOL_CONSENT"
echo "STRANDS_KNOWLEDGE_BASE_ID: $STRANDS_KNOWLEDGE_BASE_ID"
```

**Option 2: Add to .bashrc for persistent setup (recommended):**

```bash
# Add to your .bashrc file
echo 'AWS_REGION="us-east-1"' >> ~/.bashrc
echo 'export BYPASS_TOOL_CONSENT="true"' >> ~/.bashrc
echo 'export STRANDS_KNOWLEDGE_BASE_ID="your_knowledge_base_id_here"' >> ~/.bashrc

# Reload your shell configuration
source ~/.bashrc

# Verify the environment variables are set
echo "AWS_REGION: $AWS_REGION"
echo "BYPASS_TOOL_CONSENT: $BYPASS_TOOL_CONSENT"
echo "STRANDS_KNOWLEDGE_BASE_ID: $STRANDS_KNOWLEDGE_BASE_ID"
```

**Option 3: For demonstration/testing without a real knowledge base:**

```bash
# Use the default demo KB ID for testing
export AWS_REGION="us-east-1"
export BYPASS_TOOL_CONSENT="true"
export STRANDS_KNOWLEDGE_BASE_ID="demokb123"
```

#### Running Step 3

```bash
# Navigate to the multi-agent directory
cd workshop4/multi_agent_bedrock

# Verify the environment variables are set
echo "AWS_REGION: $AWS_REGION"
echo "BYPASS_TOOL_CONSENT: $BYPASS_TOOL_CONSENT"
echo "STRANDS_KNOWLEDGE_BASE_ID: $STRANDS_KNOWLEDGE_BASE_ID"

# Run the enhanced Streamlit web app with knowledge base
streamlit run app.py
```

#### Step 3 Features

- **Intelligent Query Routing**: Automatically determines whether queries should go to educational specialists or knowledge base
- **Knowledge Storage**: Store personal information, preferences, and facts
- **Knowledge Retrieval**: Retrieve previously stored information with natural language queries
- **Dual Functionality**: Seamlessly combines educational assistance with personal knowledge management
- **Enhanced UI**: Updated interface showing both educational and knowledge base capabilities

#### Step 3 Sample Interactions

**Knowledge Storage Examples:**
```
"Remember that my birthday is July 25"
"Store this information: I live in Seattle"
"My favorite programming language is Python"
"I work as a software engineer at Amazon"
"My favorite K-pop groups are aespa, BLACKPINK, NMIXX, Hearts2Hearts, Red Velvet, ITZY, and TWICE"
```

**Knowledge Retrieval Examples:**
```
"What's my birthday?"
"Where do I live?"
"What is my favorite programming language?"
"What do you know about my job?"
"Who are my favorite K-pop groups?"
```

**Educational Queries (still work as before):**
```
"Solve the quadratic equation x^2 + 5x + 6 = 0"
"Write a Python function to check if a string is a palindrome"
"Translate 'Hello, how are you?' to Spanish"
```

#### How Knowledge Base Routing Works

The enhanced Step 3 implementation uses **intelligent dual routing** to seamlessly handle both educational and personal knowledge queries:

1. **Query Analysis**: When you submit a query, the system first determines whether it's:
   - **Educational** (math, programming, translations, etc.) → Routes to Teacher's Assistant
   - **Knowledge-based** (storing/retrieving personal information) → Routes to Knowledge Base Agent

2. **Knowledge Base Operations**: For knowledge queries, the system further determines:
   - **Store Action**: Phrases like "Remember that...", "Store this...", "My favorite..." 
   - **Retrieve Action**: Questions like "What's my...", "Who are...", "Where do I..."

3. **Clean Response Processing**: Knowledge base responses are automatically cleaned to remove technical metadata and provide user-friendly answers.

#### Knowledge Base Response Examples

**Storage Confirmation:**
```
User: "Remember that my birthday is July 25"
System: "✅ I've stored this information in your knowledge base."
```

**Retrieval Response:**
```
User: "Who are my favorite K-pop groups?"
System: "Your favorite K-pop groups are: aespa, BLACKPINK, NMIXX, Hearts2Hearts, Red Velvet, ITZY, and TWICE."
```

**Educational Query (unchanged):**
```
User: "Solve x^2 + 5x + 6 = 0"
System: "Routed to Math Assistant

I'll solve the quadratic equation x² + 5x + 6 = 0 step by step...
[Full mathematical solution follows]"
```

#### Troubleshooting Step 3

**Common Issues:**

1. **Knowledge Base ID not set:**
   ```
   Error: STRANDS_KNOWLEDGE_BASE_ID environment variable is not set
   ```
   **Solution:** Set the environment variable as shown above

2. **Tool consent issues:**
   ```
   Error: Tool consent required
   ```
   **Solution:** Ensure `BYPASS_TOOL_CONSENT="true"` is set

3. **Environment variables not persisting:**
   ```bash
   # Check if variables are set
   env | grep STRANDS
   
   # If not found, re-source your .bashrc
   source ~/.bashrc
   ```

4. **Knowledge base connection issues:**
   - Verify AWS credentials are properly configured
   - Ensure you have permissions for the knowledge base service
   - Check that the knowledge base ID exists and is accessible

5. **Knowledge base indexing delay (Normal Behavior):**
   ```
   User: "my favorite subjects are: history, literature, math"
   System: "✅ I've stored this information in your knowledge base."
   User: "what are my favorite subjects?"
   System: "I don't have any information about your favorite subjects stored."
   ```
   **Explanation:** This is **normal AWS Bedrock Knowledge Base behavior**
   - **Store operations**: Complete immediately with success confirmation
   - **Indexing delay**: 2-3 minutes for new data to become searchable
   - **Retrieve operations**: Only work on fully indexed data
   - **Solution**: Wait 2-3 minutes after storing, then retry retrieval queries
   - **Workshop benefit**: Demonstrates real-world cloud service behavior

## Sample Interactions

### Example 1: Mathematics Question

**Input:**
```
Solve the quadratic equation x^2 + 5x + 6 = 0
```

**Expected Output (Routed to Math Assistant):**
```
Routed to Math Assistant

I'll solve the quadratic equation x² + 5x + 6 = 0 step by step, showing multiple methods and explaining the concepts clearly.

## Solution to x² + 5x + 6 = 0

**The solutions are x = -3 and x = -2**

### Method 1: Factoring (Most Efficient for this equation)

**Step 1:** Identify the quadratic equation in standard form
- We have: x² + 5x + 6 = 0
- This is in the form ax² + bx + c = 0, where a = 1, b = 5, c = 6

**Step 2:** Look for two numbers that multiply to give 'c' and add to give 'b'
- We need two numbers that multiply to 6 and add to 5
- Factor pairs of 6: (1,6), (2,3), (-1,-6), (-2,-3)
- Check which pair adds to 5: 2 + 3 = 5 ✓

**Step 3:** Factor the quadratic
- x² + 5x + 6 = (x + 2)(x + 3) = 0

**Step 4:** Apply the Zero Product Property
- If (x + 2)(x + 3) = 0, then either (x + 2) = 0 OR (x + 3) = 0
- From x + 2 = 0: x = -2
- From x + 3 = 0: x = -3

### Method 2: Quadratic Formula (Works for any quadratic)

Using the quadratic formula: x = (-b ± √(b² - 4ac))/(2a)
- a = 1, b = 5, c = 6
- Discriminant: b² - 4ac = 25 - 24 = 1
- x = (-5 ± 1)/2 = -2 or -3

### Final Answer
**x = -3 and x = -2**

These are the x-intercepts of the parabola y = x² + 5x + 6.
```

### Example 2: Computer Science Question

**Input:**
```
Write a Python function to check if a string is a palindrome
```

**Expected Output (Routed to Computer Science Assistant):**
```
Routed to Computer Science Assistant

Certainly! A palindrome is a string that reads the same backward as forward. Here's a simple Python function to check if a given string is a palindrome:

```python
def is_palindrome(s: str) -> bool:
    """
    Check if the given string is a palindrome.
    
    Parameters:
    s (str): The string to check.
    
    Returns:
    bool: True if the string is a palindrome, False otherwise.
    """
    # Remove any non-alphanumeric characters and convert to lowercase
    cleaned_string = ''.join(e for e in s if e.isalnum()).lower()
    
    # Check if the cleaned string is equal to its reverse
    return cleaned_string == cleaned_string[::-1]

# Example usage:
print(is_palindrome("A man, a plan, a canal, Panama"))  # True
print(is_palindrome("hello"))  # False
```

### Explanation:
1. **Cleaning the String**: Removes non-alphanumeric characters and converts to lowercase
2. **Checking for Palindrome**: Compares the cleaned string with its reverse
3. **Return Value**: True if palindrome, False otherwise

### Examples:
- `is_palindrome("A man, a plan, a canal, Panama")` returns `True`
- `is_palindrome("hello")` returns `False`
```

### Example 3: Language Translation Request

**Input:**
```
Translate "Hello, how are you?" to Spanish
```

**Expected Output (Routed to Language Assistant):**
```
Routed to Language Assistant

The translation of "Hello, how are you?" to Spanish is "Hola, ¿cómo estás?"

Here's a breakdown of the translation:
- "Hello" translates to "Hola"
- "how are you?" translates to "¿cómo estás?"

If you are speaking in a more formal context, you might use "¿cómo está usted?" instead of "¿cómo estás?". The phrase "usted" is a formal version of "you," often used when addressing someone with whom you are not familiar or in a professional setting.
```

### Example 4: Knowledge Base Storage (Step 3)

**Input:**
```
Remember that my favorite K-pop groups are aespa, BLACKPINK, NMIXX, Hearts2Hearts, Red Velvet, ITZY, and TWICE
```

**Expected Output (Routed to Knowledge Base Agent):**
```
✅ I've stored this information in your knowledge base.
```

### Example 5: Knowledge Base Retrieval (Step 3)

**Input:**
```
Who are my favorite K-pop groups?
```

**Expected Output (Routed to Knowledge Base Agent):**
```
Your favorite K-pop groups are: aespa, BLACKPINK, NMIXX, Hearts2Hearts, Red Velvet, ITZY, and TWICE.
```

## Technical Implementation

### Cross-Platform Tool Compatibility

The system uses dynamic platform detection to ensure compatibility across Windows, Linux, and macOS:

```python
# cross_platform_tools.py handles platform-specific tool imports
from cross_platform_tools import get_computer_science_tools, get_platform_capabilities

# Automatic platform detection and tool fallbacks
capabilities = get_platform_capabilities()
available_tools = get_computer_science_tools()

# Platform-aware system prompts
if not capabilities['available_tools']['python_repl']:
    platform_note += "Note: Python code execution not available. Providing code examples with explanations."
```

**Tool Availability by Platform:**
- **Windows**: Core tools (calculator, http_request, file operations, editor) ✓, execution tools (python_repl, shell) ✗
- **Linux/macOS**: All tools available ✓

For detailed cross-platform implementation, see [Cross-Platform Development Guide](CROSS_PLATFORM.md).

### 1. Teacher's Assistant (Orchestrator)

The `teacher_assistant` acts as the central coordinator that analyzes incoming natural language queries, determines the most appropriate specialized agent, and routes queries to that agent.

**Implementation:**
```python
teacher_agent = Agent(
    model=bedrock_model,  # Amazon Bedrock Nova Pro
    system_prompt=TEACHER_SYSTEM_PROMPT,
    callback_handler=None,  # Suppresses intermediate output
    tools=[math_assistant, language_assistant, english_assistant,
           computer_science_assistant, general_assistant],
)
```

**Key Features:**
- **Clean Output**: `callback_handler=None` suppresses intermediate processing
- **Natural Language Routing**: System prompt guides intelligent query classification
- **Tool Integration**: All specialized agents available as tools

### 2. Specialized Agents (Tool-Agent Pattern)

Each specialized agent is implemented as a Strands tool using the `@tool` decorator with domain-specific capabilities:

**Math Assistant Example:**
```python
@tool
def math_assistant(query: str) -> str:
    """Process and respond to math-related queries using a specialized math agent."""
    formatted_query = f"Please solve the following mathematical problem, showing all steps and explaining concepts clearly: {query}"
    
    try:
        print("Routed to Math Assistant")
        math_agent = Agent(
            system_prompt=MATH_ASSISTANT_SYSTEM_PROMPT,
            tools=[calculator],
        )
        response = math_agent(formatted_query)
        return str(response)
    except Exception as e:
        return f"Error processing your mathematical query: {str(e)}"
```

**Agent Specializations:**
- **Math Assistant**: Mathematical calculations using `calculator` tool (cross-platform)
- **English Assistant**: Writing and grammar using `editor`, `file_read`, `file_write` tools (cross-platform)
- **Language Assistant**: Translations using `http_request` tool (cross-platform)
- **Computer Science Assistant**: Programming using available tools based on platform detection
  - **Linux/macOS**: `python_repl`, `shell`, `editor`, file operations (full functionality)
  - **Windows**: `editor`, file operations (code examples with explanations)
- **General Assistant**: General knowledge without specialized tools (cross-platform)

### 3. Tool-Agent Pattern

This example demonstrates the **Tool-Agent Pattern** where Strands agents are wrapped as tools using the `@tool` decorator. These tools are then provided to another agent (the Teacher's Assistant), creating a system where agents can use other agents as tools.

**Benefits:**
- **Modularity**: Each agent can be developed and tested independently
- **Scalability**: Easy to add new specialized agents
- **Cross-Platform Compatibility**: Automatic adaptation to platform capabilities
- **Maintainability**: Clear separation of concerns and responsibilities
- **Reusability**: Specialized agents can be used in other contexts

## Tools Used Overview

The multi-agent system utilizes several tools to provide specialized capabilities:

### Core Tools

| Tool | Purpose | Capabilities | Used By |
|------|---------|--------------|---------|
| **calculator** | Mathematical operations | SymPy-powered calculations, equation solving, differentiation, integration | Math Assistant |
| **python_repl** | Code execution | Interactive Python environment with state persistence | Computer Science Assistant |
| **shell** | System operations | Command execution with real-time output | Computer Science Assistant |
| **http_request** | Web requests | External API access with authentication support | Language Assistant |
| **editor** | File editing | Code creation and modification with syntax highlighting | English & CS Assistants |
| **file_read/file_write** | File operations | Reading and writing files for content management | English & CS Assistants |
| **memory** | Knowledge base operations | Store and retrieve personal information from Strands Knowledge Base | Knowledge Base Agent |
| **use_agent** | Agent orchestration | Route queries to appropriate agents and process responses | Knowledge Base Agent |

### Tool Integration Benefits

- **Domain Optimization**: Each agent has tools specifically chosen for its domain
- **Capability Extension**: Tools extend agent capabilities beyond pure language processing
- **Real-world Integration**: Agents can interact with external systems and APIs
- **Interactive Execution**: Real-time code execution and system interaction

## Directory Structure

```
workshop4/multi_agent_bedrock/
├── app.py                          # Step 2: Streamlit web interface
├── teachers_assistant.py           # Step 1: CLI interface  
├── cross_platform_tools.py         # Cross-platform compatibility
├── math_assistant.py               # Math specialist
├── english_assistant.py            # English specialist
├── language_assistant.py           # Language specialist
├── computer_science_assistant.py   # CS specialist
└── no_expertise.py                 # General assistant
```

## Implementation Files

- **[app.py](multi_agent_bedrock/app.py)** - Step 2: Streamlit web interface for multi-agent system with conversation history, enhanced UX, and Amazon Bedrock service identification
- **[teachers_assistant.py](multi_agent_bedrock/teachers_assistant.py)** - Step 1: CLI orchestrator agent with routing logic and command-line interface
- **[cross_platform_tools.py](multi_agent_bedrock/cross_platform_tools.py)** - Cross-platform tool detection and import management for Windows/Linux/macOS compatibility
- **[math_assistant.py](multi_agent_bedrock/math_assistant.py)** - Mathematical specialist with calculator integration for equations and mathematical concepts
- **[english_assistant.py](multi_agent_bedrock/english_assistant.py)** - Language arts specialist with file operations for writing, grammar, and literature
- **[language_assistant.py](multi_agent_bedrock/language_assistant.py)** - Translation specialist with HTTP capabilities for language-related queries
- **[computer_science_assistant.py](multi_agent_bedrock/computer_science_assistant.py)** - Programming specialist with platform-aware tools (python_repl, shell, editor, file operations)
- **[no_expertise.py](multi_agent_bedrock/no_expertise.py)** - General knowledge assistant for queries outside specialized domains (no specific tools)

## Amazon Bedrock Integration

### Model Configuration

The system uses Amazon Bedrock's Nova Pro model for enhanced reasoning capabilities:

```python
bedrock_model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",  # Amazon Nova Pro via Amazon Bedrock
    temperature=0.3,
)
```

**Model Benefits:**
- **Advanced Reasoning**: Superior performance on complex multi-step problems
- **Domain Expertise**: Better understanding of specialized subject areas
- **Natural Language Processing**: Improved query classification and routing
- **Cost Efficiency**: Optimized pricing for production workloads
- **Cross-Region Support**: Can use cross-region inference profile IDs for multi-region deployments

### AWS Prerequisites

- **AWS Credentials**: Properly configured with Bedrock permissions
- **Region Support**: Ensure your region supports Amazon Bedrock
- **Model Access**: Request access to Nova Pro model if needed
- **IAM Permissions**: Bedrock invoke permissions for your role/user
- **Production Deployment**: CDK stack includes comprehensive IAM permissions for Bedrock, S3, and OpenSearch Serverless (lines 136-194 in `cdk_stack.py` - intentionally broad for workshop reliability)

## Extending the Example

### Suggested Enhancements

1. **Add Memory**: Implement session memory so the system remembers previous interactions
2. **Add More Specialists**: Create additional specialized agents for other domains (Science, History, Art)
3. **Implement Agent Collaboration**: Enable multiple agents to collaborate on complex queries
4. **Add Knowledge Base**: Integrate Bedrock Knowledge Base for document-enhanced responses (Step 3)
5. **Production Deployment**: Deploy using Docker and AWS CDK infrastructure (Step 4)
6. **Add Evaluation**: Implement a system to evaluate and improve routing accuracy
7. **Performance Monitoring**: Track agent performance and response quality
8. **Multi-Modal Support**: Add support for image, audio, and document processing
9. **Advanced Routing**: Implement confidence scoring and fallback mechanisms
10. **Enhanced Cross-Platform Support**: Add more platform-specific optimizations

### Advanced Use Cases

**Complex Query Handling:**
- Multi-domain questions requiring multiple agents
- Sequential problem-solving with agent handoffs
- Collaborative research and analysis tasks
- Cross-domain validation and fact-checking

**Production Enhancements:**
- Load balancing across multiple agent instances
- Caching for frequently asked questions
- Rate limiting and cost management
- Monitoring and observability integration

## Troubleshooting

### Common Issues

**AWS Credentials:**
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check Bedrock access
aws bedrock list-foundation-models --region us-west-2
```

**Model Access:**
- Ensure you have access to Amazon Nova Pro model (`us.amazon.nova-pro-v1:0`) in your region
- Check Amazon Bedrock console for model availability
- Verify IAM permissions for bedrock:InvokeModel
- For multi-region deployments, consider using cross-region inference profile IDs

**Import Errors:**
- Ensure all required packages are installed: `uv pip install -r requirements.txt`
- Verify Strands Agents SDK is properly installed
- Check Python version compatibility (3.12+)

**Performance Issues:**
- Monitor token usage and costs in AWS console
- Adjust temperature settings for different response styles
- Consider model alternatives for cost optimization

### Error Resolution

**Connection Errors:**
- Check internet connectivity for HTTP requests
- Verify AWS region configuration
- Ensure proper network access to Bedrock endpoints

**Tool Failures:**
- Individual tool errors are handled gracefully by each agent
- Check tool-specific requirements (calculator, shell access, etc.)
- Verify file permissions for editor and file operations

## Usage Notes

### CLI Version (Step 1)
- Type `exit` to quit the application
- Press `Ctrl+C` to stop the program
- Each agent provides routing confirmation for transparency
- Clean terminal output with suppressed intermediate processing

### Web Interface (Step 2)
- Access via browser at `http://localhost:8501`
- Use the sidebar for specialist information and sample questions
- Conversation history is maintained during the session
- Use "Clear Conversation" button to start fresh
- Loading indicators show processing status

### General Guidelines
- Avoid entering sensitive or PII data in queries
- Be patient with complex queries - they may take time to process
- Cross-platform compatibility automatically adapts tool availability
- Service information clearly shows "Amazon Bedrock" and model details

---

*This module serves as the foundation for building sophisticated multi-agent systems with Strands Agents and Amazon Bedrock, demonstrating enterprise-ready patterns for AI agent coordination and specialization.*