---
inclusion: always
---

# Git Workflow Rules

## CRITICAL: Cannot Push from Windows PC

**This workspace CANNOT push to the remote Git repository from the Windows PC.**

Git push must be done from the code-server (Linux). The workflow is:
1. Make changes on Windows PC
2. Zip the changed files
3. Upload to code-server
4. Commit and push from code-server

**NEVER attempt `git push` from this machine. NEVER attempt `git commit` expecting to push later from here. Always remind the user they need to upload to code-server for commit/push.**

## Commit Workflow
- Do NOT run `git add` or `git commit` on the Windows PC
- Do NOT suggest pushing from here
- When the user says "checkpoint" or "commit":
  1. Run `git status --short` IMMEDIATELY
  2. Extract ALL unique parent directories (including leaf subdirectories — do NOT collapse)
  3. Present them as a code block (alphabetical order)
  4. Do NOT guess, do NOT explain, do NOT list files from memory — USE GIT STATUS
  5. Do it in ONE response, no back-and-forth
  6. Include leaf subdirectories separately — code-server requires uploading files INTO each directory (cannot upload whole directory trees)

## Deployment Workflow

| Command | Where to Run | Why |
|---------|-------------|-----|
| `agentcore deploy -y` | **Windows PC** (here) | No Docker needed, just CodeZip + CDK |
| `cdk deploy` (Streamlit thin client) | **Code-server** (Linux) | Requires Docker for container build |
| `git commit/push` | **Code-server** (Linux) | Git credentials only configured there |

**Run `agentcore deploy` HERE first, then zip/upload/commit/push to code-server.**

