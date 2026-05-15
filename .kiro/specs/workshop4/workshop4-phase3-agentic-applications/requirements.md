# Requirements Document

## Introduction

Phase 3 adds SSM-based model configuration and thin client interfaces to the Student Services AgentCore microservices architecture. All 5 AgentCore runtimes (1 orchestrator + 4 MCP specialists) read their model configuration from a shared SSM parameter (`/student-services/model-id`) at agent creation time, replacing hardcoded model IDs. A local Streamlit thin client and a production ECS Fargate deployment provide chat UIs that invoke the orchestrator via SigV4-signed HTTP POST. The model is a system-wide parameter — not a per-user or per-request choice — enabling administrators to switch models by updating a single SSM parameter without redeploying any runtime.

## Glossary

- **AgentCore_Runtime**: A Bedrock AgentCore Direct Deploy runtime hosting a Strands Agent or FastMCP server
- **Orchestrator**: The StudentServicesAgent runtime that routes user prompts to specialist MCP tools via the AgentCore Gateway
- **Specialist_MCP_Server**: One of the 4 MCP runtimes (CourseRegistrationMcp, CourseReviewMcp, LoanApplicationMcp, MathTeachingMcp)
- **SSM_Parameter**: An AWS Systems Manager Parameter Store parameter at path `/student-services/model-id`
- **get_model_config**: A helper function that reads model configuration from SSM and returns a dictionary with model_id, region, and max_tokens
- **Thin_Client**: A Streamlit web application that sends prompts to the Orchestrator and displays responses
- **Local_Thin_Client**: The Streamlit app in `workshop4/phase3/streamlit_app/` run locally via `streamlit run`
- **Production_Web_App**: The Streamlit app deployed on ECS Fargate behind CloudFront + ALB with Cognito authentication in `workshop4/phase3/deploy-streamlit-app/`
- **SigV4**: AWS Signature Version 4 request signing for authenticating HTTP requests to AgentCore runtimes
- **AgentCoreBasePolicy**: The shared IAM managed policy attached to all 5 execution roles in the CloudFormation stack
- **CDK_Stack**: The AWS CDK Python stack that deploys the Production_Web_App infrastructure

## Requirements

### Requirement 1: SSM Model Configuration Helper

**User Story:** As a workshop developer, I want all AgentCore runtimes to read their model configuration from SSM Parameter Store, so that I can change the model for all runtimes by updating a single parameter without redeploying.

#### Acceptance Criteria

1. WHEN an AgentCore_Runtime creates a new Agent instance, THE get_model_config function SHALL read the `/student-services/model-id` SSM parameter and return a dictionary containing `model_id`, `region`, and `max_tokens` keys.
2. THE get_model_config function SHALL return `region` as `us-west-2` and `max_tokens` as `4096` as fixed values in the returned dictionary.
3. IF the SSM parameter read fails, THEN THE get_model_config function SHALL fall back to the hardcoded default model ID `us.amazon.nova-2-lite-v1:0`.
4. THE get_model_config function SHALL use `boto3.client("ssm")` with `get_parameter` to read the single parameter `/student-services/model-id`.
5. THE get_model_config function SHALL be defined in a shared module at `workshop4/phase3/studentservices/shared/config.py` importable by all 5 agent.py files.

### Requirement 2: Orchestrator SSM Integration

**User Story:** As a workshop developer, I want the StudentServicesAgent orchestrator to use get_model_config instead of hardcoding the model ID, so that model changes propagate to the orchestrator automatically.

#### Acceptance Criteria

1. WHEN the StudentServicesAgent Orchestrator creates a cached Agent instance, THE Orchestrator SHALL call get_model_config and use the returned `model_id` value to construct the BedrockModel.
2. THE Orchestrator SHALL continue to cache agents keyed by `{session_id}/{user_id}` so that new sessions pick up SSM parameter changes while existing sessions retain their model.
3. THE Orchestrator SHALL accept only `{"prompt": "..."}` as the request payload format and SHALL return `{"response": "..."}` as the response format.
4. THE Orchestrator SHALL NOT accept a `model_id` field in the request payload.

