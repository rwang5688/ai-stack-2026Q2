# SageMaker JupyterLab Setup Scripts

These scripts handle one-time setup tasks on SageMaker JupyterLab where you don't have root/sudo access.

## Prerequisites

- SageMaker JupyterLab environment
- A GitHub account with a **classic** personal access token (PAT) with `repo` scope
- A Hugging Face account with an access token

### Why a classic GitHub token?

Fine-grained tokens (starting with `github_pat_`) have a known issue where repository permissions snap back to "public read-only" after saving. Classic tokens (starting with `ghp_`) work reliably.

To create a classic token:
1. Go to https://github.com/settings/tokens/new
2. Name it (e.g., `sagemaker-push`)
3. Check the **repo** scope
4. Generate and copy the token

---

## Step 1: Install git-lfs

Hugging Face model downloads require git-lfs. SageMaker doesn't have it pre-installed.

```bash
bash scripts/install-git-lfs.sh
```

You only need to do this once per SageMaker environment. Works in both terminal and notebooks — no PATH hacks needed.

---

## Step 2: Configure GitHub push access

This clears any stale credential helpers and sets your remote URL with your token so the JupyterLab Git UI can push.

1. Edit `scripts/git-push.sh` and replace `YOUR_TOKEN_HERE` with your classic GitHub token
2. Run from inside your repo directory:

```bash
cd ~/user-default-efs/ai-stack-2026Q2
bash scripts/git-push.sh
```

3. Push using the JupyterLab Git UI

**Do not check in the script with a real token.** Reset it to `YOUR_TOKEN_HERE` before committing.

---

## Step 3: Authenticate with Hugging Face

Required before running notebooks that download models from Hugging Face Hub.

1. Edit `scripts/hf-setup.sh` and replace `YOUR_TOKEN_HERE` with your Hugging Face token
2. Run:

```bash
bash scripts/hf-setup.sh
```

This persists across kernel restarts. You only need to re-run it if the token expires or EFS storage is wiped.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `git: 'lfs' is not a git command` | Re-run `bash scripts/install-git-lfs.sh` |
| `Permission denied` on git push (403) | Token doesn't have `repo` scope, or you're using a fine-grained token — switch to classic |
| `Invalid username or token` on git push | Token is wrong or expired — regenerate it |
| HF login warning about credential helper | Run `git config --global credential.helper store` first |
