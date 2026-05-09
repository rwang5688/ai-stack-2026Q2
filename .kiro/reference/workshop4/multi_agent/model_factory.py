#!/usr/bin/env python3
"""
Model Factory Module

This module provides a unified interface for creating models from
configuration dictionaries. It supports both Bedrock and SageMaker
model providers and is designed for distributed architectures where
model objects cannot be passed directly between components.

Usage:
    >>> from model_factory import create_model_from_config
    >>> config = {
    ...     "provider": "bedrock",
    ...     "model_id": "us.amazon.nova-2-lite-v1:0",
    ...     "temperature": 0.3
    ... }
    >>> model = create_model_from_config(config)
"""

from typing import Dict, Any, Union
from strands.models import BedrockModel
from strands.models.sagemaker import SageMakerAIModel

import bedrock_model
import sagemaker_model


def create_model_from_config(model_config: Dict[str, Any]) -> Union[BedrockModel, SageMakerAIModel]:
    """
    Create a model instance from a configuration dictionary.
    
    This function routes to the appropriate model creation function
    based on the provider specified in the configuration.
    
    Args:
        model_config: Dictionary with model configuration:
            - provider: "bedrock" or "sagemaker" (required)
            - model_id: Bedrock model ID (required if provider=bedrock)
            - endpoint_name: SageMaker endpoint (required if provider=sagemaker)
            - inference_component: SageMaker component (optional)
            - temperature: Model temperature (optional)
            - region: AWS region (optional)
            - max_tokens: Maximum tokens (optional, SageMaker only)
    
    Returns:
        Model instance (BedrockModel or SageMakerAIModel)
    
    Raises:
        ValueError: If provider is not "bedrock" or "sagemaker"
    
    Example:
        >>> # Bedrock model
        >>> config = {
        ...     "provider": "bedrock",
        ...     "model_id": "us.amazon.nova-2-lite-v1:0",
        ...     "temperature": 0.3
        ... }
        >>> model = create_model_from_config(config)
        
        >>> # SageMaker model
        >>> config = {
        ...     "provider": "sagemaker",
        ...     "endpoint_name": "my-endpoint",
        ...     "inference_component": "adapter-xyz",
        ...     "temperature": 0.7
        ... }
        >>> model = create_model_from_config(config)
    """
    provider = model_config.get('provider', 'bedrock')
    
    if provider == 'bedrock':
        return bedrock_model.create_model_from_config(model_config)
    elif provider == 'sagemaker':
        return sagemaker_model.create_model_from_config(model_config)
    else:
        raise ValueError(
            f"Unknown provider: '{provider}'. "
            f"Must be 'bedrock' or 'sagemaker'"
        )
