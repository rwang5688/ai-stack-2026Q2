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

def cleanup_knowledge_bases():
    """Delete all knowledge bases"""
    print("🧹 Cleaning up Knowledge Bases...")
    try:
        response = bedrock_agent_client.list_knowledge_bases()
        knowledge_bases = response.get('knowledgeBaseSummaries', [])
        
        for kb in knowledge_bases:
            kb_id = kb['knowledgeBaseId']
            print(f"  Deleting Knowledge Base: {kb_id}")
            
            # Delete data sources first
            try:
                ds_response = bedrock_agent_client.list_data_sources(knowledgeBaseId=kb_id)
                for ds in ds_response.get('dataSourceSummaries', []):
                    print(f"    Deleting Data Source: {ds['dataSourceId']}")
                    bedrock_agent_client.delete_data_source(
                        knowledgeBaseId=kb_id,
                        dataSourceId=ds['dataSourceId']
                    )
                    time.sleep(2)
            except Exception as e:
                print(f"    Error deleting data sources: {e}")
            
            # Delete the knowledge base
            try:
                bedrock_agent_client.delete_knowledge_base(knowledgeBaseId=kb_id)
                print(f"    ✅ Deleted Knowledge Base: {kb_id}")
                time.sleep(3)
            except Exception as e:
                print(f"    ❌ Error deleting knowledge base: {e}")
                
        print(f"✅ Cleaned up {len(knowledge_bases)} knowledge bases")
    except Exception as e:
        print(f"❌ Error listing knowledge bases: {e}")

def cleanup_s3_buckets():
    """Delete bedrock-kb-bucket-* buckets"""
    print("🗑️  Cleaning up S3 Buckets...")
    try:
        response = s3_client.list_buckets()
        buckets_to_delete = [b['Name'] for b in response['Buckets'] 
                           if b['Name'].startswith('bedrock-kb-bucket')]
        
        for bucket_name in buckets_to_delete:
            print(f"  Deleting S3 bucket: {bucket_name}")
            
            # Delete all objects first
            try:
                objects_response = s3_client.list_objects_v2(Bucket=bucket_name)
                if 'Contents' in objects_response:
                    objects_to_delete = [{'Key': obj['Key']} for obj in objects_response['Contents']]
                    s3_client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': objects_to_delete}
                    )
                    print(f"    Deleted {len(objects_to_delete)} objects")
                
                # Delete the bucket
                s3_client.delete_bucket(Bucket=bucket_name)
                print(f"    ✅ Deleted bucket: {bucket_name}")
                
            except Exception as e:
                print(f"    ❌ Error deleting bucket {bucket_name}: {e}")
        
        print(f"✅ Cleaned up {len(buckets_to_delete)} S3 buckets")
    except Exception as e:
        print(f"❌ Error listing S3 buckets: {e}")

def cleanup_opensearch_collections():
    """Delete OpenSearch Serverless collections"""
    print("🔍 Cleaning up OpenSearch Collections...")
    try:
        response = opensearch_client.list_collections()
        collections = response.get('collectionSummaries', [])
        
        for collection in collections:
            collection_name = collection['name']
            if 'bedrock' in collection_name.lower() or 'kb' in collection_name.lower():
                print(f"  Deleting OpenSearch collection: {collection_name}")
                try:
                    opensearch_client.delete_collection(id=collection['id'])
                    print(f"    ✅ Deleted collection: {collection_name}")
                    time.sleep(2)
                except Exception as e:
                    print(f"    ❌ Error deleting collection {collection_name}: {e}")
        
        print(f"✅ Cleaned up OpenSearch collections")
    except Exception as e:
        print(f"❌ Error listing OpenSearch collections: {e}")

def cleanup_iam_roles():
    """Delete Bedrock-related IAM roles and policies"""
    print("👤 Cleaning up IAM Roles and Policies...")
    try:
        response = iam_client.list_roles()
        roles_to_delete = [role for role in response['Roles'] 
                          if 'AmazonBedrockExecutionRoleForKnowledgeBase' in role['RoleName']]
        
        # Collect all policy ARNs to delete
        policies_to_delete = set()
        
        for role in roles_to_delete:
            role_name = role['RoleName']
            print(f"  Deleting IAM role: {role_name}")
            
            try:
                # Collect attached managed policies for deletion
                attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)
                for policy in attached_policies['AttachedPolicies']:
                    policy_arn = policy['PolicyArn']
                    # Only delete policies we created (not AWS managed policies)
                    if 'AmazonBedrock' in policy_arn and 'policy/' in policy_arn:
                        policies_to_delete.add(policy_arn)
                    
                    iam_client.detach_role_policy(
                        RoleName=role_name,
                        PolicyArn=policy_arn
                    )
                
                # Delete inline policies
                inline_policies = iam_client.list_role_policies(RoleName=role_name)
                for policy_name in inline_policies['PolicyNames']:
                    iam_client.delete_role_policy(
                        RoleName=role_name,
                        PolicyName=policy_name
                    )
                
                # Delete the role
                iam_client.delete_role(RoleName=role_name)
                print(f"    ✅ Deleted role: {role_name}")
                
            except Exception as e:
                print(f"    ❌ Error deleting role {role_name}: {e}")
        
        # Also find and delete orphaned Bedrock policies (not attached to any role)
        print("  Searching for orphaned Bedrock policies...")
        try:
            paginator = iam_client.get_paginator('list_policies')
            for page in paginator.paginate(Scope='Local'):  # Only customer-managed policies
                for policy in page['Policies']:
                    policy_name = policy['PolicyName']
                    policy_arn = policy['Arn']
                    
                    # Look for all Bedrock KnowledgeBase-related policies
                    if 'AmazonBedrock' in policy_name and 'KnowledgeBase' in policy_name:
                        policies_to_delete.add(policy_arn)
                        print(f"    Found orphaned policy: {policy_name}")
        except Exception as e:
            print(f"    ❌ Error listing policies: {e}")
        
        # Now delete the collected policies
        for policy_arn in policies_to_delete:
            try:
                policy_name = policy_arn.split('/')[-1]
                iam_client.delete_policy(PolicyArn=policy_arn)
                print(f"    ✅ Deleted policy: {policy_name}")
            except Exception as e:
                print(f"    ❌ Error deleting policy {policy_arn}: {e}")
        
        print(f"✅ Cleaned up {len(roles_to_delete)} IAM roles and {len(policies_to_delete)} policies")
    except Exception as e:
        print(f"❌ Error listing IAM roles: {e}")

def main():
    print("🚀 Starting COMPLETE CLEANUP")
    print("=" * 50)
    
    # Clean up in order: KB -> S3 -> OpenSearch -> IAM
    cleanup_knowledge_bases()
    print()
    cleanup_s3_buckets()
    print()
    cleanup_opensearch_collections()
    print()
    cleanup_iam_roles()
    
    print("\n" + "=" * 50)
    print("🎉 CLEANUP COMPLETE!")
    print("You can now run: uv run python create_knowledge_base.py")

if __name__ == '__main__':
    main()