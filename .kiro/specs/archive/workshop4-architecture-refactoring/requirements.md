# Requirements Document

## Introduction

This specification defines the requirements for simplifying and refactoring the Workshop 4 multi-agent architecture to focus on monolithic Streamlit applications that orchestrate multiple Strands Agents within a single deployment. The refactoring avoids Bedrock AgentCore complexity to better align with DATASCI 210 course objectives of model training, deployment, and agentic application development. The simplified architecture maintains model choice capabilities between Bedrock and SageMaker AI while focusing on practical application development patterns.

## Glossary

- **Deploy_Multi_Agent**: Renamed from "deploy_multi_agent_bedrock" - the deployable Streamlit app with Cognito authentication
- **Multi_Agent**: Renamed from "multi_agent_bedrock" - the local Streamlit app for development
- **Strands_Agents**: Multi-agent framework running embedded within the Streamlit application
- **Model_Choice**: Capability to select between Bedrock models (Nova Pro) and SageMaker AI models (GPT OSS)
- **Monolithic_Application**: Single Streamlit app that orchestrates multiple agents within one deployment
- **ECS_Fargate**: AWS container hosting service for deploying the monolithic application
- **Local_Development**: Local Streamlit app environment for development and testing
- **Cognito_Authentication**: AWS Cognito integration for user authentication in deployed applications

## Requirements

### Requirement 1

**User Story:** As a workshop instructor, I want to rename directories to use generic naming conventions, so that the architecture can illustrate different deployment patterns without being tied to specific cloud services.

#### Acceptance Criteria

1. WHEN renaming directories THEN the System SHALL change "deploy_multi_agent_bedrock" to "deploy_multi_agent"
2. WHEN renaming directories THEN the System SHALL change "multi_agent_bedrock" to "multi_agent"
3. WHEN updating references THEN the System SHALL update all file imports, documentation, and configuration files to use the new directory names
4. WHEN maintaining functionality THEN the System SHALL preserve all existing functionality during the rename process
5. WHERE documentation exists THEN the System SHALL update all README files and documentation to reflect the new naming convention

### Requirement 2

**User Story:** As a developer, I want to add model choice capabilities to the local Streamlit app, so that I can compare Bedrock models with SageMaker AI models for different use cases.

#### Acceptance Criteria

1. WHEN selecting models THEN the Multi_Agent SHALL provide dropdown selection between Bedrock Nova Pro and SageMaker AI GPT OSS models
2. WHEN using Bedrock models THEN the Multi_Agent SHALL maintain existing Bedrock integration and functionality
3. WHEN using SageMaker AI models THEN the Multi_Agent SHALL integrate with SageMaker AI endpoints for GPT OSS model access
4. WHEN switching models THEN the Multi_Agent SHALL update all agent configurations to use the selected model type
5. WHERE model configuration is needed THEN the Multi_Agent SHALL provide clear model selection interface and status indicators

### Requirement 3

**User Story:** As a course instructor, I want to maintain a monolithic application architecture, so that students can focus on model training, deployment, and application development without microservice complexity.

#### Acceptance Criteria

1. WHEN building the application THEN the Deploy_Multi_Agent SHALL maintain Strands Agents embedded within the Streamlit application
2. WHEN deploying to production THEN the Deploy_Multi_Agent SHALL run as a single ECS Fargate task with all agents included
3. WHEN developing locally THEN the Multi_Agent SHALL provide the same agent orchestration patterns as production
4. WHERE agent coordination is needed THEN the application SHALL use in-process communication rather than distributed service calls
5. WHILE maintaining functionality THEN the application SHALL preserve all existing multi-agent capabilities within the monolithic architecture

### Requirement 4

**User Story:** As a developer, I want to focus on core AI/ML capabilities, so that I can concentrate on model training, deployment, and practical application development without distributed system complexity.

#### Acceptance Criteria

1. WHEN building applications THEN the System SHALL remove references to Bedrock AgentCore from documentation and code
2. WHEN learning about deployment THEN the System SHALL focus on ECS Fargate deployment patterns for monolithic applications
3. WHEN working with agents THEN the System SHALL demonstrate Strands Agents coordination within a single application process
4. WHEN integrating models THEN the System SHALL show direct integration with Bedrock and SageMaker AI services
5. WHERE complexity exists THEN the System SHALL focus complexity on AI/ML model usage rather than microservice orchestration

### Requirement 5

**User Story:** As a workshop participant, I want to understand the difference between local development and deployed applications, so that I can learn about different deployment patterns and authentication methods.

#### Acceptance Criteria

1. WHEN running locally THEN the Multi_Agent SHALL operate without authentication requirements for development ease
2. WHEN deploying to production THEN the Deploy_Multi_Agent SHALL integrate AWS Cognito authentication for secure access
3. WHEN comparing environments THEN the System SHALL clearly document the differences between local and deployed configurations
4. WHEN switching between environments THEN the System SHALL provide clear setup instructions for both local and deployed scenarios
5. WHERE authentication is required THEN the Deploy_Multi_Agent SHALL implement proper Cognito user management and session handling

### Requirement 6

**User Story:** As a system administrator, I want simplified deployment architecture, so that I can easily configure and deploy applications without managing distributed service dependencies.

#### Acceptance Criteria

1. WHEN configuring applications THEN the System SHALL support modular agent selection within the monolithic application
2. WHEN selecting models THEN the System SHALL provide pluggable model interfaces for easy switching between Bedrock and SageMaker AI
3. WHEN deploying services THEN the System SHALL support single-container deployment with all components included
4. WHEN integrating tools THEN the System SHALL provide in-process tool integration without external service dependencies
5. WHERE customization is needed THEN the System SHALL support configuration-driven customization within the application

### Requirement 7

**User Story:** As a developer, I want comprehensive documentation of the simplified monolithic architecture, so that I can understand the design decisions and implementation patterns for practical AI application development.

#### Acceptance Criteria

1. WHEN accessing documentation THEN the System SHALL provide clear architecture diagrams showing the monolithic design
2. WHEN understanding model choice THEN the System SHALL document the differences between Bedrock and SageMaker AI integration patterns
3. WHEN learning deployment THEN the System SHALL provide detailed ECS Fargate deployment documentation
4. WHEN building applications THEN the System SHALL provide complete setup and integration guides for monolithic applications
5. WHERE troubleshooting is needed THEN the System SHALL provide comprehensive troubleshooting guides focused on single-application deployment