# Implementation Plan: Workshop 4 Phase 3 — Agentic Applications (SSM Model Config + Thin Clients)

## Overview

This plan implements SSM-based model configuration across all 5 AgentCore runtimes, then builds a local Streamlit thin client, and finally creates the production ECS Fargate deployment with Cognito auth. The SSM approach centralizes model selection in a single parameter (`/student-services/model-id`) — change once, all runtimes pick it up on next session creation. Tasks are ordered: backend changes → local thin client → production web app.

## Tasks

- [x] 1. Backend: Shared config module and runtime modifications
  - [x] 1.1 Create shared config module `workshop4/phase3/studentservices/shared/__init__.py` and `workshop4/phase3/studentservices/shared/config.py`
    - Create `shared/__init__.py` with module docstring
    - Create `shared/config.py` with `get_model_config()` function
    - Resolution order: `MODEL_ID` env var → SSM `/student-services/model-id` → hardcoded default `us.amazon.nova-2-lite-v1:0`
    - Return dict with keys: `model_id`, `region` (always `us-west-2`), `max_tokens` (always `4096`)
    - Use `boto3.client("ssm", region_name="us-west-2")` with `get_parameter`
    - Catch all exceptions from SSM and fall back gracefully
    - NOTE: shared/ module NOT used by deployed runtimes (CodeZip limitation). Function inlined in each agent.py instead.
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [x] 1.2 Modify `workshop4/phase3/studentservices/student_services/agent.py` to use `get_model_config`
    - Inlined `get_model_config()` directly in agent.py (CodeZip only packages codeLocation directory)
    - Replace hardcoded `BedrockModel(model_id="us.amazon.nova-2-lite-v1:0", ...)` with `get_model_config()` dict values
    - Keep cache key as `{session_id}/{user_id}` (model is infrastructure config, not user identity)
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 1.3 Modify `workshop4/phase3/studentservices/course_registration/agent.py` to use `get_model_config`
    - Inlined `get_model_config()` directly in agent.py
    - Replace hardcoded `BedrockModel(model_id="us.amazon.nova-2-lite-v1:0", ...)` in `course_registration_assistant()` with `get_model_config()` dict values
    - _Requirements: 3.1, 3.5_

  - [x] 1.4 Modify `workshop4/phase3/studentservices/course_review/agent.py` to use `get_model_config`
    - Inlined `get_model_config()` directly in agent.py
    - Replace hardcoded `BedrockModel(model_id="us.amazon.nova-2-lite-v1:0", ...)` in `course_review_assistant()` with `get_model_config()` dict values
    - _Requirements: 3.2, 3.5_

  - [x] 1.5 Modify `workshop4/phase3/studentservices/loan_application/agent.py` to use `get_model_config`
    - Inlined `get_model_config()` directly in agent.py
    - Replace hardcoded `BedrockModel(model_id="us.amazon.nova-2-lite-v1:0", ...)` in the MCP tool function with `get_model_config()` dict values
    - _Requirements: 3.3, 3.5_

  - [x] 1.6 Modify `workshop4/phase3/studentservices/math_teaching/agent.py` to use `get_model_config`
    - Inlined `get_model_config()` directly in agent.py
    - Added `boto3` to math_teaching/requirements.txt
    - Replace hardcoded `BedrockModel(model_id="us.amazon.nova-2-lite-v1:0", ...)` in the MCP tool function with `get_model_config()` dict values
    - _Requirements: 3.4, 3.5_

  - [x] 1.7 Add `ssm:GetParameter` to `AgentCoreBasePolicy` in `workshop4/phase3/cloudformation/student-services-agentcore-infra.yaml`
    - Add new Statement with Sid `SSMParameterAccess`
    - Action: `ssm:GetParameter`
    - Resource: `arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/student-services/*`
    - CloudFormation stack deployed successfully
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ]* 1.8 Write property tests for shared config module
    - **Property 1: Config Structure Invariant** — for any SSM value (or SSM failure), `get_model_config()` returns dict with exactly `model_id`, `region`, `max_tokens` where region is always `us-west-2` and max_tokens is always `4096`
    - **Property 2: SSM Freshness (No Caching)** — consecutive calls with SSM value change between them return the updated model_id
    - **Validates: Requirements 1.1, 1.2, 1.3, 8.1, 8.3**

