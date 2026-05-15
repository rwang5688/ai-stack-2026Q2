# Implementation Plan: Workshop 4 Phase 3 — Agentic Applications (Thin Client + Model Selection)

## Overview

This plan implements runtime model selection in the AgentCore backend, then builds a local Streamlit thin client, and finally creates the production ECS Fargate deployment with Cognito auth. Tasks are ordered: backend changes → local thin client → production web app, ensuring each layer builds on the previous.

## Tasks

- [ ] 1. Backend: Add runtime model selection to agent.py
  - [ ] 1.1 Add ALLOWED_MODELS constant and model validation logic to `workshop4/phase3/studentservices/student_services/agent.py`
    - Add module-level `ALLOWED_MODELS` list containing `us.amazon.nova-2-lite-v1:0` and `us.anthropic.claude-sonnet-4-6`
    - Add `DEFAULT_MODEL_ID = "us.amazon.nova-2-lite-v1:0"`
    - Modify the `invoke` entrypoint to extract `model_id` from payload, validate against ALLOWED_MODELS, return error for invalid models
    - Update cache key from `{session_id}/{user_id}` to `{session_id}/{user_id}/{model_id}`
    - Pass resolved `model_id` to `BedrockModel(model_id=..., region_name="us-west-2", max_tokens=4096)`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [ ]* 1.2 Write property tests for runtime model selection
    - **Property 1: Invalid model rejection** — any string not in ALLOWED_MODELS returns error listing permitted models
    - **Property 2: Default model fallback** — absent/empty/whitespace model_id resolves to default
    - **Property 3: Cache key incorporates model selection** — cache key equals `{session_id}/{user_id}/{model_id}`
    - **Validates: Requirements 1.2, 1.3, 1.4**

- [ ] 2. Checkpoint — Verify backend changes
  - Ensure all tests pass, ask the user if questions arise.
  - User should redeploy the runtime: `agentcore deploy -y` (manual execution required)

- [ ] 3. Local thin client: Create `workshop4/phase3/streamlit_app/`
  - [ ] 3.1 Create `workshop4/phase3/streamlit_app/agent_client.py`
    - Implement `get_config_errors()` returning missing env var names
    - Implement `invoke(prompt, model_id=None)` with SigV4 signing (service `bedrock-agentcore`, region `us-west-2`)
    - Use `boto3.Session()` credentials, `httpx` for HTTP, 120s timeout
    - Include `model_id` in JSON body only when truthy
    - Extract `response` field from JSON reply on 200, raise `RuntimeError` otherwise
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11_

  - [ ] 3.2 Create `workshop4/phase3/streamlit_app/app.py`
    - Streamlit chat UI with page title "Student Services Assistant"
    - Validate env vars on startup via `agent_client.get_config_errors()`
    - Sidebar: model selection dropdown (Nova 2 Lite + Claude Sonnet 4), sample prompts, Clear Chat button
    - Chat input sends prompt + selected model_id to `agent_client.invoke()`
    - Display spinner "Thinking..." during request, show errors via `st.error()`
    - Maintain chat history in `st.session_state.messages`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10_

  - [ ] 3.3 Create `workshop4/phase3/streamlit_app/requirements.txt`
    - Include: `boto3`, `httpx`, `streamlit`
    - _Requirements: 3.10_

  - [ ] 3.4 Create `workshop4/phase3/streamlit_app/run.ps1` and `workshop4/phase3/streamlit_app/run.sh`
    - PowerShell script sets `STUDENT_SERVICES_AGENT_URL` env var and runs `streamlit run app.py`
    - Bash script does the same with `export`
    - Include placeholder URL with comment for user to replace
    - _Requirements: 3.10_

  - [ ]* 3.5 Write property tests for agent_client module
    - **Property 4: Request body construction reflects model_id presence** — truthy model_id includes both keys, falsy includes only prompt
    - **Property 5: Successful response extraction** — HTTP 200 with JSON `{"response": "..."}` returns exact string
    - **Property 6: Error propagation on non-200 status** — non-200 raises RuntimeError with status code and body
    - **Validates: Requirements 2.4, 2.5, 2.6, 2.8**

- [ ] 4. Checkpoint — Verify local thin client
  - Ensure all tests pass, ask the user if questions arise.
  - User should test locally: set env var and run `streamlit run app.py` (manual execution required)

