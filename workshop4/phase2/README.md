# Workshop 4 Phase 2 — ECS Fargate Deployment

Deploys the Phase 1 Student Services Assistant to ECS Fargate (ARM64/Graviton), secured behind CloudFront with Cognito authentication.

## Architecture

```
User → CloudFront (HTTPS) → ALB (custom header check) → ECS Fargate (ARM64, private subnet)
                                                              ↓
                                              Bedrock / DynamoDB / SSM / SageMaker
```

- **CloudFront** provides HTTPS termination and restricts access via a custom header
- **ALB** sits in public subnets, rejects requests without the custom header (returns 403)
- **ECS Fargate** runs the Streamlit app in private subnets on ARM64/Graviton
- **Cognito User Pool** handles end-user authentication
- **VPC** with 2 AZs, public + private subnets, 1 NAT gateway

Stack name: `StudentServicesPhase2`  
Region: `us-west-2`

## Prerequisites

- **code-server** (ARM/Graviton EC2) with:
  - Docker
  - AWS CLI (configured with credentials)
  - AWS CDK (`npm install -g aws-cdk`)
  - Python 3.12+
  - Node.js 22+
- **Phase 1 infrastructure deployed** — S3, DynamoDB, Bedrock Knowledge Base, SSM parameters under `/student-services/`
- AWS credentials configured with permissions for CDK deployment

## Deployment

```bash
cd workshop4/phase2
pip install -r requirements.txt
chmod +x deploy.sh force-deploy.sh
./deploy.sh
```

`deploy.sh` performs:
1. `cdk bootstrap` (idempotent — safe to run multiple times)
2. `cdk deploy --require-approval never` (builds Docker image, pushes to ECR, deploys stack)

Deployment takes ~10-15 minutes. On completion, note the outputs:
- **CloudFront URL** — the application endpoint
- **Cognito User Pool ID** — needed to create users

### Create a Cognito User

After deployment, create a user in the Cognito User Pool:

1. Open the AWS Console → Cognito → User Pools
2. Find the `StudentServicesPhase2` user pool
3. Create a user (set email + temporary password)
4. Access the CloudFront URL and log in with those credentials

### Access the Application

Navigate to the CloudFront URL output by the deploy script. You'll see a login page — authenticate with your Cognito user credentials to access the Student Services Assistant.

## Force Redeployment

After making code changes, force ECS to pull the latest container image:

```bash
./force-deploy.sh
```

This script:
1. Runs `cdk deploy` to rebuild the Docker image and push to ECR
2. Forces an ECS service update (`aws ecs update-service --force-new-deployment`)

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **ARM64/Graviton** | ~20% cost savings vs x86; native builds on code-server (also ARM) — no cross-compilation or QEMU needed |
| **CDK (not CloudFormation YAML)** | CDK handles Docker build + ECR push automatically via `DockerImageAsset` |
| **CloudFront + custom header** | Restricts ALB to CloudFront-only access; ALB returns 403 for direct requests |
| **Circuit breaker** | ECS deployment circuit breaker enables auto-rollback on failed deployments |
| **Cognito** | Managed user pool for end-user authentication; credentials stored in Secrets Manager |
| **512 MiB / 256 CPU** | Minimal Fargate task size sufficient for Streamlit + agent orchestration |
| **SSM Parameter Store** | Same config mechanism as Phase 1 — no env var overrides needed in ECS |

## Project Structure

```
workshop4/phase2/
├── deploy-streamlit-app/               # CDK project + containerized app
│   ├── app.py                          # CDK app entry point
│   ├── cdk.json                        # CDK configuration
│   ├── cdk/
│   │   ├── __init__.py
│   │   └── cdk_stack.py               # CDK stack (ECS, ALB, CloudFront, Cognito)
│   └── docker_app/                     # Self-contained containerized application
│       ├── app.py                      # Streamlit entry point
│       ├── config.py                   # SSM + env var configuration
│       ├── config_file.py              # Stack name, secrets ID, region
│       ├── Dockerfile                  # ARM64 Python 3.12 base
│       ├── requirements.txt            # Container dependencies
│       ├── __init__.py
│       ├── shared/                     # Model factory, cross-platform tools
│       │   ├── model_factory.py
│       │   └── cross_platform_tools.py
│       ├── student_services/           # All agents in one flat package
│       │   ├── __init__.py
│       │   ├── student_services_agent.py
│       │   ├── course_registration_agent.py
│       │   ├── course_review_agent.py
│       │   ├── loan_application_agent.py
│       │   └── math_teaching_agent.py
│       └── utils/                      # Auth utilities (Cognito)
│           └── auth.py
├── deploy.sh                           # One-command deploy
├── force-deploy.sh                     # Force redeployment after code changes
├── README.md
└── requirements.txt                    # CDK dependencies (aws-cdk-lib)
```

`docker_app/` is the deployment unit — it contains everything that goes into the container. The agent code from Phase 1's `streamlit_app/` lives here in a flat `student_services/` package (one file per agent), plus Cognito auth (`utils/auth.py`) and CDK config (`config_file.py`).

## Troubleshooting

- **CDK bootstrap fails**: Ensure AWS credentials are configured and have CloudFormation/S3/ECR permissions
- **Docker build fails**: Verify you're on ARM/Graviton code-server (not x86)
- **ECS task fails to start**: Check CloudWatch Logs for the task; verify Phase 1 SSM parameters exist
- **403 from ALB**: You're accessing the ALB directly — use the CloudFront URL instead
- **Login page doesn't appear**: Verify the Cognito secret exists in Secrets Manager
