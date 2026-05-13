# Requirements Document

## Introduction

Phase 3 decomposes the monolithic Student Services application (Phase 1) into independent AgentCore microservices. The orchestrator and four specialist agents become separate AgentCore Runtimes communicating through an AgentCore Gateway. A thin Streamlit client on ECS Fargate invokes the orchestrator via SigV4-signed HTTP, fully decoupled from backend agent logic. Identity infrastructure uses per-runtime Cognito User Pools with OAuth2 client_credentials flow. AgentCore Memory provides cross-session context, and AgentCore Policies enforce content safety.

## Glossary

- **AgentCore_Runtime**: A managed compute environment on Bedrock AgentCore that hosts a single agent or MCP server, deployed via the AgentCore CLI
- **AgentCore_Gateway**: A single endpoint that aggregates multiple AgentCore Runtimes (targets) and exposes their tools to an orchestrator agent
- **AgentCore_Memory**: A managed memory service providing semantic search, conversation summarization, and user preference extraction across sessions
- **AgentCore_Policy_Engine**: A Cedar-based policy evaluation engine attached to a Gateway that enforces content safety rules on tool invocations
- **Orchestrator_Runtime**: The AgentCore Runtime hosting the Student Services Agent that routes queries to specialist agents via the Gateway
- **Specialist_Runtime**: An AgentCore Runtime hosting one of the four specialist agents (Course Registration, Course Review, Loan Application, Math Teaching)
- **Identity_Stack**: A CloudFormation stack creating Cognito User Pools, domains, resource servers, and app clients for OAuth2 authentication of AgentCore Runtimes
- **Thin_Client**: The Streamlit web application deployed on ECS Fargate that communicates with the Orchestrator Runtime via SigV4-signed HTTP POST
- **SigV4Auth**: AWS Signature Version 4 request signing used by the Thin Client to authenticate with the Orchestrator Runtime
- **BedrockAgentCoreApp**: The Python entrypoint decorator pattern that wraps agent logic for deployment as an AgentCore Runtime
- **Gateway_Target**: A runtime registered with the AgentCore Gateway, exposing its tools to the orchestrator
- **OAuth2_Client_Credentials**: An OAuth2 grant type where a client authenticates with client_id and client_secret to obtain an access token without user interaction
- **Cedar_Policy**: A policy written in the Cedar language used by AgentCore Policy Engine to permit or deny tool invocations
- **agentcore.json**: The declarative configuration file defining all AgentCore project resources (runtimes, memories, credentials, gateways, policies)

## Requirements

### Requirement 1: Identity Infrastructure Provisioning

**User Story:** As a platform engineer, I want individual Cognito User Pools for each AgentCore Runtime, so that each runtime has isolated OAuth2 identity and can be independently secured.

#### Acceptance Criteria

1. WHEN the Identity Stack is deployed, THE Identity_Stack SHALL create one Cognito User Pool for each of the five runtimes (Orchestrator, Course Registration, Course Review, Loan Application, Math Teaching)
2. WHEN the Identity Stack is deployed, THE Identity_Stack SHALL create a User Pool Domain for each pool using the pattern `{runtime-name}-{AWS::AccountId}` where runtime-name is one of: `orchestrator`, `course-registration`, `course-review`, `loan-application`, `math-teaching`
3. WHEN the Identity Stack is deployed, THE Identity_Stack SHALL create a Resource Server on each pool with the identifier set to the runtime-name (e.g., `orchestrator`, `course-registration`) and a single scope named `access`
4. WHEN the Identity Stack is deployed, THE Identity_Stack SHALL create an App Client on each pool configured for the `client_credentials` OAuth2 grant flow with a generated secret and allowed OAuth scope set to `{resource-server-identifier}/access`
5. WHEN the Identity Stack is deployed, THE Identity_Stack SHALL export as CloudFormation Stack Outputs the User Pool ID, Discovery URL (in the format `https://cognito-idp.{region}.amazonaws.com/{pool-id}/.well-known/openid-configuration`), App Client ID, Token Endpoint (in the format `https://{domain}.auth.{region}.amazoncognito.com/oauth2/token`), and OAuth scope for each runtime
6. THE Identity_Stack SHALL deploy to the us-west-2 region
7. IF the Identity Stack deployment fails, THEN THE Identity_Stack SHALL roll back all created resources so that no partial pool configuration remains

