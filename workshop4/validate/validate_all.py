#!/usr/bin/env python3
"""
Comprehensive Validation Script

This script runs all validation checks in sequence to verify that the
multi-agent application environment is properly configured.

Usage:
    python validate_all.py

Environment Variables:
    TEACHERS_ASSISTANT_ENV: Environment name (dev, staging, prod) - defaults to 'dev'
    AWS_REGION: AWS region for all AWS services - defaults to 'us-east-1'
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_separator():
    """Print a separator line."""
    print("\n" + "-" * 70 + "\n")


def run_validation_script(script_name: str, description: str) -> bool:
    """
    Run a validation script and return success status.
    
    Args:
        script_name: Name of the validation script to run
        description: Human-readable description of what's being validated
        
    Returns:
        True if validation passed, False otherwise
    """
    print_header(description)
    
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"❌ ERROR: Validation script not found: {script_path}")
        return False
    
    try:
        # Run the validation script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ ERROR: Failed to run validation script")
        print(f"   Error: {str(e)}")
        return False


def main():
    """Main function to run all validation checks."""
    print_header("Comprehensive Validation - Multi-Agent Application")
    
    # Check environment variables
    env = os.getenv('TEACHERS_ASSISTANT_ENV', 'dev')
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    print(f"📋 Configuration:")
    print(f"   Environment: {env}")
    print(f"   AWS Region: {region}")
    print(f"   Python: {sys.executable}")
    
    if not env:
        print("\n❌ ERROR: TEACHERS_ASSISTANT_ENV environment variable not set")
        print("   Set it with: export TEACHERS_ASSISTANT_ENV=dev")
        sys.exit(1)
    
    if not region:
        print("\n❌ ERROR: AWS_REGION environment variable not set")
        print("   Set it with: export AWS_REGION=us-east-1")
        sys.exit(1)
    
    print_separator()
    
    # Track validation results
    validations = []
    
    # Validation 1: SSM Parameter Store
    print("🔍 Running Validation 1 of 4...")
    ssm_passed = run_validation_script(
        "validate_ssm_parameters.py",
        "Validation 1: SSM Parameter Store"
    )
    validations.append(("SSM Parameter Store", ssm_passed))
    
    print_separator()
    
    # Validation 2: Bedrock Custom Model Deployment
    print("🔍 Running Validation 2 of 4...")
    bedrock_custom_passed = run_validation_script(
        "validate_bedrock_custom_model_deployment.py",
        "Validation 2: Bedrock Custom Model Deployment"
    )
    validations.append(("Bedrock Custom Model Deployment", bedrock_custom_passed))
    
    print_separator()
    
    # Validation 3: SageMaker Model Endpoint
    print("🔍 Running Validation 3 of 4...")
    sagemaker_passed = run_validation_script(
        "validate_sagemaker_endpoint.py",
        "Validation 3: SageMaker Model Endpoint"
    )
    validations.append(("SageMaker Model Endpoint", sagemaker_passed))
    
    print_separator()
    
    # Validation 4: XGBoost Model Endpoint
    print("🔍 Running Validation 4 of 4...")
    xgboost_passed = run_validation_script(
        "validate_xgboost_endpoint.py",
        "Validation 4: XGBoost Model Endpoint"
    )
    validations.append(("XGBoost Model Endpoint", xgboost_passed))
    
    # Print summary
    print_header("Validation Summary")
    
    all_passed = True
    for name, passed in validations:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {name:40} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED")
        print("=" * 70)
        print("\n🎉 Your environment is ready for the multi-agent application!")
        print("\nNext Steps:")
        print("   1. Review PART-2-MULTI-AGENT.md for local development")
        print("   2. Run: cd ../multi_agent && streamlit run app.py")
        print("   3. Test model selection and agent features")
        print("\n")
        sys.exit(0)
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("=" * 70)
        print("\n⚠️  Please fix the failed validations before proceeding.")
        print("\nCommon Issues:")
        print("   - SSM parameters not deployed: Deploy CloudFormation template")
        print("   - Placeholder values: Update SSM parameters with actual resource names")
        print("   - Endpoint not found: Verify endpoint exists and name is correct")
        print("   - Access denied: Check IAM permissions for SSM and SageMaker")
        print("\nFor detailed troubleshooting, see workshop4/GETTING-STARTED.md")
        print("\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
