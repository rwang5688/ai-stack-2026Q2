#!/usr/bin/env python3
"""
Configuration module for multi-agent application.

This module centralizes environment variable management and provides
validated configuration values for the application. All environment
variable access should go through this module to ensure consistency
and proper validation.

Environment variables are organized alphabetically for easy lookup.
"""

import os
from typing import Optional


def get_aws_region() -> str:
    """
    Get AWS region from environment variable.
    
    Environment Variable: AWS_REGION
    Default: us-east-1 (recommended for workshop to access Nova Forge)
    
    Returns:
        AWS region string (e.g., 'us-east-1', 'us-west-2')
    
    Example:
        >>> region = get_aws_region()
        >>> print(region)
        'us-east-1'
    """
    return os.getenv("AWS_REGION", "us-east-1")


def get_bedrock_model_id() -> str:
    """
    Get Bedrock model ID from environment variable.
    
    Environment Variable: BEDROCK_MODEL_ID
    Default: us.amazon.nova-pro-v1:0
    
    Supported Models:
        - us.amazon.nova-pro-v1:0 (default)
        - us.amazon.nova-2-lite-v1:0
        - us.anthropic.claude-haiku-4-5-20251001-v1:0
        - us.anthropic.claude-sonnet-4-5-20250929-v1:0
    
    Returns:
        Bedrock model ID or cross-region inference profile
    
    Example:
        >>> model_id = get_bedrock_model_id()
        >>> print(model_id)
        'us.amazon.nova-pro-v1:0'
    """
    return os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0")


def get_max_results() -> int:
    """
    Get maximum results for knowledge base queries.
    
    Environment Variable: MAX_RESULTS
    Default: 9
    
    Returns:
        Maximum number of results to return from knowledge base queries
    
    Example:
        >>> max_results = get_max_results()
        >>> print(max_results)
        9
    """
    return int(os.getenv("MAX_RESULTS", "9"))


def get_min_score() -> float:
    """
    Get minimum score threshold for knowledge base queries.
    
    Environment Variable: MIN_SCORE
    Default: 0.000001
    
    Returns:
        Minimum relevance score threshold (0.0 to 1.0)
    
    Example:
        >>> min_score = get_min_score()
        >>> print(min_score)
        0.000001
    """
    return float(os.getenv("MIN_SCORE", "0.000001"))


def get_sagemaker_inference_component() -> Optional[str]:
    """
    Get SageMaker inference component name from environment variable.
    
    Environment Variable: SAGEMAKER_INFERENCE_COMPONENT
    Default: my-llm-inference-component
    Required: Only when endpoint uses inference components (multi-model endpoints)
    
    Inference components allow multiple models/adapters on a single endpoint.
    If your endpoint uses inference components, you must specify which one to use.
    
    Returns:
        Inference component name or default placeholder
    
    Example:
        >>> component = get_sagemaker_inference_component()
        >>> print(component)
        'adapter-my-gpt-oss-20b-1-1768457329-1768457350'
    
    Note:
        To list inference components for an endpoint:
        aws sagemaker list-inference-components --endpoint-name-equals <endpoint-name>
    """
    return os.getenv("SAGEMAKER_INFERENCE_COMPONENT", "my-llm-inference-component")


def get_sagemaker_model_endpoint() -> str:
    """
    Get SageMaker model endpoint name from environment variable.
    
    Environment Variable: SAGEMAKER_MODEL_ENDPOINT
    Default: my-llm-endpoint
    Required: Only when STRANDS_MODEL_PROVIDER=sagemaker
    
    Returns:
        SageMaker endpoint name
    
    Raises:
        ValueError: If provider is 'sagemaker' but endpoint is not set
    
    Example:
        >>> endpoint = get_sagemaker_model_endpoint()
        >>> print(endpoint)
        'my-llm-endpoint'
    """
    return os.getenv("SAGEMAKER_MODEL_ENDPOINT", "my-llm-endpoint")


def get_strands_knowledge_base_id() -> str:
    """
    Get Strands knowledge base ID from environment variable.
    
    Environment Variable: STRANDS_KNOWLEDGE_BASE_ID
    Default: my-kb-id
    
    Returns:
        Knowledge base ID for memory operations
    
    Example:
        >>> kb_id = get_strands_knowledge_base_id()
        >>> print(kb_id)
        'my-kb-id'
    """
    return os.getenv("STRANDS_KNOWLEDGE_BASE_ID", "my-kb-id")


def get_strands_model_provider() -> str:
    """
    Get Strands Agent model provider from environment variable.
    
    Environment Variable: STRANDS_MODEL_PROVIDER
    Default: bedrock
    Valid Values: bedrock, sagemaker
    
    Returns:
        Model provider choice ('bedrock' or 'sagemaker')
    
    Raises:
        ValueError: If provider is not 'bedrock' or 'sagemaker'
    
    Example:
        >>> provider = get_strands_model_provider()
        >>> print(provider)
        'bedrock'
    """
    provider = os.getenv("STRANDS_MODEL_PROVIDER", "bedrock").lower()
    
    # Validate provider value
    valid_providers = ["bedrock", "sagemaker"]
    if provider not in valid_providers:
        raise ValueError(
            f"Invalid STRANDS_MODEL_PROVIDER: '{provider}'. "
            f"Must be one of: {', '.join(valid_providers)}"
        )
    
    return provider


def get_xgboost_endpoint_name() -> str:
    """
    Get XGBoost model endpoint name from environment variable.
    
    Environment Variable: XGBOOST_ENDPOINT_NAME
    Default: my-xgboost-endpoint
    Required: Only when using loan assistant feature
    
    Returns:
        XGBoost endpoint name
    
    Example:
        >>> endpoint = get_xgboost_endpoint_name()
        >>> print(endpoint)
        'my-xgboost-endpoint'
    """
    return os.getenv("XGBOOST_ENDPOINT_NAME", "my-xgboost-endpoint")


# Utility function for debugging
def get_all_config_values() -> dict:
    """
    Get all configuration values as a dictionary.
    
    Useful for debugging and displaying current configuration.
    
    Returns:
        Dictionary with all configuration values
    
    Example:
        >>> config = get_all_config_values()
        >>> for key, value in config.items():
        ...     print(f"{key}: {value}")
    """
    return {
        "AWS_REGION": get_aws_region(),
        "BEDROCK_MODEL_ID": get_bedrock_model_id(),
        "MAX_RESULTS": get_max_results(),
        "MIN_SCORE": get_min_score(),
        "SAGEMAKER_INFERENCE_COMPONENT": get_sagemaker_inference_component(),
        "SAGEMAKER_MODEL_ENDPOINT": get_sagemaker_model_endpoint(),
        "STRANDS_KNOWLEDGE_BASE_ID": get_strands_knowledge_base_id(),
        "STRANDS_MODEL_PROVIDER": get_strands_model_provider(),
        "XGBOOST_ENDPOINT_NAME": get_xgboost_endpoint_name(),
    }
