# Implementation Plan: workshop4-multi-agent-sagemaker-ai

## Overview

This implementation plan follows a local-first development approach: build and test all features in `multi_agent/` directory first, then merge the working implementation to `deploy_multi_agent/docker_app/` while preserving authentication logic. The plan is organized into discrete, incremental tasks that build upon each other.

## Tasks

- [x] 1. Create agent model endpoint validation script
  - Create `workshop4/sagemaker/validate_agent_endpoint.py`
  - Extract endpoint invocation logic from openai-reasoning notebook
  - Use environment variables for endpoint configuration
  - Create sample prompt for validation
  - Implement endpoint invocation with error handling
  - Print clear success or failure messages
  - Test validation script with actual endpoint (if available)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Create XGBoost model endpoint validation script
  - Create `workshop4/sagemaker/validate_xgboost_endpoint.py`
  - Extract endpoint invocation logic from numpy_xgboost notebook
  - Use environment variables for endpoint configuration
  - Create sample customer data for validation
  - Implement endpoint invocation with error handling
  - Print clear success or failure messages
  - Test validation script with actual endpoint (if available)
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 3. Create configuration module for multi_agent
  - Create `multi_agent/config.py` with SSM Parameter Store integration
  - Implement getter functions in alphabetical order:
    - `get_agent_knowledge_base_id()` - AGENT_KNOWLEDGE_BASE_ID
    - `get_agent_model_endpoint()` - AGENT_MODEL_ENDPOINT
    - `get_agent_model_inference_component()` - AGENT_MODEL_INFERENCE_COMPONENT
    - `get_aws_region()` - AWS_REGION
    - `get_default_model_id()` - DEFAULT_MODEL_ID
    - `get_max_results()` - MAX_RESULTS
    - `get_min_score()` - MIN_SCORE
    - `get_temperature()` - TEMPERATURE
    - `get_xgboost_model_endpoint()` - XGBOOST_MODEL_ENDPOINT
  - Add validation logic and default values for each getter
  - Add comprehensive docstrings explaining each function and its SSM parameter
  - Use environment variable `TEACHER_ASSISTANT_ENV` to determine parameter path
  - **Note**: Provider is determined dynamically from UI selection, not from configuration
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [ ]* 3.1 Write unit tests for configuration module
  - Test each getter function with valid environment variables
  - Test default value returns when environment variable not set
  - Test validation of invalid environment variable values
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 4. Create Bedrock model module for multi_agent
  - Create `multi_agent/bedrock_model.py` with `create_bedrock_model()` function
  - Import BedrockModel from strands.models
  - Support all four cross-region inference profiles
  - Use config module for model ID and region
  - Add error handling for invalid model IDs
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ]* 4.1 Write unit tests for Bedrock model module
  - Test model creation with each supported model ID
  - Test default model ID selection
  - Test error handling for invalid model IDs
  - Test temperature configuration
  - _Requirements: 4.2, 4.3, 4.5_

- [x] 5. Create SageMaker model module for multi_agent
  - Create `multi_agent/sagemaker_model.py` with `create_sagemaker_model()` function
  - Import SageMakerAIModel from strands.models.sagemaker
  - Use config module for endpoint name and region
  - Configure endpoint settings (max_tokens, temperature, streaming)
  - Add error handling for missing or unavailable endpoints
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ]* 5.1 Write unit tests for SageMaker model module
  - Test model creation with valid endpoint name
  - Test error handling for missing endpoint name
  - Test configuration parameter passing
  - _Requirements: 5.2, 5.3, 5.4_

- [x] 6. Update multi_agent/app.py to use new model modules with dropdown selection
  - Import config module and replace remaining `os.getenv()` calls if any
  - Import bedrock_model and sagemaker_model modules
  - Add model selection dropdown in sidebar with options:
    - Amazon Nova 2 Lite (us.amazon.nova-2-lite-v1:0) - DEFAULT
    - Amazon Nova Pro (us.amazon.nova-pro-v1:0)
    - Anthropic Claude Haiku 4.5 (us.anthropic.claude-haiku-4-5-20251001-v1:0)
    - Anthropic Claude Sonnet 4.5 (us.anthropic.claude-sonnet-4-5-20250929-v1:0)
    - Custom gpt-oss-20b (SageMaker endpoint)
  - Add logic to select model provider based on dropdown selection
  - Update teacher agent creation to use selected model (bedrock or sagemaker)
  - Update sidebar to display active model provider and model
  - Store selected model in session state
  - _Requirements: 3.6, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

- [ ]* 6.1 Write integration test for app with model selection
  - Test teacher agent with Bedrock models
  - Test teacher agent with SageMaker model (if endpoint available)
  - Test model switching between providers
  - _Requirements: 6.3, 6.4, 6.5_

- [ ] 7. Refactor naming conventions and deploy SSM parameters
  - **Naming Refactoring**:
    - Rename CloudFormation template: `ssm/teachassist-params.yaml` → `ssm/teacher-assistant-params.yaml`
    - Update all parameter names to use functionality-based naming (not service-based)
    - Update SSM parameter paths to single-level format: `/teacher_assistant/{env}/{parameter_name}`
    - Update environment variable: `TEACHASSIST_ENV` → `TEACHER_ASSISTANT_ENV`
    - Update all config function names to match new parameter names
    - Update all application code to use new config function names
  - **SSM Parameter Deployment**:
    - Deploy CloudFormation template with generic placeholder defaults
    - Update `ssm/README.md` to document deployment and update process
    - Document that CloudFormation stack updates cannot change parameter values
    - Explain students must update SSM parameters directly via Console or CLI
  - **Testing**:
    - Deploy SSM parameters using CloudFormation
    - Set `TEACHER_ASSISTANT_ENV=dev` environment variable
    - Run multi_agent/app.py locally and verify it fetches config from SSM
    - Use the sidebar model dropdown to test each model selection
    - Test SageMaker model selection (if endpoint available)
    - Verify sidebar displays correct model information
    - Test error handling for missing SageMaker endpoint
    - Ask the user if questions arise
  - _Requirements: 3.1, 3.2, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

