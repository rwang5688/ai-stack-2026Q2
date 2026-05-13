# Session Notes - May 13, 2026

## Session Overview
Resuming Phase 3 AgentCore microservices work. Verified refactored directory structure, confirmed Phase 1 code works on Windows PC, continuing with AgentCore deployment.

## Directory Structure Refactoring (done between sessions)

### Rationale
Restructured all phases to match the reference implementation pattern and ensure self-contained directories:

### Phase 1 Changes
- Agent code duplicated into `streamlit_app/` as sibling directories
- `streamlit_app/` is now self-contained — imports from sibling packages within its own directory
- `app.py` adds its own directory to `sys.path` for clean imports
- Original agent directories at phase1 root kept for reference/testing

### Phase 2 Changes
- Restructured to `deploy-streamlit-app/` (matching reference pattern)
- CDK + Docker app lives under single directory

### Phase 3 Structure
```
workshop4/phase3/
├── cloudformation/              # Identity stack (deployed)
├── deploy-streamlit-app/        # ECS Fargate thin client (placeholder)
├── streamlit_app/               # Local dev thin client (placeholder)
├── studentservices/             # AgentCore CLI project boundary
│   ├── agentcore/               # Config only (agentcore.json, aws-targets.json)
│   ├── course_registration/     # Specialist runtime
│   ├── course_review/           # Specialist runtime
│   ├── loan_application/        # Specialist runtime
│   ├── math_teaching/           # Specialist runtime
│   ├── policies/                # Cedar policy files
│   └── student_services/        # Orchestrator runtime
├── .gitignore
├── PREREQUISITES.md
└── README.md
```

Key: `studentservices/` is the AgentCore project root — `agentcore deploy` runs from here. Agent code directories are siblings of `agentcore/` (not inside it). `codeLocation` paths in agentcore.json resolve relative to this root.

## Verification Results
- Phase 1 orchestrator creates successfully with 4 tools on Windows PC
- All imports resolve (strands, boto3, streamlit)
- Config falls back to defaults when AWS credentials not set (expected)
- Python 3.13.12, Node 24.15.0, AgentCore CLI 0.13.1, CDK 2.1121.0 confirmed

## Current State of agentcore.json
- Validates successfully (`agentcore validate` → Valid)
- 5 runtimes declared (orchestrator + 4 specialists)
- 1 memory (StudentServicesMemory with 3 strategies)
- 5 OAuth credentials
- Gateway and policy engine arrays empty (to be added after first deploy provides runtime URLs)

## AgentCore Project Scaffolding (Lesson Learned)

**Problem**: `agentcore create` defaults to initializing a new Git repo. When working inside an existing repo, this creates a nested `.git` which is wrong. Also, `agentcore deploy` requires the `agentcore/cdk/` directory — you can't just hand-create `agentcore.json`.

**Solution**: Use `--skip-git --skip-python-setup --skip-install` flags, then copy the scaffold into your repo:

```bash
# Scaffold to temp (or directly with --output-dir)
agentcore create --name studentservices --no-agent --skip-git --skip-python-setup --skip-install --output-dir <parent>

# Install CDK deps
cd <parent>/studentservices/agentcore/cdk && npm install

# Add your agent code as siblings of agentcore/
# Edit agentcore.json, validate, deploy
```

**Key gotcha**: If the target directory already exists (even empty), `agentcore create` refuses. You must delete it first. File locks from IDEs (Kiro, VS Code) can prevent deletion — close the IDE first if needed.

Documented in `workshop4/phase3/PREREQUISITES.md` for future reference.

## Next Steps
- [ ] Zip and upload to code-server for commit/push
- [ ] Run `agentcore deploy -y` from `studentservices/` (Deploy 1: runtimes only)
- [ ] Get runtime URLs from `agentcore status`
- [ ] Add gateway targets with actual endpoint URLs (Deploy 2)
- [ ] Retrieve Cognito client secret for orchestrator gateway auth
- [ ] Update orchestrator agent.py with real gateway URL + secret
- [ ] Add runtime identifier to each specialist response for demo visibility
- [ ] Test individual runtimes in AgentCore Playground
