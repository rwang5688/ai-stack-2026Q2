# Requirements Document

## Introduction

Phase 1 of the Student Services Assistant workshop: a monolithic Streamlit desktop application implementing a multi-agent architecture using Strands Agents SDK and Amazon Bedrock Models. The application demonstrates five agentic AI patterns (orchestrator routing, RAG, MCP server writes, SageMaker inference, and generative Bedrock invocation) within a single local process. Infrastructure-as-Code provisions the required AWS resources (S3, DynamoDB, Bedrock Knowledge Base).

## Glossary

- **Streamlit_App**: The monolithic Python Streamlit application serving as the user interface and runtime host for all agents and MCP servers
- **Student_Services_Agent**: The orchestrator agent, instantiated as `strands.Agent` from the Strands Agents SDK, responsible for interpreting user intent and routing requests to the appropriate specialist agent
- **Course_Review_Agent**: A specialist agent, instantiated as `strands.Agent` from the Strands Agents SDK, that searches the Bedrock Knowledge Base for course catalog information and queries DynamoDB for course reviews
- **Course_Registration_Agent**: A specialist agent, instantiated as `strands.Agent` from the Strands Agents SDK, that registers students to courses by writing to DynamoDB
- **Loan_Application_Agent**: A specialist agent, instantiated as `strands.Agent` from the Strands Agents SDK, that invokes a SageMaker Serverless Endpoint running an XGBoost model to predict loan acceptance
- **Math_Teaching_Agent**: A specialist agent, instantiated as `strands.Agent` from the Strands Agents SDK, that uses Bedrock Models and calculator tools to provide step-by-step math education
- **Model_Factory**: A module that creates Bedrock or SageMaker model instances from a configuration dictionary, supporting multiple model providers
- **Bedrock_Knowledge_Base**: An Amazon Bedrock Knowledge Base backed by an S3 data source (undergraduate course catalog PDF) and an S3-based vector store
- **IaC_Stack**: The CloudFormation stack (YAML template) that provisions foundational AWS resources required by the application (S3 buckets, DynamoDB tables, Bedrock Knowledge Base). CloudFormation YAML is the default IaC choice for Workshop Studio compatibility. CDK is only used when required by specific tooling (deploy-streamlit-app in Phase 2, AgentCore CLI in Phase 3).

## Requirements

### Requirement 1: Project Structure and Documentation

**User Story:** As a workshop participant, I want clear documentation and a well-organized project structure, so that I can understand and run the application independently.

#### Acceptance Criteria

1. THE Streamlit_App SHALL reside in the workshop4/phase1/ directory with a README.md documenting setup, prerequisites, deployment, and usage instructions
2. THE README.md SHALL document all required environment variables and configuration parameters, including for each variable: the variable name, a description of its purpose, an example value, and whether a default is provided
3. THE README.md SHALL include step-by-step instructions for deploying the IaC stack and running the Streamlit application locally, including the expected verification outcome at the final step (such as the URL and port where the application becomes accessible)
4. THE project SHALL include a requirements.txt or pyproject.toml listing all Python dependencies with exact version pins (using == specifiers)
5. THE README.md SHALL specify the minimum required Python version in the prerequisites section
6. THE Streamlit_App SHALL run on both Windows and Linux/macOS by using a cross-platform tools module that dynamically imports platform-specific Strands tools (e.g., shell and python_repl are unavailable on Windows) and provides fallbacks
6. THE README.md SHALL list as a prerequisite that a SageMaker Serverless Inference Endpoint running a pre-trained XGBoost loan acceptance prediction model must already be deployed, and SHALL document the expected endpoint name configuration variable
7. THE README.md SHALL include a "Design Decisions" section that explains when and why to use an MCP Server interface versus a Strands `@tool`, using the Course Registration Agent as a concrete example of when MCP is unnecessary (single-purpose, tightly-coupled DynamoDB operation) and contrasting with scenarios where MCP is appropriate (reusable application interfaces consumed by multiple agents or use cases, such as GitHub, Slack, or Jira integrations)
8. THE README.md SHALL include in the "Design Decisions" section an explanation of the runtime-boundary directory structure, explaining that each specialist agent resides in its own directory so that agents can be added, removed, or evolved independently, and that this organization enables direct migration to independent AgentCore Runtimes in Phase 3

