"""
Configuration module for the Student Services multi-agent application.

Fetches configuration from AWS Systems Manager Parameter Store with
environment variable overrides and hardcoded defaults as fallback.

Resolution order: environment variable → SSM Parameter Store → hardcoded default

SSM Parameters are stored under /student-services/ prefix.
"""

import os
from functools import lru_cache
from typing import Any, Dict, Optional

import boto3


# Default region for all AWS operations
DEFAULT_REGION = "us-west-2"


@lru_cache(maxsize=1)
def _get_ssm_client():
    """Get cached SSM client."""
    region = os.getenv("AWS_REGION", DEFAULT_REGION)
    return boto3.client("ssm", region_name=region)


@lru_cache(maxsize=1)
def _fetch_all_parameters() -> Dict[str, str]:
    """
    Fetch all parameters from SSM Parameter Store under /student-services/.

    Returns:
        Dictionary mapping parameter short names to values.
        e.g., {"model-id": "us.amazon.nova-2-lite-v1:0", ...}
    """
    ssm = _get_ssm_client()
    parameter_path = "/student-services/"

    params = {}
    next_token = None

    try:
        while True:
            kwargs = {
                "Path": parameter_path,
                "Recursive": True,
                "WithDecryption": False,
            }
            if next_token:
                kwargs["NextToken"] = next_token

            response = ssm.get_parameters_by_path(**kwargs)

            for param in response.get("Parameters", []):
                # Extract short name: /student-services/model-id -> model-id
                name = param["Name"].replace(parameter_path, "")
                params[name] = param["Value"]

            next_token = response.get("NextToken")
            if not next_token:
                break

    except Exception as e:
        print(f"Warning: Could not fetch SSM parameters: {e}")
        print("Falling back to hardcoded defaults.")

    return params


def _get_param(ssm_key: str, env_var: str, default: str) -> str:
    """
    Get a parameter value with resolution order:
    1. Environment variable
    2. SSM Parameter Store
    3. Hardcoded default

    Args:
        ssm_key: The short key name in SSM (e.g., "model-id")
        env_var: The environment variable name to check first
        default: Hardcoded default if neither env var nor SSM has a value
    """
    # 1. Environment variable takes precedence
    env_value = os.getenv(env_var)
    if env_value:
        return env_value

    # 2. SSM Parameter Store
    params = _fetch_all_parameters()
    if ssm_key in params:
        return params[ssm_key]

    # 3. Hardcoded default
    return default


# --- Public getter functions ---


def get_model_config() -> Dict[str, Any]:
    """
    Get model configuration dictionary for creating models via model_factory.

    Returns:
        Dictionary with provider, model_id, temperature, and region.
    """
    return {
        "provider": _get_param("model-provider", "MODEL_PROVIDER", "bedrock"),
        "model_id": _get_param("model-id", "MODEL_ID", "us.amazon.nova-2-lite-v1:0"),
        "temperature": float(_get_param("temperature", "MODEL_TEMPERATURE", "0.3")),
        "region": get_aws_region(),
    }


def get_knowledge_base_id() -> str:
    """Get Bedrock Knowledge Base ID."""
    return _get_param("knowledge-base-id", "KNOWLEDGE_BASE_ID", "")


def get_data_source_id() -> str:
    """Get Bedrock Knowledge Base data source ID."""
    return _get_param("data-source-id", "DATA_SOURCE_ID", "")


def get_xgboost_endpoint() -> str:
    """Get SageMaker XGBoost endpoint name for loan predictions."""
    return _get_param("xgboost-endpoint-name", "XGBOOST_ENDPOINT_NAME", "")


def get_aws_region() -> str:
    """Get AWS region."""
    return _get_param("aws-region", "AWS_REGION", DEFAULT_REGION)


def get_course_registration_table() -> str:
    """Get DynamoDB course registration table name."""
    return _get_param("course-registration-table", "COURSE_REGISTRATION_TABLE", "course_registration")


def get_course_reviews_table() -> str:
    """Get DynamoDB course reviews table name."""
    return _get_param("course-reviews-table", "COURSE_REVIEWS_TABLE", "course_reviews")


def get_all_config_values() -> Dict[str, str]:
    """
    Get all configuration values as a dictionary for debug display.

    Returns:
        Dictionary with all config key-value pairs.
    """
    return {
        "model_provider": _get_param("model-provider", "MODEL_PROVIDER", "bedrock"),
        "model_id": _get_param("model-id", "MODEL_ID", "us.amazon.nova-2-lite-v1:0"),
        "temperature": _get_param("temperature", "MODEL_TEMPERATURE", "0.3"),
        "aws_region": get_aws_region(),
        "knowledge_base_id": get_knowledge_base_id(),
        "data_source_id": get_data_source_id(),
        "xgboost_endpoint": get_xgboost_endpoint(),
        "course_registration_table": get_course_registration_table(),
        "course_reviews_table": get_course_reviews_table(),
    }


def clear_parameter_cache():
    """
    Clear the SSM parameter cache.

    Call this to refresh parameters from SSM without restarting the app.
    Useful when parameters are updated in the AWS console or via CLI.
    """
    _fetch_all_parameters.cache_clear()
    _get_ssm_client.cache_clear()
