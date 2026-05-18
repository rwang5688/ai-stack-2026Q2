"""
Deploy a fine-tuned distilgpt2 model to a SageMaker Real-Time Inference endpoint
on a GPU instance using an explicit Deep Learning Container (DLC) image URI.

This script demonstrates deploying to a PROVISIONED GPU endpoint — in contrast to
deploy_serverless.py which deploys to a serverless CPU endpoint. The same universal
boto3 pattern is used, but here we:
  1. Use the GPU-optimized variant of the DLC image (includes CUDA)
  2. Deploy to a dedicated ml.g6.xlarge instance (NVIDIA L4, 24 GB VRAM)

Key differences from serverless:
  - GPU acceleration (faster inference)
  - No cold starts (instance is always running)
  - Charges PER HOUR while the endpoint is active (~$0.80/hr for ml.g6.xlarge)
  - ALWAYS run cleanup when done to stop charges!

Usage:
    python deploy_provisioned.py deploy     # Deploy with default model
    python deploy_provisioned.py deploy --model-id "your-org/your-model"  # Custom model
    python deploy_provisioned.py invoke     # Invoke with default prompt
    python deploy_provisioned.py invoke --prompt "Once upon a time"  # Custom prompt
    python deploy_provisioned.py cleanup    # Delete the endpoint (STOPS CHARGES)

Prerequisites:
    - pip install boto3
    - AWS credentials configured (SageMaker execution role or local credentials)
    - The model rwang5688/distilgpt2-finetuned-wikitext2 must exist on HuggingFace Hub
    - Service quota for ml.g6.xlarge endpoint instances (request increase if needed)

DLC Image Catalog:
    https://aws.github.io/deep-learning-containers/reference/available_images/

COST WARNING:
    A provisioned ml.g6.xlarge endpoint costs approximately $0.80/hour.
    Always run 'python deploy_provisioned.py cleanup' when you're done!
"""

import argparse
import json
import sys

import boto3


# --- Configuration ---
DEFAULT_EXECUTION_ROLE_ARN = None  # Set to skip auto-detection (e.g., "arn:aws:iam::123456789012:role/YourRole")
DEFAULT_MODEL_ID = "rwang5688/distilgpt2-finetuned-wikitext2"
DEFAULT_PROMPT = "A long time ago in a galaxy far, far away"
DEFAULT_REGION = "us-west-2"
ENDPOINT_NAME = "distilgpt2-finetuned-wikitext2-provisioned"

# Environment variables passed to the DLC container.
# The HuggingFace DLC uses these to know which model to download and what task to run.
HUB_CONFIG = {
    "HF_MODEL_ID": DEFAULT_MODEL_ID,
    "HF_TASK": "text-generation",
}

# --- DLC Image Configuration ---
# AWS Deep Learning Containers follow a predictable URI pattern:
#   <account_id>.dkr.ecr.<region>.amazonaws.com/<repository>:<tag>
#
# For HuggingFace PyTorch Inference (GPU variant):
#   Account ID: 763104351884 (same across all regions for DLC images)
#   Repository: huggingface-pytorch-inference
#   Tag: includes "gpu" and CUDA version for GPU-accelerated inference
#
# Compare with deploy_serverless.py which uses the CPU tag (no CUDA, smaller image).
#
# Find available images at:
#   https://aws.github.io/deep-learning-containers/reference/available_images/
#
# GPU tag (includes CUDA for GPU-accelerated inference):
# NOTE: Use a transformers version compatible with the version used during training.
# Training used transformers 5.7.0, so we use the DLC with transformers 5.5.3.
DLC_ACCOUNT_ID = "763104351884"
DLC_REPOSITORY = "huggingface-pytorch-inference"
DLC_TAG = "2.6.0-transformers5.5.3-gpu-py312-cu124-ubuntu22.04"

# --- Provisioned Endpoint Configuration ---
# ml.g6.xlarge: NVIDIA L4 GPU, 24 GB VRAM, 4 vCPUs, 16 GB RAM
# This is the same instance type used for training in Workshop 2.
DEPLOY_INSTANCE_TYPE = "ml.g6.xlarge"
INITIAL_INSTANCE_COUNT = 1


def get_region(region=None):
    """Get the AWS region.

    Resolution order:
    1. --region CLI argument (if provided)
    2. boto3 session region (from AWS_DEFAULT_REGION or AWS config)
    3. DEFAULT_REGION constant at top of script
    """
    if region:
        return region

    session = boto3.session.Session()
    session_region = session.region_name
    if session_region:
        return session_region

    return DEFAULT_REGION


