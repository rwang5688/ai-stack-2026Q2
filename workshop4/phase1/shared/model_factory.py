"""
Model Factory Module

Provides a unified interface for creating Strands Agent models from
configuration dictionaries. Supports Bedrock and SageMaker providers.

Usage:
    >>> from shared.model_factory import create_model_from_config
    >>> config = {
    ...     "provider": "bedrock",
    ...     "model_id": "us.amazon.nova-2-lite-v1:0",
    ...     "temperature": 0.3
    ... }
    >>> model = create_model_from_config(config)
"""

from typing import Any, Dict, Union

from strands.models import BedrockModel
from strands.models.sagemaker import SageMakerAIModel


SUPPORTED_PROVIDERS = ["bedrock", "sagemaker"]


def create_model_from_config(model_config: Dict[str, Any]) -> Union[BedrockModel, SageMakerAIModel]:
    """
    Create a model instance from a configuration dictionary.

    Args:
        model_config: Dictionary with model configuration:
            - provider: "bedrock" or "sagemaker" (required)
            - model_id: Model ID (required)
            - temperature: Model temperature 0.0-1.0 (optional)
            - region: AWS region (optional, default: us-west-2)
            - endpoint_name: SageMaker endpoint (required if provider=sagemaker)

    Returns:
        Model instance (BedrockModel or SageMakerAIModel)

    Raises:
        ValueError: If provider is not supported, model_id is missing,
                    or temperature is outside valid range.
    """
    provider = model_config.get("provider")
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unsupported provider: '{provider}'. "
            f"Supported providers: {SUPPORTED_PROVIDERS}"
        )

    model_id = model_config.get("model_id")
    if not model_id:
        raise ValueError("model_id is required in model configuration.")

    temperature = model_config.get("temperature")
    if temperature is not None:
        if not isinstance(temperature, (int, float)) or temperature < 0.0 or temperature > 1.0:
            raise ValueError(
                f"temperature must be between 0.0 and 1.0, got: {temperature}"
            )

    region = model_config.get("region", "us-west-2")

    if provider == "bedrock":
        kwargs = {
            "model_id": model_id,
            "region_name": region,
        }
        if temperature is not None:
            kwargs["temperature"] = temperature
        return BedrockModel(**kwargs)

    elif provider == "sagemaker":
        kwargs = {
            "endpoint_name": model_config.get("endpoint_name", model_id),
            "region_name": region,
        }
        if temperature is not None:
            kwargs["temperature"] = temperature
        inference_component = model_config.get("inference_component")
        if inference_component:
            kwargs["inference_component_name"] = inference_component
        return SageMakerAIModel(**kwargs)
