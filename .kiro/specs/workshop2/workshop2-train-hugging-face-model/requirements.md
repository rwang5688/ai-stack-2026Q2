# Requirements Document

## Introduction

This workshop module demonstrates fine-tuning a Hugging Face Transformers model (distilgpt2) on the Wikitext-2 dataset using a SageMaker AI JupyterLab Space as a managed GPU instance. The educational purpose is to show students how SageMaker AI provides accessible P-type or G-type EC2 instances with a streamlined service quota increase process, and to demonstrate the full Causal Language Modeling (CLM) fine-tuning lifecycle that mirrors how modern LLMs (GPT-4, Claude, Gemini, Llama) are trained.

## Glossary

- **Notebook**: The Jupyter notebook (`language_modeling.ipynb`) that contains the fine-tuning workflow
- **SageMaker_Space**: An Amazon SageMaker AI JupyterLab space configured with a GPU instance (ml.g6.xlarge)
- **CLM**: Causal Language Modeling — next-token prediction training objective used by decoder-only models
- **Trainer**: The HuggingFace Transformers `Trainer` class that manages the training loop
- **Tokenizer**: The HuggingFace `AutoTokenizer` that converts text to token IDs for the model
- **Hub**: The Hugging Face Hub where models are published and shared
- **Setup_Scripts**: Shell scripts that configure the SageMaker environment (git-lfs, GitHub credentials, HF authentication)
- **README**: The documentation file that provides prerequisites, setup instructions, and a runbook

## Requirements

### Requirement 1: Environment Setup Scripts

**User Story:** As a workshop student, I want automated setup scripts for the SageMaker JupyterLab environment, so that I can quickly configure git-lfs, GitHub push access, and Hugging Face authentication without manual steps.

#### Acceptance Criteria

1. WHEN a student runs the install-git-lfs script, THE Setup_Scripts SHALL install git-lfs via apt-get and initialize it with `git lfs install`
2. WHEN a student runs the git-push script from inside a git repository, THE Setup_Scripts SHALL clear all existing credential helpers, configure credential store, and set the remote URL with the provided GitHub token
3. IF the git-push script is run outside a git repository, THEN THE Setup_Scripts SHALL display an error message and exit with a non-zero status code
4. WHEN a student runs the hf-setup script, THE Setup_Scripts SHALL authenticate with Hugging Face CLI using the provided token and confirm successful authentication
5. THE Setup_Scripts SHALL include placeholder tokens (`YOUR_TOKEN_HERE`) to prevent accidental credential commits

### Requirement 2: Dependency Installation

**User Story:** As a workshop student, I want the notebook to install and upgrade required dependencies, so that I can avoid Arrow serialization errors and version incompatibilities on SageMaker.

#### Acceptance Criteria

1. WHEN the first notebook cell is executed, THE Notebook SHALL upgrade the `datasets` and `pyarrow` packages to their latest versions
2. WHEN the first notebook cell is executed, THE Notebook SHALL upgrade the `transformers` package to its latest version
3. WHEN dependencies are installed, THE Notebook SHALL resolve the Arrow serialization error that occurs during dataset `.map()` calls without the pyarrow upgrade

### Requirement 3: Hugging Face Authentication

**User Story:** As a workshop student, I want to authenticate with Hugging Face from within the notebook, so that I can download models and push fine-tuned results to the Hub.

#### Acceptance Criteria

1. WHEN the authentication cell is executed, THE Notebook SHALL invoke `notebook_login()` to authenticate the user with Hugging Face
2. WHEN authentication succeeds, THE Notebook SHALL enable model downloads from the Hub and push-to-hub functionality for the training session

### Requirement 4: Dataset Preparation

**User Story:** As a workshop student, I want the notebook to load and preprocess the Wikitext-2 dataset, so that I can use it for fine-tuning the language model.

#### Acceptance Criteria

1. WHEN the dataset loading cell is executed, THE Notebook SHALL load the `wikitext-2-raw-v1` dataset from the Hugging Face datasets library
2. WHEN the tokenization step is executed, THE Tokenizer SHALL tokenize all text samples using the distilgpt2 tokenizer with `batched=True` and 4 parallel processes
3. WHEN the grouping step is executed, THE Notebook SHALL concatenate all tokenized texts and split them into chunks of 128 tokens (block_size)
4. WHEN text is grouped into blocks, THE Notebook SHALL create labels by copying the input_ids (the Trainer handles left-shifting internally)
5. WHEN the remainder of concatenated tokens is less than block_size, THE Notebook SHALL drop the remainder rather than pad

### Requirement 5: Model Fine-Tuning with CLM

**User Story:** As a workshop student, I want to fine-tune distilgpt2 using Causal Language Modeling, so that I can understand the same training approach used by modern LLMs.

#### Acceptance Criteria

1. WHEN the model loading cell is executed, THE Notebook SHALL load the pretrained `distilgpt2` model using `AutoModelForCausalLM.from_pretrained`
2. WHEN training arguments are configured, THE Trainer SHALL use a learning rate of 2e-5, weight decay of 0.01, evaluation at each epoch, and push_to_hub enabled
3. WHEN training is initiated, THE Trainer SHALL fine-tune the model for 3 epochs on the training split of the prepared dataset
4. WHEN training completes on an ml.g6.xlarge instance, THE Trainer SHALL complete within approximately 13-14 minutes
5. WHEN training completes, THE Trainer SHALL achieve a training loss of approximately 3.57 and a validation loss of approximately 3.61

### Requirement 6: Model Evaluation

**User Story:** As a workshop student, I want to evaluate the fine-tuned model's perplexity, so that I can understand how well the model learned the language patterns.

#### Acceptance Criteria

1. WHEN evaluation is executed after training, THE Trainer SHALL compute the evaluation loss on the validation split
2. WHEN evaluation loss is computed, THE Notebook SHALL calculate and display perplexity as `exp(eval_loss)`
3. WHEN evaluated on Wikitext-2 validation set, THE Notebook SHALL achieve a perplexity of approximately 37

### Requirement 7: Model Publishing

**User Story:** As a workshop student, I want to push the fine-tuned model to the Hugging Face Hub, so that I can share it and demonstrate the end-to-end lifecycle.

#### Acceptance Criteria

1. WHEN `push_to_hub()` is called after training, THE Trainer SHALL upload the fine-tuned model to the Hub under the user's namespace
2. WHEN the model is published, THE Hub SHALL make it loadable via `AutoModelForCausalLM.from_pretrained("username/distilgpt2-finetuned-wikitext2")`

### Requirement 8: Workshop Documentation

**User Story:** As a workshop student, I want comprehensive documentation covering prerequisites, setup steps, and expected outcomes, so that I can follow the workshop independently.

#### Acceptance Criteria

1. THE README SHALL document all prerequisites including SageMaker AI JupyterLab space requirements, GitHub classic PAT requirements, and Hugging Face token requirements
2. THE README SHALL explain why classic GitHub tokens are required instead of fine-grained tokens
3. THE README SHALL provide step-by-step setup instructions for git-lfs installation, GitHub push configuration, and Hugging Face authentication
4. THE README SHALL explain why only the CLM section is run (mirrors modern LLM architecture) and not the MLM section
5. THE README SHALL include a metrics table with expected training time, loss values, and perplexity
6. THE README SHALL include a troubleshooting section covering common errors and their fixes
7. THE README SHALL document the key change from the original notebook (explicit pyarrow upgrade)
