# Design Document

## Overview

This design describes the SSM-based model configuration system and thin client interfaces for the Phase 3 Student Services AgentCore microservices. The architecture centralizes model selection in a single SSM parameter, enabling administrators to switch models across all 5 runtimes without redeployment. Two Streamlit thin clients (local and production) provide chat UIs that invoke the orchestrator via SigV4-signed HTTP POST.

## Architecture

```
Admin updates SSM /student-services/model-id
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  All 5 AgentCore Runtimes read SSM on agent creation            │
│                                                                 │
│  shared/config.py → get_model_config() → {"model_id": "...",   │
│                                            "region": "...",     │
│                                            "max_tokens": 4096}  │
│                                                                 │
│  StudentServicesAgent (orchestrator)                             │
│  CourseRegistrationMcp (specialist)                              │
│  CourseReviewMcp (specialist)                                    │
│  LoanApplicationMcp (specialist)                                │
│  MathTeachingMcp (specialist)                                   │
└─────────────────────────────────────────────────────────────────┘
         ▲
         │ SigV4 HTTP POST {"prompt": "..."}
         │
┌────────┴────────┐              ┌─────────────────────────────┐
│ Local Client    │              │ Production (ECS Fargate)     │
│ streamlit_app/  │              │ deploy-streamlit-app/        │
│ • Displays model│              │ • Cognito auth               │
│   (read-only)   │              │ • Same chat UI               │
└─────────────────┘              └─────────────────────────────┘
```

### Key Design Decisions

1. **No model_id in payload** — model is system-wide config, not per-request. The MCP protocol boundary between orchestrator → gateway → specialist means propagating model_id would require changing the tool contract at each hop.
2. **SSM read per agent creation (no caching)** — ensures new sessions always get the current value. Since agents are cached per session, SSM is only read when a new session starts.
3. **Shared config module** — DRY pattern, consistent across all 5 runtimes.
4. **Cache key stays `{session_id}/{user_id}`** — model is not part of user identity; it's infrastructure config.
5. **Fallback chain** — env var `MODEL_ID` → SSM → hardcoded default provides resilience during development and deployment.

## Components and Interfaces

### Component 1: Shared Config Module

**File:** `workshop4/phase3/studentservices/shared/config.py`

```python
"""
Shared model configuration for all AgentCore runtimes.

Reads the model ID from SSM Parameter Store with fallback to
environment variable and hardcoded default.

Resolution order: environment variable MODEL_ID → SSM → hardcoded default
"""

import os

import boto3

DEFAULT_MODEL_ID = "us.amazon.nova-2-lite-v1:0"
DEFAULT_REGION = "us-west-2"
DEFAULT_MAX_TOKENS = 4096
SSM_PARAMETER_NAME = "/student-services/model-id"


def get_model_config() -> dict:
    """
    Get model configuration dictionary for creating BedrockModel instances.

    Reads the model ID from SSM Parameter Store on each call (no caching)
    so that new sessions always pick up the current value.

    Returns:
        Dictionary with model_id, region, and max_tokens keys.
    """
    # 1. Environment variable override (for local dev)
    model_id = os.environ.get("MODEL_ID")

    # 2. SSM Parameter Store
    if not model_id:
        try:
            ssm = boto3.client("ssm", region_name=DEFAULT_REGION)
            response = ssm.get_parameter(Name=SSM_PARAMETER_NAME)
            model_id = response["Parameter"]["Value"]
        except Exception:
            model_id = None

    # 3. Hardcoded default
    if not model_id:
        model_id = DEFAULT_MODEL_ID

    return {
        "model_id": model_id,
        "region": DEFAULT_REGION,
        "max_tokens": DEFAULT_MAX_TOKENS,
    }
```

**File:** `workshop4/phase3/studentservices/shared/__init__.py`

```python
"""Shared utilities for Student Services AgentCore runtimes."""
```

### Component 2: Runtime Modifications (All 5 agent.py Files)

Each agent.py replaces the hardcoded `BedrockModel(model_id="...", ...)` with a call to `get_model_config()`.

**Pattern — Orchestrator (`student_services/agent.py`):**

```python
from shared.config import get_model_config

# Inside the invoke entrypoint, when creating a new cached agent:
if cache_key not in _agent_cache:
    mcp_client = get_mcp_client()
    model_config = get_model_config()
    model = BedrockModel(
        model_id=model_config["model_id"],
        region_name=model_config["region"],
        max_tokens=model_config["max_tokens"],
    )
    _agent_cache[cache_key] = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[mcp_client],
    )
```

