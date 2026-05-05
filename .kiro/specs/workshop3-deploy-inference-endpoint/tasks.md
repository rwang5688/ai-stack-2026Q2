# Implementation Tasks

## Overview

Deploy a fine-tuned model using two SageMaker inference patterns: Serverless (CPU, pay-per-request) and Provisioned (GPU, always-on). Both use direct DLC image URI construction with the generic `sagemaker.model.Model` class.

## Tasks

- [x] 1. Implement serverless deployment script (`deploy_serverless.py`)
  - [x] 1.1 Construct DLC image URI directly using AWS ECR pattern with CPU tag
  - [x] 1.2 Create model with generic `sagemaker.model.Model` class and explicit DLC image URI
  - [x] 1.3 Deploy with `ServerlessInferenceConfig` (4096 MB memory, max concurrency 5)
  - [x] 1.4 Implement invoke command using `boto3 sagemaker-runtime` client
  - [x] 1.5 Implement cleanup command (delete endpoint, config, model in order)
  - [x] 1.6 Add educational comments explaining DLC URI pattern and the universal deployment approach

- [x] 2. Document serverless deployment in README
  - [x] 2.1 Explain explicit DLC approach vs HuggingFaceModel wrapper
  - [x] 2.2 Document serverless inference limitations (no GPU, memory cap, cold starts)
  - [x] 2.3 Include runbook for deploy/invoke/cleanup
  - [x] 2.4 Add section on finding available DLC images
  - [x] 2.5 Add section on adapting for other frameworks

- [x] 3. Implement provisioned GPU deployment script (`deploy_provisioned.py`)
  - [x] 3.1 Create `deploy_provisioned.py` with same structure as `deploy_serverless.py` (deploy, invoke, cleanup commands)
  - [x] 3.2 Construct DLC image URI with GPU tag (includes CUDA) for GPU-accelerated inference
  - [x] 3.3 Create model with generic `sagemaker.model.Model` class and GPU-variant DLC image URI
  - [x] 3.4 Deploy with `instance_type="ml.g6.xlarge"` and `initial_instance_count=1` (no ServerlessInferenceConfig)
  - [x] 3.5 Use endpoint name `"distilgpt2-finetuned-wikitext2-provisioned"`
  - [x] 3.6 Implement invoke command (same pattern as serverless but with provisioned endpoint name)
  - [x] 3.7 Implement cleanup command with prominent warning about stopping hourly GPU charges
  - [x] 3.8 Add educational comments explaining GPU deployment, no cold starts, and cost implications
  - [x] 3.9 Add cost warning in deploy output reminding students to run cleanup when done

- [x] 4. Update README.md with provisioned deployment content
  - [x] 4.1 Add deployment comparison table (serverless vs provisioned: cost, latency, GPU, cold starts, scaling)
  - [x] 4.2 Add provisioned deployment runbook section (deploy/invoke/cleanup)
  - [x] 4.3 Add cost warning section for provisioned endpoints (charges per hour while running)
  - [x] 4.4 Update introduction to describe both deployment patterns

- [x] 5. Validate the provisioned deployment script
  - [x] 5.1 Verify the script has no syntax errors
  - [x] 5.2 Verify the script can be imported with mocked dependencies
  - [x] 5.3 Confirm deploy/invoke/cleanup functions are properly defined
