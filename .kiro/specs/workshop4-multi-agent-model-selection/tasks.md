# Implementation Plan: Workshop4 Multi-Agent Model Selection

## Overview

This implementation plan breaks down the workshop4-multi-agent-model-selection feature into discrete coding tasks. The feature adds support for Bedrock Custom Model Deployment and improves SageMaker model display. Implementation follows the local development → deployment workflow documented in PART-2-MULTI-AGENT.md and PART-3-DEPLOY-MULTI-AGENT.md.

**Note**: The validation directory has been renamed from `workshop4/validation` to `workshop4/validate` for consistency.

## Tasks

- [ ] 1. Add SSM Parameter for Custom Model Deployment ARN
  - Update CloudFormation template `workshop4/ssm/teachers-assistant-params.yaml`
  - Add `BedrockCustomModelDeploymentArn` parameter with default value `my-bedrock-custom-model-deployment-arn`
  - Add parameter description explaining its purpose for Bedrock custom model deployments
  - Add SSM Parameter resource `ParamBedrockCustomModelDeploymentArn` under `/teachers_assistant/${Environment}/bedrock_custom_model_deployment_arn`
  - Add output `BedrockCustomModelDeploymentArnParameter` for reference
  - Add appropriate tags (Environment, Application, ManagedBy)
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 2. Update configuration module for local development
  - [ ] 2.1 Add getter function to local config module
    - Modify `workshop4/multi_agent/config.py`
    - Add `get_bedrock_custom_model_deployment_arn()` function that retrieves the parameter value
    - Use `_get_parameter('bedrock_custom_model_deployment_arn', default='my-bedrock-custom-model-deployment-arn')`
    - Add comprehensive docstring with parameter path, default value, return type, and example
    - Insert function alphabetically between `get_aws_region()` and `get_default_model_id()`
    - _Requirements: 1.4, 1.5_
  
  - [ ]* 2.2 Write unit test for configuration getter
    - Test that `get_bedrock_custom_model_deployment_arn()` returns a string value
    - Test with mocked SSM parameter values
    - Test default value handling
    - _Requirements: 1.4_

- [ ] 3. Update local application for model selection
  - [ ] 3.1 Import configuration getter in local app
    - Modify `workshop4/multi_agent/app.py`
    - Add `get_bedrock_custom_model_deployment_arn` to imports from config module
    - _Requirements: 2.1_
  
  - [ ] 3.2 Fetch configuration values before model_options dictionary
    - Add `custom_model_arn = get_bedrock_custom_model_deployment_arn()` before model_options
    - Add `sagemaker_endpoint = get_sagemaker_model_endpoint()` before model_options
    - _Requirements: 2.1, 4.1_
  
  - [ ] 3.3 Add Bedrock Custom Model Deployment option to model_options
    - Add new dictionary entry with key `f"Bedrock Custom Model Deployment ({custom_model_arn})"`
    - Set provider to "bedrock"
    - Set model_id to `custom_model_arn`
    - Set display_name to "Bedrock Custom Model Deployment"
    - Place after existing Bedrock options and before SageMaker option
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [ ] 3.4 Update SageMaker model option label
    - Change key from "Custom SageMaker Model" to `f"SageMaker Model ({sagemaker_endpoint})"`
    - Keep provider, model_id, and display_name unchanged
    - Update display_name to "SageMaker Model"
    - _Requirements: 4.1_
  
  - [ ] 3.5 Add custom model deployment information display
    - Add conditional block after active model info display
    - Check if `selected_model_info['display_name'] == "Bedrock Custom Model Deployment"`
    - Display markdown with explanation about ARN usage for custom model deployments
    - Include information that model_id is the value of bedrock-custom-model-deployment-arn parameter
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [ ]* 3.6 Write unit tests for model selection
    - Test that model_options contains custom model deployment entry
    - Test that custom model deployment option has correct provider and model_id
    - Test that SageMaker option label includes endpoint name
    - Test that all existing model options are preserved
    - _Requirements: 2.1, 2.2, 2.3, 2.5, 4.1_

