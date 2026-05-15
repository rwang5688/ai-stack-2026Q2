# Requirements Document

## Introduction

This specification defines the backend runtime modification and thin client applications for Workshop 4 Phase 3 — the AgentCore microservices architecture. The backend change adds dynamic model selection to the StudentServicesAgent runtime, allowing thin clients to specify which foundation model powers the agent. Two thin client deployment targets are covered: a local development Streamlit app and a production web deployment on ECS Fargate with CloudFront, ALB, and Cognito authentication. Both thin clients invoke the StudentServicesAgent HTTP runtime on AgentCore via SigV4-signed HTTP POST requests.

## Glossary

- **StudentServicesAgent_Runtime**: The AgentCore HTTP runtime hosting the orchestrator agent at `workshop4/phase3/studentservices/student_services/agent.py`, accepting `{"prompt": "...", "model_id": "..."}` payloads and returning `{"response": "..."}`
- **Thin_Client**: A Streamlit-based chat UI that sends user prompts to the StudentServicesAgent_Runtime and displays responses without performing any agent logic locally
- **Agent_Client**: A Python module that constructs SigV4-signed HTTP POST requests to the StudentServicesAgent_Runtime URL and parses JSON responses
- **SigV4**: AWS Signature Version 4 request signing protocol used to authenticate HTTP requests to AWS services, with service name `bedrock-agentcore`
- **CDK_Stack**: An AWS CDK (Python) infrastructure-as-code stack that provisions cloud resources for the production deployment
- **ECS_Fargate**: AWS Elastic Container Service serverless compute for running Docker containers without managing servers
- **CloudFront**: AWS content delivery network providing HTTPS termination in front of the ALB
- **ALB**: Application Load Balancer routing HTTP traffic to ECS Fargate tasks
- **Cognito**: AWS Cognito User Pool providing user authentication for the production web deployment
- **Secrets_Manager**: AWS Secrets Manager storing Cognito pool parameters for runtime retrieval
- **Config_Module**: A Python configuration class defining stack name, region, secrets ID, and custom header values
- **Allowed_Models**: The set of model identifiers permitted for use: `us.amazon.nova-2-lite-v1:0` (default) and `us.anthropic.claude-sonnet-4-6`

## Requirements

### Requirement 1: Runtime Model Selection

**User Story:** As a developer, I want the StudentServicesAgent runtime to accept an optional model_id in the request payload, so that thin clients can dynamically select which foundation model powers the agent without redeploying the runtime.

#### Acceptance Criteria

1. WHEN the request payload contains a `model_id` field with a non-empty string value from the Allowed_Models list, THE StudentServicesAgent_Runtime SHALL use that model_id for BedrockModel creation instead of the hardcoded default
2. WHEN the request payload does not contain a `model_id` field or the field is empty, THE StudentServicesAgent_Runtime SHALL use the default model_id `us.amazon.nova-2-lite-v1:0`
3. IF the request payload contains a `model_id` value that is not in the Allowed_Models list, THEN THE StudentServicesAgent_Runtime SHALL return an error response indicating the model is not allowed and listing the permitted models
4. THE StudentServicesAgent_Runtime SHALL cache Agent instances by the composite key `{session_id}/{user_id}/{model_id}` so that switching models creates a new Agent instance
5. THE StudentServicesAgent_Runtime SHALL pass the resolved model_id to BedrockModel with region_name `us-west-2` and max_tokens 4096
6. THE StudentServicesAgent_Runtime SHALL define the Allowed_Models list as a module-level constant containing `us.amazon.nova-2-lite-v1:0` and `us.anthropic.claude-sonnet-4-6`

### Requirement 2: Agent Client Module

**User Story:** As a developer, I want a reusable HTTP client module that signs requests to the StudentServicesAgent runtime and supports model selection, so that both local and deployed thin clients can communicate with AgentCore securely.

#### Acceptance Criteria

1. THE Agent_Client SHALL send HTTP POST requests to the URL specified by the STUDENT_SERVICES_AGENT_URL environment variable
2. THE Agent_Client SHALL sign each request using SigV4 with service name `bedrock-agentcore` and region `us-west-2`
3. THE Agent_Client SHALL send a JSON body with Content-Type header `application/json`
4. WHEN a model_id parameter is provided to the invoke function, THE Agent_Client SHALL include it in the JSON body as `{"prompt": "<user_message>", "model_id": "<model_id>"}`
5. WHEN no model_id parameter is provided to the invoke function, THE Agent_Client SHALL send only `{"prompt": "<user_message>"}`
6. THE Agent_Client SHALL extract and return the `response` field from the JSON reply on HTTP 200 status
7. IF the STUDENT_SERVICES_AGENT_URL environment variable is empty or unset, THEN THE Agent_Client SHALL report the missing variable via a configuration error check function
8. IF the HTTP response status code is not 200, THEN THE Agent_Client SHALL raise a RuntimeError containing the status code and response body
9. IF a network error occurs during the HTTP request, THEN THE Agent_Client SHALL raise a RuntimeError describing the failure
10. THE Agent_Client SHALL use boto3 Session credentials for SigV4 signing to support IAM roles, environment credentials, and AWS profiles
11. THE Agent_Client SHALL set an HTTP request timeout of 120 seconds

