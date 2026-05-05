# Design Document

## Introduction

This document describes the technical design for refactoring the Workshop 3 serverless deployment script from using the `HuggingFaceModel` convenience wrapper to using explicit DLC image URI retrieval with the generic `sagemaker.model.Model` class. The refactoring teaches students the universal pattern for deploying any model with any available Deep Learning Container.

## Architecture Overview

The module is a single Python CLI script with supporting documentation:

```
workshop3/deploy_serverless/
├── deploy_serverless.py    # CLI script (deploy, invoke, cleanup)
└── README.md               # Documentation, runbook, and educational context
```

### Execution Flow

```
[deploy command]
       │
       ▼
  1. Resolve SageMaker session + role
       │
       ▼
  2. Retrieve DLC image URI via image_uris.retrieve()
       │        ├── framework: "huggingface"
       │        ├── version: "4.37.0" (transformers)
       │        ├── base_framework_version: "pytorch2.1.0"
       │        ├── py_version: "py310"
       │        └── image_scope: "inference"
       │
       ▼
  3. Create Model(image_uri=..., env=HUB_CONFIG, role=..., sagemaker_session=...)
       │
       ▼
  4. Configure ServerlessInferenceConfig(memory=4096, concurrency=5)
       │
       ▼
  5. model.deploy(endpoint_name=..., serverless_inference_config=...)
       │
       ▼
  Endpoint InService

[invoke command]
       │
       ▼
  1. Create sagemaker-runtime client
       │
       ▼
  2. invoke_endpoint(EndpointName, ContentType, Body)
       │
       ▼
  3. Display response

[cleanup command]
       │
       ▼
  1. Describe endpoint → get config name
       │
       ▼
  2. Describe endpoint config → get model name
       │
       ▼
  3. Delete endpoint → delete config → delete model
```

## Components

### 1. DLC Image URI Retrieval

**Purpose**: Explicitly retrieve the container image URI from the AWS DLC catalog, making the DLC selection visible and configurable.

**Implementation**:
```python
from sagemaker import image_uris

image_uri = image_uris.retrieve(
    framework="huggingface",
    region=sess.boto_region_name,
    version="4.37.0",              # transformers version
    instance_type="ml.m5.xlarge",  # used for image selection only
    image_scope="inference",
    py_version="py310",
    base_framework_version="pytorch2.1.0"
)
```

**Design Decisions**:
- `instance_type` is required by the API for image selection but does not affect serverless deployment — it selects the CPU/GPU variant of the image
- Using `"ml.m5.xlarge"` (CPU) since serverless inference uses CPU-based containers
- The region is derived from the SageMaker session to ensure the correct regional ECR repository is used

### 2. Generic Model Creation

**Purpose**: Create a SageMaker Model using the universal `Model` class instead of the framework-specific `HuggingFaceModel` wrapper.

**Implementation**:
```python
from sagemaker.model import Model

model = Model(
    image_uri=image_uri,
    env=HUB_CONFIG,
    role=role,
    sagemaker_session=sess,
)
```

**Design Decisions**:
- The generic `Model` class accepts any DLC image URI, making the pattern transferable to PyTorch, TensorFlow, MXNet, or custom containers
- Environment variables (`HUB_CONFIG`) configure the container behavior — this is how the HuggingFace DLC knows which model to load and what task to perform
- No model data (S3 artifact) is needed because the HuggingFace DLC downloads the model from the Hub at container startup using `HF_MODEL_ID`

### 3. Configuration Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `ENDPOINT_NAME` | `"distilgpt2-finetuned-wikitext2-serverless"` | Unique endpoint identifier |
| `HUB_CONFIG` | `{"HF_MODEL_ID": "rwang5688/distilgpt2-finetuned-wikitext2", "HF_TASK": "text-generation"}` | Container environment variables |
| `TRANSFORMERS_VERSION` | `"4.37.0"` | DLC transformers version |
| `PYTORCH_VERSION` | `"pytorch2.1.0"` | DLC base framework version (note: format includes "pytorch" prefix for `base_framework_version`) |
| `PY_VERSION` | `"py310"` | Python version in the DLC |
| `MEMORY_SIZE_IN_MB` | `4096` | Serverless memory allocation |
| `MAX_CONCURRENCY` | `5` | Maximum concurrent invocations |
| `IMAGE_SCOPE` | `"inference"` | DLC image scope (inference vs training) |