### Requirement 2: AgentCore Project Configuration

**User Story:** As a platform engineer, I want a single agentcore.json file that declaratively defines all runtimes, memory, credentials, gateway, and policies, so that the entire microservices topology can be deployed with one `agentcore deploy` command.

#### Acceptance Criteria

1. THE agentcore.json SHALL define a project with name "student-services", schema version v1, and a managedBy field indicating the deployment toolchain
2. THE agentcore.json SHALL declare exactly five runtimes: one Orchestrator Runtime named for the student-services orchestrator (HTTP protocol) and four Specialist Runtimes (HTTP protocol) corresponding to course registration, course review, loan application, and math teaching agents
3. WHEN a Specialist Runtime is declared, THE agentcore.json SHALL configure CUSTOM_JWT authorization with an authorizerConfiguration containing the Cognito pool Discovery URL, allowed client ID, and allowed scope that correspond to that specialist's Identity Stack resource
4. THE agentcore.json SHALL declare an AgentCore Memory resource with SEMANTIC, SUMMARIZATION, and USER_PREFERENCE strategies, each strategy specifying at least one namespace pattern using actorId and sessionId path variables as applicable
5. THE agentcore.json SHALL declare exactly five OAuth credential providers (one per Specialist Runtime and one for the Gateway), each specifying a name, discoveryUrl referencing the corresponding Cognito pool openid-configuration endpoint, at least one scope, and vendor set to "CustomOauth2"
6. THE agentcore.json SHALL declare one AgentCore Gateway named "student-services-gateway" with all four Specialist Runtimes registered as targets, where each target specifies a targetType, at least one toolDefinition, and an outboundAuth block referencing the corresponding OAuth credential provider by name
7. THE agentcore.json SHALL declare a Policy Engine with at least one Cedar policy, a policyEngineConfiguration mode of either ENFORCE or MONITOR, and the Gateway SHALL reference this Policy Engine by name in its policyEngineConfiguration block
8. THE agentcore.json SHALL set all five runtimes to use PYTHON_3_13 runtimeVersion, CodeZip build type, and each runtime SHALL specify an entrypoint file and a codeLocation directory path
9. THE AgentCore project SHALL NOT initialize a separate Git repository; it resides within the existing workspace Git repo under `workshop4/phase3/`
10. THE AgentCore project SHALL include a project-level steering file at `workshop4/phase3/.kiro/steering/student-services-conventions.md` with conventions tailored to the Student Services Agent (specialist names, AWS services, routing rules, model config)

### Requirement 3: Orchestrator Runtime Adaptation

**User Story:** As a developer, I want the Student Services orchestrator agent adapted to the BedrockAgentCoreApp entrypoint pattern, so that it runs as a managed AgentCore Runtime and routes queries to specialists via the Gateway.

#### Acceptance Criteria

1. THE Orchestrator_Runtime SHALL use the BedrockAgentCoreApp entrypoint decorator pattern to handle incoming HTTP invocations
2. WHEN a request is received with a "prompt" key in the payload, THE Orchestrator_Runtime SHALL extract the prompt value and invoke the orchestrator agent
3. IF the request payload does not contain a "prompt" key or the value is empty, THEN THE Orchestrator_Runtime SHALL return a JSON object with a "response" field containing an error message indicating the missing prompt
4. THE Orchestrator_Runtime SHALL connect to the AgentCore Gateway via an MCPClient using streamable-http transport with OAuth2 authentication, reading the Gateway MCP URL, client ID, client secret, token endpoint, and scope from environment variables
5. THE Orchestrator_Runtime SHALL cache OAuth2 tokens and refresh them at least 300 seconds before expiry
6. THE Orchestrator_Runtime SHALL integrate AgentCore Memory using a session manager that keys on session_id and user_id from the invocation context, with retrieval namespaces for user facts and session summaries
7. IF the AgentCore Memory ID environment variable is not set, THEN THE Orchestrator_Runtime SHALL operate without memory integration and process requests using only the current conversation context
8. THE Orchestrator_Runtime SHALL route queries to specialist agents through Gateway tool calls (agents-as-tools pattern)
9. WHEN the orchestrator receives a response from a specialist, THE Orchestrator_Runtime SHALL return the response in a JSON object with a "response" field

