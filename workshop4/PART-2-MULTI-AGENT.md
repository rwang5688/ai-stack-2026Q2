# Part 2: Multi-Agent with Amazon Bedrock

Build sophisticated multi-agent systems using Amazon Bedrock foundation models with the Teacher's Assistant pattern. This comprehensive guide takes you from CLI implementation to production deployment with full authentication and knowledge base integration.

## Overview

This track demonstrates how to implement a multi-agent architecture using Strands Agents with Amazon Bedrock model hosting. The system uses natural language routing to direct queries to specialized agents, showcasing the **Teacher's Assistant Pattern** and **Tool-Agent Pattern**.

**Time Investment**: 4-6 hours total
**Prerequisites**: [Part 1: Foundational Modules](PART-1-FOUNDATIONS.md) completed (especially Module 3 for Knowledge Base integration)

## Learning Journey

```
Step 1: CLI Multi-Agent → Step 2: Web Interface → Step 3: Knowledge Base → Step 4: Production
   ↓                        ↓                     ↓                      ↓
Command Line             Streamlit UI          Personal Memory        Docker + AWS CDK
Basic Routing           Enhanced UX           Knowledge Storage      Full Deployment
```

## Architecture Overview

### Multi-Agent System Pattern

The Teacher's Assistant implements a **multi-agent coordination pattern** where specialized agents work together:

| Agent | Role | Responsibility | Tools Used |
|-------|------|----------------|------------|
| **Teacher's Assistant** | Central Orchestrator | Analyzes queries and routes to appropriate specialists | All specialized agents as tools |
| **Math Assistant** | Mathematical Expert | Handles calculations, equations, and mathematical concepts | `calculator` |
| **English Assistant** | Language Arts Expert | Processes grammar, writing, and literature queries | `editor`, `file_read`, `file_write` |
| **Language Assistant** | Translation Specialist | Manages translations and language-related queries | `http_request` |
| **Computer Science Assistant** | Programming Expert | Handles coding, algorithms, and technical concepts | `python_repl`, `shell`, `editor`, `file_read`, `file_write` |
| **General Assistant** | Knowledge Generalist | Processes queries outside specialized domains | None (LLM only) |

### Progressive Enhancement

```
Step 1: Basic Multi-Agent CLI
├── Natural language routing
├── 5 specialized agents
├── Cross-platform tool compatibility
└── Clean terminal output

Step 2: Enhanced Web Interface  
├── Streamlit UI with conversation history
├── Sidebar with agent information
├── Service identification (Amazon Bedrock)
└── Enhanced error handling

Step 3: Knowledge Base Integration
├── Personal information storage
├── Intelligent query routing (Educational vs Knowledge)
├── Dual functionality (Teaching + Memory)
└── Knowledge base indexing behavior

Step 4: Production Deployment
├── Docker containerization
├── AWS CDK infrastructure
├── Cognito authentication
├── ECS Fargate hosting
├── CloudFront distribution
└── Comprehensive monitoring
```

## Step 1: CLI Multi-Agent System

Build the foundational multi-agent system with command-line interface.

### What You'll Build

A command-line multi-agent system that demonstrates:
- **Natural Language Routing**: Intelligent query classification and agent selection
- **Tool-Agent Pattern**: Strands agents wrapped as tools using the `@tool` decorator
- **Cross-Platform Compatibility**: Dynamic tool detection and fallbacks for Windows/Linux/macOS
- **Clean Output Management**: Suppressed intermediate outputs for optimal user experience

### Key Features

- **5 Specialized Agents**: Math, English, Language, Computer Science, General
- **Amazon Bedrock Integration**: Using Nova Pro model (`us.amazon.nova-pro-v1:0`)
- **Cross-Platform Tools**: Automatic adaptation to platform capabilities
- **Routing Transparency**: Clear indication of which agent handles each query

### Environment Setup

**Set AWS Region and Credentials:**
```bash
export AWS_REGION="us-east-1"  # or us-west-2
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_SESSION_TOKEN="your-session-token"  # For temporary credentials
export BYPASS_TOOL_CONSENT="true"  # Skip tool consent prompts
```

**Add to .bashrc for persistence:**
```bash
echo 'export AWS_REGION="us-east-1"' >> ~/.bashrc
echo 'export BYPASS_TOOL_CONSENT="true"' >> ~/.bashrc
source ~/.bashrc
```

### How to Run

```bash
# Navigate to the multi-agent directory
cd workshop4/multi_agent_bedrock

# Activate virtual environment
source ../.venv/bin/activate

# Run the CLI version
uv run teachers_assistant.py
```

