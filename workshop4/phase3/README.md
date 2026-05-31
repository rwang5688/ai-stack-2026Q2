# Workshop 4 Phase 3: AgentCore Microservices

Decomposes the Phase 1/2 monolithic Student Services app into AgentCore microservices. All agent intelligence runs in one HTTP Runtime (Agent-as-Tool pattern), with dumb deterministic data-access tools exposed as MCP servers via AgentCore Gateway.

## Architecture

```
Thin Streamlit Client ──(SigV4 HTTP POST)──→ StudentServicesAgent (HTTP Runtime)
                                                    │
                                          ┌─────────┼─────────┬─────────────┐
                                          │         │         │             │
                                   course_review  course_reg  loan_app   math_teaching
                                     (Agent)      (Agent)     (Agent)      (Agent)
                                          │         │         │             │
                                          │ OAuth2 token (student-services-gateway-pool)
                                          ↓         ↓         ↓             │
                                    AgentCore Gateway                       │
                              ┌───────────┼─────────┼─────────┐            │
                              ↓           ↓         ↓         ↓            ↓
                        CourseCatalog  CourseReview  CourseReg  LoanApp  calculator
                         (MCP Server)  (MCP Server)  (MCP Srv)  (MCP Srv)  (local)
                              ↓           ↓            ↓          ↓
                          Bedrock KB   DynamoDB     DynamoDB   SageMaker
                                                               XGBoost
```

- **1 HTTP Runtime** — StudentServicesAgent (orchestrator + 4 specialist agents locally via Agent-as-Tool)
- **4 MCP Runtimes** — Dumb data-access tools only (no LLM calls, no reasoning)
- **1 AgentCore Gateway** — aggregates MCP tools, OAuth2-secured per target
- **1 AgentCore Memory** — SEMANTIC, SUMMARIZATION, USER_PREFERENCE strategies
- **Thin Client** — Streamlit app (local dev + ECS Fargate deployment)

## Key Design Principle: Reasoning Layer vs Capability Layer

- **Reasoning Layer** — ALL agent intelligence (orchestrator + 4 specialists) runs in one AgentCore HTTP Runtime using the Agent-as-Tool pattern. Each specialist has its own system prompt and LLM reasoning.
- **Capability Layer** — MCP servers are stateless data-access functions (direct SDK calls, return in <1 second). No LLM calls, no reasoning.

This separation ensures fast tool responses, independent scaling of data access, and clean observability boundaries.

## Prerequisites

See [PREREQUISITES.md](PREREQUISITES.md) for required tools and CLI reference.

## Project Structure

```
workshop4/phase3/
├── cloudformation/                     # Identity + IAM stack
│   └── student-services-agentcore-infra.yaml
├── deploy-streamlit-app/               # Thin client ECS deployment (CDK)
│   ├── cdk/                            # CDK stack (VPC, ECS, ALB, CloudFront)
│   └── docker_app/                     # Container app (Cognito auth + SigV4 client)
├── streamlit_app/                      # Local dev thin client
│   ├── agent_client.py                 # SigV4-signed HTTP client
│   ├── app.py                          # Streamlit chat UI
│   ├── run.sh                          # Linux launcher
│   └── run.ps1                         # Windows launcher
├── studentservices/                    # AgentCore project root
│   ├── agentcore/                      # Config (agentcore.json, aws-targets.json, cdk/)
│   ├── course_catalog/                 # MCP server: Bedrock KB search
│   │   └── server.py
│   ├── course_registration/            # MCP server: DynamoDB write
│   │   └── server.py
│   ├── course_review/                  # MCP server: DynamoDB read
│   │   └── server.py
│   ├── loan_application/               # MCP server: SageMaker invoke
│   │   └── server.py
│   ├── policies/                       # Cedar policy files
│   │   └── permit_all_tools.cedar
│   └── student_services/               # Orchestrator (all agent intelligence here)
│       ├── __init__.py
│       ├── student_services_agent.py   # Orchestrator + MCPClient
│       ├── course_registration_agent.py
│       ├── course_review_agent.py
│       ├── loan_application_agent.py
│       ├── math_teaching_agent.py
│       └── calculator.py
├── deploy-agentcore-infra.sh
├── deploy-streamlit-app.sh
├── register-credentials.sh
├── PREREQUISITES.md
└── README.md
```

## Deployment

### Two-Pass Deploy (Required for Fresh Deployments)

AgentCore gateway targets need runtime URLs that only exist after runtimes deploy. This requires two passes:

