# Implementation Plan: Workshop 4 Phase 3 Agent Swarm Refactoring

## Overview

Refactor Phase 3 from the broken "Agent-inside-MCP" anti-pattern to the AWS-recommended architecture: all agent intelligence in one AgentCore HTTP Runtime (Agent-as-Tool pattern), with only dumb deterministic data-access tools exposed as MCP servers via AgentCore Gateway.

Deployment sequence: CloudFormation → register-credentials.sh → CLI upgrade → MCP servers → orchestrator → agentcore.json → CDK scaffold → deploy (first pass) → update endpoints → deploy (second pass) → test → Streamlit → README.

## Tasks

- [x] 1. CloudFormation Infrastructure Update
  - [x] 1.1 Update CloudFormation template for new MCP server topology
    - Remove MathTeaching domain section entirely
    - Replace CourseReview domain with CourseCatalog + CourseReviews domains
    - CourseCatalog: base policy + bedrock:Retrieve, scope: course-catalog/access
    - CourseReviews: base policy + DynamoDBReadOnlyAccess, scope: course-reviews/access
    - Keep StudentServicesAgent, StudentServicesGateway, CourseRegistration, LoanApplication unchanged
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8_
  - [x] 1.2 Deploy CloudFormation stack update
    - Run from Windows: `aws cloudformation deploy --template-file cloudformation/student-services-agentcore-infra.yaml --stack-name student-services-agentcore-infra --capabilities CAPABILITY_NAMED_IAM --region us-west-2`
    - _Requirements: 1.7_

- [x] 2. Register OAuth Credentials
  - [x] 2.1 Update register-credentials.sh for new topology
    - Replace CourseReviewMcp-oauth + MathTeachingMcp-oauth with CourseCatalogMcp-oauth + CourseReviewsMcp-oauth
    - Update CloudFormation output key references to match new resource names
    - _Requirements: 1.8_
  - [x] 2.2 Run register-credentials.sh
    - Run from GitBash or code-server: `bash workshop4/phase3/register-credentials.sh`
    - Verify all 5 credentials registered successfully
    - _Requirements: 1.8_

- [x] 3. CLI Upgrade and Clean Install
  - [x] 3.1 Uninstall existing AgentCore CLI and reinstall at latest version
    - Both Windows and Ubuntu at 0.15.0
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 4. Implement Dumb MCP Servers
  - [x] 4.1 Create CourseCatalogMcp server (`course_catalog/server.py`)
    - FastMCP with `path="/mcp/"`, search_course_catalog tool, Bedrock KB retrieve
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 15.1, 15.2, 15.3, 15.4_
  - [x] 4.2 Create CourseReviewsMcp server (`course_reviews/server.py`)
    - FastMCP with `path="/mcp/"`, get_course_reviews tool, DynamoDB scan
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 15.1, 15.2, 15.3, 15.4_
  - [x] 4.3 Create CourseRegistrationMcp server (`course_registration/server.py`)
    - FastMCP with `path="/mcp/"`, register_course tool, DynamoDB write
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 15.1, 15.2, 15.3, 15.4_
  - [x] 4.4 Create LoanApplicationMcp server (`loan_application/server.py`)
    - FastMCP with `path="/mcp/"`, predict_loan tool, SageMaker invoke
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 15.1, 15.2, 15.3, 15.4_

- [x] 5. Implement Orchestrator Runtime
  - [x] 5.1 Implement calculator local tool + rewrite orchestrator agent
    - Agent-as-Tool pattern: 4 specialist agents as @tool functions
    - MCPClient connected to gateway for 3 specialists, local calculator for math
    - _Requirements: 2.1-2.6, 7.1, 7.2, 8.1-8.3, 10.1, 10.2_

- [x] 6. Update agentcore.json and Directory Cleanup
  - [x] 6.1 Update agentcore.json with new runtime topology
    - 5 runtimes, 4 gateway targets, updated credentials, placeholder endpoints for new runtimes
    - _Requirements: 9.1-9.5, 14.1-14.5_
  - [x] 6.2 Delete obsolete directories
    - Removed course_review/, math_teaching/, old agent.py files
    - _Requirements: 7.3, 7.4, 14.3_

- [x] 7. Regenerate CDK Scaffold
  - [x] 7.1 Regenerate agentcore/cdk/ from fresh scaffold + npm install
    - _Requirements: 14.1_