### Sample Interactions

**Mathematics Query:**
```
Input: Solve the quadratic equation x^2 + 5x + 6 = 0
Output: Routed to Math Assistant

I'll solve the quadratic equation x² + 5x + 6 = 0 step by step...
[Detailed mathematical solution with multiple methods]
```

**Programming Query:**
```
Input: Write a Python function to check if a string is a palindrome
Output: Routed to Computer Science Assistant

Certainly! A palindrome is a string that reads the same backward as forward...
[Complete Python function with explanation and examples]
```

**Translation Query:**
```
Input: Translate "Hello, how are you?" to Spanish
Output: Routed to Language Assistant

The translation of "Hello, how are you?" to Spanish is "Hola, ¿cómo estás?"
[Detailed translation with formal/informal variations]
```

### Cross-Platform Compatibility

The system automatically detects your platform and adapts tool availability:

**Linux/macOS (Full Functionality):**
- All tools available: calculator, python_repl, shell, http_request, editor, file operations
- Complete code execution capabilities

**Windows (Adapted Functionality):**
- Core tools available: calculator, http_request, editor, file operations
- Code examples with explanations instead of execution
- Clear platform capability feedback

## Step 2: Streamlit Web Interface

Enhance the CLI system with a user-friendly web interface.

### What You'll Build

A web-based interface that provides:
- **Interactive Web UI**: User-friendly interface at `http://localhost:8501`
- **Conversation History**: Persistent chat history during session
- **Service Information**: Clear identification of Amazon Bedrock and Nova Pro model
- **Enhanced UX**: Loading indicators, error handling, and conversation management
- **Agent Information**: Sidebar with specialist descriptions and sample questions

### Key Enhancements

- **Streamlit Integration**: Modern web interface with real-time updates
- **Session Management**: Conversation history and state persistence
- **Visual Feedback**: Loading indicators and status messages
- **Agent Discovery**: Sidebar information about each specialist
- **Clear Conversation**: Button to reset conversation history

### How to Run

```bash
# Navigate to the multi-agent directory
cd workshop4/multi_agent_bedrock

# Activate virtual environment
source ../.venv/bin/activate

# Run the Streamlit web app
streamlit run app.py
```

**Access the application**: Open your browser to `http://localhost:8501`

### Web Interface Features

**Main Interface:**
- Chat-style conversation interface
- Real-time message streaming
- Clear routing indicators ("Routed to Math Assistant")
- Service identification showing "Amazon Bedrock" and model details

**Sidebar Information:**
- User authentication status (in production)
- AI service details (Amazon Bedrock + Nova Pro)
- Specialist agent descriptions
- Sample questions for each agent
- Clear conversation button

**Enhanced User Experience:**
- Loading spinners during processing
- Error handling with user-friendly messages
- Conversation persistence during session
- Responsive design for different screen sizes

## Step 3: Knowledge Base Integration

Add personal information storage and retrieval capabilities.

### What You'll Build

An enhanced multi-agent system that combines educational assistance with personal knowledge management:
- **Intelligent Query Routing**: Automatically determines Educational vs Knowledge queries
- **Knowledge Storage**: Store personal information, preferences, and facts
- **Knowledge Retrieval**: Retrieve previously stored information with natural language
- **Dual Functionality**: Seamlessly combines teaching assistance with personal memory

### Prerequisites

**Knowledge Base Setup** (from Module 3):
```bash
# Ensure you have completed Module 3
cd modules/module3

# Verify Knowledge Base exists
export STRANDS_KNOWLEDGE_BASE_ID=$(aws bedrock-agent list-knowledge-bases --region $AWS_REGION --query 'knowledgeBaseSummaries[].knowledgeBaseId' --output text)
echo "STRANDS_KNOWLEDGE_BASE_ID: $STRANDS_KNOWLEDGE_BASE_ID"

# Add to .bashrc for persistence
echo "export STRANDS_KNOWLEDGE_BASE_ID=\"${STRANDS_KNOWLEDGE_BASE_ID}\"" >> ~/.bashrc
source ~/.bashrc
```

### Enhanced Architecture

The Step 3 system adds intelligent routing between two main pathways:

```
User Query → Query Analysis → Educational OR Knowledge Base
                ↓                    ↓
        Teacher's Assistant    Knowledge Base Agent
        (5 Specialists)        (Store/Retrieve)
```

**Educational Queries** → Routed to Teacher's Assistant:
- Math problems and calculations
- Programming questions and code examples
- Translation requests
- Grammar and writing assistance
- General knowledge questions

