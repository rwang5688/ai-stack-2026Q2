# Workshop 4 Phase 3: AgentCore Microservices

Decomposes the Phase 1/2 monolithic Student Services app into independent AgentCore microservices. Each agent becomes its own runtime, communicating via an AgentCore Gateway with Cedar policy enforcement and shared memory.

## Architecture

```
Streamlit Thin Client → StudentServicesOrchestrator (AgentCore Runtime)
                              ↓ (via AgentCore Gateway + OAuth2)
              ┌───────────────┼───────────────┐───────────────┐
              ↓               ↓               ↓               ↓
    CourseRegistration   CourseReview    LoanApplication   MathTeaching
      (Runtime)           (Runtime)       (Runtime)        (Runtime)
         ↓                   ↓               ↓
      DynamoDB         Bedrock KB +      SageMaker
                       DynamoDB          XGBoost
```

- **5 AgentCore Runtimes** — 1 orchestrator + 4 specialists
- **1 AgentCore Gateway** — aggregates specialist tools, OAuth2-secured
- **1 AgentCore Memory** — SEMANTIC, SUMMARIZATION, USER_PREFERENCE strategies
- **Cedar Policies** — content safety and tool access control
- **Thin Client** — Streamlit app (local dev + ECS Fargate deployment)

## Prerequisites

See [PREREQUISITES.md](PREREQUISITES.md) for required tools and CLI reference.

## Project Structure

```
workshop4/phase3/
├── cloudformation/                     # Identity stack (Cognito pools)
│   ├── stack-outputs.json
│   └── student-services-identity.yaml
├── deploy-streamlit-app/               # Thin client ECS deployment (Phase 2 pattern)
│   └── .gitkeep
├── streamlit_app/                      # Local dev thin client
│   └── .gitkeep
├── studentservices/                    # AgentCore project
│   ├── agentcore/                      # Config ONLY (agentcore.json, aws-targets.json)
│   │   ├── agentcore.json
│   │   └── aws-targets.json
│   ├── course_registration/            # Specialist agent runtime
│   │   ├── agent.py
│   │   └── requirements.txt
│   ├── course_review/                  # Specialist agent runtime
│   │   ├── agent.py
│   │   └── requirements.txt
│   ├── loan_application/               # Specialist agent runtime
│   │   ├── agent.py
│   │   └── requirements.txt
│   ├── math_teaching/                  # Specialist agent runtime
│   │   ├── agent.py
│   │   └── requirements.txt
│   ├── policies/                       # Cedar policy files
│   │   └── permit_all_tools.cedar
│   └── student_services/               # Orchestrator agent runtime
│       ├── agent.py
│       └── requirements.txt
├── .gitignore
├── PREREQUISITES.md
└── README.md
```

### Structure Rationale

The `studentservices/` directory is the AgentCore CLI project boundary (equivalent to `travelplanner/` in the reference implementation):
- `agentcore/` contains only configuration — `agentcore.json` and `aws-targets.json`
- Agent code lives at the project root as sibling directories of `agentcore/`
- `codeLocation` paths in `agentcore.json` resolve relative to the project root (e.g., `"./orchestrator/"`)
- `cloudformation/`, `deploy-streamlit-app/`, and `streamlit_app/` are at the phase3 root (same level pattern as Phase 1 and Phase 2)

## Deployment

### 1. Deploy Identity Stack (Cognito Pools)

```bash
cd workshop4/phase3
aws cloudformation deploy \
  --stack-name student-services-identity \
  --template-file cloudformation/student-services-identity.yaml \
  --region us-west-2
```

### 2. Deploy AgentCore Runtimes

```bash
cd workshop4/phase3/studentservices
agentcore deploy -y
```

### 3. Check Status

```bash
cd workshop4/phase3/studentservices
agentcore status
```

### 4. Invoke the Orchestrator

```bash
cd workshop4/phase3/studentservices
agentcore invoke "What courses are available for Fall 2026?"
```

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Agents (not MCP servers) for specialists | Each specialist has its own LLM reasoning — they're agents, not data servers |
| AgentCore Gateway | Single entry point for orchestrator to reach all specialists via MCP protocol |
| Cedar policies | Declarative access control; forbid-wins semantics for content safety |
| OAuth2 per specialist | Each runtime has its own Cognito pool for independent identity |
| Memory with 3 strategies | SEMANTIC for facts, SUMMARIZATION for session context, USER_PREFERENCE for personalization |
| `studentservices/` project boundary | Matches AgentCore CLI conventions; `agentcore deploy` runs from this directory |

## AWS Region

All Phase 3 resources deploy to **us-west-2** (matching Phase 1 infrastructure).
