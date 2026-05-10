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

def get_resources_to_cleanup():
    """Get exact resources used by knowledge bases for targeted cleanup"""
    print("🔍 Discovering resources to cleanup...")
    
    resources = {
        'knowledge_bases': [],
        's3_buckets': set(),
        'iam_roles': set(),
        'iam_policies': set(),
        'opensearch_collections': set()
    }
    
    try:
        # 1. Get all knowledge bases in current region
        response = bedrock_agent_client.list_knowledge_bases()
        knowledge_bases = response.get('knowledgeBaseSummaries', [])
        
        for kb in knowledge_bases:
            kb_id = kb['knowledgeBaseId']
            kb_name = kb.get('name', 'Unknown')
            resources['knowledge_bases'].append({'id': kb_id, 'name': kb_name})
            
            try:
                # 2. Get KB details for IAM role and OpenSearch collection
                kb_details = bedrock_agent_client.get_knowledge_base(knowledgeBaseId=kb_id)
                kb_data = kb_details['knowledgeBase']
                
                # Extract IAM role
                role_arn = kb_data.get('roleArn')
                if role_arn:
                    resources['iam_roles'].add(role_arn)
                
                # Extract OpenSearch collection from storage configuration
                storage_config = kb_data.get('storageConfiguration', {})
                if 'opensearchServerlessConfiguration' in storage_config:
                    collection_arn = storage_config['opensearchServerlessConfiguration'].get('collectionArn')
                    if collection_arn:
                        resources['opensearch_collections'].add(collection_arn)
                
                # Also check vector configuration as fallback (for different KB types)
                kb_config = kb_data.get('knowledgeBaseConfiguration', {})
                vector_config = kb_config.get('vectorKnowledgeBaseConfiguration', {})
                if 'opensearchServerlessConfiguration' in vector_config:
                    collection_arn = vector_config['opensearchServerlessConfiguration'].get('collectionArn')
                    if collection_arn:
                        resources['opensearch_collections'].add(collection_arn)
                
                # 3. Get data sources for S3 buckets
                try:
                    ds_response = bedrock_agent_client.list_data_sources(knowledgeBaseId=kb_id)
                    data_sources = ds_response.get('dataSourceSummaries', [])
                    
                    for ds in data_sources:
                        ds_id = ds['dataSourceId']
                        try:
                            ds_details = bedrock_agent_client.get_data_source(
                                knowledgeBaseId=kb_id, 
                                dataSourceId=ds_id
                            )
                            
                            # Extract S3 bucket if it's an S3 data source
                            ds_config = ds_details['dataSource']['dataSourceConfiguration']
                            if 's3Configuration' in ds_config:
                                bucket_arn = ds_config['s3Configuration'].get('bucketArn')
                                if bucket_arn:
                                    # Extract bucket name from ARN: arn:aws:s3:::bucket-name
                                    bucket_name = bucket_arn.split(':::')[1] if ':::' in bucket_arn else bucket_arn
                                    resources['s3_buckets'].add(bucket_name)
                            
                            # For CUSTOM data sources, we need to find S3 buckets by pattern matching
                            elif ds_config.get('type') == 'CUSTOM':
                                # Look for S3 buckets that match our naming patterns
                                s3_response = s3_client.list_buckets()
                                all_buckets = [b['Name'] for b in s3_response['Buckets']]
                                
                                # Check both old and new naming patterns
                                for bucket_name in all_buckets:
                                    # New pattern: bedrock-kb-bucket-{region}-{suffix}
                                    if bucket_name.startswith(f'bedrock-kb-bucket-{region}-'):
                                        resources['s3_buckets'].add(bucket_name)
                                    # Old pattern: bedrock-kb-bucket-{suffix} (no region)
                                    elif bucket_name.startswith('bedrock-kb-bucket-') and len(bucket_name.split('-')) == 4:
                                        # Old pattern has exactly 4 parts: bedrock-kb-bucket-{8char-suffix}
                                        resources['s3_buckets'].add(bucket_name)
                        
                        except Exception as e:
                            print(f"    ⚠️  Warning: Could not get data source {ds_id}: {e}")
                
                except Exception as e:
                    print(f"    ⚠️  Warning: Could not list data sources for KB {kb_id}: {e}")
            
            except Exception as e:
                print(f"    ⚠️  Warning: Could not get details for KB {kb_id}: {e}")
        
        # 4. For each IAM role, get attached policies
        for role_arn in list(resources['iam_roles']):
            try:
                role_name = role_arn.split('/')[-1]
                
                # Get managed policies attached to this role
                attached_response = iam_client.list_attached_role_policies(RoleName=role_name)
                for policy in attached_response.get('AttachedPolicies', []):
                    policy_arn = policy['PolicyArn']
                    # Only include customer-managed policies (not AWS managed)
                    if not policy_arn.startswith('arn:aws:iam::aws:'):
                        resources['iam_policies'].add(policy_arn)
                
            except Exception as e:
                print(f"    ⚠️  Warning: Could not get policies for role {role_arn}: {e}")
        
        print(f"✅ Discovery complete!")
        return resources
        
    except Exception as e:
        print(f"❌ Error during resource discovery: {e}")
        return resources

