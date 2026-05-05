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

Both scripts follow the same universal deployment pattern:

```
1. Resolve SageMaker session + role
2. Retrieve DLC image URI via image_uris.retrieve()
3. Create Model(image_uri=..., env=HUB_CONFIG, role=..., sagemaker_session=...)
4. Deploy with endpoint-specific configuration
```

The only difference is step 4:
- **Serverless**: `model.deploy(serverless_inference_config=...)`
- **Provisioned**: `model.deploy(instance_type="ml.g6.xlarge", initial_instance_count=1)`

## Components

### 1. DLC Image URI Retrieval (Shared)

Both scripts use `image_uris.retrieve()` but with different `instance_type` parameters to select the appropriate image variant:

| Script | `instance_type` | Image Variant | Reason |
|--------|-----------------|---------------|--------|
| `deploy_serverless.py` | `ml.m5.xlarge` (CPU) | CPU-optimized | Serverless runs on CPU |
| `deploy_provisioned.py` | `ml.g6.xlarge` (GPU) | GPU-optimized (CUDA) | Provisioned runs on GPU |

### 2. Serverless Deployment (`deploy_serverless.py`)

**Already implemented.** Uses `ServerlessInferenceConfig`:

```python
serverless_config = ServerlessInferenceConfig(
    memory_size_in_mb=4096,
    max_concurrency=5,
)
model.deploy(
    endpoint_name=ENDPOINT_NAME,
    serverless_inference_config=serverless_config,
)
```

### 3. Provisioned Deployment (`deploy_provisioned.py`)

Uses standard real-time deployment with a GPU instance:

```python
model.deploy(
    endpoint_name=ENDPOINT_NAME,
    instance_type="ml.g6.xlarge",
    initial_instance_count=1,
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

### 5. Session and Role Resolution (Shared)

Both scripts use the same `get_sagemaker_session_and_role()` function:
1. Create `sagemaker.Session()`
2. Try `sagemaker.get_execution_role()` (works in SageMaker environments)
3. Fall back to `LOCAL_EXECUTION_ROLE_ARN` constant
4. Exit with helpful error if neither is available

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

1. **Two separate scripts**: Rather than one script with flags, two scripts make the comparison clearer. Students can read each independently and see the full pattern.

2. **Same model, two deployments**: Using the same distilgpt2 model for both lets students compare latency and behavior without model differences confounding the comparison.

3. **GPU instance for provisioned**: `ml.g6.xlarge` (NVIDIA L4) matches the training instance from Workshop 2, reinforcing the connection between training and inference hardware.

4. **Explicit DLC in both**: Both scripts use `image_uris.retrieve()` + `Model()`, showing that the universal pattern works regardless of deployment target.

5. **Cost warnings**: The provisioned script prominently warns about hourly charges and emphasizes cleanup, since forgetting to delete a GPU endpoint is an expensive mistake.

## Correctness Properties

1. **DLC image URI validity**: Retrieved image URIs must be valid ECR URIs in the correct region
2. **GPU variant selection**: The provisioned script must retrieve the GPU-optimized DLC image (different from the CPU variant used by serverless)
3. **Environment variable passthrough**: Hub_Config variables must reach the container in both deployment patterns
4. **Endpoint lifecycle consistency**: Deploy creates exactly 3 resources; cleanup deletes exactly those 3 resources
5. **Invocation round-trip**: Both endpoints return valid JSON responses with generated text
6. **Graceful degradation**: Cleanup handles missing resources without raising unhandled exceptions
7. **No resource conflicts**: The two endpoints use different names and can coexist simultaneously
