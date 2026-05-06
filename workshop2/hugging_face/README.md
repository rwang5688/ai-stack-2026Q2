# Workshop 2: Fine-Tune a Language Model on SageMaker AI

Fine-tune a pretrained [distilgpt2](https://huggingface.co/distilgpt2) model on the Wikitext-2 dataset using HuggingFace Transformers, running on a SageMaker AI JupyterLab space.

## Hugging Face Transformers Notebooks

- Landing Page: https://huggingface.co/docs/transformers/notebooks
- GitHub: https://github.com/huggingface/notebooks/blob/main/examples/language_modeling.ipynb

## Prerequisites

- A SageMaker AI JupyterLab space (ml.g6.xlarge recommended — NVIDIA L4, 24 GB VRAM)
- A GitHub account with a **classic** personal access token (PAT) with `repo` scope
- A Hugging Face account with an access token

### Why a classic GitHub token?

Fine-grained tokens (starting with `github_pat_`) have a known issue where repository permissions snap back to "public read-only" after saving. Classic tokens (starting with `ghp_`) work reliably.

To create one: [github.com/settings/tokens/new](https://github.com/settings/tokens/new) → name it, check **repo** scope, generate and copy.

## Part 1: Environment Setup

Run these scripts from a terminal in your SageMaker JupyterLab space.

### Step 1: Install git-lfs

HuggingFace model downloads require git-lfs. SageMaker doesn't have it pre-installed.

```bash
bash install-git-lfs.sh
```

You only need to do this once per SageMaker environment.

### Step 2: Configure GitHub push access

This clears stale credential helpers and sets your remote URL with your token so the JupyterLab Git UI can push.

1. Edit `git-push.sh` and replace `YOUR_TOKEN_HERE` with your classic GitHub token
2. Run from inside your repo directory:

```bash
cd ~/user-default-efs/ai-stack-2026Q2
bash workshop2/hugging_face/git-push.sh
```

**Do not check in the script with a real token.** Reset it to `YOUR_TOKEN_HERE` before committing.

### Step 3: Authenticate with Hugging Face

Required before running the notebook (model downloads and push-to-hub).

1. Edit `hf-setup.sh` and replace `YOUR_TOKEN_HERE` with your Hugging Face token
2. Run:

```bash
bash hf-setup.sh
```

This persists across kernel restarts.

## Part 2: Run the Hugging Face Language Modeling Notebook

Open `language_modeling.ipynb` in JupyterLab and run through the cells in order.

### What the notebook does

1. **Install dependencies** — upgrades `datasets`, `pyarrow`, and `transformers`
2. **Authenticate with Hugging Face** — uses `notebook_login()` for push-to-hub access
3. **Prepare the dataset** — loads Wikitext-2, explores sample data
4. **Causal Language Modeling (CLM)** — tokenizes, chunks, fine-tunes distilgpt2, evaluates perplexity, and pushes the model to HuggingFace Hub

### Key change from the original notebook

The only meaningful changes to make things work on SageMaker are:

1. **Explicit pyarrow upgrade** in the first code cell — avoids Arrow serialization errors during `.map()` calls:
   ```python
   !pip install -U datasets pyarrow
   !pip install -U transformers
   ```

2. **Pass tokenizer to Trainer** — ensures `push_to_hub()` uploads the tokenizer files alongside the model weights. Without this, the deployed inference endpoint can't load the tokenizer:
   ```python
   trainer = Trainer(
       model=model,
       args=training_args,
       train_dataset=lm_datasets["train"],
       eval_dataset=lm_datasets["validation"],
       tokenizer=tokenizer,  # Required for push_to_hub to include tokenizer files
   )
   ```

### We only run the CLM section

The notebook contains two sections: Causal Language Modeling (CLM) and Masked Language Modeling (MLM). **We only run the CLM section** (cells up through `push_to_hub`).

Why? Modern LLMs like GPT-4, Claude, Gemini, and Llama all use the decoder-only, next-token prediction architecture — the same fundamental approach as distilgpt2, just massively scaled up. The CLM section demonstrates the full fine-tuning lifecycle that mirrors how real-world LLMs are trained:

1. Load a pretrained decoder model
2. Tokenize and chunk your dataset
3. Fine-tune with next-token prediction
4. Evaluate perplexity
5. Publish to HuggingFace Hub

The MLM section uses distilroberta-base (an encoder-only, bidirectional model). That architecture is from the BERT era and is used for understanding tasks like classification and NER — not text generation. It's still useful, but not representative of how modern LLMs work.

### What to expect

| Metric | Value |
|---|---|
| Instance | ml.g6.xlarge (NVIDIA L4, 24 GB VRAM) |
| Training time | ~13-14 minutes (3 epochs, batch size 8) |
| Training loss | ~3.57 |
| Validation loss | ~3.61 |
| Perplexity | ~37 |

### After training

Your fine-tuned model will be published to HuggingFace Hub at `your-username/distilgpt2-finetuned-wikitext2`. Anyone can load it with:

```python
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("your-username/distilgpt2-finetuned-wikitext2")
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `git: 'lfs' is not a git command` | Re-run `bash scripts/install-git-lfs.sh` |
| `Permission denied` on git push (403) | Token doesn't have `repo` scope, or you're using a fine-grained token — switch to classic |
| `Invalid username or token` on git push | Token is wrong or expired — regenerate it |
| HF login warning about credential helper | Run `git config --global credential.helper store` first |
| Arrow/pyarrow errors during `.map()` | Make sure you ran `!pip install -U datasets pyarrow` |