def confirm_resources_to_cleanup(resources):
    """Display resources and confirm cleanup"""
    print("\n" + "=" * 60)
    print("🎯 TARGETED CLEANUP - Resources to be deleted:")
    print("=" * 60)
    
    # Knowledge Bases
    if resources['knowledge_bases']:
        print(f"\n📚 Knowledge Bases ({len(resources['knowledge_bases'])}):")
        for kb in resources['knowledge_bases']:
            print(f"  • {kb['name']} ({kb['id']})")
    else:
        print(f"\n📚 Knowledge Bases: None found")
    
    # S3 Buckets
    if resources['s3_buckets']:
        print(f"\n🗑️  S3 Buckets ({len(resources['s3_buckets'])}):")
        for bucket in sorted(resources['s3_buckets']):
            print(f"  • {bucket}")
    else:
        print(f"\n🗑️  S3 Buckets: None found")
    
    # OpenSearch Collections
    if resources['opensearch_collections']:
        print(f"\n🔍 OpenSearch Collections ({len(resources['opensearch_collections'])}):")
        for collection_arn in sorted(resources['opensearch_collections']):
            collection_name = collection_arn.split('/')[-1] if '/' in collection_arn else collection_arn
            print(f"  • {collection_name}")
    else:
        print(f"\n🔍 OpenSearch Collections: None found")
    
    # IAM Roles
    if resources['iam_roles']:
        print(f"\n👤 IAM Roles ({len(resources['iam_roles'])}):")
        for role_arn in sorted(resources['iam_roles']):
            role_name = role_arn.split('/')[-1]
            print(f"  • {role_name}")
    else:
        print(f"\n👤 IAM Roles: None found")
    
    # IAM Policies
    if resources['iam_policies']:
        print(f"\n📋 IAM Policies ({len(resources['iam_policies'])}):")
        for policy_arn in sorted(resources['iam_policies']):
            policy_name = policy_arn.split('/')[-1]
            print(f"  • {policy_name}")
    else:
        print(f"\n📋 IAM Policies: None found")
    
    print("\n" + "=" * 60)
    
    # Check if there's anything to clean up
    total_resources = (len(resources['knowledge_bases']) + 
                      len(resources['s3_buckets']) + 
                      len(resources['opensearch_collections']) + 
                      len(resources['iam_roles']) + 
                      len(resources['iam_policies']))
    
    if total_resources == 0:
        print("✅ No resources found to cleanup!")
        return False
    
    print(f"⚠️  This will delete {total_resources} resources in region: {region}")
    print("⚠️  This action cannot be undone!")
    
    # Get user confirmation
    while True:
        response = input("\nDo you want to proceed with cleanup? (yes/no): ").lower().strip()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            print("❌ Cleanup cancelled by user")
            return False
        else:
            print("Please enter 'yes' or 'no'")

def cleanup_targeted_knowledge_bases(resources):
    """Clean up targeted knowledge bases"""
    if not resources['knowledge_bases']:
        print("📚 No knowledge bases to cleanup")
        return
    
    print(f"🧹 Cleaning up {len(resources['knowledge_bases'])} Knowledge Bases...")
    
    for kb in resources['knowledge_bases']:
        kb_id = kb['id']
        kb_name = kb['name']
        print(f"  Deleting Knowledge Base: {kb_name} ({kb_id})")
        
        try:
            # Delete data sources first
            ds_response = bedrock_agent_client.list_data_sources(knowledgeBaseId=kb_id)
            for ds in ds_response.get('dataSourceSummaries', []):
                print(f"    Deleting Data Source: {ds['dataSourceId']}")
                bedrock_agent_client.delete_data_source(
                    knowledgeBaseId=kb_id,
                    dataSourceId=ds['dataSourceId']
                )
                time.sleep(2)
            
            # Delete the knowledge base
            bedrock_agent_client.delete_knowledge_base(knowledgeBaseId=kb_id)
            print(f"    ✅ Deleted Knowledge Base: {kb_name}")
            time.sleep(3)
            
        except Exception as e:
            print(f"    ❌ Error deleting knowledge base {kb_name}: {e}")
    
    print(f"✅ Cleaned up {len(resources['knowledge_bases'])} knowledge bases")