**Knowledge Queries** → Routed to Knowledge Base Agent:
- Store: "Remember that my birthday is July 25"
- Retrieve: "What's my birthday?"
- Personal information management

### How to Run

```bash
# Navigate to the multi-agent directory
cd workshop4/multi_agent_bedrock

# Verify environment variables
echo "AWS_REGION: $AWS_REGION"
echo "STRANDS_KNOWLEDGE_BASE_ID: $STRANDS_KNOWLEDGE_BASE_ID"
echo "BYPASS_TOOL_CONSENT: $BYPASS_TOOL_CONSENT"

# Run the enhanced Streamlit web app
streamlit run app.py
```

### Sample Interactions

**Knowledge Storage:**
```
Input: Remember that my favorite K-pop groups are aespa, BLACKPINK, NMIXX, Hearts2Hearts, Red Velvet, ITZY, and TWICE
Output: ✅ I've stored this information in your knowledge base.
```

**Knowledge Retrieval:**
```
Input: Who are my favorite K-pop groups?
Output: Your favorite K-pop groups are: aespa, BLACKPINK, NMIXX, Hearts2Hearts, Red Velvet, ITZY, and TWICE.
```

**Educational Query (unchanged):**
```
Input: Solve x^2 + 5x + 6 = 0
Output: Routed to Math Assistant
[Full mathematical solution follows]
```

### Knowledge Base Behavior

**Important**: Understanding normal AWS Bedrock Knowledge Base behavior:

**Store Operations:**
- Complete immediately with success confirmation
- "✅ I've stored this information in your knowledge base."

**Indexing Delay:**
- **2-3 minutes** for new data to become searchable (normal AWS behavior)
- This is expected cloud service behavior, not a bug

**Retrieve Operations:**
- Only work on fully indexed data
- May return "I don't have information" immediately after storage
- Wait 2-3 minutes after storing, then retry retrieval

**Example Normal Behavior:**
```
User: "my favorite subjects are: history, literature, math"
System: "✅ I've stored this information in your knowledge base."
User: "what are my favorite subjects?" (immediately after)
System: "I don't have any information about your favorite subjects stored."
[Wait 2-3 minutes]
User: "what are my favorite subjects?" (after indexing)
System: "Your favorite subjects are history, literature, and math."
```

This demonstrates real-world cloud service behavior and is valuable for understanding production systems.

## Step 4: Production Deployment

Deploy your multi-agent system to AWS with full production infrastructure.

### What You'll Build

A production-ready deployment featuring:
- **Docker Containerization**: Containerized Streamlit application
- **AWS CDK Infrastructure**: Complete infrastructure as code
- **Cognito Authentication**: User authentication and authorization
- **ECS Fargate Hosting**: Serverless container hosting
- **CloudFront Distribution**: Global content delivery and security
- **Comprehensive Monitoring**: CloudWatch logs and metrics

### Architecture Components

**Infrastructure Stack:**
```
Internet → CloudFront → ALB → ECS Fargate → Streamlit App
    ↓           ↓        ↓         ↓            ↓
Security    Caching   Load      Container    Application
Headers     & CDN     Balancing  Hosting     + Auth
```

**AWS Services Used:**
- **Amazon ECS Fargate**: Serverless container hosting
- **Application Load Balancer**: Traffic distribution and health checks
- **Amazon CloudFront**: Global CDN with security headers
- **Amazon Cognito**: User authentication and management
- **AWS Secrets Manager**: Secure credential storage
- **Amazon VPC**: Network isolation and security
- **AWS CDK**: Infrastructure as code deployment

### Prerequisites

**AWS Permissions Required:**
- ECS, Fargate, and container registry permissions
- VPC, ALB, and networking permissions
- CloudFront and CDN permissions
- Cognito and authentication permissions
- Secrets Manager permissions
- CDK deployment permissions

**Local Requirements:**
- Docker installed and running
- AWS CDK CLI installed (`npm install -g aws-cdk`)
- Node.js for CDK operations

### Deployment Process

#### Step 1: Prepare Application

```bash
# Navigate to deployment directory
cd workshop4/deploy_multi_agent_bedrock

# Review the deployment structure
ls -la
# cdk/          - CDK infrastructure code
# docker_app/   - Containerized application
# README.md     - Deployment documentation
```

#### Step 2: Application Merge

The deployment requires merging your local application with authentication:

```bash
# The docker_app/app.py needs to be updated with your multi-agent functionality
# See APP_MERGE_GUIDE.md for detailed instructions

# Key merge points:
# 1. Keep authentication section intact
# 2. Add your application logic after authentication
# 3. Merge sidebar components carefully
# 4. Test both authentication and functionality
```

