# Implementation Plan: Workshop4 All-Phases Refactoring (Grouped by Phase)

## Overview

Refactor workshop4 phases 1, 2, and 3 to achieve singular naming (`course_reviews` → `course_review`) and consistent directory structure (`student_services/` flat package). Tasks are grouped by deployment phase so each phase can be fully working before touching the next.

All deployments run on the Ubuntu code-server. Code changes happen on this Windows machine.

## Tasks

- [ ] 1. Phase 1 — Infrastructure + Code (get fully working first)

  - [ ] 1.1 Update Phase 1 CloudFormation (DynamoDB + SSM + Output singular rename)
    - File: `workshop4/phase1/cloudformation/student-services-infra.yaml`
    - Rename logical ID `CourseReviewsTable` → `CourseReviewTable`
    - Change physical table name `course_reviews` → `course_review`
    - Rename logical ID `SSMCourseReviewsTable` → `SSMCourseReviewTable`
    - Change SSM path `/student-services/course-reviews-table` → `/student-services/course-review-table`
    - Change SSM value from `!Ref CourseReviewsTable` → `!Ref CourseReviewTable`
    - Rename output key `CourseReviewsTableName` → `CourseReviewTableName`
    - Change export name `${AWS::StackName}-CourseReviewsTable` → `${AWS::StackName}-CourseReviewTable`
    - ⚠️ DESTRUCTIVE: DynamoDB table will be deleted and recreated — re-seed after deploy
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ] 1.2 Update seed data script to use new output key
    - File: `workshop4/phase1/scripts/populate_seed_data.py`
    - In `required_keys` list: change `"CourseReviewsTableName"` → `"CourseReviewTableName"`
    - In variable assignment: change `reviews_table = outputs["CourseReviewsTableName"]` → `outputs["CourseReviewTableName"]`
    - Data file `course_reviews.csv` and S3 key `dynamodb/course_reviews.csv` remain unchanged
    - _Requirements: 1.4, 9.1, 9.2, 9.3_

  - [ ] 1.3 Update Phase 1 config.py (singular table function)
    - File: `workshop4/phase1/streamlit_app/config.py`
    - Rename function `get_course_reviews_table` → `get_course_review_table`
    - Change SSM key from `"course-reviews-table"` → `"course-review-table"`
    - Change env var from `"COURSE_REVIEWS_TABLE"` → `"COURSE_REVIEW_TABLE"`
    - Change default from `"course_reviews"` → `"course_review"`
    - Update `get_all_config_values()` to call `get_course_review_table()` and use key `"course_review_table"`
    - _Requirements: 8.1_

  - [ ] 1.4 Create Phase 1 `student_services/` package and move agent files
    - Create directory: `workshop4/phase1/streamlit_app/student_services/`
    - Create `student_services/__init__.py` that imports and re-exports `create_orchestrator`
    - Move `course_review_agent/agent.py` → `student_services/course_review_agent.py`
    - Move `course_registration_agent/agent.py` → `student_services/course_registration_agent.py`
    - Move `loan_application_agent/agent.py` → `student_services/loan_application_agent.py`
    - Move `math_teaching_agent/agent.py` → `student_services/math_teaching_agent.py`
    - Move `student_services_agent/agent.py` → `student_services/student_services_agent.py`
    - In each moved file: remove `sys.path` hacks, update imports to use `from config import ...` and `from shared.model_factory import ...`
    - In `course_review_agent.py`: change `get_course_reviews_table` → `get_course_review_table`
    - Delete old subdirectories: `course_review_agent/`, `course_registration_agent/`, `loan_application_agent/`, `math_teaching_agent/`, `student_services_agent/`
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.7, 8.4_

  - [ ] 1.5 Update Phase 1 app.py imports
    - File: `workshop4/phase1/streamlit_app/app.py`
    - Change `from student_services_agent.agent import create_orchestrator` → `from student_services.student_services_agent import create_orchestrator`
    - _Requirements: 5.5, 5.6_