def cleanup_targeted_s3_buckets(resources):
    """Clean up targeted S3 buckets"""
    if not resources['s3_buckets']:
        print("🗑️  No S3 buckets to cleanup")
        return
    
    print(f"🗑️  Cleaning up {len(resources['s3_buckets'])} S3 Buckets...")
    
    for bucket_name in resources['s3_buckets']:
        print(f"  Deleting S3 bucket: {bucket_name}")
        
        try:
            # Delete all objects first
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
    
    print(f"✅ Cleaned up {len(resources['s3_buckets'])} S3 buckets")

def cleanup_targeted_opensearch_collections(resources):
    """Clean up targeted OpenSearch collections"""
    if not resources['opensearch_collections']:
        print("🔍 No OpenSearch collections to cleanup")
        return
    
    print(f"🔍 Cleaning up {len(resources['opensearch_collections'])} OpenSearch Collections...")
    
    for collection_arn in resources['opensearch_collections']:
        # Extract collection ID from ARN
        collection_id = collection_arn.split('/')[-1] if '/' in collection_arn else collection_arn
        collection_name = collection_id  # For display purposes
        
        print(f"  Deleting OpenSearch collection: {collection_name}")
        
        try:
            opensearch_client.delete_collection(id=collection_id)
            print(f"    ✅ Deleted collection: {collection_name}")
            time.sleep(2)
            
        except Exception as e:
            print(f"    ❌ Error deleting collection {collection_name}: {e}")
    
    print(f"✅ Cleaned up {len(resources['opensearch_collections'])} OpenSearch collections")

def cleanup_targeted_iam_roles(resources):
    """Clean up targeted IAM roles"""
    if not resources['iam_roles']:
        print("👤 No IAM roles to cleanup")
        return
    
    print(f"👤 Cleaning up {len(resources['iam_roles'])} IAM Roles...")
    
    for role_arn in resources['iam_roles']:
        role_name = role_arn.split('/')[-1]
        print(f"  Deleting IAM role: {role_name}")
        
        try:
            # Detach all managed policies
            attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)
            for policy in attached_policies['AttachedPolicies']:
                iam_client.detach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy['PolicyArn']
                )
            
            # Delete all inline policies
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
    
    print(f"✅ Cleaned up {len(resources['iam_roles'])} IAM roles")

def cleanup_targeted_iam_policies(resources):
    """Clean up targeted IAM policies"""
    if not resources['iam_policies']:
        print("📋 No IAM policies to cleanup")
        return
    
    print(f"📋 Cleaning up {len(resources['iam_policies'])} IAM Policies...")
    
    for policy_arn in resources['iam_policies']:
        policy_name = policy_arn.split('/')[-1]
        print(f"  Deleting IAM policy: {policy_name}")
        
        try:
            # Check if policy is still attached to other entities before deleting
            try:
                policy_details = iam_client.get_policy(PolicyArn=policy_arn)
                attachment_count = policy_details['Policy']['AttachmentCount']
                
                if attachment_count > 0:
                    print(f"    ⚠️  Policy {policy_name} is still attached to {attachment_count} entities, skipping")
                    continue
                    
            except Exception as e:
                print(f"    ⚠️  Could not check attachment count for {policy_name}: {e}")
            
            # Delete the policy
            iam_client.delete_policy(PolicyArn=policy_arn)
            print(f"    ✅ Deleted policy: {policy_name}")
            
        except Exception as e:
            print(f"    ❌ Error deleting policy {policy_name}: {e}")
    
    print(f"✅ Cleaned up {len(resources['iam_policies'])} IAM policies")

def main():
    print("🚀 Starting TARGETED CLEANUP")
    print("=" * 50)
    print("🎯 This script will only delete resources actually used by")
    print("   knowledge bases in the current region.")
    print("=" * 50)
    
    # Step 1: Discover resources
    resources = get_resources_to_cleanup()
    
    # Step 2: Confirm with user
    if not confirm_resources_to_cleanup(resources):
        return
    
    print("\n🚀 Starting cleanup process...")
    print("=" * 50)
    
    # Step 3: Clean up in order: KB -> S3 -> OpenSearch -> IAM
    cleanup_targeted_knowledge_bases(resources)
    print()
    cleanup_targeted_s3_buckets(resources)
    print()
    cleanup_targeted_opensearch_collections(resources)
    print()
    cleanup_targeted_iam_roles(resources)
    print()
    cleanup_targeted_iam_policies(resources)
    
    print("\n" + "=" * 50)
    print("🎉 TARGETED CLEANUP COMPLETE!")
    print("You can now run: uv run python create_knowledge_base.py")

if __name__ == '__main__':
    main()