### 4. Session and Role Resolution

**Purpose**: Support both SageMaker-hosted and local execution environments.

**Logic**:
1. Create `sagemaker.Session()`
2. Try `sagemaker.get_execution_role()` (works in SageMaker environments)
3. Fall back to `LOCAL_EXECUTION_ROLE_ARN` constant (for local development)
4. Exit with helpful error if neither is available

### 5. Endpoint Invocation

**Purpose**: Demonstrate sending inference requests to the serverless endpoint.

**Implementation**: Uses `boto3.client("sagemaker-runtime").invoke_endpoint()` directly rather than the SageMaker SDK predictor, showing students the low-level API pattern.

### 6. Resource Cleanup

**Purpose**: Delete all AWS resources created during deployment.

**Deletion Order** (required by AWS dependencies):
1. Endpoint (depends on endpoint config)
2. Endpoint Configuration (depends on model)
3. Model

**Error Handling**: Gracefully handles the case where the endpoint doesn't exist (already cleaned up or never deployed).

## Key Design Decisions

1. **Generic `Model` over `HuggingFaceModel`**: The `HuggingFaceModel` wrapper is convenient but hides the DLC selection process. Using the generic `Model` class with explicit `image_uris.retrieve()` teaches students the universal pattern that works with any framework.

2. **`image_uris.retrieve()` over hardcoded URI**: While you could hardcode an ECR URI, using `image_uris.retrieve()` is the recommended approach because it handles regional ECR endpoints and version resolution automatically.

3. **CPU instance type for image selection**: Serverless inference runs on CPU-based infrastructure. Using `"ml.m5.xlarge"` as the instance_type parameter selects the CPU variant of the DLC image.

4. **Direct boto3 for invocation**: Using `boto3.client("sagemaker-runtime")` for invocation (rather than the SDK's `Predictor`) shows students the raw API call, which is more transferable to other languages and environments.

5. **Single-file CLI script**: Keeps the workshop simple — one file with three commands. No package structure or dependencies beyond `sagemaker` and `boto3`.

6. **Comments as education**: The script includes extensive comments explaining each step, parameter, and design choice. The code is the teaching material.

## Differences from Current Implementation

| Aspect | Current (HuggingFaceModel) | Refactored (Generic Model + DLC) |
|--------|---------------------------|----------------------------------|
| Import | `from sagemaker.huggingface.model import HuggingFaceModel` | `from sagemaker.model import Model` + `from sagemaker import image_uris` |
| Image selection | Implicit (SDK resolves internally) | Explicit via `image_uris.retrieve()` |
| Model creation | `HuggingFaceModel(transformers_version=..., pytorch_version=...)` | `Model(image_uri=image_uri, env=...)` |
| Transferability | HuggingFace models only | Any model + any DLC |
| Educational value | "It works" | "Here's how it works and how to adapt it" |

## Correctness Properties

1. **DLC image URI validity**: The retrieved image URI must be a valid ECR URI in the correct region matching the SageMaker session region
2. **Environment variable passthrough**: All Hub_Config environment variables must be passed to the container and accessible at inference time
3. **Endpoint lifecycle consistency**: Deploy creates exactly 3 resources (model, endpoint config, endpoint); cleanup deletes exactly those 3 resources
4. **Invocation round-trip**: A valid JSON payload sent to the endpoint returns a valid JSON response containing generated text
5. **Graceful degradation**: Cleanup handles missing resources without raising unhandled exceptions
6. **Role resolution determinism**: The script always resolves to exactly one execution role or exits with a clear error — never proceeds without a role
