# Design Document

## Overview

This document specifies the architecture for Workshop 4 Phase 3's thin client layer and runtime model selection. The system decomposes into three concerns:

1. **Runtime modification** — Adding dynamic model selection to the existing `StudentServicesAgent` BedrockAgentCoreApp entrypoint
2. **Local thin client** — A Streamlit chat UI that invokes the runtime via SigV4-signed HTTP
3. **Production web deployment** — The same thin client packaged in Docker on ECS Fargate behind CloudFront + ALB with Cognito authentication

All components use Python. The CDK stack uses `aws-cdk-lib` (Python). The runtime uses `strands` and `bedrock-agentcore`.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AgentCore Platform                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  StudentServicesAgent Runtime (HTTP)                           │  │
│  │  POST /invoke  {"prompt": "...", "model_id": "..."}           │  │
│  │                                                               │  │
│  │  ┌─────────────┐   ┌──────────────┐   ┌──────────────────┐  │  │
│  │  │ Model       │   │ Agent Cache   │   │ MCP Gateway      │  │  │
│  │  │ Validation  │──▶│ {sid/uid/mid} │──▶│ (Specialists)    │  │  │
│  │  └─────────────┘   └──────────────┘   └──────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
         ▲                                          ▲
         │ SigV4 HTTP POST                          │ SigV4 HTTP POST
         │                                          │
┌────────┴────────┐                    ┌────────────┴────────────────┐
│ Local Client    │                    │ Production Deployment        │
│ (streamlit_app) │                    │                              │
│                 │                    │  CloudFront → ALB → ECS     │
│ • Model select  │                    │  Cognito auth                │
│ • Chat UI       │                    │  docker_app/                 │
│ • agent_client  │                    │  • app.py (Cognito + chat)  │
└─────────────────┘                    │  • agent_client.py          │
                                       │  • cognito_client.py        │
                                       │  • config_file.py           │
                                       └─────────────────────────────┘
```

---

## Components and Interfaces

### Component 1: Runtime Model Selection (`agent.py`)

**File:** `workshop4/phase3/studentservices/student_services/agent.py`

**Changes to existing file:**

```python
# Module-level constant — add after existing constants
ALLOWED_MODELS = [
    "us.amazon.nova-2-lite-v1:0",
    "us.anthropic.claude-sonnet-4-6",
]

DEFAULT_MODEL_ID = "us.amazon.nova-2-lite-v1:0"
```

**Modified entrypoint logic:**

```python
@app.entrypoint
def invoke(payload: dict, context: dict | None = None) -> dict:
    session_id = getattr(context, "session_id", None) or "default-session"
    user_id = getattr(context, "user_id", None) or "default-user"
    prompt = payload.get("prompt", "")

    if not prompt or not prompt.strip():
        return {"response": "Error: 'prompt' field is required and cannot be empty."}

    # --- Model selection ---
    model_id = payload.get("model_id", "").strip()
    if not model_id:
        model_id = DEFAULT_MODEL_ID
    elif model_id not in ALLOWED_MODELS:
        return {
            "response": f"Error: model_id '{model_id}' is not allowed. "
            f"Permitted models: {ALLOWED_MODELS}"
        }

    # --- Agent caching with model_id in key ---
    cache_key = f"{session_id}/{user_id}/{model_id}"
    if cache_key not in _agent_cache:
        mcp_client = get_mcp_client()

        model = BedrockModel(
            model_id=model_id,
            region_name="us-west-2",
            max_tokens=4096,
        )

        _agent_cache[cache_key] = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            tools=[mcp_client],
        )

    response = _agent_cache[cache_key](prompt)
    return {"response": str(response)}
