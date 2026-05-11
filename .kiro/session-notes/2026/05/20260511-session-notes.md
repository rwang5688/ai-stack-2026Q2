# Session Notes - May 11, 2026

## Session Overview
Implemented all Phase 1 code: shared utilities, specialist agents, orchestrator, and Streamlit UI. All files parse cleanly, imports resolve, model factory validates correctly, config fetches SSM parameters, and orchestrator creates with all 4 specialist tools registered.

## Key Accomplishments
- Verified infrastructure is healthy (S3, DynamoDB, Bedrock KB all confirmed populated)
- Implemented Task 3: Shared utilities
  - `shared/cross_platform_tools.py` — platform detection + calculator tool wrapper
  - `shared/model_factory.py` — Bedrock/SageMaker model creation with validation
  - `streamlit_app/config.py` — SSM-backed config with env var override and lru_cache
- Implemented Task 5: Specialist agents
  - `course_review_agent/agent.py` — RAG (Bedrock KB + DynamoDB reviews)
  - `course_registration_agent/agent.py` — DynamoDB write with validation
  - `loan_application_agent/agent.py` — SageMaker XGBoost invocation with error sanitization
  - `math_teaching_agent/agent.py` — Calculator tools with step-by-step teaching
- Implemented Task 7: Orchestrator and Streamlit UI
  - `student_services_agent/agent.py` — Orchestrator routing to 4 specialists
  - `streamlit_app/app.py` — Full Streamlit chat UI with model selection, debug sidebar, cache clear
- Tested end-to-end on Windows (Nova 2 Lite) and Ubuntu Linux (Claude Sonnet 4.6)
- Fixed XGBoost endpoint ARN issue (invoke_endpoint requires name, not ARN)
- Fixed SageMaker import issue (conditional import for cross-version compatibility)
- Updated requirements.txt to pin strands-agents>=1.0.0
- Reorganized session notes into yyyy/mm/ structure
- Reorganized specs into module-based structure
- Updated MCP servers (aws-cdk → aws-iac-mcp-server, disabled deprecated diagram server)

## Verification Results
- All 9 Python files pass syntax check (AST parse)
- `strands-agents` v1.34.1, `strands-agents-tools` v0.3.0, `streamlit` v1.56.0, `boto3` v1.42.87 installed
- `cross_platform_tools`: Detects Windows, calculator tool available
- `model_factory`: Creates BedrockModel, validates provider/model_id/temperature correctly
- `config.py`: Successfully fetches all 10 SSM parameters from `/student-services/`
- Orchestrator: Creates with 4 tools registered (`course_review_assistant`, `course_registration_assistant`, `loan_offering_assistant`, `math_assistant`)

## Config Values Confirmed from SSM
- model_provider: bedrock
- model_id: us.amazon.nova-2-lite-v1:0
- temperature: 0.3
- aws_region: us-west-2
- knowledge_base_id: NCGF0S9LJR
- data_source_id: ZCGGBFFO0X
- xgboost_endpoint: arn:aws:sagemaker:us-west-2:149057604171:endpoint/xgboost-serverless-ep2026-05-10-06-08-28
- course_registration_table: course_registration
- course_reviews_table: course_reviews

## Notes
- `strands-agents` is v1.34.1 (not 0.1.x as in requirements.txt) — may need to update pinning
- XGBoost endpoint stored as full ARN — `invoke_endpoint` accepts ARNs so this is fine
- Optional tasks (3.3, 5.4, 7.2) skipped for now — property tests can be added later

## Decisions Made
- **Routing status in UI**: Each specialist `@tool` function prefixes its return value with `[Agent Name]` (e.g., `[Course Review Agent]`). Callback handlers and LLM system prompt instructions were too unreliable — callbacks hit Streamlit threading issues, and LLMs inconsistently follow formatting instructions. A simple string prefix in the tool return is deterministic and zero-complexity.
- **University naming**: Changed from "University of Octank" to "Any University (any.edu)" per AWS workshop naming conventions. Updated PDF, re-uploaded to S3, re-ingested KB.
- **XGBoost endpoint ARN fix**: `invoke_endpoint` requires the endpoint name (max 63 chars), not the full ARN. Added extraction logic: `endpoint.split("/")[-1]` when value starts with `arn:`.

## Next Steps
- [ ] Task 9: Create README documentation (deferred — can do in a future session)
- [x] Phase 1 implementation complete and tested on both platforms
- [ ] Phase 2: Deploy to ECS Fargate
- [ ] Phase 3: AgentCore microservices
