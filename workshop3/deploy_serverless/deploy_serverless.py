"""
Deploy a fine-tuned distilgpt2 model to a SageMaker Serverless Inference endpoint
using an explicit Deep Learning Container (DLC) image URI.

This script demonstrates the UNIVERSAL pattern for deploying ANY model with ANY
available AWS Deep Learning Container using boto3 directly. No framework-specific
SDK wrappers needed — just the raw AWS API.

This approach teaches you how to:
1. Find DLC image URIs from the AWS DLC catalog
2. Construct the full ECR image URI for your region
3. Create a SageMaker Model with any DLC image via the CreateModel API
4. Deploy to a serverless endpoint for cost-effective inference

The same pattern works with PyTorch DLCs, TensorFlow DLCs, or any custom container
— just change the repository name and tag.

Usage:
    python deploy_serverless.py deploy     # Deploy with default model
    python deploy_serverless.py deploy --model-id "your-org/your-model"  # Custom model
    python deploy_serverless.py invoke     # Invoke with default prompt
    python deploy_serverless.py invoke --prompt "Once upon a time"  # Custom prompt
    python deploy_serverless.py cleanup    # Delete the endpoint and model

Prerequisites:
    - pip install boto3
    - AWS credentials configured (SageMaker execution role or local credentials)
    - The model rwang5688/distilgpt2-finetuned-wikitext2 must exist on HuggingFace Hub

DLC Image Catalog:
    https://aws.github.io/deep-learning-containers/reference/available_images/
"""

import argparse
import json
import sys
import time

import boto3


# --- Configuration ---
DEFAULT_EXECUTION_ROLE_ARN = None  # Set to skip auto-detection (e.g., "arn:aws:iam::123456789012:role/YourRole")
DEFAULT_MODEL_ID = "rwang5688/distilgpt2-finetuned-wikitext2"
DEFAULT_PROMPT = "A long time ago in a galaxy far, far away"
DEFAULT_REGION = "us-west-2"
ENDPOINT_NAME = "distilgpt2-finetuned-wikitext2-serverless"

# Environment variables passed to the DLC container.
# The HuggingFace DLC uses these to know which model to download and what task to run.
# This same env-var pattern works with any DLC that supports environment-based configuration.
HUB_CONFIG = {
    "HF_MODEL_ID": DEFAULT_MODEL_ID,
    "HF_TASK": "text-generation",
}

# --- DLC Image Configuration ---
# AWS Deep Learning Containers follow a predictable URI pattern:
#   <account_id>.dkr.ecr.<region>.amazonaws.com/<repository>:<tag>
#
# For HuggingFace PyTorch Inference:
#   Account ID: 763104351884 (same across all regions for DLC images)
#   Repository: huggingface-pytorch-inference
#   Tag format: <pytorch_version>-transformers<transformers_version>-<cpu|gpu>-<py_version>-<os>
#
# Find available images at:
#   https://aws.github.io/deep-learning-containers/reference/available_images/
#
# CPU tag for serverless — uses transformers 4.49.0 which can load safetensors
# models saved by transformers 5.x. The GPU images with transformers 5.x are too
# large (>10 GB) for the serverless container size limit.
DLC_ACCOUNT_ID = "763104351884"
DLC_REPOSITORY = "huggingface-pytorch-inference"
DLC_TAG = "2.6.0-transformers4.49.0-cpu-py312-ubuntu22.04"

# Serverless config
MEMORY_SIZE_IN_MB = 4096
MAX_CONCURRENCY = 5


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
    Construct the DLC image URI for the given region.

    AWS DLC images use a consistent URI pattern across all regions:
      <account_id>.dkr.ecr.<region>.amazonaws.com/<repository>:<tag>

    The account ID (763104351884) is the same for all AWS DLC images in all regions.
    The repository name identifies the framework (e.g., huggingface-pytorch-inference).
    The tag specifies the exact versions (PyTorch, Transformers, CPU/GPU, Python, OS).

    To use a DIFFERENT DLC, just change DLC_REPOSITORY and DLC_TAG:
      - PyTorch inference:    "pytorch-inference" + "2.1.0-cpu-py310-ubuntu22.04"
      - TensorFlow inference: "tensorflow-inference" + "2.14.0-cpu-py310-ubuntu22.04"
      - HuggingFace (GPU):   "huggingface-pytorch-inference" + "2.1.0-transformers4.37.0-gpu-py310-cu118-ubuntu20.04"

    Args:
        region: AWS region (e.g., "us-west-2")

    Returns:
        The fully qualified ECR image URI
    """
    return f"{DLC_ACCOUNT_ID}.dkr.ecr.{region}.amazonaws.com/{DLC_REPOSITORY}:{DLC_TAG}"


def deploy(model_id, role_arn, region):
    """Deploy the model to a SageMaker Serverless Inference endpoint."""
    region = get_region(region)
    role = get_execution_role(role_arn)
    sm_client = boto3.client("sagemaker", region_name=region)

    print(f"Region:             {region}")
    print(f"SageMaker role ARN: {role}")

    # Step 1: Construct the DLC image URI
    image_uri = get_dlc_image_uri(region)
    print(f"\nDLC Image URI: {image_uri}")

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

    # Step 3: Create endpoint configuration with serverless settings
    config_name = f"{ENDPOINT_NAME}-config"
    print(f"\nCreating endpoint config: {config_name}")
    print(f"  Memory:          {MEMORY_SIZE_IN_MB} MB")
    print(f"  Max concurrency: {MAX_CONCURRENCY}")

    try:
        sm_client.create_endpoint_config(
            EndpointConfigName=config_name,
            ProductionVariants=[
                {
                    "VariantName": "AllTraffic",
                    "ModelName": model_name,
                    "ServerlessConfig": {
                        "MemorySizeInMB": MEMORY_SIZE_IN_MB,
                        "MaxConcurrency": MAX_CONCURRENCY,
                    },
                }
            ],
        )
    except sm_client.exceptions.ClientError as e:
        if "Cannot create already existing" in str(e):
            print(f"  Config '{config_name}' already exists, reusing it.")
        else:
            raise

    # Step 4: Create the endpoint
    print(f"\nDeploying serverless endpoint: {ENDPOINT_NAME}")
    print("  This may take 2-5 minutes...\n")

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
    print("Run: python deploy_serverless.py invoke")


def invoke(prompt, region):
    """Send a text-generation request to the serverless endpoint."""
    region = get_region(region)
    print(f"Invoking endpoint: {ENDPOINT_NAME}")
    print("  (First request may have a cold start of 30-60 seconds)\n")

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
    """Delete the serverless endpoint and its model."""
    region = get_region(region)
    print(f"Cleaning up endpoint: {ENDPOINT_NAME}")

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

    print("\nCleanup complete. No more charges for this endpoint.")


def main():
    parser = argparse.ArgumentParser(
        description="Deploy/invoke/cleanup a SageMaker Serverless Inference endpoint"
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
