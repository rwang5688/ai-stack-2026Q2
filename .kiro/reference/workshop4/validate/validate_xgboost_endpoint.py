#!/usr/bin/env python3
"""
XGBoost Model Endpoint Validation Script

This script validates that a SageMaker XGBoost serverless endpoint is working correctly
by sending a test inference request with sample customer data and verifying the response.

Usage:
    python validate_xgboost_endpoint.py

Environment Variables:
    TEACHERS_ASSISTANT_ENV: Environment name (dev, staging, prod) - defaults to 'dev'
    AWS_REGION: AWS region for all AWS services - defaults to 'us-east-1'
    
SSM Parameters (read from /teachers_assistant/{env}/):
    xgboost_model_endpoint: Name of the SageMaker XGBoost endpoint to validate
"""

import os
import sys
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


def validate_xgboost_endpoint(endpoint_name: str, region: str) -> bool:
    """
    Validate the XGBoost model endpoint by sending a test inference request.
    
    Args:
        endpoint_name: Name of the SageMaker endpoint
        region: AWS region
        
    Returns:
        True if validation succeeds, False otherwise
    """
    print(f"\n🔍 Validating XGBoost Model Endpoint: {endpoint_name}")
    print(f"   Region: {region}")
    print("-" * 60)
    
    try:
        # Create SageMaker Runtime client
        runtime = boto3.client(
            service_name='sagemaker-runtime',
            region_name=region
        )
        
        # Sample customer data from the Direct Marketing dataset
        # This is a CSV row with 59 features (one-hot encoded)
        # Format: age, campaign, pdays, previous, + one-hot encoded categorical features
        sample_payload = "29,2,999,0,1,0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0"
        
        # Parse features for display
        features = sample_payload.split(',')
        feature_count = len(features)
        
        print(f"\n📤 Sending test request...")
        print(f"   Sample customer data ({feature_count} features)")
        print(f"   Format: CSV (text/csv)")
        print(f"\n   Feature values:")
        print(f"   {sample_payload}")
        print(f"\n   First 10 features: {', '.join(features[:10])}")
        print(f"   Last 10 features: {', '.join(features[-10:])}")
        
        # Invoke endpoint
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            Body=sample_payload,
            ContentType="text/csv"
        )
        
        # Parse response
        result = response['Body'].read().decode()
        
        # Try to parse as float (prediction score)
        try:
            prediction = float(result.strip())
            prediction_label = "Accept" if prediction >= 0.5 else "Reject"
            
            print(f"\n✅ SUCCESS: Endpoint is responding correctly!")
            print(f"\n📥 Response:")
            print(f"   Raw prediction: {prediction}")
            print(f"   Prediction label: {prediction_label}")
            print(f"   Confidence: {prediction * 100:.2f}%")
            
        except ValueError:
            # If not a float, just print the raw response
            print(f"\n✅ SUCCESS: Endpoint is responding!")
            print(f"\n📥 Response:")
            print(f"   {result}")
        
        print("\n" + "=" * 60)
        print("✅ XGBoost model endpoint validation PASSED")
        print("=" * 60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: Error validating endpoint")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print("\n" + "=" * 60)
        print("❌ XGBoost model endpoint validation FAILED")
        print("=" * 60 + "\n")
        
        return False


def main():
    """Main function to run the validation."""
    print("\n" + "=" * 60)
    print("  XGBoost Model Endpoint Validation")
    print("=" * 60)
    
    # Get environment and region from environment variables
    env = get_environment()
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    print(f"\n📋 Environment: {env}")
    print(f"   AWS Region: {region}")
    print(f"   Reading configuration from SSM Parameter Store...")
    print(f"   Parameter path: /teachers_assistant/{env}/")
    
    # Get configuration from SSM Parameter Store
    endpoint_name = get_ssm_parameter('xgboost_model_endpoint', env, region, required=True)
    
    # Validate the endpoint
    success = validate_xgboost_endpoint(endpoint_name, region)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