- [ ] 2. Checkpoint — Phase 1 working
  - Deploy CloudFormation stack update on code-server: `aws cloudformation deploy --template-file student-services-infra.yaml --stack-name student-services-infra --capabilities CAPABILITY_NAMED_IAM`
  - Re-seed data on code-server: `python scripts/populate_seed_data.py --region us-west-2`
  - Verify app starts without import errors: `python -c "import sys; sys.path.insert(0, '.'); from student_services.student_services_agent import create_orchestrator"`
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 3. Phase 2 — Code Changes (get fully working second)

  - [ ] 3.1 Update Phase 2 config.py (singular table function)
    - File: `workshop4/phase2/deploy-streamlit-app/docker_app/config.py`
    - Rename function `get_course_reviews_table` → `get_course_review_table`
    - Change SSM key from `"course-reviews-table"` → `"course-review-table"`
    - Change env var from `"COURSE_REVIEWS_TABLE"` → `"COURSE_REVIEW_TABLE"`
    - Change default from `"course_reviews"` → `"course_review"`
    - Update `get_all_config_values()` to call `get_course_review_table()`
    - _Requirements: 8.2_

  - [ ] 3.2 Create Phase 2 `student_services/` package and move agent files
    - Create directory: `workshop4/phase2/deploy-streamlit-app/docker_app/student_services/`
    - Create `student_services/__init__.py` that imports and re-exports `create_orchestrator` and specialist creation functions
    - Move `course_review_agent/agent.py` → `student_services/course_review_agent.py`
    - Move `course_registration_agent/agent.py` → `student_services/course_registration_agent.py`
    - Move `loan_application_agent/agent.py` → `student_services/loan_application_agent.py`
    - Move `math_teaching_agent/agent.py` → `student_services/math_teaching_agent.py`
    - Move `student_services_agent/agent.py` → `student_services/student_services_agent.py`
    - In each moved file: remove `sys.path` hacks, update imports to use flat package paths (`from config import ...`, `from shared.model_factory import ...`)
    - In `course_review_agent.py`: change `get_course_reviews_table` → `get_course_review_table`
    - Update intra-agent imports to use `student_services.<module_name>` instead of `<agent_name>.agent`
    - Delete old subdirectories: `course_review_agent/`, `course_registration_agent/`, `loan_application_agent/`, `math_teaching_agent/`, `student_services_agent/`
    - `shared/` and `utils/` directories remain at `docker_app/` level unchanged
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.7, 8.5_

  - [ ] 3.3 Update Phase 2 app.py imports
    - File: `workshop4/phase2/deploy-streamlit-app/docker_app/app.py`
    - Change `from student_services_agent.agent import create_orchestrator` → `from student_services.student_services_agent import create_orchestrator`
    - _Requirements: 6.6, 6.8_

