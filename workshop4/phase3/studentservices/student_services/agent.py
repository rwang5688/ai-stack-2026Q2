"""Student Services Orchestrator — routes queries to specialist agents via AgentCore Gateway.

Usage:
    agentcore dev --runtime StudentServicesOrchestrator
    agentcore invoke "What courses are available for Fall 2026?"
"""

import os
import sys

# Fix Windows cp1252 encoding for emoji/unicode in responses
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from datetime import datetime

import boto3
import httpx
from bedrock_agentcore import BedrockAgentCoreApp
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient


# ---------------------------------------------------------------------------
# Model configuration — reads from SSM Parameter Store (no caching)
# ---------------------------------------------------------------------------
def get_model_config() -> dict:
    """Get model config from SSM. Resolution: env var → SSM → hardcoded default."""
    model_id = os.environ.get("MODEL_ID")
    if not model_id:
        try:
            ssm = boto3.client("ssm", region_name="us-west-2")
            response = ssm.get_parameter(Name="/student-services/model-id")
            model_id = response["Parameter"]["Value"]
        except Exception:
            model_id = None
    if not model_id:
        model_id = "us.amazon.nova-2-lite-v1:0"
    return {"model_id": model_id, "region": "us-west-2", "max_tokens": 4096}


# ---------------------------------------------------------------------------
# Gateway configuration — hardcoded defaults, overridable via env vars
# ---------------------------------------------------------------------------
GATEWAY_MCP_URL = os.environ.get(
    "GATEWAY_MCP_URL",
    "https://studentservices-studentservicesgateway-ts3cbbncol.gateway.bedrock-agentcore.us-west-2.amazonaws.com/mcp",
)
GATEWAY_CLIENT_ID = os.environ.get(
    "GATEWAY_CLIENT_ID",
    "3b48jg8f940sef71ldeetismr",
)
GATEWAY_CLIENT_SECRET = os.environ.get(
    "GATEWAY_CLIENT_SECRET",
    "7ecg2e78ni41s1r17kk0jd5akul0v28f1h3d7v7mrn7l21h6shh",
)
GATEWAY_TOKEN_ENDPOINT = os.environ.get(
    "GATEWAY_TOKEN_ENDPOINT",
    "https://student-services-gateway-149057604171.auth.us-west-2.amazoncognito.com/oauth2/token",
)
GATEWAY_SCOPE = os.environ.get("GATEWAY_SCOPE", "student-services-gateway/access")

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are the Student Services Assistant for Any University (any.edu).
You help students with course information, registration, loan predictions, and math tutoring.

You route queries to specialized tools via the gateway:
- course_registration: Register students in courses. Requires student_id, course_name, and semester.
- course_review: Search course catalog, retrieve course reviews and ratings.
- loan_application: Predict loan acceptance based on 59 numeric feature values.
- math_teaching: Solve math problems with step-by-step explanations.

Routing rules:
- Course information, reviews, ratings, catalog queries → course_review
- Registration, enrollment, sign up for a course → course_registration
- Loan predictions, loan acceptance, financial features → loan_application
- Math problems, calculations, equations, tutoring → math_teaching
- Out-of-domain queries → Respond directly listing the available services above

Always route to the appropriate specialist. Do not attempt to answer domain-specific questions yourself.
When you receive a tool result, pass it through to the user verbatim. Do not summarize or reformat.

CRITICAL for loan predictions: When the user provides comma-separated numeric values, pass the ENTIRE string to the loan_application tool EXACTLY as the user typed it. Do NOT count the values, do NOT validate the count, do NOT modify or truncate the string. The specialist will handle validation.
"""

# ---------------------------------------------------------------------------
# OAuth2 token management with caching
# ---------------------------------------------------------------------------
_token_cache: dict = {"token": None, "expires_at": 0.0}


def get_oauth_token() -> str:
    """Fetch or return cached OAuth2 token, refreshing 5 min before expiry."""
    now = datetime.now().timestamp()
    if _token_cache["token"] and now < _token_cache["expires_at"]:
        return _token_cache["token"]

    resp = httpx.post(
        GATEWAY_TOKEN_ENDPOINT,
        data={"grant_type": "client_credentials", "scope": GATEWAY_SCOPE},
        auth=(GATEWAY_CLIENT_ID, GATEWAY_CLIENT_SECRET),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Token fetch failed ({resp.status_code}): {resp.text}")

    data = resp.json()
    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = now + data["expires_in"] - 300
    return _token_cache["token"]


# ---------------------------------------------------------------------------
# MCP client factory with auto-refreshing auth
# ---------------------------------------------------------------------------
def get_mcp_client() -> MCPClient:
    """Create an MCPClient that auto-refreshes the OAuth token on each request."""

    class _OAuthAuth(httpx.Auth):
        def auth_flow(self, request):
            request.headers["Authorization"] = f"Bearer {get_oauth_token()}"
            yield request

    return MCPClient(
        lambda: streamablehttp_client(url=GATEWAY_MCP_URL, auth=_OAuthAuth())
    )


# ---------------------------------------------------------------------------
# BedrockAgentCoreApp entrypoint
# ---------------------------------------------------------------------------
app = BedrockAgentCoreApp()

_agent_cache: dict = {}


@app.entrypoint
def invoke(payload: dict, context: dict | None = None) -> dict:
    session_id = getattr(context, "session_id", None) or "default-session"
    user_id = getattr(context, "user_id", None) or "default-user"
    prompt = payload.get("prompt", "")

    if not prompt or not prompt.strip():
        return {"response": "Error: 'prompt' field is required and cannot be empty."}

    cache_key = f"{session_id}/{user_id}"
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

    response = _agent_cache[cache_key](prompt)
    return {"response": str(response)}


if __name__ == "__main__":
    app.run()