**Pattern — Specialist MCP Servers (e.g., `course_registration/agent.py`):**

```python
from shared.config import get_model_config

# Inside the MCP tool function:
@mcp.tool()
def course_registration_assistant(prompt: str) -> dict:
    model_config = get_model_config()
    model = BedrockModel(
        model_id=model_config["model_id"],
        region_name=model_config["region"],
        max_tokens=model_config["max_tokens"],
    )
    agent = Agent(model=model, system_prompt=SYSTEM_PROMPT, tools=[register_course])
    response = agent(prompt)
    return {"response": str(response), "runtime": RUNTIME_NAME}
```

**Files modified:**
- `workshop4/phase3/studentservices/student_services/agent.py`
- `workshop4/phase3/studentservices/course_registration/agent.py`
- `workshop4/phase3/studentservices/course_review/agent.py`
- `workshop4/phase3/studentservices/loan_application/agent.py`
- `workshop4/phase3/studentservices/math_teaching/agent.py`

### Component 3: IAM Permission Update

**File:** `workshop4/phase3/cloudformation/student-services-agentcore-infra.yaml`

Add to the `AgentCoreBasePolicy` PolicyDocument Statements:

```yaml
- Sid: SSMParameterAccess
  Effect: Allow
  Action:
    - ssm:GetParameter
  Resource:
    - !Sub 'arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/student-services/*'
```

This grants all 5 execution roles (which reference `AgentCoreBasePolicy` via `ManagedPolicyArns`) permission to read SSM parameters under the `/student-services/` path.

### Component 4: Local Thin Client

**Directory:** `workshop4/phase3/streamlit_app/`

#### `agent_client.py`

```python
"""HTTP client for communicating with the StudentServicesAgent runtime on AgentCore.

Sends prompts via SigV4-signed HTTP POST requests.
"""

import json
import os

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

STUDENT_SERVICES_AGENT_URL = os.environ.get("STUDENT_SERVICES_AGENT_URL", "")


def get_config_errors() -> list[str]:
    """Return list of missing required environment variable names."""
    missing = []
    if not STUDENT_SERVICES_AGENT_URL:
        missing.append("STUDENT_SERVICES_AGENT_URL")
    return missing


def invoke(prompt: str) -> str:
    """Send prompt to StudentServicesAgent and return the response text.

    Signs the request with SigV4 using service name 'bedrock-agentcore'.
    Sends HTTP POST with body {"prompt": prompt}.
    Returns the "response" field from the JSON reply.

    Raises RuntimeError on non-200 status or network errors.
    """
    import httpx

    body = json.dumps({"prompt": prompt})

    session = boto3.Session()
    credentials = session.get_credentials().get_frozen_credentials()
    region = session.region_name or "us-west-2"

    aws_request = AWSRequest(
        method="POST",
        url=STUDENT_SERVICES_AGENT_URL,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    SigV4Auth(credentials, "bedrock-agentcore", region).add_auth(aws_request)

    try:
        resp = httpx.post(
            STUDENT_SERVICES_AGENT_URL,
            content=body,
            headers=dict(aws_request.headers),
            timeout=120.0,
        )
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Agent request failed: {exc}") from exc

    if resp.status_code != 200:
        raise RuntimeError(
            f"Agent call failed ({resp.status_code}): {resp.text}"
        )

    return resp.json()["response"]
```

#### `app.py`

```python
"""Local Streamlit thin client for Student Services Agent.

Provides a chat interface that sends prompts to the StudentServicesAgent
runtime via SigV4-signed HTTP POST. Displays the configured model ID
from SSM as read-only sidebar information.
"""

import boto3
import streamlit as st

import agent_client

# --- Page config ---
st.set_page_config(page_title="Student Services Agent", page_icon="🎓")
st.title("🎓 Student Services Agent")

# --- Validate configuration ---
errors = agent_client.get_config_errors()
if errors:
    st.error(f"Missing required environment variables: {', '.join(errors)}")
    st.stop()

# --- Sidebar: model info and controls ---
with st.sidebar:
    st.header("Configuration")
    try:
        ssm = boto3.client("ssm", region_name="us-west-2")
        param = ssm.get_parameter(Name="/student-services/model-id")
        model_id = param["Parameter"]["Value"]
    except Exception:
        model_id = "(unable to read from SSM)"
    st.text_input("Model ID", value=model_id, disabled=True)

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("**Sample Prompts:**")
    st.markdown("- What courses are available for Fall 2026?")
    st.markdown("- Register STU001 for CS 441 in Fall 2026")
    st.markdown("- Solve x² + 5x + 6 = 0")

# --- Chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat input ---
if prompt := st.chat_input("Ask the Student Services Agent..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = agent_client.invoke(prompt)
            except RuntimeError as e:
                response = f"⚠️ Error: {e}"
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
```

