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
- **Model selection in thin client UI** — No dynamic per-request model_id. SSM-only approach.
  - MCP protocol can't propagate model_id through gateway to specialists
  - Dynamic model_id would only affect orchestrator, not specialists = half-baked
  - SSM gives centralized, consistent config across all 5 runtimes
  - New session picks up SSM changes (no redeploy needed)
- **Allowed models**: `us.amazon.nova-2-lite-v1:0` (default), `us.anthropic.claude-sonnet-4-6`
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
- [ ] ~~Checkpoint: zip specs + README changes, upload to code-server, commit/push~~
- [x] Execute Task 1.1–1.7: Backend changes (shared config inlined into all 5 agent.py files)
- [x] Deploy CloudFormation stack update (ssm:GetParameter permission added)
- [x] Redeploy runtimes: `agentcore deploy -y` (from studentservices/ directory) — DONE
- [x] Test in Runtime Playground to confirm SSM model config works — all 4 specialists confirmed
- [x] Execute Task 3: Build local thin client (streamlit_app/) — files created
- [x] Test local thin client — working on Windows, all specialists routing correctly
- [x] Execute Tasks 5-6: Build production web app (deploy-streamlit-app/) — files created
- [ ] Deploy CDK stack from code-server (requires Docker) — IN PROGRESS
- [x] Update README — corrected model config section, added testing order, deploy scripts

## Troubleshooting: AgentCore CLI + TypeScript/Node Issues (2026-05-14)

### Problem: `agentcore deploy -y` fails with `'tsc' is not recognized`
- **Root cause**: `@aws/agentcore@0.13.1` bundles TypeScript as a nested dep but doesn't expose `tsc` globally
- **Fix**: `npm install -g typescript`

### Problem: `tsc` compiles but errors on `moduleResolution=node10` deprecated
- **Root cause**: TypeScript 6.0 (installed globally) treats `moduleResolution: "Node"` as an error
- **Fix**: Either pin `typescript@5.x` globally, or add `"ignoreDeprecations": "6.0"` to `agentcore/cdk/tsconfig.json`
- **Better fix**: The `npm install` in the CDK dir should pull a compatible TS version locally

### Problem: `Cannot find module 'aws-cdk-lib'` and `@aws/agentcore-cdk` errors
- **Root cause**: `agentcore/cdk/node_modules/` missing — the global CLI reinstall regenerated the CDK scaffold without running `npm install`
- **Fix**: `cd agentcore/cdk && npm install`, then retry `agentcore deploy -y`

### Lesson Learned
- Reinstalling `@aws/agentcore` globally can blow away the local CDK scaffold's `node_modules`
- Always check `agentcore/cdk/node_modules` exists before deploying after a CLI upgrade
- The CDK scaffold is TypeScript — it needs its own `npm install` separate from the global CLI

## Design Pivot: Shared Module → Inline
- Originally planned `shared/config.py` importable by all runtimes
- Discovered AgentCore CodeZip only packages the `codeLocation` directory (e.g., `./student_services/`)
- `shared/` as a sibling directory would NOT be included in the zip
- Solution: inline `get_model_config()` directly in each agent.py (~20 lines, acceptable duplication)
- The `shared/` directory still exists but is NOT used by the deployed runtimes

## Resources
- Spec: `.kiro/specs/workshop4/workshop4-phase3-agentic-applications/`
- Reference thin client: `.kiro/references/agentcore-workshop/streamlit_app/`
- Reference web deploy: `.kiro/references/agentcore-workshop/deploy-streamlit-app/`
- Phase 2 CDK reference: `workshop4/phase2/deploy-streamlit-app/cdk/cdk_stack.py`
