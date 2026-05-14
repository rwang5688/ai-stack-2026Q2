# Workshop 4 Phase 3: AgentCore Microservices

Decomposes the Phase 1/2 monolithic Student Services app into independent AgentCore microservices. Each agent becomes its own runtime, communicating via an AgentCore Gateway with Cedar policy enforcement and shared memory.

## Architecture

```
Thin Streamlit Client ──(SigV4 HTTP POST)──→ StudentServicesAgent (HTTP Runtime)
                                                    │
                                                    │ OAuth2 token (student-services-gateway-pool)
                                                    ↓
                                          AgentCore Gateway (validates token)
                              ┌───────────────┼───────────────┐───────────────┐
                              ↓               ↓               ↓               ↓
                    CourseRegistration   CourseReview    LoanApplication   MathTeaching
                       (MCP Server)      (MCP Server)    (MCP Server)     (MCP Server)
                           ↓                 ↓               ↓
                        DynamoDB       Bedrock KB +      SageMaker
                                       DynamoDB          XGBoost
```

- **1 HTTP Runtime** — StudentServicesAgent (orchestrator with LLM reasoning)
- **4 MCP Runtimes** — Specialist agents wrapped as MCP tool servers (each with its own LLM)
- **1 AgentCore Gateway** — aggregates specialist tools, OAuth2-secured
- **1 AgentCore Memory** — SEMANTIC, SUMMARIZATION, USER_PREFERENCE strategies
- **Cedar Policies** — content safety and tool access control (added after initial deploy)
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

## Identity & Authentication

AgentCore uses OAuth2 (Cognito User Pools) to secure communication between runtimes. Each pool issues tokens via the `client_credentials` grant — no human users involved.

### Auth Flow

```
Thin Client ──(SigV4/IAM)──→ StudentServicesAgent (HTTP runtime)
                                    │
                                    │ presents token from student-services-gateway-pool
                                    ↓
                              AgentCore Gateway (validates token)
                                    │
                                    │ presents tokens from specialist pools
                                    ↓
                              MCP Servers (validate tokens against their own pools)
```

### Pool Naming & Purpose

| Pool Name | Protects | Used By (as client) |
|-----------|----------|---------------------|
| `student-services-gateway-pool` | Gateway inbound | StudentServicesAgent (orchestrator) |
| `course-registration-pool` | CourseRegistrationMcp | Gateway (outbound to specialist) |
| `course-review-pool` | CourseReviewMcp | Gateway (outbound to specialist) |
| `loan-application-pool` | LoanApplicationMcp | Gateway (outbound to specialist) |
| `math-teaching-pool` | MathTeachingMcp | Gateway (outbound to specialist) |

### Key Points

- The **orchestrator does NOT need its own inbound auth pool** — it's invoked via SigV4 (IAM-based) from the thin client
- The **gateway pool** (`student-services-gateway-pool`) is the orchestrator's **outbound credential** to authenticate with the gateway
- Each **specialist pool** protects that specialist's MCP server — the gateway authenticates outbound to each specialist using that specialist's pool credentials
- Pool names match the directory/runtime names for consistency (e.g., `course_registration/` → `course-registration-pool`)

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Agent-inside-MCP for specialists | Each specialist has its own LLM reasoning wrapped in FastMCP — preserves Phase 1 behavior while exposing tools via MCP protocol |
| AgentCore Gateway | Single entry point for orchestrator to reach all specialists via MCP protocol |
| Cedar policies | Declarative access control; forbid-wins semantics for content safety |
| OAuth2 per specialist | Each MCP server has its own Cognito pool for independent identity and rotation |
| Memory with 3 strategies | SEMANTIC for facts, SUMMARIZATION for session context, USER_PREFERENCE for personalization |
| `studentservices/` project boundary | Matches AgentCore CLI conventions; `agentcore deploy` runs from this directory |
| File name `agent.py` preserved | Enables `diff` comparison between Phase 1 and Phase 3 to see the mapping |

## AWS Region

All Phase 3 resources deploy to **us-west-2** (matching Phase 1 infrastructure).
