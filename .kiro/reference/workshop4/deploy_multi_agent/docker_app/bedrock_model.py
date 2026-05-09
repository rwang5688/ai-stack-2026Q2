#!/usr/bin/env python3
"""
Bedrock Model Module for Strands Agents

This module provides a factory function for creating Bedrock models
with support for multiple cross-region inference profiles.

Supported Models:
    - us.amazon.nova-2-lite-v1:0 (default)
    - us.amazon.nova-pro-v1:0
    - us.anthropic.claude-haiku-4-5-20251001-v1:0
    - us.anthropic.claude-sonnet-4-5-20250929-v1:0
"""

import re
from strands.models import BedrockModel
from config import get_default_model_id, get_aws_region


# ARN pattern for Bedrock custom model deployments
ARN_PATTERN = r'^arn:aws:bedrock:[a-z0-9-]+:\d{12}:custom-model-deployment/[a-zA-Z0-9]+'

# Supported cross-region inference profiles
SUPPORTED_MODELS = [
    "us.amazon.nova-2-lite-v1:0",
    "us.amazon.nova-pro-v1:0",
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
]


def create_bedrock_model(
    model_id: str = None,
    temperature: float = 0.3
) -> BedrockModel:
    """
    Create a Bedrock model instance.
    
    Args:
        model_id: Bedrock model ID, cross-region profile, or custom model deployment ARN.
                 If None, uses value from get_default_model_id().
                 ARN format: arn:aws:bedrock:{region}:{account}:custom-model-deployment/{id}
                 Default: us.amazon.nova-2-lite-v1:0
        temperature: Model temperature setting (0.0 to 1.0).
                    Lower values make output more deterministic.
                    Default: 0.3
    
    Returns:
        Configured BedrockModel instance
    
    Raises:
        ValueError: If model_id is not in the list of supported models and is not a valid ARN
    
    Example:
        >>> # Use default model from environment
        >>> model = create_bedrock_model()
        
        >>> # Use specific model
        >>> model = create_bedrock_model(
        ...     model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        ...     temperature=0.5
        ... )
        
        >>> # Use custom model deployment ARN
        >>> model = create_bedrock_model(
        ...     model_id="arn:aws:bedrock:us-east-1:123456789012:custom-model-deployment/abc123",
        ...     temperature=0.3
        ... )
    """
    # Get model ID from parameter or config
    if model_id is None:
        model_id = get_default_model_id()
    
    # Check if model_id is an ARN (custom model deployment)
    is_arn = re.match(ARN_PATTERN, model_id) is not None
    
    # Validate model ID only if it's not an ARN
    if not is_arn and model_id not in SUPPORTED_MODELS:
        raise ValueError(
            f"Invalid Bedrock model ID: '{model_id}'. "
            f"Supported models: {', '.join(SUPPORTED_MODELS)}"
        )
    
    # Get AWS region from config
    region = get_aws_region()
    
    # Create and return Bedrock model
    return BedrockModel(
        model_id=model_id,
        region_name=region,
        temperature=temperature
    )



def create_model_from_config(model_config: dict) -> BedrockModel:
    """
    Create a Bedrock model instance from a configuration dictionary.
    
    This function is used to create models from serializable configuration,
    which is useful for distributed architectures where model objects
    cannot be passed directly.
    
    Args:
        model_config: Dictionary with model configuration:
            - model_id: Bedrock model ID (required)
            - temperature: Model temperature (optional, default: 0.3)
            - region: AWS region (optional, uses config default)
    
    Returns:
        Configured BedrockModel instance
    
    Example:
        >>> config = {
        ...     "model_id": "us.amazon.nova-2-lite-v1:0",
        ...     "temperature": 0.5
        ... }
        >>> model = create_model_from_config(config)
    """
    return create_bedrock_model(
        model_id=model_config.get('model_id'),
        temperature=model_config.get('temperature', 0.3)
    )