def get_execution_role(role_arn=None):
    """Resolve the SageMaker execution role ARN.

    Resolution order:
    1. --role-arn CLI argument (if provided)
    2. DEFAULT_EXECUTION_ROLE_ARN constant (if set at top of script)
    3. Auto-detect from current AWS session (STS + IAM lookup)
    4. Error out with helpful message
    """
    if role_arn:
        return role_arn

    if DEFAULT_EXECUTION_ROLE_ARN:
        return DEFAULT_EXECUTION_ROLE_ARN

    # Use boto3 STS + IAM — get the role name from STS, then look up the full ARN from IAM
    try:
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        arn = identity["Arn"]
        # If the ARN is an assumed-role session, extract the role name and look it up in IAM
        # Format: arn:aws:sts::123456789012:assumed-role/RoleName/session-name
        if ":assumed-role/" in arn:
            role_name = arn.split(":assumed-role/")[1].split("/")[0]
            iam = boto3.client("iam")
            role_info = iam.get_role(RoleName=role_name)
            return role_info["Role"]["Arn"]
        # If it's already a role ARN, return as-is
        if ":role/" in arn:
            return arn
    except Exception:
        pass

    print("ERROR: Could not resolve SageMaker execution role ARN.")
    print("Provide it via --role-arn, or set DEFAULT_EXECUTION_ROLE_ARN at the top of this script.")
    print('  Example: --role-arn "arn:aws:iam::123456789012:role/YourRole"')
    sys.exit(1)


def get_dlc_image_uri(region):
    """
    Construct the GPU-optimized DLC image URI for the given region.

    This uses the SAME URI pattern as deploy_serverless.py, but with the GPU tag.
    The GPU image includes CUDA libraries for GPU-accelerated inference.
    The CPU image (used by serverless) does not include CUDA — smaller image, CPU-only.

    URI pattern: <account_id>.dkr.ecr.<region>.amazonaws.com/<repository>:<tag>

    To use a DIFFERENT DLC, just change DLC_REPOSITORY and DLC_TAG:
      - PyTorch inference (GPU): "pytorch-inference" + "2.1.0-gpu-py310-cu118-ubuntu20.04"
      - TensorFlow inference:    "tensorflow-inference" + "2.14.0-gpu-py310-cu121-ubuntu22.04"

    Args:
        region: AWS region (e.g., "us-west-2")

    Returns:
        The fully qualified ECR image URI for the GPU-optimized DLC
    """
    return f"{DLC_ACCOUNT_ID}.dkr.ecr.{region}.amazonaws.com/{DLC_REPOSITORY}:{DLC_TAG}"


def deploy(model_id, role_arn, region):
    """Deploy the model to a provisioned GPU endpoint (ml.g6.xlarge)."""
    region = get_region(region)
    role = get_execution_role(role_arn)
    sm_client = boto3.client("sagemaker", region_name=region)

    print(f"Region:             {region}")
    print(f"SageMaker role ARN: {role}")

    # Step 1: Construct the GPU-optimized DLC image URI
    # Note: This uses a DIFFERENT tag than deploy_serverless.py — the GPU tag includes
    # CUDA libraries for GPU-accelerated inference.
    image_uri = get_dlc_image_uri(region)
    print(f"\nDLC Image URI (GPU): {image_uri}")

    # Step 2: Create a SageMaker Model
    hub_config = {
        "HF_MODEL_ID": model_id,
        "HF_TASK": "text-generation",
    }
    model_name = f"{ENDPOINT_NAME}-model"
    print(f"\nCreating Model '{model_name}' with config: {json.dumps(hub_config, indent=2)}")

    try:
        sm_client.create_model(
            ModelName=model_name,
            PrimaryContainer={
                "Image": image_uri,
                "Environment": hub_config,
            },
            ExecutionRoleArn=role,
        )
    except sm_client.exceptions.ClientError as e:
        if "Cannot create already existing model" in str(e):
            print(f"  Model '{model_name}' already exists, reusing it.")
        else:
            raise

    # Step 3: Create endpoint configuration with provisioned instance
    config_name = f"{ENDPOINT_NAME}-config"
    print(f"\nCreating endpoint config: {config_name}")
    print(f"  Instance type:    {DEPLOY_INSTANCE_TYPE} (NVIDIA L4, 24 GB VRAM)")
    print(f"  Instance count:   {INITIAL_INSTANCE_COUNT}")

    try:
        sm_client.create_endpoint_config(
            EndpointConfigName=config_name,
            ProductionVariants=[
                {
                    "VariantName": "AllTraffic",
                    "ModelName": model_name,
                    "InstanceType": DEPLOY_INSTANCE_TYPE,
                    "InitialInstanceCount": INITIAL_INSTANCE_COUNT,
                }
            ],
        )
    except sm_client.exceptions.ClientError as e:
        if "Cannot create already existing" in str(e):
            print(f"  Config '{config_name}' already exists, reusing it.")
        else:
            raise

    # Step 4: Create the endpoint
    print(f"\nDeploying provisioned endpoint: {ENDPOINT_NAME}")
    print("  This may take 5-10 minutes...\n")
    print("  ** COST WARNING: This endpoint charges ~$0.80/hour while running.")
    print("  ** Run 'python deploy_provisioned.py cleanup' when done!\n")

    try:
        sm_client.create_endpoint(
            EndpointName=ENDPOINT_NAME,
            EndpointConfigName=config_name,
        )
    except sm_client.exceptions.ClientError as e:
        if "Cannot create already existing" in str(e):
            print(f"  Endpoint '{ENDPOINT_NAME}' already exists.")
            return
        else:
            raise

    # Wait for endpoint to be in service
    print("  Waiting for endpoint to be InService...")
    waiter = sm_client.get_waiter("endpoint_in_service")
    waiter.wait(EndpointName=ENDPOINT_NAME)

    print(f"\nEndpoint '{ENDPOINT_NAME}' is now InService.")
    print("Run: python deploy_provisioned.py invoke")
    print("\n** Remember: Run 'python deploy_provisioned.py cleanup' when done to stop charges!")


