#!/bin/bash
# Authenticate with Hugging Face on SageMaker JupyterLab
# Usage: Edit YOUR_TOKEN below, then run:
#   bash hf-setup.sh

HF_TOKEN="YOUR_TOKEN_HERE"

git config --global credential.helper store
huggingface-cli login --token "$HF_TOKEN"
echo "Hugging Face authenticated."
