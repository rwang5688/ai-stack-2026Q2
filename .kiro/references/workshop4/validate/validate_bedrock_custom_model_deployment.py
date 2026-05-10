#!/usr/bin/env python3
"""
Bedrock Custom Model Deployment Validation Script

This script validates that a Bedrock Custom Model Deployment is working correctly
by sending a test inference request and verifying the response.

Usage:
    python validate_bedrock_custom_model_deployment.py

Environment Variables:
    TEACHERS_ASSISTANT_ENV: Environment name (dev, staging, prod) - defaults to 'dev'
    AWS_REGION: AWS region for all AWS services - defaults to 'us-east-1'
    
SSM Parameters (read from /teachers_assistant/{env}/):
    bedrock_custom_model_deployment_arn: ARN of the Bedrock custom model deployment to validate
"""

import os
import sys
import json
import boto3
from typing import Optional


def get_environment() -> str:
    """Get the environment name from environment variable."""
    return os.getenv('TEACHERS_ASSISTANT_ENV', 'dev')


def get_region() -> str:
    """Get the AWS region from environment variable."""
    return os.getenv('AWS_REGION', 'us-east-1')


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


def validate_bedrock_custom_model_deployment(custom_model_arn: str, region: str) -> bool:
    """
    Validate the Bedrock Custom Model Deployment by sending a test inference request.
    
    Args:
        custom_model_arn: ARN of the Bedrock custom model deployment
        region: AWS region
        
    Returns:
        True if validation succeeds, False otherwise
    """
    print(f"\n🔍 Validating Bedrock Custom Model Deployment")
    print(f"   ARN: {custom_model_arn}")
    print(f"   Region: {region}")
    print("-" * 70)
    
    # Check if ARN is placeholder value
    if custom_model_arn == 'my-bedrock-custom-model-deployment-arn':
        print(f"\n⚠️  SKIPPED: Custom model deployment ARN is placeholder value")
        print(f"   The parameter 'bedrock_custom_model_deployment_arn' has not been updated")
        print(f"   with an actual Bedrock custom model deployment ARN.")
        print(f"\n💡 To validate a custom model deployment:")
        print(f"   1. Deploy a custom model in Amazon Bedrock")
        print(f"   2. Update the SSM parameter with the deployment ARN:")
        print(f"      aws ssm put-parameter \\")
        print(f"        --name '/teachers_assistant/{get_environment()}/bedrock_custom_model_deployment_arn' \\")
        print(f"        --value 'arn:aws:bedrock:REGION:ACCOUNT:custom-model-deployment/ID' \\")
        print(f"        --overwrite")
        print(f"   3. Run this validation script again")
        print("\n" + "=" * 70)
        print("⚠️  Bedrock custom model deployment validation SKIPPED")
        print("=" * 70 + "\n")
        return True  # Return True since this is expected for placeholder
    
    try:
        # Create Bedrock Runtime client
        bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=region
        )
        
        # Prepare test prompt
        test_prompt = "What is the capital of France?"
        
        print(f"\n📤 Sending test request...")
        print(f"   Prompt: {test_prompt}")
        print(f"   Max tokens: 50")
        
        # Prepare request body (using Converse API format)
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": test_prompt}]
                }
            ],
            "inferenceConfig": {
                "temperature": 0.3,
                "maxTokens": 50
            }
        }
        
        # Invoke model using Converse API
        response = bedrock_runtime.converse(
            modelId=custom_model_arn,
            messages=request_body["messages"],
            inferenceConfig=request_body["inferenceConfig"]
        )
        
        # Extract response text
        response_text = response['output']['message']['content'][0]['text']
        
        print(f"\n✅ SUCCESS: Custom model deployment is responding correctly!")
        print(f"\n📥 Response:")
        print(f"   {response_text}")
        print(f"\n💡 Note: The response quality depends on the custom model:")
        print(f"   - Base models may generate less coherent text")
        print(f"   - Fine-tuned models will reflect their training data")
        print(f"   - The validation confirms the deployment is operational")
        print("\n" + "=" * 70)
        print("✅ Bedrock custom model deployment validation PASSED")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: Error validating custom model deployment")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"\n💡 Common issues:")
        print(f"   - ARN format invalid: Ensure ARN follows pattern")
        print(f"     arn:aws:bedrock:REGION:ACCOUNT:custom-model-deployment/ID")
        print(f"   - Model not found: Verify deployment exists in Bedrock")
        print(f"   - Access denied: Check IAM permissions for bedrock:InvokeModel")
        print(f"   - Region mismatch: Ensure ARN region matches AWS_REGION")
        print("\n" + "=" * 70)
        print("❌ Bedrock custom model deployment validation FAILED")
        print("=" * 70 + "\n")
        
        return False


def main():
    """Main function to run the validation."""
    print("\n" + "=" * 70)
    print("  Bedrock Custom Model Deployment Validation")
    print("=" * 70)
    
    # Get environment and region from environment variables
    env = get_environment()
    region = get_region()
    
    print(f"\n📋 Configuration:")
    print(f"   Environment: {env}")
    print(f"   AWS Region: {region}")
    print(f"   Reading configuration from SSM Parameter Store...")
    print(f"   Parameter path: /teachers_assistant/{env}/")
    
    # Validate environment variables
    if not env:
        print("\n❌ ERROR: TEACHERS_ASSISTANT_ENV environment variable not set")
        print("   Set it with: export TEACHERS_ASSISTANT_ENV=dev")
        sys.exit(1)
    
    if not region:
        print("\n❌ ERROR: AWS_REGION environment variable not set")
        print("   Set it with: export AWS_REGION=us-east-1")
        sys.exit(1)
    
    # Get configuration from SSM Parameter Store
    custom_model_arn = get_ssm_parameter('bedrock_custom_model_deployment_arn', env, region, required=True)
    
    # Validate the custom model deployment
    success = validate_bedrock_custom_model_deployment(custom_model_arn, region)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