#### Step 3: Deploy Infrastructure

```bash
# Navigate to CDK directory
cd cdk

# Install CDK dependencies
npm install

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy the stack
cdk deploy

# Note the outputs:
# - CloudFront URL for accessing the application
# - ALB URL (for direct access, not recommended)
# - Cognito User Pool details
```

#### Step 4: Configure Authentication

```bash
# The CDK stack automatically creates:
# - Cognito User Pool for user management
# - Cognito User Pool Client for application integration
# - Secrets Manager entry with authentication configuration

# Create test users in Cognito console or via CLI:
aws cognito-idp admin-create-user \
  --user-pool-id <your-user-pool-id> \
  --username testuser \
  --temporary-password TempPass123! \
  --message-action SUPPRESS
```

### Production Features

**Security:**
- Cognito authentication required for all access
- CloudFront security headers (HSTS, CSP, etc.)
- ALB protected by custom headers from CloudFront
- VPC isolation with private subnets

**Scalability:**
- ECS Fargate auto-scaling based on CPU/memory
- Application Load Balancer health checks
- CloudFront global edge locations
- Container resource optimization

**Monitoring:**
- CloudWatch logs for application and infrastructure
- ECS service metrics and alarms
- ALB access logs and metrics
- Custom application metrics

**Cost Optimization:**
- Fargate Spot instances for development
- CloudFront caching to reduce origin requests
- Efficient container resource allocation
- Auto-scaling to match demand

### Accessing Your Deployment

**Production URL:**
```
https://your-cloudfront-domain.cloudfront.net
```

**Authentication Flow:**
1. Access the CloudFront URL
2. Redirect to Cognito hosted UI for login
3. After successful authentication, access the application
4. Full multi-agent functionality with knowledge base integration

**User Management:**
- Create users via Cognito console
- Users can change passwords after first login
- Self-service password reset available
- User attributes and groups supported

### Monitoring and Maintenance

**CloudWatch Logs:**
- Application logs: `/aws/ecs/multi-agent-bedrock`
- ALB access logs: Configured S3 bucket
- CloudFront logs: Optional S3 bucket

**Key Metrics to Monitor:**
- ECS service CPU and memory utilization
- ALB response times and error rates
- CloudFront cache hit ratio
- Cognito authentication success rates

**Maintenance Tasks:**
- Regular security updates for container base image
- Monitor AWS service costs and optimize
- Review and rotate secrets periodically
- Update CDK stack for new features

### Troubleshooting Production Issues

**Authentication Issues:**
- Verify Cognito User Pool configuration
- Check Secrets Manager values
- Confirm application authentication code integration

**Application Issues:**
- Check ECS service logs in CloudWatch
- Verify environment variables in task definition
- Test knowledge base connectivity from container

**Infrastructure Issues:**
- Review CDK deployment logs
- Check ALB target group health
- Verify VPC and security group configuration

## Technical Implementation Details

### Amazon Bedrock Integration

**Model Configuration:**
```python
bedrock_model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",  # Amazon Nova Pro
    temperature=0.3,
)
```

**Benefits of Nova Pro:**
- Advanced reasoning capabilities for complex queries
- Superior performance on multi-step problems
- Better understanding of specialized subject areas
- Optimized for production workloads
- Cost-effective for high-volume usage

### Tool-Agent Pattern Implementation

Each specialized agent is wrapped as a tool using the `@tool` decorator:

```python
@tool
def math_assistant(query: str) -> str:
    """Process and respond to math-related queries using a specialized math agent."""
    formatted_query = f"Please solve the following mathematical problem: {query}"
    
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

### Cross-Platform Tool Compatibility

The system uses dynamic platform detection:

```python
from cross_platform_tools import get_computer_science_tools, get_platform_capabilities

# Automatic platform detection and tool fallbacks
capabilities = get_platform_capabilities()
available_tools = get_computer_science_tools()

# Platform-aware system prompts
if not capabilities['available_tools']['python_repl']:
    platform_note += "Note: Python code execution not available. Providing code examples with explanations."
```

### Knowledge Base Integration Architecture

**Dual Routing System:**
```python
def determine_action(query):
    """Determine if query should go to educational agents or knowledge base."""
    # Uses LLM to classify query intent
    # Returns: "educational" or "knowledge_store" or "knowledge_retrieve"

def route_query(query, action):
    if action == "educational":
        return teacher_assistant(query)
    elif action in ["knowledge_store", "knowledge_retrieve"]:
        return knowledge_base_agent(query, action)
