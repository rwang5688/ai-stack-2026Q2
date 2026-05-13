# Design Document: Workshop 4 Phase 1 — Monolithic Multi-Agent Student Services Assistant

## Overview

This design describes a monolithic Streamlit desktop application that implements a multi-agent architecture using the Strands Agents SDK. The application demonstrates four agentic AI patterns within a single local process:

1. **Orchestrator routing** — A Student Services Agent routes user intent to specialist agents
2. **RAG** — Course Review Agent combines Bedrock Knowledge Base retrieval with DynamoDB queries
3. **DynamoDB writes** — Course Registration Agent writes enrollment records to DynamoDB
4. **SageMaker inference** — Loan Application Agent invokes a pre-existing XGBoost endpoint
5. **Generative Bedrock invocation** — Math Teaching Agent uses calculator tools for step-by-step math education

All agents are instantiated as `strands.Agent` from the Strands Agents SDK. Specialist agents are exposed as Strands tools to the orchestrator using the "agents-as-tools" pattern. Infrastructure is provisioned via a CloudFormation YAML template.

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| CloudFormation YAML (not CDK) | Workshop Studio compatibility requirement |
| `strands.Agent` for all agents | SDK standard; enables agents-as-tools pattern natively |
| `@tool` decorator for specialist wrappers | Gives full control over error handling and response formatting |
| Directory structure as self-contained app | All agents and shared code inside `streamlit_app/` — the app is one deployable unit |
| Environment variables with SSM fallback | Supports both local dev (env vars) and deployed environments (SSM) |
| `strands_tools.calculator` for math | Cross-platform, no shell dependency |
| "Routing to..." status in UI | Each specialist `@tool` prefixes its return value with `[Agent Name]` — callbacks and LLM instructions are unreliable |

## Architecture

```mermaid
graph TD
    User([Student]) --> UI[Streamlit Chat Interface]
    UI --> Orchestrator[Student Services Agent<br/>strands.Agent]
    
    Orchestrator -->|tool call| CRA[course_review_assistant<br/>@tool wrapper]
    Orchestrator -->|tool call| CRegA[course_registration_assistant<br/>@tool wrapper]
    Orchestrator -->|tool call| LoanA[loan_offering_assistant<br/>@tool wrapper]
    Orchestrator -->|tool call| MathA[math_assistant<br/>@tool wrapper]
    
    CRA --> CRAgent[Course Review Agent<br/>strands.Agent]
    CRAgent -->|retrieve tool| KB[Bedrock Knowledge Base]
    CRAgent -->|query tool| DDB_Reviews[(DynamoDB<br/>course_reviews)]
    
    CRegA --> CRegAgent[Course Registration Agent<br/>strands.Agent]
    CRegAgent -->|register tool| DDB_Reg[(DynamoDB<br/>course_registration)]
    
    LoanA --> LoanAgent[Loan Application Agent<br/>strands.Agent]
    LoanAgent -->|prediction tool| SM[SageMaker Endpoint<br/>XGBoost]
    
    MathA --> MathAgent[Math Teaching Agent<br/>strands.Agent]
    MathAgent -->|calculator| Calc[strands_tools.calculator]
    
    KB --> S3_Data[(S3 Data Source<br/>Course Catalog PDF)]
    KB --> S3_Vec[(S3 Vector Store)]

    subgraph AWS Cloud
        KB
        S3_Data
        S3_Vec
        DDB_Reviews
        DDB_Reg
        SM
    end
    
    subgraph "Local Process (Streamlit App)"
        UI
        Orchestrator
        CRA
        CRegA
        LoanA
        MathA
        CRAgent
        CRegAgent
        LoanAgent
        MathAgent
        Calc
    end
```

### Data Flow

1. User submits a message via the Streamlit chat interface
2. Streamlit passes the message to the Student Services Agent (orchestrator)
3. The orchestrator's LLM determines intent and calls the appropriate specialist tool
4. The specialist `@tool` function instantiates a specialist `strands.Agent` with domain-specific tools
5. The specialist agent processes the request using its tools (KB retrieval, DynamoDB, SageMaker, calculator)
6. The response propagates back: specialist agent → `@tool` return → orchestrator → Streamlit UI

## Components and Interfaces

### Directory Structure

