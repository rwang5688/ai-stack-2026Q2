# Workshop 2: Fine-Tune a Language Model

Fine-tune a pretrained language model (distilgpt2) on the Wikitext-2 dataset using HuggingFace Transformers, running on a SageMaker AI JupyterLab space with GPU acceleration.

## Topics Covered

- Causal language modeling (next-token prediction)
- HuggingFace Transformers training pipeline
- SageMaker AI JupyterLab Spaces (ml.g6.xlarge / NVIDIA L4)
- Dataset preparation and tokenization
- Model evaluation (perplexity) and publishing to HuggingFace Hub
- SageMaker JumpStart dataset format transformation

## Contents

| Directory | Description |
|-----------|-------------|
| [hugging_face/](hugging_face/) | Fine-tuning notebook, environment setup scripts, and detailed walkthrough |
| [sagemaker_jumpstart/](sagemaker_jumpstart/) | Training datasets and format transformation scripts for SageMaker JumpStart fine-tuning |

## Outcome

A fine-tuned distilgpt2 model published to HuggingFace Hub, ready for deployment in Workshop 3.