### Requirement 3: Local Streamlit Chat UI

**User Story:** As a developer, I want a local Streamlit chat application for testing the StudentServicesAgent runtime with model selection, so that I can verify agent behavior during development without deploying infrastructure.

#### Acceptance Criteria

1. THE Thin_Client SHALL display a page title of "Student Services Assistant" and a university-themed header
2. THE Thin_Client SHALL validate required environment variables on startup and display an error message with the missing variable names when validation fails
3. THE Thin_Client SHALL display a model selection dropdown in the sidebar with display names and model IDs matching the Allowed_Models list
4. WHEN a user submits a non-empty message via the chat input, THE Thin_Client SHALL invoke the Agent_Client with the message text and the currently selected model_id
5. WHILE the Agent_Client request is in progress, THE Thin_Client SHALL display a spinner with the text "Thinking..."
6. IF the Agent_Client raises an exception, THEN THE Thin_Client SHALL display the error message in the chat interface
7. THE Thin_Client SHALL maintain chat history in session state and render all previous messages on page load
8. THE Thin_Client SHALL provide a "Clear Chat" button in the sidebar that resets the conversation history
9. THE Thin_Client SHALL display sample prompts in the sidebar covering course registration, course reviews, loan prediction, and math tutoring domains
10. THE Thin_Client SHALL reside in the directory `workshop4/phase3/streamlit_app/`

### Requirement 4: Production Streamlit App with Cognito Authentication

**User Story:** As a developer, I want a production-ready Streamlit app that adds Cognito user authentication to the thin client with model selection, so that the deployed web application restricts access to authenticated users and provides full feature parity with the local version.

#### Acceptance Criteria

1. THE Thin_Client SHALL authenticate users via Cognito before displaying the chat interface, using the streamlit-cognito-auth library
2. THE Thin_Client SHALL retrieve Cognito pool parameters (pool_id, app_client_id, app_client_secret) from Secrets_Manager using the secret ID defined in Config_Module
3. WHEN a user is not authenticated, THE Thin_Client SHALL display the Cognito login form and stop rendering the chat interface
4. WHEN a user is authenticated, THE Thin_Client SHALL display the username in the sidebar and provide a Logout button
5. THE Thin_Client SHALL include the same chat functionality, model selection, sample prompts, and error handling as the local development version
6. THE Thin_Client SHALL read the STUDENT_SERVICES_AGENT_URL from an environment variable injected by the ECS task definition
7. THE Thin_Client SHALL reside in the directory `workshop4/phase3/deploy-streamlit-app/docker_app/`

### Requirement 5: Configuration Module

**User Story:** As a developer, I want a centralized configuration module for the CDK stack and Docker app, so that resource naming and deployment parameters are consistent and easy to update.

#### Acceptance Criteria

1. THE Config_Module SHALL define STACK_NAME as `StudentServicesPhase3`
2. THE Config_Module SHALL define DEPLOYMENT_REGION as `us-west-2`
3. THE Config_Module SHALL define SECRETS_MANAGER_ID derived from the STACK_NAME for Cognito secret storage
4. THE Config_Module SHALL define CUSTOM_HEADER_VALUE as a unique string for CloudFront-to-ALB request validation
5. THE Config_Module SHALL reside in the directory `workshop4/phase3/deploy-streamlit-app/docker_app/`

### Requirement 6: Docker Container Image

**User Story:** As a developer, I want a Docker image that packages the production Streamlit app for deployment on ECS Fargate, so that the application runs consistently in the cloud environment.

#### Acceptance Criteria

1. THE Docker image SHALL be built from the `docker_app/` directory within `workshop4/phase3/deploy-streamlit-app/`
2. THE Docker image SHALL target the ARM64 architecture for Graviton-based Fargate tasks
3. THE Docker image SHALL expose port 8501 for Streamlit's default HTTP server
4. THE Docker image SHALL install all Python dependencies including streamlit, boto3, httpx, and streamlit-cognito-auth
5. THE Docker image SHALL run the Streamlit application as the container entrypoint

### Requirement 7: CDK Stack — VPC and Networking

**User Story:** As a developer, I want the CDK stack to provision a VPC with public and private subnets, so that the ALB is internet-accessible while ECS tasks run in private subnets with NAT egress.

#### Acceptance Criteria

