# Requirements Document

## Introduction

Refactor the directory structures across all three phases of workshop4 to achieve consistency, and rename "course_reviews" (plural) to singular "course_review" in all infrastructure, configuration, and code references. The data file `course_reviews.csv` retains its plural name. The refactoring begins with singular naming changes to infrastructure (CloudFormation, AgentCore config), then proceeds to directory flattening in Phase 1 and Phase 2, and finally agent modularization in Phase 3. Each phase is standardized to use a single `student_services/` directory containing one Python file per agent.

## Glossary

- **Phase_1**: The local Streamlit application at `workshop4/phase1/streamlit_app/` that runs agents directly in-process.
- **Phase_2**: The Dockerized Streamlit application at `workshop4/phase2/deploy-streamlit-app/docker_app/` deployed to ECS Fargate.
- **Phase_3**: The AgentCore-deployed microservices application at `workshop4/phase3/studentservices/` using BedrockAgentCoreApp.
- **Agent_Directory**: A `student_services/` directory containing one Python file per agent (orchestrator + 4 specialists).
- **Orchestrator**: The `student_services_agent.py` file that routes queries to specialist agents.
- **Specialist_Agent**: One of the four domain agents: `course_registration_agent.py`, `course_review_agent.py`, `loan_application_agent.py`, `math_teaching_agent.py`.
- **MCP_Server**: A FastMCP-based server deployed as an AgentCore runtime providing tool access via the MCP protocol.
- **AgentCore_Gateway**: The AgentCore Gateway that aggregates MCP server targets for the orchestrator.
- **CloudFormation_Stack**: An AWS CloudFormation template defining infrastructure resources.
- **SSM_Parameter**: An AWS Systems Manager Parameter Store entry used for runtime configuration.
- **DynamoDB_Table**: An AWS DynamoDB table storing application data.
- **Cognito_Pool**: An AWS Cognito User Pool providing OAuth2 authentication for AgentCore runtimes.

## Requirements

### Requirement 1: DynamoDB Table Rename

**User Story:** As a developer, I want the DynamoDB table name changed from `course_reviews` (plural) to `course_review` (singular), so that naming is consistent with the singular convention used for other resources.

#### Acceptance Criteria

1. WHEN the CloudFormation_Stack is updated, THE DynamoDB_Table logical ID SHALL be `CourseReviewTable` instead of `CourseReviewsTable`, and the physical table name SHALL be `course_review` instead of `course_reviews`.
2. WHEN the CloudFormation_Stack is updated, THE SSM_Parameter logical ID SHALL be `SSMCourseReviewTable` with path `/student-services/course-review-table` and value `course_review`, replacing the previous `SSMCourseReviewsTable` at `/student-services/course-reviews-table`.
3. WHEN the CloudFormation_Stack is updated, THE Stack Outputs SHALL export the table name under output key `CourseReviewTableName` with export name `${AWS::StackName}-CourseReviewTable`, replacing the previous `CourseReviewsTableName` and `${AWS::StackName}-CourseReviewsTable`.
4. WHEN the table is renamed, THE seed data script SHALL reference the new CloudFormation output key `CourseReviewTableName` instead of `CourseReviewsTableName` in both the `required_keys` list and the variable assignment that reads the output value.
5. WHEN the table is renamed, THE Phase_3 MCP_Server `course_review/server.py` SHALL use `COURSE_REVIEW_TABLE` as the environment variable name and `course_review` as the hardcoded fallback default value, replacing the previous `COURSE_REVIEWS_TABLE` variable name and `course_reviews` default.

### Requirement 2: Cognito Pool and OAuth Scope Rename

**User Story:** As a developer, I want the Cognito pool names and OAuth scopes updated from plural "course-reviews" to singular "course-review", so that the authentication infrastructure uses consistent naming.

#### Acceptance Criteria

