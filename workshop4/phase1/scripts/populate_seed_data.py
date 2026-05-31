#!/usr/bin/env python3
"""
Populate seed data for the Student Services multi-agent application.

This script:
1. Reads CloudFormation stack outputs to get resource names/IDs
2. Uploads data files to S3 with proper prefixes
3. Parses CSVs and populates DynamoDB tables via batch_write_item
4. Triggers Bedrock KB ingestion job and waits for completion
5. Writes the XGBoost endpoint name to SSM Parameter Store
"""

import argparse
import csv
import os
import sys
import time

import boto3


def get_stack_outputs(stack_name: str, region: str) -> dict:
    """Read CloudFormation stack outputs and return as a dictionary."""
    cf_client = boto3.client("cloudformation", region_name=region)
    try:
        response = cf_client.describe_stacks(StackName=stack_name)
    except cf_client.exceptions.ClientError as e:
        print(f"ERROR: Could not describe stack '{stack_name}': {e}")
        sys.exit(1)

    stacks = response.get("Stacks", [])
    if not stacks:
        print(f"ERROR: Stack '{stack_name}' not found.")
        sys.exit(1)

    outputs = {}
    for output in stacks[0].get("Outputs", []):
        outputs[output["OutputKey"]] = output["OutputValue"]

    required_keys = [
        "DataBucketName",
        "KnowledgeBaseId",
        "DataSourceId",
        "CourseRegistrationTableName",
        "CourseReviewTableName",
    ]
    for key in required_keys:
        if key not in outputs:
            print(f"ERROR: Missing expected stack output: {key}")
            sys.exit(1)

    return outputs


def upload_files_to_s3(bucket_name: str, data_dir: str, region: str):
    """Upload data files to S3 with proper prefixes."""
    s3_client = boto3.client("s3", region_name=region)

    uploads = [
        ("course_catalog.pdf", "kb-datasource/course_catalog.pdf"),
        ("course_reviews.csv", "dynamodb/course_reviews.csv"),
        ("course_registrations.csv", "dynamodb/course_registrations.csv"),
    ]

    for local_file, s3_key in uploads:
        local_path = os.path.join(data_dir, local_file)
        if not os.path.exists(local_path):
            print(f"WARNING: File not found, skipping: {local_path}")
            continue
        print(f"  Uploading {local_file} → s3://{bucket_name}/{s3_key}")
        s3_client.upload_file(local_path, bucket_name, s3_key)

    print("  S3 uploads complete.")


def populate_dynamodb_table(table_name: str, csv_path: str, region: str):
    """Parse a CSV file and populate a DynamoDB table via batch_write_item."""
    dynamodb = boto3.resource("dynamodb", region_name=region)
    table = dynamodb.Table(table_name)

    if not os.path.exists(csv_path):
        print(f"WARNING: CSV file not found, skipping: {csv_path}")
        return

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        items = list(reader)

    if not items:
        print(f"  No records found in {csv_path}")
        return

    # Use batch_write_item for efficiency
    with table.batch_writer() as batch:
        for item in items:
            # Convert numeric fields where appropriate
            cleaned_item = {}
            for key, value in item.items():
                if value == "":
                    continue
                # Try to convert to number for known numeric fields
                if key in ("difficulty", "rating", "review_count", "workload_hrs_per_week"):
                    try:
                        # Use Decimal-compatible string for DynamoDB
                        if "." in value:
                            cleaned_item[key] = value
                        else:
                            cleaned_item[key] = value
                    except (ValueError, TypeError):
                        cleaned_item[key] = value
                else:
                    cleaned_item[key] = value
            batch.put_item(Item=cleaned_item)

    print(f"  Loaded {len(items)} records into {table_name}")


def trigger_kb_ingestion(knowledge_base_id: str, data_source_id: str, region: str):
    """Trigger Bedrock KB ingestion job and wait for completion."""
    bedrock_agent_client = boto3.client("bedrock-agent", region_name=region)

    print(f"  Starting ingestion job for KB={knowledge_base_id}, DataSource={data_source_id}")
    response = bedrock_agent_client.start_ingestion_job(
        knowledgeBaseId=knowledge_base_id,
        dataSourceId=data_source_id,
    )

    ingestion_job_id = response["ingestionJob"]["ingestionJobId"]
    print(f"  Ingestion job started: {ingestion_job_id}")

    # Poll for completion
    while True:
        status_response = bedrock_agent_client.get_ingestion_job(
            knowledgeBaseId=knowledge_base_id,
            dataSourceId=data_source_id,
            ingestionJobId=ingestion_job_id,
        )
        status = status_response["ingestionJob"]["status"]
        print(f"  Ingestion status: {status}")

        if status in ("COMPLETE", "FAILED", "STOPPED"):
            break

        time.sleep(5)

    if status != "COMPLETE":
        print(f"WARNING: Ingestion job ended with status: {status}")
        if "failureReasons" in status_response["ingestionJob"]:
            for reason in status_response["ingestionJob"]["failureReasons"]:
                print(f"  Failure reason: {reason}")
    else:
        stats = status_response["ingestionJob"].get("statistics", {})
        print(f"  Ingestion complete. Stats: {stats}")