### Requirement 2: Infrastructure as Code (IaC Stack) and Data Seeding

**User Story:** As a workshop participant, I want a single deploy script that provisions all required AWS resources and populates them with data, so that I can set up the backend infrastructure and verify it works before writing agent code.

#### Acceptance Criteria

1. THE IaC_Stack SHALL create an S3 bucket named `student-services-data-{AccountId}-{Region}` for storing KB data source files and DynamoDB seed data
2. THE IaC_Stack SHALL create an S3 Vectors bucket named `student-services-vectors-{AccountId}-{Region}` as the vector store for the Bedrock Knowledge Base (NOT OpenSearch Serverless, which is prohibitively expensive for workshop/demo use)
3. THE IaC_Stack SHALL create a Bedrock Knowledge Base configured with the S3 data source bucket (prefix `kb-datasource/`), S3 Vectors storage type, and embedding model `amazon.titan-embed-text-v2:0`
4. THE IaC_Stack SHALL create a DynamoDB table named `course_registration` with partition key `reg_id` (String)
5. THE IaC_Stack SHALL create a DynamoDB table named `course_reviews` with partition key `course_name` (String)
6. THE IaC_Stack SHALL output the resource identifiers (data bucket name, vectors bucket name, table names, Knowledge Base ID, data source ID) as CloudFormation stack outputs
7. THE IaC_Stack SHALL be deployable via `aws cloudformation deploy` and complete successfully within 15 minutes
8. IF the IaC_Stack is deployed when the stack already exists with no template changes, THEN THE IaC_Stack SHALL complete without error (idempotent re-deployment)
9. IF the IaC_Stack deployment fails, THEN THE IaC_Stack SHALL automatically roll back all resources to their previous state
10. A `scripts/populate_seed_data.py` script SHALL read CloudFormation stack outputs, upload `data/course_catalog.pdf` to `s3://{bucket}/kb-datasource/`, upload CSV files to `s3://{bucket}/dynamodb/`, populate DynamoDB tables via `batch_write_item`, and trigger Bedrock KB ingestion job
11. A `deploy.sh` script SHALL execute the CloudFormation deploy followed by `python scripts/populate_seed_data.py` as a single deployment workflow

### Requirement 3: Model Factory and Provider Configuration

**User Story:** As a workshop instructor, I want to configure which foundation model provider and model ID the agents use, so that I can demonstrate the application with different models (Amazon Nova 2, Anthropic Claude 4.x, OpenAI GPT 5.x).

#### Acceptance Criteria

1. IF the provider configuration specifies "bedrock", THEN THE Model_Factory SHALL create a BedrockModel instance using the configured model_id
2. IF the provider configuration specifies "sagemaker", THEN THE Model_Factory SHALL create a SageMakerAIModel instance using the configured model_id
3. IF an unsupported provider value is specified, THEN THE Model_Factory SHALL raise a ValueError with a message listing the supported providers ("bedrock", "sagemaker")
4. THE Model_Factory SHALL accept configuration via environment variables, and SHALL fall back to AWS SSM Parameter Store when the environment variables are not set
5. WHEN a model configuration includes a temperature parameter with a value between 0.0 and 1.0 inclusive, THE Model_Factory SHALL pass the temperature value to the created model instance
6. IF a temperature value outside the range 0.0 to 1.0 is specified, THEN THE Model_Factory SHALL raise a ValueError indicating the valid temperature range
7. THE Model_Factory SHALL require both a provider value and a model_id value in the configuration, and SHALL raise a ValueError indicating the missing parameter if either is absent

### Requirement 4: Student Services Orchestrator Agent

**User Story:** As a student, I want a single conversational agent that understands my intent and routes my request to the right specialist, so that I do not need to know which service to use.

#### Acceptance Criteria

