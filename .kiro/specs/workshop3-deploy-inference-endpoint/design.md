# Design Document

## Introduction

This document describes the technical design for Workshop 3, which demonstrates deploying a fine-tuned model to SageMaker using two inference patterns: Serverless (CPU, pay-per-request) and Provisioned (GPU, always-on). Both use explicit DLC image URI retrieval with the generic `sagemaker.model.Model` class.

## Architecture Overview

```
workshop3/deploy_serverless/
├── deploy_serverless.py      # Serverless endpoint (CPU, pay-per-request)
├── deploy_provisioned.py     # Provisioned endpoint (GPU, always-on)
└── README.md                 # Documentation covering both patterns
```

### Shared Pattern

Both scripts follow the same universal deployment pattern using boto3 directly:

```
1. Resolve AWS region and execution role
2. Construct DLC image URI for the region (CPU or GPU tag)
3. CreateModel (boto3 create_model API with image URI and environment variables)
4. CreateEndpointConfig (serverless or provisioned settings)
5. CreateEndpoint and wait for InService
```

The only difference is step 4:
- **Serverless**: `model.deploy(serverless_inference_config=...)`
- **Provisioned**: `model.deploy(instance_type="ml.g6.xlarge", initial_instance_count=1)`

## Components

### 1. DLC Image URI Construction (Shared)

Both scripts construct the DLC image URI directly using the predictable AWS pattern:
`763104351884.dkr.ecr.<region>.amazonaws.com/<repository>:<tag>`

The only difference is the tag — CPU vs GPU variant:

| Script | DLC Tag | Image Variant | Reason |
|--------|---------|---------------|--------|
| `deploy_serverless.py` | `2.1.0-transformers4.37.0-cpu-py310-ubuntu22.04` | CPU-optimized | Serverless runs on CPU |
| `deploy_provisioned.py` | `2.1.0-transformers4.37.0-gpu-py310-cu118-ubuntu20.04` | GPU-optimized (CUDA) | Provisioned runs on GPU |

### 2. Serverless Deployment (`deploy_serverless.py`)

**Already implemented.** Uses boto3 `create_endpoint_config` with `ServerlessConfig`:

```python
sm_client.create_endpoint_config(
    EndpointConfigName=config_name,
    ProductionVariants=[{
        "VariantName": "AllTraffic",
        "ModelName": model_name,
        "ServerlessConfig": {
            "MemorySizeInMB": 4096,
            "MaxConcurrency": 5,
        },
    }],
)
```

### 3. Provisioned Deployment (`deploy_provisioned.py`)

Uses boto3 `create_endpoint_config` with a dedicated GPU instance:

```python
sm_client.create_endpoint_config(
    EndpointConfigName=config_name,
    ProductionVariants=[{
        "VariantName": "AllTraffic",
        "ModelName": model_name,
        "InstanceType": "ml.g6.xlarge",
        "InitialInstanceCount": 1,
    }],
)
```

**Key differences from serverless**:
- Deploys to a dedicated `ml.g6.xlarge` instance (NVIDIA L4, 24 GB VRAM)
- No cold starts — instance is always running
- Charges per hour while the endpoint is active (~$0.80/hr for ml.g6.xlarge)
- Supports GPU-accelerated inference

### 4. Configuration Constants

#### Serverless Script

| Constant | Value |
|----------|-------|
| `ENDPOINT_NAME` | `"distilgpt2-finetuned-wikitext2-serverless"` |
| `INSTANCE_TYPE` | `"ml.m5.xlarge"` (for image selection only) |
| `MEMORY_SIZE_IN_MB` | `4096` |
| `MAX_CONCURRENCY` | `5` |

#### Provisioned Script

| Constant | Value |
|----------|-------|
| `ENDPOINT_NAME` | `"distilgpt2-finetuned-wikitext2-provisioned"` |
| `DEPLOY_INSTANCE_TYPE` | `"ml.g6.xlarge"` |
| `INITIAL_INSTANCE_COUNT` | `1` |

