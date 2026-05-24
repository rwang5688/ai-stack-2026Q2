# Requirements Document

## Introduction

Refactor Workshop 4 Phase 3 from the broken "Agent-inside-MCP" anti-pattern (each specialist Strands Agent wrapped inside its own MCP server) to the correct AWS-recommended architecture: all agent intelligence consolidated in one AgentCore HTTP Runtime using the Agent-as-Tool pattern locally, with only dumb deterministic data-access tools exposed as MCP servers via AgentCore Gateway.

The refactoring preserves the workshop progression story (Phase 1: monolithic → Phase 2: multi-agent → Phase 3: microservices with gateway) while fixing the architectural flaw that caused the May 2026 breakage.

## Glossary

- **Orchestrator_Runtime**: The single AgentCore HTTP Runtime (`StudentServicesAgent`) containing the orchestrator agent and all four specialist agents running locally via Agent-as-Tool pattern
- **Agent_as_Tool**: Strands SDK pattern where a specialist Agent is invoked as a tool by the orchestrator, running in the same process with its own system prompt and reasoning loop
- **Dumb_MCP_Server**: An AgentCore MCP Runtime that exposes only deterministic data-access functions (no LLM calls, no Strands Agent) via FastMCP
- **AgentCore_Gateway**: The AgentCore Gateway (`studentservicesgateway`) that aggregates MCP server targets with OAuth authentication, Cedar policies, and semantic routing
- **CourseCatalogMcp**: Dumb MCP server exposing `search_course_catalog(query)` backed by Bedrock Knowledge Base retrieve
- **CourseReviewsMcp**: Dumb MCP server exposing `get_course_reviews(course_name)` backed by DynamoDB read
- **CourseRegistrationMcp**: Dumb MCP server exposing `register_course(student_id, course_name, semester)` backed by DynamoDB write
- **LoanApplicationMcp**: Dumb MCP server exposing `predict_loan(features_csv)` backed by SageMaker Serverless Endpoint invoke
- **Calculator**: A pure local Python function used by the math teaching specialist agent — no MCP server needed
- **Routing_Path**: A display string showing the distributed routing chain for instructional visibility in the Streamlit UI
- **FastMCP**: The Python MCP server framework used with floating version (no hard pin) since dumb tools are immune to version changes
- **AgentCore_CLI**: The `@aws/agentcore` npm package used for deployment, installed at latest available version

## Requirements

### Requirement 1: CloudFormation Infrastructure Update

**User Story:** As a workshop developer, I want the CloudFormation template updated to reflect the new MCP server topology, so that IAM execution roles and Cognito OAuth pools are correctly provisioned before AgentCore deployment.

#### Acceptance Criteria

1. THE CloudFormation template SHALL remove the MathTeaching domain section entirely (execution role, Cognito pool, domain, resource server, app client)
2. THE CloudFormation template SHALL replace the CourseReview domain section with two separate domain sections: CourseCatalog and CourseReviews, each with their own execution role, Cognito pool, domain, resource server, and app client
3. THE CourseCatalog execution role SHALL have the AgentCore base policy plus Bedrock Knowledge Base retrieve permission (`bedrock:Retrieve`)
4. THE CourseReviews execution role SHALL have the AgentCore base policy plus DynamoDB read-only access (`AmazonDynamoDBReadOnlyAccess`)
5. THE CourseRegistration and LoanApplication domain sections SHALL remain unchanged
6. THE StudentServicesAgent and StudentServicesGateway domain sections SHALL remain unchanged
7. THE CloudFormation stack SHALL be deployed (updated) before any AgentCore CLI operations
8. THE CloudFormation stack outputs SHALL include discovery URLs, client IDs, token endpoints, and scopes for CourseCatalog and CourseReviews (replacing CourseReview outputs)

### Requirement 2: CLI Upgrade and Clean Install

**User Story:** As a workshop developer, I want to start from a clean AgentCore CLI installation at the latest available version, so that the deployment toolchain is current and consistent.

#### Acceptance Criteria