- [ ] 4. Enhance Bedrock model creation with ARN validation
  - [ ] 4.1 Add ARN pattern detection to bedrock_model.py
    - Modify `workshop4/multi_agent/bedrock_model.py`
    - Import `re` module at top of file
    - Add ARN_PATTERN constant: `r'^arn:aws:bedrock:[a-z0-9-]+:\d{12}:custom-model-deployment/[a-zA-Z0-9]+$'`
    - Update `create_bedrock_model()` to detect ARN format using regex
    - Skip validation if model_id matches ARN pattern
    - Keep existing validation for non-ARN model IDs
    - _Requirements: 2.4_
  
  - [ ]* 4.2 Write property test for ARN format acceptance
    - **Property 2: ARN Format Acceptance**
    - **Validates: Requirements 2.4**
    - Use hypothesis to generate valid ARN formats
    - Test that BedrockModel creation succeeds for all valid ARNs
    - _Requirements: 2.4_
  
  - [ ]* 4.3 Write unit tests for ARN validation
    - Test that valid ARNs pass validation
    - Test that invalid model IDs fail validation
    - Test that standard model IDs still work
    - _Requirements: 2.4_

- [ ] 5. Checkpoint - Local development testing
  - Follow PART-2-MULTI-AGENT.md instructions for local testing
  - Test model selection dropdown displays all options correctly
  - Test selecting custom model deployment option
  - Test selecting SageMaker option with endpoint name
  - Test that existing model options still work
  - Verify custom model deployment information displays correctly
  - Ensure all tests pass, ask the user if questions arise

- [ ] 6. Update configuration module for deployment
  - [ ] 6.1 Add getter function to deployed config module
    - Modify `workshop4/deploy_multi_agent/docker_app/config.py`
    - Add `get_bedrock_custom_model_deployment_arn()` function (identical to local version)
    - Use `_get_parameter('bedrock_custom_model_deployment_arn', default='my-bedrock-custom-model-deployment-arn')`
    - Add comprehensive docstring with parameter path, default value, return type, and example
    - Insert function alphabetically between `get_aws_region()` and `get_default_model_id()`
    - _Requirements: 1.4, 1.5, 5.1_

- [ ] 7. Update deployed application for model selection
  - [ ] 7.1 Import configuration getter in deployed app
    - Modify `workshop4/deploy_multi_agent/docker_app/app.py`
    - Add `get_bedrock_custom_model_deployment_arn` to imports from config module
    - _Requirements: 2.1, 5.1_
  
  - [ ] 7.2 Fetch configuration values before model_options dictionary
    - Add `custom_model_arn = get_bedrock_custom_model_deployment_arn()` before model_options
    - Add `sagemaker_endpoint = get_sagemaker_model_endpoint()` before model_options
    - _Requirements: 2.1, 4.1, 5.1_
  
  - [ ] 7.3 Add Bedrock Custom Model Deployment option to model_options
    - Add new dictionary entry with key `f"Bedrock Custom Model Deployment ({custom_model_arn})"`
    - Set provider to "bedrock"
    - Set model_id to `custom_model_arn`
    - Set display_name to "Bedrock Custom Model Deployment"
    - Place after existing Bedrock options and before SageMaker option
    - _Requirements: 2.1, 2.2, 2.3, 5.1_
  
  - [ ] 7.4 Update SageMaker model option label
    - Change key from "Custom SageMaker Model" to `f"SageMaker Model ({sagemaker_endpoint})"`
    - Keep provider, model_id, and display_name unchanged
    - Update display_name to "SageMaker Model"
    - _Requirements: 4.1, 5.1_
  
  - [ ] 7.5 Add custom model deployment information display
    - Add conditional block after active model info display
    - Check if `selected_model_info['display_name'] == "Bedrock Custom Model Deployment"`
    - Display markdown with explanation about ARN usage for custom model deployments
    - Include information that model_id is the value of bedrock-custom-model-deployment-arn parameter
    - _Requirements: 3.1, 3.2, 3.3, 5.1_

- [ ] 8. Enhance deployed Bedrock model creation with ARN validation
  - [ ] 8.1 Add ARN pattern detection to deployed bedrock_model.py
    - Modify `workshop4/deploy_multi_agent/docker_app/bedrock_model.py`
    - Import `re` module at top of file
    - Add ARN_PATTERN constant: `r'^arn:aws:bedrock:[a-z0-9-]+:\d{12}:custom-model-deployment/[a-zA-Z0-9]+$'`
    - Update `create_bedrock_model()` to detect ARN format using regex
    - Skip validation if model_id matches ARN pattern
    - Keep existing validation for non-ARN model IDs
    - _Requirements: 2.4, 5.1_