```

## Learning Outcomes

After completing Part 2, you will have mastered:

### Multi-Agent Architecture
- ✅ **Teacher's Assistant Pattern**: Central orchestrator with specialized agents
- ✅ **Tool-Agent Pattern**: Wrapping agents as tools for composition
- ✅ **Natural Language Routing**: Intelligent query classification and routing
- ✅ **Agent Specialization**: Domain-specific agents with targeted tools

### Amazon Bedrock Integration
- ✅ **Foundation Model Usage**: Amazon Nova Pro for enhanced reasoning
- ✅ **Knowledge Base Integration**: Document storage and retrieval
- ✅ **Production Deployment**: Scalable Bedrock integration patterns
- ✅ **Cost Optimization**: Efficient model usage and caching strategies

### Production Deployment
- ✅ **Containerization**: Docker-based application packaging
- ✅ **Infrastructure as Code**: AWS CDK for reproducible deployments
- ✅ **Authentication**: Cognito integration for user management
- ✅ **Scalability**: ECS Fargate with auto-scaling capabilities
- ✅ **Security**: Production-grade security headers and isolation
- ✅ **Monitoring**: CloudWatch integration for observability

### Advanced Concepts
- ✅ **Cross-Platform Development**: Platform-aware tool selection
- ✅ **Error Handling**: Robust error handling and user feedback
- ✅ **Session Management**: Conversation history and state persistence
- ✅ **Knowledge Management**: Personal information storage and retrieval
- ✅ **Dual Functionality**: Educational assistance + personal memory

## Next Steps

### Compare with SageMaker Implementation
After completing the Bedrock track, consider exploring:
- **[Part 3: Multi-Agent with Amazon SageMaker AI](PART-3-SAGEMAKER.md)** *(coming soon)*
- Compare different model hosting approaches
- Understand trade-offs between Bedrock and SageMaker
- Learn when to choose each approach

### Extend Your Implementation
**Suggested Enhancements:**
1. **Additional Specialists**: Add Science, History, or Art agents
2. **Agent Collaboration**: Enable multiple agents to work together on complex queries
3. **Advanced Memory**: Implement categorized memory with importance levels
4. **Multi-Modal Support**: Add image, audio, and document processing
5. **Performance Monitoring**: Track agent performance and response quality
6. **Cost Optimization**: Implement caching and request optimization

### Production Considerations
**For Real-World Deployment:**
1. **Security Hardening**: Implement additional security measures
2. **Compliance**: Add audit logging and compliance features
3. **Scalability**: Optimize for high-volume usage
4. **Monitoring**: Implement comprehensive observability
5. **Disaster Recovery**: Add backup and recovery procedures

## Troubleshooting

### Common Issues

**AWS Credentials:**
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check Bedrock access
aws bedrock list-foundation-models --region $AWS_REGION
```

**Model Access:**
- Ensure access to Amazon Nova Pro model in your region
- Check Amazon Bedrock console for model availability
- Verify IAM permissions for bedrock:InvokeModel

**Knowledge Base Issues:**
- Verify STRANDS_KNOWLEDGE_BASE_ID is set correctly
- Check Knowledge Base exists in your region
- Understand normal 2-3 minute indexing delay

**Cross-Platform Issues:**
- Windows users: Use provided Windows-compatible versions
- Check platform detection output for tool availability
- Verify virtual environment activation

**Production Deployment:**
- Check CDK deployment logs for infrastructure issues
- Verify Docker image builds successfully
- Test authentication flow with Cognito

### Getting Help

**Debug Information:**
```bash
# Check environment variables
env | grep AWS
env | grep STRANDS

# Verify platform capabilities
python -c "from cross_platform_tools import get_platform_capabilities; print(get_platform_capabilities())"

# Test Bedrock connectivity
aws bedrock invoke-model --region $AWS_REGION --model-id us.amazon.nova-pro-v1:0 --body '{"messages":[{"role":"user","content":[{"text":"Hello"}]}],"inferenceConfig":{"temperature":0.3}}' --cli-binary-format raw-in-base64-out output.json
```

---

**Congratulations!** 🎉

You've built a sophisticated multi-agent system with Amazon Bedrock, from CLI prototype to production deployment. This implementation demonstrates enterprise-ready patterns for AI agent coordination, natural language routing, and scalable cloud deployment.

**Next**: Explore [Part 3: Multi-Agent with Amazon SageMaker AI](PART-3-SAGEMAKER.md) *(coming soon)* to compare different model hosting approaches, or dive into the [Reference Guide](REFERENCE.md) for advanced troubleshooting and optimization techniques.