1. WHEN the refactoring begins, THE AgentCore_CLI SHALL be installed at the latest available version via `npm install -g @aws/agentcore@latest`
2. IF a previous AgentCore_CLI installation exists, THEN THE AgentCore_CLI SHALL be cleanly removed before reinstallation by deleting the global node_modules directory for `@aws/agentcore`
3. THE installed version SHALL be recorded in session notes for reproducibility

### Requirement 2: Orchestrator Runtime with Local Specialist Agents

**User Story:** As a workshop developer, I want all agent intelligence consolidated in one AgentCore HTTP Runtime, so that specialist reasoning runs locally without double-inference latency or MCP transport fragility.

#### Acceptance Criteria

1. THE Orchestrator_Runtime SHALL contain one orchestrator agent and four specialist agents (course_review_agent, course_registration_agent, loan_application_agent, math_teaching_agent) running via Agent_as_Tool pattern
2. THE Orchestrator_Runtime SHALL use the `BedrockAgentCoreApp` entrypoint with HTTP protocol
3. WHEN the orchestrator receives a user query, THE Orchestrator_Runtime SHALL route it to the appropriate specialist agent locally without making any MCP calls for the routing decision
4. THE Orchestrator_Runtime SHALL connect specialist agents to their data-access tools via MCPClient routed through the AgentCore_Gateway using OAuth authentication
5. THE Orchestrator_Runtime SHALL use the same OAuth token caching pattern (refresh 300 seconds before expiry) as the current implementation
6. WHEN the math_teaching_agent needs to perform calculations, THE Orchestrator_Runtime SHALL use a local Calculator function without any MCP server call

### Requirement 3: Course Catalog Dumb MCP Server

**User Story:** As a workshop developer, I want the course catalog search exposed as a dumb MCP tool, so that the Knowledge Base retrieve operation is independently scalable and observable behind the gateway.

#### Acceptance Criteria

1. THE CourseCatalogMcp SHALL expose a single tool `search_course_catalog` that accepts a `query` string parameter
2. WHEN `search_course_catalog` is called, THE CourseCatalogMcp SHALL invoke Bedrock Knowledge Base retrieve with the query and return formatted results
3. THE CourseCatalogMcp SHALL NOT contain any Strands Agent, LLM call, or reasoning logic
4. THE CourseCatalogMcp SHALL use FastMCP with floating version (no pinned version in requirements.txt)
5. THE CourseCatalogMcp SHALL use the Knowledge Base ID `NCGF0S9LJR` (configurable via environment variable)

### Requirement 4: Course Reviews Dumb MCP Server

**User Story:** As a workshop developer, I want the course reviews lookup exposed as a dumb MCP tool, so that DynamoDB read operations are independently observable and policy-controlled.

#### Acceptance Criteria

1. THE CourseReviewsMcp SHALL expose a single tool `get_course_reviews` that accepts a `course_name` string parameter
2. WHEN `get_course_reviews` is called, THE CourseReviewsMcp SHALL query the DynamoDB `course_reviews` table and return matching reviews
3. THE CourseReviewsMcp SHALL NOT contain any Strands Agent, LLM call, or reasoning logic
4. THE CourseReviewsMcp SHALL use FastMCP with floating version (no pinned version in requirements.txt)
5. THE CourseReviewsMcp SHALL support partial course name matching via DynamoDB scan with contains filter

### Requirement 5: Course Registration Dumb MCP Server

**User Story:** As a workshop developer, I want the course registration write exposed as a dumb MCP tool, so that DynamoDB write operations are independently policy-controlled and auditable.

#### Acceptance Criteria

1. THE CourseRegistrationMcp SHALL expose a single tool `register_course` that accepts `student_id`, `course_name`, and `semester` string parameters
2. WHEN `register_course` is called with valid parameters, THE CourseRegistrationMcp SHALL write a registration record to the DynamoDB `course_registration` table with a generated UUID
3. IF any required parameter is missing or empty, THEN THE CourseRegistrationMcp SHALL return a descriptive error message listing the missing fields
4. THE CourseRegistrationMcp SHALL NOT contain any Strands Agent, LLM call, or reasoning logic
5. THE CourseRegistrationMcp SHALL use FastMCP with floating version (no pinned version in requirements.txt)

