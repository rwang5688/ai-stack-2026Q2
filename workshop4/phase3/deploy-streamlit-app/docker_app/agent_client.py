"""HTTP client for communicating with the StudentServicesAgent runtime on AgentCore.

Sends prompts to the StudentServicesAgent runtime via SigV4-signed HTTP POST
requests. The runtime URL is read from the STUDENT_SERVICES_AGENT_URL environment
variable (injected by the ECS task definition).
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

    Args:
        prompt: The user message to send to the agent.

    Returns:
        The agent's response text.

    Raises:
        RuntimeError: On non-200 status or network errors.
    """
    import httpx

    body = json.dumps({"prompt": prompt})

    # SigV4 signing
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
