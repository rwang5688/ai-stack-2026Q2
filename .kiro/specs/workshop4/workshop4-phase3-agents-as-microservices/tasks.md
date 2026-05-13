# Implementation Plan: Phase 3 — AgentCore Microservices Decomposition

## Overview

This plan decomposes the monolithic Student Services application into five independent AgentCore Runtimes communicating through a single AgentCore Gateway. Implementation follows the TravelPlanner reference pattern: CloudFormation identity stack → agentcore.json project configuration → specialist runtimes → orchestrator runtime → Cedar policies → thin Streamlit client with CDK infrastructure. All code is Python targeting `workshop4/phase3/`.

## Tasks

- [ ] 1. Identity Infrastructure and Project Setup
  - [x] 1.1 Create CloudFormation identity stack with 5 Cognito pools
    - Create `workshop4/phase3/cloudformation/student-services-identity.yaml`
    - Define 5 Cognito User Pools (Orchestrator, Course Registration, Course Review, Loan Application, Math Teaching)
    - Each pool gets: UserPoolDomain (`{runtime-name}-{AccountId}`), ResourceServer (identifier = runtime-name, scope = `access`), AppClient (client_credentials grant, generated secret, scope = `{identifier}/access`)
    - Export Stack Outputs: User Pool ID, Discovery URL, App Client ID, Token Endpoint, OAuth Scope for each pool
    - Follow the pattern from `.kiro/references/agentcore-workshop/cloudformation/infra.yaml`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [~] 1.2 Create agentcore.json project configuration
    - Create `workshop4/phase3/agentcore/agentcore.json`
    - Define project name "student-services", schema v1, managedBy field
    - Declare 5 runtimes (Orchestrator HTTP + 4 Specialist HTTP with CUSTOM_JWT auth)
    - Declare 1 memory (SEMANTIC, SUMMARIZATION, USER_PREFERENCE strategies with namespace patterns)
    - Declare 5 OAuth credential providers (one per specialist + one for gateway)
    - Declare 1 gateway "student-services-gateway" with 4 targets, outboundAuth per target, semantic search enabled
    - Declare 1 policy engine with Cedar policies, ENFORCE mode
    - All runtimes: PYTHON_3_13, CodeZip, entrypoint and codeLocation specified
    - Do NOT initialize a separate Git repo — project lives within existing workspace repo
    - Create `workshop4/phase3/agentcore/aws-targets.json` with account and region (us-west-2)
    - Create project-level steering file at `workshop4/phase3/.kiro/steering/student-services-conventions.md` with conventions tailored to Student Services Agent (specialist names, routing rules, AWS services, model config, AgentCore patterns)
    - Follow the pattern from `.kiro/references/agentcore-workshop/travelplanner/agentcore/agentcore.json`
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10_

  - [~] 1.3 Create Cedar policy files
    - Create `workshop4/phase3/agentcore/policies/permit_all_tools.cedar` — baseline permit for all tools on the gateway
    - Create `workshop4/phase3/agentcore/policies/content_safety.cedar` — forbid invocations when `context.input.containsAbusiveLanguage`
    - Create `workshop4/phase3/agentcore/policies/pii_masking.cedar` — mask PII (emails, phone numbers, student IDs) in inputs
    - Follow Cedar syntax from `.kiro/references/agentcore-workshop/travelplanner/policies/`
    - _Requirements: 10.1, 10.2, 10.5_

  - [x] 1.4 Create shared requirements.txt for agentcore runtimes
    - Create `workshop4/phase3/agentcore/requirements.txt` with: strands-agents, bedrock-agentcore, boto3, httpx, mcp
    - _Requirements: 2.8_