1. WHEN the CloudFormation_Stack is updated, THE Cognito_Pool logical IDs SHALL use `CourseReview` prefix instead of `CourseReviews` (e.g., `CourseReviewUserPool`, `CourseReviewExecutionRole`, `CourseReviewUserPoolDomain`, `CourseReviewResourceServer`, `CourseReviewAppClient`).
2. WHEN the CloudFormation_Stack is updated, THE Cognito_Pool name SHALL be `course-review-user-pool` instead of `course-reviews-user-pool`.
3. WHEN the CloudFormation_Stack is updated, THE Cognito domain SHALL be `course-review-{AccountId}` instead of `course-reviews-{AccountId}`.
4. WHEN the CloudFormation_Stack is updated, THE resource server identifier SHALL be `course-review` instead of `course-reviews`.
5. WHEN the CloudFormation_Stack is updated, THE OAuth scope SHALL be `course-review/access` instead of `course-reviews/access`.
6. WHEN the CloudFormation_Stack is updated, THE IAM execution role name SHALL be `CourseReview-execution-role` instead of `CourseReviews-execution-role`.
7. WHEN the `agentcore.json` is updated, THE allowedScopes for the CourseReviewMcp runtime SHALL be `course-review/access` instead of `course-reviews/access`.
8. WHEN the `agentcore.json` is updated, THE credential scopes SHALL be `course-review/access` instead of `course-reviews/access`.
9. WHEN the `agentcore.json` is updated, THE discoveryUrl for the CourseReviewMcp runtime and credential SHALL reference the new Cognito User Pool ID created by the updated CloudFormation stack.

### Requirement 3: AgentCore Runtime and Credential Rename

**User Story:** As a developer, I want the AgentCore runtime, credential, and gateway target names updated from plural "CourseReviews" to singular "CourseReview", so that naming is consistent across all infrastructure.

#### Acceptance Criteria

1. WHEN the refactoring is complete, THE `agentcore.json` runtime name SHALL be `CourseReviewMcp` instead of `CourseReviewsMcp`.
2. WHEN the refactoring is complete, THE `agentcore.json` runtime executionRoleArn SHALL reference `CourseReview-execution-role` instead of `CourseReviews-execution-role`.
3. WHEN the refactoring is complete, THE `agentcore.json` credential name SHALL be `CourseReviewMcp-oauth` instead of `CourseReviewsMcp-oauth`.
4. WHEN the refactoring is complete, THE `agentcore.json` gateway target name SHALL be `coursereview` instead of `coursereviews`.
5. WHEN the refactoring is complete, THE `agentcore.json` gateway target outboundAuth credentialName SHALL be `CourseReviewMcp-oauth` instead of `CourseReviewsMcp-oauth`.
6. WHEN the refactoring is complete, THE `agentcore.json` gateway target endpoint URL SHALL contain the runtime identifier `CourseReviewMcp` instead of `CourseReviewsMcp`.
7. IF the rename is applied, THEN THE `agentcore.json` SHALL preserve all other runtime, credential, and gateway target entries unchanged (StudentServicesAgent, CourseCatalogMcp, CourseRegistrationMcp, LoanApplicationMcp and their associated credentials and targets).

### Requirement 4: Phase 3 MCP Server Directory Rename

**User Story:** As a developer, I want the Phase 3 MCP server directory renamed from `course_reviews/` to `course_review/`, so that the directory name matches the singular naming convention.

#### Acceptance Criteria

1. WHEN the refactoring is complete, THE directory `studentservices/course_reviews/` SHALL be renamed to `studentservices/course_review/`, containing the same files (`server.py`, `requirements.txt`, `pyproject.toml`) with identical content.
2. WHEN the directory is renamed, THE `agentcore.json` `codeLocation` for the `CourseReviewMcp` runtime SHALL reference `./course_review/` instead of `./course_reviews/`.
3. WHEN the directory is renamed, THE `agentcore.json` runtime name SHALL be updated from `CourseReviewsMcp` to `CourseReviewMcp` to match the singular naming convention.
4. WHEN the directory is renamed, THE `agentcore.json` credential name SHALL be updated from `CourseReviewsMcp-oauth` to `CourseReviewMcp-oauth`, and all gateway target references to the CourseReviews credential SHALL use the updated name.
5. THE MCP server code in `course_review/server.py` SHALL expose the `get_course_reviews` tool that performs a DynamoDB scan and returns course review data, with no change in tool name, input schema, or response format.

### Requirement 5: Phase 1 Directory Flattening

**User Story:** As a developer, I want Phase 1 agent code organized in a flat `student_services/` directory with one file per agent, so that the structure is consistent across all phases and easier to navigate.

#### Acceptance Criteria