### Requirement 3: Specialist MCP Servers SSM Integration

**User Story:** As a workshop developer, I want all 4 specialist MCP servers to use get_model_config instead of hardcoding the model ID, so that model changes propagate to all specialists automatically.

#### Acceptance Criteria

1. WHEN the CourseRegistrationMcp Specialist_MCP_Server creates an Agent instance, THE CourseRegistrationMcp SHALL call get_model_config and use the returned `model_id` to construct the BedrockModel.
2. WHEN the CourseReviewMcp Specialist_MCP_Server creates an Agent instance, THE CourseReviewMcp SHALL call get_model_config and use the returned `model_id` to construct the BedrockModel.
3. WHEN the LoanApplicationMcp Specialist_MCP_Server creates an Agent instance, THE LoanApplicationMcp SHALL call get_model_config and use the returned `model_id` to construct the BedrockModel.
4. WHEN the MathTeachingMcp Specialist_MCP_Server creates an Agent instance, THE MathTeachingMcp SHALL call get_model_config and use the returned `model_id` to construct the BedrockModel.
5. THE Specialist_MCP_Server agent.py files SHALL import get_model_config from the shared config module rather than duplicating SSM logic.

### Requirement 4: IAM Permission for SSM Access

**User Story:** As a workshop developer, I want all AgentCore execution roles to have permission to read SSM parameters, so that the get_model_config function can access `/student-services/model-id` at runtime.

#### Acceptance Criteria

1. THE AgentCoreBasePolicy in `student-services-agentcore-infra.yaml` SHALL include an `ssm:GetParameter` permission statement.
2. THE SSM permission resource scope SHALL be limited to `arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/student-services/*`.
3. WHEN the CloudFormation stack is deployed, THE AgentCoreBasePolicy SHALL grant all 5 execution roles the ability to read SSM parameters under the `/student-services/` path.

### Requirement 5: Local Thin Client

**User Story:** As a workshop participant, I want a local Streamlit chat application that sends prompts to the StudentServicesAgent runtime, so that I can test the agentic system from my development machine.

#### Acceptance Criteria

1. THE Local_Thin_Client SHALL provide a Streamlit chat interface with a text input field and message history display.
2. WHEN the user submits a prompt, THE Local_Thin_Client SHALL send an HTTP POST request to the StudentServicesAgent runtime URL with body `{"prompt": "<user_message>"}`.
3. THE Local_Thin_Client SHALL sign all HTTP requests to the Orchestrator using SigV4 with service name `bedrock-agentcore` and the configured AWS region.
4. THE Local_Thin_Client SHALL display the `response` field from the JSON reply in the chat message area.
5. THE Local_Thin_Client SHALL read the runtime URL from the `STUDENT_SERVICES_AGENT_URL` environment variable.
6. THE Local_Thin_Client SHALL display the currently configured model ID (read from SSM parameter `/student-services/model-id`) as read-only information in the sidebar.
7. THE Local_Thin_Client SHALL provide a "Clear Chat" button in the sidebar that resets the conversation history.
8. IF the `STUDENT_SERVICES_AGENT_URL` environment variable is not set, THEN THE Local_Thin_Client SHALL display an error message and stop execution.
9. IF the HTTP request to the Orchestrator fails, THEN THE Local_Thin_Client SHALL display the error message in the chat area without crashing.
10. THE Local_Thin_Client SHALL be located at `workshop4/phase3/streamlit_app/` with an `app.py` entry point, `agent_client.py` for HTTP logic, and `requirements.txt` for dependencies.

### Requirement 6: Production Web App Infrastructure

**User Story:** As a workshop developer, I want the thin client deployed on ECS Fargate behind CloudFront with Cognito authentication, so that the application is accessible over HTTPS with user login.

#### Acceptance Criteria

