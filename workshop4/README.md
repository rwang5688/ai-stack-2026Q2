# Workshop 4: AI Application Development on AWS

Welcome to an immersive hands-on workshop for building AI applications using Strands Agents SDK with Amazon Bedrock and Amazon SageMaker AI. This workshop takes you from foundational concepts to production-ready multi-agent systems through a carefully structured learning journey.

## 🎯 Workshop Learning Journey

This workshop is designed as a progressive learning experience. **Follow the path that matches your goals:**

### 🚀 **Start Here** → [Getting Started Guide](GETTING-STARTED.md)
Set up your development environment, install prerequisites, and verify your setup works correctly.

### 📚 **Learn Foundations**

Learn the the foundations of building agents with Strands Agents SDK.

#### 📚 **Part 1: Foundational Modules** → [PART-1-FOUNDATIONS.md](PART-1-FOUNDATIONS.md)
Master the building blocks through hands-on modules:
- **Module 1**: MCP Calculator - Basic tool creation and usage
- **Module 2**: Weather Agent - External API integration  
- **Module 3**: Knowledge Base Agent - Document retrieval capabilities
- **Module 4**: Agent Workflows - Orchestration patterns
- **Module 5**: Memory Agent - Persistent state management
- **Module 6**: Meta-Tooling Agent - Dynamic tool creation

**Implementation**: [`modules/`](modules/)

### 🎓 **Build Multi-Agent Applications**

After completing the foundations, build production-ready multi-agent systems:

#### 🔷 **Part 2: Multi-Agent Application** → [PART-2-MULTI-AGENT.md](PART-2-MULTI-AGENT.md)
Run the multi-agent system locally with model selection:
- **Streamlit Web Interface** with conversation management
- **Model Selection**: Choose between Bedrock and SageMaker models
- **5 Specialized Agents**: Math, English, Language, Computer Science, General
- **Knowledge Base Integration**: Personal information storage and retrieval
- **Agent Type Selection**: Auto-Route, Teacher Agent, or Knowledge Base
- **Testing and Debugging**: Validate all features work correctly

**Implementation**: [`multi_agent/`](multi_agent/)

#### 🔶 **Part 3: Production Deployment** → [PART-3-DEPLOY-MULTI-AGENT.md](PART-3-DEPLOY-MULTI-AGENT.md)
Deploy the multi-agent system to production:
- **Docker Containerization**: Package application for deployment
- **AWS CDK Infrastructure**: Automated infrastructure provisioning
- **ECS Fargate Hosting**: Serverless container hosting
- **Cognito Authentication**: Secure user authentication
- **CloudFront Distribution**: Global content delivery
- **Comprehensive Monitoring**: CloudWatch logs and metrics

**Implementation**: [`deploy_multi_agent/`](deploy_multi_agent/)

### 🔧 **Need Help?** → [Reference Guide](REFERENCE.md)
Comprehensive troubleshooting, cross-platform compatibility, authentication details, and technical reference.

## 🏗️ Workshop Architecture

### Multi-Agent System Pattern
The application implements the **Teacher's Assistant Pattern**:
- **Central Orchestrator**: Routes queries using natural language understanding
- **5 Specialized Agents**: Math, English, Language, Computer Science, General
- **Tool-Agent Pattern**: Agents wrapped as tools using `@tool` decorator
- **Knowledge Base Integration**: Personal information storage and retrieval
- **Model Flexibility**: Supports both Amazon Bedrock and Amazon SageMaker AI models
- **Production Ready**: Full deployment pipeline with authentication

### Progressive Complexity
```
Foundations (Modules 1-6) → Local Multi-Agent App → Production Deployment
```

## 📁 Repository Structure

```
workshop4/
├── README.md                         # This file - workshop overview
├── GETTING-STARTED.md               # Environment setup and prerequisites
├── PART-1-FOUNDATIONS.md            # Foundational modules guide
├── PART-2-MULTI-AGENT.md            # Local multi-agent application guide
├── PART-3-DEPLOY-MULTI-AGENT.md     # Production deployment guide
├── REFERENCE.md                      # Technical reference and troubleshooting
├── modules/                          # Foundational modules 1-6 source code
├── multi_agent/                     # Multi-agent application (local development)
├── deploy_multi_agent/              # Production deployment (Docker + AWS CDK)
├── validation/                      # Validation scripts (SSM + endpoints)
└── ssm/                             # SSM Parameter Store CloudFormation
```

## ⚡ Quick Start Options

### Option 1: Complete Workshop Journey (Recommended)
1. [Getting Started](GETTING-STARTED.md) → Environment setup + validation
2. [Part 1: Foundations](PART-1-FOUNDATIONS.md) → Complete modules 1-6
3. [Part 2: Multi-Agent](PART-2-MULTI-AGENT.md) → Run application locally
4. [Part 3: Deploy](PART-3-DEPLOY-MULTI-AGENT.md) → Deploy to production

### Option 2: Jump to Multi-Agent (If Experienced)
1. [Getting Started](GETTING-STARTED.md) → Quick environment setup + validation
2. Skip to [Part 2: Multi-Agent](PART-2-MULTI-AGENT.md)
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
- ✅ **Bedrock Models**: Foundation model hosting and inference
- ✅ **SageMaker Models**: Custom model training and deployment
- ✅ **Model Selection**: Dynamic switching between model providers
- ✅ **Unified Architecture**: Single codebase supporting multiple providers

## 🚀 Ready to Begin?

**Start your journey**: [Getting Started Guide](GETTING-STARTED.md)

---

*This workshop provides hands-on experience with cutting-edge AI agent development patterns used in production systems. Each module builds upon the previous, creating a comprehensive learning experience from basics to advanced deployment.*