- [ ] 4. Checkpoint — Phase 2 working
  - Verify app starts without import errors: `python -c "import sys; sys.path.insert(0, '.'); from student_services.student_services_agent import create_orchestrator"`
  - Docker build on code-server: `docker build -t student-services-phase2 .`
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Phase 3 — Infrastructure + Modularization (last)

  - [ ] 5.1 Update Phase 3 CloudFormation (Cognito + IAM singular naming)
    - File: `workshop4/phase3/cloudformation/student-services-agentcore-infra.yaml`
    - Rename all `CourseReviews*` logical IDs → `CourseReview*` (ExecutionRole, UserPool, UserPoolDomain, ResourceServer, AppClient)
    - Change role name: `CourseReviews-execution-role` → `CourseReview-execution-role`
    - Change pool name: `course-reviews-user-pool` → `course-review-user-pool`
    - Change domain: `course-reviews-${AccountId}` → `course-review-${AccountId}`
    - Change resource server identifier: `course-reviews` → `course-review`
    - Change scope: `course-reviews/access` → `course-review/access`
    - Rename all corresponding output keys and export names from `CourseReviews*` → `CourseReview*`
    - ⚠️ DESTRUCTIVE: Cognito pools will be deleted and recreated — capture new pool IDs from stack outputs
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [ ] 5.2 Rename Phase 3 MCP server directory + update server.py
    - Rename directory: `workshop4/phase3/studentservices/course_reviews/` → `workshop4/phase3/studentservices/course_review/`
    - In `course_review/server.py`: change env var `COURSE_REVIEWS_TABLE` → `COURSE_REVIEW_TABLE`
    - In `course_review/server.py`: change default value `"course_reviews"` → `"course_review"`
    - Tool name `get_course_reviews` remains unchanged (public API)
    - _Requirements: 4.1, 4.5, 1.5, 8.3_

  - [ ] 5.3 Update agentcore.json (runtime/credential/gateway singular naming + codeLocation + entrypoint)
    - File: `workshop4/phase3/studentservices/agentcore/agentcore.json`
    - Runtime: rename `CourseReviewsMcp` → `CourseReviewMcp`
    - Runtime: change `executionRoleArn` to reference `CourseReview-execution-role`
    - Runtime: change `codeLocation` from `./course_reviews/` → `./course_review/`
    - Runtime: change `allowedScopes` from `course-reviews/access` → `course-review/access`
    - Runtime: update `discoveryUrl` with new Cognito pool ID (from stack output after deploy)
    - Runtime: update `allowedClients` with new app client ID (from stack output after deploy)
    - Credential: rename `CourseReviewsMcp-oauth` → `CourseReviewMcp-oauth`
    - Credential: change `scopes` from `course-reviews/access` → `course-review/access`
    - Credential: update `discoveryUrl` with new Cognito pool ID
    - Gateway target: rename `coursereviews` → `coursereview`
    - Gateway target: change `credentialName` from `CourseReviewsMcp-oauth` → `CourseReviewMcp-oauth`
    - Gateway target: endpoint URL will be updated after redeploy (contains runtime ARN)
    - StudentServicesAgent runtime: change `entrypoint` from `agent.py` → `student_services_agent.py`
    - All other runtimes/credentials/targets remain unchanged
    - _Requirements: 2.7, 2.8, 2.9, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 4.2, 4.3, 4.4, 7.7_

  - [ ] 5.4 Split monolithic agent.py into modular files
    - Create 5 agent files + calculator.py + __init__.py in `workshop4/phase3/studentservices/student_services/`:
    - `student_services_agent.py`: BedrockAgentCoreApp entrypoint, ORCHESTRATOR_SYSTEM_PROMPT, get_model_config, OAuth2 get_oauth_token with caching, get_mcp_client factory, gateway config constants, invoke entrypoint, `if __name__` block. Import specialist tools from siblings: `from .course_review_agent import course_review_agent` etc.
    - `course_review_agent.py`: COURSE_REVIEW_AGENT_PROMPT, `@tool course_review_agent()`. Import `get_model_config, get_mcp_client` from `.student_services_agent`.
    - `course_registration_agent.py`: COURSE_REGISTRATION_AGENT_PROMPT, `@tool course_registration_agent()`. Import `get_model_config, get_mcp_client` from `.student_services_agent`.
    - `loan_application_agent.py`: LOAN_APPLICATION_AGENT_PROMPT, `@tool loan_application_agent()`. Import `get_model_config, get_mcp_client` from `.student_services_agent`.
    - `math_teaching_agent.py`: MATH_TEACHING_AGENT_PROMPT, `@tool math_teaching_agent()`. Import `get_model_config` from `.student_services_agent` and `calculator` from `.calculator`.
    - `calculator.py`: ALLOWED_NAMES dict, `@tool calculator()` function.
    - `__init__.py`: Empty file (enables package imports for relative imports).
    - _Requirements: 7.1, 7.3, 7.4, 7.5, 7.6, 7.8_

  - [ ] 5.5 Delete old monolithic agent.py
    - Delete file: `workshop4/phase3/studentservices/student_services/agent.py`
    - _Requirements: 7.2_

- [ ] 6. Checkpoint — Phase 3 working
  - Deploy Phase 3 CloudFormation on code-server: `aws cloudformation deploy --template-file student-services-agentcore-infra.yaml --stack-name student-services-agentcore-infra --capabilities CAPABILITY_NAMED_IAM`
  - Capture new Cognito pool IDs and client IDs from stack outputs
  - Update agentcore.json discoveryUrl and allowedClients with new values
  - Re-register credentials on code-server: `bash register-credentials.sh`
  - Deploy AgentCore on code-server: `agentcore deploy -y`
  - Verify: `agentcore invoke "What courses are available?"`
  - Ensure all tests pass, ask the user if questions arise.
  - **Rollback if Phase 3 deploy fails**: Revert CloudFormation template, `aws cloudformation deploy` to restore old pools, revert agentcore.json, `agentcore deploy -y`

## Notes

- No property-based tests — this is a refactoring of infrastructure config, directory structure, and import paths
- DynamoDB table rename (Phase 1) is destructive — data must be re-seeded after stack update
- Cognito pool rename (Phase 3) creates new pool IDs — must capture from stack outputs and update agentcore.json
- All deployments happen on Ubuntu code-server (Docker build requirements + better performance)
- Code changes happen on this Windows machine
- The MCP tool name `get_course_reviews` and data file `course_reviews.csv` intentionally retain plural naming
- Each phase is independently verifiable before proceeding to the next

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "1.3"] },
    { "id": 2, "tasks": ["1.4"] },
    { "id": 3, "tasks": ["1.5"] },
    { "id": 4, "tasks": ["3.1"] },
    { "id": 5, "tasks": ["3.2"] },
    { "id": 6, "tasks": ["3.3"] },
    { "id": 7, "tasks": ["5.1", "5.2"] },
    { "id": 8, "tasks": ["5.3"] },
    { "id": 9, "tasks": ["5.4"] },
    { "id": 10, "tasks": ["5.5"] }
  ]
}
```
