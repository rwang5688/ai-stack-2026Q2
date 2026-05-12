"""
Loan Application Agent

Predicts loan acceptance using a SageMaker XGBoost endpoint.
Expects a CSV payload with 59 features representing customer demographics.
"""

import re
import sys
import os

import boto3
from botocore.config import Config
from strands import Agent, tool

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_app.config import get_aws_region, get_model_config, get_xgboost_endpoint
from shared.model_factory import create_model_from_config


BOTO_CONFIG = Config(read_timeout=60, connect_timeout=30, retries={"max_attempts": 2})

LOAN_ASSISTANT_SYSTEM_PROMPT = """You are a loan offering specialist that predicts loan acceptance.

Your capabilities:
1. Analyze customer feature payloads (59 CSV features)
2. Predict loan acceptance or rejection with confidence scores
3. Explain predictions clearly

The loan_prediction tool expects a CSV string with exactly 59 comma-separated numeric values.
Example: "29,2,999,0,1,0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0"

Present predictions clearly with the raw score, label (Accept/Reject), and confidence percentage."""


def validate_csv_features(payload: str) -> tuple:
    """
    Validate that the payload contains exactly 59 comma-separated values.

    Args:
        payload: CSV string of features.

    Returns:
        Tuple of (is_valid: bool, feature_count: int)
    """
    values = [v.strip() for v in payload.split(",")]
    return (len(values) == 59, len(values))


def interpret_prediction(score: float) -> dict:
    """
    Interpret a prediction score into a label and confidence.

    Args:
        score: Raw prediction score from XGBoost (0.0 to 1.0)

    Returns:
        Dictionary with "label" and "confidence" keys.
    """
    if score >= 0.5:
        return {"label": "Accept", "confidence": round(score * 100, 1)}
    else:
        return {"label": "Reject", "confidence": round((1 - score) * 100, 1)}


def _sanitize_error(error_msg: str) -> str:
    """Remove sensitive information from error messages."""
    # Remove ARNs
    sanitized = re.sub(r"arn:aws[^\s,\"']+", "[REDACTED]", error_msg)
    # Remove account IDs (12-digit numbers)
    sanitized = re.sub(r"\b\d{12}\b", "[REDACTED]", sanitized)
    # Remove endpoint names that look like AWS resources
    sanitized = re.sub(r"endpoint/[^\s,\"']+", "endpoint/[REDACTED]", sanitized)
    return sanitized


@tool
def loan_prediction(payload: str) -> str:
    """
    Predict loan acceptance using the XGBoost model endpoint.

    Args:
        payload: CSV string with exactly 59 features representing customer demographics.
                 Example: "29,2,999,0,1,0,0.0,1.0,0.0,..."

    Returns:
        Formatted prediction result with raw score, label, and confidence.
    """
    # Validate feature count
    is_valid, count = validate_csv_features(payload)
    if not is_valid:
        return f"Invalid payload: expected 59 features, got {count}. Please provide exactly 59 comma-separated numeric values."

    endpoint_name = get_xgboost_endpoint()
    region = get_aws_region()

    if not endpoint_name:
        return "XGBoost endpoint not configured. Please set the endpoint name in SSM parameters."

    # Extract endpoint name from ARN if full ARN was stored
    # ARN format: arn:aws:sagemaker:{region}:{account}:endpoint/{name}
    if endpoint_name.startswith("arn:"):
        endpoint_name = endpoint_name.split("/")[-1]

    try:
        runtime = boto3.client(
            "sagemaker-runtime", region_name=region, config=BOTO_CONFIG
        )

        response = runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            Body=payload,
            ContentType="text/csv",
        )

        result = response["Body"].read().decode()
        score = float(result.strip())

        prediction = interpret_prediction(score)

        return (
            f"Feature Payload: {payload}\n"
            f"Raw Prediction Score: {score:.4f}\n"
            f"Prediction: {prediction['label']}\n"
            f"Confidence: {prediction['confidence']}%"
        )

    except Exception as e:
        sanitized = _sanitize_error(str(e))
        return f"Error invoking prediction model: {sanitized}"


@tool
def loan_offering_assistant(query: str) -> str:
    """
    Process loan prediction queries using the XGBoost model.

    Args:
        query: A loan prediction question with CSV feature payload.

    Returns:
        A detailed prediction with raw score, label, and confidence.
    """
    try:
        print("Routed to Loan Offering Assistant")

        model_config = get_model_config()
        model = create_model_from_config(model_config)

        agent = Agent(
            model=model,
            system_prompt=LOAN_ASSISTANT_SYSTEM_PROMPT,
            tools=[loan_prediction],
        )

        response = agent(query)
        text_response = str(response)

        if text_response.strip():
            return f"[Loan Application Agent]\n\n{text_response}"

        return "[Loan Application Agent]\n\nI couldn't process your loan prediction. Please provide a CSV payload with 59 features."

    except Exception as e:
        sanitized = _sanitize_error(str(e))
        return f"[Loan Application Agent]\n\nError: {sanitized}"
