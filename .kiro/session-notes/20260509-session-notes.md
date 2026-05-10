# Session Notes - May 9, 2026

## Session Overview
Deployed code-server.yaml after removing EC2 Key Pair dependency (security risk). Captured plan for workshop4 rewrite.

## Key Accomplishments
- Removed `EC2KeyPairName` parameter and `KeyName` from EC2 instance in code-server.yaml
- Instance now accessible only via CloudFront (web UI) and SSM Session Manager (shell)
- Deployment started to Isengard account

## Workshop 4 Rebuild Plan (Revised — Morning Session)

### Revision Note
Previous plan was less ambitious and organized. This morning's revision restructures workshop4 into 3 clear phases with a Higher Ed use case (Student Services Assistant) that serves as a real demo for Higher Ed customers.

---

### Design Decisions

**Default deployment region: `us-west-2`**
- All workshops (2, 3, 4) deploy to us-west-2 this semester
- Hardcoded as the default in config; overridable via environment variable

**Cross-session memory: Phase 3 only (AgentCore Memory)**
- Phases 1 and 2: Conversation history is session-only (Streamlit session state, cleared on tab close)
- Phase 3: AgentCore Memory provides persistent cross-session memory (user facts + session summaries keyed by actor/session ID)
- Reference: `agentcore-workshop/travelplanner/travel_agent/memory/session.py` uses `AgentCoreMemorySessionManager` with retrieval config for `/users/{actor_id}/facts` and `/summaries/{actor_id}/{session_id}`

**IaC: CloudFormation YAML (not CDK)**
- CloudFormation YAML is the default for foundational infrastructure (S3, DynamoDB, Bedrock KB, Cognito)
- CDK only when required by tooling: deploy-streamlit-app (Phase 2), AgentCore CLI (Phase 3)
- Rationale: Workshop Studio only supports CloudFormation templates (JSON/YAML) for event provisioning

**No MCP Server for Course Registration (or Course Review)**
- MCP is appropriate when wrapping a reusable application interface (e.g., GitHub, Slack, Jira) that multiple agents or use cases could consume as an industry-standard protocol
- For single-purpose DynamoDB read/write operations tightly coupled to one agent's domain logic, a Strands `@tool` is simpler and more appropriate
- Course Review Agent reads DynamoDB via `@tool`; Course Registration Agent writes DynamoDB via `@tool` — same pattern, no MCP overhead
- MCP will be demonstrated in Phase 3 when agents communicate over AgentCore Gateway (which uses MCP as the transport protocol between runtimes)

**Directory structure grouped by runtime boundary**
- Each agent gets its own directory (`student_services_agent/`, `course_review_agent/`, etc.)
- In Phase 3, each directory maps directly to an AgentCore Runtime — just copy the directory
- `streamlit_app/` maps to the ECS Fargate Task in Phase 2
- `shared/` contains utilities (model_factory) used across agents

---

### Use Case: Student Services Assistant

A Streamlit app that invokes the **Student Services Agent** — an orchestrator Strands Agent responsible for routing to specialist agents via a Student Services Gateway.

#### Specialist Agents

| Agent | Pattern Demonstrated | Data Source |
|-------|---------------------|-------------|
| **Course Review Agent** | RAG (Bedrock KB + DynamoDB) | `bedrock-agents-workshop/workshop-labs/KB-DataSource` for catalog; DB for reviews; Code for logic |
| **Course Registration Agent** | DynamoDB write | `bedrock-agents-workshop/DB` for sample data; Code for business logic |
| **Loan Application Agent** | Invoke SageMaker Serverless Endpoint (XGBoost) | `workshop4/multi_agent/loan_offering_assistant.py` |
| **Math Teaching Agent** | Invoke Bedrock Model for generative task | `workshop4/multi_agent/math_assistant.py` |

---

### Directory Structure
```
workshop4/
├── phase1/          # Monolithic Streamlit app (local desktop)
│   └── README.md
├── phase2/          # Monolithic web app on ECS Fargate
│   └── README.md
└── phase3/          # Microservices via AgentCore
    └── README.md
```
Each phase is independently runnable with its own README.

### Three Phases

#### Phase 1: Monolithic Streamlit App (Local Desktop)
- Build multi-agent architecture using Strands Agents + Bedrock Models
- Orchestrator Strands Agent routes to specialist Strands Agents as tools
- All agents wrapped inside a **monolithic** Streamlit app
- Bedrock model factory supporting: Amazon Nova 2, Anthropic Claude 4.x, OpenAI GPT 5.x (when GA)

#### Phase 2: Monolithic Web App on ECS Fargate
- Use `deploy-streamlit-app` reference pattern
- Deploy the monolithic Streamlit app to ECS Fargate (serverless runtime)
- Secured behind CloudFront + Cognito user pool

