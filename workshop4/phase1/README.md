# Workshop 4 Phase 1: Student Services Assistant (Monolithic)

A multi-agent Streamlit application using the Strands Agents SDK. An orchestrator agent routes student queries to four specialist agents, each demonstrating a different agentic AI pattern.

## Architecture

```
Streamlit UI → Student Services Agent (orchestrator)
                 ├── Course Review Agent      (RAG: Bedrock KB + DynamoDB)
                 ├── Course Registration Agent (DynamoDB write)
                 ├── Loan Application Agent   (SageMaker XGBoost endpoint)
                 └── Math Teaching Agent      (Bedrock + calculator tool)
```

## Prerequisites

- Python 3.12+
- AWS CLI configured with credentials (`us-west-2`)
- SageMaker XGBoost Serverless Endpoint (pre-deployed from Workshop 3)

## Setup

### 1. Deploy Infrastructure

```bash
cd workshop4/phase1
./deploy-infra.sh
```

This deploys the CloudFormation stack (`student-services-infra`) which creates:
- S3 data bucket with `kb-datasource/` and `dynamodb/` prefixes
- S3 Vectors bucket + index for Bedrock Knowledge Base
- Bedrock Knowledge Base with S3 data source
- DynamoDB tables: `course_registration`, `course_reviews`
- SSM Parameters under `/student-services/`

### 2. Populate Seed Data

```bash
./populate-seed-data.sh --xgboost-endpoint-name <your-endpoint-name>
```

Or without the XGBoost endpoint (loan agent won't work):
```bash
./populate-seed-data.sh
```

This uploads data to S3, seeds DynamoDB, and triggers KB ingestion.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run streamlit_app/app.py
```

Opens at `http://localhost:8501`.

## Environment Variables

All configuration is read from SSM Parameter Store (`/student-services/` prefix) with environment variable overrides:

| Variable | Description | Default |
|----------|-------------|---------|
| `MODEL_PROVIDER` | Model provider (`bedrock`) | From SSM |
| `MODEL_ID` | Bedrock model ID | `us.amazon.nova-2-lite-v1:0` |
| `MODEL_TEMPERATURE` | Model temperature (0.0-1.0) | `0.3` |
| `AWS_REGION` | AWS region | `us-west-2` |
| `KNOWLEDGE_BASE_ID` | Bedrock KB ID | From SSM |
| `DATA_SOURCE_ID` | KB data source ID | From SSM |
| `XGBOOST_ENDPOINT_NAME` | SageMaker endpoint name | From SSM |
| `COURSE_REGISTRATION_TABLE` | DynamoDB table name | `course_registration` |
| `COURSE_REVIEWS_TABLE` | DynamoDB table name | `course_reviews` |

## Supported Models

Select from the sidebar dropdown:
- Amazon Nova 2 Lite (`us.amazon.nova-2-lite-v1:0`)
- Anthropic Claude Sonnet 4.6 (`us.anthropic.claude-sonnet-4-6`)

## Design Decisions

### `@tool` vs MCP Server

Each specialist agent uses Strands `@tool` decorators for its capabilities (DynamoDB reads/writes, KB retrieval, SageMaker invocation). MCP Servers are appropriate for wrapping reusable application interfaces (GitHub, Slack, Jira) that multiple agents could consume. For single-purpose operations tightly coupled to one agent's domain logic, `@tool` is simpler and more appropriate. MCP will be demonstrated in Phase 3 when agents communicate over AgentCore Gateway.

### Directory Structure (Runtime Boundary)

Each agent has its own directory (`course_review_agent/`, `course_registration_agent/`, etc.). In Phase 3, each directory maps directly to an AgentCore Runtime — just copy the directory. This structure enables independent agent evolution and straightforward migration to microservices.

### Routing Status Display

Each specialist `@tool` function prefixes its return value with `[Agent Name]` so the user sees which specialist handled their query. Callback handlers and LLM system prompt instructions were too unreliable for this purpose.

### S3 Vectors (not OpenSearch Serverless)

The Bedrock Knowledge Base uses S3 Vectors as the vector store. OpenSearch Serverless is prohibitively expensive for workshop/demo purposes and takes minutes to initialize. S3 Vectors provides subsecond query performance at a fraction of the cost.