1. THE CDK_Stack SHALL deploy an ECS Fargate service running the Streamlit Thin_Client container on ARM64 (Graviton).
2. THE CDK_Stack SHALL create a VPC with 2 availability zones, public subnets for the ALB, and private subnets with NAT gateway for ECS tasks.
3. THE CDK_Stack SHALL create an Application Load Balancer that routes traffic to the ECS service on port 8501.
4. THE CDK_Stack SHALL create a CloudFront distribution in front of the ALB with a custom header to restrict direct ALB access.
5. THE CDK_Stack SHALL create a Cognito User Pool and store pool credentials in Secrets Manager for the application to use.
6. THE CDK_Stack SHALL grant the ECS task role `bedrock-agentcore:InvokeAgentRuntime` permission to invoke the Orchestrator runtime.
7. THE CDK_Stack SHALL grant the ECS task role `ssm:GetParameter` and `ssm:GetParametersByPath` permissions to read model configuration from SSM.
8. THE CDK_Stack SHALL grant the ECS task role read access to the Cognito secret in Secrets Manager.
9. THE CDK_Stack SHALL use a `config_file.py` with stack name `StudentServicesPhase3` and a unique custom header value.
10. THE CDK_Stack SHALL output the CloudFront distribution URL and Cognito User Pool ID.
11. THE CDK_Stack SHALL be located at `workshop4/phase3/deploy-streamlit-app/` following the same structure as the Phase 2 CDK deployment.

### Requirement 7: Production Web App Container

**User Story:** As a workshop developer, I want the production Docker container to run the same thin client logic as the local version, so that behavior is consistent between local and deployed environments.

#### Acceptance Criteria

1. THE Production_Web_App container SHALL run the Streamlit application on port 8501.
2. THE Production_Web_App SHALL read the `STUDENT_SERVICES_AGENT_URL` from an environment variable passed by the CDK stack or set at deploy time.
3. THE Production_Web_App SHALL implement Cognito-based user authentication using the credentials stored in Secrets Manager.
4. THE Production_Web_App SHALL use the same SigV4 signing logic as the Local_Thin_Client for requests to the Orchestrator.
5. THE Production_Web_App SHALL include a Dockerfile that installs dependencies and runs `streamlit run app.py --server.port=8501`.
6. THE Production_Web_App docker application SHALL be located at `workshop4/phase3/deploy-streamlit-app/docker_app/`.

### Requirement 8: Model Switch Without Redeployment

**User Story:** As an administrator, I want to change the model used by all runtimes by updating a single SSM parameter, so that new sessions use the updated model without requiring any redeployment.

#### Acceptance Criteria

1. WHEN an administrator updates the SSM parameter `/student-services/model-id` to a new value, THE AgentCore_Runtime SHALL use the new model ID for all subsequently created Agent instances.
2. WHILE an existing cached Agent session is active, THE AgentCore_Runtime SHALL continue using the model ID that was configured when that session was created.
3. THE get_model_config function SHALL read from SSM on each invocation without caching the parameter value, so that new sessions always get the current value.

### Requirement 9: README Documentation

**User Story:** As a workshop participant, I want documentation explaining the SSM-based model configuration pattern and deployment steps, so that I understand the architectural decisions and can follow the workshop.

#### Acceptance Criteria

1. THE README SHALL explain why dynamic per-request model propagation is difficult in microservices architectures with multiple hops (UI → orchestrator → gateway → MCP server → inner agent).
2. THE README SHALL explain that propagating model_id through MCP tool calls would require changing the MCP protocol contract at each hop.
3. THE README SHALL explain that SSM provides "one model everywhere" via shared configuration — change once, all runtimes pick it up on next session creation.
4. THE README SHALL document the steps to deploy the local thin client including setting the `STUDENT_SERVICES_AGENT_URL` environment variable.
5. THE README SHALL document the steps to deploy the production web app using CDK.
6. THE README SHALL document how to switch models by updating the SSM parameter via AWS CLI.
