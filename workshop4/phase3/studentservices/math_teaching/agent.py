"""Math Teaching MCP Server — Strands Agent wrapped as MCP tool via FastMCP.

The MCP tool delegates to an internal Strands Agent that provides step-by-step
mathematical tutoring using calculator tools.

Usage:
    agentcore dev --runtime MathTeachingMcp
"""

import math
import os

import boto3
from fastmcp import FastMCP
from strands import Agent, tool
from strands.models import BedrockModel

mcp = FastMCP("math-teaching-mcp-server")

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
# Configuration
# ---------------------------------------------------------------------------
AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
RUNTIME_NAME = "MathTeachingMcp"

SYSTEM_PROMPT = """You are the Math Teaching Assistant for Any University (any.edu).
You help students solve math problems with clear, step-by-step explanations.

Guidelines:
- Break complex problems into numbered sub-steps
- Show intermediate calculations using the calculator tool
- Explain the reasoning behind each step
- Use real-world analogies where applicable
- Verify your final answer with the calculator

Use the calculator tool for all arithmetic operations to ensure accuracy.
"""


# ---------------------------------------------------------------------------
# Inner Strands tool
# ---------------------------------------------------------------------------
@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression and return the result.

    Args:
        expression: A mathematical expression (e.g., "2 + 3 * 4", "math.sqrt(16)")
    """
    try:
        allowed_names = {
            "abs": abs,
            "math": math,
            "max": max,
            "min": min,
            "pow": pow,
            "round": round,
            "sum": sum,
        }
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error evaluating '{expression}': {str(e)}"


# ---------------------------------------------------------------------------
# MCP tool (exposed to the gateway — wraps the Strands Agent)
# ---------------------------------------------------------------------------
@mcp.tool()
def math_assistant(prompt: str) -> dict:
    """Math Teaching — solve math problems with step-by-step explanations.

    This agent provides pedagogical math tutoring with calculator-verified solutions.

    Args:
        prompt: A math problem or question (e.g., "Solve x^2 + 5x + 6 = 0")

    Returns:
        Dict with the agent's step-by-step response and runtime identifier.
    """
    model_config = get_model_config()
    model = BedrockModel(
        model_id=model_config["model_id"],
        region_name=model_config["region"],
        max_tokens=model_config["max_tokens"],
    )

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[calculator],
    )

    response = agent(prompt)
    return {"response": str(response), "runtime": RUNTIME_NAME}


if __name__ == "__main__":
    if os.environ.get("MCP_TRANSPORT") == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", stateless_http=True)
    else:
        mcp.run()
