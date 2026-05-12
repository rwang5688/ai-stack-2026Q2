# Implementation Plan: Workshop 4 Phase 2 — ECS Fargate Deployment

## Overview

This plan deploys the Phase 1 monolithic Student Services Assistant to ECS Fargate (ARM64/Graviton) behind CloudFront with Cognito authentication. The CDK stack and Docker build run on code-server (ARM/Graviton EC2).

## Tasks

- [x] 1. Set up Phase 2 project structure
  - [x] 1.1 Create directory structure
    - Create `workshop4/phase2/` with subdirectories: `cdk/`, `docker_app/`
    - Create `cdk/__init__.py`
    - _Requirements: 2.1_

  - [x] 1.2 Create `docker_app/config_file.py`
    - Define `Config` class with: `STACK_NAME = "StudentServicesPhase2"`, `CUSTOM_HEADER_VALUE`, `SECRETS_MANAGER_ID`, `DEPLOYMENT_REGION = "us-west-2"`
    - _Requirements: 2.6, 2.9, 4.4_

  - [x] 1.3 Create CDK entry point `app.py`
    - Import `CdkStack` from `cdk.cdk_stack`
    - Import `Config` from `docker_app.config_file`
    - Set `env=cdk.Environment(region=Config.DEPLOYMENT_REGION)`
    - _Requirements: 2.9_

  - [x] 1.4 Create `cdk.json`
    - Set `"app": "python3 app.py"`
    - Include standard CDK context flags
    - _Requirements: 2.1_

  - [x] 1.5 Create `requirements.txt` (CDK dependencies)
    - `aws-cdk-lib>=2.160.0`
    - `constructs>=10.0.0`
    - _Requirements: 2.1_

- [x] 2. Create Docker container
  - [x] 2.1 Create `docker_app/Dockerfile`
    - Base image: `--platform=linux/arm64 python:3.12`
    - EXPOSE 8501
    - WORKDIR /app
    - COPY and install requirements.txt
    - COPY all source code
    - Set ENV: `BYPASS_TOOL_CONSENT=true`, `OTEL_SDK_DISABLED=true`
    - CMD: `streamlit run streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [x] 2.2 Create `docker_app/requirements.txt`
    - Include: `strands-agents>=1.0.0`, `strands-agents-tools>=0.3.0`, `streamlit>=1.0.0`, `boto3>=1.0.0`, `streamlit-cognito-auth>=1.0.0`
    - _Requirements: 1.4, 4.4_

  - [x] 2.3 Copy Phase 1 source code into `docker_app/`
    - Copy directories: `streamlit_app/`, `shared/`, `course_review_agent/`, `course_registration_agent/`, `loan_application_agent/`, `math_teaching_agent/`, `student_services_agent/`
    - Only copy `.py` files (no `__pycache__`, no `.gitkeep`, no data files)
    - _Requirements: 1.4_

  - [x] 2.4 Modify `streamlit_app/app.py` for Cognito authentication
    - Add `streamlit-cognito-auth` integration at the top of the app
    - Read Cognito credentials from Secrets Manager (pool_id, app_client_id, app_client_secret)
    - Wrap the main app content in an authentication check
    - Show login page for unauthenticated users
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 3. Create CDK stack
  - [x] 3.1 Implement `cdk/cdk_stack.py`
    - Create Cognito User Pool + Client (generate_secret=True)
    - Store Cognito credentials in Secrets Manager (secret_name from Config)
    - Create VPC (10.0.0.0/16, 2 AZs, 1 NAT gateway)
    - Create security groups (ECS allows port 8501 from ALB only)
    - Create ECS Cluster with Fargate capacity provider
    - Create ALB in public subnets
    - Create Fargate Task Definition:
      - `runtime_platform`: ARM64 + Linux
      - `memory_limit_mib`: 512
      - `cpu`: 256
    - Build Docker image from `docker_app/` and add as container (port 8501)
    - Create ECS Fargate Service in private subnets
    - Create IAM policy on task role with permissions for: Bedrock, SageMaker, DynamoDB, SSM, Secrets Manager, S3 Vectors
    - Create CloudFront distribution → ALB origin (custom header restriction)
    - Create ALB listener with custom header condition + 403 default action
    - Output: CloudFront URL, Cognito User Pool ID
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [x] 4. Create deployment scripts
  - [x] 4.1 Create `deploy.sh`
    - Run `cdk bootstrap` (idempotent — safe to run multiple times)
    - Run `cdk deploy --require-approval never`
    - Print CloudFront URL and Cognito User Pool ID from stack outputs
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 4.2 Create `force-deploy.sh`
    - Run `cdk deploy --require-approval never`
    - Force ECS service update: `aws ecs update-service --force-new-deployment`
    - _Requirements: 5.4_

- [ ] 5. Checkpoint - Verify CDK synth works locally
  - Run `cdk synth` on code-server to verify template generation
  - Verify Docker image builds natively on ARM
  - Ask the user if questions arise.

- [ ] 6. Deploy and test
  - [ ] 6.1 Deploy CDK stack from code-server
    - Run `./deploy.sh` on code-server
    - Wait for deployment to complete (~10-15 minutes)
    - Note CloudFront URL and Cognito User Pool ID from outputs
    - _Requirements: 5.1, 5.5_

  - [ ] 6.2 Create Cognito user and test
    - Create a user in the Cognito User Pool via AWS Console
    - Access the CloudFront URL in a browser
    - Verify login page appears
    - Verify app works after authentication (test all 4 specialist agents)
    - _Requirements: 4.1, 4.2, 4.3_

- [ ] 7. Create README documentation
  - [ ] 7.1 Create `workshop4/phase2/README.md`
    - Document prerequisites (code-server, CDK, Docker, AWS CLI)
    - Document deployment steps (deploy.sh, create Cognito user, access URL)
    - Document architecture (CloudFront → ALB → ECS Fargate ARM64)
    - Document design decisions (ARM64 for cost, CDK for Docker+ECR automation, custom header for ALB restriction)
    - Document force-redeployment process
    - _Requirements: 5.1, 5.4_

## Notes

- All Docker builds happen on code-server (ARM/Graviton) — native builds, no cross-compilation
- Phase 1 infrastructure (S3, DynamoDB, Bedrock KB, SSM parameters) must already be deployed
- The ECS task reads config from SSM — same parameters as Phase 1
- Cognito user must be created manually after deployment (via AWS Console)
- Reference implementations: `.kiro/references/deploy-streamlit-app/` (baseline) and `.kiro/references/workshop4/deploy_multi_agent/` (custom)

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.3", "1.4", "1.5"] },
    { "id": 1, "tasks": ["2.1", "2.2", "2.3"] },
    { "id": 2, "tasks": ["2.4", "3.1"] },
    { "id": 3, "tasks": ["4.1", "4.2"] },
    { "id": 4, "tasks": ["6.1"] },
    { "id": 5, "tasks": ["6.2"] },
    { "id": 6, "tasks": ["7.1"] }
  ]
}
```