- [x] 2. Checkpoint — Verify backend changes
  - CloudFormation stack deployed successfully (ssm:GetParameter added)
  - SSM parameter `/student-services/model-id` already exists from Phase 1
  - `agentcore deploy -y` completed — all 5 runtimes READY, credentials Deployed, gateway with 4 targets

- [x] 3. Local thin client: Create `workshop4/phase3/streamlit_app/`
  - [x] 3.1 Create `workshop4/phase3/streamlit_app/agent_client.py`
    - Implement `get_config_errors()` returning list of missing env var names (checks `STUDENT_SERVICES_AGENT_URL`)
    - Implement `invoke(prompt: str) -> str` with SigV4 signing (service `bedrock-agentcore`, region from boto3 session or `us-west-2`)
    - Use `boto3.Session()` for credentials, `httpx` for HTTP POST, 120s timeout
    - Send body `{"prompt": prompt}` — no model_id in payload
    - Extract `response` field from JSON reply on 200, raise `RuntimeError` otherwise
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.8, 5.9_

  - [x] 3.2 Create `workshop4/phase3/streamlit_app/app.py`
    - Streamlit chat UI with page title "Student Services Agent" and 🎓 icon
    - Validate env vars on startup via `agent_client.get_config_errors()`, display error and `st.stop()` if missing
    - Sidebar: read-only model ID display (read from SSM `/student-services/model-id`), Clear Chat button, sample prompts
    - Chat input sends prompt to `agent_client.invoke(prompt)`
    - Display spinner "Thinking..." during request, show errors in chat area without crashing
    - Maintain chat history in `st.session_state.messages`
    - _Requirements: 5.1, 5.4, 5.6, 5.7, 5.8, 5.9, 5.10_

  - [x] 3.3 Create `workshop4/phase3/streamlit_app/requirements.txt`
    - Include: `boto3`, `httpx`, `streamlit` (alphabetical order)
    - _Requirements: 5.10_

  - [x] 3.4 Create `workshop4/phase3/streamlit_app/run.ps1` and `workshop4/phase3/streamlit_app/run.sh`
    - PowerShell script with comment about required `STUDENT_SERVICES_AGENT_URL` env var, runs `streamlit run app.py`
    - Bash script with `#!/bin/bash`, same pattern
    - _Requirements: 5.10_

  - [ ]* 3.5 Write property tests for agent_client module
    - **Property 5: Client Request Serialization** — for any non-empty string prompt, `invoke(prompt)` sends HTTP POST with body exactly `json.dumps({"prompt": prompt})` signed with SigV4 service `bedrock-agentcore`
    - **Validates: Requirements 5.2, 5.3**

- [x] 4. Checkpoint — Verify local thin client
  - Tested locally on Windows — all 4 specialists working (course review, registration, loan prediction, math)
  - Model selection displayed as read-only with SSM explanation
  - Loan CSV prompt passing through correctly with system prompt fix

- [x] 5. Production web app: Create `workshop4/phase3/deploy-streamlit-app/docker_app/`
  - [x] 5.1 Create `workshop4/phase3/deploy-streamlit-app/docker_app/config_file.py`
    - Define `Config` class with `STACK_NAME = "StudentServicesPhase3"`, `SECRETS_MANAGER_ID`, `CUSTOM_HEADER_VALUE`, VPC/ALB/ECS naming constants, `AWS_REGION = "us-west-2"`
    - _Requirements: 6.9, 6.11_

  - [x] 5.2 Create `workshop4/phase3/deploy-streamlit-app/docker_app/agent_client.py`
    - Same SigV4 HTTP client implementation as `streamlit_app/agent_client.py`
    - Reads `STUDENT_SERVICES_AGENT_URL` from environment
    - _Requirements: 7.2, 7.4_

  - [x] 5.3 Create `workshop4/phase3/deploy-streamlit-app/docker_app/cognito_client.py`
    - Read Cognito credentials from Secrets Manager using `Config.SECRETS_MANAGER_ID`
    - Provide login/logout/session management for Streamlit app
    - _Requirements: 7.3_

  - [x] 5.4 Create `workshop4/phase3/deploy-streamlit-app/docker_app/app.py`
    - Cognito authentication gate — show login form when not authenticated
    - After login, same chat interface as local version (no model_id in payload, read-only model display from SSM)
    - Display username + Logout button in sidebar when authenticated
    - _Requirements: 7.1, 7.3, 7.4_

  - [x] 5.5 Create `workshop4/phase3/deploy-streamlit-app/docker_app/requirements.txt`
    - Include: `boto3`, `httpx`, `streamlit` (alphabetical order)
    - _Requirements: 7.5_

  - [x] 5.6 Create `workshop4/phase3/deploy-streamlit-app/docker_app/Dockerfile`
    - Base image: `python:3.13-slim`
    - Install requirements, copy app files, expose port 8501
    - CMD: `streamlit run app.py --server.port=8501 --server.address=0.0.0.0`
    - _Requirements: 7.1, 7.5, 7.6_

