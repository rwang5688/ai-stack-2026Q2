# Workshop 3A: Deploy to a Serverless Inference Endpoint

Deploy the fine-tuned `rwang5688/distilgpt2-finetuned-wikitext2` model to a SageMaker Serverless Inference endpoint (CPU, pay-per-request) using an explicit DLC image URI.

This is the **serverless** deployment pattern — compare with `../deploy_provisioned/` for the provisioned GPU pattern.

## Serverless vs Provisioned

| Aspect | Serverless (this directory) | Provisioned (`../deploy_provisioned/`) |
|--------|----------------------------|----------------------------------------|
| **Hardware** | Managed CPU | ml.g6.xlarge (NVIDIA L4, 24 GB VRAM) |
| **GPU** | No | Yes |
| **Cold start** | 30-60 seconds | None |
| **Cost model** | Per-request (duration x memory) | Per-hour (~$0.80/hr) |
| **Best for** | Small models, infrequent traffic, demos | Large models, low-latency, GPU-required |

## Key Concept: Explicit DLC Image Selection

This script demonstrates the **universal pattern** for deploying models to SageMaker using any available Deep Learning Container:

```python
from sagemaker.model import Model

# Construct the DLC image URI directly
# Pattern: <account_id>.dkr.ecr.<region>.amazonaws.com/<repository>:<tag>
image_uri = f"763104351884.dkr.ecr.{region}.amazonaws.com/huggingface-pytorch-inference:{tag}"

model = Model(image_uri=image_uri, env={...}, role=role)
model.deploy(serverless_inference_config=...)
```

Instead of using the `HuggingFaceModel` wrapper (which hides the DLC selection), we use the generic `Model` class with a directly constructed DLC image URI. This pattern works with ANY framework — PyTorch, TensorFlow, MXNet, or custom containers.

### Why This Approach Over the Wrapper?

| Approach | Pros | Cons |
|----------|------|------|
| **`HuggingFaceModel` wrapper** | Convenient, fewer lines of code | Only works for HuggingFace models; hides the DLC selection |
| **Generic `Model` + explicit DLC** | Works with ANY framework/model; you see exactly which container is used | Slightly more code |

## Finding Available DLC Images

- **Full catalog**: [aws.github.io/deep-learning-containers/reference/available_images/](https://aws.github.io/deep-learning-containers/reference/available_images/)
- **URI pattern**: `763104351884.dkr.ecr.<region>.amazonaws.com/<repository>:<tag>`
- The account ID `763104351884` is the same across all regions for AWS DLC images

### Common Frameworks

| Framework | `framework` param | Example `version` | `base_framework_version` |
|-----------|-------------------|-------------------|--------------------------|
| HuggingFace | `"huggingface"` | `"4.37.0"` | `"pytorch2.1.0"` |
| PyTorch | `"pytorch"` | `"2.1.0"` | — |
| TensorFlow | `"tensorflow"` | `"2.14.0"` | — |

## Prerequisites

- AWS credentials configured (SageMaker execution role or local credentials with SageMaker permissions)
- Python 3.10+
- The fine-tuned model published to HuggingFace Hub: [rwang5688/distilgpt2-finetuned-wikitext2](https://huggingface.co/rwang5688/distilgpt2-finetuned-wikitext2)

```bash
pip install sagemaker boto3
```

**If running locally** (not in SageMaker JupyterLab), edit `deploy_serverless.py` and set `LOCAL_EXECUTION_ROLE_ARN`:

```python
LOCAL_EXECUTION_ROLE_ARN = "arn:aws:iam::123456789012:role/YourSageMakerExecutionRole"
```

## Runbook

### 1. Deploy the serverless endpoint

```bash
python deploy_serverless.py deploy
```

Creates a serverless endpoint with:
- **Container**: HuggingFace DLC (CPU variant, transformers 4.37.0, PyTorch 2.1.0)
- **Memory**: 4096 MB
- **Max concurrency**: 5

The script prints the full DLC image URI so you can see exactly which container is being used.

Deployment takes about 2-5 minutes.

### 2. Send a test request

```bash
python deploy_serverless.py invoke
```

First request may have a cold start of 30-60 seconds.

### 3. Clean up

```bash
python deploy_serverless.py cleanup
```

Deletes the endpoint, endpoint configuration, and model.

## Serverless Inference Limitations

| Limitation | Value |
|------------|-------|
| **Maximum memory** | 6144 MB (6 GB) |
| **Maximum container image size** | 10 GB (uncompressed) |
| **Maximum concurrency** | 200 (per endpoint) |
| **GPU support** | **None** — CPU only |
| **Maximum payload size** | 4 MB (request) / 4 MB (response) |
| **Maximum invocation timeout** | 60 seconds |
| **Cold start** | 30-60+ seconds on first request after idle |

### Key Implications

- **No GPU**: Serverless endpoints run exclusively on CPU. For GPU, use `../deploy_provisioned/`.
- **Memory ceiling**: Model + framework must fit within 6 GB. distilgpt2 (~330 MB) fits easily.
- **Container size**: DLC image + model artifacts must stay under 10 GB uncompressed.
- **Cold starts**: Not suitable for latency-sensitive production workloads.

## Cost Estimate

Serverless Inference charges per request duration and memory used. For occasional test invocations with distilgpt2, expect costs well under $1/day.
