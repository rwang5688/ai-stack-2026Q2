# Requirements Document

## Introduction

This feature expands the workshop4 multi-agent application to support multiple reasoning LLM choices (Amazon Bedrock and Amazon SageMaker) and adds a loan prediction assistant that integrates with a SageMaker XGBoost model. The goal is to demonstrate the flexibility of the Strands Agents framework with respect to reasoning LLMs and showcase integration of team-trained predictive models into multi-agent applications.

## Glossary

- **Strands_Agent_Model**: The language model used by Strands Agents to process natural language, make decisions, and generate responses
- **Model_Provider**: The service providing the Strands Agent model (Amazon Bedrock or Amazon SageMaker)
- **Bedrock_Model**: An Amazon Bedrock foundation model accessed via cross-region inference profiles
- **SageMaker_Model**: A model deployed on Amazon SageMaker and accessed via inference endpoints
- **XGBoost_Model**: A gradient boosted tree model trained for binary classification (loan acceptance prediction)
- **Serverless_Endpoint**: A SageMaker inference endpoint that automatically scales based on demand
- **Loan_Assistant**: A specialized agent that predicts loan acceptance using the XGBoost model
- **Multi_Agent_App**: The Streamlit application that orchestrates multiple specialized agents
- **Config_Module**: A Python module that centralizes environment variable management
- **Cross_Region_Profile**: A Bedrock inference profile that enables multi-region model access

## Requirements

### Requirement 1: Configuration Management

**User Story:** As a developer, I want centralized configuration management, so that environment variables are consistently accessed and validated across the application.

#### Acceptance Criteria

1. THE Config_Module SHALL provide getter functions for all environment variables used by the application
2. THE Config_Module SHALL manage the following environment variables:
   - AWS_REGION: AWS region for all services
   - BEDROCK_MODEL_ID: Bedrock model ID or cross-region profile
   - MAX_RESULTS: Maximum results for knowledge base queries
   - MIN_SCORE: Minimum score threshold for knowledge base queries
   - SAGEMAKER_MODEL_ENDPOINT: SageMaker model endpoint name
   - STRANDS_KNOWLEDGE_BASE_ID: Strands knowledge base ID
   - STRANDS_MODEL_PROVIDER: Model provider choice (bedrock or sagemaker)
   - XGBOOST_ENDPOINT_NAME: XGBoost loan prediction endpoint name
3. WHEN an environment variable is missing, THE Config_Module SHALL return a sensible default value or raise a descriptive error
4. THE Config_Module SHALL validate environment variable values before returning them
5. THE Config_Module SHALL organize getter functions in alphabetical order by environment variable name
6. THE Multi_Agent_App SHALL use Config_Module functions instead of direct `os.getenv()` calls

### Requirement 2: Bedrock Model Support

**User Story:** As a developer, I want to support multiple Bedrock cross-region inference profiles, so that I can demonstrate flexibility in choosing Strands Agent models.

#### Acceptance Criteria

