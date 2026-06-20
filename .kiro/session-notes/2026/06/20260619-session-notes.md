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
- [ ] Upload changed files to code-server
- [ ] Run `cdk deploy` from code-server for both Phase 2 and Phase 3
- [ ] Verify via Inspector that CVEs are resolved (~24 hours after new tasks are running)
- [ ] Consider adding a periodic rebuild schedule to prevent future SLA breaches

## Resources
- Container remediation findings: `.kiro/references/workshop4-container-remediation-findings/container-remediation-findings.md`
- Phase 2 Dockerfile: `workshop4/phase2/deploy-streamlit-app/docker_app/Dockerfile`
- Phase 3 Dockerfile: `workshop4/phase3/deploy-streamlit-app/docker_app/Dockerfile`
