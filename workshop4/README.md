# Workshop 4: Multi-Agent Student Services — Agentic AI Application Development - From Monolith to Agents as Microservices

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

## Code Mapping: Phase 1 → Phase 3

The core business logic is **identical** between phases. The difference is how specialist agents are exposed and invoked. Use `diff` to compare:

```bash
diff workshop4/phase1/streamlit_app/course_registration_agent/agent.py \
     workshop4/phase3/studentservices/course_registration/agent.py
```

### Structural Comparison

| Aspect | Phase 1 (Monolith) | Phase 3 (AgentCore MCP) |
|--------|-------------------|------------------------|
| **Entry point** | `@tool` decorator — called in-process by orchestrator | `@mcp.tool()` decorator — called remotely via MCP protocol through Gateway |
| **Transport** | Direct function call (same process) | MCP streamable-http (network call) |
| **Config** | Shared `config.py` (SSM-backed, imported) | `os.environ.get(...)` (env vars injected by AgentCore runtime) |
| **Model creation** | `create_model_from_config()` (shared factory) | `BedrockModel(...)` (direct, self-contained per runtime) |
| **Inner tools** | `@tool register_student(...)` | `@tool register_course_inner(...)` (same logic) |
| **Response format** | Returns `str` prefixed with `[Agent Name]` | Returns `dict` with `{"response": str, "runtime": RUNTIME_NAME}` |
| **Server bootstrap** | None (imported by orchestrator) | `mcp.run(transport="streamable-http", ...)` |
| **Dependencies** | Shares code with other agents via imports | Self-contained — no cross-runtime imports |

### The Two-Layer Tool Pattern (Preserved Across Phases)

Both phases use the same two-layer pattern:

```
Phase 1:
  Orchestrator calls → @tool course_registration_assistant(query)
                            → creates inner Agent
                            → inner Agent calls → @tool register_student(...)
                            → returns string response

Phase 3:
  Orchestrator calls → Gateway → @mcp.tool() course_registration_assistant(prompt)
                                      → creates inner Agent
                                      → inner Agent calls → @tool register_course_inner(...)
                                      → returns dict response
```

The inner agent reasoning (LLM call, tool selection, validation) is identical. The only difference is the **outer wrapper**: `@tool` (in-process) vs `@mcp.tool()` (network service).

### What Changes When Moving to AgentCore

1. **Replace `@tool` with `@mcp.tool()`** on the outer function (the one the orchestrator calls)
2. **Add `FastMCP` server bootstrap** at the bottom of the file
3. **Replace shared config imports** with `os.environ.get()` (each runtime is self-contained)
4. **Replace shared model factory** with direct `BedrockModel(...)` instantiation
5. **Add `RUNTIME_NAME`** to responses so the thin client can show which runtime handled the request
6. **Return `dict` instead of `str`** from the outer MCP tool (MCP protocol uses structured data)

### What Stays the Same

- System prompts
- Inner tool logic (validation, DynamoDB writes, KB queries, SageMaker invocations)
- Error handling patterns
- The Agent-inside-tool pattern (specialist agent with its own LLM reasoning)