- [ ] 2. Specialist Runtimes — Pure Functions and Validation
  - [~] 2.1 Implement Course Registration specialist runtime
    - Create `workshop4/phase3/agentcore/course_registration/agent.py`
    - Implement BedrockAgentCoreApp with `@app.entrypoint` decorator
    - Extract `validate_registration(student_id, course_name, semester) -> list[str]` as a pure function
    - On valid input: generate UUID reg_id, write to DynamoDB `course_registration` table
    - On invalid input: return error listing each invalid field
    - On DynamoDB failure: return generic error without exposing ARNs/table names
    - Adapt logic from `workshop4/phase1/course_registration_agent/agent.py`
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [ ]* 2.2 Write property test: Registration field validation (Property 3)
    - **Property 3: Registration field validation identifies all invalid fields**
    - Use Hypothesis to generate random (str|None|whitespace) tuples for 3 fields
    - Assert: returned list contains exactly the field names that are None/empty/whitespace-only
    - Assert: no false positives (valid fields never appear in error list)
    - **Validates: Requirements 4.2, 4.4**

  - [~] 2.3 Implement Loan Application specialist runtime
    - Create `workshop4/phase3/agentcore/loan_application/agent.py`
    - Implement BedrockAgentCoreApp with `@app.entrypoint` decorator
    - Extract `validate_csv_features(payload: str) -> tuple[bool, int]` as a pure function
    - Extract `interpret_prediction(score: float) -> dict` as a pure function
    - Extract `sanitize_error(msg: str) -> str` as a pure function
    - On valid 59-feature CSV: invoke SageMaker endpoint, return score/label/confidence
    - On invalid count: return error with expected (59) vs actual count
    - On SageMaker failure: sanitize error (redact ARNs, account IDs, endpoint names)
    - Adapt logic from `workshop4/phase1/loan_application_agent/agent.py`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [ ]* 2.4 Write property test: CSV feature count validation (Property 5)
    - **Property 5: CSV feature count validation accepts exactly 59 values**
    - Use Hypothesis to generate random comma-separated strings of varying lengths (0-200 tokens)
    - Assert: returns (True, 59) iff exactly 59 non-empty tokens after split
    - Assert: returns (False, actual_count) for all other counts
    - **Validates: Requirements 6.2, 6.6**

  - [ ]* 2.5 Write property test: Prediction score interpretation (Property 6)
    - **Property 6: Prediction score interpretation is consistent**
    - Use Hypothesis to generate random floats in [0.0, 1.0]
    - Assert: score >= 0.5 → label "Accept", confidence = round(score * 100, 1)
    - Assert: score < 0.5 → label "Reject", confidence = round((1 - score) * 100, 1)
    - Assert: confidence always in [50.0, 100.0]
    - **Validates: Requirements 6.3**

  - [ ]* 2.6 Write property test: Error sanitization (Property 4)
    - **Property 4: Error sanitization redacts all sensitive patterns**
    - Use Hypothesis to generate random strings with injected ARN patterns (`arn:aws:...`), 12-digit account IDs, and `endpoint/...` patterns
    - Assert: output contains no ARN patterns, no 12-digit sequences, no endpoint resource names
    - Assert: non-sensitive portions of the string are preserved
    - **Validates: Requirements 4.5, 6.4**

  - [~] 2.7 Implement Course Review specialist runtime
    - Create `workshop4/phase3/agentcore/course_review/agent.py`
    - Implement BedrockAgentCoreApp with `@app.entrypoint` decorator
    - Implement Bedrock KB retrieval tool (KB ID: NCGF0S9LJR, up to 5 results)
    - Implement DynamoDB query tool with partial-match scan fallback
    - On KB unreachable/empty: return "no matching course catalog information found"
    - On DynamoDB unreachable/empty: return "no reviews available for the requested course"
    - Adapt logic from `workshop4/phase1/course_review_agent/agent.py`
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [~] 2.8 Implement Math Teaching specialist runtime
    - Create `workshop4/phase3/agentcore/math_teaching/agent.py`
    - Implement BedrockAgentCoreApp with `@app.entrypoint` decorator
    - Implement calculator tools for step-by-step math solving
    - On non-math/unsolvable input: return error suggesting user rephrase as specific math question
    - Return step-by-step solutions with intermediate calculations
    - Adapt logic from `workshop4/phase1/math_teaching_agent/agent.py`
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [~] 3. Checkpoint — Specialist runtimes and property tests
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Orchestrator Runtime and Memory Integration
  - [~] 4.1 Implement memory session manager module
    - Create `workshop4/phase3/agentcore/orchestrator/memory/session.py`
    - Implement `get_memory_session_manager(session_id, actor_id)` returning `AgentCoreMemorySessionManager` or None
    - Configure retrieval namespaces: `/users/{actorId}/facts` and `/summaries/{actorId}/{sessionId}`
    - Return None when `MEMORY_STUDENTSERVICESMEMORY_ID` env var is not set
    - Follow pattern from `.kiro/references/agentcore-workshop/travelplanner/travel_agent/memory/session.py`
    - _Requirements: 3.6, 3.7, 9.1, 9.2, 9.5, 9.6_

  - [~] 4.2 Implement Orchestrator runtime with Gateway MCPClient
    - Create `workshop4/phase3/agentcore/orchestrator/agent.py`
    - Implement BedrockAgentCoreApp with `@app.entrypoint` decorator
    - Implement OAuth2 token caching with 300s pre-expiry refresh (`_token_cache` dict pattern)
    - Implement `_OAuthAuth(httpx.Auth)` class for auto-refreshing auth on MCPClient requests
    - Create MCPClient with `streamablehttp_client` transport pointing to Gateway MCP URL
    - Read config from env vars: GATEWAY_MCP_URL, GATEWAY_CLIENT_ID, GATEWAY_CLIENT_SECRET, GATEWAY_TOKEN_ENDPOINT, GATEWAY_SCOPE
    - Implement agent caching keyed by `{session_id}/{user_id}`
    - Integrate memory session manager (conditional on env var)
    - Validate prompt: return error if missing/empty/whitespace-only
    - Route queries to specialists via Gateway tool calls (agents-as-tools)
    - Follow pattern from `.kiro/references/agentcore-workshop/travelplanner/travel_agent/agent.py`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_

  - [ ]* 4.3 Write property test: Missing prompt validation (Property 1)
    - **Property 1: Missing or empty prompt returns error**
    - Use Hypothesis to generate random dicts without "prompt" key, or with empty/whitespace values
    - Assert: response contains "response" field with error message
    - Assert: downstream agent is NOT invoked (mock verification)
    - **Validates: Requirements 3.3**

  - [ ]* 4.4 Write property test: OAuth token cache refresh (Property 2)
    - **Property 2: OAuth token cache respects 300-second pre-expiry refresh**
    - Use Hypothesis to generate random (current_time, expires_at) pairs
    - Assert: if current_time < expires_at → cached token returned (no network call)
    - Assert: if current_time >= expires_at → new token fetched
    - **Validates: Requirements 3.5**