```
workshop4/phase1/
├── cloudformation/
│   └── student-services-infra.yaml    # CloudFormation IaC template
├── data/
│   ├── course_catalog.pdf             # Bedrock KB data source
│   ├── course_registrations.csv       # Sample registration data for DynamoDB
│   └── course_reviews.csv             # Sample review data for DynamoDB
├── scripts/
│   └── populate_seed_data.py          # Upload data to S3, seed DynamoDB, trigger KB ingestion
├── streamlit_app/                     # Self-contained application package
│   ├── __init__.py
│   ├── app.py                         # Streamlit entry point
│   ├── config.py                      # Configuration (env vars + SSM fallback)
│   ├── course_registration_agent/     # DynamoDB write specialist
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── course_review_agent/           # RAG specialist (KB + DynamoDB read)
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── loan_application_agent/        # SageMaker inference specialist
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── math_teaching_agent/           # Generative Bedrock specialist
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── shared/                        # Shared utilities across agents
│   │   ├── __init__.py
│   │   ├── cross_platform_tools.py    # Platform-specific tool imports
│   │   └── model_factory.py           # Model creation from config dict
│   └── student_services_agent/        # Orchestrator agent
│       ├── __init__.py
│       └── agent.py
├── tests/
│   └── integration/
├── .env / .env.example
├── deploy-infra.sh                    # Deploy CloudFormation stack
├── populate-seed-data.sh              # Seed data script wrapper
├── README.md
└── requirements.txt
```

All application code (agents, shared modules, config) lives inside `streamlit_app/` as a self-contained package. Infrastructure, data, and scripts remain at the phase1 root. The Streamlit app is run from the phase1 root with `streamlit run streamlit_app/app.py`.

### Component: `cloudformation/student-services-infra.yaml` (CloudFormation)

Provisions:
- S3 bucket for KB data source (course catalog PDF) — named `student-services-data-{AccountId}-{Region}`
- S3 bucket for KB vector store (**S3 Vectors**, NOT OpenSearch Serverless) — named `student-services-vectors-{AccountId}-{Region}`
- Bedrock Knowledge Base with S3 data source prefix `kb-datasource/` and S3 Vectors storage configuration, embedding model `amazon.titan-embed-text-v2:0`
- DynamoDB table `course_registration` (PK: `reg_id` String) — created empty
- DynamoDB table `course_reviews` (PK: `course_name` String) — created empty
- SSM Parameters (all under `/student-services/` prefix):
  - `/student-services/data-bucket-name`
  - `/student-services/vectors-bucket-name`
  - `/student-services/knowledge-base-id`
  - `/student-services/data-source-id`
  - `/student-services/course-registration-table`
  - `/student-services/course-reviews-table`
  - `/student-services/aws-region` → `us-west-2`
  - `/student-services/model-provider` → `bedrock`
  - `/student-services/model-id` → `us.amazon.nova-2-lite-v1:0` (also supports `us.anthropic.claude-sonnet-4-6`)
  - `/student-services/temperature` → `0.3`
- Stack outputs: data bucket name, vectors bucket name, table names, Knowledge Base ID, data source ID

### Component: `course_registration_agent/agent.py` (DynamoDB Write)

```python
from strands import Agent, tool

@tool
def register_student(student_id: str, course_name: str, semester: str) -> str:
    """
    Write registration record to DynamoDB course_registration table.
    Generates UUID for reg_id. Returns confirmation or error message.
    Validates required parameters before writing.
    """

@tool
def course_registration_assistant(query: str) -> str:
    """
    Specialist tool exposed to orchestrator.
    Instantiates a Course Registration Agent with the register_student tool.
    """
```

### Component: `course_review_agent/agent.py` (RAG)

```python
from strands import Agent, tool

@tool
def retrieve_course_catalog(query: str) -> str:
    """Query Bedrock Knowledge Base for course catalog information."""

@tool
def query_course_reviews(course_name: str) -> str:
    """Query DynamoDB course_reviews table by course_name partition key."""

@tool
def course_review_assistant(query: str) -> str:
    """
    Specialist tool exposed to orchestrator.
    Instantiates a Course Review Agent with KB retrieval and DynamoDB query tools.
    """
```

### Component: `loan_application_agent/agent.py` (SageMaker)

```python
from strands import Agent, tool

@tool
def loan_prediction(payload: str) -> str:
    """
    Invoke SageMaker endpoint with CSV payload (59 features).
    Returns prediction label (Accept/Reject) with confidence percentage.
    """

@tool
def loan_offering_assistant(query: str) -> str:
    """
    Specialist tool exposed to orchestrator.
    Instantiates a Loan Application Agent with the prediction tool.
    """
```

### Component: `math_teaching_agent/agent.py` (Generative)

```python
from strands import Agent, tool
from strands_tools import calculator

@tool
def math_assistant(query: str) -> str:
    """
    Specialist tool exposed to orchestrator.
    Instantiates a Math Teaching Agent with calculator tools.
    """
```

