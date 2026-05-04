# Workshop 3: Deploy a Fine-Tuned Model with SageMaker Serverless Inference

Deploy the fine-tuned `rwang5688/distilgpt2-finetuned-wikitext2` model from Workshop 2 to a SageMaker Serverless Inference endpoint using the HuggingFace Deep Learning Container.

## Prerequisites

- AWS credentials configured (SageMaker execution role or local credentials with SageMaker permissions)
- Python 3.10+
- The fine-tuned model published to HuggingFace Hub: [rwang5688/distilgpt2-finetuned-wikitext2](https://huggingface.co/rwang5688/distilgpt2-finetuned-wikitext2)

```bash
pip install sagemaker boto3
```

**If running locally** (not in SageMaker JupyterLab), edit `deploy_serverless.py` and set `LOCAL_EXECUTION_ROLE_ARN` to your SageMaker execution role ARN:

```python
LOCAL_EXECUTION_ROLE_ARN = "arn:aws:iam::123456789012:role/YourSageMakerExecutionRole"
```

If running from a SageMaker JupyterLab terminal, the role is picked up automatically.

## Runbook

### 1. Deploy the serverless endpoint

```bash
python deploy_serverless.py deploy
```

This creates a SageMaker Serverless Inference endpoint with:
- **Model**: `rwang5688/distilgpt2-finetuned-wikitext2` (text-generation)
- **Container**: HuggingFace DLC (transformers 4.37.0, PyTorch 2.1.0)
- **Memory**: 4096 MB
- **Max concurrency**: 5

Deployment takes about 2-5 minutes.

### 2. Send a test request

```bash
python deploy_serverless.py invoke
```

Sends a text-generation prompt to the endpoint. The first request may have a cold start of 30-60 seconds.

### 3. Clean up

```bash
python deploy_serverless.py cleanup
```

Deletes the endpoint, endpoint configuration, and model. **Always run this when done** — serverless endpoints don't charge while idle, but cleaning up avoids any unexpected costs.

## Why Serverless?

distilgpt2 is a small model (~82M parameters, ~330MB) that fits well within the serverless limits:
- Container image < 10 GB
- Model memory footprint < 6 GB

Serverless Inference is a good fit for demos and workshops because you only pay per invocation instead of per hour for a dedicated instance.

## Cost Estimate

Serverless Inference charges per request duration and memory used. For occasional test invocations with distilgpt2, expect costs well under $1/day.
