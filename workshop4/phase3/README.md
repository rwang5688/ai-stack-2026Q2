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

### Bootstrap Sequence (First Time Only)

The initial deployment requires multiple steps due to dependencies between resources:

```
┌─────────────────────────────────────────────────────────────────────┐
│ Step 1: CloudFormation (Cognito pools)                              │
│   bash deploy-student-services-identity.sh                          │
│                                                                     │
│ Step 2: Register OAuth credentials (fetches secrets from Cognito)   │
│   cd studentservices                                                │
│   bash ../register-credentials.sh                                   │
│                                                                     │
│ Step 3: AgentCore Deploy 1 (runtimes + memory + credentials)        │
│   agentcore deploy -y                                               │
│   agentcore status  ← note runtime URLs                             │
│                                                                     │
│ Step 4: Add gateway to agentcore.json (with runtime endpoint URLs)  │
│   [manual edit or script — gateway needs real runtime URLs]          │
│                                                                     │
│ Step 5: AgentCore Deploy 2 (gateway)                                │
│   agentcore deploy -y                                               │
│   agentcore status  ← verify gateway deployed                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Why two deploys?** The gateway targets need runtime endpoint URLs, which only exist after runtimes are deployed. This chicken-and-egg problem requires deploying runtimes first, then adding the gateway with real URLs.

**After bootstrap:** Subsequent deploys are single-step (`agentcore deploy -y`) because runtimes already exist and the gateway references them.

### Step-by-Step Commands

#### 1. Deploy Identity Stack (Cognito Pools)

```bash
cd workshop4/phase3
bash deploy-student-services-identity.sh
```

Creates 5 Cognito User Pools and captures outputs to `cloudformation/stack-outputs.json`.

#### 2. Register OAuth Credentials

```bash
cd workshop4/phase3/studentservices
bash ../register-credentials.sh
```

Fetches client secrets from Cognito and registers them with the AgentCore CLI. Must run AFTER Step 1 (needs pools to exist) and BEFORE Step 3 (so credentials deploy with runtimes).

#### 3. AgentCore Deploy 1 (Runtimes)

```bash
cd workshop4/phase3/studentservices
agentcore deploy -y
agentcore status
```

Deploys 5 runtimes + memory + credentials. Note the runtime URLs from `agentcore status` output.

#### 4. Add Gateway Configuration

Update `agentcore/agentcore.json` to add the `agentCoreGateways` array with the real runtime endpoint URLs from Step 3. See the deployed `agentcore.json` for the complete gateway configuration.

#### 5. AgentCore Deploy 2 (Gateway)

```bash
cd workshop4/phase3/studentservices
agentcore deploy -y
agentcore status
```

Deploys the gateway with 4 MCP server targets. Verify "Gateways: studentservicesgateway: Deployed (4 targets)" in status output.

### Testing

```bash
cd workshop4/phase3/studentservices
agentcore invoke "What courses are available for Fall 2026?"
```

Or test in the AgentCore Runtime Playground (AWS Console → Bedrock → AgentCore → Runtimes → StudentServicesAgent → Playground).

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

## Sample Test Prompts (Runtime Playground)

Use these in the AgentCore Runtime Playground or via `agentcore invoke`.

### Course Review (catalog search, reviews, ratings)

```
What courses are available in the CS department?
```

```
Show me reviews for CS 441
```

```
Which course has the highest rating?
```

```
What is the workload for CS 525 Advanced Distributed Systems?
```

### Course Registration

```
Register student 1111 for CS 498 for spring semester
```

```
Register student 2222 for CS 411 for spring semester
```

### Loan Application (59 numeric features)

```
Predict loan acceptance for these features: 1, 0, 0, 1, 1, 0, 500, 120, 360, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
```

### Math Tutoring

```
Solve the integral of x^2 * e^x dx step by step
```

```
Factor x^3 - 8
```

```
What is the derivative of sin(x) * ln(x)?
```

### Out-of-Domain (should list available services)

```
What is the weather today?
```

```
Write me a poem about campus life
```
