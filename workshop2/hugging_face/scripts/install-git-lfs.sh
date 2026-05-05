#!/bin/bash
# Install git-lfs on SageMaker JupyterLab
# Run once in your SageMaker terminal:
#   bash scripts/install-git-lfs.sh

sudo apt-get install -y git-lfs && git lfs install
