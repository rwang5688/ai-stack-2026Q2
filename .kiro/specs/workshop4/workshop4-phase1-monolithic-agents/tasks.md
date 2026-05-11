# Implementation Plan: Workshop 4 Phase 1 — Monolithic Multi-Agent Student Services Assistant

## Overview

This plan implements a monolithic Streamlit desktop application with a multi-agent architecture using the Strands Agents SDK. The implementation is organized by runtime boundary (each agent in its own directory) to enable direct migration to AgentCore Runtimes in Phase 3. Infrastructure is provisioned via CloudFormation YAML. All agents are instantiated as `strands.Agent`.

## Tasks

- [x] 1. Set up project structure and deploy infrastructure
  - [x] 1.1 Create directory structure and initial files
    - Create all directories: `workshop4/phase1/cloudformation/`, `course_registration_agent/`, `course_review_agent/`, `data/`, `loan_application_agent/`, `math_teaching_agent/`, `shared/`, `streamlit_app/`, `student_services_agent/`, `tests/`, `tests/integration/`
    - Create `__init__.py` files in each agent directory, `shared/`, and `tests/`
    - Create `requirements.txt` with pinned dependencies: `strands-agents==0.1.*`, `strands-agents-tools==0.1.*`, `streamlit==1.*`, `boto3==1.*`, `hypothesis==6.*`, `pytest==8.*`
    - _Requirements: 1.1, 1.4_

  - [x] 1.2 Copy data files to `workshop4/phase1/data/`
    - Copy `course_catalog.pdf` from `.kiro/references/bedrock-agents-workshop/workshop-labs/KB-DataSource/Undergraduate-Catalog-2023-24.pdf`
    - Copy and rename `.kiro/references/bedrock-agents-workshop/workshop-labs/DB/course_registration_db_sample_data.csv` → `data/course_registrations.csv`
    - Copy and rename `.kiro/references/bedrock-agents-workshop/workshop-labs/DB/course_reviews_db_sample_data.csv` → `data/course_reviews.csv`
    - _Requirements: 2.1, 2.4, 2.5_

  - [x] 1.3 Create `cloudformation/student-services-infra.yaml`
    - S3 bucket for all data files, named `student-services-data-{AccountId}-{Region}`
    - S3 Vectors bucket as vector store for Bedrock Knowledge Base (NOT OpenSearch Serverless), named `student-services-vectors-{AccountId}-{Region}`
    - Bedrock Knowledge Base configured with S3 data source prefix `kb-datasource/` and **S3 Vectors** storage type, embedding model `amazon.titan-embed-text-v2:0`
    - DynamoDB table `course_registration` (PK: `reg_id` String) — created empty
    - DynamoDB table `course_reviews` (PK: `course_name` String) — created empty
    - SSM Parameters (all under `/student-services/` prefix):
      - `/student-services/data-bucket-name` → !Ref DataBucket
      - `/student-services/vectors-bucket-name` → !Ref VectorsBucket
      - `/student-services/knowledge-base-id` → !Ref KnowledgeBase
      - `/student-services/data-source-id` → !Ref DataSource
      - `/student-services/course-registration-table` → !Ref CourseRegistrationTable
      - `/student-services/course-reviews-table` → !Ref CourseReviewsTable
      - `/student-services/aws-region` → !Ref AWS::Region
      - `/student-services/model-provider` → `bedrock`
      - `/student-services/model-id` → `us.amazon.nova-2-lite-v1:0`
      - `/student-services/temperature` → `0.3`
    - Stack outputs: data bucket name, vectors bucket name, table names, Knowledge Base ID, data source ID
    - Ensure idempotent re-deployment (no errors on unchanged re-deploy)
    - Default region: `us-west-2`
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9_

  - [x] 1.4 Create `scripts/populate_seed_data.py`
    - Accept `--xgboost-endpoint-name` as a required CLI argument (no default — user must provide)
    - Read CloudFormation stack outputs to get bucket name, table names, KB ID, data source ID
    - Upload `data/course_catalog.pdf` to `s3://{bucket}/kb-datasource/`
    - Upload `data/course_registrations.csv` to `s3://{bucket}/dynamodb/`
    - Upload `data/course_reviews.csv` to `s3://{bucket}/dynamodb/`
    - Parse CSVs and populate DynamoDB tables via `batch_write_item`
    - Trigger Bedrock KB ingestion job (`bedrock-agent` API: `start_ingestion_job`) and wait for completion
    - Write SSM parameter `/student-services/xgboost-endpoint-name` with the user-provided endpoint name
    - Print summary of all SSM parameters written
    - _Requirements: 2.1, 2.4, 2.5, 2.10_

  - [x] 1.5 Create `deploy.sh`
    - Accept XGBoost endpoint name as first argument: `./deploy.sh <xgboost-endpoint-name>`
    - Step 1: `aws cloudformation deploy --stack-name student-services-infra --template-file cloudformation/student-services-infra.yaml --capabilities CAPABILITY_IAM --region us-west-2`
    - Step 2: `python scripts/populate_seed_data.py --xgboost-endpoint-name $1`
    - Fail with usage message if endpoint name not provided
    - _Requirements: 2.7, 2.11_

  - [ ]* 1.6 Validate CloudFormation template
    - Validate template syntax with `aws cloudformation validate-template`
    - Verify all expected outputs are declared
    - Verify DynamoDB table key schemas match design
    - _Requirements: 2.6, 2.7_

