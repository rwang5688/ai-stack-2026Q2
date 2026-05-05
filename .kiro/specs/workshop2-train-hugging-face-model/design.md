# Design Document

## Introduction

This document describes the technical design of the Workshop 2 Hugging Face Model Training module. The workshop demonstrates fine-tuning distilgpt2 on Wikitext-2 using a SageMaker AI JupyterLab Space with GPU acceleration.

## Architecture Overview

The workshop follows a linear, notebook-driven architecture with supporting shell scripts for environment setup:

```
workshop2/hugging_face/
├── language_modeling.ipynb    # Main training notebook (CLM fine-tuning)
├── README.md                  # Documentation and runbook
├── .gitignore                 # Excludes model output directories
└── scripts/
    ├── install-git-lfs.sh     # Git LFS installation
    ├── hf-setup.sh            # Hugging Face authentication
    └── git-push.sh            # GitHub credential configuration
```

### Execution Flow

```
[Environment Setup]          [Notebook Execution]
       │                            │
  install-git-lfs.sh               │
       │                            │
  git-push.sh                      │
       │                            │
  hf-setup.sh                     │
       │                            │
       └────────────────────────────┤
                                    ▼
                          1. Install dependencies
                                    │
                          2. notebook_login()
                                    │
                          3. Load Wikitext-2
                                    │
                          4. Tokenize (4 processes)
                                    │
                          5. Group into 128-token blocks
                                    │
                          6. Load distilgpt2
                                    │
                          7. Configure TrainingArguments
                                    │
                          8. Train (3 epochs, ~13 min)
                                    │
                          9. Evaluate (perplexity ~37)
                                    │
                         10. Push to Hub
```

## Components

### 1. Setup Scripts (`scripts/`)

**Purpose**: Configure the SageMaker JupyterLab environment for the workshop.

| Script | Responsibility |
|--------|---------------|
| `install-git-lfs.sh` | Installs git-lfs via apt-get (required for HF model downloads) |
| `git-push.sh` | Clears stale credential helpers, sets GitHub remote URL with token |
| `hf-setup.sh` | Authenticates with Hugging Face CLI using access token |

**Design Decisions**:
- Scripts use placeholder tokens (`YOUR_TOKEN_HERE`) to prevent accidental credential commits
- `git-push.sh` validates it's running inside a git repo before proceeding
- `git-push.sh` aggressively clears all credential helpers (global, system, local) to avoid conflicts with SageMaker's default credential configuration
- Classic GitHub PATs are required because fine-grained tokens have a known bug where permissions revert

### 2. Training Notebook (`language_modeling.ipynb`)

**Purpose**: Demonstrates the complete CLM fine-tuning lifecycle.

#### Data Pipeline

```
Wikitext-2 (raw text)
    │
    ▼ tokenize_function() [batched, 4 processes]
Token IDs (variable length per sample)
    │
    ▼ group_texts() [batched, batch_size=1000, 4 processes]
Fixed-length blocks (128 tokens each, with labels = input_ids copy)
```

**Tokenization**: Uses `AutoTokenizer.from_pretrained("distilgpt2", use_fast=True)` — the fast Rust-based tokenizer for performance.

**Chunking Strategy**: Concatenates all tokenized texts, then splits into fixed 128-token blocks. This means blocks can span multiple original documents. Remainders less than 128 tokens are dropped.

#### Training Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | distilgpt2 (~82M params) | Small enough for workshop timing, large enough to demonstrate real fine-tuning |
| Block size | 128 | Fits in GPU memory, fast iteration for workshop |
| Learning rate | 2e-5 | Standard for fine-tuning pretrained transformers |
| Weight decay | 0.01 | Light regularization |
| Epochs | 3 | Sufficient to show convergence without overfitting |
| Batch size | 8 (default) | Fits ml.g6.xlarge VRAM |
| Eval strategy | per epoch | Shows loss progression across epochs |
| push_to_hub | True | Demonstrates full lifecycle including publishing |

#### Evaluation

Perplexity is computed as `exp(eval_loss)` after training completes. Expected value is ~37 on Wikitext-2 validation set.

### 3. Documentation (`README.md`)

**Purpose**: Self-contained runbook for workshop students.

**Structure**:
- Prerequisites (hardware, accounts, tokens)
- Part 1: Environment Setup (3 steps with scripts)
- Part 2: Notebook execution (what it does, key changes, expected metrics)
- Troubleshooting table

### 4. Git Ignore Configuration (`.gitignore`)

**Purpose**: Prevents model output directories from being committed.

Excludes:
- `distilgpt2-finetuned-wikitext2/` (CLM training output)
- `distilroberta-base-finetuned-wikitext2/` (MLM training output, if run)

## Infrastructure Requirements

| Resource | Specification |
|----------|--------------|
| Instance type | ml.g6.xlarge |
| GPU | NVIDIA L4, 24 GB VRAM |
| Service | SageMaker AI JupyterLab Space |
| Storage | Default EFS mount (`~/user-default-efs/`) |

## Key Design Decisions

1. **Only CLM, not MLM**: The notebook contains both CLM and MLM sections, but only CLM is executed. CLM (decoder-only, next-token prediction) mirrors modern LLM architectures (GPT-4, Claude, Gemini, Llama). MLM (encoder-only, bidirectional) is from the BERT era and not representative of current generative AI.

2. **Explicit pyarrow upgrade**: The original HuggingFace notebook doesn't include pyarrow in the install cell. On SageMaker, this causes Arrow serialization errors during `.map()` calls. Adding `pyarrow` to the pip install is the only meaningful change from the upstream notebook.

3. **Block size 128 vs model max**: The model supports 1024 tokens, but 128 is chosen for faster training in a workshop setting (~13 min vs potentially hours).

4. **Scripts over inline commands**: Environment setup is extracted into reusable shell scripts rather than notebook cells, keeping the notebook focused on the ML workflow and allowing setup to be done once in a terminal.

5. **Classic GitHub PAT**: Fine-grained tokens have a known issue where repository permissions snap back to "public read-only" after saving. Classic tokens work reliably for pushing from SageMaker.

## Correctness Properties

1. **Tokenization preserves content**: All text from the dataset is tokenized without loss (verified by decoding tokenized blocks back to text)
2. **Block size consistency**: Every training sample has exactly 128 tokens (verified by the chunking logic that drops remainders)
3. **Labels match inputs**: Labels are a copy of input_ids (the Trainer handles the left-shift internally for CLM)
4. **Perplexity calculation**: Perplexity = exp(eval_loss), providing a human-interpretable metric for language model quality
5. **Training convergence**: Validation loss decreases across epochs (3.64 → 3.62 → 3.61), indicating the model is learning without overfitting
6. **Credential safety**: Scripts use placeholder tokens and .gitignore excludes model output directories
