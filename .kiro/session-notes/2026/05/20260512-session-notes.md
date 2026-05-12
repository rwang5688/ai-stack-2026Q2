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
- Generated spec for Phase 3 implementation (requirements, design, tasks)
- Deployed CloudFormation identity stack (`student-services-identity`) — 5 Cognito pools in us-west-2
- Created all 5 AgentCore runtime agent.py files (orchestrator + 4 specialists)
- Created agentcore.json (validated) — runtimes, memory, credentials
- Created Cedar policy file (permit_all_tools.cedar)
- Installed AgentCore CLI v0.13.1 and CDK v2.1121.0
- Created PREREQUISITES.md and agentcore-conventions.md steering file
- Confirmed Python 3.13.12, Node 24.15.0

## Deployment Strategy
AgentCore deploy is two-phase:
1. **Phase A**: Deploy runtimes + memory + credentials (agentcore deploy -y)
2. **Phase B**: After getting runtime URLs from `agentcore status`, add gateway + policy engine targets with actual endpoint URLs, then redeploy

This matches the TravelPlanner reference pattern — gateway targets need real endpoint URLs.

## Next Steps
- [ ] Run `agentcore deploy -y` from code-server (Phase A — runtimes only)
- [ ] Run `agentcore status` to get runtime URLs
- [ ] Add gateway + policy engine with real endpoint URLs
- [ ] Redeploy with gateway (Phase B)
- [ ] Update orchestrator agent.py with actual gateway URL + client secret
- [ ] Test in AgentCore Playground