1. WHEN a user message relates to course information or course reviews, THE Student_Services_Agent SHALL route the request to the Course_Review_Agent and return the specialist's response to the user
2. WHEN a user message relates to course registration, THE Student_Services_Agent SHALL route the request to the Course_Registration_Agent and return the specialist's response to the user
3. WHEN a user message relates to loan applications or loan predictions, THE Student_Services_Agent SHALL route the request to the Loan_Application_Agent and return the specialist's response to the user
4. WHEN a user message relates to mathematics problems or math tutoring, THE Student_Services_Agent SHALL route the request to the Math_Teaching_Agent and return the specialist's response to the user
5. THE Student_Services_Agent SHALL expose each specialist agent as a Strands tool so that the orchestrator uses the Strands Agents tool-calling mechanism for routing
6. IF the user message does not match any specialist domain, THEN THE Student_Services_Agent SHALL respond directly with a message that lists the available specialist domains (course information and reviews, course registration, loan applications, and math tutoring) and invites the user to rephrase their request
7. IF the user message is ambiguous and could match more than one specialist domain, THEN THE Student_Services_Agent SHALL select the single most relevant specialist based on the primary intent of the message and route the request to that specialist
8. WHEN the Student_Services_Agent receives a user message, THE Student_Services_Agent SHALL determine routing and return a response within 30 seconds

### Requirement 5: Course Review Agent (RAG Pattern)

**User Story:** As a student, I want to search for courses matching my requirements and read reviews from other students, so that I can make informed course selection decisions.

#### Acceptance Criteria

1. WHEN a course search query is received, THE Course_Review_Agent SHALL query the Bedrock_Knowledge_Base to retrieve the top 5 matching course catalog entries ranked by similarity score
2. WHEN a course name is identified, THE Course_Review_Agent SHALL query the DynamoDB course_reviews table using the course_name partition key and return up to 10 review records
3. WHEN both the knowledge base search and the DynamoDB review query have completed, THE Course_Review_Agent SHALL return a single response containing a course information section (from the knowledge base) and a student reviews section (from DynamoDB)
4. IF the Bedrock_Knowledge_Base returns no matching results, THEN THE Course_Review_Agent SHALL inform the user that no matching courses were found and suggest refining the search terms
5. IF the DynamoDB query returns no review records, THEN THE Course_Review_Agent SHALL inform the user that no reviews are available for the specified course while still presenting any course catalog information retrieved from the knowledge base

### Requirement 6: Course Registration Agent (DynamoDB Write Pattern)

**User Story:** As a student, I want to register for courses by providing my student ID, course name, and semester, so that my enrollment is recorded.

#### Acceptance Criteria

1. WHEN a registration request is received with student_id, course_name, and semester, THE Course_Registration_Agent SHALL write a new item to the DynamoDB course_registration table with a generated reg_id (UUID), storing student_id, course_name, and semester as attributes
2. WHEN registration succeeds, THE Course_Registration_Agent SHALL return a confirmation message including the course name and registration ID
3. IF any required parameter (student_id, course_name, or semester) is missing, THEN THE Course_Registration_Agent SHALL return an error message specifying which parameters are missing
4. IF the DynamoDB write operation fails, THEN THE Course_Registration_Agent SHALL return an error message describing the failure without exposing internal AWS error details

### Requirement 7: Loan Application Agent (SageMaker Inference Pattern)

**User Story:** As a student, I want to check my eligibility for a student loan by providing my demographic information, so that I can understand my likelihood of approval before applying.

**Assumption:** A SageMaker Serverless Inference Endpoint running a pre-trained XGBoost model for loan acceptance prediction already exists. The endpoint accepts a CSV payload of 59 features representing customer demographics and engagement information, and returns a float prediction score. Deploying this endpoint is out of scope for this spec.

#### Acceptance Criteria

1. WHEN a loan prediction request is received with a CSV payload of exactly 59 features, THE Loan_Application_Agent SHALL invoke the configured SageMaker Serverless Endpoint with the payload using content type text/csv
2. WHEN the SageMaker endpoint returns a prediction score greater than or equal to 0.5, THE Loan_Application_Agent SHALL report the prediction as "Accept" with a confidence percentage calculated as the score multiplied by 100 and rounded to 1 decimal place
3. WHEN the SageMaker endpoint returns a prediction score less than 0.5, THE Loan_Application_Agent SHALL report the prediction as "Reject" with a confidence percentage calculated as (1 minus the score) multiplied by 100 and rounded to 1 decimal place
4. THE Loan_Application_Agent SHALL read the SageMaker endpoint name from configuration (environment variable or SSM Parameter Store)
5. IF the SageMaker endpoint invocation fails, THEN THE Loan_Application_Agent SHALL return an error message indicating the prediction service is unavailable without exposing the endpoint name, ARN, or internal error details to the user
6. IF a loan prediction request is received with a CSV payload that does not contain exactly 59 features, THEN THE Loan_Application_Agent SHALL reject the request and return an error message indicating the expected number of features and the number actually provided

