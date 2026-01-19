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

### Requirement 1: SageMaker Model Endpoint Validation Script

**User Story:** As a developer, I want a standalone validation script for the SageMaker model endpoint, so that I can validate the reasoning model endpoint works before running the full application.

#### Acceptance Criteria

1. THE validation script for SageMaker models SHALL extract invocation logic from the Jupyter notebook
2. WHEN the SageMaker model validation script runs, THE script SHALL invoke the provisioned endpoint with sample prompts
3. THE validation script SHALL print clear success or failure messages
4. THE validation script SHALL use environment variables for endpoint configuration
5. THE validation script SHALL be executable independently without requiring the full application to be running

### Requirement 2: XGBoost Model Endpoint Validation Script

**User Story:** As a developer, I want a standalone validation script for the XGBoost model endpoint, so that I can validate the loan prediction endpoint works before building the loan assistant.

#### Acceptance Criteria

1. THE validation script for XGBoost SHALL extract invocation logic from the Jupyter notebook
2. WHEN the XGBoost validation script runs, THE script SHALL invoke the serverless endpoint with sample data
3. THE validation script SHALL print clear success or failure messages
4. THE validation script SHALL use environment variables for endpoint configuration
5. THE validation script SHALL be executable independently without requiring the full application to be running

### Requirement 3: Configuration Management

**User Story:** As a developer, I want centralized configuration management, so that environment variables are consistently accessed and validated across the application.

#### Acceptance Criteria

1. THE Config_Module SHALL provide getter functions for all environment variables used by the application
2. THE Config_Module SHALL manage the following SSM parameters (alphabetically sorted):
   - DEFAULT_MODEL_ID: Default model ID (typically Bedrock cross-region profile)
   - MAX_RESULTS: Maximum results for knowledge base queries
   - MIN_SCORE: Minimum score threshold for knowledge base queries
   - SAGEMAKER_MODEL_ENDPOINT: SageMaker model endpoint name
   - SAGEMAKER_MODEL_INFERENCE_COMPONENT: SageMaker model inference component name (for multi-model endpoints)
   - STRANDS_KNOWLEDGE_BASE_ID: Strands knowledge base ID (REQUIRED - Framework integration point with Bedrock Knowledge Base)
   - TEMPERATURE: Model temperature setting for all agents
   - XGBOOST_MODEL_ENDPOINT: XGBoost loan prediction endpoint name
2a. THE Config_Module SHALL read AWS_REGION from environment variable (not SSM Parameter Store)
3. WHEN an environment variable is missing, THE Config_Module SHALL return a sensible default value or raise a descriptive error
4. THE Config_Module SHALL validate environment variable values before returning them
5. THE Config_Module SHALL organize getter functions in alphabetical order by environment variable name
6. THE Multi_Agent_App SHALL use Config_Module functions instead of direct `os.getenv()` calls

**Note**: The model provider (bedrock or sagemaker) is NOT an environment variable. It is determined dynamically based on the user's model selection in the UI.

### Requirement 4: Bedrock Model Support

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

### Requirement 4: Bedrock Model Support

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

### Requirement 5: SageMaker Model Support

**User Story:** As a developer, I want to support SageMaker endpoint-based models, so that I can use custom deployed models as Strands Agent models.

#### Acceptance Criteria

1. THE SageMaker_Model module SHALL create SageMakerAIModel instances from endpoint names
2. WHEN a SageMaker endpoint name is provided via environment variable, THE SageMaker_Model module SHALL use that endpoint
3. THE SageMaker_Model module SHALL configure endpoint settings including region, max_tokens, temperature, and streaming
4. WHEN the SageMaker endpoint is unavailable, THE SageMaker_Model module SHALL raise a descriptive error

### Requirement 6: Model Selection UI

**User Story:** As a user, I want to select which model to use for the Strands Agent via a dropdown, so that I can easily switch between different Bedrock and SageMaker models.

#### Acceptance Criteria

1. THE Multi_Agent_App SHALL display a model selection dropdown in the sidebar
2. THE dropdown SHALL include the following options:
   - Amazon Nova Pro (us.amazon.nova-pro-v1:0)
   - Amazon Nova 2 Lite (us.amazon.nova-2-lite-v1:0)
   - Anthropic Claude Haiku 4.5 (us.anthropic.claude-haiku-4-5-20251001-v1:0)
   - Anthropic Claude Sonnet 4.5 (us.anthropic.claude-sonnet-4-5-20250929-v1:0)
   - Custom gpt-oss-20b (SageMaker endpoint)
3. WHEN a Bedrock model is selected, THE application SHALL use the Bedrock_Model module
4. WHEN the SageMaker model is selected, THE application SHALL use the SageMaker_Model module
5. THE sidebar SHALL display the currently active model provider and model ID
6. THE selected model SHALL persist in session state during the user's session
7. WHEN the model selection changes, THE teacher agent SHALL be recreated with the new model

### Requirement 7: Loan Offering Assistant

**User Story:** As a user, I want a loan offering assistant that predicts loan acceptance, so that I can evaluate whether a customer will accept a loan offer based on their feature payload.

#### Acceptance Criteria

1. THE Loan_Offering_Assistant SHALL be implemented similar to math_assistant
2. THE Loan_Offering_Assistant SHALL use a loan_offering_prediction tool (similar to calculator tool in math_assistant)
3. WHEN a user provides a CSV feature payload, THE loan_offering_prediction tool SHALL invoke the XGBoost endpoint
4. THE loan_offering_prediction tool SHALL work similarly to validate_xgboost_endpoint function
5. THE tool SHALL accept a CSV string payload with 59 features
6. WHEN the XGBoost endpoint returns a prediction, THE tool SHALL parse the numeric result
7. THE tool SHALL return raw prediction, prediction label (Accept/Reject), and confidence percentage
8. THE prediction label SHALL be "Accept" if prediction >= 0.5, otherwise "Reject"
9. THE confidence SHALL be formatted as prediction * 100 with 2 decimal places
10. WHEN the endpoint is unavailable, THE tool SHALL return an error message

### Requirement 8: Multi-Agent Application Integration

**User Story:** As a user, I want the loan offering assistant integrated into the multi-agent application, so that I can access loan predictions through the same interface as other assistants.

#### Acceptance Criteria

1. THE Multi_Agent_App (app.py) SHALL import loan_offering_assistant
2. THE Multi_Agent_App SHALL add loan_offering_assistant to teacher agent's tools list
3. THE CLI App (teachers_assistant.py) SHALL import loan_offering_assistant  
4. THE CLI App SHALL add loan_offering_assistant to teacher agent's tools list
5. WHEN a user query relates to loan prediction, THE teacher agent SHALL route to loan_offering_assistant
6. THE sidebar SHALL list Loan Offering Assistant with an appropriate icon and description

### Requirement 9: Code Organization

**User Story:** As a developer, I want the loan offering assistant code organized consistently with other assistants, so that the codebase is maintainable.

#### Acceptance Criteria

1. THE loan_offering_assistant.py file SHALL be created in multi_agent directory
2. THE file SHALL follow the same structure as math_assistant.py
3. THE file SHALL use config module for XGBoost endpoint configuration
4. THE file SHALL use model_factory for model creation (consistent with other assistants)