### Component: `shared/model_factory.py`

Creates model instances from configuration dictionaries.

```python
from strands.models import BedrockModel
from strands.models.sagemaker import SageMakerAIModel

def create_model_from_config(config: dict) -> BedrockModel | SageMakerAIModel:
    """
    Args:
        config: {
            "provider": "bedrock" | "sagemaker",
            "model_id": str,
            "temperature": float (0.0-1.0),
            "region": str (optional)
        }
    Returns: Model instance
    Raises: ValueError if provider unsupported, model_id missing, or temperature out of range
    """
```

### Component: `streamlit_app/app.py` (Streamlit Interface)

```python
import streamlit as st

# Sidebar: model selection dropdown (Nova 2 Lite, Claude Sonnet 4.6)
# On model change, recreate orchestrator agent with new model config
# Session state management for conversation history
# Chat input handling with empty-message filtering
# Loading indicator during agent processing
# Clear conversation button
# Agent instantiation (once per session, recreated on model change)

# Routing status feedback via callback_handler:
# When orchestrator calls a specialist tool, the UI updates to show
# "Routing to {Agent Name}..." before the specialist starts processing.
```

#### Routing Status Feedback (Design Decision)

Each specialist `@tool` function prefixes its return value with `[Agent Name]` (e.g., `[Course Review Agent]\n\n{response}`). The orchestrator is instructed to pass tool results through verbatim.

Callback handlers and LLM system prompt instructions were tried and abandoned — callbacks hit Streamlit threading issues (`NoSessionContext`), and LLMs inconsistently follow formatting instructions. A string prefix in the tool return is deterministic and zero-complexity.

### Component: `streamlit_app/config.py`

Provides configuration values with environment variable priority and SSM Parameter Store fallback.

```python
# SSM Parameter Store path prefix
SSM_PREFIX = "/student-services"

# Interface
def get_model_config() -> dict:
    """Returns {"provider": str, "model_id": str, "temperature": float, "region": str}
    Reads from env vars MODEL_PROVIDER, MODEL_ID, TEMPERATURE, AWS_REGION
    Falls back to SSM: /student-services/model-provider, /student-services/model-id, etc.
    """

def get_knowledge_base_id() -> str:
    """Env: KNOWLEDGE_BASE_ID, SSM: /student-services/knowledge-base-id"""

def get_data_source_id() -> str:
    """Env: DATA_SOURCE_ID, SSM: /student-services/data-source-id"""

def get_xgboost_endpoint() -> str:
    """Env: XGBOOST_ENDPOINT_NAME, SSM: /student-services/xgboost-endpoint-name"""

def get_aws_region() -> str:
    """Env: AWS_REGION, SSM: /student-services/aws-region, Default: us-west-2"""

def get_course_registration_table() -> str:
    """Env: COURSE_REGISTRATION_TABLE, SSM: /student-services/course-registration-table"""

def get_course_reviews_table() -> str:
    """Env: COURSE_REVIEWS_TABLE, SSM: /student-services/course-reviews-table"""
```

**Configuration Resolution Order:**
1. Environment variable (e.g., `MODEL_PROVIDER`, `MODEL_ID`, `TEMPERATURE`, `XGBOOST_ENDPOINT_NAME`)
2. SSM Parameter Store path: `/student-services/{param-name}`
3. Hardcoded default (only for region: `us-west-2`)

### Component: `student_services_agent/agent.py` (Orchestrator)

```python
from strands import Agent

def create_orchestrator(model_config: dict) -> Agent:
    """
    Creates the Student Services orchestrator agent with specialist tools.
    
    The orchestrator uses the @tool-wrapped specialist agents as its tools list.
    Routing is handled by the LLM's tool-calling mechanism.
    """
```

The orchestrator's system prompt instructs it to:
- Route registration requests → `course_registration_assistant` tool
- Route course info/review queries → `course_review_assistant` tool
- Route loan queries → `loan_offering_assistant` tool
- Route math problems → `math_assistant` tool
- Respond directly for out-of-domain queries with available services list

## Data Models

### DynamoDB: `course_registration` Table

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| reg_id | String | Partition Key | UUID generated at registration time |
| student_id | String | — | Student identifier |
| course_name | String | — | Course being registered for |
| semester | String | — | Registration semester |

### DynamoDB: `course_reviews` Table

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| course_name | String | Partition Key | Course identifier (e.g., "CS 441") |
| course_title | String | — | Full course title |
| difficulty | String | — | Difficulty rating |
| rating | Number | — | Numeric rating |
| review_count | Number | — | Number of reviews |
| semester | String | — | Semester offered |
| workload_hrs_per_week | Number | — | Weekly workload hours |