1. WHEN the refactoring is complete, THE Phase_1 application SHALL contain a `streamlit_app/student_services/` directory with exactly five Python files: `student_services_agent.py`, `course_registration_agent.py`, `course_review_agent.py`, `loan_application_agent.py`, and `math_teaching_agent.py`.
2. WHEN the refactoring is complete, THE Phase_1 application SHALL NOT contain the previous per-agent subdirectories (`course_registration_agent/`, `course_review_agent/`, `loan_application_agent/`, `math_teaching_agent/`, `student_services_agent/`).
3. WHEN the refactoring is complete, THE Phase_1 `student_services/` directory SHALL contain an `__init__.py` file that imports and re-exports the `create_orchestrator` function from `student_services_agent.py` and the agent-creation function from each specialist module, making them accessible via `from student_services import create_orchestrator`.
4. THE Phase_1 `shared/` directory SHALL remain at `streamlit_app/shared/` with its existing contents (`model_factory.py`, `cross_platform_tools.py`).
5. WHEN the refactoring is complete, THE Phase_1 `app.py` SHALL import `create_orchestrator` from `student_services.student_services_agent` instead of `student_services_agent.agent`.
6. WHEN the refactoring is complete, THE Phase_1 application SHALL start without import errors and respond to a user query by routing to a specialist agent, confirming that all inter-module references have been updated to reflect the flat directory structure.
7. WHEN the refactoring is complete, each agent file in `student_services/` SHALL import shared utilities using the path `shared.model_factory` or `shared.cross_platform_tools` rather than any path referencing the removed subdirectory structure.

### Requirement 6: Phase 2 Directory Flattening

**User Story:** As a developer, I want Phase 2 agent code organized in a flat `student_services/` directory with one file per agent, so that the structure mirrors Phase 1 and Phase 3.

#### Acceptance Criteria

