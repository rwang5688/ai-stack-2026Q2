"""Loan Application MCP Server — predict loan acceptance via SageMaker endpoint."""

import os
import re

import boto3
from fastmcp import FastMCP

mcp = FastMCP("loan-application-mcp-server")

AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
XGBOOST_ENDPOINT = os.environ.get(
    "XGBOOST_ENDPOINT", "xgboost-serverless-ep2026-05-10-06-08-28"
)


def _sanitize_error(msg: str) -> str:
    """Redact ARNs and 12-digit account IDs from error messages."""
    msg = re.sub(r"arn:aws[:\w\-/]*", "[REDACTED_ARN]", msg)
    msg = re.sub(r"\b\d{12}\b", "[REDACTED_ACCOUNT]", msg)
    return msg


@mcp.tool()
def predict_loan(features_csv: str) -> dict:
    """Predict loan acceptance based on 59 numeric feature values.

    Args:
        features_csv: Exactly 59 comma-separated numeric values.

    Returns:
        Dict with score, label, and confidence, or error dict.
    """
    values = [v.strip() for v in features_csv.split(",") if v.strip()]
    if len(values) != 59:
        return {"error": f"Expected 59 features, got {len(values)}"}

    try:
        endpoint_name = XGBOOST_ENDPOINT
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

        return {"score": score, "label": label, "confidence": confidence}
    except Exception as e:
        safe_msg = _sanitize_error(str(e))
        return {"error": f"Prediction failed: {safe_msg}"}


if __name__ == "__main__":
    if os.environ.get("MCP_TRANSPORT") == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", stateless_http=True)
    else:
        mcp.run()
