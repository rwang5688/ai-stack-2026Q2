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

```bash
pip install boto3
```

**If running locally** (not in SageMaker JupyterLab), edit `deploy_provisioned.py` and set `EXECUTION_ROLE_ARN`:

```python
EXECUTION_ROLE_ARN = "arn:aws:iam::123456789012:role/YourSageMakerExecutionRole"
```

## Runbook

### 1. Deploy the provisioned endpoint

```bash
python deploy_provisioned.py deploy
```

Creates a real-time endpoint with:
- **Container**: HuggingFace DLC (GPU variant with CUDA, transformers 4.37.0, PyTorch 2.1.0)
- **Instance**: ml.g6.xlarge (NVIDIA L4, 24 GB VRAM)
- **Instance count**: 1

Deployment takes about 5-10 minutes.

**COST WARNING**: This endpoint charges ~$0.80/hour while running. Always clean up when done!

### 2. Send a test request

```bash
python deploy_provisioned.py invoke
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