- [ ] 8. Clean Slate Deployment
  - [ ] 8.1 Stop Kiro, apply fresh AWS credentials
    - Credentials expire; must refresh before any AWS operations
  - [ ] 8.2 Delete old AgentCore CDK stack
    - `aws cloudformation delete-stack --stack-name AgentCore-studentservices-default --region us-west-2`
    - `aws cloudformation wait stack-delete-complete --stack-name AgentCore-studentservices-default --region us-west-2`
    - This deletes all runtimes, gateway, credential providers, and memory
  - [ ] 8.3 Delete stale deployed state
    - `Remove-Item "workshop4\phase3\studentservices\agentcore\.cli\deployed-state.json" -Force`
    - This forces the CLI to treat next deploy as a fresh creation
  - [ ] 8.4 Clear gateway targets in agentcore.json (set `"targets": []`)
    - Avoids chicken-and-egg: gateway can't reference runtime URLs that don't exist yet
    - Keep the gateway definition, credentials, runtimes — just empty the targets array
  - [ ] 8.5 Re-register OAuth credentials
    - `bash register-credentials.sh` (from GitBash on Windows or code-server)
    - Deleting the stack deletes credential providers; they must be re-registered
    - Verify all 5 credentials registered successfully
  - [ ] 8.6 First `agentcore deploy -y` (creates runtimes + gateway with no targets)
    - Creates all 5 runtimes and the gateway (empty targets)
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [ ] 9. Update Gateway Endpoints and Second Deploy
  - [ ] 9.1 Get runtime URLs from `agentcore status`
    - Record all 4 MCP server endpoint URLs (CourseCatalog, CourseReviews, CourseRegistration, LoanApplication)
  - [ ] 9.2 Update agentcore.json gateway targets with real endpoint URLs
    - Add all 4 targets back with correct endpoint URLs from 9.1
  - [ ] 9.3 Second `agentcore deploy -y` (adds targets to gateway)
    - Gateway now has correct endpoints for all 4 MCP servers
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_
  - [ ] 9.4 Update orchestrator hardcoded gateway URL if it changed
    - Check `student_services/agent.py` — GATEWAY_MCP_URL must match new gateway endpoint

- [ ] 10. End-to-End Testing (via agentcore invoke)
  - [ ]* 10.1 Test math teaching (local, no MCP)
    - `agentcore invoke --runtime StudentServicesAgent "What is the derivative of x^3 + 2x?"`
    - _Requirements: 7.1, 7.2, 10.2_
  - [ ]* 10.2 Test course review (gateway → 2 MCP servers)
    - `agentcore invoke --runtime StudentServicesAgent "What are the most challenging courses?"`
    - _Requirements: 8.1, 8.2, 8.3, 10.1_
  - [ ]* 10.3 Test course registration (gateway → 1 MCP server)
    - `agentcore invoke --runtime StudentServicesAgent "Register student STU001 for CS 441 in Fall 2026"`
    - _Requirements: 5.1, 5.2, 10.1_
  - [ ]* 10.4 Test loan application (gateway → 1 MCP server)
    - `agentcore invoke --runtime StudentServicesAgent` with 59 CSV features
    - _Requirements: 6.1, 6.2, 10.1_

- [ ] 11. Test Local Streamlit App (`streamlit_app/`)
  - [ ] 11.1 Update and test local Streamlit thin client
    - Run `streamlit run app.py` locally, test all 4 specialists
    - _Requirements: 10.3, 11.1, 11.2_

- [ ] 12. Deploy Production Streamlit App (`deploy-streamlit-app/`)
  - [ ] 12.1 Deploy to ECS Fargate from code-server
    - _Requirements: 11.1, 11.2, 12.3_

- [ ] 13. Update README and Documentation
  - [ ] 13.1 Update Phase 3 README with new architecture
    - _Requirements: 13.1, 13.2, 13.3_

- [ ] 14. Final checkpoint
  - Ensure all tests pass.

## Notes

- **Deployment sequence**: Delete old stack → delete deployed-state.json → empty gateway targets → re-register credentials → deploy (first, no targets) → get URLs → add targets → deploy (second) → test
- Tasks marked with `*` are optional for faster MVP
- `register-credentials.sh` must run from bash (GitBash on Windows or code-server)
- All MCP servers use `path="/mcp/"` in FastMCP constructor (fixes 307 redirect)
- pyproject.toml required in each MCP server directory (CDK synth requirement)
- Deleting the AgentCore CDK stack also deletes credential providers — re-registration is mandatory

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["8.1"] },
    { "id": 1, "tasks": ["8.2"] },
    { "id": 2, "tasks": ["8.3", "8.4"] },
    { "id": 3, "tasks": ["8.5"] },
    { "id": 4, "tasks": ["8.6"] },
    { "id": 5, "tasks": ["9.1"] },
    { "id": 6, "tasks": ["9.2", "9.4"] },
    { "id": 7, "tasks": ["9.3"] },
    { "id": 8, "tasks": ["10.1", "10.2", "10.3", "10.4"] },
    { "id": 9, "tasks": ["11.1"] },
    { "id": 10, "tasks": ["12.1"] },
    { "id": 11, "tasks": ["13.1"] },
    { "id": 12, "tasks": ["14"] }
  ]
}
```
