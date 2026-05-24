"""Student Services Orchestrator — Agent-as-Tool architecture.

All agent intelligence (orchestrator + 4 specialists) runs locally in one
AgentCore HTTP Runtime. Specialist agents reach their data-access tools
through a single MCPClient connected to the AgentCore Gateway.

The math_teaching_agent uses only a local calculator tool (no MCP needed).

Usage:
    agentcore dev --runtime StudentServicesAgent
    agentcore invoke "What courses are available for Fall 2026?"
"""

import json
import math
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
from strands import Agent, tool
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient


# ---------------------------------------------------------------------------
# Model configuration — reads from SSM Parameter Store
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
    "https://studentservices-studentservicesgateway-8dicrvcvo8.gateway.bedrock-agentcore.us-west-2.amazonaws.com/mcp",
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
# System prompts
# ---------------------------------------------------------------------------
ORCHESTRATOR_SYSTEM_PROMPT = """You are the Student Services Assistant for Any University (any.edu).
You help students with course information, registration, loan predictions, and math tutoring.

You route queries to specialized agents:
- course_review_agent: Course information, reviews, ratings, catalog queries, difficulty, challenging courses, recommendations
- course_registration_agent: Registration, enrollment, sign up for a course
- loan_application_agent: Loan predictions, loan acceptance, financial features
- math_teaching_agent: Math problems, calculations, equations, tutoring

CRITICAL ROUTING BEHAVIOR:
- ALWAYS call the appropriate specialist agent immediately. NEVER ask the user for confirmation before routing.
- NEVER say "I can connect you with..." or "Would you like me to..." — just DO IT.
- If the query is even remotely related to courses, call course_review_agent immediately.
- Pass the user's question directly as the query parameter to the specialist.

When you receive a tool result, pass it through to the user verbatim. Do not summarize or reformat.

If the tool result contains a routing_path field, display it at the TOP of your response like: 🔀 Routing: <routing_path value>

CRITICAL for loan predictions: When the user provides comma-separated numeric values, pass the ENTIRE string to loan_application_agent EXACTLY as the user typed it."""

COURSE_REVIEW_AGENT_PROMPT = """You are the Course Review Assistant for Any University (any.edu).
You help students find information about courses from the course catalog and student reviews.

CRITICAL WORKFLOW: For ANY course-related query, you MUST:
1. FIRST call search_course_catalog to find relevant courses
2. THEN call get_course_reviews for EACH course found (use the course code, e.g., "CS 441")
3. Combine both sources in your response — catalog info AND student reviews

NEVER skip step 2. Even if the user only asks about course descriptions, always include available student reviews."""

COURSE_REGISTRATION_AGENT_PROMPT = """You are the Course Registration Assistant for Any University (any.edu).
You help students register for courses. Use the register_course tool with student_id, course_name, and semester.
If any required field is missing from the user's request, ask for it before calling the tool."""

LOAN_APPLICATION_AGENT_PROMPT = """You are the Loan Offering Assistant for Any University (any.edu).
You predict loan acceptance based on customer features. Use the predict_loan tool with the CSV features string.
CRITICAL: Pass the user's CSV string EXACTLY as-is to predict_loan. Do NOT reformat, recount, or modify it.
Interpret results: score >= 0.5 = Accept, score < 0.5 = Reject. Confidence = distance from 0.5 threshold."""

MATH_TEACHING_AGENT_PROMPT = """You are the Math Teaching Assistant for Any University (any.edu).
You solve math problems with clear, step-by-step explanations.
Use the calculator tool for all arithmetic to ensure accuracy.
Break complex problems into numbered steps and verify your final answer."""


# ---------------------------------------------------------------------------
# OAuth2 token management with caching
# ---------------------------------------------------------------------------
_token_cache: dict = {"token": None, "expires_at": 0.0}