1. THE Bedrock_Model module SHALL support creating models from cross-region inference profiles
2. WHEN a Bedrock model ID is provided, THE Bedrock_Model module SHALL create a BedrockModel instance with that ID
3. THE Bedrock_Model module SHALL support the following cross-region profiles:
   - `us.amazon.nova-pro-v1:0`
   - `us.amazon.nova-2-lite-v1:0`
   - `us.anthropic.claude-haiku-4-5-20251001-v1:0`
   - `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
4. WHEN no model ID is specified, THE Bedrock_Model module SHALL use `us.amazon.nova-pro-v1:0` as the default
5. THE Bedrock_Model module SHALL configure appropriate temperature settings for each model

### Requirement 3: SageMaker Model Support

**User Story:** As a developer, I want to support SageMaker endpoint-based models, so that I can use custom deployed models as Strands Agent models.

#### Acceptance Criteria

1. THE SageMaker_Model module SHALL create SageMakerAIModel instances from endpoint names
2. WHEN a SageMaker endpoint name is provided via environment variable, THE SageMaker_Model module SHALL use that endpoint
3. THE SageMaker_Model module SHALL configure endpoint settings including region, max_tokens, temperature, and streaming
4. WHEN the SageMaker endpoint is unavailable, THE SageMaker_Model module SHALL raise a descriptive error

### Requirement 4: Loan Prediction Assistant

**User Story:** As a user, I want a loan assistant that predicts loan acceptance, so that I can evaluate whether a customer will accept a loan offer based on their attributes.

#### Acceptance Criteria

1. THE Loan_Assistant SHALL accept customer attributes as input parameters
2. WHEN customer attributes are provided, THE Loan_Assistant SHALL invoke the XGBoost_Model via Serverless_Endpoint
3. THE Loan_Assistant SHALL format customer attributes as CSV payload for the XGBoost_Model
4. WHEN the XGBoost_Model returns a prediction, THE Loan_Assistant SHALL interpret the result as accept or reject
5. THE Loan_Assistant SHALL return a human-readable prediction with confidence score
6. WHEN the Serverless_Endpoint is unavailable, THE Loan_Assistant SHALL return an error message

### Requirement 5: XGBoost Model Integration

**User Story:** As a developer, I want to integrate the XGBoost loan prediction model, so that the application can demonstrate predictive analytics capabilities.

#### Acceptance Criteria

1. THE XGBoost_Model integration SHALL use SageMaker Serverless Inference Endpoint
2. WHEN invoking the endpoint, THE integration SHALL send CSV-formatted customer data
3. THE integration SHALL handle the following customer attributes:
   - age, job type, marital status, education level
   - credit default status, housing loan status, personal loan status
   - contact type, campaign information
   - previous contact history
4. WHEN the endpoint returns a prediction, THE integration SHALL parse the CSV response
5. THE integration SHALL convert numeric predictions (0-1) to binary outcomes (accept/reject)

### Requirement 6: SageMaker Endpoint Validation Scripts

**User Story:** As a developer, I want standalone validation scripts for SageMaker endpoints, so that I can validate endpoints work before running the full application.

#### Acceptance Criteria

1. THE validation script for XGBoost SHALL extract invocation logic from the Jupyter notebook
2. WHEN the XGBoost validation script runs, THE script SHALL invoke the serverless endpoint with sample data
3. THE validation script for reasoning models SHALL extract invocation logic from the Jupyter notebook
4. WHEN the reasoning model validation script runs, THE script SHALL invoke the provisioned endpoint with sample prompts
5. THE validation scripts SHALL print clear success or failure messages
6. THE validation scripts SHALL use the Config_Module for endpoint configuration

### Requirement 7: Multi-Agent Application Integration

**User Story:** As a user, I want the loan assistant integrated into the multi-agent application, so that I can access loan predictions through the same interface as other assistants.

#### Acceptance Criteria

1. THE Multi_Agent_App SHALL include Loan_Assistant in the list of available specialists
2. WHEN a user query relates to loan prediction, THE teacher agent SHALL route to Loan_Assistant
3. THE Multi_Agent_App SHALL display loan predictions in the chat interface
4. THE Multi_Agent_App SHALL handle errors from Loan_Assistant gracefully
5. THE sidebar SHALL list Loan_Assistant with an appropriate icon and description

### Requirement 8: Model Selection Configuration

**User Story:** As a developer, I want to configure which model provider to use via environment variables, so that I can easily switch between Bedrock and SageMaker models for Strands Agents.

#### Acceptance Criteria

1. THE Config_Module SHALL provide a function to determine the active model provider
2. WHEN `STRANDS_MODEL_PROVIDER` environment variable is set to "bedrock", THE application SHALL use Bedrock_Model
3. WHEN `STRANDS_MODEL_PROVIDER` environment variable is set to "sagemaker", THE application SHALL use SageMaker_Model
4. WHEN no provider is specified, THE application SHALL default to Bedrock with `us.amazon.nova-pro-v1:0`
5. THE Multi_Agent_App SHALL display the active model provider and model in the sidebar

### Requirement 9: Code Refactoring and Deployment Strategy

**User Story:** As a developer, I want the codebase refactored to follow the consolidated architecture with a local-first development approach, so that the code is maintainable, testable, and ready for cloud deployment.

#### Acceptance Criteria

1. THE multi_agent directory SHALL contain config.py, bedrock_model.py, sagemaker_model.py, and loan_assistant.py modules
2. THE multi_agent/app.py SHALL import and use the new modules
3. WHEN implementing new features, THE developer SHALL build and test locally in multi_agent first
4. WHEN local implementation is complete and tested, THE developer SHALL merge new application logic into deploy_multi_agent/docker_app
5. WHEN merging to deploy_multi_agent/docker_app, THE developer SHALL preserve the Cognito authentication and authorization logic
6. THE deploy_multi_agent/docker_app directory SHALL contain the same modules as multi_agent
7. THE deploy_multi_agent/docker_app/app.py SHALL maintain the authentication section at the top of the file
8. WHEN refactoring is complete, THE application SHALL maintain all existing functionality in both local and deployed versions