1. WHEN the refactoring is complete, THE Phase_2 application SHALL contain a `docker_app/student_services/` directory with exactly five Python files: `student_services_agent.py`, `course_registration_agent.py`, `course_review_agent.py`, `loan_application_agent.py`, and `math_teaching_agent.py`.
2. WHEN the refactoring is complete, THE Phase_2 application SHALL NOT contain the previous per-agent subdirectories (`course_registration_agent/`, `course_review_agent/`, `loan_application_agent/`, `math_teaching_agent/`, `student_services_agent/`).
3. WHEN the refactoring is complete, THE Phase_2 `student_services/__init__.py` SHALL export the primary factory function from each agent module (e.g., `create_orchestrator` from `student_services_agent`, and each specialist agent's creation function) so that callers can import directly from the `student_services` package.
4. THE Phase_2 `shared/` directory SHALL remain at `docker_app/shared/` with its existing contents.
5. THE Phase_2 `utils/` directory SHALL remain at `docker_app/utils/` with its existing contents.
6. WHEN the refactoring is complete, THE Phase_2 `app.py` SHALL import agents from `student_services.student_services_agent` instead of `student_services_agent.agent`.
7. WHEN the refactoring is complete, THE Phase_2 application SHALL resolve all intra-agent imports (where one agent module references another as a sub-agent tool) using the new flat package path `student_services.<module_name>` instead of the previous subdirectory path `<agent_name>.agent`.
8. WHEN the refactoring is complete, THE Phase_2 application SHALL start without import errors, confirming that all module references within `docker_app/` resolve correctly under the new directory structure.

### Requirement 7: Phase 3 Agent Modularization

**User Story:** As a developer, I want the Phase 3 monolithic `agent.py` split into separate files within `student_services/`, so that each agent is independently maintainable and the structure matches Phase 1 and Phase 2.

#### Acceptance Criteria

1. WHEN the refactoring is complete, THE Phase_3 `student_services/` directory SHALL contain exactly five agent Python files: `student_services_agent.py`, `course_registration_agent.py`, `course_review_agent.py`, `loan_application_agent.py`, and `math_teaching_agent.py`.
2. WHEN the refactoring is complete, THE Phase_3 `student_services/` directory SHALL NOT contain the previous monolithic `agent.py` file.
3. THE Phase_3 `student_services_agent.py` SHALL contain the `BedrockAgentCoreApp` entrypoint, the `ORCHESTRATOR_SYSTEM_PROMPT` constant, the `get_model_config` function, the OAuth2 `get_oauth_token` function with token caching, the `get_mcp_client` factory function, and the `invoke` entrypoint function decorated with `@app.entrypoint`.
4. WHEN the Phase_3 orchestrator imports specialist agent tools, THE `student_services_agent.py` SHALL import them from sibling modules using relative imports (e.g., `from .course_review_agent import course_review_agent`).
5. WHEN the refactoring is complete, THE Phase_3 `student_services/` directory SHALL contain an `__init__.py` file that enables the directory to function as a Python package supporting the relative imports in criterion 4.
6. THE Phase_3 `student_services/calculator.py` SHALL remain as a separate utility module, and `math_teaching_agent.py` SHALL import the `calculator` tool from it using a relative import (e.g., `from .calculator import calculator`).
7. THE Phase_3 `agentcore.json` `runtimes` entry where `name` equals `StudentServicesAgent` SHALL have its `entrypoint` field set to `student_services_agent.py` instead of `agent.py`.
8. WHEN the refactored agent files are deployed and invoked with a test prompt, THE system SHALL produce functionally equivalent responses to the monolithic `agent.py`, routing queries to the same four specialist agents (`course_review_agent`, `course_registration_agent`, `loan_application_agent`, `math_teaching_agent`) with identical tool signatures.

### Requirement 8: Import Path and Reference Updates

**User Story:** As a developer, I want all Python import paths and configuration references updated to reflect the new directory structure, so that the application runs correctly after refactoring.

#### Acceptance Criteria

1. WHEN the Phase_1 refactoring is complete, THE `config.py` function `get_course_reviews_table` SHALL be renamed to `get_course_review_table`, SHALL reference SSM parameter key `course-review-table`, SHALL use environment variable `COURSE_REVIEW_TABLE`, and SHALL use default value `course_review`.
2. WHEN the Phase_2 refactoring is complete, THE `config.py` function `get_course_reviews_table` SHALL be renamed to `get_course_review_table`, SHALL reference SSM parameter key `course-review-table`, SHALL use environment variable `COURSE_REVIEW_TABLE`, and SHALL use default value `course_review`.
3. WHEN the Phase_3 refactoring is complete, THE MCP server `course_review/server.py` SHALL use environment variable `COURSE_REVIEW_TABLE` with default value `course_review`.
4. WHEN the Phase_1 refactoring is complete, THE `course_review_agent.py` SHALL import `get_course_review_table` from `config` and SHALL use it in place of all prior references to `get_course_reviews_table`.
5. WHEN the Phase_2 refactoring is complete, THE `course_review_agent.py` SHALL import `get_course_review_table` from `config` and SHALL use it in place of all prior references to `get_course_reviews_table`.
6. WHEN any phase refactoring is complete, THE application SHALL start without raising `ImportError` or `AttributeError` related to the renamed function or updated import paths.

### Requirement 9: Data File Preservation

**User Story:** As a developer, I want the source data file `course_reviews.csv` to retain its plural name, so that the data file accurately describes its contents (multiple reviews).

#### Acceptance Criteria

1. THE data file SHALL exist at path `workshop4/phase1/data/course_reviews.csv` with the filename `course_reviews.csv` unchanged.
2. WHEN the seed data script executes, THE seed data script SHALL read from the local file `course_reviews.csv` in the `data/` directory and load its records into the DynamoDB table identified by the CloudFormation stack output key `CourseReviewTableName`.
3. WHEN the seed data script uploads files to S3, THE seed data script SHALL upload `course_reviews.csv` using the S3 object key `dynamodb/course_reviews.csv`.

### Requirement 10: Phase Execution Order

**User Story:** As a developer, I want the refactoring executed in Singular Naming → Phase 1 Flattening → Phase 2 Flattening → Phase 3 Modularization order, so that infrastructure changes propagate first and each phase can be validated independently before proceeding.

#### Acceptance Criteria

1. THE refactoring tasks SHALL be organized to complete all singular naming changes (DynamoDB table rename, Cognito pool rename, AgentCore runtime/credential rename, MCP server directory rename) before beginning any Phase_1 directory flattening changes.
2. THE refactoring tasks SHALL be organized to complete all Phase_1 file creation, modification, deletion, and import updates before beginning any Phase_2 changes.
3. THE refactoring tasks SHALL be organized to complete all Phase_2 file creation, modification, deletion, and import updates before beginning any Phase_3 agent modularization changes.
4. WHEN a phase's file changes are complete, THE refactoring process SHALL verify that all Python imports resolve correctly and no references to removed paths remain before proceeding to the next phase.
5. IF a Phase_3 infrastructure change fails during deployment, THEN THE refactoring process SHALL document the rollback steps in the task file, specifying the commands required to restore the infrastructure to its pre-Phase_3-deployment state.
6. IF a Phase_1 or Phase_2 code change causes import errors or test failures, THEN THE refactoring process SHALL resolve those errors within that phase before proceeding to the next phase.
7. THE refactoring process SHALL execute all deployments (both the CDK Streamlit thin client deployment and the AgentCore `agentcore deploy -y`) on the Ubuntu code-server, not the Windows desktop, due to Docker build requirements (CDK) and dramatically better deployment performance (AgentCore).