- [x] 2. Checkpoint - Deploy infrastructure and verify prerequisites
  - Run `./deploy.sh` (deploys CloudFormation stack, uploads data to S3, seeds DynamoDB, triggers KB ingestion)
  - Verify S3 data bucket has files under `kb-datasource/` and `dynamodb/` prefixes
  - Verify DynamoDB tables are populated with sample data
  - Verify Bedrock KB ingestion job completed successfully
  - Verify SageMaker Serverless Endpoint is accessible (pre-existing, user-deployed)
  - Ask the user if questions arise.

- [x] 3. Implement shared utilities and configuration
  - [x] 3.1 Implement `shared/cross_platform_tools.py`
    - Adapt from `.kiro/references/workshop4/multi_agent/cross_platform_tools.py`
    - Provide `get_math_tools()` returning `[calculator]` from `strands_tools`
    - Handle Windows/Linux/macOS platform detection with graceful fallbacks
    - Export `get_platform_capabilities()` for debugging
    - _Requirements: 1.6_

  - [x] 3.2 Implement `shared/model_factory.py`
    - Adapt from `.kiro/references/workshop4/multi_agent/model_factory.py` and `.kiro/references/workshop4/multi_agent/bedrock_model.py`
    - Create `create_model_from_config(config: dict)` function
    - Support `"bedrock"` provider → `BedrockModel` and `"sagemaker"` provider → `SageMakerAIModel`
    - Validate: raise `ValueError` if provider not in `["bedrock", "sagemaker"]` with message listing supported providers
    - Validate: raise `ValueError` if `model_id` is missing
    - Validate: raise `ValueError` if temperature is outside 0.0–1.0 range
    - Pass temperature to model instance when provided and valid
    - Default region to `us-west-2`
    - _Requirements: 3.1, 3.2, 3.3, 3.5, 3.6, 3.7_

  - [ ]* 3.3 Write property tests for `shared/model_factory.py`
    - **Property 1: Invalid provider raises ValueError** — For any string not in ["bedrock", "sagemaker"], `create_model_from_config` raises ValueError mentioning both supported providers. Use `hypothesis.strategies.text().filter(lambda s: s not in ["bedrock", "sagemaker"])`.
    - **Property 2: Valid temperature is passed through** — For any float in [0.0, 1.0], model is created with that temperature. Use `st.floats(min_value=0.0, max_value=1.0)`.
    - **Property 3: Invalid temperature raises ValueError** — For any float outside [0.0, 1.0] (excluding NaN/inf), raises ValueError. Use `st.floats().filter(lambda x: not math.isnan(x) and not math.isinf(x) and (x < 0.0 or x > 1.0))`.
    - **Validates: Requirements 3.3, 3.5, 3.6**

  - [x] 3.4 Implement `streamlit_app/config.py`
    - Adapt from `.kiro/references/workshop4/multi_agent/config.py`
    - Implement getter functions: `get_model_config()`, `get_knowledge_base_id()`, `get_data_source_id()`, `get_xgboost_endpoint()`, `get_aws_region()`, `get_course_registration_table()`, `get_course_reviews_table()`
    - Implement `clear_parameter_cache()` to allow refreshing SSM params without restarting the app
    - Implement `get_all_config_values()` for the debug sidebar display
    - Use `get_parameters_by_path` to batch-fetch all params under `/student-services/` prefix
    - Resolution order: environment variable → SSM Parameter Store (`/student-services/{param-name}`) → hardcoded default
    - Default region: `us-west-2`
    - Use `@lru_cache` for SSM parameter fetching
    - _Requirements: 3.4_

