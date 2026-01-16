#!/usr/bin/env python3
"""
Configuration module for multi-agent application.

This module fetches all configuration from AWS Systems Manager Parameter Store.
No environment variables are used except for TEACHASSIST_ENV (which specifies
the environment: dev, staging, or prod) and AWS credentials.

All configuration parameters are stored in SSM Parameter Store under:
    /teachassist/{environment}/{category}/{parameter_name}

Example:
    /teachassist/dev/bedrock/model_id
    /teachassist/prod/sagemaker/model_endpoint

To deploy parameters, use the CloudFormation template in workshop4/ssm/
"""

import os
import boto3
from typing import Optional, Dict, Any
from functools import lru_cache


# Get environment from environment variable (only env var we use!)
TEACHASSIST_ENV = os.getenv('TEACHASSIST_ENV', 'dev')


@lru_cache(maxsize=1)
def _get_ssm_client():
    """Get cached SSM client."""
    # AWS region can be set via AWS_REGION env var or AWS config
    region = os.getenv('AWS_REGION', 'us-east-1')
    return boto3.client('ssm', region_name=region)


@lru_cache(maxsize=1)
def _fetch_all_parameters() -> Dict[str, str]:
    """
    Fetch all parameters from SSM Parameter Store for the current environment.
    
    This function fetches all parameters under /teachassist/{env}/ and caches them.
    The cache is cleared when the Python process restarts.
    
    Returns:
        Dictionary mapping parameter names to values
    """
    ssm = _get_ssm_client()
    parameter_path = f'/teachassist/{TEACHASSIST_ENV}'
    
    try:
        # Fetch all parameters recursively
        response = ssm.get_parameters_by_path(
            Path=parameter_path,
            Recursive=True,
            WithDecryption=True
        )
        
        # Build dictionary of parameter name -> value
        params = {}
        for param in response['Parameters']:
            # Extract the parameter name (last part of the path)
            # e.g., /teachassist/dev/bedrock/model_id -> bedrock/model_id
            name = param['Name'].replace(f'{parameter_path}/', '')
            params[name] = param['Value']
        
        return params
        
    except Exception as e:
        print(f"Error fetching parameters from SSM: {e}")
        print(f"Ensure parameters are deployed for environment: {TEACHASSIST_ENV}")
        print(f"See workshop4/ssm/README.md for deployment instructions")
        raise


def _get_parameter(category: str, name: str, default: Optional[str] = None) -> str:
    """
    Get a parameter value from the cached parameters.
    
    Args:
        category: Parameter category (e.g., 'bedrock', 'sagemaker')
        name: Parameter name (e.g., 'model_id', 'endpoint_name')
        default: Default value if parameter not found
    
    Returns:
        Parameter value
    
    Raises:
        KeyError: If parameter not found and no default provided
    """
    params = _fetch_all_parameters()
    key = f'{category}/{name}'
    
    if key in params:
        return params[key]
    elif default is not None:
        return default
    else:
        raise KeyError(
            f"Parameter '{key}' not found in SSM Parameter Store for environment '{TEACHASSIST_ENV}'. "
            f"Deploy parameters using: aws cloudformation create-stack --stack-name teachassist-params-{TEACHASSIST_ENV} "
            f"--template-body file://workshop4/ssm/teachassist-params.yaml"
        )


# Configuration getter functions (alphabetically sorted)

def get_aws_region() -> str:
    """
    Get AWS region from SSM Parameter Store.
    
    Parameter: /teachassist/{env}/aws/region
    Default: us-east-1
    
    Returns:
        AWS region string (e.g., 'us-east-1', 'us-west-2')
    
    Example:
        >>> region = get_aws_region()
        >>> print(region)
        'us-east-1'
    """
    return _get_parameter('aws', 'region', default='us-east-1')


def get_bedrock_model_id() -> str:
    """
    Get Bedrock model ID from SSM Parameter Store.
    
    Parameter: /teachassist/{env}/bedrock/model_id
    Default: us.amazon.nova-2-lite-v1:0
    
    Supported Models:
        - us.amazon.nova-2-lite-v1:0 (default)
        - us.amazon.nova-pro-v1:0
        - us.anthropic.claude-haiku-4-5-20251001-v1:0
        - us.anthropic.claude-sonnet-4-5-20250929-v1:0
    
    Returns:
        Bedrock model ID or cross-region inference profile
    
    Example:
        >>> model_id = get_bedrock_model_id()
        >>> print(model_id)
        'us.amazon.nova-2-lite-v1:0'
    """
    return _get_parameter('bedrock', 'model_id', default='us.amazon.nova-2-lite-v1:0')


def get_max_results() -> int:
    """
    Get maximum results for knowledge base queries from SSM Parameter Store.
    
    Parameter: /teachassist/{env}/knowledge_base/max_results
    Default: 9
    
    Returns:
        Maximum number of results to return from knowledge base queries
    
    Example:
        >>> max_results = get_max_results()
        >>> print(max_results)
        9
    """
    return int(_get_parameter('knowledge_base', 'max_results', default='9'))


