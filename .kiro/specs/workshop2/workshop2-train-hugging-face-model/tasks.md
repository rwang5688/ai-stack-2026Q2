# Implementation Tasks

## Overview

This is a catch-up spec documenting the existing implementation of Workshop 2: Hugging Face Model Training. All tasks reflect work that has already been completed.

## Tasks

- [x] 1. Create environment setup scripts
  - [x] 1.1 Create `scripts/install-git-lfs.sh` that installs git-lfs via apt-get and runs `git lfs install`
  - [x] 1.2 Create `scripts/git-push.sh` that clears credential helpers, validates git repo context, and sets remote URL with GitHub token
  - [x] 1.3 Create `scripts/hf-setup.sh` that authenticates with Hugging Face CLI using a provided token
  - [x] 1.4 Use placeholder tokens (`YOUR_TOKEN_HERE`) in all scripts to prevent accidental credential commits

- [x] 2. Create the training notebook
  - [x] 2.1 Add dependency installation cell with explicit `pyarrow` upgrade to avoid Arrow serialization errors
  - [x] 2.2 Add Hugging Face authentication cell using `notebook_login()`
  - [x] 2.3 Add dataset loading cell for Wikitext-2 (`wikitext-2-raw-v1`)
  - [x] 2.4 Add data exploration cells showing random samples from the dataset
  - [x] 2.5 Implement tokenization with `AutoTokenizer` (distilgpt2, fast tokenizer, batched, 4 processes)
  - [x] 2.6 Implement `group_texts()` function to concatenate and chunk into 128-token blocks with labels
  - [x] 2.7 Load pretrained distilgpt2 model with `AutoModelForCausalLM.from_pretrained`
  - [x] 2.8 Configure `TrainingArguments` (lr=2e-5, weight_decay=0.01, eval per epoch, push_to_hub=True)
  - [x] 2.9 Create `Trainer` instance with model, args, train dataset, and validation dataset
  - [x] 2.10 Execute training (3 epochs, ~13-14 minutes on ml.g6.xlarge)
  - [x] 2.11 Add evaluation cell computing perplexity as `exp(eval_loss)`
  - [x] 2.12 Add `push_to_hub()` cell to publish fine-tuned model to Hugging Face Hub

- [x] 3. Configure repository hygiene
  - [x] 3.1 Create `.gitignore` excluding `distilgpt2-finetuned-wikitext2/` and `distilroberta-base-finetuned-wikitext2/` output directories

- [x] 4. Create comprehensive documentation
  - [x] 4.1 Document prerequisites (SageMaker AI JupyterLab space, GitHub classic PAT, HF token)
  - [x] 4.2 Explain why classic GitHub tokens are required (fine-grained token permission bug)
  - [x] 4.3 Write Part 1: Environment Setup with step-by-step instructions for all three scripts
  - [x] 4.4 Write Part 2: Notebook execution guide explaining what each section does
  - [x] 4.5 Document the key change from the original notebook (pyarrow upgrade)
  - [x] 4.6 Explain why only CLM is run (mirrors modern LLM architecture) vs MLM (BERT-era)
  - [x] 4.7 Add expected metrics table (instance, training time, loss values, perplexity)
  - [x] 4.8 Add troubleshooting section with common errors and fixes
  - [x] 4.9 Document post-training usage (how others can load the published model)