- [x] 4. Checkpoint - Ensure shared utilities and config work
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement specialist agents
  - [x] 5.1 Implement `course_review_agent/agent.py`
    - Adapt from `.kiro/references/bedrock-agents-workshop/workshop-labs/Code/courses-agent-group-courses-review.py`
    - Create `@tool` function `retrieve_course_catalog(query: str) -> str` that queries Bedrock Knowledge Base using `boto3` `bedrock-agent-runtime` client with `retrieve_and_generate` or `retrieve` API, returning top 5 results
    - Create `@tool` function `query_course_reviews(course_name: str) -> str` that queries DynamoDB `course_reviews` table by partition key `course_name`, returning up to 10 records
    - Create `@tool` function `course_review_assistant(query: str) -> str` that instantiates a `strands.Agent` with `[retrieve_course_catalog, query_course_reviews]` tools and a system prompt instructing it to combine KB and review results
    - Handle empty KB results with "No matching courses found" message
    - Handle empty DynamoDB results with "No reviews available" message
    - Use 30-second timeout on AWS SDK calls via `botocore.config.Config(read_timeout=30)`
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 10.2_

  - [x] 5.2 Implement `course_registration_agent/agent.py`
    - Adapt from `.kiro/references/bedrock-agents-workshop/workshop-labs/Code/courses-agent-group-courses-registration.py`
    - Create `@tool` function `register_student(student_id: str, course_name: str, semester: str) -> str` that writes to DynamoDB `course_registration` table with UUID `reg_id`
    - Validate all three parameters are non-empty; return error listing missing params if any are absent
    - On success, return confirmation with course name and reg_id
    - On DynamoDB failure, return sanitized error (no ARNs, no table names in user message)
    - Create `@tool` function `course_registration_assistant(query: str) -> str` that instantiates a `strands.Agent` with `[register_student]` tool
    - Use 30-second timeout on AWS SDK calls
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 10.2_

  - [x] 5.3 Implement `loan_application_agent/agent.py`
    - Adapt from `.kiro/references/workshop4/multi_agent/loan_offering_assistant.py`
    - Create validation function `validate_csv_features(payload: str) -> tuple[bool, int]` that checks for exactly 59 comma-separated values
    - Create interpretation function `interpret_prediction(score: float) -> dict` returning `{"label": str, "confidence": float}` — "Accept" with `round(score*100, 1)` if score ≥ 0.5, "Reject" with `round((1-score)*100, 1)` if score < 0.5
    - Create `@tool` function `loan_prediction(payload: str) -> str` that validates features, invokes SageMaker endpoint (name from config), and returns formatted result
    - Sanitize errors: never expose endpoint name, ARN, or account ID in user-facing messages
    - Create `@tool` function `loan_offering_assistant(query: str) -> str` that instantiates a `strands.Agent` with `[loan_prediction]` tool
    - Use 30-second timeout on SageMaker invocation
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 10.2_

  - [ ]* 5.4 Write property tests for loan prediction logic
    - **Property 4: Prediction score interpretation** — For any float in [0.0, 1.0], verify correct label and confidence calculation. Use `st.floats(min_value=0.0, max_value=1.0)`.
    - **Property 5: Error messages do not leak sensitive information** — For any exception containing endpoint name/ARN/account ID, verify user-facing message does not contain those strings. Use `st.text()` for endpoint names.
    - **Property 6: Invalid feature count is rejected with correct counts** — For any N ≠ 59, verify error message states expected=59 and actual=N. Use `st.integers(min_value=0, max_value=200).filter(lambda n: n != 59)`.
    - **Validates: Requirements 7.2, 7.3, 7.5, 7.6**

  - [x] 5.5 Implement `math_teaching_agent/agent.py`
    - Adapt from `.kiro/references/workshop4/multi_agent/math_assistant.py`
    - Import `calculator` from `strands_tools` (via `shared/cross_platform_tools.py` `get_math_tools()`)
    - Create `@tool` function `math_assistant(query: str) -> str` that instantiates a `strands.Agent` with calculator tools and a system prompt instructing step-by-step solutions with intermediate calculations and real-world analogies
    - Handle non-math queries with a message suggesting how to rephrase
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 6. Checkpoint - Ensure specialist agents are implemented
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement orchestrator and Streamlit UI
  - [x] 7.1 Implement `student_services_agent/agent.py`
    - Create `create_orchestrator(model_config: dict) -> Agent` function
    - Import all specialist `@tool` functions: `course_registration_assistant`, `course_review_assistant`, `loan_offering_assistant`, `math_assistant`
    - Instantiate `strands.Agent` with tools list `[course_registration_assistant, course_review_assistant, loan_offering_assistant, math_assistant]`
    - System prompt instructs routing: registration → `course_registration_assistant`, course info/reviews → `course_review_assistant`, loans → `loan_offering_assistant`, math → `math_assistant`, out-of-domain → respond with available services list
    - Wrap specialist tool calls in try/except to catch exceptions and return user-friendly error identifying which service is unavailable
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 10.1_

  - [ ]* 7.2 Write property tests for orchestrator error handling
    - **Property 7: Whitespace-only messages are not processed** — For any whitespace-only string, verify it is not passed to the orchestrator. Use `st.text(alphabet=st.characters(whitespace_only=True))`.
    - **Property 8: Specialist exceptions are caught and reported** — For any specialist that raises an exception, verify the error message identifies the service without exposing stack traces. Use `st.sampled_from(["course_registration", "course_review", "loan_offering", "math"])`.
    - **Validates: Requirements 9.3, 10.1**

  - [x] 7.3 Implement `streamlit_app/app.py`
    - Adapt from `.kiro/references/workshop4/multi_agent/app.py`
    - Set `os.environ["BYPASS_TOOL_CONSENT"] = "true"` at startup to suppress tool consent prompts
    - Sidebar with model selection dropdown (options: `us.amazon.nova-2-lite-v1:0`, `us.anthropic.claude-sonnet-4-6`)
    - Sidebar with "Sample Questions" section showing example prompts for each specialist agent (course review, course registration, loan prediction, math tutoring)
    - Sidebar with expandable "Debug Info" section showing all current config values (model, region, KB ID, endpoint names, table names)
    - Sidebar with "Clear Cache" button that calls `clear_parameter_cache()` to refresh SSM params without restart
    - On model change, recreate orchestrator agent with new model via Model Factory
    - Initialize session state with `messages` list, `orchestrator` (cached agent instance), and `selected_model`
    - Display chat interface with `st.chat_message` for role-based visual distinction
    - Filter empty/whitespace-only messages before processing
    - Show `st.spinner` loading indicator during agent processing
    - On response, append both user and assistant messages to session state
    - Provide "Clear Conversation" button that resets `st.session_state.messages`
    - Wrap orchestrator call in try/except; on error display message in chat and return to input-ready state
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 10.3_

