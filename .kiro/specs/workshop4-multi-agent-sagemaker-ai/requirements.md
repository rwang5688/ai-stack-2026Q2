# Requirements Document

## Introduction

This specification defines the requirements for creating Module 7: Building Multi-Agent with Strands using Amazon SageMaker AI model hosting. This implementation serves as a side-by-side analog to the Bedrock version, following the same 6-step progressive approach: (1) CLI multi-agent system using Teacher's Assistant pattern, (2) Streamlit web interface integration, (3) knowledge base enhancement, (4) Memory integration and enhanced UI features, (5) production deployment using AWS CDK, Docker, and ECS Fargate, and (6) comprehensive documentation and workshop materials. The key difference is using SageMaker AI (JumpStart) models instead of Bedrock models.

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

**User Story:** As a workshop instructor, I want a 6-step progressive multi-agent workshop using Strands Agents SDK with Amazon SageMaker AI, so that I can teach students how to build from basic CLI agents to production-deployed web applications using SageMaker models.

#### Acceptance Criteria

1. WHEN the workshop materials are accessed THEN the Workshop System SHALL provide complete documentation for the 6-step progression (CLI → UI → Knowledge → Memory/UI → Deployment → Documentation) using SageMaker AI models
2. WHEN students complete Step 1 THEN the Workshop System SHALL enable successful implementation of the Teacher's Assistant pattern with 5 specialized agents using SageMaker JumpStart models
3. WHEN students complete Step 2 THEN the Workshop System SHALL enable successful integration of Streamlit web UI with the SageMaker-based multi-agent system
4. WHEN students complete Step 3 THEN the Workshop System SHALL enable successful integration of knowledge base capabilities with SageMaker AI model hosting
5. WHEN students complete Step 4 THEN the Workshop System SHALL enable successful integration of memory capabilities with SageMaker model selection and agent customization
6. WHEN students complete Step 5 THEN the Workshop System SHALL enable successful deployment using AWS CDK, Docker, and ECS Fargate with SageMaker model integration
7. WHEN students complete Step 6 THEN the Workshop System SHALL provide comprehensive documentation and workshop materials for instructor delivery

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

**User Story:** As a student, I want to add memory capabilities and enhanced UI features to my SageMaker-based multi-agent system, so that I can understand memory integration, model selection, and agent customization patterns with SageMaker AI.

#### Acceptance Criteria

1. WHEN implementing memory THEN the Workshop System SHALL demonstrate integrating memory agent capabilities from module5 with OpenSearch backend support for SageMaker-based agents
2. WHEN selecting models THEN the Workshop System SHALL provide dropdown selection for multiple SageMaker JumpStart model IDs and endpoint configurations
3. WHEN customizing agents THEN the Workshop System SHALL enable toggling individual teacher agents (math, language, computer science, english) on and off with SageMaker models
4. WHEN OpenSearch is unavailable THEN the Workshop System SHALL gracefully disable OpenSearch backend option if OPENSEARCH_HOST environment variable is not defined
5. WHILE using memory features THEN the Workshop System SHALL maintain compatibility with existing knowledge base and teacher agent functionality using SageMaker AI

### Requirement 6

**User Story:** As a technical lead, I want reusable multi-agent patterns and flexible configuration options for SageMaker AI, so that I can adapt the system for different business contexts and deployment scenarios.

#### Acceptance Criteria

1. WHEN customizing agents THEN the Workshop System SHALL support modular specialized agent creation and configuration with toggle controls for SageMaker models
2. WHEN adapting for use cases THEN the Workshop System SHALL provide configurable agent roles, tools, system prompts, and SageMaker model selection
3. WHEN integrating memory systems THEN the Workshop System SHALL provide clear patterns for memory integration with fallback options for SageMaker-based agents
4. WHEN integrating with existing systems THEN the Workshop System SHALL provide clear APIs and interfaces for extending the SageMaker-based multi-agent system
5. WHERE performance optimization is required THEN the Workshop System SHALL provide guidance on SageMaker AI model selection, endpoint configuration, memory backends, and system tuning

### Requirement 7

**User Story:** As a student, I want to deploy my enhanced SageMaker-based multi-agent system to production, so that I can understand containerization and AWS deployment patterns with full SageMaker AI integration.

#### Acceptance Criteria

1. WHEN containerizing the application THEN the Workshop System SHALL show how to create a Docker container for the Streamlit multi-agent application with SageMaker AI and memory integration
2. WHEN deploying infrastructure THEN the Workshop System SHALL provide AWS CDK code for provisioning ECS Fargate cluster with SageMaker AI access and memory backend support
3. WHEN deploying to production THEN the Workshop System SHALL enable successful deployment of the containerized SageMaker-based application to AWS ECS Fargate
4. WHEN monitoring the deployment THEN the Workshop System SHALL include monitoring, logging, and alerting for the SageMaker AI production environment
5. WHILE maintaining the deployment THEN the Workshop System SHALL include cleanup and maintenance procedures for the SageMaker AI production environment

### Requirement 8

**User Story:** As a workshop instructor, I want comprehensive documentation and materials for the SageMaker AI workshop, so that I can deliver the workshop effectively and students can reference complete guides.

#### Acceptance Criteria

1. WHEN accessing workshop materials THEN the Workshop System SHALL provide complete 6-step workshop documentation with SageMaker AI setup guides
2. WHEN following tutorials THEN the Workshop System SHALL provide detailed step-by-step instructions with clear progression for SageMaker AI integration
3. WHEN troubleshooting issues THEN the Workshop System SHALL provide comprehensive FAQ and troubleshooting documentation for SageMaker AI and memory integration
4. WHEN preparing for instruction THEN the Workshop System SHALL provide instructor guides and presentation materials for SageMaker AI workshop delivery
5. WHERE customization is needed THEN the Workshop System SHALL provide modular component documentation and adaptation guides for SageMaker AI implementations