### Requirement 4: Course Registration Specialist Runtime

**User Story:** As a developer, I want the Course Registration agent deployed as an independent AgentCore Runtime, so that it can be scaled and updated independently of other agents.

#### Acceptance Criteria

1. THE Specialist_Runtime for Course Registration SHALL use the BedrockAgentCoreApp entrypoint decorator pattern
2. WHEN a registration request is received, THE Specialist_Runtime SHALL validate that student_id, course_name, and semester are each present and non-empty after whitespace trimming
3. WHEN validation passes, THE Specialist_Runtime SHALL generate a unique registration ID and write a record containing reg_id, student_id, course_name, and semester to the course_registration DynamoDB table
4. IF a required field is missing or empty, THEN THE Specialist_Runtime SHALL return an error message listing each field that failed validation without writing to DynamoDB
5. IF the DynamoDB write fails, THEN THE Specialist_Runtime SHALL return an error message indicating a database failure without exposing internal resource identifiers
6. WHEN a registration record is successfully written, THE Specialist_Runtime SHALL return a JSON object with a "response" field containing the registration ID and confirmed student_id, course_name, and semester values
7. THE Specialist_Runtime SHALL have IAM permissions to write to the course_registration DynamoDB table

### Requirement 5: Course Review Specialist Runtime

**User Story:** As a developer, I want the Course Review agent deployed as an independent AgentCore Runtime, so that it can perform RAG queries against the Bedrock Knowledge Base and DynamoDB reviews independently.

#### Acceptance Criteria

1. THE Specialist_Runtime for Course Review SHALL instantiate a BedrockAgentCoreApp and expose an invoke function decorated with @app.entrypoint that accepts a payload dict containing a "prompt" key and returns a dict containing a "response" key
2. WHEN a course information query is received, THE Specialist_Runtime SHALL retrieve up to 5 relevant results from the Bedrock Knowledge Base (ID: NCGF0S9LJR) using the query text for vector search
3. WHEN a course review query is received, THE Specialist_Runtime SHALL query the course_reviews DynamoDB table by course_name key, falling back to partial-match scan if no exact match is found
4. THE Specialist_Runtime SHALL have IAM permissions to invoke the Bedrock Knowledge Base and read from the course_reviews DynamoDB table
5. IF the Bedrock Knowledge Base returns no results or is unreachable, THEN THE Specialist_Runtime SHALL return a response indicating that no matching course catalog information was found
6. IF the DynamoDB query returns no matching reviews or the table is unreachable, THEN THE Specialist_Runtime SHALL return a response indicating that no reviews are available for the requested course

### Requirement 6: Loan Application Specialist Runtime

**User Story:** As a developer, I want the Loan Application agent deployed as an independent AgentCore Runtime, so that it can invoke the SageMaker XGBoost endpoint independently.

#### Acceptance Criteria

1. THE Specialist_Runtime for Loan Application SHALL use the BedrockAgentCoreApp entrypoint decorator pattern
2. WHEN a loan prediction request is received with exactly 59 comma-separated numeric feature values, THE Specialist_Runtime SHALL invoke the SageMaker endpoint (xgboost-serverless-ep2026-05-10-06-08-28) with the feature payload using content type text/csv
3. WHEN the SageMaker endpoint returns a prediction score, THE Specialist_Runtime SHALL classify scores greater than or equal to 0.5 as "Accept" and scores below 0.5 as "Reject", and SHALL return the raw score, the label, and a confidence percentage
4. IF the SageMaker invocation fails, THEN THE Specialist_Runtime SHALL return an error message with AWS ARNs, 12-digit account IDs, and endpoint resource names redacted from the response
5. THE Specialist_Runtime SHALL have IAM permissions to invoke the SageMaker endpoint via the sagemaker-runtime:InvokeEndpoint action
6. IF the loan prediction request does not contain exactly 59 comma-separated values, THEN THE Specialist_Runtime SHALL reject the request and return an error message indicating the expected count of 59 and the actual count received