- [ ] 5. Production web app: Create `workshop4/phase3/deploy-streamlit-app/docker_app/`
  - [ ] 5.1 Create `workshop4/phase3/deploy-streamlit-app/docker_app/config_file.py`
    - Define `Config` class with `STACK_NAME`, `CUSTOM_HEADER_VALUE`, `SECRETS_MANAGER_ID`, `DEPLOYMENT_REGION`
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ] 5.2 Create `workshop4/phase3/deploy-streamlit-app/docker_app/agent_client.py`
    - Same implementation as `streamlit_app/agent_client.py` (Component 2 from design)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11_

  - [ ] 5.3 Create `workshop4/phase3/deploy-streamlit-app/docker_app/cognito_client.py`
    - Implement `get_authenticator(secret_id, region)` reading Cognito params from Secrets Manager
    - Return configured `CognitoAuthenticator` instance
    - _Requirements: 4.1, 4.2_

  - [ ] 5.4 Create `workshop4/phase3/deploy-streamlit-app/docker_app/app.py`
    - Cognito authentication gate using `cognito_client.get_authenticator()`
    - Show login form when not authenticated, `st.stop()` to block chat
    - Display username + Logout button in sidebar when authenticated
    - Same chat functionality, model selection, sample prompts as local version
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [ ] 5.5 Create `workshop4/phase3/deploy-streamlit-app/docker_app/requirements.txt`
    - Include: `boto3`, `httpx`, `streamlit`, `streamlit-cognito-auth`
    - _Requirements: 6.4_

  - [ ] 5.6 Create `workshop4/phase3/deploy-streamlit-app/docker_app/Dockerfile`
    - Base image: `python:3.13-slim` with `--platform=linux/arm64`
    - Install requirements, copy app files, expose port 8501
    - Entrypoint: `streamlit run app.py --server.port=8501 --server.address=0.0.0.0`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 6. Production web app: Create CDK stack at `workshop4/phase3/deploy-streamlit-app/`
  - [ ] 6.1 Create `workshop4/phase3/deploy-streamlit-app/cdk/__init__.py`
    - Empty file for Python package
    - _Requirements: 13.1_

  - [ ] 6.2 Create `workshop4/phase3/deploy-streamlit-app/cdk/cdk_stack.py`
    - Cognito User Pool + Client + Secrets Manager secret
    - VPC (10.0.0.0/16, 2 AZs, 1 NAT), ALB SG, ECS SG (port 8501 from ALB only)
    - ECS Cluster + Fargate task (ARM64, 256 CPU, 512 MiB), container with `STUDENT_SERVICES_AGENT_URL` env var from CDK context
    - Internet-facing ALB with listener: custom header match → ECS target, default → 403
    - CloudFront distribution with ALB origin, custom header injection, HTTPS redirect, caching disabled
    - IAM policy: `bedrock-agentcore:InvokeAgentRuntime` on `*`
    - Grant Secrets Manager read to task role
    - CfnOutputs: `CloudFrontDistributionURL`, `CognitoPoolId`
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 10.1, 10.2, 10.3, 10.4, 11.1, 11.2, 12.1, 12.2_

  - [ ] 6.3 Create `workshop4/phase3/deploy-streamlit-app/cdk/app.py`
    - CDK app entry point importing `CdkStack` and `Config`
    - Instantiate stack with `Config.STACK_NAME` and `Config.DEPLOYMENT_REGION`
    - _Requirements: 13.3_

  - [ ] 6.4 Create `workshop4/phase3/deploy-streamlit-app/cdk.json`
    - Set `"app": "python cdk/app.py"`
    - _Requirements: 13.4_

  - [ ] 6.5 Create `workshop4/phase3/deploy-streamlit-app/requirements.txt`
    - Include: `aws-cdk-lib`, `constructs`
    - _Requirements: 13.1_

- [ ] 7. Final checkpoint — Deploy and verify production stack
  - Ensure all tests pass, ask the user if questions arise.
  - User should deploy from code-server (Linux): `cdk deploy -c student_services_agent_url=<RUNTIME_URL>` (manual execution required — requires Docker for container build)
  - After deployment: create Cognito user via AWS Console, access CloudFront URL

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design document
- **Manual execution required**: `agentcore deploy -y` (task 2), `streamlit run app.py` (task 4), `cdk deploy` (task 7) — these cannot be automated by the coding agent
- The CDK stack follows the same pattern as Phase 2 (`workshop4/phase2/deploy-streamlit-app/cdk/cdk_stack.py`) with updated stack name, IAM policy, and agent URL context parameter
- `agent_client.py` is duplicated between local and production apps (same implementation, separate files for independent deployment)

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2"] },
    { "id": 2, "tasks": ["3.1", "3.3", "3.4"] },
    { "id": 3, "tasks": ["3.2", "3.5"] },
    { "id": 4, "tasks": ["5.1"] },
    { "id": 5, "tasks": ["5.2", "5.3", "5.5", "5.6", "6.1", "6.4", "6.5"] },
    { "id": 6, "tasks": ["5.4", "6.2", "6.3"] }
  ]
}
```
