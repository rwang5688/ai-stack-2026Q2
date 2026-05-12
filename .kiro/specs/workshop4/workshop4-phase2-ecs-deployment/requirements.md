# Requirements: Workshop 4 Phase 2 — ECS Fargate Deployment

## Introduction

Phase 2 deploys the Phase 1 monolithic Student Services Assistant to AWS as a web application on ECS Fargate, secured behind CloudFront with Cognito authentication. The deployment uses CDK and Docker, built on code-server (ARM/Graviton architecture).

## Glossary

- **ECS Fargate**: Serverless container runtime — no EC2 instances to manage
- **Graviton/ARM64**: AWS custom ARM processors, ~20% cheaper than x86 for Fargate
- **CloudFront**: CDN that provides HTTPS termination and caching
- **Cognito**: AWS managed user authentication service
- **CDK**: AWS Cloud Development Kit — infrastructure as code using Python
- **code-server**: Remote VS Code instance running on EC2 Graviton (ARM), used for Docker builds and CDK deploy

## Requirements

### Requirement 1: Docker Container

**User Story:** As a developer, I want to containerize the Phase 1 Streamlit app so that it can run on ECS Fargate.

#### Acceptance Criteria

1. WHEN the Dockerfile is built, THEN it SHALL use `--platform=linux/arm64` base image (Python 3.12) to match Graviton Fargate runtime.
2. WHEN the container starts, THEN it SHALL run `streamlit run streamlit_app/app.py` on port 8501.
3. WHEN the container is built on code-server (ARM/Graviton), THEN it SHALL build natively without cross-compilation or emulation.
4. WHEN the container runs, THEN it SHALL have all Phase 1 source code copied into `/app` working directory.
5. WHEN the container runs, THEN it SHALL set `BYPASS_TOOL_CONSENT=true` and `OTEL_SDK_DISABLED=true` environment variables.

### Requirement 2: CDK Stack

**User Story:** As a developer, I want a CDK stack that deploys the containerized app to ECS Fargate with CloudFront and Cognito.

#### Acceptance Criteria

1. WHEN the CDK stack is deployed, THEN it SHALL create a VPC with 2 AZs, public and private subnets, and 1 NAT gateway.
2. WHEN the CDK stack is deployed, THEN it SHALL create an ECS Fargate service with ARM64/Graviton runtime platform.
3. WHEN the CDK stack is deployed, THEN it SHALL create an Application Load Balancer in public subnets.
4. WHEN the CDK stack is deployed, THEN it SHALL create a CloudFront distribution that forwards all traffic to the ALB.
5. WHEN the CDK stack is deployed, THEN it SHALL restrict ALB access to CloudFront only via a custom header.
6. WHEN the CDK stack is deployed, THEN it SHALL create a Cognito user pool and store credentials in Secrets Manager.
7. WHEN the CDK stack is deployed, THEN it SHALL output the CloudFront distribution URL and Cognito user pool ID.
8. WHEN the CDK stack is deployed, THEN the Fargate task definition SHALL use 512 MiB memory and 256 CPU units.
9. WHEN the CDK stack is deployed, THEN the deployment region SHALL be `us-west-2`.

### Requirement 3: IAM Permissions

**User Story:** As a deployed application, I need IAM permissions to access all AWS services used by the specialist agents.

#### Acceptance Criteria

1. WHEN the ECS task runs, THEN it SHALL have permission to invoke Bedrock models (`bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`).
2. WHEN the ECS task runs, THEN it SHALL have permission to query Bedrock Knowledge Base (`bedrock:Retrieve`, `bedrock:RetrieveAndGenerate`).
3. WHEN the ECS task runs, THEN it SHALL have permission to invoke SageMaker endpoints (`sagemaker:InvokeEndpoint`).
4. WHEN the ECS task runs, THEN it SHALL have permission to read/write DynamoDB tables (`dynamodb:GetItem`, `dynamodb:PutItem`, `dynamodb:Query`, `dynamodb:Scan`, `dynamodb:BatchWriteItem`).
5. WHEN the ECS task runs, THEN it SHALL have permission to read SSM parameters (`ssm:GetParameter`, `ssm:GetParameters`, `ssm:GetParametersByPath`).
6. WHEN the ECS task runs, THEN it SHALL have permission to read the Cognito secret from Secrets Manager.
7. WHEN the ECS task runs, THEN it SHALL have permission to access S3 Vectors for Knowledge Base operations (`s3vectors:QueryVectors`, `s3vectors:GetVector`).

### Requirement 4: Authentication

**User Story:** As an end user, I want to authenticate via Cognito before accessing the Student Services Assistant.

#### Acceptance Criteria

1. WHEN a user accesses the CloudFront URL, THEN they SHALL be presented with a login page.
2. WHEN a user provides valid Cognito credentials, THEN they SHALL be granted access to the Streamlit app.
3. WHEN a user is not authenticated, THEN they SHALL NOT be able to access the Streamlit app.
4. WHEN the app starts, THEN it SHALL read Cognito configuration from Secrets Manager.

### Requirement 5: Deployment Process

**User Story:** As a developer, I want a simple deployment process that runs from code-server.

#### Acceptance Criteria

1. WHEN the developer runs the deploy script on code-server, THEN it SHALL bootstrap CDK (if needed), build the Docker image natively on ARM, push to ECR, and deploy the CloudFormation stack.
2. WHEN the Docker image is built on code-server, THEN it SHALL build natively on ARM64 without requiring QEMU or cross-compilation.
3. WHEN the deployment completes, THEN it SHALL output the CloudFront URL for accessing the application.
4. WHEN the developer needs to force a redeployment, THEN there SHALL be a mechanism to force ECS to pull the latest container image.
5. WHEN the CDK stack is deployed, THEN it SHALL complete within 15 minutes.

### Requirement 6: Configuration

**User Story:** As a deployed application, I want to read configuration from SSM Parameter Store just like the local version.

#### Acceptance Criteria

1. WHEN the app runs in ECS, THEN it SHALL read all configuration from SSM Parameter Store under `/student-services/` prefix (same as Phase 1).
2. WHEN the app runs in ECS, THEN it SHALL NOT require any environment variable overrides — SSM is the source of truth.
3. WHEN the app runs in ECS, THEN the AWS region SHALL be determined from the ECS task metadata or default to `us-west-2`.
