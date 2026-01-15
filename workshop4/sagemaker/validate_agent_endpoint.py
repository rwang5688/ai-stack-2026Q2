#!/usr/bin/env python3
"""
Agent Model Endpoint Validation Script

This script validates that a SageMaker agent model endpoint is working correctly
by sending a test inference request and verifying the response.

Usage:
    python validate_agent_endpoint.py

Environment Variables:
    SAGEMAKER_MODEL_ENDPOINT: Name of the SageMaker endpoint to validate
    SAGEMAKER_INFERENCE_COMPONENT: (Optional) Inference component name for multi-model endpoints
    AWS_REGION: AWS region where the endpoint is deployed (default: us-east-1)
"""

import os
import sys
import json
import boto3
from typing import Dict, Any


def get_endpoint_name() -> str:
    """Get the SageMaker endpoint name from environment variable."""
    endpoint_name = os.getenv('SAGEMAKER_MODEL_ENDPOINT')
    if not endpoint_name:
        print("❌ ERROR: SAGEMAKER_MODEL_ENDPOINT environment variable is not set")
        print("   Please set it to your SageMaker agent model endpoint name")
        sys.exit(1)
    return endpoint_name


def get_aws_region() -> str:
    """Get the AWS region from environment variable."""
    return os.getenv('AWS_REGION', 'us-east-1')


def get_inference_component_name() -> str:
    """Get the inference component name from environment variable."""
    return os.getenv('SAGEMAKER_INFERENCE_COMPONENT')


def validate_agent_endpoint(endpoint_name: str, region: str, inference_component_name: str = None) -> bool:
    """
    Validate the agent model endpoint by sending a test inference request.
    
    Args:
        endpoint_name: Name of the SageMaker endpoint
        region: AWS region
        inference_component_name: Optional inference component name for multi-model endpoints
        
    Returns:
        True if validation succeeds, False otherwise
    """
    print(f"\n🔍 Validating Agent Model Endpoint: {endpoint_name}")
    print(f"   Region: {region}")
    if inference_component_name:
        print(f"   Inference Component: {inference_component_name}")
    print("-" * 60)
    
    try:
        # Create SageMaker Runtime client
        sagemaker_runtime = boto3.client(
            'sagemaker-runtime',
            region_name=region
        )
        
        # Prepare test payload
        test_prompt = "What is the capital of France?"
        payload = {
            "inputs": test_prompt,
            "parameters": {
                "max_new_tokens": 50
            }
        }
        
        print(f"\n📤 Sending test request...")
        print(f"   Prompt: {test_prompt}")
        print(f"   Max tokens: 50")
        
        # Prepare invoke_endpoint parameters
        invoke_params = {
            'EndpointName': endpoint_name,
            'Body': json.dumps(payload),
            'ContentType': 'application/json'
        }
        
        # Add inference component name if provided
        if inference_component_name:
            invoke_params['InferenceComponentName'] = inference_component_name
        
        # Invoke endpoint
        response = sagemaker_runtime.invoke_endpoint(**invoke_params)
        
        # Parse response
        result = json.loads(response['Body'].read().decode())
        
        print(f"\n✅ SUCCESS: Endpoint is responding correctly!")
        print(f"\n📥 Response:")
        print(f"   {json.dumps(result, indent=2)}")
        print(f"\n💡 Note: The response quality depends on the model type:")
        print(f"   - Base models may generate less coherent text")
        print(f"   - Instruction-tuned models will follow prompts better")
        print(f"   - The validation confirms the endpoint is operational")
        print("\n" + "=" * 60)
        print("✅ Agent model endpoint validation PASSED")
        print("=" * 60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: Error validating endpoint")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print("\n" + "=" * 60)
        print("❌ Agent model endpoint validation FAILED")
        print("=" * 60 + "\n")
        
        return False


def main():
    """Main function to run the validation."""
    print("\n" + "=" * 60)
    print("  Agent Model Endpoint Validation")
    print("=" * 60)
    
    # Get configuration from environment variables
    endpoint_name = get_endpoint_name()
    region = get_aws_region()
    inference_component_name = get_inference_component_name()
    
    # Validate the endpoint
    success = validate_agent_endpoint(endpoint_name, region, inference_component_name)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
