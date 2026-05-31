# Session Notes - May 30, 2026

## Session Overview

Created the spec for workshop4 all-phases refactoring — standardizing directory structure across phases 1, 2, 3 and renaming `course_reviews` → `course_review` (singular) in all infrastructure and code.

## Key Accomplishments

- Created spec at `.kiro/specs/workshop4/workshop4-all-phases-refactoring/`
- Generated requirements.md (10 requirements), design.md, and tasks.md
- Iterated on requirements ordering and task grouping based on user feedback

## Decisions Made

### Spec Structure Decisions

1. **Tasks grouped by PHASE, not by requirement category** — Even though singular naming requirements span all phases, tasks are grouped Phase 1 → Phase 2 → Phase 3 so each phase can be fully working before touching the next. Phase 3 singular naming (Cognito, agentcore.json, MCP directory) is deferred until the Phase 3 task group.

2. **Execution order**: Phase 1 (infra + flattening) → Phase 2 (flattening only) → Phase 3 (infra + modularization)

3. **Terminology**:
   - Phase 1 & 2 = "Directory Flattening" (per-agent subdirectories → flat `student_services/` package)
   - Phase 3 = "Agent Modularization" (monolithic `agent.py` → one file per agent)

4. **Singular naming starts with Phase 1 CloudFormation** — DynamoDB table rename (`course_reviews` → `course_review`) and SSM parameter rename happen first because Phase 1 config.py needs the new SSM key.

5. **All deployments on Ubuntu code-server** — Both CDK Streamlit thin client deployment AND AgentCore `agentcore deploy -y` run on Ubuntu for Docker build requirements and better performance.

6. **DynamoDB table rename is destructive** — CloudFormation will DELETE old table and CREATE new one. Seed data must be re-run after stack update.

7. **Cognito pool rename (Phase 3) creates new pool IDs** — Must capture from stack outputs and update agentcore.json discoveryUrl + allowedClients before redeploying AgentCore.

8. **No property-based tests** — This is a refactoring (file moves, IaC config changes, import path updates). Correctness validated via import resolution checks and deployment smoke tests.

9. **Data file `course_reviews.csv` keeps plural name** — Only the DynamoDB table, SSM parameter, config function, env var, and infrastructure names go singular.

10. **MCP tool name `get_course_reviews` keeps plural** — It's a public API describing the action (getting reviews), not the table name.

### Architecture Decisions

- Phase 3 specialist agents import `get_model_config` and `get_mcp_client` from `student_services_agent.py` (circular import resolved at function-call time)
- Phase 1/2 agents import from `config` and `shared.model_factory` (unchanged paths since `streamlit_app/` or `docker_app/` is on sys.path)
- `calculator.py` remains a separate utility module in Phase 3 (imported by `math_teaching_agent.py`)

## Next Steps

- [ ] Checkpoint commit and push from code-server
- [ ] Pull down new files for review
- [ ] Execute tasks Phase 1 → Phase 2 → Phase 3
- [ ] Deploy each phase on Ubuntu code-server after code changes complete
