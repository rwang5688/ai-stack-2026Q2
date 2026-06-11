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

Both notebooks use the **same** DLC inference container:

```
huggingface-pytorch-inference:2.0.0-transformers4.28.1-gpu-py310-cu118-ubuntu20.04
```

ECR registry: `763104351884.dkr.ecr.{region}.amazonaws.com/`

**Why not use the newer DLC (2.6.0, Python 3.12)?** Because `openai-whisper` uses a legacy `setup.py` that imports `pkg_resources`, which is broken on Python 3.12. The package fails to build inside the container, and the endpoint deploy fails after 20+ minutes with no useful error. The old DLC (Python 3.10) installs whisper cleanly in seconds. We wasted an entire evening learning this the hard way.

The notebook kernel (SageMaker Distribution 4.x) and the endpoint container are **completely independent**. You can run a modern Python 3.12 kernel and still deploy an endpoint using a Python 3.10 container. They don't talk to each other.

### Inference Code Directory

| Variant | `source_dir` |
|---------|-------------|
| 2.x | `code_sagemaker_2` |
| 4.x | `code_sagemaker_4` |

Both directories contain identical `inference.py` logic (model_fn + transform_fn). They're split so that `requirements.txt` inside each container can diverge if needed.

### Model Serving Environment Variables (MMS)

Both notebooks use the same DLC (2.0.0) which uses **Multi-Model Server (MMS)**. The environment variables are:

| Setting | Environment Variable | Value |
|---------|---------------------|-------|
| Max request size | `MMS_MAX_REQUEST_SIZE` | `2000000000` (2 GB) |
| Max response size | `MMS_MAX_RESPONSE_SIZE` | `2000000000` (2 GB) |
| Response timeout | `MMS_DEFAULT_RESPONSE_TIMEOUT` | `900` (15 minutes) |

**Why this matters**: If these aren't set, the container applies defaults (~6 MB request size, 60s timeout). Your endpoint will reject audio files > 6 MB with no useful error message. No warning, no log, nothing.

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
- **First run of cell 1 takes 3-5 minutes** — whisper builds from source on Python 3.12. Subsequent runs (after kernel restart) are instant because the package is cached on disk. **Pre-run this before the workshop.**
- **Endpoint deploy takes ~7 minutes** — don't panic, it's pulling the DLC image and loading the model
- **`ml.g6.xlarge` quota** — you need quota for `ml.g6.xlarge for endpoint usage` (at least 4). Request in Service Quotas console.
- **The DLC image must exist in your region** — most regions have it, but if you get a "repository not found" error, check the [AWS DLC Available Images](https://github.com/aws/deep-learning-containers/blob/master/available_images.md) list
- **Batch transform `max_payload=100`** — this is in MB. Audio files larger than 100 MB will be rejected

## Pre-Built Whisper Wheels (CRITICAL — READ THIS)

### The Problem

`openai-whisper` on PyPI is distributed ONLY as a source tarball (`.tar.gz`), not a pre-built wheel. Its `setup.py` imports `pkg_resources`, which has been removed from modern `setuptools` (v71+). This means:

- **Inside the DLC container**: `pip install openai-whisper` FAILS because pip's build isolation creates a temp env with the latest setuptools (which doesn't have `pkg_resources`). The endpoint deploy fails after 20+ minutes with `ModuleNotFoundError: No module named 'pkg_resources'`.
- **Inside the notebook kernel** (Python 3.12, Distribution 4.x): Same problem. We work around it with `setuptools<71` + the install takes 3-5 minutes (source compile).
- **This affects ALL versions of openai-whisper on PyPI** (20230918, 20231117, etc.) — they all use the same broken `setup.py`.

### The Solution

We pre-build the wheel locally and check it into the repo. The container installs from the local `.whl` file — no build, no setuptools, no `pkg_resources`, instant install.

### How the Wheels Were Built

Run from a SageMaker Studio terminal (or any environment with setuptools and Python 3.x):

```bash
# Build the 20231117 wheel (for code_sagemaker_4)
cd /tmp
pip wheel openai-whisper==20231117 --no-build-isolation --no-deps -w .
cp openai_whisper-20231117-py3-none-any.whl ~/your-repo/workshop3/openai_whisper/code_sagemaker_4/

# Build the 20230918 wheel (for code_sagemaker_2)
pip wheel openai-whisper==20230918 --no-build-isolation --no-deps -w /tmp
cp /tmp/openai_whisper-20230918-py3-none-any.whl ~/your-repo/workshop3/openai_whisper/code_sagemaker_2/
```

Key flags:
- `--no-build-isolation`: Uses the system's setuptools (which has `pkg_resources`) instead of downloading a new broken one
- `--no-deps`: Don't download dependencies — we only want the whisper wheel itself
- `-w .`: Output the wheel to current directory

The resulting wheels are `py3-none-any` (pure Python, no C extensions, works on any Python 3.x, any OS).

### How the Wheels Are Used

In `code_sagemaker_4/requirements.txt`:
```
ffmpeg-python
/opt/ml/model/code/openai_whisper-20231117-py3-none-any.whl
```

When SageMaker starts the container, it runs `pip install -r /opt/ml/model/code/requirements.txt`. The `.whl` file is already in `/opt/ml/model/code/` (bundled with the source tarball via `source_dir`). Pip installs it instantly — no network, no build, no setuptools.

### If You Ever Need to Rebuild

If you upgrade to a newer whisper version, repeat the `pip wheel` command with the new version number. The key requirement is having a working `setuptools<71` in the environment where you run `pip wheel`. The SageMaker Distribution 4.x Studio terminal works because we install `setuptools<71` in cell 1 of the notebook.

### Why This Happened

AWS silently patches DLC images even when the tag stays the same (security updates). The `huggingface-pytorch-inference:2.0.0-transformers4.28.1-gpu-py310-cu118-ubuntu20.04` image that worked 2 years ago now has a newer setuptools that removed `pkg_resources`. The image tag is identical but the contents changed. There's no way to pin to the old image contents.