#### `requirements.txt`

```
boto3
httpx
streamlit
```

#### `run.ps1`

```powershell
# Run the local Streamlit thin client
# Requires: STUDENT_SERVICES_AGENT_URL environment variable set
streamlit run app.py
```

#### `run.sh`

```bash
#!/bin/bash
# Run the local Streamlit thin client
# Requires: STUDENT_SERVICES_AGENT_URL environment variable set
streamlit run app.py
```

### Component 5: Production Web App

**Directory:** `workshop4/phase3/deploy-streamlit-app/`

#### `docker_app/config_file.py`

```python
"""Configuration constants for the CDK stack and Docker app."""


class Config:
    STACK_NAME = "StudentServicesPhase3"
    SECRETS_MANAGER_ID = "student-services-phase3-cognito-secret"
    CUSTOM_HEADER_VALUE = "StudentServicesPhase3SecureHeader2026"
    VPC_NAME = f"{STACK_NAME}-stl-vpc"
    ALB_NAME = f"{STACK_NAME}-stl"
    ALB_SG_NAME = f"{STACK_NAME}-stl-alb-sg"
    ECS_SG_NAME = f"{STACK_NAME}-stl-ecs-sg"
    ECS_SERVICE_NAME = f"{STACK_NAME}-stl-front"
    TARGET_GROUP_NAME = f"{STACK_NAME}-tg"
    AWS_REGION = "us-west-2"
```

#### `docker_app/agent_client.py`

Same SigV4 HTTP client as the local version, reading `STUDENT_SERVICES_AGENT_URL` from environment.

#### `docker_app/cognito_client.py`

Handles Cognito user authentication using credentials from Secrets Manager. Provides login/logout/session management for the Streamlit app.

#### `docker_app/app.py`

Production Streamlit app with Cognito authentication gate. After login, provides the same chat interface as the local client.

#### `docker_app/Dockerfile`

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### `docker_app/requirements.txt`

```
boto3
httpx
streamlit
```

#### `cdk/cdk_stack.py`

CDK Python stack that deploys:
- **VPC**: 2 AZs, public subnets (ALB), private subnets with NAT (ECS)
- **ECS Fargate**: ARM64 task running the Streamlit container on port 8501
- **ALB**: Internet-facing, routes to ECS with custom header validation
- **CloudFront**: HTTPS distribution in front of ALB, caching disabled
- **Cognito**: User Pool + client, credentials stored in Secrets Manager
- **IAM**: Task role with `bedrock-agentcore:InvokeAgentRuntime`, `ssm:GetParameter`, `ssm:GetParametersByPath`, and Secrets Manager read

