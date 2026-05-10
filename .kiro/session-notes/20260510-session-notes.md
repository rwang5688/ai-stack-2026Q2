# Session Notes - May 10, 2026

## Session Overview
Created workshop4-phase1-monolithic-agents spec (requirements, design, tasks). Deployed CloudFormation infrastructure with S3 Vectors + Bedrock KB. Ran populate_seed_data.py successfully.

## Key Accomplishments
- Created full spec for Phase 1: requirements.md, design.md, tasks.md
- Deployed `student-services-infra` CloudFormation stack successfully
- Ran `populate_seed_data.py` — uploaded PDF to S3, seeded DynamoDB (9 reviews, 1 registration), triggered KB ingestion (1 doc indexed)
- All SSM parameters populated and verified

## CRITICAL LESSONS LEARNED

### ⚠️ WARNING: Reference code in `.kiro/references/workshop4/modules/module3/` is OUTDATED
- `knowledge_base.py` uses **OpenSearch Serverless** — DO NOT USE
- `create_knowledge_base.py` calls into `knowledge_base.py` which creates OSS collections — ALSO OUTDATED
- The reference code was NEVER updated to use S3 Vectors
- DO NOT reference this code for KB creation patterns

### ⚠️ WARNING: OpenSearch Serverless is EVIL
- Prohibitively expensive (up to 90% more than S3 Vectors)
- Takes forever to initialize OSS collections (minutes of waiting)
- S3 Vectors does the same job with subsecond query performance at a fraction of the cost
- NEVER use OpenSearch Serverless for workshop/demo purposes

### ✅ What WORKS: S3 Vectors via CloudFormation
The correct approach for Bedrock KB with S3 Vectors in CloudFormation:

1. `AWS::S3Vectors::VectorBucket` — creates the vector bucket (NOT a regular S3 bucket)
2. `AWS::S3Vectors::Index` — creates the vector index with:
   - `Dimension: 1024` (for amazon.titan-embed-text-v2:0)
   - `DistanceMetric: cosine`
   - `DataType: float32`
   - `MetadataConfiguration.NonFilterableMetadataKeys: ["AMAZON_BEDROCK_TEXT"]`
3. `AWS::Bedrock::KnowledgeBase` with `StorageConfiguration`:
   - `Type: S3_VECTORS`
   - `S3VectorsConfiguration.IndexArn: !GetAtt VectorsIndex.IndexArn`
   - **ONLY IndexArn** — do NOT include `VectorBucketArn` or `IndexName` (causes EarlyValidation failure)

4. IAM policy resource format for S3 Vectors:
   - `arn:aws:s3vectors:{REGION}:{ACCOUNT_ID}:bucket/{VECTOR_BUCKET_NAME}/index/{VECTOR_INDEX_NAME}`

5. Source: AWS Blog "Building cost-effective RAG applications with Amazon Bedrock Knowledge Bases and Amazon S3 Vectors" (July 17, 2025)

### ✅ CloudFormation deploy command
```bash
aws cloudformation deploy --stack-name student-services-infra --template-file cloudformation/student-services-infra.yaml --capabilities CAPABILITY_NAMED_IAM --region us-west-2
```
- Must use `CAPABILITY_NAMED_IAM` (not just `CAPABILITY_IAM`) because template has a named IAM role

### ✅ populate_seed_data.py works
- Reads CloudFormation stack outputs
- Uploads files to S3 with prefixes (`kb-datasource/`, `dynamodb/`)
- Seeds DynamoDB via `batch_write_item`
- Triggers KB ingestion via `bedrock-agent` API (stupid naming but that's where AWS put KB APIs)
- XGBoost endpoint is optional — skips if not provided

## Issues Encountered

### CloudFormation S3VectorsConfiguration validation failure
- **Issue**: `EarlyValidation::PropertyValidation` error when deploying
- **Root cause**: Including `VectorBucketArn` and `IndexName` in `S3VectorsConfiguration` — CloudFormation only wants `IndexArn`
- **Resolution**: Removed `VectorBucketArn` and `IndexName`, kept only `IndexArn: !GetAtt VectorsIndex.IndexArn`

### CAPABILITY_IAM vs CAPABILITY_NAMED_IAM
- **Issue**: `InsufficientCapabilitiesException` on first deploy
- **Root cause**: Template uses a named IAM role (`student-services-kb-role-${Region}`)
- **Resolution**: Changed to `--capabilities CAPABILITY_NAMED_IAM`

### Shell script chaos
- **Issue**: Multiple conflicting shell scripts created (`deploy.sh`, `seed.sh`, `seed-data.sh`, `infrastructure.sh`, `populate-seed-data.sh`)
- **Resolution**: Settled on two scripts with verb-leading names: `deploy-infra.sh` and `populate-seed-data.sh`

## Decisions Made
- Code-server is ONLY for: (1) commit and push to GitHub, (2) Docker builds
- GitBash is for: AWS CLI, shell scripts, Python scripts
- NEVER push to GitHub from Kiro without explicit permission
- When user says "checkpoint commit" — user handles it manually
- Shell scripts must have verb-leading names (e.g., `deploy-infra.sh`, `populate-seed-data.sh`)
- Files with `_old` suffix in references are deprecated garbage — ignore them

## Next Steps
- [ ] Provide XGBoost endpoint name to complete SSM setup
- [ ] Continue with Phase 1 tasks (shared utilities, specialist agents, orchestrator, Streamlit UI)
- [ ] Delete the deployed stack when done testing (to avoid costs)
