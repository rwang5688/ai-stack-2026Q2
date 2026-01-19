# Implementation Plan: workshop4-multi-agent-sagemaker-ai

## Overview

This implementation plan follows a local-first development approach: build and test all features in `multi_agent/` directory first, then merge the working implementation to `deploy_multi_agent/docker_app/` while preserving authentication logic. The plan is organized into discrete, incremental tasks that build upon each other.

## Tasks

- [x] 1. Create SageMaker model endpoint validation script
  - Create `workshop4/sagemaker/validate_sagemaker_endpoint.py`
  - Extract endpoint invocation logic from openai-reasoning notebook
  - Use SSM Parameter Store for endpoint configuration
  - Create sample prompt for validation
  - Implement endpoint invocation with error handling
  - Print clear success or failure messages
  - Test validation script with actual endpoint (if available)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Create XGBoost model endpoint validation script
  - Create `workshop4/sagemaker/validate_xgboost_endpoint.py`
  - Extract endpoint invocation logic from numpy_xgboost notebook
  - Use SSM Parameter Store for endpoint configuration
  - Create sample customer data for validation
  - Implement endpoint invocation with error handling
  - Print clear success or failure messages
  - Test validation script with actual endpoint (if available)
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 3. Create configuration module for multi_agent
  - Create `multi_agent/config.py` with SSM Parameter Store integration
  - Implement getter functions in alphabetical order:
    - `get_aws_region()` - AWS_REGION
    - `get_default_model_id()` - DEFAULT_MODEL_ID
    - `get_max_results()` - MAX_RESULTS
    - `get_min_score()` - MIN_SCORE
    - `get_sagemaker_model_endpoint()` - SAGEMAKER_MODEL_ENDPOINT
    - `get_sagemaker_model_inference_component()` - SAGEMAKER_MODEL_INFERENCE_COMPONENT
    - `get_strands_knowledge_base_id()` - STRANDS_KNOWLEDGE_BASE_ID (REQUIRED - Framework integration point)
    - `get_temperature()` - TEMPERATURE
    - `get_xgboost_model_endpoint()` - XGBOOST_MODEL_ENDPOINT
  - Add validation logic and default values for each getter
  - Add comprehensive docstrings explaining each function and its SSM parameter
  - Use environment variable `TEACHERS_ASSISTANT_ENV` to determine parameter path
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

- [x] 7. Refactor naming conventions and deploy SSM parameters
  - **Naming Refactoring**:
    - Rename CloudFormation template: `ssm/teachassist-params.yaml` → `ssm/teachers-assistant-params.yaml`
    - Update all parameter names to use functionality-based naming (not service-based)
    - Update SSM parameter paths to single-level format: `/teachers_assistant/{env}/{parameter_name}`
    - Update environment variable: `TEACHASSIST_ENV` → `TEACHERS_ASSISTANT_ENV`
    - Update all config function names to match new parameter names
    - Update all application code to use new config function names
  - **SSM Parameter Deployment**:
    - Deploy CloudFormation template with generic placeholder defaults
    - Update `ssm/README.md` to document deployment and update process
    - Document that CloudFormation stack updates cannot change parameter values
    - Explain students must update SSM parameters directly via Console or CLI
  - **Testing**:
    - Deploy SSM parameters using CloudFormation
    - Set `TEACHERS_ASSISTANT_ENV=dev` environment variable
    - Run multi_agent/app.py locally and verify it fetches config from SSM
    - Use the sidebar model dropdown to test each model selection
    - Test SageMaker model selection (if endpoint available)
    - Verify sidebar displays correct model information
    - Test error handling for missing SageMaker endpoint
    - Ask the user if questions arise
  - _Requirements: 3.1, 3.2, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

- [x] 8. Implement loan_offering_assistant.py
  - Create `multi_agent/loan_offering_assistant.py` following math_assistant.py structure
  - Implement `loan_offering_prediction` tool (similar to calculator tool)
  - Tool accepts CSV payload string with 59 features
  - Tool invokes XGBoost endpoint using boto3 sagemaker-runtime (like validate_xgboost_endpoint)
  - Tool parses prediction and returns formatted response with:
    - Feature payload
    - Raw prediction
    - Prediction label ("Accept" if >= 0.5, else "Reject")
    - Confidence (prediction * 100 formatted to 2 decimals)
  - Implement `loan_offering_assistant` tool that wraps the prediction tool
  - Use config module to get XGBoost endpoint name
  - Use model_factory to create agent model
  - Add system prompt for loan offering assistant agent
  - Add error handling for endpoint failures
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 9.1, 9.2, 9.3, 9.4_

