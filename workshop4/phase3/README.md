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

### After Recreating Cognito Pools (Full Redeploy)

If you tear down and recreate the CloudFormation stack, you MUST update these files with new pool IDs/secrets:

1. `studentservices/agentcore/agentcore.json` — discoveryUrl + allowedClients on each runtime and gateway
2. `studentservices/student_services/agent.py` — GATEWAY_MCP_URL, GATEWAY_CLIENT_ID, GATEWAY_CLIENT_SECRET (hardcoded defaults)
3. Re-run `register-credentials.sh` to register new OAuth credentials

The gateway URL also changes on every fresh deploy (random suffix). Update it in both `agentcore.json` (gateway targets) and `agent.py` (GATEWAY_MCP_URL).

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

## Model Configuration

All runtimes (orchestrator + 4 specialists) read the model ID from SSM Parameter Store at agent creation time:

```
/student-services/model-id → us.amazon.nova-2-lite-v1:0  (default, set by Phase 1 infra stack)
```

**To change the model for all agents:**

```bash
aws ssm put-parameter \
  --name /student-services/model-id \
  --value "us.anthropic.claude-sonnet-4-6" \
  --type String \
  --overwrite \
  --region us-west-2
```

The change takes effect on the next new session (sign out and back in). No redeployment required — each agent reads SSM at creation time, and a new session creates a fresh agent instance.

**Resolution order** (same as Phase 1): environment variable `MODEL_ID` → SSM `/student-services/model-id` → hardcoded default `us.amazon.nova-2-lite-v1:0`

### Why No Dynamic Model Selection?

In Phase 1/2 (monolithic), the orchestrator creates specialist agents locally and can pass the model config directly. In Phase 3 (microservices), the orchestrator communicates with specialists via MCP protocol through the gateway — there's no mechanism to propagate a model choice from the thin client through the orchestrator, through the gateway, to each specialist's internal agent.

Dynamic per-request model selection in a distributed architecture would require:
1. Adding `model_id` as a parameter to every MCP tool
2. Each specialist's MCP handler accepting and forwarding it to its internal agent
3. Breaking the independence of each microservice's configuration

The SSM approach gives you centralized, consistent model configuration across all runtimes without coupling them at the protocol level. The thin client displays the configured model as read-only information.

## Sample Test Prompts (Runtime Playground)

Use these in the AgentCore Runtime Playground or via `agentcore invoke`.

### Course Registration

```
Register student STU001 for CS 441 in Fall 2026
```

### Course Reviews

```
What are the most challenging courses?
```

```
Find courses about artificial intelligence
```

```
Tell me about CS 441 Machine Learning
```

### Loan Prediction

```
Will a person with these features accept the loan: `29,2,999,0,1,0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0`
```

### Math Tutoring

```
Solve x^2 + 5x + 6 = 0
```

```
What is the derivative of x^3 + 2x?
```
