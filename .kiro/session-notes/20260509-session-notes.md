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

### Use Case: Student Services Assistant

A Streamlit app that invokes the **Student Services Agent** — an orchestrator Strands Agent responsible for routing to specialist agents via a Student Services Gateway.

#### Specialist Agents

| Agent | Pattern Demonstrated | Data Source |
|-------|---------------------|-------------|
| **Course Review Agent** | RAG (Bedrock KB + DynamoDB) | `bedrock-agents-workshop/workshop-labs/KB-DataSource` for catalog; DB for reviews; Code for logic |
| **Course Registration Agent** | MCP Server with DynamoDB write | `bedrock-agents-workshop/DB` for sample data; Code for business logic |
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
- Orchestrator Strands Agent routes to specialist Strands Agents and MCP servers as tools
- All agents and MCP servers wrapped inside a **monolithic** Streamlit app
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
   - Multi-Agent with Orchestrator routing to Specialists as MCP Tools
   - RAG combining Bedrock Knowledge Base + DynamoDB (Course Review)
   - MCP Server performing DynamoDB writes (Course Registration)
   - Invoke SageMaker Model for predictive task (Loan Application)
   - Invoke Bedrock Model for generative task (Math Teaching)

3. **Deployment Architecture Progression**:
   - Monolithic local desktop app → Monolithic web app (ECS Fargate) → Microservices (ECS Fargate + AgentCore)

---

### IaC Requirements (Kiro to help build)
- S3 bucket as Bedrock KB data source + S3 Vectors bucket as vector store (Course Review)
- DynamoDB table + sample data upload (Course Review — reviews)
- DynamoDB table + sample data upload (Course Registration)
- Bedrock Knowledge Base configuration

### Reference Materials
- `.kiro/references/agentcore-workshop/` — AgentCore patterns (travelplanner)
- `.kiro/references/bedrock-agents-workshop/` — KB, DB, Code patterns
- `.kiro/references/deploy-streamlit-app/` — ECS Fargate deployment pattern
- `.kiro/references/workshop4/` — Original workshop4 code (multi_agent)

---

## Next Steps
- [ ] Review reference code in `.kiro/references/` for detailed patterns
- [ ] Identify IaC tooling (CDK vs CloudFormation) for infrastructure provisioning
- [ ] Create spec for Phase 1: Monolithic Streamlit + Strands multi-agent architecture
- [ ] Create spec for Phase 2: ECS Fargate deployment with CloudFront + Cognito
- [ ] Create spec for Phase 3: AgentCore decoupling with per-agent runtimes and identities