```

**Key design decisions:**
- `payload.get("model_id")` works because BedrockAgentCoreApp passes the full payload dict to the entrypoint function — it does NOT strip unknown keys from the dict itself
- Validation happens before agent creation to fail fast on invalid models
- Cache key includes `model_id` so switching models creates a fresh Agent with separate conversation history
- Default model is `us.amazon.nova-2-lite-v1:0` (matching Phase 1 behavior)

---

### Component 2: Agent Client Module (`agent_client.py`)

**Shared between local and production deployments.** Both `workshop4/phase3/streamlit_app/agent_client.py` and `workshop4/phase3/deploy-streamlit-app/docker_app/agent_client.py` use the same implementation.

```python
"""HTTP client for communicating with the StudentServicesAgent runtime on AgentCore.

Sends prompts to the StudentServicesAgent runtime via SigV4-signed HTTP POST
requests. Supports optional model_id parameter for dynamic model selection.
"""

import json
import os
from typing import Optional

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

STUDENT_SERVICES_AGENT_URL = os.environ.get("STUDENT_SERVICES_AGENT_URL", "")

_REQUIRED_VARS = [
    "STUDENT_SERVICES_AGENT_URL",
]


def get_config_errors() -> list[str]:
    """Return list of missing required environment variable names."""
    missing = []
    if not STUDENT_SERVICES_AGENT_URL:
        missing.append("STUDENT_SERVICES_AGENT_URL")
    return missing


