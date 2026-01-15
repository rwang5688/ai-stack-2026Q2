#!/usr/bin/env python3
"""
XGBoost Model Endpoint Validation Script

This script validates that a SageMaker XGBoost serverless endpoint is working correctly
by sending a test inference request with sample customer data and verifying the response.

Usage:
    python validate_xgboost_endpoint.py

Environment Variables:
    XGBOOST_ENDPOINT_NAME: Name of the SageMaker XGBoost endpoint to validate
    AWS_REGION: AWS region where the endpoint is deployed (default: us-east-1)
"""

import os
import sys
import boto3
from typing import Dict, Any


def get_endpoint_name() -> str:
    """Get the XGBoost endpoint name from environment variable."""
    endpoint_name = os.getenv('XGBOOST_ENDPOINT_NAME')
    if not endpoint_name:
        print("❌ ERROR: XGBOOST_ENDPOINT_NAME environment variable is not set")
        print("   Please set it to your SageMaker XGBoost endpoint name")
        sys.exit(1)
    return endpoint_name


def get_aws_region() -> str:
    """Get the AWS region from environment variable."""
    return os.getenv('AWS_REGION', 'us-east-1')


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
        
        print(f"\n📤 Sending test request...")
        print(f"   Sample customer data (59 features)")
        print(f"   Format: CSV (text/csv)")
        
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
    
    # Get configuration from environment variables
    endpoint_name = get_endpoint_name()
    region = get_aws_region()
    
    # Validate the endpoint
    success = validate_xgboost_endpoint(endpoint_name, region)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
