"""
Deploy a fine-tuned distilgpt2 model to a SageMaker Serverless Inference endpoint
using the HuggingFace Deep Learning Container.

Usage:
    python deploy_serverless.py deploy     # Deploy the model
    python deploy_serverless.py invoke     # Send a test request
    python deploy_serverless.py cleanup    # Delete the endpoint and model

Prerequisites:
    - pip install sagemaker boto3
    - AWS credentials configured (SageMaker execution role or local credentials)
    - The model rwang5688/distilgpt2-finetuned-wikitext2 must exist on HuggingFace Hub
"""

import argparse
import json
import sys

import boto3
import sagemaker
from sagemaker.huggingface.model import HuggingFaceModel
from sagemaker.serverless import ServerlessInferenceConfig


# --- Configuration ---
ENDPOINT_NAME = "distilgpt2-finetuned-wikitext2-serverless"

HUB_CONFIG = {
    "HF_MODEL_ID": "rwang5688/distilgpt2-finetuned-wikitext2",
    "HF_TASK": "text-generation",
}

# HuggingFace DLC versions
# Check available versions: https://github.com/aws/deep-learning-containers/blob/master/available_images.md
TRANSFORMERS_VERSION = "4.37.0"
PYTORCH_VERSION = "2.1.0"
PY_VERSION = "py310"

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


def deploy():
    """Deploy the model to a SageMaker Serverless Inference endpoint."""
    sess, role = get_sagemaker_session_and_role()

    print(f"\nCreating HuggingFaceModel with config: {json.dumps(HUB_CONFIG, indent=2)}")

    huggingface_model = HuggingFaceModel(
        env=HUB_CONFIG,
        role=role,
        transformers_version=TRANSFORMERS_VERSION,
        pytorch_version=PYTORCH_VERSION,
        py_version=PY_VERSION,
        sagemaker_session=sess,
    )

    serverless_config = ServerlessInferenceConfig(
        memory_size_in_mb=MEMORY_SIZE_IN_MB,
        max_concurrency=MAX_CONCURRENCY,
    )

    print(f"\nDeploying serverless endpoint: {ENDPOINT_NAME}")
    print(f"  Memory:         {MEMORY_SIZE_IN_MB} MB")
    print(f"  Max concurrency: {MAX_CONCURRENCY}")
    print("  This may take 2-5 minutes...\n")

    predictor = huggingface_model.deploy(
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