- [~] 5. Checkpoint — Orchestrator and memory integration
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Thin Client and CDK Infrastructure
  - [~] 6.1 Implement thin client agent_client module
    - Create `workshop4/phase3/thin_client/docker_app/agent_client.py`
    - Implement `get_config_errors() -> list[str]` to check STUDENT_SERVICES_AGENT_URL
    - Implement `invoke(prompt: str) -> str` with SigV4-signed HTTP POST
    - Use boto3 SigV4Auth with service "bedrock-agentcore" and region from session
    - Send JSON body `{"prompt": prompt}`, return `response["response"]`
    - Raise RuntimeError on non-200 or network errors
    - Follow pattern from `.kiro/references/agentcore-workshop/deploy-streamlit-app/docker_app/agent_client.py`
    - _Requirements: 11.3, 11.5, 11.7, 11.8_

  - [~] 6.2 Implement thin client Streamlit app
    - Create `workshop4/phase3/thin_client/docker_app/app.py`
    - Implement Streamlit chat UI with Cognito auth (streamlit-cognito-auth pattern)
    - On startup: check `get_config_errors()`, fail with logged error if STUDENT_SERVICES_AGENT_URL missing
    - On message submit: call `agent_client.invoke(prompt)`, display response
    - On timeout/error: display error message, preserve conversation history
    - _Requirements: 11.1, 11.2, 11.4, 11.5, 11.8_

  - [~] 6.3 Create Dockerfile for thin client
    - Create `workshop4/phase3/thin_client/docker_app/Dockerfile`
    - ARM64 base image, install dependencies, expose port 8501
    - _Requirements: 11.1_

  - [~] 6.4 Implement CDK stack for thin client infrastructure
    - Create `workshop4/phase3/thin_client/cdk/cdk_stack.py`
    - VPC with 2 AZs, public + private subnets, NAT gateway
    - ECS Fargate service (ARM64/Graviton) in private subnets
    - ALB with custom header routing condition, 403 default action
    - CloudFront distribution: HTTPS redirect, caching disabled, custom header injection
    - Cognito User Pool + Secrets Manager secret (pool_id, app_client_id, app_client_secret)
    - IAM policy: `bedrock-agentcore:InvokeAgentRuntime`
    - Container env var: STUDENT_SERVICES_AGENT_URL from CDK context
    - Grant task role read access to Secrets Manager secret
    - Follow pattern from `.kiro/references/agentcore-workshop/deploy-streamlit-app/cdk/cdk_stack.py`
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8_

  - [~] 6.5 Create CDK app entry point and config
    - Create `workshop4/phase3/thin_client/cdk/app.py` with CDK App instantiation
    - Create `workshop4/phase3/thin_client/docker_app/config_file.py` with stack name, header value, resource names
    - Create `workshop4/phase3/thin_client/cdk/requirements.txt` with CDK dependencies
    - _Requirements: 12.1_

  - [ ]* 6.6 Write CDK assertion tests for infrastructure validation
    - Create `workshop4/phase3/thin_client/cdk/tests/test_cdk_stack.py`
    - Assert: VPC with 2 AZs, public + private subnets
    - Assert: ECS Fargate service in private subnets (ARM64)
    - Assert: ALB with custom header condition and 403 default
    - Assert: CloudFront with HTTPS redirect, caching disabled
    - Assert: IAM policy with `bedrock-agentcore:InvokeAgentRuntime`
    - Assert: Secrets Manager secret with Cognito parameters
    - Assert: Container environment variable STUDENT_SERVICES_AGENT_URL
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8_

  - [ ]* 6.7 Write CloudFormation template validation tests
    - Create `workshop4/phase3/tests/test_identity_stack.py`
    - Validate: 5 Cognito User Pools declared
    - Validate: 5 User Pool Domains with correct naming pattern
    - Validate: 5 Resource Servers with correct identifiers and scopes
    - Validate: 5 App Clients with client_credentials grant
    - Validate: All required Stack Outputs present with correct format
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 7. Integration Tests
  - [ ]* 7.1 Write integration tests for external service interactions
    - Create `workshop4/phase3/tests/test_integration.py`
    - Test: Cognito token exchange (client_credentials flow returns valid JWT)
    - Test: DynamoDB write (registration record persists correctly)
    - Test: Bedrock KB retrieval (returns results for known course query)
    - Test: SageMaker invocation (returns prediction score for valid 59-feature payload)
    - Test: SigV4 end-to-end (thin client successfully invokes orchestrator)
    - _Requirements: 3.4, 4.3, 5.2, 6.2, 11.3_

- [~] 8. Final Checkpoint — All tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design document (6 properties total)
- Unit tests validate specific examples and edge cases
- All specialist runtimes follow the same BedrockAgentCoreApp entrypoint pattern from the TravelPlanner reference
- Pure functions (`validate_registration`, `validate_csv_features`, `interpret_prediction`, `sanitize_error`) are extracted for testability
- The orchestrator uses the same OAuth2 token caching pattern as the TravelPlanner reference agent
- CDK stack follows the exact pattern from `.kiro/references/agentcore-workshop/deploy-streamlit-app/cdk/cdk_stack.py`

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.4"] },
    { "id": 1, "tasks": ["1.2", "1.3"] },
    { "id": 2, "tasks": ["2.1", "2.3", "2.7", "2.8"] },
    { "id": 3, "tasks": ["2.2", "2.4", "2.5", "2.6"] },
    { "id": 4, "tasks": ["4.1"] },
    { "id": 5, "tasks": ["4.2"] },
    { "id": 6, "tasks": ["4.3", "4.4", "6.1", "6.3", "6.5"] },
    { "id": 7, "tasks": ["6.2", "6.4"] },
    { "id": 8, "tasks": ["6.6", "6.7", "7.1"] }
  ]
}
```