- [x] 6. Production web app: Create CDK stack at `workshop4/phase3/deploy-streamlit-app/`
  - [x] 6.1 Create `workshop4/phase3/deploy-streamlit-app/cdk/__init__.py` and `workshop4/phase3/deploy-streamlit-app/cdk/app.py`
    - Empty `__init__.py` for Python package
    - `app.py`: CDK app entry point, instantiate `CdkStack` with `"StudentServicesPhase3"`
    - _Requirements: 6.11_

  - [x] 6.2 Create `workshop4/phase3/deploy-streamlit-app/cdk/cdk_stack.py`
    - Cognito User Pool + Client + Secrets Manager secret
    - VPC (10.0.0.0/16, 2 AZs, 1 NAT), ALB SG, ECS SG (port 8501 from ALB only)
    - ECS Cluster + Fargate task (ARM64, 256 CPU, 512 MiB), container with `STUDENT_SERVICES_AGENT_URL` env var from CDK context
    - Internet-facing ALB with listener: custom header match → ECS target, default → 403
    - CloudFront distribution with ALB origin, custom header injection, HTTPS redirect, caching disabled
    - IAM policy: `bedrock-agentcore:InvokeAgentRuntime` on `*`, `ssm:GetParameter` + `ssm:GetParametersByPath` on `/student-services/*`
    - Grant Secrets Manager read to task role
    - CfnOutputs: `CloudFrontDistributionURL`, `CognitoPoolId`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10, 6.11_

  - [x] 6.3 Create `workshop4/phase3/deploy-streamlit-app/cdk.json` and `workshop4/phase3/deploy-streamlit-app/requirements.txt`
    - `cdk.json`: `{"app": "python3 cdk/app.py"}`
    - `requirements.txt`: `aws-cdk-lib>=2.100.0`, `constructs>=10.0.0`
    - _Requirements: 6.11_

- [x] 7. Documentation: Update `workshop4/phase3/README.md`
  - Added "Why No Dynamic Model Selection?" section explaining multi-hop propagation difficulty
  - Documented SSM "one model everywhere" pattern with `aws ssm put-parameter` command
  - Documented local thin client steps (run.sh / run.ps1)
  - Documented production web app deployment (deploy-streamlit-app.sh)
  - Reorganized Testing section: Runtime Playground → Local thin client → Deploy web app → Test web app
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 8. Final checkpoint — Deploy and verify
  - Phase 3 web app deployed to ECS Fargate via `deploy-streamlit-app.sh`
  - Cognito user created, login working
  - All 4 specialists tested end-to-end through the web app (loan prediction confirmed)
  - All phases (1, 2, 3) working with loan CSV passthrough fix

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design document
- **Manual execution required**:
  - `aws cloudformation deploy ...` (task 2) — updates IAM policy for SSM access
  - `agentcore deploy -y` (task 2) — redeploys runtimes with shared config module
  - `streamlit run app.py` (task 4) — local testing
  - `cdk deploy` (task 8) — production deployment from code-server (requires Docker)
- The CDK stack follows the same pattern as Phase 2 (`workshop4/phase2/deploy-streamlit-app/cdk/cdk_stack.py`) with updated stack name and IAM policy
- `agent_client.py` is duplicated between local and production apps (same implementation, separate files for independent deployment)
- Model is NOT in the request payload — it's system-wide infrastructure config read from SSM at agent creation time

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.7"] },
    { "id": 1, "tasks": ["1.2", "1.3", "1.4", "1.5", "1.6"] },
    { "id": 2, "tasks": ["1.8"] },
    { "id": 3, "tasks": ["3.1", "3.3", "3.4"] },
    { "id": 4, "tasks": ["3.2", "3.5"] },
    { "id": 5, "tasks": ["5.1", "5.5", "5.6"] },
    { "id": 6, "tasks": ["5.2", "5.3", "6.1", "6.3"] },
    { "id": 7, "tasks": ["5.4", "6.2"] }
  ]
}
```
