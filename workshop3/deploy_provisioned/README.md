# Workshop 3B: Deploy to a Provisioned GPU Endpoint

Deploy the fine-tuned `rwang5688/distilgpt2-finetuned-wikitext2` model to a SageMaker Real-Time Inference endpoint on a dedicated GPU instance (ml.g6.xlarge) using an explicit DLC image URI.

This is the **provisioned** deployment pattern — compare with `../deploy_serverless/` for the serverless (CPU) pattern.

## Serverless vs Provisioned

| Aspect | Serverless (`../deploy_serverless/`) | Provisioned (this directory) |
|--------|--------------------------------------|------------------------------|
| **Hardware** | Managed CPU | ml.g6.xlarge (NVIDIA L4, 24 GB VRAM) |
| **GPU** | No | Yes |
| **Cold start** | 30-60 seconds | None |
| **Cost model** | Per-request | Per-hour (~$0.80/hr) |
| **Best for** | Small models, infrequent traffic | Large models, low-latency, GPU-required |

## Key Concept: GPU DLC Image Selection

This script uses the same direct URI construction pattern as the serverless script, but with the **GPU tag** (includes CUDA):

```python
# GPU variant — includes CUDA for GPU-accelerated inference
DLC_TAG = "2.1.0-transformers4.37.0-gpu-py310-cu118-ubuntu20.04"
image_uri = f"763104351884.dkr.ecr.{region}.amazonaws.com/huggingface-pytorch-inference:{DLC_TAG}"
```

Compare with the serverless script which uses the CPU tag:
```python
# CPU variant — no CUDA, smaller image, for serverless (CPU-only)
DLC_TAG = "2.1.0-transformers4.37.0-cpu-py310-ubuntu22.04"
```

## Prerequisites

- AWS credentials configured (SageMaker execution role or local credentials with SageMaker permissions)
- Python 3.10+
- The fine-tuned model published to HuggingFace Hub: [rwang5688/distilgpt2-finetuned-wikitext2](https://huggingface.co/rwang5688/distilgpt2-finetuned-wikitext2)
- **Service quota for `ml.g6.xlarge` endpoint instances** (request increase via Service Quotas console if needed)

  **How to request the quota increase:**
  1. Go to the [Service Quotas console](https://console.aws.amazon.com/servicequotas/)
  2. Select **Amazon SageMaker**
  3. Search for `ml.g6.xlarge for endpoint usage`
  4. Click **Request increase at account level** and set the value to at least 1
  5. Approval typically takes a few hours

```bash
pip install boto3
```

**If running locally** (not in SageMaker JupyterLab), provide the role ARN via CLI or edit the script:

```bash
python deploy_provisioned.py deploy --role-arn "arn:aws:iam::123456789012:role/YourSageMakerExecutionRole"
```

Or set `DEFAULT_EXECUTION_ROLE_ARN` at the top of `deploy_provisioned.py`:

```python
DEFAULT_EXECUTION_ROLE_ARN = "arn:aws:iam::123456789012:role/YourSageMakerExecutionRole"
```

## Runbook

All commands accept `--region` to override the AWS region (default: `us-west-2`):

```bash
python deploy_provisioned.py deploy --region us-east-1   # deploy in a different region
```

Or change `DEFAULT_REGION` at the top of the script for a permanent override.

| Argument | Applies to | Default |
|----------|-----------|---------|
| `--model-id` | `deploy` | `rwang5688/distilgpt2-finetuned-wikitext2` |
| `--prompt` | `invoke` | `A long time ago in a galaxy far, far away` |
| `--region` | all | From AWS config, or `us-west-2` |
| `--role-arn` | `deploy` | Auto-detected from AWS session |

### 1. Deploy the provisioned endpoint

```bash
python deploy_provisioned.py deploy
python deploy_provisioned.py deploy --model-id "your-org/your-model"  # custom model
python deploy_provisioned.py deploy --role-arn "arn:aws:iam::..."     # explicit role
```

Creates a real-time endpoint with:
- **Container**: HuggingFace DLC (GPU variant with CUDA, transformers 5.5.3, PyTorch 2.6.0)
- **Instance**: ml.g6.xlarge (NVIDIA L4, 24 GB VRAM)
- **Instance count**: 1

Deployment takes about 5-10 minutes.

**COST WARNING**: This endpoint charges ~$0.80/hour while running. Always clean up when done!

### 2. Send a test request

```bash
python deploy_provisioned.py invoke
python deploy_provisioned.py invoke --prompt "Once upon a time"  # custom prompt
```

No cold start — the GPU instance is always running. Expect fast responses.

### 3. Clean up

```bash
python deploy_provisioned.py cleanup
```

**Always run this when done** — this stops the hourly GPU instance charges immediately.

## Cost

| Duration | Approximate Cost |
|----------|-----------------|
| 15 minutes | ~$0.20 |
| 1 hour | ~$0.80 |
| Forgot overnight (8 hours) | ~$6.40 |

**Tip**: Deploy, run a few test invocations, then immediately clean up. A 15-minute test session costs about $0.20.

## When to Use Provisioned Over Serverless

- Your model requires GPU for acceptable inference latency
- Your model exceeds the 6 GB serverless memory limit
- You need consistent low-latency responses (no cold starts)
- You're serving production traffic with steady request volume
- Your container image exceeds the 10 GB serverless limit
- **You need the latest transformers version** — GPU DLC images have transformers 5.x, but they're too large for serverless (>10 GB with CUDA). Serverless is limited to CPU images which currently max out at transformers 4.49.0

## DLC Version Compatibility

The DLC container's transformers version must be able to load the model files saved during training.

### What We Learned

- **Training** was done with transformers 5.7.0 (on SageMaker JupyterLab)
- **Provisioned endpoint** uses the GPU DLC with transformers 5.5.3 — works perfectly
- **Serverless endpoint** uses the CPU DLC with transformers 4.49.0 — also works (safetensors format is backward-compatible)
- DLC with transformers 4.37.0 — **does NOT work** (too old to deserialize the model)

### Rules of Thumb

1. **Use the latest available DLC image** — newer is almost always better for compatibility
2. **GPU images have newer transformers** — AWS publishes GPU DLCs with the latest versions first
3. **Safetensors format is stable** — models saved as `.safetensors` can generally be loaded by any transformers >= 4.30
4. **When in doubt, match versions** — pin your training transformers version to match the DLC you plan to deploy on
