# Requirements Document

## Introduction

This workshop module demonstrates deploying a fine-tuned model to SageMaker Inference endpoints using two deployment patterns: Serverless Inference (CPU, pay-per-request) and Provisioned Real-Time Inference (GPU, always-on). Both patterns use explicit Deep Learning Container (DLC) image URIs with the generic `sagemaker.model.Model` class, teaching students the universal pattern for deploying ANY model with ANY available DLC.

## Glossary

- **Serverless_Script**: The Python CLI script (`deploy_serverless.py`) that manages the serverless endpoint lifecycle
- **Provisioned_Script**: The Python CLI script (`deploy_provisioned.py`) that manages the GPU-backed real-time endpoint lifecycle
- **DLC**: AWS Deep Learning Container — pre-built Docker images optimized for ML inference and training
- **DLC_Image_URI**: The fully qualified ECR URI for a specific Deep Learning Container image
- **Model**: A SageMaker Model resource created with a DLC image URI and environment configuration
- **Serverless_Endpoint**: A SageMaker Serverless Inference endpoint (CPU-only, scales to zero)
- **Provisioned_Endpoint**: A SageMaker Real-Time Inference endpoint backed by a dedicated GPU instance
- **Endpoint_Config**: The SageMaker endpoint configuration specifying deployment parameters
- **SageMaker_Session**: The SageMaker SDK session managing AWS API interactions
- **Hub_Config**: Environment variables passed to the DLC container (HF_MODEL_ID, HF_TASK)
- **README**: The documentation file providing prerequisites, educational context, and a runbook

## Requirements

### Requirement 1: DLC Image URI Retrieval

**User Story:** As a workshop student, I want to see how to explicitly retrieve a DLC image URI from the AWS DLC catalog, so that I can apply this pattern to any framework and model combination.

#### Acceptance Criteria

1. WHEN the deploy command is executed in either script, THE Script SHALL retrieve the HuggingFace DLC image URI using `sagemaker.image_uris.retrieve()` with explicit framework, version, and scope parameters
2. WHEN the image URI is retrieved, THE Script SHALL display the full ECR image URI to the student so they can see the DLC image being used
3. THE Serverless_Script SHALL use a CPU instance type (`ml.m5.xlarge`) for image selection since serverless runs on CPU
4. THE Provisioned_Script SHALL use a GPU instance type (`ml.g6.xlarge`) for image selection to get the GPU-optimized DLC variant
5. THE Scripts SHALL include comments explaining each parameter of `image_uris.retrieve()` so students understand how to adapt it for other frameworks

### Requirement 2: Generic Model Creation with DLC

**User Story:** As a workshop student, I want to create a SageMaker Model using the generic `Model` class with an explicit DLC image URI, so that I understand the universal pattern for deploying models with any DLC.

#### Acceptance Criteria

1. WHEN the deploy command is executed, THE Scripts SHALL create a SageMaker Model using `sagemaker.model.Model` (not `HuggingFaceModel`) with the retrieved DLC image URI
2. WHEN the Model is created, THE Scripts SHALL pass the Hub_Config environment variables (HF_MODEL_ID, HF_TASK) to configure the container
3. WHEN the Model is created, THE Scripts SHALL pass the SageMaker execution role and session
4. THE Scripts SHALL include comments explaining that this same pattern works with any DLC image (PyTorch, TensorFlow, MXNet, etc.)

### Requirement 3: Serverless Endpoint Deployment

**User Story:** As a workshop student, I want to deploy the model to a SageMaker Serverless Inference endpoint, so that I can see the cost-effective deployment pattern for small models on CPU.

#### Acceptance Criteria

1. WHEN the deploy command is executed, THE Serverless_Script SHALL create a ServerlessInferenceConfig with 4096 MB memory and max concurrency of 5
2. WHEN the model is deployed, THE Serverless_Script SHALL use the endpoint name "distilgpt2-finetuned-wikitext2-serverless"
3. WHEN deployment completes, THE Serverless_Script SHALL display a confirmation message with the endpoint name and instructions to invoke it
4. WHEN deployment is in progress, THE Serverless_Script SHALL display the serverless configuration parameters (memory, concurrency) and an estimated wait time

### Requirement 4: Provisioned GPU Endpoint Deployment

