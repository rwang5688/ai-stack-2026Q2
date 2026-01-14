# Implementation Plan: workshop4-multi-agent-sagemaker-ai

## Overview

This implementation plan follows a local-first development approach: build and test all features in `multi_agent/` directory first, then merge the working implementation to `deploy_multi_agent/docker_app/` while preserving authentication logic. The plan is organized into discrete, incremental tasks that build upon each other.

## Tasks

- [x] 1. Create configuration module for multi_agent
  - Create `multi_agent/config.py` with environment variable getter functions
  - Implement getter functions in alphabetical order by environment variable name:
    - `get_aws_region()` - AWS_REGION
    - `get_bedrock_model_id()` - BEDROCK_MODEL_ID
    - `get_max_results()` - MAX_RESULTS
    - `get_min_score()` - MIN_SCORE
    - `get_sagemaker_model_endpoint()` - SAGEMAKER_MODEL_ENDPOINT
    - `get_strands_knowledge_base_id()` - STRANDS_KNOWLEDGE_BASE_ID
    - `get_strands_model_provider()` - STRANDS_MODEL_PROVIDER
    - `get_xgboost_endpoint_name()` - XGBOOST_ENDPOINT_NAME
  - Add validation logic and default values for each getter
  - Add comprehensive docstrings explaining each function and its environment variable
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [ ]* 1.1 Write unit tests for configuration module
  - Test each getter function with valid environment variables
  - Test default value returns when environment variable not set
  - Test validation of invalid environment variable values
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 2. Create Bedrock model module for multi_agent
  - Create `multi_agent/bedrock_model.py` with `create_bedrock_model()` function
  - Import BedrockModel from strands.models
  - Support all four cross-region inference profiles
  - Use config module for model ID and region
  - Add error handling for invalid model IDs
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 2.1 Write unit tests for Bedrock model module
  - Test model creation with each supported model ID
  - Test default model ID selection
  - Test error handling for invalid model IDs
  - Test temperature configuration
  - _Requirements: 2.2, 2.3, 2.5_

- [ ] 3. Create SageMaker model module for multi_agent
  - Create `multi_agent/sagemaker_model.py` with `create_sagemaker_model()` function
  - Import SageMakerAIModel from strands.models.sagemaker
  - Use config module for endpoint name and region
  - Configure endpoint settings (max_tokens, temperature, streaming)
  - Add error handling for missing or unavailable endpoints
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ]* 3.1 Write unit tests for SageMaker model module
  - Test model creation with valid endpoint name
  - Test error handling for missing endpoint name
  - Test configuration parameter passing
  - _Requirements: 3.2, 3.3, 3.4_

- [ ] 4. Checkpoint - Verify model modules work locally
  - Ensure all tests pass for config, bedrock_model, and sagemaker_model modules
  - Ask the user if questions arise

- [ ] 5. Update multi_agent/app.py to use new model modules with dropdown selection
  - Import config module and replace remaining `os.getenv()` calls if any
  - Import bedrock_model and sagemaker_model modules
  - Add model selection dropdown in sidebar with options:
    - Amazon Nova Pro (us.amazon.nova-pro-v1:0)
    - Amazon Nova 2 Lite (us.amazon.nova-2-lite-v1:0)
    - Anthropic Claude Haiku 4.5 (us.anthropic.claude-haiku-4-5-20251001-v1:0)
    - Anthropic Claude Sonnet 4.5 (us.anthropic.claude-sonnet-4-5-20250929-v1:0)
    - Custom gpt-oss-20b (SageMaker endpoint)
  - Add logic to select model provider based on dropdown selection
  - Update teacher agent creation to use selected model (bedrock or sagemaker)
  - Update sidebar to display active model provider and model
  - Store selected model in session state
  - _Requirements: 1.4, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ]* 5.1 Write integration test for app with model selection
  - Test teacher agent with Bedrock models
  - Test teacher agent with SageMaker model (if endpoint available)
  - Test model switching between providers
  - _Requirements: 5.3, 5.4, 5.5_

- [ ] 6. Test model selection end-to-end
  - Run multi_agent/app.py locally
  - Test each Bedrock model selection from dropdown
  - Test SageMaker model selection (if endpoint available)
  - Verify sidebar displays correct model information
  - Test error handling for missing SageMaker endpoint
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ] 7. Checkpoint - Model selection complete
  - Ensure model dropdown works correctly
  - Ensure all model providers work
  - Ask the user if questions arise

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
  - Test error handling for missing XGBoost endpoint
  - Verify sidebar displays loan assistant
  - _Requirements: 7.1, 7.2, 7.5, 7.6, 8.3, 8.4, 8.5_

- [ ] 13. Checkpoint - Loan assistant complete
  - Ensure loan assistant works correctly
  - Ensure all tests pass
  - Ask the user if questions arise

- [ ] 14. Create XGBoost endpoint validation script
  - Create `workshop4/sagemaker/validate_xgboost_endpoint.py`
  - Extract endpoint invocation logic from numpy_xgboost notebook
  - Use config module for endpoint name
  - Create sample customer data for validation
  - Implement endpoint invocation with error handling
  - Print clear success or failure messages
  - _Requirements: 6.1, 6.2, 6.5, 6.6_

- [ ] 14. Create XGBoost endpoint validation script
  - Create `workshop4/sagemaker/validate_xgboost_endpoint.py`
  - Extract endpoint invocation logic from numpy_xgboost notebook
  - Use config module for endpoint name
  - Create sample customer data for validation
  - Implement endpoint invocation with error handling
  - Print clear success or failure messages
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 15. Create reasoning model endpoint validation script
  - Create `workshop4/sagemaker/validate_reasoning_endpoint.py`
  - Extract endpoint invocation logic from openai-reasoning notebook
  - Use config module for endpoint name
  - Create sample prompt for validation
  - Implement endpoint invocation with error handling
  - Print clear success or failure messages
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 16. Checkpoint - Validation scripts complete
  - Ensure validation scripts work independently
  - Ask the user if questions arise

- [ ] 17. Merge new modules to deploy_multi_agent/docker_app
  - Copy `config.py` to `deploy_multi_agent/docker_app/config.py`
  - Copy `bedrock_model.py` to `deploy_multi_agent/docker_app/bedrock_model.py`
  - Copy `sagemaker_model.py` to `deploy_multi_agent/docker_app/sagemaker_model.py`
  - Copy `loan_assistant.py` to `deploy_multi_agent/docker_app/loan_assistant.py`
  - Verify no conflicts with existing files
  - _Requirements: 9.1, 9.3, 9.6_

- [ ] 18. Merge application logic to deploy_multi_agent/docker_app/app.py
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

- [ ] 19. Test deployed application logic
  - Review merged code for correctness
  - Verify authentication section is preserved
  - Verify all new features are included
  - Verify no duplicate code or conflicts
  - _Requirements: 9.5, 9.7, 9.8_

- [ ] 20. Final checkpoint - Implementation complete
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