1. THE CDK_Stack SHALL create a VPC with CIDR `10.0.0.0/16`, 2 availability zones, and 1 NAT gateway
2. THE CDK_Stack SHALL create an ALB security group allowing inbound HTTP traffic on port 80
3. THE CDK_Stack SHALL create an ECS security group allowing inbound traffic on port 8501 only from the ALB security group
4. THE CDK_Stack SHALL place the ALB in public subnets and ECS tasks in private subnets with egress

### Requirement 8: CDK Stack — ECS Fargate Service

**User Story:** As a developer, I want the CDK stack to deploy the Streamlit Docker container on ECS Fargate, so that the application runs serverlessly with automatic scaling and health management.

#### Acceptance Criteria

1. THE CDK_Stack SHALL create a Fargate task definition with 256 CPU units and 512 MiB memory on ARM64 runtime platform
2. THE CDK_Stack SHALL build the Docker image from the `docker_app/` directory and add it as the task container
3. THE CDK_Stack SHALL map container port 8501 with TCP protocol
4. THE CDK_Stack SHALL pass the STUDENT_SERVICES_AGENT_URL as an environment variable to the container via CDK context parameter `student_services_agent_url`
5. THE CDK_Stack SHALL create a Fargate service in private subnets with the ECS security group attached
6. THE CDK_Stack SHALL enable AWS CloudWatch logging with a stream prefix for container logs

### Requirement 9: CDK Stack — ALB and CloudFront

**User Story:** As a developer, I want the CDK stack to provision CloudFront in front of an ALB, so that users access the application over HTTPS while the ALB validates requests originate from CloudFront.

#### Acceptance Criteria

1. THE CDK_Stack SHALL create an internet-facing ALB in public subnets
2. THE CDK_Stack SHALL create a CloudFront distribution with the ALB as origin, using HTTP-only origin protocol and caching disabled
3. THE CDK_Stack SHALL configure CloudFront to inject a custom header (X-Custom-Header) with the value from Config_Module on all origin requests
4. THE CDK_Stack SHALL configure the ALB listener on port 80 to route requests containing the custom header to the ECS target group on port 8501
5. THE CDK_Stack SHALL configure the ALB listener default action to return HTTP 403 for requests missing the custom header
6. THE CDK_Stack SHALL configure CloudFront to redirect viewers to HTTPS and allow all HTTP methods

### Requirement 10: CDK Stack — Cognito and Secrets Manager

**User Story:** As a developer, I want the CDK stack to create a Cognito User Pool and store its parameters in Secrets Manager, so that the Streamlit app can authenticate users without hardcoded credentials.

#### Acceptance Criteria

1. THE CDK_Stack SHALL create a Cognito User Pool for end-user authentication
2. THE CDK_Stack SHALL create a Cognito User Pool Client with a generated secret
3. THE CDK_Stack SHALL store pool_id, app_client_id, and app_client_secret in a Secrets Manager secret with the ID defined in Config_Module
4. THE CDK_Stack SHALL grant the ECS task role read access to the Cognito secret in Secrets_Manager

### Requirement 11: CDK Stack — IAM Permissions

**User Story:** As a developer, I want the ECS task role to have permission to invoke the AgentCore runtime, so that the containerized thin client can communicate with the StudentServicesAgent.

#### Acceptance Criteria

1. THE CDK_Stack SHALL attach an inline IAM policy to the ECS task role granting `bedrock-agentcore:InvokeAgentRuntime` action on all resources
2. THE CDK_Stack SHALL grant the ECS task role read access to the Secrets_Manager secret containing Cognito parameters

### Requirement 12: CDK Stack — Outputs

**User Story:** As a developer, I want the CDK stack to output the CloudFront URL and Cognito Pool ID, so that I can access the deployed application and configure user accounts.

#### Acceptance Criteria

1. THE CDK_Stack SHALL output the CloudFront distribution domain name as `CloudFrontDistributionURL`
2. THE CDK_Stack SHALL output the Cognito User Pool ID as `CognitoPoolId`

### Requirement 13: CDK Project Structure

**User Story:** As a developer, I want the CDK project to follow the established Phase 2 directory layout, so that the deployment is consistent and familiar.

#### Acceptance Criteria

1. THE CDK_Stack SHALL reside at `workshop4/phase3/deploy-streamlit-app/cdk/cdk_stack.py`
2. THE CDK_Stack SHALL use the stack name `StudentServicesPhase3` matching Config_Module
3. THE CDK_Stack SHALL include a CDK app entry point at `workshop4/phase3/deploy-streamlit-app/cdk/app.py`
4. THE CDK_Stack SHALL include `cdk.json` at `workshop4/phase3/deploy-streamlit-app/` pointing to the app entry point
5. THE CDK_Stack SHALL accept the StudentServicesAgent runtime URL via CDK context parameter `student_services_agent_url`