#### Phase 3: Microservices via AgentCore
- Use `agentcore-workshop` reference pattern (travelplanner)
- Decouple into thin Streamlit app on ECS Fargate → invokes orchestrator via AgentCore Gateway
- Each agent runs on its own AgentCore Runtime with its own AgentCore Identity, Cognito User Pool, and OAuth2 key:
  - **Student Services Agent** — own AgentCore Runtime + Identity + Cognito + OAuth2
  - **Student Services Gateway** — own AgentCore Identity + Cognito + OAuth2
  - **Course Review Agent** — own AgentCore Runtime + Identity + Cognito + OAuth2
  - **Course Registration Agent** — own AgentCore Runtime + Identity + Cognito + OAuth2
  - **Loan Application Agent** — own AgentCore Runtime + Identity + Cognito + OAuth2
  - **Math Teaching Agent** — own AgentCore Runtime + Identity + Cognito + OAuth2
- Student Services Agent uses AgentCore Memory for student preferences (course review, registration, loan application)

---

### Value Proposition

1. **Business**: Agentic AI demo for Higher Ed Institutions — covers course review, course registration, loan application, and teaching/learning. Real demo for Higher Ed Account SA customers.

2. **Functional Architecture Patterns**:
   - Multi-Agent with Orchestrator routing to Specialists as Strands Tools
   - RAG combining Bedrock Knowledge Base + DynamoDB (Course Review)
   - DynamoDB write for course enrollment (Course Registration)
   - Invoke SageMaker Model for predictive task (Loan Application)
   - Invoke Bedrock Model for generative task (Math Teaching)

3. **Deployment Architecture Progression**:
   - Monolithic local desktop app → Monolithic web app (ECS Fargate) → Microservices (ECS Fargate + AgentCore)

---

### IaC Requirements (Kiro to help build)
- **CloudFormation YAML templates** are used to provision foundational infrastructure (S3, DynamoDB, Bedrock KB, Cognito user pools). This is the default IaC choice for Workshop Studio compatibility.
- **CDK exceptions** (only when required by tooling):
  - Phase 2: `deploy-streamlit-app` pattern uses CDK CLI (`cdk deploy`) to deploy ECS Fargate + ALB + CloudFront + Cognito
  - Phase 3: AgentCore CLI (`agentcore deploy`) is a wrapper around `cdk deploy` for deploying agent runtimes
  - Phase 3: Cognito user pools for AgentCore Identities are provisioned via a separate CloudFormation YAML template (following the `agentcore-workshop/cloudformation/infra.yaml` pattern)
- **Deployment approach** (single `deploy.sh` script):
  1. `aws cloudformation deploy` — creates S3 data bucket, S3 Vectors bucket, Bedrock KB, DynamoDB tables (empty)
  2. `python scripts/populate_seed_data.py` — uploads PDF + CSVs to S3 (with prefixes), seeds DynamoDB via `batch_write_item`, triggers KB ingestion
- **S3 bucket naming**: `student-services-data-{AccountId}-{Region}`, `student-services-vectors-{AccountId}-{Region}`
- **S3 prefixes**: `kb-datasource/` for PDF, `dynamodb/` for CSVs (NOT bucket root)
- **Vector store**: S3 Vectors (NOT OpenSearch Serverless — too expensive for workshop/demo)
**SSM Parameter Store layout** (path prefix: `/student-services/`):
- Created by CloudFormation template:
  - `/student-services/data-bucket-name` → S3 data bucket name
  - `/student-services/vectors-bucket-name` → S3 Vectors bucket name
  - `/student-services/knowledge-base-id` → Bedrock KB ID
  - `/student-services/data-source-id` → Bedrock KB data source ID
  - `/student-services/course-registration-table` → DynamoDB table name
  - `/student-services/course-reviews-table` → DynamoDB table name
  - `/student-services/aws-region` → `us-west-2`
  - `/student-services/model-provider` → `bedrock` (default)
  - `/student-services/model-id` → `us.amazon.nova-2-lite-v1:0` (default; also supports `us.anthropic.claude-sonnet-4-6`)
  - `/student-services/temperature` → `0.3` (default)
- Created by `populate_seed_data.py` (user provides endpoint name as CLI argument):
  - `/student-services/xgboost-endpoint-name` → user's SageMaker Serverless Endpoint name
- All parameters overridable via environment variables at runtime

**Embedding model**: `amazon.titan-embed-text-v2:0`

### Reference Materials
- `.kiro/references/agentcore-workshop/` — AgentCore patterns (travelplanner)
- `.kiro/references/bedrock-agents-workshop/` — KB, DB, Code patterns
- `.kiro/references/deploy-streamlit-app/` — ECS Fargate deployment pattern
- `.kiro/references/workshop4/` — Original workshop4 code (multi_agent)

---

## Next Steps
- [ ] Review reference code in `.kiro/references/` for detailed patterns
- [ ] ~~Identify IaC tooling~~ → **Decision made:**
  - CloudFormation YAML for foundational infra (S3, DynamoDB, Bedrock KB, Cognito)
  - CDK only when required by tooling: deploy-streamlit-app (Phase 2), AgentCore CLI (Phase 3)
- [ ] Create spec for Phase 1: Monolithic Streamlit + Strands multi-agent architecture
- [ ] Create spec for Phase 2: ECS Fargate deployment with CloudFront + Cognito
- [ ] Create spec for Phase 3: AgentCore decoupling with per-agent runtimes and identities
