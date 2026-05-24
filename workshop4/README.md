# Workshop 4: Multi-Agent Student Services — Agentic AI Application Development - From Monolith to Agents as Microservices

This workshop builds a multi-agent Student Services system for Any University (any.edu) and progressively evolves its architecture from a monolithic application to independently deployable microservices.

## Architecture Evolution

| Phase | Architecture | Key Characteristic |
|-------|-------------|-------------------|
| Phase 1 | Monolithic Agentic App | All agents + UI in one process |
| Phase 2 | Containerized Monolith | Same app deployed to ECS Fargate with Cognito auth |
| Phase 3 | Agent Microservices | Agent intelligence in one runtime, data access decoupled behind Gateway |

## [Phase 1: Monolithic Agentic Application](phase1/README.md)

A single Streamlit application that embeds all agent logic in one process. The orchestrator agent and four specialist agents (Course Registration, Course Review, Loan Application, Math Teaching) run in-process, communicating via direct function calls.

```
┌─────────────────────────────────────────────────┐
│              Streamlit Application               │
│                                                  │
│  Orchestrator Agent                              │
│    ├── Course Registration Agent → DynamoDB      │
│    ├── Course Review Agent → Bedrock KB + DDB    │
│    ├── Loan Application Agent → SageMaker        │
│    └── Math Teaching Agent → Calculator          │
└─────────────────────────────────────────────────┘
```

**Pros**: Simple to develop and debug locally.
**Cons**: All agents coupled — changing one requires redeploying everything.

## [Phase 2: Containerized Monolith on ECS Fargate](phase2/README.md)

The same monolithic application from Phase 1, containerized and deployed to AWS ECS Fargate behind CloudFront and an ALB. Cognito provides end-user authentication.

```
CloudFront → ALB → ECS Fargate (Streamlit + all agents)
                        ↓
              Cognito User Pool (end-user auth)
```

**Pros**: Production-ready hosting with HTTPS, auth, and auto-scaling.
**Cons**: Still a monolith — backend agent changes require container rebuild and redeployment.

## [Phase 3: Agent Microservices (AgentCore)](phase3/README.md)

Separates the Reasoning Layer from the Capability Layer. All agent intelligence (orchestrator + 4 specialists) runs in one AgentCore HTTP Runtime using the Agent-as-Tool pattern. Data access is decoupled into dumb MCP servers behind an AgentCore Gateway — no LLM calls in MCP servers, just direct SDK calls that return in <1 second.

```
Thin Streamlit Client ──(SigV4 HTTP POST)──→ StudentServicesAgent (HTTP Runtime)
                                                    │
                                          ┌─────────┼─────────┬──────────┐
                                          │         │         │          │
                                   course_review  course_reg  loan_app  math
                                     (Agent)      (Agent)     (Agent)   (Agent)
                                          │         │         │          │
                                    OAuth2 via Gateway                calculator
                              ┌───────────┼─────────┼─────────┐      (local)
                              ↓           ↓         ↓         ↓
                        CourseCatalog  CourseReviews  CourseReg  LoanApp
                         (MCP Server)  (MCP Server)  (MCP Srv)  (MCP Srv)
                              ↓           ↓            ↓          ↓
                          Bedrock KB   DynamoDB     DynamoDB   SageMaker
```

**Pros**: Frontend and backend evolve independently. Data-access tools scale independently. Cedar policies enforce access control at the gateway. OAuth2 per-service identity. Observability per-tool.
**Cons**: Two-pass deployment required. Gateway adds latency for tool calls.

## Agents

| Agent | Role | External Services |
|-------|------|-------------------|
| Student Services (Orchestrator) | Routes queries to specialists | AgentCore Gateway (MCPClient) |
| Course Review (local Agent-as-Tool) | Course catalog and review lookup | Gateway → CourseCatalogMcp + CourseReviewsMcp |
| Course Registration (local Agent-as-Tool) | Enrolls students in courses | Gateway → CourseRegistrationMcp |
| Loan Application (local Agent-as-Tool) | Predicts loan acceptance | Gateway → LoanApplicationMcp |
| Math Teaching (local Agent-as-Tool) | Step-by-step math tutoring | Local calculator (no MCP) |

## MCP Servers (Dumb Tools — No LLM Calls)

| MCP Server | Tool | Backend |
|-----------|------|---------|
| CourseCatalogMcp | `search_course_catalog` | Bedrock Knowledge Base |
| CourseReviewsMcp | `get_course_reviews` | DynamoDB (course_reviews table) |
| CourseRegistrationMcp | `register_course` | DynamoDB (course_registration table) |
| LoanApplicationMcp | `predict_loan` | SageMaker XGBoost endpoint |

## AWS Region

All resources deploy to **us-west-2**.

## Code Mapping: Phase 1 → Phase 3

The core business logic is preserved across phases. The key architectural difference:

| Aspect | Phase 1 (Monolith) | Phase 3 (AgentCore) |
|--------|-------------------|---------------------|
| **Agent location** | All in one process | All in one AgentCore Runtime (Agent-as-Tool) |
| **Tool location** | In-process (direct SDK calls) | Remote MCP servers (via Gateway) |
| **Transport** | Direct function call | MCPClient → Gateway → MCP server |
| **Auth** | None (same process) | OAuth2 per MCP server (Cognito pools) |
| **Model config** | Shared `config.py` | SSM Parameter Store (centralized) |
| **Thin client** | Streamlit (embedded) | Streamlit (SigV4 HTTP POST to runtime) |

### What Moved Where

```
Phase 1 (one process):
  Orchestrator → @tool specialist_agent(query) → inner Agent → @tool do_thing() → SDK call

Phase 3 (distributed):
  Orchestrator → @tool specialist_agent(query) → inner Agent → MCPClient → Gateway → MCP server → SDK call
```

The specialist agents still have their own system prompts and LLM reasoning — they just reach their data-access tools through the network (Gateway + MCP) instead of direct function calls. The MCP servers themselves have NO agent logic — they're just thin wrappers around boto3 SDK calls.