- [ ]* 8.1 Write unit tests for loan_offering_prediction tool
  - Test endpoint invocation with sample payload
  - Test prediction parsing
  - Test label mapping (Accept/Reject)
  - Test confidence formatting
  - Test error handling
  - _Requirements: 7.6, 7.7, 7.8, 7.9_

- [x] 9. Integrate loan_offering_assistant into applications
  - Import loan_offering_assistant in `multi_agent/app.py`
  - Add loan_offering_assistant to teacher agent's tools list in app.py
  - Update sidebar to list "💰 Loan Offering Assistant" with description
  - Import loan_offering_assistant in `multi_agent/teachers_assistant.py`
  - Add loan_offering_assistant to teacher agent's tools list in CLI app
  - Update TEACHER_SYSTEM_PROMPT to include loan offering routing
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [x] 10. Test loan_offering_assistant locally and checkpoint
  - Run multi_agent/app.py locally
  - Test with sample query: "will a person with the following demographics accept the loan: 29,2,999,0,1,0,0.0,1.0,..."
  - Verify prediction response includes payload, raw score, label, and confidence
  - Test error handling when XGBoost endpoint unavailable
  - Test CLI app (teachers_assistant.py) with same query
  - Verify sidebar displays loan offering assistant
  - Verify loan offering assistant works in both app.py and teachers_assistant.py
  - Verify all tests pass (if written)
  - Ask the user if questions arise
  - _Requirements: 7.1, 7.2, 7.5, 7.6, 7.7, 7.8, 7.9, 8.5, 8.6_

- [ ] 11. Copy all multi_agent modules to deploy_multi_agent/docker_app
  - Copy ALL Python modules from `multi_agent/` to `deploy_multi_agent/docker_app/`
  - This includes all assistant modules, config, model modules, and utilities
  - Verify no conflicts with existing files
  - Follow the merge process documented in workshop4/PART-3-DEPLOY-MULTI-AGENT.md
  - **Note**: This task demonstrates how Kiro can automate deployment runbooks by reading documentation
  - _Requirements: 9.1_

- [ ] 12. Integrate multi_agent/app.py logic into deploy_multi_agent/docker_app/app.py
  - Merge application logic from `multi_agent/app.py` into `deploy_multi_agent/docker_app/app.py`
  - Preserve Cognito authentication and authorization sections
  - Keep authentication UI elements intact (logout button, user info display)
  - Follow the merge process documented in workshop4/PART-3-DEPLOY-MULTI-AGENT.md
  - **Note**: This task demonstrates how Kiro can follow documentation to perform complex merge operations
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 8.1, 8.2, 8.6_

- [ ] 13. Deploy to ECS Fargate using CDK
  - Navigate to `deploy_multi_agent/` directory
  - Execute `cdk deploy` on Ubuntu Linux
  - CDK will trigger Docker build of the Streamlit application
  - CDK will push Docker image to Amazon ECR
  - CDK will deploy updated image to ECS Fargate task
  - Wait for deployment to complete
  - Follow the deployment process documented in workshop4/PART-3-DEPLOY-MULTI-AGENT.md
  - **Note**: This task demonstrates the full CDK deployment workflow
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 8.1, 8.2, 8.6_

- [ ] 14. Test deployed application and final checkpoint
  - Access the deployed Streamlit app via ALB URL
  - Test Cognito authentication (login)
  - Test model selection dropdown with each model option
  - Test loan offering assistant with sample query
  - Verify sidebar displays correct model information
  - Verify sidebar lists all 6 specialists (including loan offering)
  - Test logout functionality
  - Verify deployed application has all features working:
    - Cognito authentication
    - Model selection dropdown
    - All 5 model options
    - Loan offering assistant
    - All 6 specialists listed
  - Verify all tests pass (if written)
  - Deployment to ECS Fargate complete
  - Ask the user if questions arise
  - _Requirements: 6.3, 6.4, 6.5, 8.1, 8.2_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Local-first approach ensures faster iteration and easier debugging
- Merge strategy preserves authentication logic in deployed version
- Validation scripts enable pre-deployment endpoint testing
