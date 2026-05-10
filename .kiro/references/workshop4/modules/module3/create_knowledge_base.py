import boto3
import json
import logging
import os
import re
import time
import uuid

from knowledge_base import BedrockKnowledgeBase


logging.basicConfig(format='[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

session = boto3.session.Session()
region = os.getenv('AWS_REGION', session.region_name)
if region:
    print(f'Region: {region}')
else:
    print("Cannot determine AWS region from `AWS_REGION` environment variable or from `boto3.session.Session().region_name`")
    raise

s3_client = boto3.client('s3', region)
bedrock_agent_client = boto3.client('bedrock-agent', region)
bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime', region)

def create_s3_bucket_with_random_suffix(prefix):
    random_suffix = str(uuid.uuid4())[:8]
    bucket_name = f"{prefix.lower()}-{region}-{random_suffix.lower()}"
    try:
        if region == "us-east-1":
            # For us-east-1, we don't specify LocationConstraint
            response = s3_client.create_bucket(
                Bucket=bucket_name
            )
        else:
            # For other regions, we need to specify LocationConstraint
            response = s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': region
                }
            )

        print(f"Successfully created bucket: {bucket_name}")

        # Wait for the bucket to be available
        waiter = s3_client.get_waiter('bucket_exists')
        waiter.wait(Bucket=bucket_name)
        return bucket_name

    except Exception as e:
        print(f"Error creating bucket: {e}")
        return None

def upload_directory(path, bucket_name):
    for root,dirs,files in os.walk(path):
        for file in files:
            file_to_upload = os.path.join(root,file)
            basename = os.path.basename(file_to_upload)
            if basename == ".DS_Store":
                continue
            print(f"uploading file {file_to_upload} to {bucket_name}")
            s3_client.upload_file(file_to_upload,bucket_name,file)

def check_bucket_has_files(bucket_name, expected_files):
    """Check if S3 bucket contains the expected PDF files"""
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' not in response:
            print(f"Bucket {bucket_name} is empty")
            return False
        
        existing_files = [obj['Key'] for obj in response['Contents']]
        missing_files = [f for f in expected_files if f not in existing_files]
        
        if missing_files:
            print(f"Bucket {bucket_name} is missing files: {missing_files}")
            return False
        
        print(f"Bucket {bucket_name} contains all {len(expected_files)} expected files")
        return True
    except Exception as e:
        print(f"Error checking bucket contents: {e}")
        return False

def get_or_create_s3_bucket():
    """Get existing bucket or create new one if needed"""
    buckets = s3_client.list_buckets()['Buckets']
    s3_buckets = [b['Name'] for b in buckets if b['Name'].startswith(f'bedrock-kb-bucket-{region}')]
    
    if s3_buckets:
        print(f"Found existing bucket: {s3_buckets[0]}")
        return s3_buckets[0]
    else:
        bucket_name = create_s3_bucket_with_random_suffix('bedrock-kb-bucket')
        print(f"Created new S3 bucket: {bucket_name}")
        return bucket_name

def create_bedrock_knowledge_base(name, description, s3_bucket):
    knowledge_base = BedrockKnowledgeBase(
        kb_name=name,
        kb_description=description,
        data_bucket_name=s3_bucket,
        embedding_model = "amazon.titan-embed-text-v2:0"
    )
    # Actually create/retrieve the knowledge base resources
    knowledge_base.create_or_retrieve_knowledge_base()
    print("Sleeping for 30 seconds.....")
    time.sleep(30)
    return knowledge_base

def ingest_knowledge_base_documents(knowledge_base_id, data_source_id, s3_bucket, kb_folder):
    # Ingest all files in folder into Bedrock Knowledge Base Custom Data Source
    kb_files = [ file for file in os.listdir(kb_folder) if file.endswith('.pdf') ]

    documents = []
    for kb_file in kb_files:
        s3_uri = f's3://{s3_bucket}/{kb_file}'
        clean_filename = re.sub(r'[\s-]+', '-', kb_file)
        custom_document_identifier = os.path.splitext(clean_filename)[0]
        custom_document_identifier = custom_document_identifier.lower()
        print(f'{s3_uri} -> Custom Document Identifier: "{custom_document_identifier}"')
        documents.append(
            {
                'content': {
                    'custom': {
                        'customDocumentIdentifier': {
                            'id': custom_document_identifier
                        },
                        's3Location': {
                            'uri': s3_uri
                        },
                        'sourceType': 'S3_LOCATION'
                    },
                    'dataSourceType': 'CUSTOM'
                }
            }
        )
    try:
        response = bedrock_agent_client.ingest_knowledge_base_documents(
            dataSourceId = data_source_id,
            documents=documents,
            knowledgeBaseId = knowledge_base_id
        )
        print(json.dumps(response, indent=2, default=str))
    except Exception as e:
        print(f'Exception: {e}')
        return None
    return response