### Requirement 8: Math Teaching Agent (Generative Bedrock Pattern)

**User Story:** As a student, I want a math tutoring assistant that solves problems step-by-step and explains concepts, so that I can learn mathematical reasoning.

#### Acceptance Criteria

1. WHEN a math problem is submitted, THE Math_Teaching_Agent SHALL provide a solution broken into numbered steps where each step contains the mathematical operation performed and a natural-language explanation of why that operation is applied
2. THE Math_Teaching_Agent SHALL use calculator tools for performing arithmetic, algebraic, geometric, and statistical computations to ensure numerical accuracy in solutions
3. WHEN presenting solutions, THE Math_Teaching_Agent SHALL show intermediate calculations and, for problems involving quantities or measurements, relate the concept to a real-world analogy or application
4. IF the submitted query does not contain a recognizable mathematical expression, equation, or word problem requesting a numeric or symbolic result, THEN THE Math_Teaching_Agent SHALL respond with a message indicating the input was not recognized as a math problem and suggest how the user can rephrase it as a mathematical question
5. IF the Math_Teaching_Agent cannot solve the submitted problem due to unsupported problem type or computational limitations, THEN THE Math_Teaching_Agent SHALL inform the user that the problem cannot be solved, state the reason, and suggest alternative approaches or resources

### Requirement 9: Streamlit Chat Interface

**User Story:** As a student, I want a chat-based interface so that I can interact with the Student Services Assistant using natural language.

#### Acceptance Criteria

1. WHEN the Streamlit_App is launched, THE Streamlit_App SHALL display a chat interface with a text input field and a message history panel that visually distinguishes user messages from assistant messages by role
2. WHEN a user submits a non-empty message, THE Streamlit_App SHALL immediately display the user message in the message history, pass the message to the Student_Services_Agent, and display the agent response in the message history upon completion
3. IF a user submits an empty or whitespace-only message, THEN THE Streamlit_App SHALL not send the message to the Student_Services_Agent and SHALL not add an entry to the message history
4. WHILE the Student_Services_Agent is processing a request, THE Streamlit_App SHALL display a loading indicator to the user
5. THE Streamlit_App SHALL maintain conversation history in session state so that messages persist across Streamlit reruns within the same browser session but are cleared when the browser tab is closed or the session expires. Cross-session memory is not supported in Phase 1 or Phase 2; it is introduced in Phase 3 via AgentCore Memory.
6. THE Streamlit_App SHALL provide a control to clear the conversation history and start a new conversation without reloading the page
7. THE Streamlit_App SHALL provide a sidebar dropdown for selecting the Bedrock model (options: `us.amazon.nova-2-lite-v1:0`, `us.anthropic.claude-sonnet-4-6`), and SHALL recreate the orchestrator agent with the newly selected model when the selection changes

### Requirement 10: Error Handling and Resilience

**User Story:** As a student, I want the application to handle errors gracefully, so that a failure in one specialist agent does not crash the entire application.

#### Acceptance Criteria

1. IF a specialist agent raises an exception during processing, THEN THE Student_Services_Agent SHALL catch the exception and return an error message to the user that identifies which service is unavailable and suggests the user try again or rephrase their request, without terminating the session
2. IF an AWS service call (DynamoDB, SageMaker, Bedrock) does not respond within 30 seconds or returns an error, THEN the calling agent SHALL return an error message to the orchestrator that identifies the failing service and the nature of the failure (timeout or service error)
3. WHEN an error occurs in any agent, THE Streamlit_App SHALL return to an input-ready state within 3 seconds, preserve the existing conversation history, and allow the user to submit new messages
