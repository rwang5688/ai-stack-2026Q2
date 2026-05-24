# Session Notes - May 24, 2026

## Session Overview

Completed Phase 3 deployment on Ubuntu (c7g.xlarge). Fixed deployment blockers, ran two-pass deploy, verified all 4 specialists end-to-end, deployed production Streamlit app to ECS Fargate. Phase 3 is DONE.

## Key Accomplishments

- Fixed `agentcore deploy` on Ubuntu: `sudo rm -rf agentcore/cdk/dist` (permission issue from root-owned files)
- Installed `uv` on Ubuntu (required for CDK synth CodeZip bundling): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Completed two-pass deploy (empty targets → add targets after runtimes warm)
- All 4 specialists verified working via `agentcore invoke`
- Updated runtime URLs in `streamlit_app/run.sh`, `run.ps1`, `deploy-streamlit-app.sh`
- Deployed production Streamlit app to ECS Fargate (CloudFront + Cognito auth)
- Verified all 4 specialists working through production app
- Rewrote Phase 3 README to reflect correct architecture
- All tasks in `workshop4-phase3-agent-swarm-refactoring` spec marked COMPLETE

## Issues & Resolutions

- **Issue**: `EACCES: permission denied` on `agentcore/cdk/dist/`
  - **Resolution**: `sudo rm -rf agentcore/cdk/dist` — files were owned by root from previous operations

- **Issue**: `CDK synth failed: uv install failed on platform aarch64-manylinux2014`
  - **Resolution**: Install `uv` on Ubuntu: `curl -LsSf https://astral.sh/uv/install.sh | sh` (one-time setup)

- **Issue**: All 4 gateway targets failed with "Runtime initialization time exceeded" (30s health check timeout)
  - **Resolution**: Two-pass deploy. Pass 1 with empty `"targets": []` creates runtimes without health check. Pass 2 adds targets after runtimes are warm and READY.

- **Issue**: CloudFormation IAM roles — thought we needed to add DynamoDB/SageMaker permissions
  - **Resolution**: Already handled in `student-services-agentcore-infra.yaml` (CourseRegistration has DynamoDBFullAccess, LoanApplication has sagemaker:InvokeEndpoint)

## Decisions Made

- **Two-pass deploy is MANDATORY for fresh AgentCore stacks** — gateway health check times out on cold-starting runtimes. Always deploy runtimes first (empty targets), then add targets on second pass.
- **`uv` is a one-time install on Ubuntu** — persists in `~/.local/bin`
- **SSM for model config is the right pattern** — no mechanism to pass model_id through MCP protocol; centralized SSM parameter is cleaner than coupling
- **Deploy from Ubuntu going forward** — c7g.xlarge is significantly faster than Windows for CDK synth and `uv` bundling

## Current Deployment State

| Resource | Status | Identifier |
|----------|--------|------------|
| StudentServicesAgent | READY | studentservices_StudentServicesAgent-DVMRTdBLbs |
| CourseCatalogMcp | READY | studentservices_CourseCatalogMcp-1eMaj0DXfd |
| CourseRegistrationMcp | READY | studentservices_CourseRegistrationMcp-BbB8mO8Spr |
| CourseReviewsMcp | READY | studentservices_CourseReviewsMcp-vYqB8A7u89 |
| LoanApplicationMcp | READY | studentservices_LoanApplicationMcp-SGOP4FCEDG |
| Gateway | Deployed (4 targets) | studentservices-studentservicesgateway-nxhssbogbd |
| Memory | Deployed | studentservices_StudentServicesMemory-li2XVGC76S |
| Streamlit (ECS) | Deployed | StudentServicesPhase3 stack |

## New Rules (Add to Steering)

- **Always two-pass deploy for fresh AgentCore stacks** — never put targets in on first deploy
- **Ubuntu prerequisites**: `uv`, `node`, `npm`, `aws-cdk`, `@aws/agentcore` globally installed
- **`sudo rm -rf agentcore/cdk/dist`** if permission errors on CDK build (root-owned files from cross-platform sync)

## Next Steps

- [x] Delete old Cognito User Pool (`us-west-2_6QVBX7KZT`) — stale from previous CDK deployment
- [x] Workshop 4 complete — architecture diagram update for presentation (offline)
