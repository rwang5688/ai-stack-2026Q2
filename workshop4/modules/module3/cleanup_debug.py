import boto3
import json
import os
import time

# Initialize clients
session = boto3.session.Session()
region = os.getenv('AWS_REGION', session.region_name)
print(f'Region: {region}')

s3_client = boto3.client('s3', region)
bedrock_agent_client = boto3.client('bedrock-agent', region)
opensearch_client = boto3.client('opensearchserverless', region)
iam_client = boto3.client('iam', region)

def debug_resources():
    """Debug version to see what's happening with resource discovery"""
    print("🔍 DEBUG: Discovering resources...")
    
    try:
        # 1. Get all knowledge bases in current region
        response = bedrock_agent_client.list_knowledge_bases()
        knowledge_bases = response.get('knowledgeBaseSummaries', [])
        print(f"DEBUG: Found {len(knowledge_bases)} knowledge bases")
        
        for kb in knowledge_bases:
            kb_id = kb['knowledgeBaseId']
            kb_name = kb.get('name', 'Unknown')
            print(f"\nDEBUG: Processing KB: {kb_name} ({kb_id})")
            
            try:
                # 2. Get KB details
                kb_details = bedrock_agent_client.get_knowledge_base(knowledgeBaseId=kb_id)
                kb_data = kb_details['knowledgeBase']
                
                print(f"DEBUG: KB Configuration keys: {list(kb_data.keys())}")
                
                # Check storage configuration for OpenSearch
                storage_config = kb_data.get('storageConfiguration', {})
                print(f"DEBUG: Storage Config keys: {list(storage_config.keys())}")
                print(f"DEBUG: Full Storage Config: {json.dumps(storage_config, indent=2, default=str)}")
                
                # Check vector configuration
                kb_config = kb_data.get('knowledgeBaseConfiguration', {})
                print(f"DEBUG: KB Config keys: {list(kb_config.keys())}")
                
                vector_config = kb_config.get('vectorKnowledgeBaseConfiguration', {})
                print(f"DEBUG: Vector Config keys: {list(vector_config.keys())}")
                
                # Print the entire vector config to see structure
                print(f"DEBUG: Full Vector Config: {json.dumps(vector_config, indent=2, default=str)}")
                
                # 3. Get data sources
                ds_response = bedrock_agent_client.list_data_sources(knowledgeBaseId=kb_id)
                data_sources = ds_response.get('dataSourceSummaries', [])
                print(f"DEBUG: Found {len(data_sources)} data sources")
                
                for ds in data_sources:
                    ds_id = ds['dataSourceId']
                    ds_name = ds.get('name', 'Unknown')
                    print(f"DEBUG: Processing Data Source: {ds_name} ({ds_id})")
                    
                    try:
                        ds_details = bedrock_agent_client.get_data_source(
                            knowledgeBaseId=kb_id, 
                            dataSourceId=ds_id
                        )
                        
                        ds_config = ds_details['dataSource']['dataSourceConfiguration']
                        print(f"DEBUG: Data Source Config keys: {list(ds_config.keys())}")
                        print(f"DEBUG: Full Data Source Config: {json.dumps(ds_config, indent=2, default=str)}")
                        
                    except Exception as e:
                        print(f"DEBUG: Error getting data source {ds_id}: {e}")
                
            except Exception as e:
                print(f"DEBUG: Error getting KB details for {kb_id}: {e}")
        
        # 4. Also check what S3 buckets exist with our naming pattern
        print(f"\nDEBUG: Checking S3 buckets with pattern 'bedrock-kb-bucket-{region}'")
        try:
            s3_response = s3_client.list_buckets()
            all_buckets = [b['Name'] for b in s3_response['Buckets']]
            matching_buckets = [b for b in all_buckets if b.startswith(f'bedrock-kb-bucket-{region}')]
            print(f"DEBUG: All buckets: {all_buckets}")
            print(f"DEBUG: Matching buckets: {matching_buckets}")
        except Exception as e:
            print(f"DEBUG: Error listing S3 buckets: {e}")
        
        # 5. Check OpenSearch collections
        print(f"\nDEBUG: Checking OpenSearch collections")
        try:
            os_response = opensearch_client.list_collections()
            collections = os_response.get('collectionSummaries', [])
            print(f"DEBUG: Found {len(collections)} OpenSearch collections:")
            for collection in collections:
                print(f"DEBUG: Collection: {collection.get('name')} (ID: {collection.get('id')})")
        except Exception as e:
            print(f"DEBUG: Error listing OpenSearch collections: {e}")
                
    except Exception as e:
        print(f"DEBUG: Error during discovery: {e}")

if __name__ == '__main__':
    debug_resources()