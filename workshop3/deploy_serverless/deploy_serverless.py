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
    python deploy_serverless.py deploy     # Deploy the model
    python deploy_serverless.py invoke     # Send a test request
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
ENDPOINT_NAME = "distilgpt2-finetuned-wikitext2-serverless"

# Environment variables passed to the DLC container.
# The HuggingFace DLC uses these to know which model to download and what task to run.
# This same env-var pattern works with any DLC that supports environment-based configuration.
HUB_CONFIG = {
    "HF_MODEL_ID": "rwang5688/distilgpt2-finetuned-wikitext2",
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
# GPU-variant tag used for serverless too — the GPU image works on CPU infrastructure,
# it just has extra CUDA libraries. We use it because there's no CPU image with
# transformers 5.x, and our model was trained with transformers 5.7.0.
DLC_ACCOUNT_ID = "763104351884"
DLC_REPOSITORY = "huggingface-pytorch-inference"
DLC_TAG = "2.6.0-transformers5.5.3-gpu-py312-cu124-ubuntu22.04"

# Serverless config
MEMORY_SIZE_IN_MB = 4096
MAX_CONCURRENCY = 5

# SageMaker execution role ARN.
# If running in SageMaker, this is auto-detected. If running locally, set it here.
# Example: "arn:aws:iam::123456789012:role/YourSageMakerExecutionRole"
EXECUTION_ROLE_ARN = None


def get_region():
    """Get the current AWS region from the boto3 session."""
    session = boto3.session.Session()
    region = session.region_name
    if not region:
        print("ERROR: No AWS region configured. Set AWS_DEFAULT_REGION or configure your AWS CLI.")
        sys.exit(1)
    return region


def get_execution_role():
    """Resolve the SageMaker execution role ARN.

    Resolution order:
    1. EXECUTION_ROLE_ARN constant (if set manually)
    2. boto3 IAM — look up the role from the assumed-role session to get the full ARN with path
    """
    if EXECUTION_ROLE_ARN:
        return EXECUTION_ROLE_ARN

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

    print("ERROR: EXECUTION_ROLE_ARN is not set and could not be auto-detected.")
    print("Edit deploy_serverless.py and set EXECUTION_ROLE_ARN to your")
    print("SageMaker execution role ARN, e.g.:")
    print('  EXECUTION_ROLE_ARN = "arn:aws:iam::123456789012:role/YourRole"')
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


def deploy():
    """Deploy the model to a SageMaker Serverless Inference endpoint."""
    region = get_region()
    role = get_execution_role()
    sm_client = boto3.client("sagemaker", region_name=region)

    print(f"Region:             {region}")
    print(f"SageMaker role ARN: {role}")

    # Step 1: Construct the DLC image URI
    image_uri = get_dlc_image_uri(region)
    print(f"\nDLC Image URI: {image_uri}")

    # Step 2: Create a SageMaker Model
    model_name = f"{ENDPOINT_NAME}-model"
    print(f"\nCreating Model '{model_name}' with config: {json.dumps(HUB_CONFIG, indent=2)}")

    try:
        sm_client.create_model(
            ModelName=model_name,
            PrimaryContainer={
                "Image": image_uri,
                "Environment": HUB_CONFIG,
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


def invoke():
    """Send a test text-generation request to the serverless endpoint."""
    print(f"Invoking endpoint: {ENDPOINT_NAME}")
    print("  (First request may have a cold start of 30-60 seconds)\n")

    runtime = boto3.client("sagemaker-runtime")

    payload = {
        "inputs": "In a distant galaxy far, far away,",
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


def cleanup():
    """Delete the serverless endpoint and its model."""
    print(f"Cleaning up endpoint: {ENDPOINT_NAME}")

    sm_client = boto3.client("sagemaker")

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
    args = parser.parse_args()

    actions = {
        "deploy": deploy,
        "invoke": invoke,
        "cleanup": cleanup,
    }
    actions[args.action]()


if __name__ == "__main__":
    main()