def get_oauth_token() -> str:
    """Fetch or return cached OAuth2 token, refreshing 300s before expiry."""
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
# Calculator tool (local, no MCP)
# ---------------------------------------------------------------------------
ALLOWED_NAMES = {
    "abs": abs,
    "max": max,
    "min": min,
    "pow": pow,
    "round": round,
    "sum": sum,
    **{k: getattr(math, k) for k in dir(math) if not k.startswith("_")},
}


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression safely and return the result.

    Supports arithmetic operators (+, -, *, /, **), parentheses, and math
    functions (sqrt, sin, cos, tan, log, etc.). No system access allowed.

    Args:
        expression: A mathematical expression (e.g., "2 + 3 * 4", "math.sqrt(16)")
    """
    try:
        result = eval(expression, {"__builtins__": {}}, ALLOWED_NAMES)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error evaluating '{expression}': {str(e)}"


# ---------------------------------------------------------------------------
# Specialist agent tools (@tool decorated)
# ---------------------------------------------------------------------------
@tool
def course_review_agent(query: str) -> str:
    """Handle course catalog and review queries. Use for ANY question about courses, difficulty, reviews, ratings, recommendations, prerequisites, or course information."""
    mcp_client = get_mcp_client()
    model_config = get_model_config()
    model = BedrockModel(
        model_id=model_config["model_id"],
        region_name=model_config["region"],
        max_tokens=model_config["max_tokens"],
    )
    agent = Agent(
        model=model,
        system_prompt=COURSE_REVIEW_AGENT_PROMPT,
        tools=[mcp_client],
    )
    response = agent(query)
    return json.dumps({
        "response": str(response),
        "routing_path": "StudentServicesAgent → course_review_agent → AgentCore Gateway → CourseCatalogMcp + CourseReviewsMcp",
    })


@tool
def course_registration_agent(query: str) -> str:
    """Register students in courses. Requires student_id, course_name, and semester."""
    mcp_client = get_mcp_client()
    model_config = get_model_config()
    model = BedrockModel(
        model_id=model_config["model_id"],
        region_name=model_config["region"],
        max_tokens=model_config["max_tokens"],
    )
    agent = Agent(
        model=model,
        system_prompt=COURSE_REGISTRATION_AGENT_PROMPT,
        tools=[mcp_client],
    )
    response = agent(query)
    return json.dumps({
        "response": str(response),
        "routing_path": "StudentServicesAgent → course_registration_agent → AgentCore Gateway → CourseRegistrationMcp",
    })


@tool
def loan_application_agent(query: str) -> str:
    """Predict loan acceptance based on 59 numeric feature values provided as CSV."""
    mcp_client = get_mcp_client()
    model_config = get_model_config()
    model = BedrockModel(
        model_id=model_config["model_id"],
        region_name=model_config["region"],
        max_tokens=model_config["max_tokens"],
    )
    agent = Agent(
        model=model,
        system_prompt=LOAN_APPLICATION_AGENT_PROMPT,
        tools=[mcp_client],
    )
    response = agent(query)
    return json.dumps({
        "response": str(response),
        "routing_path": "StudentServicesAgent → loan_application_agent → AgentCore Gateway → LoanApplicationMcp",
    })


@tool
def math_teaching_agent(query: str) -> str:
    """Solve math problems with step-by-step explanations using a local calculator."""
    model_config = get_model_config()
    model = BedrockModel(
        model_id=model_config["model_id"],
        region_name=model_config["region"],
        max_tokens=model_config["max_tokens"],
    )
    agent = Agent(
        model=model,
        system_prompt=MATH_TEACHING_AGENT_PROMPT,
        tools=[calculator],
    )
    response = agent(query)
    return json.dumps({
        "response": str(response),
        "routing_path": "StudentServicesAgent → math_teaching_agent → calculator (local)",
    })


# ---------------------------------------------------------------------------
# BedrockAgentCoreApp entrypoint
# ---------------------------------------------------------------------------
app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload: dict, context: dict | None = None) -> dict:
    """Handle incoming requests by routing through the orchestrator agent."""
    prompt = payload.get("prompt", "")

    if not prompt or not prompt.strip():
        return {"response": "Error: 'prompt' field is required and cannot be empty."}

    model_config = get_model_config()
    model = BedrockModel(
        model_id=model_config["model_id"],
        region_name=model_config["region"],
        max_tokens=model_config["max_tokens"],
    )

    orchestrator = Agent(
        model=model,
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        tools=[
            course_review_agent,
            course_registration_agent,
            loan_application_agent,
            math_teaching_agent,
        ],
    )

    response = orchestrator(prompt)
    return {"response": str(response)}


if __name__ == "__main__":
    app.run()
