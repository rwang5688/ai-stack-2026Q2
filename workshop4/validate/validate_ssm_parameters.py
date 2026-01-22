#!/usr/bin/env python3
"""
SSM Parameter Store Validation Script

This script validates that all required SSM parameters are accessible and
displays their current values. This is a prerequisite check before running
the multi-agent application.

Usage:
    python validate_ssm_parameters.py

Environment Variables:
    TEACHERS_ASSISTANT_ENV: Environment name (dev, staging, prod) - defaults to 'dev'
    AWS_REGION: AWS region for all AWS services - defaults to 'us-east-1'
"""

import os
import sys
import boto3
from typing import Dict, List, Tuple


def get_environment() -> str:
    """Get the environment name from environment variable."""
    return os.getenv('TEACHERS_ASSISTANT_ENV', 'dev')


def get_region() -> str:
    """Get the AWS region from environment variable."""
    return os.getenv('AWS_REGION', 'us-east-1')


def validate_ssm_parameters() -> Tuple[bool, Dict[str, str], List[str]]:
    """
    Validate that all required SSM parameters exist and are accessible.
    
    Returns:
        Tuple of (success, parameters_dict, missing_parameters_list)
    """
    env = get_environment()
    region = get_region()
    
    print("\n" + "=" * 70)
    print("  SSM Parameter Store Validation")
    print("=" * 70)
    print(f"\n📋 Configuration:")
    print(f"   Environment: {env}")
    print(f"   AWS Region: {region}")
    print(f"   Parameter Path: /teachers_assistant/{env}/")
    print("-" * 70)
    
    # Expected parameters
    expected_parameters = [
        'default_model_id',
        'max_results',
        'min_score',
        'sagemaker_model_endpoint',
        'sagemaker_model_inference_component',
        'strands_knowledge_base_id',
        'temperature',
        'xgboost_model_endpoint'
    ]
    
    try:
        # Create SSM client
        ssm = boto3.client('ssm', region_name=region)
        parameter_path = f'/teachers_assistant/{env}'
        
        print(f"\n🔍 Fetching parameters from SSM Parameter Store...")
        
        # Fetch all parameters
        response = ssm.get_parameters_by_path(
            Path=parameter_path,
            Recursive=True,
            WithDecryption=True
        )
        
        # Build dictionary of parameter name -> value
        found_parameters = {}
        for param in response['Parameters']:
            # Extract parameter name (last part of path)
            name = param['Name'].replace(f'{parameter_path}/', '')
            found_parameters[name] = param['Value']
        
        # Check for missing parameters
        missing_parameters = []
        for param_name in expected_parameters:
            if param_name not in found_parameters:
                missing_parameters.append(param_name)
        
        # Display results
        print(f"\n📊 Validation Results:")
        print(f"   Expected parameters: {len(expected_parameters)}")
        print(f"   Found parameters: {len(found_parameters)}")
        print(f"   Missing parameters: {len(missing_parameters)}")
        
        if missing_parameters:
            print(f"\n❌ MISSING PARAMETERS:")
            for param_name in missing_parameters:
                print(f"   - {param_name}")
            print(f"\n💡 To fix: Deploy CloudFormation stack or create missing parameters")
            return False, found_parameters, missing_parameters
        
        # Display all parameters
        print(f"\n✅ ALL PARAMETERS FOUND:")
        print("-" * 70)
        
        # Sort parameters alphabetically for display
        for param_name in sorted(found_parameters.keys()):
            value = found_parameters[param_name]
            
            # Highlight placeholder values that need updating
            if value in ['my-sagemaker-model-endpoint', 'my-sagemaker-model-inference-component',
                        'my-strands-knowledge-base-id', 'my-xgboost-model-endpoint']:
                display_value = f"{value} ⚠️  (placeholder - needs update)"
            else:
                display_value = value
            
            print(f"   {param_name:40} = {display_value}")
        
        print("-" * 70)
        
        # Check for placeholder values (exact matches only, not real endpoint names)
        placeholder_values = [
            'my-sagemaker-model-endpoint',
            'my-sagemaker-model-inference-component',
            'my-strands-knowledge-base-id',
            'my-xgboost-model-endpoint'
        ]
        placeholder_params = [name for name, value in found_parameters.items() 
                            if value in placeholder_values]
        
        if placeholder_params:
            print(f"\n⚠️  WARNING: {len(placeholder_params)} parameter(s) still have placeholder values:")
            for param_name in placeholder_params:
                print(f"   - {param_name}")
            print(f"\n💡 Update these parameters with your actual AWS resource names:")
            print(f"   1. Via AWS Console: Systems Manager → Parameter Store")
            print(f"   2. Via AWS CLI: aws ssm put-parameter --name <path> --value <value> --overwrite")
        
        print("\n" + "=" * 70)
        print("✅ SSM Parameter Store validation PASSED")
        print("=" * 70 + "\n")
        
        return True, found_parameters, []
        
    except ssm.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        print(f"\n❌ FAILED: AWS API Error")
        print(f"   Error Code: {error_code}")
        print(f"   Error Message: {error_message}")
        
        if error_code == 'AccessDeniedException':
            print(f"\n💡 Fix: Ensure your IAM role/user has these permissions:")
            print(f"   - ssm:GetParameter")
            print(f"   - ssm:GetParameters")
            print(f"   - ssm:GetParametersByPath")
            print(f"   Resource: arn:aws:ssm:*:*:parameter/teachers_assistant/*")
        
        print("\n" + "=" * 70)
        print("❌ SSM Parameter Store validation FAILED")
        print("=" * 70 + "\n")
        
        return False, {}, expected_parameters
        
    except Exception as e:
        print(f"\n❌ FAILED: Unexpected error")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        
        print("\n" + "=" * 70)
        print("❌ SSM Parameter Store validation FAILED")
        print("=" * 70 + "\n")
        
        return False, {}, expected_parameters


def main():
    """Main function to run the validation."""
    # Validate environment variables
    env = get_environment()
    region = get_region()
    
    if not env:
        print("❌ ERROR: TEACHERS_ASSISTANT_ENV environment variable not set")
        print("   Set it with: export TEACHERS_ASSISTANT_ENV=dev")
        sys.exit(1)
    
    if not region:
        print("❌ ERROR: AWS_REGION environment variable not set")
        print("   Set it with: export AWS_REGION=us-east-1")
        sys.exit(1)
    
    # Run validation
    success, parameters, missing = validate_ssm_parameters()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