### Requirement 6: Loan Application Dumb MCP Server

**User Story:** As a workshop developer, I want the loan prediction exposed as a dumb MCP tool, so that SageMaker endpoint invocations are independently scalable and cost-observable.

#### Acceptance Criteria

1. THE LoanApplicationMcp SHALL expose a single tool `predict_loan` that accepts a `features_csv` string parameter containing 59 comma-separated numeric values
2. WHEN `predict_loan` is called with valid features, THE LoanApplicationMcp SHALL invoke the SageMaker Serverless Endpoint and return the prediction score, label, and confidence
3. IF the features_csv does not contain exactly 59 values, THEN THE LoanApplicationMcp SHALL return a descriptive error message with the actual count received
4. THE LoanApplicationMcp SHALL NOT contain any Strands Agent, LLM call, or reasoning logic
5. THE LoanApplicationMcp SHALL use FastMCP with floating version (no pinned version in requirements.txt)
6. THE LoanApplicationMcp SHALL redact ARNs and account IDs from error messages before returning them

### Requirement 7: Math Teaching Agent Without MCP Server

**User Story:** As a workshop developer, I want the math teaching specialist to use only a local calculator function, so that pure computation does not incur unnecessary network overhead or gateway routing.

#### Acceptance Criteria

1. THE Orchestrator_Runtime SHALL include a math_teaching_agent that uses a local Calculator tool defined as a Python function
2. THE Calculator SHALL evaluate mathematical expressions safely using a restricted eval with only math, abs, max, min, pow, round, and sum allowed
3. THE Orchestrator_Runtime SHALL NOT deploy any MCP server for math teaching functionality
4. WHEN the agentcore.json is updated, THE MathTeachingMcp runtime entry SHALL be removed

### Requirement 8: Course Review Specialist Dual-Tool Behavior

**User Story:** As a workshop developer, I want the course review specialist to always consult both the catalog and reviews, so that students get comprehensive course information combining official descriptions with peer feedback.

#### Acceptance Criteria

1. WHEN the course_review_agent receives a query, THE course_review_agent SHALL call BOTH `search_course_catalog` AND `get_course_reviews` tools
2. THE course_review_agent system prompt SHALL contain explicit instructions requiring both tools be called for every course-related query
3. THE course_review_agent SHALL combine catalog information and student reviews in its response

### Requirement 9: AgentCore Gateway Configuration Update

**User Story:** As a workshop developer, I want the gateway configuration updated to reflect the new dumb MCP server topology, so that tool routing, OAuth, and Cedar policies work correctly with the refactored architecture.

#### Acceptance Criteria

1. THE AgentCore_Gateway SHALL retain all existing Cognito pools, OAuth credentials, and Cedar policy configurations
2. THE AgentCore_Gateway targets SHALL be updated to point to the new dumb MCP server endpoints (CourseCatalogMcp, CourseReviewsMcp, CourseRegistrationMcp, LoanApplicationMcp)
3. THE AgentCore_Gateway SHALL remove the MathTeachingMcp target since math teaching no longer uses an MCP server
4. THE AgentCore_Gateway tool definitions SHALL list individual tool names (`search_course_catalog`, `get_course_reviews`, `register_course`, `predict_loan`) instead of aggregate agent names
5. WHILE the gateway is being reconfigured, THE AgentCore_Gateway SHALL preserve the existing `StudentServicesMemory` configuration

### Requirement 10: Routing Path Display

**User Story:** As a workshop instructor, I want the distributed routing path displayed in responses, so that students can visualize how requests flow through the microservices architecture.

#### Acceptance Criteria

1. WHEN a specialist agent completes a request that used MCP tools, THE Orchestrator_Runtime SHALL include a `routing_path` string showing the full routing chain (e.g., "StudentServicesAgent → course_review_agent → AgentCore Gateway → CourseCatalogMcp + CourseReviewsMcp")
2. WHEN the math_teaching_agent completes a request, THE Orchestrator_Runtime SHALL include a routing_path showing local-only routing (e.g., "StudentServicesAgent → math_teaching_agent → calculator (local)")
3. THE Streamlit thin client SHALL display the routing_path with a 🔀 prefix at the top of each response

