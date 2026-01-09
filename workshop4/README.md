# Workshop 4: AI Application Development on AWS

Welcome to an immersive hands-on workshop for building AI applications using Strands Agents SDK with Amazon Bedrock and Amazon SageMaker AI. This workshop takes you from foundational concepts to production-ready multi-agent systems through a carefully structured learning journey.

## 🎯 Workshop Learning Journey

This workshop is designed as a progressive learning experience. **Follow the path that matches your goals:**

### 🚀 **Start Here** → [Getting Started Guide](GETTING-STARTED.md)
Set up your development environment, install prerequisites, and verify your setup works correctly.

### 📚 **Learn Foundations** → [Part 1: Foundational Modules](PART-1-FOUNDATIONS.md)
Master the building blocks through hands-on modules:
- **Module 1**: MCP Calculator - Basic tool creation and usage
- **Module 2**: Weather Agent - External API integration  
- **Module 3**: Knowledge Base Agent - Document retrieval capabilities
- **Module 4**: Agent Workflows - Orchestration patterns
- **Module 5**: Memory Agent - Persistent state management
- **Module 6**: Meta-Tooling Agent - Dynamic tool creation
- **Module 8**: MCPify Lambda - Serverless MCP tools *(coming soon)*

### 🎓 **Choose Your Advanced Track**

After completing the foundations, choose your preferred AI model hosting approach:

#### 🔷 **Bedrock Track** → [Part 2: Multi-Agent with Amazon Bedrock](PART-2-BEDROCK.md)
Build sophisticated multi-agent systems using Amazon Bedrock foundation models:
- **Step 1**: CLI Multi-Agent System with Teacher's Assistant pattern
- **Step 2**: Streamlit Web Interface with conversation management
- **Step 3**: Knowledge Base Integration for personal information storage
- **Step 4**: Enhanced UI with model selection and agent customization
- **Step 5**: Production Deployment with Docker + AWS CDK + ECS Fargate
- **Step 6**: Workshop Materials and documentation

**Implementation**: [`multi_agent_bedrock/`](multi_agent_bedrock/) → [`deploy_multi_agent_bedrock/`](deploy_multi_agent_bedrock/)

#### 🔶 **SageMaker Track** → [Part 3: Multi-Agent with Amazon SageMaker AI](PART-3-SAGEMAKER.md) *(coming soon)*
Build the same multi-agent system using Amazon SageMaker AI (JumpStart) models:
- **Same 6-step progression** as Bedrock track
- **SageMaker JumpStart models** instead of Bedrock foundation models
- **Side-by-side comparison** to understand different hosting approaches

**Implementation**: `multi_agent_sagemaker_ai/` → `deploy_multi_agent_sagemaker_ai/` *(coming soon)*

### 🔧 **Need Help?** → [Reference Guide](REFERENCE.md)
Comprehensive troubleshooting, cross-platform compatibility, authentication details, and technical reference.

## 🏗️ Workshop Architecture

### Multi-Agent System Pattern
Both tracks implement the **Teacher's Assistant Pattern**:
- **Central Orchestrator**: Routes queries using natural language understanding
- **5 Specialized Agents**: Math, English, Language, Computer Science, General
- **Tool-Agent Pattern**: Agents wrapped as tools using `@tool` decorator
- **Knowledge Base Integration**: Personal information storage and retrieval
- **Production Ready**: Full deployment pipeline with authentication

### Progressive Complexity
```
Foundations (Modules 1-6, 8) → Multi-Agent CLI → Web Interface → Knowledge Base → Enhanced UI → Production
```

## 📁 Repository Structure

```
workshop4/
├── README.md                         # This file - workshop overview
├── GETTING-STARTED.md               # Environment setup and prerequisites
├── PART-1-FOUNDATIONS.md            # Foundational modules guide
├── PART-2-BEDROCK.md                # Complete Bedrock multi-agent guide
├── PART-3-SAGEMAKER.md              # Complete SageMaker multi-agent guide
├── REFERENCE.md                      # Technical reference and troubleshooting
├── modules/                          # Foundational modules 1-6, 8 source code
├── multi_agent_bedrock/             # Bedrock implementation source code
├── deploy_multi_agent_bedrock/      # Bedrock production deployment
├── multi_agent_sagemaker_ai/        # SageMaker implementation (coming soon)
└── deploy_multi_agent_sagemaker_ai/ # SageMaker production deployment (coming soon)
```

## ⚡ Quick Start Options

### Option 1: Complete Workshop Journey (Recommended)
1. [Getting Started](GETTING-STARTED.md) → Environment setup
2. [Part 1: Foundations](PART-1-FOUNDATIONS.md) → Complete modules 1-6
3. Choose [Bedrock](PART-2-BEDROCK.md) or [SageMaker](PART-3-SAGEMAKER.md) track
4. Build and deploy your multi-agent system

### Option 2: Jump to Multi-Agent (If Experienced)
1. [Getting Started](GETTING-STARTED.md) → Quick environment setup
2. Skip to [Bedrock](PART-2-BEDROCK.md) or [SageMaker](PART-3-SAGEMAKER.md) track
3. Reference [Foundations](PART-1-FOUNDATIONS.md) as needed

### Option 3: Specific Module Focus
1. [Getting Started](GETTING-STARTED.md) → Environment setup
2. [Part 1: Foundations](PART-1-FOUNDATIONS.md) → Choose specific modules
3. Use [Reference](REFERENCE.md) for troubleshooting

## 🎯 Learning Objectives

By completing this workshop, you will:

### Foundational Skills
- ✅ Master Strands Agents SDK fundamentals
- ✅ Create and integrate MCP tools
- ✅ Build agent workflows and orchestration patterns
- ✅ Handle cross-platform development challenges

### Advanced Multi-Agent Systems
- ✅ Implement Teacher's Assistant coordination pattern
- ✅ Use Tool-Agent Pattern with `@tool` decorator
- ✅ Build natural language query routing
- ✅ Integrate knowledge base capabilities
- ✅ Deploy production-ready applications

### Model Integration Expertise
- ✅ **Bedrock Track**: Foundation model hosting and inference
- ✅ **SageMaker Track**: Custom model training and JumpStart deployment
- ✅ **Comparison**: Understand trade-offs between hosting approaches

## 🚀 Ready to Begin?

**Start your journey**: [Getting Started Guide](GETTING-STARTED.md)

---

*This workshop provides hands-on experience with cutting-edge AI agent development patterns used in production systems. Each module builds upon the previous, creating a comprehensive learning experience from basics to advanced deployment.*
