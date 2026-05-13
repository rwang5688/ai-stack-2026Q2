"""Loan Application Agent — predicts loan acceptance via SageMaker XGBoost endpoint.

Usage:
    agentcore dev --runtime LoanApplicationAgent
"""

import os
import re
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import boto3
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
XGBOOST_ENDPOINT = os.environ.get(
    "XGBOOST_ENDPOINT",
    "arn:aws:sagemaker:us-west-2:149057604171:endpoint/xgboost-serverless-ep2026-05-10-06-08-28",
)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are the Loan Offering Assistant for Any University (any.edu).
You help predict loan acceptance based on customer features.

To make a prediction, you need exactly 59 comma-separated numeric feature values.
Use the predict_loan tool with the CSV features string.

Interpret the results:
- Score >= 0.5: Loan likely to be ACCEPTED
- Score < 0.5: Loan likely to be REJECTED
- Confidence is based on how far the score is from the 0.5 threshold
"""


# ---------------------------------------------------------------------------
# Pure functions
# ---------------------------------------------------------------------------
def validate_csv_features(payload: str) -> tuple[bool, int]:
    """Check that payload contains exactly 59 comma-separated values."""
    values = [v.strip() for v in payload.split(",") if v.strip()]
    return (len(values) == 59, len(values))


def interpret_prediction(score: float) -> dict:
    """Map prediction score to label and confidence."""
    if score >= 0.5:
        return {"label": "Accept", "confidence": round(score * 100, 1), "score": score}
    else:
        return {"label": "Reject", "confidence": round((1 - score) * 100, 1), "score": score}


def sanitize_error(msg: str) -> str:
    """Redact ARNs, 12-digit account IDs, and endpoint names from error messages."""
    # Redact ARNs
    msg = re.sub(r"arn:aws[:\w\-/]*", "[REDACTED_ARN]", msg)
    # Redact 12-digit account IDs
    msg = re.sub(r"\b\d{12}\b", "[REDACTED_ACCOUNT]", msg)
    # Redact endpoint names after endpoint/
    msg = re.sub(r"endpoint/[\w\-]+", "endpoint/[REDACTED]", msg)
    return msg


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
@tool
def predict_loan(features_csv: str) -> str:
    """Predict loan acceptance based on 59 numeric feature values.

    Args:
        features_csv: Exactly 59 comma-separated numeric values
    """
    is_valid, count = validate_csv_features(features_csv)
    if not is_valid:
        return f"[Loan Application Agent] Error: Expected exactly 59 feature values, got {count}."

    try:
        # Extract endpoint name from ARN if needed
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
        result = interpret_prediction(score)

        return (
            f"[Loan Application Agent] Prediction Result:\n"
            f"Score: {result['score']:.4f}\n"
            f"Label: {result['label']}\n"
            f"Confidence: {result['confidence']}%"
        )
    except Exception as e:
        safe_msg = sanitize_error(str(e))
        return f"[Loan Application Agent] Prediction failed: {safe_msg}"


# ---------------------------------------------------------------------------
# BedrockAgentCoreApp entrypoint
# ---------------------------------------------------------------------------
app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload: dict, context: dict | None = None) -> dict:
    prompt = payload.get("prompt", "")
    if not prompt or not prompt.strip():
        return {"response": "Error: 'prompt' field is required."}

    model = BedrockModel(
        model_id="us.amazon.nova-2-lite-v1:0",
        region_name="us-west-2",
        max_tokens=4096,
    )

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[predict_loan],
    )

    response = agent(prompt)
    return {"response": str(response)}


if __name__ == "__main__":
    app.run()
