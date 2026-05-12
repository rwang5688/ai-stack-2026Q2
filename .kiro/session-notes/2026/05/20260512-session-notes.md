# Session Notes - May 12, 2026

## Session Overview
Starting Phase 3: Decomposing the monolithic Student Services app into AgentCore microservices. Generating specs based on the architecture plan from May 11 session notes and the TravelPlanner reference implementation.

## Phase 3 Context

### Current State
- Phase 1: Monolithic multi-agent app (Strands SDK, 4 specialists + orchestrator + Streamlit UI) — COMPLETE
- Phase 2: Containerized Phase 1 on ECS Fargate (CloudFront → ALB → ECS, Cognito auth) — COMPLETE
- Phase 3: AgentCore microservices decomposition — STARTING NOW

### Architecture (from May 11 planning)
Three-step decomposition:

**Step 1: Identity Infrastructure (CloudFormation)**
- Individual Cognito User Pools + OAuth2 clients for each AgentCore Runtime
- Backs AgentCore Inbound Identities for securing individual runtimes

**Step 2: AgentCore Project ("student-services")**
- Orchestrator: "Student Services Agent" as AgentCore Runtime
- 4 Specialist AgentCore Runtimes (Course Registration, Course Review, Loan Application, Math Teaching)
- AgentCore Gateway ("student-services-gateway") — single endpoint for all specialists
- AgentCore Memory (SEMANTIC, SUMMARIZATION, USER_PREFERENCES)
- AgentCore Policies (block abusive language, mask PII)

**Step 3: Thin Streamlit App (CDK/ECS Fargate)**
- Microservices-based Streamlit on ECS Fargate behind CloudFront + ALB
- Cognito User Pool for end-user auth
- `agent_client.py` — SigV4Auth POST to STUDENT_SERVICES_AGENT_URL
- Completely decoupled from backend agent layer

### Reference Implementation
- `.kiro/references/agentcore-workshop/travelplanner/` — TravelPlanner pattern
- Key patterns: agentcore.json (flat resource model), OAuth2 via Cognito, Gateway with Cedar policies, SigV4 agent_client, CDK ECS deployment

## Key Accomplishments
- Reviewed Phase 3 architecture plan and reference implementations
- Generated spec for Phase 3 implementation

## Next Steps
- [ ] Implement Phase 3 per spec tasks