- [x] 8. Checkpoint - Ensure orchestrator and UI work end-to-end
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Create README and documentation
  - [ ] 9.1 Create `workshop4/phase1/README.md`
    - Document setup prerequisites (Python version, AWS CLI, SageMaker endpoint pre-deployed)
    - Document all environment variables with name, description, example value, and default
    - Step-by-step instructions for deploying CloudFormation stack (`aws cloudformation deploy`)
    - Step-by-step instructions for running Streamlit app locally (expected URL/port)
    - "Design Decisions" section: MCP Server vs `@tool` (using Course Registration Agent as example of when MCP is unnecessary vs when MCP is appropriate for reusable interfaces)
    - "Design Decisions" section: runtime-boundary directory structure explanation (enables independent agent evolution and Phase 3 AgentCore migration)
    - _Requirements: 1.1, 1.2, 1.3, 1.5, 1.7, 1.8_

- [ ] 10. Final checkpoint - Ensure all tests pass and app runs end-to-end
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- All agents MUST be instantiated as `strands.Agent` — no custom Agent classes
- IaC uses CloudFormation YAML (not CDK) for Workshop Studio compatibility
- Default region is `us-west-2` throughout
- SageMaker XGBoost endpoint is a pre-existing external dependency (endpoint name from env var)
- Reference implementations: `.kiro/references/workshop4/multi_agent/` and `.kiro/references/bedrock-agents-workshop/workshop-labs/`

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "1.3"] },
    { "id": 2, "tasks": ["1.4", "1.5", "1.6"] },
    { "id": 3, "tasks": ["3.1", "3.2", "3.3", "3.4"] },
    { "id": 4, "tasks": ["5.1", "5.2", "5.3", "5.5"] },
    { "id": 5, "tasks": ["5.4", "7.1"] },
    { "id": 6, "tasks": ["7.2", "7.3"] },
    { "id": 7, "tasks": ["9.1"] }
  ]
}
```