- [ ] 9. Deploy CloudFormation template
  - Follow PART-3-DEPLOY-MULTI-AGENT.md instructions for deployment
  - Deploy CloudFormation stack with new SSM parameter
  - Verify parameter is created in SSM Parameter Store
  - Verify parameter has correct default value
  - _Requirements: 1.1, 1.2, 6.1_

- [ ] 10. Create validation script for custom model deployment
  - [ ] 10.1 Create validate_bedrock_custom_model_deployment.py
    - Create file `workshop4/validate/validate_bedrock_custom_model_deployment.py`
    - Import config module to get custom model deployment ARN
    - Import BedrockModel from bedrock_model module
    - Create `validate_bedrock_custom_model_deployment()` function
    - Retrieve bedrock-custom-model-deployment-arn using `get_bedrock_custom_model_deployment_arn()`
    - Check if ARN is placeholder value and skip validation if so
    - Create BedrockModel instance with ARN
    - Invoke model with simple test prompt (e.g., "Hello, please respond with 'OK'")
    - Print clear success message if validation passes
    - Print clear failure message with error details if validation fails
    - Return True on success, False on failure
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ] 10.2 Update validate_ssm_parameters.py
    - Modify `workshop4/validate/validate_ssm_parameters.py`
    - Update `expected_parameters` list to include `'bedrock_custom_model_deployment_arn'`
    - Maintain alphabetical ordering in the list
    - Remove `'strands_knowledge_base_id'` from list (now an environment variable)
    - Add `'my-bedrock-custom-model-deployment-arn'` to placeholder_values list
    - Updated expected_parameters should be: bedrock_custom_model_deployment_arn, default_model_id, max_results, min_score, sagemaker_model_endpoint, sagemaker_model_inference_component, temperature, xgboost_model_endpoint
    - _Requirements: 2.8, 2.9_
  
  - [ ] 10.3 Update validate_all.py to include all validations in correct sequence
    - Modify `workshop4/validate/validate_all.py`
    - Import validation functions in this order:
      1. `validate_ssm_parameters` from validate_ssm_parameters.py
      2. `validate_bedrock_custom_model_deployment` from validate_bedrock_custom_model_deployment.py
      3. `validate_sagemaker_endpoint` from validate_sagemaker_endpoint.py
      4. `validate_xgboost_endpoint` from validate_xgboost_endpoint.py
    - Execute validations in the sequence above
    - Print validation status for each script
    - Include all results in overall validation summary
    - Exit with appropriate status code (0 if all pass, 1 if any fail)
    - _Requirements: 2.6, 2.7_

- [ ] 11. Checkpoint - Remote deployment testing
  - Follow PART-3-DEPLOY-MULTI-AGENT.md instructions for remote testing
  - Deploy application to remote environment
  - Verify SSM parameters are accessible
  - Test model selection dropdown in deployed application
  - Test selecting custom model deployment option
  - Test selecting SageMaker option with endpoint name
  - Test end-to-end functionality with custom model deployment
  - Run validate_all.py to verify all endpoints including custom model deployment
  - Verify backward compatibility with existing models
  - Ensure all tests pass, ask the user if questions arise

- [ ]* 12. Write property test for inference component conditional logic
  - **Property 1: Inference Component Conditional Setting**
  - **Validates: Requirements 4.3**
  - Use hypothesis to generate various inference component values
  - Test that inference component is only included when not placeholder
  - Test with None, placeholder value, and valid component names
  - _Requirements: 4.3_

- [ ]* 13. Write integration tests for backward compatibility
  - Test that all existing Bedrock options still work
  - Test that SageMaker integration still works
  - Test that model invocation parameters are unchanged
  - Test that existing SSM parameters are not modified
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at local and remote stages
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Follow PART-2-MULTI-AGENT.md for local development workflow
- Follow PART-3-DEPLOY-MULTI-AGENT.md for deployment workflow
- Maintain consistency between local and deployed versions
- Test backward compatibility thoroughly to ensure no breaking changes
