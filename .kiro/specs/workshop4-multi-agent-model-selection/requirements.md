# Requirements Document

## Introduction

This feature enhances the workshop4 multi-agent application's model selection capabilities by adding support for Bedrock Custom Model Deployment as a new model selection option and improving the SageMaker model display to show the actual endpoint name. This enables users to leverage custom-trained models deployed through Amazon Bedrock while providing clearer visibility into which models are being used.

## Glossary

- **Application**: The workshop4 multi-agent Streamlit application
- **SSM_Parameter_Store**: AWS Systems Manager Parameter Store for configuration management
- **Custom_Model_Deployment**: A Bedrock custom model deployment identified by an ARN
- **Model_Selection_Dropdown**: The UI component in Streamlit that allows users to choose which model to use
- **SageMaker_Endpoint**: A deployed SageMaker model endpoint for inference
- **CloudFormation_Template**: The infrastructure-as-code template that defines SSM parameters
- **Config_Module**: The config.py module that retrieves configuration values from SSM Parameter Store
- **Bedrock_Model**: A model provider using Amazon Bedrock service
- **Model_ARN**: Amazon Resource Name uniquely identifying a Bedrock custom model deployment
- **Validation_Script**: A standalone Python script that validates configuration and endpoint accessibility

## Requirements

### Requirement 1: SSM Parameter for Bedrock Custom Model Deployment ARN

**User Story:** As a system administrator, I want to configure a Bedrock Custom Model Deployment ARN through SSM Parameter Store, so that the application can access custom-trained models without code changes.

#### Acceptance Criteria

1. THE CloudFormation_Template SHALL define a parameter named `BedrockCustomModelDeploymentArn` under the `/teachers_assistant/{environment}/` path
2. WHEN the CloudFormation_Template is deployed, THE SSM_Parameter_Store SHALL store the custom model deployment ARN with a default value of `my-bedrock-custom-model-deployment-arn`
3. THE CloudFormation_Template SHALL include a description for the BedrockCustomModelDeploymentArn parameter explaining its purpose
4. THE Config_Module SHALL provide a getter function `get_bedrock_custom_model_deployment_arn()` that retrieves the parameter value
5. THE Config_Module SHALL maintain alphabetical ordering of getter functions

### Requirement 2: Bedrock Custom Model Deployment Validation

**User Story:** As a developer, I want a standalone validation script for the Bedrock Custom Model Deployment endpoint, so that I can validate the custom model deployment ARN works before running the full application.

#### Acceptance Criteria

1. THE Validation_Script SHALL be created at `workshop4/validate/validate_bedrock_custom_model_deployment.py`
2. WHEN the validation script runs, THE script SHALL retrieve the bedrock-custom-model-deployment-arn from SSM Parameter Store
3. WHEN the validation script runs, THE script SHALL invoke the custom model deployment with a sample prompt
4. THE validation script SHALL print clear success or failure messages
5. THE validation script SHALL be executable independently without requiring the full application to be running
6. THE validate_all.py script SHALL import and execute validation scripts in this sequence: validate_ssm_parameters, validate_bedrock_custom_model_deployment, validate_sagemaker_endpoint, validate_xgboost_endpoint
7. WHEN validate_all.py runs, THE script SHALL report the validation status for each validation script
8. THE validate_ssm_parameters.py script SHALL update the expected_parameters list to include 'bedrock_custom_model_deployment_arn'
9. THE validate_ssm_parameters.py script SHALL maintain alphabetical ordering of parameters in the expected_parameters list

### Requirement 3: Bedrock Custom Model Deployment Selection

**User Story:** As an application user, I want to select a Bedrock Custom Model Deployment from the model dropdown, so that I can use custom-trained models for inference.

#### Acceptance Criteria

1. WHEN the Application starts, THE Model_Selection_Dropdown SHALL include an option labeled "Bedrock Custom Model Deployment (<arn-value>)" where <arn-value> is replaced with the actual SSM parameter value
2. WHEN a user selects the Bedrock Custom Model Deployment option, THE Application SHALL set the model provider to "bedrock"
3. WHEN a user selects the Bedrock Custom Model Deployment option, THE Application SHALL set the model_id to the value retrieved from the bedrock-custom-model-deployment-arn SSM parameter
4. WHEN invoking the custom model, THE Bedrock_Model SHALL accept the Model_ARN as the model_id parameter
5. THE Application SHALL maintain all existing model selection options without breaking changes

### Requirement 4: Custom Model Deployment Information Display

**User Story:** As an application user, I want to see explanatory information about Bedrock Custom Model Deployment when I select it, so that I understand how the model identification works.

#### Acceptance Criteria

1. WHEN a user selects the Bedrock Custom Model Deployment option, THE Application SHALL display information explaining that the ARN uniquely identifies the deployed model endpoint
2. THE Application SHALL display information explaining that for custom model deployments, the model_id is the value of the bedrock-custom-model-deployment-arn parameter
3. THE Application SHALL display this information in the sidebar or landing page area
4. THE Application SHALL format the information text clearly and readably

### Requirement 5: Improved SageMaker Model Display

**User Story:** As an application user, I want to see the actual SageMaker endpoint name in the model selection dropdown, so that I know which specific model I am using.

#### Acceptance Criteria

1. THE Model_Selection_Dropdown SHALL display the SageMaker option as "SageMaker Model (<endpoint-name>)" where <endpoint-name> is replaced with the actual SSM parameter value
2. WHEN a user selects the SageMaker model option, THE Application SHALL maintain existing behavior for setting the endpoint name
3. WHEN a user selects the SageMaker model option, THE Application SHALL set the inference component only if it exists and is not the placeholder value "my-sagemaker-model-inference-component"
4. THE Application SHALL retrieve the SageMaker endpoint name from SSM_Parameter_Store using the existing getter function

### Requirement 6: Configuration Consistency

**User Story:** As a developer, I want configuration changes to be consistent across both deployment and local development versions, so that the application behaves identically in all environments.

#### Acceptance Criteria

1. WHEN changes are made to the deployed application (docker_app/app.py), THE Application SHALL mirror equivalent changes in the local development version (multi_agent/app.py)
2. THE Application SHALL use the same SSM parameter paths in both versions
3. THE Application SHALL use the same model selection logic in both versions
4. THE Application SHALL maintain feature parity between deployed and local versions

### Requirement 7: End-to-End Development and Deployment Workflow

**User Story:** As a developer, I want to follow a structured development and deployment workflow, so that I can test changes locally before deploying to remote environments.

#### Acceptance Criteria

1. WHEN developing the feature, THE Application SHALL be developed and tested locally following the instructions in PART-2-MULTI-AGENT.md
2. WHEN the local testing is complete, THE Application SHALL be merged and deployed following the instructions in PART-3-DEPLOY-MULTI-AGENT.md
3. WHEN deployed remotely, THE Application SHALL be tested in the remote environment to verify end-to-end functionality
4. THE Application SHALL complete both local and remote testing phases before considering the feature complete
5. THE Application SHALL follow the documented workflow to ensure consistency between local and deployed versions

### Requirement 8: Backward Compatibility

**User Story:** As a system administrator, I want existing model selections to continue working after the update, so that current users experience no disruption.

#### Acceptance Criteria

1. WHEN the Application is updated, THE Application SHALL preserve all existing Bedrock cross-region inference profile options
2. WHEN the Application is updated, THE Application SHALL preserve existing SageMaker model integration functionality
3. WHEN users select previously available models, THE Application SHALL invoke them using the same parameters as before
4. THE Application SHALL not require changes to existing SSM parameters except for adding the new bedrock-custom-model-deployment-arn parameter