```python
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_cognito as cognito,
    aws_secretsmanager as secretsmanager,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_elasticloadbalancingv2 as elbv2,
    CfnOutput,
    SecretValue,
)
from constructs import Construct
from docker_app.config_file import Config

CUSTOM_HEADER_NAME = "X-Custom-Header"


class CdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        prefix = Config.STACK_NAME

        # Cognito User Pool
        user_pool = cognito.UserPool(self, f"{prefix}UserPool")
        user_pool_client = cognito.UserPoolClient(
            self, f"{prefix}UserPoolClient",
            user_pool=user_pool,
            generate_secret=True,
        )

        # Store Cognito credentials in Secrets Manager
        secret = secretsmanager.Secret(
            self, f"{prefix}ParamCognitoSecret",
            secret_object_value={
                "pool_id": SecretValue.unsafe_plain_text(user_pool.user_pool_id),
                "app_client_id": SecretValue.unsafe_plain_text(
                    user_pool_client.user_pool_client_id
                ),
                "app_client_secret": user_pool_client.user_pool_client_secret,
            },
            secret_name=Config.SECRETS_MANAGER_ID,
        )

        # VPC
        vpc = ec2.Vpc(
            self, f"{prefix}AppVpc",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            max_azs=2,
            vpc_name=Config.VPC_NAME,
            nat_gateways=1,
        )

        # Security Groups
        alb_security_group = ec2.SecurityGroup(
            self, f"{prefix}SecurityGroupALB",
            vpc=vpc, security_group_name=Config.ALB_SG_NAME,
        )
        ecs_security_group = ec2.SecurityGroup(
            self, f"{prefix}SecurityGroupECS",
            vpc=vpc, security_group_name=Config.ECS_SG_NAME,
        )
        ecs_security_group.add_ingress_rule(
            peer=alb_security_group,
            connection=ec2.Port.tcp(8501),
            description="ALB traffic",
        )

        # ECS Cluster + Fargate Task
        cluster = ecs.Cluster(
            self, f"{prefix}Cluster",
            enable_fargate_capacity_providers=True, vpc=vpc,
        )
        fargate_task_definition = ecs.FargateTaskDefinition(
            self, f"{prefix}WebappTaskDef",
            memory_limit_mib=512, cpu=256,
            runtime_platform=ecs.RuntimePlatform(
                cpu_architecture=ecs.CpuArchitecture.ARM64,
                operating_system_family=ecs.OperatingSystemFamily.LINUX,
            ),
        )
        image = ecs.ContainerImage.from_asset("docker_app")
        fargate_task_definition.add_container(
            f"{prefix}WebContainer",
            image=image,
            port_mappings=[ecs.PortMapping(container_port=8501, protocol=ecs.Protocol.TCP)],
            environment={
                "STUDENT_SERVICES_AGENT_URL": self.node.try_get_context("student_services_agent_url") or "",
            },
            logging=ecs.LogDrivers.aws_logs(stream_prefix="WebContainerLogs"),
        )
        service = ecs.FargateService(
            self, f"{prefix}ECSService",
            cluster=cluster,
            task_definition=fargate_task_definition,
            service_name=Config.ECS_SERVICE_NAME,
            security_groups=[ecs_security_group],
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
        )

        # ALB + CloudFront
        alb = elbv2.ApplicationLoadBalancer(
            self, f"{prefix}Alb",
            vpc=vpc, internet_facing=True,
            load_balancer_name=Config.ALB_NAME,
            security_group=alb_security_group,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )
        origin = origins.LoadBalancerV2Origin(
            alb,
            custom_headers={CUSTOM_HEADER_NAME: Config.CUSTOM_HEADER_VALUE},
            origin_shield_enabled=False,
            protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
        )
        cloudfront_distribution = cloudfront.Distribution(
            self, f"{prefix}CfDist",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origin,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
            ),
        )
        http_listener = alb.add_listener(f"{prefix}HttpListener", port=80, open=True)
        http_listener.add_targets(
            f"{prefix}TargetGroup",
            target_group_name=Config.TARGET_GROUP_NAME,
            port=8501, priority=1,
            conditions=[elbv2.ListenerCondition.http_header(CUSTOM_HEADER_NAME, [Config.CUSTOM_HEADER_VALUE])],
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[service],
        )
        http_listener.add_action(
            "default-action",
            action=elbv2.ListenerAction.fixed_response(
                status_code=403, content_type="text/plain", message_body="Access denied",
            ),
        )

        # IAM: Task role permissions
        task_policy = iam.Policy(
            self, f"{prefix}TaskPolicy",
            statements=[
                iam.PolicyStatement(
                    actions=["bedrock-agentcore:InvokeAgentRuntime"],
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    actions=["ssm:GetParameter", "ssm:GetParametersByPath"],
                    resources=[f"arn:aws:ssm:{self.region}:{self.account}:parameter/student-services/*"],
                ),
            ],
        )
        task_role = fargate_task_definition.task_role
        task_role.attach_inline_policy(task_policy)
        secret.grant_read(task_role)

        # Outputs
        CfnOutput(self, "CloudFrontDistributionURL", value=cloudfront_distribution.domain_name)
        CfnOutput(self, "CognitoPoolId", value=user_pool.user_pool_id)
```

#### `cdk/app.py`

```python
#!/usr/bin/env python3
import aws_cdk as cdk
from cdk_stack import CdkStack

app = cdk.App()
CdkStack(app, "StudentServicesPhase3")
app.synth()
```

