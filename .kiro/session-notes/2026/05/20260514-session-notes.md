# Session Notes - May 14, 2026

## Session Overview
Created complete spec for Workshop 4 Phase 3 thin client applications (local Streamlit + ECS Fargate web deployment). Key insight: added dynamic model selection to the AgentCore runtime — a feature that was missed during the backend build yesterday.

## Key Accomplishments
- Created full spec at `.kiro/specs/workshop4/workshop4-phase3-agentic-applications/`
  - requirements.md (13 requirements covering runtime change, thin clients, CDK stack)
  - design.md (5 components, 6 correctness properties, architecture diagram)
  - tasks.md (7 top-level tasks, 16 sub-tasks, ordered: backend → local → production)
- Updated `workshop4/phase3/README.md` test prompts to show JSON payload format with optional `model_id` field (alphabetical key order)
- Listed all 12 test combinations (6 prompts × 2 models)

## Key Decisions
- **Model selection in thin client UI** — Yes, include it. Requires modifying the runtime's `invoke` entrypoint to accept `model_id` from the payload
- **Allowed models**: `us.amazon.nova-2-lite-v1:0` (default), `us.anthropic.claude-sonnet-4-6`
- **Agent cache key change**: `{session_id}/{user_id}` → `{session_id}/{user_id}/{model_id}` so switching models creates a fresh Agent instance
- **Execution order**: Backend changes first → local thin client → production web app (cautious, incremental approach)
- **CDK stack name**: `StudentServicesPhase3` (following Phase 2 pattern)
- **No routing display in thin client** — runtime doesn't expose routing metadata in its response payload

## Issues & Resolutions
- **Issue**: BedrockAgentCoreApp strips unknown payload keys — would model_id be lost?
  - **Resolution**: Confirmed that the `payload` dict IS passed intact to the entrypoint function. The stripping only applies to what AgentCore forwards to the agent itself, not what the entrypoint receives. So `payload.get("model_id")` works fine.
- **Issue**: Model selection was hardcoded in runtime — costly oversight for production
  - **Resolution**: Adding ALLOWED_MODELS validation + dynamic model_id in the entrypoint. This is a backend change that requires `agentcore deploy -y` after modification.

## Architecture Reminder
```
Thin Client ──(SigV4 POST {"model_id": "...", "prompt": "..."})──→ StudentServicesAgent Runtime
                                                                          │
                                                                          ↓
                                                                    AgentCore Gateway → MCP Specialists
```

## Next Steps
- [ ] Checkpoint: zip specs + README changes, upload to code-server, commit/push
- [ ] Execute Task 1.1: Modify `student_services/agent.py` to add model selection
- [ ] Execute Task 1.2: Write property tests for model validation
- [ ] Redeploy runtime: `agentcore deploy -y` (manual, from Windows PC)
- [ ] Test in Runtime Playground with model_id payloads
- [ ] Execute Task 3: Build local thin client (streamlit_app/)
- [ ] Execute Tasks 5-6: Build production web app (deploy-streamlit-app/)
- [ ] Deploy CDK stack from code-server (requires Docker)

## Resources
- Spec: `.kiro/specs/workshop4/workshop4-phase3-agentic-applications/`
- Reference thin client: `.kiro/references/agentcore-workshop/streamlit_app/`
- Reference web deploy: `.kiro/references/agentcore-workshop/deploy-streamlit-app/`
- Phase 2 CDK reference: `workshop4/phase2/deploy-streamlit-app/cdk/cdk_stack.py`