```
Pass 1: Empty gateway targets → creates runtimes + gateway (no health check)
Pass 2: Add real runtime URLs to targets → gateway connects to MCP servers
```

### Step-by-Step Commands

#### 1. Deploy Infrastructure (Cognito + IAM Roles)

```bash
cd workshop4/phase3
bash deploy-agentcore-infra.sh
```

#### 2. Register OAuth Credentials

```bash
cd workshop4/phase3/studentservices
bash ../register-credentials.sh
```

#### 3. Pass 1 — Deploy Runtimes (empty gateway targets)

Ensure `agentcore.json` has `"targets": []` in the gateway section, then:

```bash
cd workshop4/phase3/studentservices
agentcore deploy -y
agentcore status
```

All 5 runtimes should show READY. Note the MCP server URLs.

#### 4. Pass 2 — Add Gateway Targets and Redeploy

Update `agentcore.json` with the real runtime URLs from step 3, then:

```bash
agentcore deploy -y
agentcore status
```

Verify: `studentservicesgateway: Deployed (4 targets)`

#### 5. Update Orchestrator Gateway URL

If the gateway name changed (new random suffix), update `student_services/student_services_agent.py`:
- `GATEWAY_MCP_URL` hardcoded default

Then redeploy to push the code change:

```bash
agentcore deploy -y
```

### Testing

```bash
# Math (local calculator, no MCP)
agentcore invoke --runtime StudentServicesAgent "What is 2 + 2?"

# Course catalog + reviews (Gateway → 2 MCP servers)
agentcore invoke --runtime StudentServicesAgent "Find courses about artificial intelligence"

# Registration (Gateway → DynamoDB write)
agentcore invoke --runtime StudentServicesAgent "Register student STU001 for CS 441 in Fall 2026"

# Loan prediction (Gateway → SageMaker)
agentcore invoke --runtime StudentServicesAgent "Will a person with these features accept the loan: 29,2,999,0,1,0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0"
```

### Local Thin Client

```bash
cd workshop4/phase3/streamlit_app
bash run.sh
```

Requires AWS credentials configured (SigV4 signing).

### Production Thin Client (ECS Fargate)

Run from **code-server** (requires Docker):

```bash
cd workshop4/phase3
bash deploy-streamlit-app.sh
```

Deploys to ECS Fargate behind CloudFront with Cognito authentication.

## Identity & Authentication

```
Thin Client ──(SigV4/IAM)──→ StudentServicesAgent
                                    │
                                    │ OAuth2 token (student-services-gateway-pool)
                                    ↓
                              AgentCore Gateway
                                    │
                                    │ OAuth2 tokens (per-specialist pools)
                                    ↓
                              MCP Servers (validate against own pools)
```

| Pool | Protects | Used By |
|------|----------|---------|
| `student-services-gateway-pool` | Gateway inbound | Orchestrator (outbound to gateway) |
| `course-catalog-pool` | CourseCatalogMcp | Gateway (outbound) |
| `course-registration-pool` | CourseRegistrationMcp | Gateway (outbound) |
| `course-review-pool` | CourseReviewMcp | Gateway (outbound) |
| `loan-application-pool` | LoanApplicationMcp | Gateway (outbound) |

The orchestrator uses SigV4 (IAM) for inbound — no Cognito pool needed for it.

## Model Configuration

All agents read model ID from SSM Parameter Store:

```
/student-services/model-id → us.amazon.nova-2-lite-v1:0
```

**To change the model:**

```bash
aws ssm put-parameter \
  --name /student-services/model-id \
  --value "us.anthropic.claude-sonnet-4-6" \
  --type String \
  --overwrite \
  --region us-west-2
```

Takes effect on next new session. No redeployment required.

**Resolution order:** env var `MODEL_ID` → SSM → hardcoded default.

## Workshop Progression

| Phase | Pattern | Key Concept |
|-------|---------|-------------|
| Phase 1 | Monolithic | All agents + tools in one process |
| Phase 2 | Multi-agent | Agent-as-Tool, Cognito auth, ECS Fargate |
| Phase 3 | Microservices | Same Agent-as-Tool intelligence, data access decoupled behind Gateway + MCP |

Phase 3 demonstrates: independent scaling per tool, Cedar policies, OAuth per-service, observability per-tool — while keeping all reasoning in one runtime for simplicity and performance.

## AWS Region

All Phase 3 resources: **us-west-2**