### Requirement 11: Streamlit UI Consistency

**User Story:** As a workshop instructor, I want all three phases to maintain consistent UI elements, so that the workshop progression is visually coherent.

#### Acceptance Criteria

1. THE Streamlit thin client for Phase 3 SHALL display the 🎓 favicon
2. THE Streamlit thin client for Phase 3 SHALL display routing information in responses
3. THE Streamlit thin clients for Phase 1 and Phase 2 SHALL retain their existing 🎓 favicon and routing display functionality

### Requirement 12: Infrastructure Preservation

**User Story:** As a workshop developer, I want existing infrastructure preserved during the refactoring, so that Cognito pools, IAM roles, and deployed resources are not recreated unnecessarily.

#### Acceptance Criteria

1. THE refactoring SHALL preserve the existing CloudFormation stack (Cognito pools, IAM roles, resource servers)
2. THE refactoring SHALL preserve the existing AgentCore Memory configuration (`StudentServicesMemory` with SEMANTIC, SUMMARIZATION, USER_PREFERENCE strategies)
3. THE refactoring SHALL preserve the existing Streamlit thin client deployment on ECS Fargate
4. THE refactoring SHALL preserve the SSM parameter `/student-services/model-id` for model configuration
5. THE refactoring SHALL preserve all existing OAuth credential registrations in agentcore.json (removing only MathTeachingMcp-oauth)

### Requirement 13: Workshop Progression Narrative

**User Story:** As a workshop instructor, I want Phase 3 to clearly demonstrate the microservices-with-gateway pattern, so that the progression from monolithic to multi-agent to microservices is pedagogically clear.

#### Acceptance Criteria

1. THE Phase 3 architecture SHALL demonstrate that agent intelligence (reasoning) stays centralized while data access (tools) is distributed behind the gateway
2. THE Phase 3 README SHALL explain the architectural difference from Phase 2: same Agent-as-Tool intelligence pattern, but data-access tools decoupled behind AgentCore Gateway for independent scaling, OAuth per-service, Cedar policies, and per-tool observability
3. THE Phase 3 README SHALL explain why math teaching has no MCP server (pure computation needs no external data access)

### Requirement 14: agentcore.json Topology Update

**User Story:** As a workshop developer, I want the agentcore.json to reflect the new runtime topology, so that `agentcore deploy -y` creates the correct infrastructure.

#### Acceptance Criteria

1. THE agentcore.json SHALL define exactly 5 runtimes: StudentServicesAgent (HTTP), CourseCatalogMcp (MCP), CourseReviewsMcp (MCP), CourseRegistrationMcp (MCP), LoanApplicationMcp (MCP)
2. THE agentcore.json SHALL remove the MathTeachingMcp runtime entry
3. THE agentcore.json SHALL split the current CourseReviewMcp into two separate runtimes: CourseCatalogMcp and CourseReviewsMcp
4. WHEN the new MCP runtimes are defined, THE agentcore.json SHALL use the same Cognito pool configurations (discoveryUrl, allowedClients, allowedScopes) as appropriate for each new runtime
5. THE agentcore.json credentials section SHALL remove `MathTeachingMcp-oauth` and add credentials for `CourseCatalogMcp-oauth` and `CourseReviewsMcp-oauth` as needed

### Requirement 15: MCP Server Implementation Pattern

**User Story:** As a workshop developer, I want all dumb MCP servers to follow a consistent minimal pattern, so that the code clearly demonstrates the separation between reasoning and data access.

#### Acceptance Criteria

1. THE Dumb_MCP_Server implementations SHALL follow the pattern: FastMCP constructor, tool function with typed parameters, direct AWS SDK call, structured return value, and `mcp.run()` entrypoint
2. THE Dumb_MCP_Server implementations SHALL NOT import `strands`, `BedrockModel`, or any agent-related packages
3. THE Dumb_MCP_Server implementations SHALL use `os.environ.get()` with hardcoded working defaults for all configuration values
4. THE Dumb_MCP_Server implementations SHALL handle the `MCP_TRANSPORT` environment variable to run as streamable-http when deployed to AgentCore