def main():
    folder = 'pets-kb-files'
    
    # Check if local folder exists
    if not os.path.isdir(folder):
        print(f"❌ Error: Local folder '{folder}' not found!")
        print(f"Please ensure the '{folder}' directory exists in the current directory.")
        print(f"This directory should contain the PDF files for the knowledge base.")
        return
    
    print(f"✅ Found local folder '{folder}' with PDF files")
    
    # Get list of PDF files that should be in S3
    pdf_files = [f for f in os.listdir(folder) if f.endswith('.pdf')]
    if not pdf_files:
        print(f"❌ Error: No PDF files found in '{folder}' directory!")
        print(f"Please add PDF files to the '{folder}' directory and try again.")
        return
        
    print(f"Found {len(pdf_files)} PDF files to upload: {pdf_files}")
    
    # Step 2: Get or create S3 bucket
    s3_bucket = get_or_create_s3_bucket()
    
    # Step 3: Check if S3 bucket has the files, if not upload them
    if not check_bucket_has_files(s3_bucket, pdf_files):
        print(f"Uploading {len(pdf_files)} files to S3 bucket {s3_bucket}...")
        upload_directory(folder, s3_bucket)
        print("Upload completed!")
    else:
        print("S3 bucket already contains all required files, skipping upload")

    # Step 4: Create or get existing Bedrock Knowledge Base
    response = bedrock_agent_client.list_knowledge_bases()
    knowledge_bases = response.get('knowledgeBaseSummaries')
    if not len(knowledge_bases):
        print("Creating new Bedrock Knowledge Base...")
        random_suffix = str(uuid.uuid4())[:8]
        knowledge_base = create_bedrock_knowledge_base(
            name = f'pets-kb-{random_suffix}',
            description = 'Pets Knowledge Base on cats and dogs',
            s3_bucket = s3_bucket
        )
        knowledge_base_id = knowledge_base.get_knowledge_base_id()
        data_source_id = knowledge_base.get_datasource_id()
        print(f'Created Bedrock Knowledge Base with ID: {knowledge_base_id}')
    else:
        print('Using existing Bedrock Knowledge Base')
        knowledge_base_id = knowledge_bases[0]['knowledgeBaseId']
        response = bedrock_agent_client.list_data_sources(knowledgeBaseId=knowledge_base_id)
        data_sources = response['dataSourceSummaries']
        data_source_ids = [ d['dataSourceId'] for d in data_sources ]
        if len(data_source_ids):
            data_source_id = data_source_ids[0]
            
            # CRITICAL: Update IAM policies for existing KB to ensure they point to current resources
            print("🔧 Updating IAM policies for existing Knowledge Base...")
            kb_wrapper = BedrockKnowledgeBase(
                kb_name=knowledge_bases[0]['name'],
                kb_description=knowledge_bases[0]['description'],
                data_bucket_name=s3_bucket,
                embedding_model="amazon.titan-embed-text-v2:0"
            )
            # Get the collection info for the existing KB
            kb_details = bedrock_agent_client.get_knowledge_base(knowledgeBaseId=knowledge_base_id)
            collection_arn = kb_details['knowledgeBase']['storageConfiguration']['opensearchServerlessConfiguration']['collectionArn']
            kb_wrapper.collection_id = collection_arn.split('/')[-1]  # Extract collection ID from ARN
            kb_wrapper.update_all_iam_policies_for_current_resources()
            print("✅ IAM policies updated for existing Knowledge Base")
            print("⏳ Waiting 30 seconds for IAM policy changes to propagate...")
            time.sleep(30)
        else:
            print('Error: Data source not created. Please create a custom data source manually')
            return

    print(f'Loading documents into Bedrock Knowledge Base: {knowledge_base_id}')
    print(f'Data Source ID: {data_source_id}')

    # Step 5: Ingest documents from S3 into Bedrock Knowledge Base
    # Requires the appropriate S3 bucket permissions in the
    # Knowledge Base role: AmazonBedrockExecutionRoleForKnowledgeBase_xx 
    ingest_knowledge_base_documents(
        knowledge_base_id = knowledge_base_id,
        data_source_id = data_source_id,
        s3_bucket = s3_bucket,
        kb_folder = folder
    )

if __name__ == '__main__':
    main()
