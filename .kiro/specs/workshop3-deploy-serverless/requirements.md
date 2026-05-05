# Requirements Document

## Introduction

This workshop module demonstrates deploying a fine-tuned model to a SageMaker Serverless Inference endpoint using an explicit Deep Learning Container (DLC) image URI. The educational purpose is to teach students the general pattern for deploying ANY model with ANY available DLC — not just Hugging Face models via the convenience wrapper. The module refactors the existing `deploy_serverless.py` from using `HuggingFaceModel` to using the generic `sagemaker.model.Model` class with an explicitly retrieved DLC image URI.

## Glossary

- **Script**: The Python CLI script (`deploy_serverless.py`) that manages the serverless endpoint lifecycle
- **DLC**: AWS Deep Learning Container — pre-built Docker images optimized for ML inference and training
- **DLC_Image_URI**: The fully qualified ECR URI for a specific Deep Learning Container image
- **Model**: A SageMaker Model resource created with a DLC image URI and environment configuration
- **Endpoint**: A SageMaker Serverless Inference endpoint that hosts the deployed model
- **Endpoint_Config**: The SageMaker endpoint configuration specifying serverless memory and concurrency settings
- **SageMaker_Session**: The SageMaker SDK session managing AWS API interactions
- **Hub_Config**: Environment variables passed to the DLC container (HF_MODEL_ID, HF_TASK)
- **README**: The documentation file providing prerequisites, educational context, and a runbook

## Requirements

### Requirement 1: DLC Image URI Retrieval

**User Story:** As a workshop student, I want to see how to explicitly retrieve a DLC image URI from the AWS DLC catalog, so that I can apply this pattern to any framework and model combination.

#### Acceptance Criteria

1. WHEN the deploy command is executed, THE Script SHALL retrieve the HuggingFace DLC image URI using `sagemaker.image_uris.retrieve()` with explicit framework, version, and scope parameters
2. WHEN the image URI is retrieved, THE Script SHALL display the full ECR image URI to the student so they can see the DLC image being used
3. THE Script SHALL specify the framework as "huggingface", the transformers version as "4.37.0", the base framework as "pytorch2.1.0", the Python version as "py310", and the image scope as "inference"
4. THE Script SHALL include comments explaining each parameter of `image_uris.retrieve()` so students understand how to adapt it for other frameworks

### Requirement 2: Generic Model Creation with DLC

**User Story:** As a workshop student, I want to create a SageMaker Model using the generic `Model` class with an explicit DLC image URI, so that I understand the universal pattern for deploying models with any DLC.

#### Acceptance Criteria

1. WHEN the deploy command is executed, THE Script SHALL create a SageMaker Model using `sagemaker.model.Model` (not `HuggingFaceModel`) with the retrieved DLC image URI
2. WHEN the Model is created, THE Script SHALL pass the Hub_Config environment variables (HF_MODEL_ID, HF_TASK) to configure the container
3. WHEN the Model is created, THE Script SHALL pass the SageMaker execution role and session
4. THE Script SHALL include comments explaining that this same pattern works with any DLC image (PyTorch, TensorFlow, MXNet, etc.)

### Requirement 3: Serverless Endpoint Deployment

**User Story:** As a workshop student, I want to deploy the model to a SageMaker Serverless Inference endpoint, so that I can see the cost-effective deployment pattern for small models.

#### Acceptance Criteria

1. WHEN the deploy command is executed, THE Script SHALL create a ServerlessInferenceConfig with 4096 MB memory and max concurrency of 5
2. WHEN the model is deployed, THE Script SHALL use the endpoint name "distilgpt2-finetuned-wikitext2-serverless"
3. WHEN deployment completes, THE Script SHALL display a confirmation message with the endpoint name and instructions to invoke it
4. WHEN deployment is in progress, THE Script SHALL display the serverless configuration parameters (memory, concurrency) and an estimated wait time

### Requirement 4: Endpoint Invocation

**User Story:** As a workshop student, I want to send a test text-generation request to the deployed endpoint, so that I can verify the model is working correctly.

#### Acceptance Criteria

1. WHEN the invoke command is executed, THE Script SHALL send a text-generation request to the serverless endpoint using the SageMaker Runtime client
2. WHEN the invoke command is executed, THE Script SHALL use a sample prompt with generation parameters (max_new_tokens=50, temperature=0.7, do_sample=True)
3. WHEN a response is received, THE Script SHALL display both the prompt and the generated text in a readable format
4. WHEN the endpoint has a cold start, THE Script SHALL inform the student that the first request may take 30-60 seconds

### Requirement 5: Resource Cleanup

**User Story:** As a workshop student, I want to delete all deployed resources, so that I avoid unexpected AWS charges.

#### Acceptance Criteria

1. WHEN the cleanup command is executed, THE Script SHALL delete the endpoint, endpoint configuration, and model in the correct order
2. WHEN the cleanup command is executed, THE Script SHALL display the name of each resource being deleted
3. IF the endpoint does not exist, THEN THE Script SHALL display a message indicating nothing to clean up and exit gracefully
4. WHEN cleanup completes, THE Script SHALL confirm that no further charges will be incurred

### Requirement 6: SageMaker Session and Role Resolution

**User Story:** As a workshop student, I want the script to automatically resolve my SageMaker execution role whether I run it from SageMaker or locally, so that I can use the script in either environment.

#### Acceptance Criteria

1. WHEN the script runs inside a SageMaker environment, THE Script SHALL automatically resolve the execution role using `sagemaker.get_execution_role()`
2. WHEN the script runs locally and LOCAL_EXECUTION_ROLE_ARN is configured, THE Script SHALL use the configured role ARN
3. IF the script runs locally and LOCAL_EXECUTION_ROLE_ARN is not set, THEN THE Script SHALL display an error message with instructions on how to set the role ARN and exit with a non-zero status code
4. WHEN the session is established, THE Script SHALL display the role ARN, default S3 bucket, and AWS region

### Requirement 7: Educational Documentation

**User Story:** As a workshop student, I want comprehensive documentation explaining the DLC approach and how it differs from the convenience wrapper, so that I understand when and why to use explicit DLC image URIs.

#### Acceptance Criteria

1. THE README SHALL explain the difference between using `HuggingFaceModel` (convenience wrapper) and the explicit DLC approach with `Model` + `image_uris.retrieve()`
2. THE README SHALL document how to find available DLC images from the AWS DLC repository
3. THE README SHALL provide a link to the AWS DLC available images catalog
4. THE README SHALL include a runbook with deploy, invoke, and cleanup steps
5. THE README SHALL document prerequisites including AWS credentials, Python packages, and the fine-tuned model on HuggingFace Hub
6. THE README SHALL explain why serverless inference is appropriate for this model (small size, workshop/demo use case)
7. THE README SHALL include a section showing how to adapt the pattern for other frameworks (PyTorch, TensorFlow)