#### Shared Constants

| Constant | Value |
|----------|-------|
| `HUB_CONFIG` | `{"HF_MODEL_ID": "rwang5688/distilgpt2-finetuned-wikitext2", "HF_TASK": "text-generation"}` |
| `TRANSFORMERS_VERSION` | `"4.37.0"` |
| `BASE_FRAMEWORK_VERSION` | `"pytorch2.1.0"` |
| `PY_VERSION` | `"py310"` |
| `IMAGE_SCOPE` | `"inference"` |

### 4. Session and Role Resolution (Shared)

Both scripts use the same `get_execution_role()` function:
1. Check `EXECUTION_ROLE_ARN` constant (for local development)
2. Try `sagemaker.get_execution_role()` (works in SageMaker environments, optional import)
3. Exit with helpful error if neither is available

### 6. Endpoint Invocation (Shared Pattern)

Both scripts use `boto3.client("sagemaker-runtime").invoke_endpoint()` with the same payload structure. The only difference is the endpoint name.

### 7. Resource Cleanup (Shared Pattern)

Both scripts follow the same deletion order:
1. Delete endpoint
2. Delete endpoint configuration
3. Delete model

**Critical for provisioned**: Cleanup stops the hourly GPU instance charges immediately.

## Deployment Comparison

| Aspect | Serverless | Provisioned |
|--------|-----------|-------------|
| Instance | None (managed CPU) | ml.g6.xlarge (NVIDIA L4) |
| GPU | No | Yes (24 GB VRAM) |
| Cold start | 30-60 seconds | None |
| Cost model | Per-request (duration × memory) | Per-hour (~$0.80/hr) |
| Max memory | 6 GB | Instance memory (16 GB+) |
| Max container | 10 GB | No limit |
| Scaling | Auto (0 to max_concurrency) | Manual (initial_instance_count) |
| Best for | Small models, infrequent traffic | Large models, low-latency, GPU-required |

## Key Design Decisions

1. **Two separate scripts in separate directories**: Rather than one script with flags, two scripts in their own directories make the comparison clearer. Students can read each independently and see the full pattern.

2. **Same model, two deployments**: Using the same distilgpt2 model for both lets students compare latency and behavior without model differences confounding the comparison.

3. **GPU instance for provisioned**: `ml.g6.xlarge` (NVIDIA L4) matches the training instance from Workshop 2, reinforcing the connection between training and inference hardware.

4. **boto3 directly over SageMaker SDK wrappers**: Using boto3 `create_model`, `create_endpoint_config`, and `create_endpoint` directly ensures compatibility with any SageMaker SDK version (v2 or v3) and shows students the raw AWS API calls, which are transferable to any language.

5. **Direct DLC URI construction over SDK helpers**: Constructing the ECR URI from the known pattern (`763104351884.dkr.ecr.<region>.amazonaws.com/<repo>:<tag>`) is more educational than a helper function — students see exactly how the URI is composed and can look up tags in the DLC catalog.

6. **Cost warnings**: The provisioned script prominently warns about hourly charges and emphasizes cleanup, since forgetting to delete a GPU endpoint is an expensive mistake.

## Correctness Properties

1. **DLC image URI validity**: Retrieved image URIs must be valid ECR URIs in the correct region
2. **GPU variant selection**: The provisioned script must retrieve the GPU-optimized DLC image (different from the CPU variant used by serverless)
3. **Environment variable passthrough**: Hub_Config variables must reach the container in both deployment patterns
4. **Endpoint lifecycle consistency**: Deploy creates exactly 3 resources; cleanup deletes exactly those 3 resources
5. **Invocation round-trip**: Both endpoints return valid JSON responses with generated text
6. **Graceful degradation**: Cleanup handles missing resources without raising unhandled exceptions
7. **No resource conflicts**: The two endpoints use different names and can coexist simultaneously
