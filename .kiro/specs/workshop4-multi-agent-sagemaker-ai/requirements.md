# Requirements Document

## Introduction

This specification defines the requirements for creating Module 7: Building Multi-Agent with Strands using Amazon SageMaker AI model hosting. This implementation serves as a side-by-side analog to the Bedrock version, following the same 4-step progressive approach: (1) CLI multi-agent system using Teacher's Assistant pattern, (2) Streamlit web interface integration, (3) knowledge base enhancement, and (4) production deployment using AWS CDK, Docker, and ECS Fargate. The key difference is using SageMaker AI (JumpStart) models instead of Bedrock models.

## Glossary

- **Strands Agents SDK**: Software development kit providing the multi-agent framework and coordination capabilities
- **Amazon SageMaker AI**: AWS managed machine learning service for building, training, and deploying ML models for agent model hosting
- **SageMaker JumpStart**: Pre-built ML solutions and foundation models available in SageMaker for agent model hosting
- **Teacher's Assistant Pattern**: Multi-agent architecture with one orchestrator agent routing queries to specialized agents
- **Tool-Agent Pattern**: Design pattern where Strands agents are wrapped as tools using the @tool decorator
- **Specialized Agents**: Domain-specific agents (Math, English, Language, Computer Science, General) with targeted capabilities
- **Streamlit UI**: Web-based user interface for interacting with the multi-agent system
- **Knowledge Base**: Document storage and retrieval system integrated with agents (SageMaker equivalent to Bedrock Knowledge Base)
- **ECS Fargate**: AWS container service for deploying the production multi-agent application
- **Workshop System**: The complete educational platform including materials, code examples, and infrastructure

## Requirements

### Requirement 1

**User Story:** As a workshop instructor, I want a 4-step progressive multi-agent workshop using Strands Agents SDK with Amazon SageMaker AI, so that I can teach students how to build from basic CLI agents to production-deployed web applications using SageMaker models.

#### Acceptance Criteria

1. WHEN the workshop materials are accessed THEN the Workshop System SHALL provide complete documentation for the 4-step progression (CLI → UI → Knowledge → Deployment) using SageMaker AI models
2. WHEN students complete Step 1 THEN the Workshop System SHALL enable successful implementation of the Teacher's Assistant pattern with 5 specialized agents using SageMaker JumpStart models
3. WHEN students complete Step 2 THEN the Workshop System SHALL enable successful integration of Streamlit web UI with the SageMaker-based multi-agent system
4. WHEN students complete Step 3 THEN the Workshop System SHALL enable successful integration of knowledge base capabilities with SageMaker AI model hosting
5. WHEN students complete Step 4 THEN the Workshop System SHALL enable successful deployment using AWS CDK, Docker, and ECS Fargate with SageMaker model integration

### Requirement 2

**User Story:** As a student, I want to implement the Teacher's Assistant multi-agent pattern using Strands Agents SDK with SageMaker AI models, so that I can understand the Tool-Agent Pattern and natural language routing with custom model hosting.

#### Acceptance Criteria

1. WHEN implementing the orchestrator THEN the Workshop System SHALL demonstrate creating a Teacher's Assistant agent that routes queries using natural language with SageMaker JumpStart models
2. WHEN implementing specialized agents THEN the Workshop System SHALL show how to create 5 domain-specific agents (Math, English, Language, Computer Science, General) using SageMaker AI models with the @tool decorator
3. WHEN agents use tools THEN the Workshop System SHALL demonstrate proper tool integration (calculator, python_repl, shell, http_request, editor, file operations) with SageMaker model hosting
4. WHEN testing interactions THEN the Workshop System SHALL enable command-line testing with sample queries for each specialized domain using SageMaker models
5. WHILE agents collaborate THEN the Workshop System SHALL maintain clean output by suppressing intermediate agent outputs using callback_handler=None

### Requirement 3

**User Story:** As a student, I want to add a Streamlit web interface to my SageMaker-based multi-agent system, so that I can understand how to create user-friendly interfaces for agent interactions with custom model hosting.

#### Acceptance Criteria

1. WHEN creating the web interface THEN the Workshop System SHALL demonstrate building a Streamlit app that integrates with the SageMaker-based Teacher's Assistant system
2. WHEN users interact with the UI THEN the Workshop System SHALL provide a clean web interface for submitting queries and viewing SageMaker model-powered agent responses
3. WHEN displaying results THEN the Workshop System SHALL show proper formatting of SageMaker agent responses in the web interface
4. WHEN handling errors THEN the Workshop System SHALL provide appropriate error handling and user feedback for SageMaker model integration issues
5. WHERE UI enhancements are needed THEN the Workshop System SHALL support customization of the Streamlit interface for SageMaker workflows

### Requirement 4

**User Story:** As a student, I want to integrate knowledge base capabilities with my SageMaker-based multi-agent system, so that I can understand how to enhance agents with document retrieval using SageMaker AI infrastructure.

#### Acceptance Criteria

1. WHEN setting up knowledge capabilities THEN the Workshop System SHALL demonstrate creating knowledge base functionality compatible with SageMaker AI model hosting
2. WHEN integrating with agents THEN the Workshop System SHALL show how to enhance SageMaker-based specialized agents with knowledge retrieval capabilities
3. WHEN querying documents THEN the Workshop System SHALL enable SageMaker-powered agents to retrieve and use relevant document information in their responses
4. WHEN managing documents THEN the Workshop System SHALL provide guidance on document storage and retrieval integration with SageMaker AI workflows
5. WHERE knowledge enhancement is needed THEN the Workshop System SHALL support extending other specialized agents with knowledge base integration using SageMaker models

### Requirement 5

**User Story:** As a student, I want to add memory capabilities and deploy my SageMaker-based multi-agent system to production, so that I can understand session persistence and AWS deployment patterns with SageMaker AI integration.

#### Acceptance Criteria

1. WHEN implementing memory THEN the Workshop System SHALL demonstrate adding session memory and conversation persistence to the SageMaker-based multi-agent system
2. WHEN containerizing the application THEN the Workshop System SHALL show how to create a Docker container for the Streamlit multi-agent application with SageMaker AI integration
3. WHEN deploying infrastructure THEN the Workshop System SHALL provide AWS CDK code for provisioning ECS Fargate cluster with SageMaker AI access and supporting resources
4. WHEN deploying to production THEN the Workshop System SHALL enable successful deployment of the containerized SageMaker-based application to AWS ECS Fargate
5. WHILE maintaining the deployment THEN the Workshop System SHALL include monitoring, logging, and cleanup procedures for the SageMaker AI production environment

### Requirement 6

**User Story:** As a technical lead, I want reusable multi-agent patterns and deployment components for SageMaker AI, so that I can adapt the SageMaker implementation for different business contexts and deployment scenarios.

#### Acceptance Criteria

1. WHEN customizing agents THEN the Workshop System SHALL support modular specialized agent creation and configuration with SageMaker AI models
2. WHEN adapting for use cases THEN the Workshop System SHALL provide configurable agent roles, tools, and system prompts optimized for SageMaker JumpStart models
3. WHEN reusing deployment patterns THEN the Workshop System SHALL maintain clear separation between application logic and SageMaker AI infrastructure deployment
4. WHEN integrating with existing systems THEN the Workshop System SHALL provide clear APIs and interfaces for extending the SageMaker-based multi-agent system
5. WHERE performance optimization is required THEN the Workshop System SHALL provide guidance on SageMaker AI model selection, endpoint configuration, and system tuning