def invoke(prompt: str, model_id: Optional[str] = None) -> str:
    """Send prompt to StudentServicesAgent and return the response text.

    Signs the request with SigV4 (service: bedrock-agentcore, region: us-west-2),
    sends HTTP POST with JSON body, and returns the "response" field from the reply.

    Args:
        prompt: The user message to send to the agent.
        model_id: Optional model identifier. If provided, included in the payload.

    Returns:
        The agent's response text.

    Raises:
        RuntimeError: On non-200 status or network errors.
    """
    import httpx

    # Build request body
    body_dict: dict = {"prompt": prompt}
    if model_id:
        body_dict["model_id"] = model_id
    body = json.dumps(body_dict)

    # SigV4 signing
    session = boto3.Session()
    credentials = session.get_credentials().get_frozen_credentials()

    aws_request = AWSRequest(
        method="POST",
        url=STUDENT_SERVICES_AGENT_URL,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    SigV4Auth(credentials, "bedrock-agentcore", "us-west-2").add_auth(aws_request)

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

**Design decisions:**
- `model_id` is `Optional[str]` — only included in body when truthy
- SigV4 region hardcoded to `us-west-2` (all Phase 3 resources are in this region)
- 120-second timeout accommodates agent tool-use chains that may take time
- `httpx` used for HTTP (consistent with reference implementation)
- Credentials sourced from `boto3.Session()` supporting IAM roles, env vars, and profiles

---

### Component 3: Local Streamlit App (`streamlit_app/`)

**Directory:** `workshop4/phase3/streamlit_app/`

**Files:**
- `app.py` — Streamlit chat UI with model selector
- `agent_client.py` — (same as Component 2)
- `requirements.txt` — `boto3`, `httpx`, `streamlit`
- `run.ps1` / `run.sh` — Convenience scripts setting env vars

**`app.py` structure:**

```python
"""Student Services Assistant — Local Streamlit thin client.

Chat interface that sends prompts to the StudentServicesAgent runtime
on AgentCore with dynamic model selection.

Run with: streamlit run app.py
"""

import streamlit as st
from agent_client import get_config_errors, invoke

# Page config
st.set_page_config(page_title="Student Services Assistant")
st.title("🎓 Student Services Assistant")
st.write("Ask about courses, register for classes, get loan predictions, or solve math problems.")

# Validate config
errors = get_config_errors()
if errors:
    st.error(f"Missing environment variables: {', '.join(errors)}")
    st.stop()

# Model options
MODEL_OPTIONS = {
    "Amazon Nova 2 Lite (us.amazon.nova-2-lite-v1:0)": "us.amazon.nova-2-lite-v1:0",
    "Anthropic Claude Sonnet 4 (us.anthropic.claude-sonnet-4-6)": "us.anthropic.claude-sonnet-4-6",
}

# Sidebar: model selector, sample prompts, clear chat
with st.sidebar:
    st.header("🤖 Model Selection")
    selected_model_key = st.selectbox(
        "Choose Model:",
        options=list(MODEL_OPTIONS.keys()),
    )
    selected_model_id = MODEL_OPTIONS[selected_model_key]

    st.header("💡 Sample Prompts")
    # ... sample prompts for each domain ...

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = invoke(prompt, model_id=selected_model_id)
                st.markdown(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
            except Exception as e:
                st.error(str(e))
```

**Convenience scripts:**

`run.ps1`:
```powershell
$env:STUDENT_SERVICES_AGENT_URL = "<runtime-url>"
streamlit run app.py
```

`run.sh`:
```bash
export STUDENT_SERVICES_AGENT_URL="<runtime-url>"
streamlit run app.py
```

---

### Component 4: Production Docker App (`deploy-streamlit-app/docker_app/`)

**Directory:** `workshop4/phase3/deploy-streamlit-app/docker_app/`

**Files:**
- `app.py` — Cognito auth + chat UI (same chat logic as local)
- `agent_client.py` — (same as Component 2)
- `cognito_client.py` — Reads Cognito params from Secrets Manager
- `config_file.py` — Configuration constants
- `Dockerfile` — ARM64 container image
- `requirements.txt` — `boto3`, `httpx`, `streamlit`, `streamlit-cognito-auth`

#### `config_file.py`

```python
class Config:
    STACK_NAME = "StudentServicesPhase3"
    CUSTOM_HEADER_VALUE = "student-services-phase3-cf-header-2026"
    SECRETS_MANAGER_ID = f"{STACK_NAME}CognitoSecret"
    DEPLOYMENT_REGION = "us-west-2"
```

#### `cognito_client.py`

```python
"""Cognito authentication module.

Retrieves Cognito User Pool parameters from AWS Secrets Manager
and returns a configured CognitoAuthenticator instance.
"""

import json

import boto3
from streamlit_cognito_auth import CognitoAuthenticator


def get_authenticator(secret_id: str, region: str) -> CognitoAuthenticator:
    """Get a CognitoAuthenticator by reading pool params from Secrets Manager."""
    secretsmanager_client = boto3.client("secretsmanager", region_name=region)
    response = secretsmanager_client.get_secret_value(SecretId=secret_id)
    secret = json.loads(response["SecretString"])

    return CognitoAuthenticator(
        pool_id=secret["pool_id"],
        app_client_id=secret["app_client_id"],
        app_client_secret=secret["app_client_secret"],
    )
```

#### `app.py` (production)

```python
"""Student Services Assistant — Production Streamlit thin client with Cognito auth."""

import streamlit as st
import agent_client
import cognito_client
from config_file import Config

st.set_page_config(page_title="Student Services Assistant")
st.title("🎓 Student Services Assistant")

# Cognito authentication
authenticator = cognito_client.get_authenticator(
    Config.SECRETS_MANAGER_ID, Config.DEPLOYMENT_REGION
)
is_logged_in = authenticator.login()
if not is_logged_in:
    st.stop()

# Validate agent URL
errors = agent_client.get_config_errors()
if errors:
    st.error(f"Missing environment variables: {', '.join(errors)}")
    st.stop()

# Model options (same as local)
MODEL_OPTIONS = {
    "Amazon Nova 2 Lite (us.amazon.nova-2-lite-v1:0)": "us.amazon.nova-2-lite-v1:0",
    "Anthropic Claude Sonnet 4 (us.anthropic.claude-sonnet-4-6)": "us.anthropic.claude-sonnet-4-6",
}

# Sidebar with auth info, model selector, sample prompts
with st.sidebar:
    st.text(f"Welcome,\n{authenticator.get_username()}")
    st.button("Logout", "logout_btn", on_click=authenticator.logout)

    st.header("🤖 Model Selection")
    selected_model_key = st.selectbox("Choose Model:", options=list(MODEL_OPTIONS.keys()))
    selected_model_id = MODEL_OPTIONS[selected_model_key]

    # ... sample prompts, clear chat button ...

# Chat interface (identical to local version)
# ...
```

#### `Dockerfile`

```dockerfile
FROM --platform=linux/arm64 python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

### Component 5: CDK Stack (`deploy-streamlit-app/cdk/`)

**Directory:** `workshop4/phase3/deploy-streamlit-app/`

**Files:**
- `cdk/cdk_stack.py` — Infrastructure stack
- `cdk/app.py` — CDK app entry point
- `cdk/__init__.py` — Empty
- `cdk.json` — CDK configuration
- `requirements.txt` — `aws-cdk-lib`, `constructs`

#### `cdk/app.py`

```python
#!/usr/bin/env python3
import aws_cdk as cdk
from cdk_stack import CdkStack
from docker_app.config_file import Config

app = cdk.App()
CdkStack(
    app,
    Config.STACK_NAME,
    env=cdk.Environment(region=Config.DEPLOYMENT_REGION),
)
app.synth()
```

#### `cdk.json`

```json
{
  "app": "python cdk/app.py"
}
```

#### `cdk/cdk_stack.py` — Resource Provisioning Order

1. **Cognito + Secrets Manager** — User Pool, Client, Secret
2. **VPC + Security Groups** — VPC (10.0.0.0/16, 2 AZs, 1 NAT), ALB SG, ECS SG
3. **ECS Cluster + Fargate** — Task definition (ARM64, 256 CPU, 512 MiB), container with `STUDENT_SERVICES_AGENT_URL` env var, service in private subnets
4. **ALB + CloudFront** — Internet-facing ALB, CloudFront with custom header, listener rules (header match → ECS, default → 403)
5. **IAM** — `bedrock-agentcore:InvokeAgentRuntime` policy, Secrets Manager read grant
6. **Outputs** — CloudFront URL, Cognito Pool ID

The CDK stack follows the exact same pattern as Phase 2 (`workshop4/phase2/deploy-streamlit-app/cdk/cdk_stack.py`) with these differences:
- Stack name: `StudentServicesPhase3` (was `StudentServicesPhase2`)
- Context parameter: `student_services_agent_url` (was none — Phase 2 didn't need an agent URL env var since it ran the agent locally)
- IAM policy: `bedrock-agentcore:InvokeAgentRuntime` (was Bedrock/SageMaker/DynamoDB/SSM/S3Vectors)
- Config import path: `docker_app.config_file` (same pattern)

---

## Data Models

### Request Payload (Runtime)

```json
{
  "prompt": "string (required, non-empty)",
  "model_id": "string (optional, must be in ALLOWED_MODELS if present)"
}
```

### Response Payload (Runtime)

**Success:**
```json
{
  "response": "string — the agent's text response"
}
```

**Error (invalid model):**
```json
{
  "response": "Error: model_id 'bad-model' is not allowed. Permitted models: ['us.amazon.nova-2-lite-v1:0', 'us.anthropic.claude-sonnet-4-6']"
}
```

**Error (empty prompt):**
```json
{
  "response": "Error: 'prompt' field is required and cannot be empty."
}
```

### Agent Cache Key Format

```
{session_id}/{user_id}/{model_id}
```

Example: `abc123/user42/us.amazon.nova-2-lite-v1:0`

### Configuration Constants

| Constant | Value |
|----------|-------|
| `STACK_NAME` | `StudentServicesPhase3` |
| `DEPLOYMENT_REGION` | `us-west-2` |
| `SECRETS_MANAGER_ID` | `StudentServicesPhase3CognitoSecret` |
| `CUSTOM_HEADER_VALUE` | `student-services-phase3-cf-header-2026` |
| `ALLOWED_MODELS[0]` | `us.amazon.nova-2-lite-v1:0` |
| `ALLOWED_MODELS[1]` | `us.anthropic.claude-sonnet-4-6` |

---

## Error Handling

| Scenario | Component | Behavior |
|----------|-----------|----------|
| Empty/missing prompt | Runtime | Returns error response (not HTTP error) |
| Invalid model_id | Runtime | Returns error response listing allowed models |
| Missing env var | Agent Client | `get_config_errors()` returns variable names |
| Non-200 HTTP response | Agent Client | Raises `RuntimeError` with status + body |
| Network failure | Agent Client | Raises `RuntimeError` with failure description |
| Agent Client exception | Streamlit UI | Displays error in chat via `st.error()` |
| Cognito not authenticated | Production UI | Shows login form, `st.stop()` |

---

## Interfaces

### Agent Client Interface

```python
def get_config_errors() -> list[str]:
    """Returns list of missing required env var names. Empty list = all good."""

def invoke(prompt: str, model_id: Optional[str] = None) -> str:
    """Send prompt to runtime, return response text. Raises RuntimeError on failure."""
```

### Cognito Client Interface

```python
def get_authenticator(secret_id: str, region: str) -> CognitoAuthenticator:
    """Read Cognito params from Secrets Manager, return configured authenticator."""
```

### Runtime Entrypoint Interface

```python
@app.entrypoint
def invoke(payload: dict, context: dict | None = None) -> dict:
    """Accept prompt + optional model_id, return {"response": "..."}."""
```

---

## Testing Strategy

**Property-based tests** (6 properties below) cover the runtime model validation logic and agent client request/response handling — these are pure functions with clear input/output behavior where input variation reveals edge cases.

**Example-based unit tests** cover:
- Static configuration values (ALLOWED_MODELS contents, Config constants)
- BedrockModel instantiation parameters (region, max_tokens)
- SigV4 signing with correct service name and region
- Streamlit UI rendering (page title, sidebar components)

**Integration tests** (CDK assertion tests) cover:
- All CDK stack resources (VPC, ECS, ALB, CloudFront, Cognito, IAM)
- Resource property values and cross-resource references

**Smoke tests** cover:
- Dockerfile structure (ARM64 base, port 8501, entrypoint)
- requirements.txt completeness
- cdk.json pointing to correct app entry

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Invalid model rejection

*For any* string that is not a member of the ALLOWED_MODELS list, when provided as `model_id` in the request payload, the runtime SHALL return a response containing an error message that lists the permitted models, and SHALL NOT create or invoke an Agent.

**Validates: Requirements 1.3**

### Property 2: Default model fallback

*For any* request payload where `model_id` is absent, empty, or whitespace-only, the runtime SHALL resolve the model to `us.amazon.nova-2-lite-v1:0` and use it for agent creation.

**Validates: Requirements 1.2**

### Property 3: Cache key incorporates model selection

*For any* combination of session_id, user_id, and valid model_id, the agent cache key SHALL equal `{session_id}/{user_id}/{model_id}`, ensuring that the same user switching models gets a distinct Agent instance.

**Validates: Requirements 1.4**

### Property 4: Request body construction reflects model_id presence

*For any* prompt string and optional model_id, the Agent Client SHALL construct a JSON body where: (a) if model_id is truthy, the body contains both `"prompt"` and `"model_id"` keys with their respective values; (b) if model_id is falsy or absent, the body contains only the `"prompt"` key.

**Validates: Requirements 2.4, 2.5**

### Property 5: Successful response extraction

*For any* HTTP 200 response containing a JSON object with a `"response"` field, the Agent Client SHALL return the exact string value of that field without modification.

**Validates: Requirements 2.6**

### Property 6: Error propagation on non-200 status

*For any* HTTP response with a status code other than 200, the Agent Client SHALL raise a RuntimeError whose message contains both the numeric status code and the response body text.

**Validates: Requirements 2.8**
