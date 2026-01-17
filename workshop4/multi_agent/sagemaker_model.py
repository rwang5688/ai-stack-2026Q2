#!/usr/bin/env python3
"""
SageMaker Model Module for Strands Agents

This module provides a factory function for creating SageMaker AI models
that can be used with Strands Agents.

IMPORTANT MODEL COMPATIBILITY NOTE:
===================================
The Strands Agents SDK SageMakerAIModel class requires SageMaker AI models 
that support OpenAI-compatible chat completion APIs.

During development and testing, the provider has been validated with 
Mistral-Small-24B-Instruct-2501, which demonstrated reliable performance 
across various conversational AI tasks.

Base language models (like Open Llama 7b V2) will fail with "Template error: 
template not found" because they lack the required chat completion API 
compatibility.

Reference: 
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/sagemaker/

Note: Tool calling support varies by model. Models like Mistral-Small-24B-Instruct-2501 
have demonstrated reliable tool calling capabilities, but not all models deployed on 
SageMaker support this feature. Verify your model's capabilities before implementing 
tool-based workflows.
"""

import warnings
from strands.models.sagemaker import SageMakerAIModel
from config import get_sagemaker_model_endpoint, get_sagemaker_model_inference_component, get_aws_region

# Suppress urllib3 warnings about unclosed connections
warnings.filterwarnings("ignore", message=".*unclosed.*", category=ResourceWarning)
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except:
    pass


def create_sagemaker_model(
    endpoint_name: str = None,
    inference_component: str = None,
    region: str = None,
    max_tokens: int = 1000,
    temperature: float = 0.7
) -> SageMakerAIModel:
    """
    Create a SageMaker AI model for Strands Agents.
    
    Args:
        endpoint_name: SageMaker endpoint name.
                      If None, uses value from get_sagemaker_model_endpoint().
        inference_component: Inference component name (for multi-model endpoints).
                           If None, uses value from get_sagemaker_model_inference_component().
                           Set to empty string to disable inference component usage.
        region: AWS region.
               If None, uses value from get_aws_region().
        max_tokens: Maximum tokens to generate (default: 1000)
        temperature: Model temperature setting (0.0 to 1.0).
                    Higher values make output more creative.
                    Default: 0.7
    
    Returns:
        Configured SageMakerAIModel instance
    
    Raises:
        ValueError: If endpoint_name is not provided and not set in environment
        RuntimeError: If endpoint is unavailable or inaccessible
    
    Example:
        >>> # Use default endpoint from environment
        >>> model = create_sagemaker_model()
        
        >>> # Use specific endpoint
        >>> model = create_sagemaker_model(
        ...     endpoint_name="my-custom-endpoint",
        ...     max_tokens=500,
        ...     temperature=0.5
        ... )
        
        >>> # Use endpoint without inference component
        >>> model = create_sagemaker_model(
        ...     endpoint_name="my-endpoint",
        ...     inference_component=""
        ... )
    """
    # Get endpoint name from parameter or config
    if endpoint_name is None:
        endpoint_name = get_sagemaker_model_endpoint()
    
    # Validate endpoint name
    if not endpoint_name or endpoint_name == "my-sagemaker-model-endpoint":
        raise ValueError(
            "SageMaker model endpoint name is required. "
            "Set SAGEMAKER_MODEL_ENDPOINT SSM parameter or pass endpoint_name parameter."
        )
    
    # Get inference component from parameter or config
    if inference_component is None:
        inference_component = get_sagemaker_model_inference_component()
    
    # Get AWS region from parameter or config
    if region is None:
        region = get_aws_region()
    
    # Build endpoint config
    endpoint_config = {
        "endpoint_name": endpoint_name,
        "region_name": region,
    }
    
    # Add inference component if specified and not empty
    if inference_component and inference_component != "my-agent-model-inference-component":
        endpoint_config["inference_component_name"] = inference_component
    
    # Create the SageMaker AI Model object
    sagemaker_model = SageMakerAIModel(
        endpoint_config=endpoint_config,
        payload_config={
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,  # Enable streaming for better user experience
        }
    )
    
    return sagemaker_model



def create_model_from_config(model_config: dict) -> SageMakerAIModel:
    """
    Create a SageMaker AI model instance from a configuration dictionary.
    
    This function is used to create models from serializable configuration,
    which is useful for distributed architectures where model objects
    cannot be passed directly.
    
    Args:
        model_config: Dictionary with model configuration:
            - endpoint_name: SageMaker endpoint name (required)
            - inference_component: Inference component name (optional)
            - region: AWS region (optional, uses config default)
            - max_tokens: Maximum tokens to generate (optional, default: 1000)
            - temperature: Model temperature (optional, default: 0.7)
    
    Returns:
        Configured SageMakerAIModel instance
    
    Example:
        >>> config = {
        ...     "endpoint_name": "my-endpoint",
        ...     "inference_component": "adapter-xyz",
        ...     "temperature": 0.5
        ... }
        >>> model = create_model_from_config(config)
    """
    return create_sagemaker_model(
        endpoint_name=model_config.get('endpoint_name'),
        inference_component=model_config.get('inference_component'),
        region=model_config.get('region'),
        max_tokens=model_config.get('max_tokens', 1000),
        temperature=model_config.get('temperature', 0.7)
    )