**User Story:** As a workshop student, I want to deploy the model to a provisioned real-time endpoint on a GPU instance, so that I can see how to deploy models that require GPU acceleration and compare performance with serverless.

#### Acceptance Criteria

1. WHEN the deploy command is executed, THE Provisioned_Script SHALL deploy the model to an `ml.g6.xlarge` instance with `initial_instance_count=1`
2. WHEN the model is deployed, THE Provisioned_Script SHALL use the endpoint name "distilgpt2-finetuned-wikitext2-provisioned"
3. WHEN deployment completes, THE Provisioned_Script SHALL display a confirmation message with the endpoint name and instructions to invoke it
4. WHEN deployment is in progress, THE Provisioned_Script SHALL display the instance type, instance count, and an estimated wait time (5-10 minutes)
5. THE Provisioned_Script SHALL include comments explaining that provisioned endpoints have no cold starts but charge per hour

### Requirement 5: Endpoint Invocation

**User Story:** As a workshop student, I want to send a test text-generation request to either endpoint, so that I can verify the model is working and compare response times.

#### Acceptance Criteria

1. WHEN the invoke command is executed, THE Scripts SHALL send a text-generation request using the SageMaker Runtime client
2. WHEN the invoke command is executed, THE Scripts SHALL use a sample prompt with generation parameters (max_new_tokens=50, temperature=0.7, do_sample=True)
3. WHEN a response is received, THE Scripts SHALL display both the prompt and the generated text in a readable format
4. WHEN invoking the serverless endpoint, THE Serverless_Script SHALL inform the student that the first request may have a cold start of 30-60 seconds
5. WHEN invoking the provisioned endpoint, THE Provisioned_Script SHALL note that there is no cold start since the instance is always running

### Requirement 6: Resource Cleanup

**User Story:** As a workshop student, I want to delete all deployed resources, so that I avoid unexpected AWS charges.

#### Acceptance Criteria

1. WHEN the cleanup command is executed, THE Scripts SHALL delete the endpoint, endpoint configuration, and model in the correct order
2. WHEN the cleanup command is executed, THE Scripts SHALL display the name of each resource being deleted
3. IF the endpoint does not exist, THEN THE Scripts SHALL display a message indicating nothing to clean up and exit gracefully
4. WHEN cleanup completes for the provisioned endpoint, THE Provisioned_Script SHALL emphasize that the GPU instance charges stop immediately
5. WHEN cleanup completes, THE Scripts SHALL confirm that no further charges will be incurred

### Requirement 7: SageMaker Session and Role Resolution

**User Story:** As a workshop student, I want the scripts to automatically resolve my SageMaker execution role whether I run them from SageMaker or locally, so that I can use the scripts in either environment.

#### Acceptance Criteria

1. WHEN the script runs inside a SageMaker environment, THE Scripts SHALL automatically resolve the execution role using `sagemaker.get_execution_role()`
2. WHEN the script runs locally and LOCAL_EXECUTION_ROLE_ARN is configured, THE Scripts SHALL use the configured role ARN
3. IF the script runs locally and LOCAL_EXECUTION_ROLE_ARN is not set, THEN THE Scripts SHALL display an error message with instructions on how to set the role ARN and exit with a non-zero status code
4. WHEN the session is established, THE Scripts SHALL display the role ARN, default S3 bucket, and AWS region

### Requirement 8: Educational Documentation

**User Story:** As a workshop student, I want comprehensive documentation comparing both deployment patterns and explaining when to use each, so that I can make informed deployment decisions for my own models.

#### Acceptance Criteria

1. THE README SHALL explain the difference between serverless and provisioned deployment patterns
2. THE README SHALL include a comparison table showing tradeoffs (cost, latency, GPU support, cold starts, scaling)
3. THE README SHALL explain the explicit DLC approach with `Model` + `image_uris.retrieve()`
4. THE README SHALL document how to find available DLC images from the AWS DLC repository
5. THE README SHALL include runbooks for both serverless and provisioned deployment
6. THE README SHALL document serverless inference limitations (no GPU, memory cap, cold starts)
7. THE README SHALL document provisioned endpoint cost implications (charges per hour while running)
8. THE README SHALL include a section showing how to adapt the pattern for other frameworks (PyTorch, TensorFlow)
