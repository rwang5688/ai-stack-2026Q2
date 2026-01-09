# Requirements Document

## Introduction

This specification defines the requirements for simplifying and refactoring the Workshop 4 multi-agent architecture to better illustrate deployment patterns and model choice capabilities. The refactoring involves renaming directories for generic naming, adding model choice between Bedrock and SageMaker AI, preparing for future Bedrock AgentCore integration, and adding MCP-enabled Lambda functions with classification models.

## Glossary

- **Deploy_Multi_Agent**: Renamed from "deploy_multi_agent_bedrock" - the deployable Streamlit app with Cognito authentication
- **Multi_Agent**: Renamed from "multi_agent_bedrock" - the local Streamlit app for development
- **Strands_Agents**: Multi-agent framework that will run on Bedrock AgentCore in future iterations
- **Model_Choice**: Capability to select between Bedrock models (Nova Pro) and SageMaker AI models (GPT OSS)
- **Bedrock_AgentCore**: AWS service for running Strands Agents with scalability, resilience, and observability
- **MCP_Lambda**: MCPified Lambda function that wraps around a SageMaker AI trained classification model
- **AgentCore_Gateway**: Bedrock AgentCore Gateway for integrating MCP-enabled Lambda functions
- **Classification_Model**: SageMaker AI trained model for classification tasks integrated via MCP Lambda
- **Cognito_Authentication**: AWS Cognito integration for user authentication in deployed applications
- **Local_Development**: Local Streamlit app environment for development and testing

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

**User Story:** As a system architect, I want to prepare the architecture for Bedrock AgentCore integration, so that Strands Agents can run with enterprise-grade scalability and observability.

#### Acceptance Criteria

1. WHEN preparing for AgentCore THEN the Deploy_Multi_Agent SHALL maintain Strands Agents as part of the Streamlit app initially
2. WHEN designing for future migration THEN the Deploy_Multi_Agent SHALL structure agent code for easy extraction to AgentCore
3. WHEN implementing current version THEN the Deploy_Multi_Agent SHALL document the planned AgentCore migration path
4. WHERE agent separation is needed THEN the Deploy_Multi_Agent SHALL use modular design patterns that support future AgentCore deployment
5. WHILE maintaining current functionality THEN the Deploy_Multi_Agent SHALL preserve all existing multi-agent capabilities

### Requirement 4

**User Story:** As a developer, I want to integrate MCP-enabled Lambda functions with classification models, so that I can demonstrate advanced agent tooling with machine learning capabilities.

#### Acceptance Criteria

1. WHEN creating MCP Lambda THEN the System SHALL implement MCPified Lambda function that wraps a SageMaker AI trained classification model
2. WHEN integrating with AgentCore Gateway THEN the MCP_Lambda SHALL connect through Bedrock AgentCore Gateway for agent access
3. WHEN performing classification THEN the Classification_Model SHALL provide accurate classification results through the MCP interface
4. WHEN agents use classification THEN the Multi_Agent SHALL demonstrate agent access to classification capabilities via MCP tools
5. WHERE model training is needed THEN the System SHALL provide or reference a trained SageMaker AI classification model

### Requirement 5

**User Story:** As a workshop participant, I want to understand the difference between local development and deployed applications, so that I can learn about different deployment patterns and authentication methods.

#### Acceptance Criteria

1. WHEN running locally THEN the Multi_Agent SHALL operate without authentication requirements for development ease
2. WHEN deploying to production THEN the Deploy_Multi_Agent SHALL integrate AWS Cognito authentication for secure access
3. WHEN comparing environments THEN the System SHALL clearly document the differences between local and deployed configurations
4. WHEN switching between environments THEN the System SHALL provide clear setup instructions for both local and deployed scenarios
5. WHERE authentication is required THEN the Deploy_Multi_Agent SHALL implement proper Cognito user management and session handling

### Requirement 6

**User Story:** As a system administrator, I want modular architecture components, so that I can easily configure and deploy different combinations of agents, models, and services.

#### Acceptance Criteria

1. WHEN configuring agents THEN the System SHALL support modular agent selection and configuration
2. WHEN selecting models THEN the System SHALL provide pluggable model interfaces for easy switching between Bedrock and SageMaker AI
3. WHEN deploying services THEN the System SHALL support independent deployment of different system components
4. WHEN integrating tools THEN the System SHALL provide standardized interfaces for MCP tool integration
5. WHERE customization is needed THEN the System SHALL support configuration-driven customization without code changes

### Requirement 7

**User Story:** As a developer, I want comprehensive documentation of the simplified architecture, so that I can understand the design decisions and implementation patterns.

#### Acceptance Criteria

1. WHEN accessing documentation THEN the System SHALL provide clear architecture diagrams showing the simplified design
2. WHEN understanding model choice THEN the System SHALL document the differences between Bedrock and SageMaker AI integration patterns
3. WHEN planning AgentCore migration THEN the System SHALL provide detailed migration path documentation
4. WHEN implementing MCP Lambda THEN the System SHALL provide complete setup and integration guides
5. WHERE troubleshooting is needed THEN the System SHALL provide comprehensive troubleshooting guides for all components