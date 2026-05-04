#!/bin/bash
# Configure GitHub credentials for SageMaker JupyterLab
# Usage: Edit YOUR_TOKEN below, then run from inside your repo:
#   bash scripts/git-push.sh
# NOTE: Must be run from inside the git repo directory.

GITHUB_USER="rwang5688"
GITHUB_TOKEN="YOUR_TOKEN_HERE"
GITHUB_REPO="rwang5688/ai-stack-2026Q2"

# Verify we're in a git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo "ERROR: Not inside a git repository. cd into your repo first."
  exit 1
fi

git config --global --unset-all credential.helper 2>/dev/null
git config --system --unset-all credential.helper 2>/dev/null
git config --local --unset-all credential.helper 2>/dev/null
rm -f ~/.git-credentials
git config --global credential.helper store

git remote set-url origin "https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git"
echo "Remote URL updated. You can now push from the JupyterLab Git UI."
