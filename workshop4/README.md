# Workshop 4: Multi-Agent Student Services — From Monolith to Microservices

This workshop builds a multi-agent Student Services system for Any University (any.edu) and progressively evolves its architecture from a monolithic application to independently deployable microservices.

## Architecture Evolution

| Phase | Architecture | Key Characteristic |
|-------|-------------|-------------------|
| Phase 1 | Monolithic Agentic App | All agents + UI in one process |
| Phase 2 | Containerized Monolith | Same app deployed to ECS Fargate |
| Phase 3 | Agent Microservices | Agents as independent runtimes, thin client frontend |

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

Decomposes the monolith into independent AgentCore Runtimes. Each agent becomes its own managed service, communicating through an AgentCore Gateway. The Streamlit app becomes a thin client that invokes the orchestrator via a stable HTTP POST — completely decoupled from backend agent logic.

```
Thin Streamlit Client ──(SigV4 HTTP POST)──→ Orchestrator Runtime
                                                    ↓
                                          AgentCore Gateway (OAuth2)
                                    ┌───────┼───────┼───────┐
                                    ↓       ↓       ↓       ↓
                              CourseReg  CourseRev  Loan   Math
                              (Runtime)  (Runtime) (Runtime) (Runtime)
                                 ↓          ↓        ↓
                              DynamoDB   Bedrock   SageMaker
                                         KB+DDB   XGBoost
```

**Pros**: Frontend and backend agents evolve independently. Add/update/scale specialists without touching the client. Cedar policies enforce content safety at the gateway layer. Memory provides cross-session context.
**Cons**: More infrastructure to manage; OAuth2 identity per runtime.

## Agents

| Agent | Role | External Services |
|-------|------|-------------------|
| Student Services (Orchestrator) | Routes queries to specialists | AgentCore Gateway |
| Course Registration | Enrolls students in courses | DynamoDB |
| Course Review | Course catalog and review lookup | Bedrock Knowledge Base, DynamoDB |
| Loan Application | Predicts loan acceptance | SageMaker XGBoost |
| Math Teaching | Step-by-step math tutoring | Calculator tools |

## AWS Region

All resources deploy to **us-west-2**.
