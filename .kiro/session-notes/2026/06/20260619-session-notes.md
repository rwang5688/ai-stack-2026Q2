# Session Notes - June 19, 2026

## Session Overview
Analyzed and remediated container vulnerability findings from Amazon Inspector for the two ECS Fargate Streamlit thin-client services (Phase 2 and Phase 3).

## Key Accomplishments
- Reviewed container remediation findings for both `StudentServicesPhase2-stl-front` and `StudentServicesPhase3-stl-front`
- Identified root causes (stale OS packages in Debian base images)
- Updated both Dockerfiles to patch vulnerabilities
- Reformatted the raw findings document into proper markdown

## Analysis: Container Remediation Findings

### Summary of Findings

| Service | Priority | SLA Status | Vulnerable Packages | CVE Count |
|---------|----------|------------|---------------------|-----------|
| Phase 2 (`StudentServicesPhase2-stl-front`) | P2 (72) | **Out of SLA** | unbound, openssl, imagemagick, libgcrypt20, krb5 | 42 |
| Phase 3 (`StudentServicesPhase3-stl-front`) | P2 (70) | Within SLA (19 days) | openssl | 15 |

### Root Cause
- Neither Dockerfile ran `apt-get upgrade` during build
- Base images were pulled weeks ago; OS patches have since been published
- Phase 2 used `python:3.12` (full image) which includes unnecessary packages like imagemagick, unbound, krb5 — dramatically increasing attack surface

## Changes Made

### 1. Phase 2 Dockerfile (`workshop4/phase2/deploy-streamlit-app/docker_app/Dockerfile`)

**Before:**
```dockerfile
FROM --platform=linux/arm64 python:3.12
EXPOSE 8501
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
COPY . .
ENV BYPASS_TOOL_CONSENT=true
ENV OTEL_SDK_DISABLED=true
CMD streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

**After:**
```dockerfile
FROM --platform=linux/arm64 python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .

ENV BYPASS_TOOL_CONSENT=true
ENV OTEL_SDK_DISABLED=true

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Key changes:**
- Switched from `python:3.12` (full) → `python:3.13-slim` (eliminates imagemagick, unbound, krb5 entirely)
- Added `apt-get update && apt-get upgrade -y` to patch remaining OS packages (openssl, libgcrypt20)
- Added `rm -rf /var/lib/apt/lists/*` to clean apt cache (smaller image)
- Switched to exec-form CMD (proper signal handling)
- Added `--no-cache-dir` to pip (smaller image)

### 2. Phase 3 Dockerfile (`workshop4/phase3/deploy-streamlit-app/docker_app/Dockerfile`)

**Before:**
```dockerfile
FROM --platform=linux/arm64 python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**After:**
```dockerfile
FROM --platform=linux/arm64 python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Key changes:**
- Added `apt-get update && apt-get upgrade -y` to patch openssl (the only vulnerable package)
- Added `rm -rf /var/lib/apt/lists/*` to clean apt cache

### 3. Reformatted findings document
- `.kiro/references/workshop4-container-remediation-findings/container-remediation-findings.md` — converted from raw console paste to proper markdown tables

## Decisions Made
- Phase 2 upgraded to `python:3.13-slim` to match Phase 3 and eliminate unnecessary packages
- Both Dockerfiles now include `apt-get upgrade` as a standard security practice
- No application code changes needed — purely OS-level patching

## Next Steps
- [x] Upload changed files to code-server
- [x] Run `cdk deploy` from code-server for both Phase 2 and Phase 3 (both tested and confirmed working)
- [ ] Verify via Inspector that CVEs are resolved (~24 hours after new tasks are running)
- [ ] Consider adding a periodic rebuild schedule to prevent future SLA breaches
  - Option A: Schedule a monthly `cdk deploy` (force new image build) via a calendar reminder
  - Option B: Add a GitHub Actions / CodePipeline workflow that rebuilds and deploys on a cron schedule (e.g., weekly)
  - Option C: Use ECR image scanning + EventBridge to trigger redeployment when new CVEs are detected
  - Option D: Pin base image to a `python:3.13-slim-bookworm` tag and monitor Debian security tracker for updates
  - Recommendation: For non-prod workshop accounts, a monthly manual rebuild (Option A) is sufficient. For anything in compliance scope, Option B or C is more appropriate.
- [ ] Check other workspaces for potential SLA breaches
  - The following findings are escalated and significantly past SLA (SLA dates from August 2025):
    - `539307129890` (wangrob-aiml-02): `Streamlit-stl-front` — SLA 2025-08-16
    - `539307129890` (wangrob-aiml-02): `TravelPlanner-agent-ui` — SLA 2025-08-16
    - `499243079778` (wangrob-hcls-digipath-demos-01): `hcls-agents-react-ui-service` — SLA 2025-08-21
  - For each workspace, use this prompt in a new Kiro session:
    ```
    I have a container remediation finding for an ECS Fargate service in this workspace.
    The service name is [SERVICE_NAME] and it has OS-level CVEs that need patching.

    Please:
    1. Find the Dockerfile for this service
    2. Determine if the container is still needed (check if the ECS service is active)
    3. If still needed: add `apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*`
       early in the Dockerfile, consider switching to a -slim base image if not already,
       and help me redeploy
    4. If no longer needed: help me tear down the ECS service and related infrastructure
       to resolve the finding by decommissioning
    ```

## Resources
- Container remediation findings: `.kiro/references/workshop4-container-remediation-findings/container-remediation-findings.md`
- Phase 2 Dockerfile: `workshop4/phase2/deploy-streamlit-app/docker_app/Dockerfile`
- Phase 3 Dockerfile: `workshop4/phase3/deploy-streamlit-app/docker_app/Dockerfile`