def get_min_score() -> float:
    """
    Get minimum score threshold for knowledge base queries from SSM Parameter Store.
    
    Parameter: /teachassist/{env}/knowledge_base/min_score
    Default: 0.000001
    
    Returns:
        Minimum relevance score threshold (0.0 to 1.0)
    
    Example:
        >>> min_score = get_min_score()
        >>> print(min_score)
        0.000001
    """
    return float(_get_parameter('knowledge_base', 'min_score', default='0.000001'))


def get_sagemaker_inference_component() -> Optional[str]:
    """
    Get SageMaker inference component name from SSM Parameter Store.
    
    Parameter: /teachassist/{env}/sagemaker/inference_component
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
    return _get_parameter('sagemaker', 'inference_component', default='my-llm-inference-component')


def get_sagemaker_model_endpoint() -> str:
    """
    Get SageMaker model endpoint name from SSM Parameter Store.
    
    Parameter: /teachassist/{env}/sagemaker/model_endpoint
    Default: my-llm-endpoint
    Required: Only when STRANDS_MODEL_PROVIDER=sagemaker
    
    Returns:
        SageMaker endpoint name
    
    Example:
        >>> endpoint = get_sagemaker_model_endpoint()
        >>> print(endpoint)
        'my-gpt-oss-20b-1-1768457329'
    """
    return _get_parameter('sagemaker', 'model_endpoint', default='my-llm-endpoint')


def get_strands_knowledge_base_id() -> str:
    """
    Get Strands knowledge base ID from SSM Parameter Store.
    
    Parameter: /teachassist/{env}/strands/knowledge_base_id
    Default: my-kb-id
    
    Returns:
        Knowledge base ID for memory operations
    
    Example:
        >>> kb_id = get_strands_knowledge_base_id()
        >>> print(kb_id)
        'IMW46CITZE'
    """
    return _get_parameter('strands', 'knowledge_base_id', default='my-kb-id')


def get_temperature() -> float:
    """
    Get model temperature setting from SSM Parameter Store.
    
    Parameter: /teachassist/{env}/model/temperature
    Default: 0.3
    
    Returns:
        Model temperature (0.0 to 1.0)
    
    Example:
        >>> temp = get_temperature()
        >>> print(temp)
        0.3
    """
    return float(_get_parameter('model', 'temperature', default='0.3'))


def get_xgboost_endpoint_name() -> str:
    """
    Get XGBoost model endpoint name from SSM Parameter Store.
    
    Parameter: /teachassist/{env}/xgboost/endpoint_name
    Default: my-xgboost-endpoint
    Required: Only when using loan assistant feature
    
    Returns:
        XGBoost endpoint name
    
    Example:
        >>> endpoint = get_xgboost_endpoint_name()
        >>> print(endpoint)
        'xgboost-serverless-ep2026-01-12-05-31-16'
    """
    return _get_parameter('xgboost', 'endpoint_name', default='my-xgboost-endpoint')


# Model configuration functions

def get_default_model_config() -> Dict[str, Any]:
    """
    Get default model configuration for creating models.
    
    This function returns a configuration dictionary that can be used
    to create model instances. It supports both Bedrock and SageMaker
    providers.
    
    Note: The provider is determined dynamically based on user selection
    in the UI, not from configuration. This function returns Bedrock
    configuration by default.
    
    Returns:
        Dictionary with model configuration:
            - provider: "bedrock" (default)
            - model_id: Bedrock model ID
            - temperature: Model temperature
            - region: AWS region
    
    Example:
        >>> config = get_default_model_config()
        >>> print(config['provider'])
        'bedrock'
        >>> print(config['model_id'])
        'us.amazon.nova-2-lite-v1:0'
    """
    config = {
        "provider": "bedrock",
        "model_id": get_bedrock_model_id(),
        "temperature": 0.3,
        "region": get_aws_region()
    }
    
    return config


# Utility functions

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
        "TEACHASSIST_ENV": TEACHASSIST_ENV,
        "AWS_REGION": get_aws_region(),
        "BEDROCK_MODEL_ID": get_bedrock_model_id(),
        "MAX_RESULTS": get_max_results(),
        "MIN_SCORE": get_min_score(),
        "SAGEMAKER_INFERENCE_COMPONENT": get_sagemaker_inference_component(),
        "SAGEMAKER_MODEL_ENDPOINT": get_sagemaker_model_endpoint(),
        "STRANDS_KNOWLEDGE_BASE_ID": get_strands_knowledge_base_id(),
        "TEMPERATURE": get_temperature(),
        "XGBOOST_ENDPOINT_NAME": get_xgboost_endpoint_name(),
    }


def clear_parameter_cache():
    """
    Clear the parameter cache.
    
    Call this function if you've updated parameters in SSM and want
    the application to fetch fresh values without restarting.
    
    Note: In production, parameters are cached for the lifetime of the
    Python process. Restart the application to pick up parameter changes.
    """
    _fetch_all_parameters.cache_clear()