### Requirement 7: Math Teaching Specialist Runtime

**User Story:** As a developer, I want the Math Teaching agent deployed as an independent AgentCore Runtime, so that it can provide step-by-step mathematical tutoring independently.

#### Acceptance Criteria

1. THE Specialist_Runtime for Math Teaching SHALL use the BedrockAgentCoreApp entrypoint decorator pattern
2. WHEN a math problem is received, THE Specialist_Runtime SHALL solve it using calculator tools and return a response containing intermediate calculations and explanations for each solution step
3. WHEN a math problem is received, THE Specialist_Runtime SHALL return the result in a JSON object with a "response" field containing the step-by-step solution
4. IF the math problem cannot be solved or the input is not a mathematical query, THEN THE Specialist_Runtime SHALL return a JSON object with a "response" field containing an error message indicating the problem could not be solved and suggesting the user rephrase as a specific math question
5. WHEN providing explanations, THE Specialist_Runtime SHALL break complex problems into numbered sub-steps, show calculator-verified intermediate results, and relate concepts to real-world analogies where applicable

### Requirement 8: AgentCore Gateway Configuration

**User Story:** As a platform engineer, I want a single Gateway endpoint that aggregates all specialist tools, so that the orchestrator connects to one URL instead of managing individual specialist connections.

#### Acceptance Criteria

1. THE AgentCore_Gateway SHALL expose a single MCP endpoint that returns all tools from all four Specialist Runtimes in a unified tools/list response
2. THE AgentCore_Gateway SHALL authenticate inbound requests using CUSTOM_JWT authorization backed by a dedicated Cognito pool with configured allowedClients and allowedScopes claims
3. IF an inbound request presents an invalid, expired, or missing JWT token, THEN THE AgentCore_Gateway SHALL reject the request with an authentication error and not forward it to any Specialist Runtime
4. THE AgentCore_Gateway SHALL use OAuth2 credential providers to authenticate outbound requests to each Specialist Runtime, with one credential provider configured per target
5. THE AgentCore_Gateway SHALL enable semantic search for tool discovery so that clients can query tools by natural-language description rather than exact tool name
6. WHEN a tool invocation violates a Cedar policy, THE AgentCore_Gateway SHALL deny the request with the Policy Engine operating in ENFORCE mode
7. IF a target Specialist Runtime is unreachable or not in READY state, THEN THE AgentCore_Gateway SHALL return an error response to the caller indicating the target is unavailable without affecting tool invocations to other healthy targets

### Requirement 9: AgentCore Memory Integration

**User Story:** As a student user, I want the system to remember context from previous conversations, so that I do not need to repeat information across sessions.

#### Acceptance Criteria

1. THE AgentCore_Memory SHALL be configured with the strategies SEMANTIC, SUMMARIZATION, and USER_PREFERENCE, storing semantic facts in a namespace keyed by user ID
2. THE AgentCore_Memory SHALL store conversation summaries in a namespace keyed by user ID and session ID, generating a summary at the end of each session
3. WHEN a user message contains a stated preference (such as a like, dislike, or habitual choice), THE AgentCore_Memory SHALL extract and store the preference in a namespace keyed by user ID
4. THE AgentCore_Memory SHALL set a memory entry expiry duration of 30 days, after which entries are no longer returned in retrieval results
5. WHEN a user sends a message in a new session, THE AgentCore_Memory SHALL retrieve relevant stored memories (semantic facts, preferences, and prior session summaries) and include them in the agent context so the agent can respond without the user repeating previously stated information
6. IF the AgentCore Memory service is unavailable or returns an error, THEN THE system SHALL continue processing the user request without memory context and SHALL not terminate the session

