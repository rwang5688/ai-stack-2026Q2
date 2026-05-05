"""
Deploy a fine-tuned distilgpt2 model to a SageMaker Serverless Inference endpoint
using an explicit Deep Learning Container (DLC) image URI.

This script demonstrates the UNIVERSAL pattern for deploying ANY model with ANY
available AWS Deep Learning Container. Instead of using framework-specific wrapper
classes (like HuggingFaceModel), it uses the generic sagemaker.model.Model class
with a directly constructed DLC image URI.

This approach teaches you how to:
1. Find DLC image URIs from the AWS DLC catalog
2. Construct the full ECR image URI for your region
3. Create a SageMaker Model with any DLC image
4. Deploy to a serverless endpoint for cost-effective inference

The same pattern works with PyTorch DLCs, TensorFlow DLCs, MXNet DLCs, or any
custom container — just change the repository name and tag.

Usage:
    python deploy_serverless.py deploy     # Deploy the model
    python deploy_serverless.py invoke     # Send a test request
    python deploy_serverless.py cleanup    # Delete the endpoint and model

Prerequisites:
    - pip install sagemaker boto3
    - AWS credentials configured (SageMaker execution role or local credentials)
    - The model rwang5688/distilgpt2-finetuned-wikitext2 must exist on HuggingFace Hub

DLC Image Catalog:
    https://aws.github.io/deep-learning-containers/reference/available_images/
"""

import argparse
import json
import sys

import boto3
import sagemaker
from sagemaker.model import Model
from sagemaker.serverless import ServerlessInferenceConfig


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
# CPU tag for serverless (no CUDA needed since serverless runs on CPU):
DLC_ACCOUNT_ID = "763104351884"
DLC_REPOSITORY = "huggingface-pytorch-inference"
DLC_TAG = "2.1.0-transformers4.37.0-cpu-py310-ubuntu22.04"

# Serverless config
# distilgpt2 (~82M params, ~330MB) fits comfortably in 4096 MB
MEMORY_SIZE_IN_MB = 4096
MAX_CONCURRENCY = 5

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
            print("Edit deploy_serverless.py and set LOCAL_EXECUTION_ROLE_ARN to your")
            print("SageMaker execution role ARN, e.g.:")
            print('  LOCAL_EXECUTION_ROLE_ARN = "arn:aws:iam::123456789012:role/YourRole"')
            sys.exit(1)

    print(f"SageMaker role ARN: {role}")
    print(f"SageMaker bucket:   {sess.default_bucket()}")
    print(f"Region:             {sess.boto_region_name}")
    return sess, role


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
    """Deploy the model to a SageMaker Serverless Inference endpoint using an explicit DLC image."""
    sess, role = get_sagemaker_session_and_role()

    # Step 1: Construct the DLC image URI for our region
    # This makes the container selection explicit — you see exactly which image is used.
    image_uri = get_dlc_image_uri(region=sess.boto_region_name)
    print(f"\nDLC Image URI: {image_uri}")

    # Step 2: Create a SageMaker Model using the GENERIC Model class
    # This is the universal pattern — it works with ANY DLC image, not just HuggingFace.
    # The env dict passes configuration to the container (model ID, task, etc.)
    print(f"\nCreating Model with config: {json.dumps(HUB_CONFIG, indent=2)}")

    model = Model(
        image_uri=image_uri,
        env=HUB_CONFIG,
        role=role,
        sagemaker_session=sess,
    )

    # Step 3: Configure serverless inference
    serverless_config = ServerlessInferenceConfig(
        memory_size_in_mb=MEMORY_SIZE_IN_MB,
        max_concurrency=MAX_CONCURRENCY,
    )

    # Step 4: Deploy
    print(f"\nDeploying serverless endpoint: {ENDPOINT_NAME}")
    print(f"  Memory:          {MEMORY_SIZE_IN_MB} MB")
    print(f"  Max concurrency: {MAX_CONCURRENCY}")
    print("  This may take 2-5 minutes...\n")

    predictor = model.deploy(
        endpoint_name=ENDPOINT_NAME,
        serverless_inference_config=serverless_config,
    )

    print(f"\nEndpoint '{ENDPOINT_NAME}' is now InService.")
    print("Run: python deploy_serverless.py invoke")
    return predictor


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