#### `cdk/__init__.py`

```python
```

#### `cdk.json`

```json
{
  "app": "python3 cdk/app.py"
}
```

#### `requirements.txt`

```
aws-cdk-lib>=2.100.0
constructs>=10.0.0
```

## Data Models

### get_model_config Return Value

```python
{
    "model_id": str,      # e.g., "us.amazon.nova-2-lite-v1:0"
    "region": str,        # Always "us-west-2"
    "max_tokens": int,    # Always 4096
}
```

### Orchestrator Request/Response

```python
# Request (HTTP POST body)
{"prompt": str}

# Response (HTTP 200 JSON body)
{"response": str}
```

### Agent Cache Structure

```python
# Key: "{session_id}/{user_id}"
# Value: Agent instance (with model configured at creation time)
_agent_cache: dict[str, Agent] = {}
```

## Error Handling

| Scenario | Behavior |
|----------|----------|
| SSM `get_parameter` fails (network, permissions) | `get_model_config` falls back to `MODEL_ID` env var, then hardcoded default |
| `STUDENT_SERVICES_AGENT_URL` not set | Thin client displays error and calls `st.stop()` |
| HTTP request to orchestrator fails | Thin client displays error message in chat, does not crash |
| Empty prompt submitted | Orchestrator returns `{"response": "Error: 'prompt' field is required..."}` |
| Invalid/unknown model_id from SSM | BedrockModel raises at invocation time; error propagates to response |

## Testing Strategy

### Unit Tests (Example-Based)
- Verify each agent.py imports and calls `get_model_config()` (not hardcoded)
- Verify `agent_client.invoke()` calls SigV4Auth with service `"bedrock-agentcore"`
- Verify orchestrator rejects empty prompts with appropriate error
- Verify thin client stops when `STUDENT_SERVICES_AGENT_URL` is unset
- Verify CDK stack synthesizes with expected resources (CDK assertions)

### Edge Case Tests
- `get_model_config()` returns hardcoded default when SSM raises `ClientError`
- `get_model_config()` returns hardcoded default when SSM raises network timeout
- Orchestrator ignores `model_id` field if present in request payload
- Thin client displays error gracefully when HTTP request fails

### Integration Tests
- CloudFormation stack deploys and all 5 roles can call `ssm:GetParameter`
- ECS Fargate container starts and serves on port 8501
- End-to-end: thin client → orchestrator → gateway → specialist → response

### Property-Based Tests
- Config structure invariant (Property 1)
- SSM freshness / no caching (Property 2)
- Session cache isolation (Property 3)
- API contract validation (Property 4)
- Client request serialization (Property 5)

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Config Structure Invariant

*For any* value stored in the SSM parameter `/student-services/model-id` (including when SSM is unreachable), the `get_model_config()` function SHALL return a dictionary with exactly three keys (`model_id`, `region`, `max_tokens`) where `region` is always `"us-west-2"` and `max_tokens` is always `4096`.

**Validates: Requirements 1.1, 1.2, 1.3**

### Property 2: SSM Freshness (No Caching)

*For any* two consecutive calls to `get_model_config()` where the SSM parameter value changes between calls, the second call SHALL return the updated `model_id` value — demonstrating that no stale cached value is returned.

**Validates: Requirements 8.1, 8.3**

### Property 3: Session Cache Isolation

*For any* orchestrator agent cache and any sequence of SSM parameter updates, an Agent instance cached under key `{session_id}/{user_id}` SHALL continue using the `model_id` that was current when that cache entry was created, while a new cache entry created after the update SHALL use the new `model_id`.

**Validates: Requirements 2.2, 8.2**

### Property 4: Orchestrator API Contract

*For any* non-empty string `s`, invoking the orchestrator with payload `{"prompt": s}` SHALL return a JSON object containing exactly a `"response"` key with a string value. No `model_id` field in the request payload SHALL influence the model used.

**Validates: Requirements 2.3, 2.4**

### Property 5: Client Request Serialization

*For any* non-empty string `prompt`, the `agent_client.invoke(prompt)` function SHALL send an HTTP POST request with body exactly equal to `json.dumps({"prompt": prompt})` and the request SHALL be signed with SigV4 using service name `"bedrock-agentcore"`.

**Validates: Requirements 5.2, 5.3**