- [ ] 8. Implement loan assistant data transformation logic
  - Create `multi_agent/loan_assistant.py` with CustomerAttributes handling
  - Implement one-hot encoding for all categorical features
  - Implement CSV payload generation function
  - Add validation for customer attribute values
  - Create mapping dictionaries for all categorical features
  - _Requirements: 7.2, 7.3, 7.8, 7.9_

- [ ]* 8.1 Write property test for CSV payload format
  - **Property 4: CSV Payload Format Correctness**
  - **Validates: Requirements 7.8, 7.9**

- [ ]* 8.2 Write property test for one-hot encoding
  - **Property 5: One-Hot Encoding Completeness**
  - **Validates: Requirements 7.9**

- [ ]* 8.3 Write unit tests for data transformation
  - Test one-hot encoding for each categorical feature
  - Test CSV payload generation with sample customer profiles
  - Test edge cases (unknown values, boundary numeric values)
  - _Requirements: 7.8, 7.9_

- [ ] 9. Implement loan assistant XGBoost invocation logic
  - Add SageMaker runtime client creation in loan_assistant.py
  - Implement endpoint invocation with CSV payload
  - Implement response parsing and prediction extraction
  - Implement binary classification mapping (threshold at 0.5)
  - Add error handling for endpoint failures
  - _Requirements: 7.2, 7.3, 7.4, 7.5, 7.6, 7.10, 7.11_

- [ ]* 9.1 Write property test for prediction output range
  - **Property 6: Prediction Output Range**
  - **Validates: Requirements 7.11**

- [ ]* 9.2 Write property test for binary classification mapping
  - **Property 7: Binary Classification Mapping**
  - **Validates: Requirements 7.4**

- [ ]* 9.3 Write unit tests for XGBoost invocation
  - Test endpoint invocation with mocked SageMaker client
  - Test response parsing for various prediction scores
  - Test error handling for endpoint failures
  - _Requirements: 7.6, 7.10, 7.11_

- [ ] 10. Complete loan assistant as Strands tool
  - Wrap loan prediction logic in @tool decorator
  - Define function signature with all customer attribute parameters
  - Add comprehensive docstring with parameter descriptions
  - Implement human-readable response formatting
  - Add confidence score to response
  - _Requirements: 7.1, 7.2, 7.5_

- [ ]* 10.1 Write integration test for loan assistant tool
  - Test loan assistant with sample customer data
  - Test error propagation through tool interface
  - _Requirements: 7.1, 7.2, 7.5, 7.6_

- [ ] 11. Integrate loan assistant into multi_agent/app.py
  - Import loan_assistant tool
  - Add loan_assistant to teacher agent's tools list
  - Update sidebar to list loan assistant with icon and description
  - _Requirements: 7.1, 8.1, 8.2_

- [ ]* 11.1 Write integration test for app with loan assistant
  - Test teacher agent routing to loan assistant
  - Test loan prediction through full agent hierarchy
  - _Requirements: 8.1, 8.2_

- [ ] 12. Test loan assistant end-to-end
  - Run multi_agent/app.py locally
  - Test loan assistant with various customer profiles
  - Test error handling for missing XGBoost model endpoint
  - Verify sidebar displays loan assistant
  - _Requirements: 7.1, 7.2, 7.5, 7.6, 8.3, 8.4, 8.5_

- [ ] 13. Checkpoint - Loan assistant complete
  - Ensure loan assistant works correctly
  - Ensure all tests pass
  - Ask the user if questions arise

- [ ] 14. Merge new modules to deploy_multi_agent/docker_app
  - Copy `config.py` to `deploy_multi_agent/docker_app/config.py`
  - Copy `bedrock_model.py` to `deploy_multi_agent/docker_app/bedrock_model.py`
  - Copy `sagemaker_model.py` to `deploy_multi_agent/docker_app/sagemaker_model.py`
  - Copy `loan_assistant.py` to `deploy_multi_agent/docker_app/loan_assistant.py`
  - Verify no conflicts with existing files
  - _Requirements: 9.1, 9.3, 9.6_

- [ ] 15. Merge application logic to deploy_multi_agent/docker_app/app.py
  - Preserve authentication section (lines 1-25) at the top
  - Preserve authentication UI in sidebar
  - Import new modules (config, bedrock_model, sagemaker_model, loan_assistant)
  - Replace `os.getenv()` calls with config module functions
  - Add model provider selection logic
  - Update teacher agent creation to use selected model
  - Add loan_assistant to teacher agent's tools list
  - Update sidebar to display active model provider and model
  - Update sidebar to list loan assistant
  - Preserve logout button and user info display
  - _Requirements: 9.2, 9.3, 9.4, 9.5, 9.7, 9.8_

- [ ] 16. Test deployed application logic
  - Review merged code for correctness
  - Verify authentication section is preserved
  - Verify all new features are included
  - Verify no duplicate code or conflicts
  - _Requirements: 9.5, 9.7, 9.8_

- [ ] 17. Final checkpoint - Implementation complete
  - Verify both local and deployed versions have all features
  - Verify all tests pass
  - Verify validation scripts work
  - Confirm ready for workshop4-architecture-refactoring completion
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Local-first approach ensures faster iteration and easier debugging
- Merge strategy preserves authentication logic in deployed version
- Validation scripts enable pre-deployment endpoint testing
