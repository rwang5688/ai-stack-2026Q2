#!/usr/bin/env python3
"""
SageMaker Model Endpoint Validation Script

This script validates that a SageMaker model endpoint is working correctly
by sending a test inference request and verifying the response.

Usage:
    python validate_sagemaker_endpoint.py

Environment Variables:
    TEACHERS_ASSISTANT_ENV: Environment name (dev, staging, prod) - defaults to 'dev'
    AWS_REGION: AWS region for all AWS services - defaults to 'us-east-1'
    
SSM Parameters (read from /teachers_assistant/{env}/):
    sagemaker_model_endpoint: Name of the SageMaker endpoint to validate
    sagemaker_model_inference_component: (Optional) Inference component name for multi-model endpoints
"""

import os
import sys
import json
import boto3
from typing import Dict, Any, Optional


def get_environment() -> str:
    """Get the environment name from environment variable."""
    return os.getenv('TEACHERS_ASSISTANT_ENV', 'dev')


def get_ssm_parameter(parameter_name: str, env: str, region: str, required: bool = True) -> Optional[str]:
    """
    Get a parameter value from SSM Parameter Store.
    
    Args:
        parameter_name: Name of the parameter (without path prefix)
        env: Environment name (dev, staging, prod)
        region: AWS region for SSM client
        required: Whether the parameter is required
        
    Returns:
        Parameter value or None if not found and not required
    """
    ssm = boto3.client('ssm', region_name=region)
    parameter_path = f'/teachers_assistant/{env}/{parameter_name}'
    
    try:
        response = ssm.get_parameter(Name=parameter_path)
        return response['Parameter']['Value']
    except ssm.exceptions.ParameterNotFound:
        if required:
            print(f"❌ ERROR: SSM parameter not found: {parameter_path}")
            print(f"   Please ensure the CloudFormation stack is deployed")
            sys.exit(1)
        return None
    except Exception as e:
        print(f"❌ ERROR: Failed to retrieve SSM parameter: {parameter_path}")
        print(f"   Error: {str(e)}")
        sys.exit(1)


def validate_sagemaker_endpoint(endpoint_name: str, region: str, inference_component_name: Optional[str] = None) -> bool:
    """
    Validate the SageMaker model endpoint by sending a test inference request.
    
    Args:
        endpoint_name: Name of the SageMaker endpoint
        region: AWS region
        inference_component_name: Optional inference component name for multi-model endpoints
        
    Returns:
        True if validation succeeds, False otherwise
    """
    print(f"\n🔍 Validating SageMaker Model Endpoint: {endpoint_name}")
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
        
        # Add inference component name if provided and not a placeholder
        if inference_component_name and inference_component_name != "my-sagemaker-model-inference-component":
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
        print("✅ SageMaker model endpoint validation PASSED")
        print("=" * 60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: Error validating endpoint")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print("\n" + "=" * 60)
        print("❌ SageMaker model endpoint validation FAILED")
        print("=" * 60 + "\n")
        
        return False


def main():
    """Main function to run the validation."""
    print("\n" + "=" * 60)
    print("  SageMaker Model Endpoint Validation")
    print("=" * 60)
    
    # Get environment and region from environment variables
    env = get_environment()
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    print(f"\n📋 Environment: {env}")
    print(f"   AWS Region: {region}")
    print(f"   Reading configuration from SSM Parameter Store...")
    print(f"   Parameter path: /teachers_assistant/{env}/")
    
    # Get configuration from SSM Parameter Store
    endpoint_name = get_ssm_parameter('sagemaker_model_endpoint', env, region, required=True)
    inference_component_name = get_ssm_parameter('sagemaker_model_inference_component', env, region, required=False)
    
    # Validate the endpoint
    success = validate_sagemaker_endpoint(endpoint_name, region, inference_component_name)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
