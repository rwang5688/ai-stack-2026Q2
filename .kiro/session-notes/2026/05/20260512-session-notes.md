# Session Notes - May 12, 2026

## Session Overview

Major project restructuring session. The workshop4 phases (1, 2, 3) all had incorrect directory structures that didn't match the reference implementation. The core mistake: agent code was scattered at the project root instead of being organized inside the application package.

## Key Issue

The reference implementation (`travelplanner`) shows:
- `agentcore/` contains ONLY config files (agentcore.json, aws-targets.json, cdk/)
- Application code lives at the project root in named directories
- For Phase 1 (monolithic Streamlit app), all agent code belongs INSIDE `streamlit_app/` as a self-contained package

What we had wrong:
- Phase 1: Agent directories (`course_review_agent/`, etc.) and `shared/` at the phase1 root, separate from `streamlit_app/`
- Phase 2: Same structural error
- Phase 3: Agent code nested inside `agentcore/` directory (should be at project root, with `agentcore/` containing only config)

## Phase 1 Fix (Completed)

### Structure Change
All agent code and shared modules moved INTO `streamlit_app/`:
```
workshop4/phase1/
├── streamlit_app/              # Self-contained application
│   ├── app.py
│   ├── config.py
│   ├── shared/
│   ├── student_services_agent/
│   ├── course_review_agent/
│   ├── course_registration_agent/
│   ├── loan_application_agent/
│   └── math_teaching_agent/
├── cloudformation/
├── data/
├── scripts/
└── tests/
```

### Import Fixes
All `sys.path` hacks and import statements updated:
- `from streamlit_app.config import ...` → `from config import ...` (agents are now inside streamlit_app)
- Path inserts point to `streamlit_app/` directory for sibling imports

### Files Updated
- `streamlit_app/app.py` — fixed imports
- `streamlit_app/student_services_agent/agent.py` — fixed imports
- `streamlit_app/course_review_agent/agent.py` — fixed imports
- `streamlit_app/course_registration_agent/agent.py` — fixed imports
- `streamlit_app/loan_application_agent/agent.py` — fixed imports
- `streamlit_app/math_teaching_agent/agent.py` — fixed imports
- `workshop4/phase1/README.md` — updated directory structure section
- `.kiro/specs/workshop4/workshop4-phase1-monolithic-agents/design.md` — updated directory structure

## Phase 2 Fix (Completed)

### Structure Change
All agent code and shared modules moved INTO `docker_app/` (the container boundary):
```
workshop4/phase2/
├── deploy-streamlit-app/           # CDK project
│   ├── app.py                      # CDK entry point
│   ├── cdk.json
│   ├── cdk/
│   │   └── cdk_stack.py
│   └── docker_app/                 # Self-contained containerized app
│       ├── Dockerfile
│       ├── app.py                  # Streamlit entry point
│       ├── config.py
│       ├── config_file.py
│       ├── shared/
│       ├── student_services_agent/
│       ├── course_review_agent/
│       ├── course_registration_agent/
│       ├── loan_application_agent/
│       ├── math_teaching_agent/
│       └── utils/                  # Cognito auth
├── deploy.sh
├── force-deploy.sh
├── requirements.txt
└── README.md
```

### Import Fixes
- All `from streamlit_app.config import ...` → `from config import ...`
- Path inserts point to `docker_app/` directory for sibling imports
- Dockerfile CMD: `streamlit run app.py` (not `streamlit_app/app.py`)
- Deploy scripts: added `cd deploy-streamlit-app` since cdk.json lives there

### Files Updated
- `docker_app/app.py` — fixed imports
- `docker_app/course_review_agent/agent.py` — fixed imports
- `docker_app/course_registration_agent/agent.py` — fixed imports
- `docker_app/loan_application_agent/agent.py` — fixed imports
- `docker_app/math_teaching_agent/agent.py` — fixed imports
- `docker_app/Dockerfile` — fixed CMD path
- `docker_app/requirements.txt` — sorted alphabetically
- `deploy.sh` — added cd to deploy-streamlit-app
- `force-deploy.sh` — added cd to deploy-streamlit-app
- `workshop4/phase2/README.md` — updated directory structure
- `.kiro/specs/workshop4/workshop4-phase2-ecs-deployment/design.md` — updated structure + Dockerfile + deploy script

### Convention: Alphabetical requirements.txt
- Rationale: easier for humans to verify if something is missing
- Applied to all requirements.txt files going forward

## Phase 3 Fix (Completed)

### Structure Change
Created `studentservices/` as the AgentCore project boundary (like `travelplanner/` in reference):
- `agentcore/` inside it contains ONLY config (agentcore.json, aws-targets.json)
- Agent code directories are siblings of `agentcore/` at the project root
- Renamed `orchestrator/` → `student_services/` (matches the agent's domain, not its role)
- `cloudformation/`, `deploy-streamlit-app/`, `streamlit_app/` at phase3 root (consistent with Phase 1/2 pattern)

### Credential Naming Fix
- `CourseRegistrationAgentoauth` → `CourseRegistrationAgent-oauth`
- `CourseReviewAgentoauth` → `CourseReviewAgent-oauth`
- `LoanApplicationAgentoauth` → `LoanApplicationAgent-oauth`
- `MathTeachingAgentoauth` → `MathTeachingAgent-oauth`
- `studentservicesgatewayoauth` → `student-services-gateway-oauth`

### Files Updated
- Created `workshop4/phase3/studentservices/` with correct structure
- Removed old `workshop4/phase3/agentcore/` (wrong structure)
- Updated `agentcore.json` — credential names, codeLocation for student_services
- Updated `PREREQUISITES.md` — correct project structure
- Created `README.md` — clean student-facing documentation
- Added `.gitkeep` for `deploy-streamlit-app/` and `streamlit_app/` (not yet built)

## Decisions Made
- All application code for Phase 1 lives inside `streamlit_app/` as one self-contained package
- Phase 2: same code inside `docker_app/` (the container boundary)
- Phase 3: `studentservices/` is the AgentCore project boundary; agent code at project root, `agentcore/` is config only
- Infrastructure (cloudformation/), data, and scripts remain at the phase root
- Alphabetical sorting for requirements.txt and directory structures in docs
- `.gitkeep` only for empty placeholder directories; remove once real content exists
- AgentCore project name must be `studentservices` (no underscores allowed by schema)

## Next Steps
- [ ] Fix Phase 3 agent code (imports, gateway config, etc.)
- [ ] Build thin client (streamlit_app/ and deploy-streamlit-app/)
- [ ] Zip, upload, unpack, commit and push on code-server for each phase