def write_xgboost_endpoint_to_ssm(endpoint_name: str, region: str):
    """Write the XGBoost endpoint name to SSM Parameter Store."""
    ssm_client = boto3.client("ssm", region_name=region)
    param_name = "/student-services/xgboost-endpoint-name"

    ssm_client.put_parameter(
        Name=param_name,
        Value=endpoint_name,
        Type="String",
        Overwrite=True,
    )
    print(f"  SSM parameter written: {param_name} = {endpoint_name}")


def print_ssm_summary(region: str):
    """Print a summary of all SSM parameters under /student-services/."""
    ssm_client = boto3.client("ssm", region_name=region)

    params = []
    next_token = None
    while True:
        kwargs = {
            "Path": "/student-services/",
            "Recursive": True,
            "WithDecryption": False,
        }
        if next_token:
            kwargs["NextToken"] = next_token

        response = ssm_client.get_parameters_by_path(**kwargs)
        params.extend(response.get("Parameters", []))
        next_token = response.get("NextToken")
        if not next_token:
            break

    print("\n  SSM Parameters under /student-services/:")
    print("  " + "-" * 60)
    for param in sorted(params, key=lambda p: p["Name"]):
        print(f"  {param['Name']} = {param['Value']}")
    print("  " + "-" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Populate seed data for Student Services application."
    )
    parser.add_argument(
        "--stack-name",
        default="student-services-infra",
        help="CloudFormation stack name (default: student-services-infra)",
    )
    parser.add_argument(
        "--region",
        default="us-west-2",
        help="AWS region (default: us-west-2)",
    )
    parser.add_argument(
        "--xgboost-endpoint-name",
        default=None,
        help="SageMaker XGBoost endpoint name (reads from .env file if not provided)",
    )

    args = parser.parse_args()

    # Read .env file if it exists (for XGBOOST_ENDPOINT_NAME)
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    env_file = os.path.normpath(env_file)
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if value and not value.startswith("<"):
                        os.environ.setdefault(key, value)

    # If --xgboost-endpoint-name not provided, try .env
    if not args.xgboost_endpoint_name:
        args.xgboost_endpoint_name = os.environ.get("XGBOOST_ENDPOINT_NAME")

    # Determine data directory relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data")
    data_dir = os.path.normpath(data_dir)

    print(f"Stack: {args.stack_name}")
    print(f"Region: {args.region}")
    print(f"Data directory: {data_dir}")
    print()

    # Step 1: Read stack outputs
    print("[1/5] Reading CloudFormation stack outputs...")
    outputs = get_stack_outputs(args.stack_name, args.region)
    bucket_name = outputs["DataBucketName"]
    kb_id = outputs["KnowledgeBaseId"]
    ds_id = outputs["DataSourceId"]
    reg_table = outputs["CourseRegistrationTableName"]
    reviews_table = outputs["CourseReviewTableName"]
    print(f"  Data bucket: {bucket_name}")
    print(f"  Knowledge Base ID: {kb_id}")
    print(f"  Data Source ID: {ds_id}")
    print(f"  Registration table: {reg_table}")
    print(f"  Reviews table: {reviews_table}")
    print()

    # Step 2: Upload files to S3
    print("[2/5] Uploading data files to S3...")
    upload_files_to_s3(bucket_name, data_dir, args.region)
    print()

    # Step 3: Populate DynamoDB tables
    print("[3/5] Populating DynamoDB tables...")
    reviews_csv = os.path.join(data_dir, "course_reviews.csv")
    registrations_csv = os.path.join(data_dir, "course_registrations.csv")
    populate_dynamodb_table(reviews_table, reviews_csv, args.region)
    populate_dynamodb_table(reg_table, registrations_csv, args.region)
    print()

    # Step 4: Trigger KB ingestion
    print("[4/5] Triggering Bedrock Knowledge Base ingestion...")
    trigger_kb_ingestion(kb_id, ds_id, args.region)
    print()

    # Step 5: Write XGBoost endpoint to SSM (if provided)
    if args.xgboost_endpoint_name:
        print("[5/5] Writing XGBoost endpoint name to SSM Parameter Store...")
        write_xgboost_endpoint_to_ssm(args.xgboost_endpoint_name, args.region)
    else:
        print("[5/5] Skipping XGBoost endpoint — not provided.")
        print("  WARNING: Loan Application Agent won't work until you run:")
        print(f"  python scripts/populate_seed_data.py --region {args.region} --xgboost-endpoint-name <your-endpoint>")
    print()

    # Print summary
    print("=" * 60)
    print("Seed data population complete!")
    print_ssm_summary(args.region)
    print()


if __name__ == "__main__":
    main()
