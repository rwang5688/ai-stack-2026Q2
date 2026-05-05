"""
Deploy a fine-tuned distilgpt2 model to a SageMaker Real-Time Inference endpoint
on a GPU instance using an explicit Deep Learning Container (DLC) image URI.

This script demonstrates deploying to a PROVISIONED GPU endpoint — in contrast to
deploy_serverless.py which deploys to a serverless CPU endpoint. The same universal
DLC pattern is used, but here we:
  1. Use the GPU-optimized variant of the DLC image (includes CUDA)
  2. Deploy to a dedicated ml.g6.xlarge instance (NVIDIA L4, 24 GB VRAM)

Key differences from serverless:
  - GPU acceleration (faster inference)
  - No cold starts (instance is always running)
  - Charges PER HOUR while the endpoint is active (~$0.80/hr for ml.g6.xlarge)
  - ALWAYS run cleanup when done to stop charges!

Usage:
    python deploy_provisioned.py deploy     # Deploy the model to a GPU instance
    python deploy_provisioned.py invoke     # Send a test request
    python deploy_provisioned.py cleanup    # Delete the endpoint (STOPS CHARGES)

Prerequisites:
    - pip install sagemaker boto3
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
import sagemaker
from sagemaker.model import Model


# --- Configuration ---
ENDPOINT_NAME = "distilgpt2-finetuned-wikitext2-provisioned"

# Environment variables passed to the DLC container.
# The HuggingFace DLC uses these to know which model to download and what task to run.
HUB_CONFIG = {
    "HF_MODEL_ID": "rwang5688/distilgpt2-finetuned-wikitext2",
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
DLC_ACCOUNT_ID = "763104351884"
DLC_REPOSITORY = "huggingface-pytorch-inference"
DLC_TAG = "2.1.0-transformers4.37.0-gpu-py310-cu118-ubuntu20.04"

# --- Provisioned Endpoint Configuration ---
# ml.g6.xlarge: NVIDIA L4 GPU, 24 GB VRAM, 4 vCPUs, 16 GB RAM
# This is the same instance type used for training in Workshop 2.
DEPLOY_INSTANCE_TYPE = "ml.g6.xlarge"
INITIAL_INSTANCE_COUNT = 1

# If running locally (not in SageMaker), replace with your SageMaker execution role ARN.
# Example: "arn:aws:iam::123456789012:role/YourSageMakerExecutionRole"
LOCAL_EXECUTION_ROLE_ARN = None


def get_sagemaker_session_and_role():
    """Set up SageMaker session and resolve the execution role."""
    sess = sagemaker.Session()

    try:
        # Works automatically inside SageMaker JupyterLab / Studio / Notebook Instances
        role = sagemaker.get_execution_role()
    except ValueError:
        # Running locally — use the explicitly configured role ARN
        if LOCAL_EXECUTION_ROLE_ARN:
            role = LOCAL_EXECUTION_ROLE_ARN
        else:
            print("ERROR: Not running in SageMaker and LOCAL_EXECUTION_ROLE_ARN is not set.")
            print("Edit deploy_provisioned.py and set LOCAL_EXECUTION_ROLE_ARN to your")
            print("SageMaker execution role ARN, e.g.:")
            print('  LOCAL_EXECUTION_ROLE_ARN = "arn:aws:iam::123456789012:role/YourRole"')
            sys.exit(1)

    print(f"SageMaker role ARN: {role}")
    print(f"SageMaker bucket:   {sess.default_bucket()}")
    print(f"Region:             {sess.boto_region_name}")
    return sess, role


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


def deploy():
    """Deploy the model to a provisioned GPU endpoint (ml.g6.xlarge)."""
    sess, role = get_sagemaker_session_and_role()

    # Step 1: Construct the GPU-optimized DLC image URI
    # Note: This uses a DIFFERENT tag than deploy_serverless.py — the GPU tag includes
    # CUDA libraries for GPU-accelerated inference.
    image_uri = get_dlc_image_uri(region=sess.boto_region_name)
    print(f"\nDLC Image URI (GPU): {image_uri}")

    # Step 2: Create a SageMaker Model — same universal pattern as serverless
    print(f"\nCreating Model with config: {json.dumps(HUB_CONFIG, indent=2)}")

    model = Model(
        image_uri=image_uri,
        env=HUB_CONFIG,
        role=role,
        sagemaker_session=sess,
    )

    # Step 3: Deploy to a PROVISIONED endpoint with a dedicated GPU instance
    # Unlike serverless, this creates an always-on instance that charges per hour.
    print(f"\nDeploying provisioned endpoint: {ENDPOINT_NAME}")
    print(f"  Instance type:    {DEPLOY_INSTANCE_TYPE} (NVIDIA L4, 24 GB VRAM)")
    print(f"  Instance count:   {INITIAL_INSTANCE_COUNT}")
    print("  This may take 5-10 minutes...\n")
    print("  ** COST WARNING: This endpoint charges ~$0.80/hour while running.")
    print("  ** Run 'python deploy_provisioned.py cleanup' when done!\n")

    predictor = model.deploy(
        endpoint_name=ENDPOINT_NAME,
        instance_type=DEPLOY_INSTANCE_TYPE,
        initial_instance_count=INITIAL_INSTANCE_COUNT,
    )

    print(f"\nEndpoint '{ENDPOINT_NAME}' is now InService.")
    print("Run: python deploy_provisioned.py invoke")
    print("\n** Remember: Run 'python deploy_provisioned.py cleanup' when done to stop charges!")
    return predictor


def invoke():
    """Send a test text-generation request to the provisioned endpoint."""
    print(f"Invoking endpoint: {ENDPOINT_NAME}")
    print("  (No cold start — GPU instance is always running)\n")

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
    """Delete the provisioned endpoint and its model. STOPS HOURLY CHARGES."""
    print(f"Cleaning up endpoint: {ENDPOINT_NAME}")
    print("  (This will stop the hourly GPU instance charges)\n")

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
    args = parser.parse_args()

    actions = {
        "deploy": deploy,
        "invoke": invoke,
        "cleanup": cleanup,
    }
    actions[args.action]()


if __name__ == "__main__":
    main()