### Model Configuration Dictionary

```python
{
    "provider": "bedrock" | "sagemaker",  # Required
    "model_id": str,                       # Required (e.g., "us.amazon.nova-2-lite-v1:0" or "us.anthropic.claude-sonnet-4-6")
    "temperature": float,                  # Optional, 0.0-1.0, default 0.3
    "region": str                          # Optional, default "us-west-2"
}
```

### Loan Prediction Payload

- **Input**: CSV string with exactly 59 numeric features (customer demographics and engagement)
- **Output**: Float prediction score (0.0 to 1.0)
- **Interpretation**: score ≥ 0.5 → "Accept", score < 0.5 → "Reject"
- **Confidence**: `score * 100` for Accept, `(1 - score) * 100` for Reject, rounded to 1 decimal

### Streamlit Session State

```python
st.session_state = {
    "messages": [                    # Conversation history
        {"role": "user" | "assistant", "content": str}
    ],
    "orchestrator": Agent | None,    # Cached orchestrator instance
    "selected_model": str            # Currently selected model ID from dropdown
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Invalid provider raises ValueError

*For any* string value that is not "bedrock" or "sagemaker", calling `create_model_from_config` with that string as the provider SHALL raise a `ValueError` whose message contains both "bedrock" and "sagemaker" as supported providers.

**Validates: Requirements 3.3**

### Property 2: Valid temperature is passed through

*For any* float value `t` where 0.0 ≤ t ≤ 1.0, calling `create_model_from_config` with temperature=t SHALL produce a model instance configured with that temperature value.

**Validates: Requirements 3.5**

### Property 3: Invalid temperature raises ValueError

*For any* float value `t` where t < 0.0 or t > 1.0, calling `create_model_from_config` with temperature=t SHALL raise a `ValueError` indicating the valid range is 0.0 to 1.0.

**Validates: Requirements 3.6**

### Property 4: Prediction score interpretation

*For any* float score `s` in [0.0, 1.0], the prediction interpretation function SHALL return label "Accept" with confidence `round(s * 100, 1)` when s ≥ 0.5, and label "Reject" with confidence `round((1 - s) * 100, 1)` when s < 0.5.

**Validates: Requirements 7.2, 7.3**

### Property 5: Error messages do not leak sensitive information

*For any* exception raised during SageMaker endpoint invocation whose message contains an endpoint name, ARN, or AWS account ID, the user-facing error message returned by the Loan Application Agent SHALL NOT contain any of those sensitive strings.

**Validates: Requirements 7.5**

### Property 6: Invalid feature count is rejected with correct counts

*For any* CSV string with N comma-separated values where N ≠ 59, the loan prediction validation SHALL reject the request and return an error message that states the expected count (59) and the actual count (N).

**Validates: Requirements 7.6**

### Property 7: Whitespace-only messages are not processed

*For any* string composed entirely of whitespace characters (spaces, tabs, newlines), the Streamlit message handler SHALL not add the message to conversation history and SHALL not invoke the orchestrator agent.

**Validates: Requirements 9.3**

### Property 8: Specialist exceptions are caught and reported

*For any* specialist agent tool that raises an exception, the orchestrator's error handling SHALL catch the exception and return a user-facing message that identifies which service is unavailable, without terminating the session or exposing the exception stack trace.

**Validates: Requirements 10.1**

## Error Handling

### Error Handling Strategy

The application uses a layered error handling approach:

```
Layer 1: Tool-level (individual @tool functions)
  → Catches AWS SDK exceptions, timeouts, validation errors
  → Returns sanitized error string (no ARNs, no stack traces)

Layer 2: Agent-level (specialist strands.Agent)
  → Agent receives error string from tool and formulates user-friendly response

Layer 3: Orchestrator-level (Student Services Agent)
  → If specialist tool raises unhandled exception, catches it
  → Returns message identifying which service failed

Layer 4: Streamlit UI
  → Catches any remaining exceptions from orchestrator
  → Displays error in chat, preserves history, returns to input-ready state