def invoke(prompt, region):
    """Send a text-generation request to the provisioned endpoint."""
    region = get_region(region)
    print(f"Invoking endpoint: {ENDPOINT_NAME}")
    print("  (No cold start — GPU instance is always running)\n")

    runtime = boto3.client("sagemaker-runtime", region_name=region)

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0.7,
            "do_sample": True,
        },
    }

    print(f"Prompt: {payload['inputs']}")
    print("---")

    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        Body=json.dumps(payload),
    )

    result = json.loads(response["Body"].read().decode("utf-8"))
    print(f"Response:\n{json.dumps(result, indent=2)}")


def cleanup(region):
    """Delete the provisioned endpoint and its model. STOPS HOURLY CHARGES."""
    region = get_region(region)
    print(f"Cleaning up endpoint: {ENDPOINT_NAME}")
    print("  (This will stop the hourly GPU instance charges)\n")

    sm_client = boto3.client("sagemaker", region_name=region)

    # Get the endpoint config and model name before deleting
    try:
        endpoint_desc = sm_client.describe_endpoint(EndpointName=ENDPOINT_NAME)
        config_name = endpoint_desc["EndpointConfigName"]
    except sm_client.exceptions.ClientError:
        print(f"Endpoint '{ENDPOINT_NAME}' not found. Nothing to clean up.")
        return

    # Get model name from endpoint config
    config_desc = sm_client.describe_endpoint_config(EndpointConfigName=config_name)
    model_name = config_desc["ProductionVariants"][0]["ModelName"]

    # Delete in order: endpoint -> endpoint config -> model
    print(f"  Deleting endpoint:        {ENDPOINT_NAME}")
    sm_client.delete_endpoint(EndpointName=ENDPOINT_NAME)

    print(f"  Deleting endpoint config: {config_name}")
    sm_client.delete_endpoint_config(EndpointConfigName=config_name)

    print(f"  Deleting model:           {model_name}")
    sm_client.delete_model(ModelName=model_name)

    print("\nCleanup complete. GPU instance charges have stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="Deploy/invoke/cleanup a SageMaker Provisioned GPU Inference endpoint"
    )
    parser.add_argument(
        "action",
        choices=["deploy", "invoke", "cleanup"],
        help="Action to perform",
    )
    parser.add_argument(
        "--region",
        default=None,
        help=f"AWS region (default: from AWS config, or '{DEFAULT_REGION}')",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help=f"Text prompt for the invoke action (default: '{DEFAULT_PROMPT}')",
    )
    parser.add_argument(
        "--model-id",
        default=DEFAULT_MODEL_ID,
        help=f"HuggingFace model ID for the deploy action (default: '{DEFAULT_MODEL_ID}')",
    )
    parser.add_argument(
        "--role-arn",
        default=None,
        help="SageMaker execution role ARN for the deploy action (default: auto-detect)",
    )
    args = parser.parse_args()

    if args.action == "invoke":
        invoke(args.prompt, args.region)
    elif args.action == "deploy":
        deploy(args.model_id, args.role_arn, args.region)
    elif args.action == "cleanup":
        cleanup(args.region)


if __name__ == "__main__":
    main()
