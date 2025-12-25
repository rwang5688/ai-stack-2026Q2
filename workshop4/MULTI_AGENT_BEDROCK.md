# Module 7: Building Multi-Agent with Strands using Amazon Bedrock

**AWS Workshop Link:** [Module 7: Building Multi-Agent with Strands](https://catalog.workshops.aws/strands/en-US/module-7-building-multi-agent-with-strands)

**Strands Agents Docs on GitHub Link:** [teachers_assistant.py](https://github.com/strands-agents/docs/blob/main/docs/examples/python/teachers_assistant.py)

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
- **Tools Used**: calculator, python_repl, shell, http_request, editor, file operations
- **Output Management**: Clean user experience with suppressed agent intermediates
- **Progressive Learning**: 4-step implementation from CLI to production deployment

## Architecture Diagram

```
Teacher's Assistant (Orchestrator)
├── Central coordinator that routes queries to specialists
├── Query Classification & Routing
│
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
└── General Assistant ──────── No Specialized Tools
    └── Processes queries outside specialized domains
```

## How to Run

**Prerequisites:**
- AWS credentials configured with Amazon Bedrock permissions
- Python 3.12+ with virtual environment activated
- Access to Amazon Bedrock Nova Pro model (`us.amazon.nova-pro-v1:0`)
- Streamlit installed (included in requirements.txt)

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