### Requirement 10: AgentCore Policy Engine

**User Story:** As a platform engineer, I want Cedar policies enforcing content safety on the Gateway, so that abusive language is blocked and PII is masked before reaching specialist agents.

#### Acceptance Criteria

1. THE AgentCore_Policy_Engine SHALL enforce a Cedar policy that permits all tool invocations by default (baseline permit)
2. IF a tool invocation input contains language matching the content safety policy's abusive-language category (profanity, slurs, threats, or harassment), THEN THE AgentCore_Policy_Engine SHALL deny the invocation
3. THE AgentCore_Policy_Engine SHALL be attached to the student-services-gateway in ENFORCE mode
4. IF a tool invocation is denied by a Cedar policy, THEN THE AgentCore_Policy_Engine SHALL return a denial response indicating the policy violation category without exposing the original input content
5. THE AgentCore_Policy_Engine SHALL enforce a Cedar policy that masks PII (email addresses, phone numbers, and student IDs) in tool invocation inputs before forwarding to specialist agents

### Requirement 11: Thin Streamlit Client Deployment

**User Story:** As a platform engineer, I want a thin Streamlit application on ECS Fargate that communicates with the orchestrator via SigV4-signed HTTP, so that the frontend is fully decoupled from backend agent logic.

#### Acceptance Criteria

1. THE Thin_Client SHALL be deployed on ECS Fargate (ARM64/Graviton) behind CloudFront and an ALB that only routes requests containing a shared secret custom header injected by CloudFront
2. THE Thin_Client SHALL authenticate end users via a Cognito User Pool using the same streamlit-cognito-auth pattern as Phase 2 (login form, session state, token validation)
3. WHEN a user submits a message, THE Thin_Client SHALL send a SigV4-signed HTTP POST to the Orchestrator Runtime URL with a JSON body containing a "prompt" field holding the user's message text
4. WHEN the Orchestrator Runtime returns a successful response, THE Thin_Client SHALL extract the "response" field from the returned JSON and display it in the chat interface
5. IF the Orchestrator Runtime does not respond within 60 seconds or returns an HTTP error status, THEN THE Thin_Client SHALL display an error message indicating the request failed and preserve the user's conversation history
6. THE Thin_Client SHALL have an IAM task role with `bedrock-agentcore:InvokeAgentRuntime` permission
7. THE Thin_Client SHALL read the Orchestrator Runtime URL from an environment variable (STUDENT_SERVICES_AGENT_URL)
8. IF the STUDENT_SERVICES_AGENT_URL environment variable is missing or empty at startup, THEN THE Thin_Client SHALL fail to start and log an error message indicating the missing configuration
9. WHEN the backend agent logic changes, THE Thin_Client SHALL NOT require redeployment

### Requirement 12: CDK Infrastructure for Thin Client

**User Story:** As a platform engineer, I want a CDK stack that provisions the ECS Fargate infrastructure for the Thin Client, so that deployment is repeatable and version-controlled.

#### Acceptance Criteria

1. THE CDK Stack SHALL create a VPC with public and private subnets across two availability zones
2. THE CDK Stack SHALL create an ECS Fargate service running the Thin Client container in private subnets with egress access
3. THE CDK Stack SHALL create an internet-facing ALB that routes traffic to the ECS service only when a custom header is present, and returns a 403 fixed response for requests that do not include the custom header
4. THE CDK Stack SHALL create a CloudFront distribution that injects the custom header, redirects viewers to HTTPS, disables caching, and forwards all viewer requests to the ALB origin over HTTP
5. THE CDK Stack SHALL create a Cognito User Pool with a generated client secret and store the pool ID, app client ID, and app client secret in a Secrets Manager secret
6. THE CDK Stack SHALL grant the ECS task role permissions for `bedrock-agentcore:InvokeAgentRuntime`
7. THE CDK Stack SHALL pass the STUDENT_SERVICES_AGENT_URL as a container environment variable
8. THE CDK Stack SHALL grant the ECS task role read access to the Cognito Secrets Manager secret
