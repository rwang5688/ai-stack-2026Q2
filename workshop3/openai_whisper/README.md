# OpenAI Whisper on SageMaker — PyTorch DLC Deployment

Deploy the OpenAI Whisper "base" model for automatic speech recognition using PyTorch Deep Learning Containers on SageMaker. Two notebook variants target different SageMaker Studio runtime images.

## Notebooks

| Notebook | SageMaker Studio Image | Status |
|----------|----------------------|--------|
| `pytorch_sagemaker_4.ipynb` | SageMaker Distribution 4.x | **PRIMARY — use this one** |
| `pytorch_sagemaker_2.ipynb` | Data Science 2.0 | ⚠️ FALLBACK ONLY — last resort if 4.x fails during workshop |

The 2.x notebook exists as emergency insurance. If something blows up with Distribution 4.x tonight and we're out of time, switch to `pytorch_sagemaker_2.ipynb` with the Data Science 2.0 image and it will work. Otherwise, pretend it doesn't exist.

## Quick Start

1. Open the notebook in SageMaker Studio
2. Select the correct image (see table above) and `ml.m5.large` instance (or any instance — `ml.g6.xlarge` works too, the GPU isn't needed for the notebook kernel itself)
3. Run All Cells — no manual edits required (bucket and region resolve automatically)

## Directory Structure

```
openai_whisper/
├── pytorch_sagemaker_2.ipynb    # Notebook for Distribution 2.x
├── pytorch_sagemaker_4.ipynb    # Notebook for Distribution 4.x
├── code_sagemaker_2/            # Inference code packaged into the 2.x DLC container
│   ├── inference.py
│   └── requirements.txt
└── code_sagemaker_4/            # Inference code packaged into the 4.x DLC container
    ├── inference.py
    └── requirements.txt
```

## Differences Between Notebook Variants

### Package Versions

| Package | Distribution 2.x | Distribution 4.x |
|---------|-------------------|-------------------|
| openai-whisper | 20230918 | 20231117 |
| torchaudio | 2.1.0 | 2.5.1 |
| datasets | 2.16.1 | 3.2.0 |
| sagemaker SDK | 2.184.0 | 2.232.1 |
| librosa | 0.10.1 | 0.10.2 |
| soundfile | 0.12.1 | 0.12.1 |

### DLC Inference Image

| Variant | Image Tag |
|---------|-----------|
| 2.x | `huggingface-pytorch-inference:2.0.0-transformers4.28.1-gpu-py310-cu118-ubuntu20.04` |
| 4.x | `huggingface-pytorch-inference:2.6.0-transformers5.5.3-gpu-py312-cu124-ubuntu22.04` |

ECR registry: `763104351884.dkr.ecr.{region}.amazonaws.com/`

### Inference Code Directory

| Variant | `source_dir` |
|---------|-------------|
| 2.x | `code_sagemaker_2` |
| 4.x | `code_sagemaker_4` |

Both directories contain identical `inference.py` logic (model_fn + transform_fn). They're split so that `requirements.txt` inside each container can diverge if needed.

### Model Serving Environment Variables (MMS vs TorchServe)

**IMPORTANT: This has NOTHING to do with which SageMaker Studio image you run the notebook on.**

There are two separate, independent things happening:

1. **Studio kernel image** (where your notebook Python code runs) — this is SageMaker Distribution 2.x or 4.x
2. **DLC inference container** (where your model serves requests on the endpoint) — this is the `image_uri` you pass to `PyTorchModel`

The env var prefix is determined by #2 — the DLC container you deploy to the endpoint:

| DLC Image Tag | Serving Framework | Env Var Prefix |
|---------------|-------------------|----------------|
| `2.0.0-transformers4.28.1-gpu-py310-cu118-ubuntu20.04` | MMS | `MMS_*` |
| `2.6.0-transformers5.5.3-gpu-py312-cu124-ubuntu22.04` | TorchServe | `TS_*` |

The specific env vars:

| Setting | MMS (older DLC) | TorchServe (newer DLC) |
|---------|-----------------|------------------------|
| Max request size (bytes) | `MMS_MAX_REQUEST_SIZE` | `TS_MAX_REQUEST_SIZE` |
| Max response size (bytes) | `MMS_MAX_RESPONSE_SIZE` | `TS_MAX_RESPONSE_SIZE` |
| Response timeout (seconds) | `MMS_DEFAULT_RESPONSE_TIMEOUT` | `TS_DEFAULT_RESPONSE_TIMEOUT` |

All three are set to:
- Request/response size: `2000000000` (2 GB)
- Timeout: `900` (15 minutes)

**Why we pair them the way we do**: The 2.x notebook uses an older DLC (which uses MMS) because those package versions are compatible. The 4.x notebook uses a newer DLC (which uses TorchServe) because *those* package versions are compatible. The pairing is about version compatibility, not a hard dependency between Studio image and serving framework.

**Why this matters**: If you use the wrong prefix, the container **silently ignores** the env vars and applies defaults (~6 MB request size, 60s timeout). Your endpoint will reject audio files > 6 MB with no useful error message. No warning, no log, nothing.

**How to tell which serving framework a DLC uses**: Look at the image tag version number. HuggingFace PyTorch inference images with tag `2.0.0` use MMS. Tags `2.1.0` and later use TorchServe. There's no official documentation that makes this obvious — you figure it out by trial and error or reading the Dockerfile.

## Usability Enhancements (Applied to Both Notebooks)

Three quality-of-life fixes over the original blog post notebook:

1. **Auto S3 bucket**: Uses `sagemaker.Session().default_bucket()` instead of a hardcoded `[BUCKET NAME]` placeholder. Resolves to `sagemaker-{region}-{account_id}`.

2. **Auto region for DLC URI**: Uses `boto3.Session().region_name` to construct the ECR image URI. No more manually replacing `[REGION]` in a long string.

3. **Fixed `load_dataset` call**: The `datasets` library (both v2 and v3) now requires the config name as a positional argument: `load_dataset('MLCommons/peoples_speech', 'clean', split='train', streaming=True)`. The original notebook omitted `'clean'` and silently failed or errored.

## Deployment Patterns

Each notebook demonstrates three SageMaker deployment patterns:

1. **Real-Time Inference** — synchronous endpoint on `ml.g4dn.xlarge`, ~7 min deploy time
2. **Batch Transform** — S3-to-S3 batch processing, non-blocking (`wait=False`)
3. **Async Inference with Autoscaling** — queued requests, scales 0→3 instances based on backlog, scales back to 0 when idle

## Gotchas

- **Kernel restart required** after `%pip install` — the notebook has a markdown reminder cell for this
- **Endpoint deploy takes ~7 minutes** — don't panic, it's pulling the DLC image and loading the model
- **`ml.g4dn.xlarge` quota** — you may need to request a quota increase for GPU instances in your account
- **The DLC image must exist in your region** — most regions have it, but if you get a "repository not found" error, check the [AWS DLC Available Images](https://github.com/aws/deep-learning-containers/blob/master/available_images.md) list
- **Batch transform `max_payload=100`** — this is in MB. Audio files larger than 100 MB will be rejected