```

### Specific Error Scenarios

| Scenario | Handler | User Message |
|----------|---------|--------------|
| Invalid provider in config | `model_factory.py` | ValueError raised at startup (developer error) |
| Temperature out of range | `model_factory.py` | ValueError raised at startup (developer error) |
| Bedrock KB returns no results | `course_review_agent.py` tool | "No matching courses found. Try refining your search terms." |
| DynamoDB query fails | Tool-level try/except | "Course review service is temporarily unavailable." |
| DynamoDB write fails | `course_registration_agent/agent.py` tool | "Registration service encountered an error. Please try again." |
| SageMaker endpoint timeout | `loan_application_agent.py` tool | "Loan prediction service is unavailable. Please try again later." |
| SageMaker endpoint error | `loan_application_agent.py` tool | "Loan prediction service is unavailable. Please try again later." |
| Invalid CSV feature count | `loan_application_agent.py` validation | "Expected 59 features but received {N}. Please check your input." |
| Missing registration params | `course_registration_agent/agent.py` validation | "Missing required parameters: {list of missing params}" |
| Specialist agent exception | Orchestrator catch | "{Service name} is currently unavailable. Please try again or rephrase your request." |
| Any unhandled exception | Streamlit UI | "An unexpected error occurred. Please try again." |

### Timeout Configuration

- AWS SDK calls: 30-second timeout via `botocore.config.Config(read_timeout=30)`
- Streamlit UI recovery: Must return to input-ready state within 3 seconds of error

### Sensitive Information Protection

Error messages MUST NOT expose:
- AWS account IDs
- Resource ARNs
- Endpoint names
- Internal exception stack traces
- DynamoDB table names (in user-facing messages)

## Testing Strategy

### Testing Approach

This feature uses a **dual testing approach**:
- **Property-based tests** for validation logic, score interpretation, and error sanitization
- **Unit tests** for specific examples, integration points, and edge cases
- **Integration tests** for end-to-end agent behavior with real AWS services

### Property-Based Testing

**Library**: [Hypothesis](https://hypothesis.readthedocs.io/) (Python)

**Configuration**: Minimum 100 iterations per property test

Each property test references its design document property:

```python
# Tag format example:
# Feature: workshop4-phase1-monolithic-agents, Property 1: Invalid provider raises ValueError
```

**Property tests to implement:**

| Property | Module Under Test | Generator Strategy |
|----------|-------------------|-------------------|
| 1: Invalid provider | `model_factory.py` | `st.text()` filtered to exclude "bedrock" and "sagemaker" |
| 2: Valid temperature | `model_factory.py` | `st.floats(min_value=0.0, max_value=1.0)` |
| 3: Invalid temperature | `model_factory.py` | `st.floats().filter(lambda x: x < 0.0 or x > 1.0)` excluding NaN/inf |
| 4: Score interpretation | `loan_application_agent.py` | `st.floats(min_value=0.0, max_value=1.0)` |
| 5: Error sanitization | `loan_application_agent.py` | `st.text()` for endpoint names + generated exception messages |
| 6: Invalid feature count | `loan_application_agent.py` | `st.integers(min_value=0, max_value=200).filter(lambda n: n != 59)` |
| 7: Whitespace rejection | `app.py` | `st.text(alphabet=st.characters(whitespace_only=True))` |
| 8: Exception handling | `student_services_agent.py` | `st.sampled_from(specialists)` × `st.from_type(Exception)` |

### Unit Tests

| Test Area | What to Verify |
|-----------|---------------|
| Model Factory — Bedrock | Returns `BedrockModel` instance with correct model_id |
| Model Factory — SageMaker | Returns `SageMakerAIModel` instance |
| Model Factory — missing params | Raises ValueError for missing provider or model_id |
| Config — env var priority | Env vars override SSM values |
| Course Review — combined response | Mocked KB + DynamoDB produce combined output |
| Course Review — empty KB | Returns "no matching courses" message |
| Course Review — empty reviews | Returns KB info with "no reviews available" |
| Registration — success | Returns confirmation with course name and UUID |
| Registration — missing params | Returns error listing missing parameters |
| Registration — DynamoDB failure | Returns sanitized error |
| Loan — valid 59 features | Invokes endpoint and returns formatted result |
| Math — agent has calculator | Verify tools list includes calculator |
| Orchestrator — has all tools | Verify 4 specialist tools registered |
| Streamlit — clear history | Session state messages cleared |

### Integration Tests

| Test Area | What to Verify |
|-----------|---------------|
| CloudFormation deployment | Stack deploys successfully, outputs correct |
| Bedrock KB query | Returns relevant course catalog results |
| DynamoDB course_reviews query | Returns review records for known course |
| DynamoDB registration write | Creates item with correct attributes |
| SageMaker endpoint invocation | Returns prediction score for valid payload |
| End-to-end routing | User message → correct specialist → response |

### Test File Structure

Tests reside in `workshop4/phase1/tests/` as shown in the project directory structure above.
