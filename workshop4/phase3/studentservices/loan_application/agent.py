"""Loan Application MCP Server — Strands Agent wrapped as MCP tool via FastMCP.

The MCP tool delegates to an internal Strands Agent that handles loan prediction
requests using the SageMaker XGBoost endpoint.

Usage:
    agentcore dev --runtime LoanApplicationMcp
"""

import os
import re

import boto3
from fastmcp import FastMCP
from strands import Agent, tool
from strands.models import BedrockModel

mcp = FastMCP("loan-application-mcp-server")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
RUNTIME_NAME = "LoanApplicationMcp"
XGBOOST_ENDPOINT = os.environ.get(
    "XGBOOST_ENDPOINT",
    "arn:aws:sagemaker:us-west-2:149057604171:endpoint/xgboost-serverless-ep2026-05-10-06-08-28",
)

SYSTEM_PROMPT = """You are the Loan Offering Assistant for Any University (any.edu).
You help predict loan acceptance based on customer features.

To make a prediction, you need exactly 59 comma-separated numeric feature values.
Use the predict_loan tool with the CSV features string.

CRITICAL: When the user provides a CSV string of feature values, pass it EXACTLY as-is to the
predict_loan tool. Do NOT reformat, recount, truncate, or modify the string in any way.
Copy the entire comma-separated string verbatim into the features_csv parameter.

Interpret the results:
- Score >= 0.5: Loan likely to be ACCEPTED
- Score < 0.5: Loan likely to be REJECTED
- Confidence is based on how far the score is from the 0.5 threshold

Always explain the prediction result clearly to the user.
"""


# ---------------------------------------------------------------------------
# Pure functions
# ---------------------------------------------------------------------------
def _sanitize_error(msg: str) -> str:
    """Redact ARNs, 12-digit account IDs, and endpoint names."""
    msg = re.sub(r"arn:aws[:\w\-/]*", "[REDACTED_ARN]", msg)
    msg = re.sub(r"\b\d{12}\b", "[REDACTED_ACCOUNT]", msg)
    msg = re.sub(r"endpoint/[\w\-]+", "endpoint/[REDACTED]", msg)
    return msg


# ---------------------------------------------------------------------------
# Inner Strands tool
# ---------------------------------------------------------------------------
@tool
def predict_loan(features_csv: str) -> str:
    """Predict loan acceptance based on 59 numeric feature values.

    Args:
        features_csv: Exactly 59 comma-separated numeric values
    """
    values = [v.strip() for v in features_csv.split(",") if v.strip()]
    if len(values) != 59:
        return f"Error: Expected exactly 59 feature values, got {len(values)}."

    try:
        endpoint_name = XGBOOST_ENDPOINT
        if endpoint_name.startswith("arn:"):
            endpoint_name = endpoint_name.split("/")[-1]

        client = boto3.client("sagemaker-runtime", region_name=AWS_REGION)
        response = client.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType="text/csv",
            Body=features_csv.strip(),
        )
        score = float(response["Body"].read().decode("utf-8").strip())

        if score >= 0.5:
            label = "Accept"
            confidence = round(score * 100, 1)
        else:
            label = "Reject"
            confidence = round((1 - score) * 100, 1)

        return f"Score: {score:.4f}\nLabel: {label}\nConfidence: {confidence}%"
    except Exception as e:
        safe_msg = _sanitize_error(str(e))
        return f"Prediction failed: {safe_msg}"


# ---------------------------------------------------------------------------
# MCP tool (exposed to the gateway — wraps the Strands Agent)
# ---------------------------------------------------------------------------
@mcp.tool()
def loan_offering_assistant(prompt: str) -> dict:
    """Loan Application — predict loan acceptance based on customer features.

    This agent handles loan prediction requests. Provide the 59 CSV feature values
    or ask about loan acceptance likelihood.

    Args:
        prompt: Natural language request with 59 CSV feature values for prediction.

    Returns:
        Dict with the agent's response and runtime identifier.
    """
    model = BedrockModel(
        model_id="us.amazon.nova-2-lite-v1:0",
        region_name=AWS_REGION,
        max_tokens=4096,
    )

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[predict_loan],
    )

    response = agent(prompt)
    return {"response": str(response), "runtime": RUNTIME_NAME}


if __name__ == "__main__":
    if os.environ.get("MCP_TRANSPORT") == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", stateless_http=True)
    else:
        mcp.run()
