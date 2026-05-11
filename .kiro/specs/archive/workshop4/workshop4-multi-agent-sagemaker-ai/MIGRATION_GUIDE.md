# Migration Guide: Environment Variables → SSM Parameter Store

## Overview

The TeachAssist application has been refactored to use AWS Systems Manager Parameter Store instead of environment variables for all configuration (except AWS credentials and `TEACHASSIST_ENV`).

## Why This Change?

### Problems with Environment Variables
1. **Docker Rebuilds**: Changing endpoint names required rebuilding and redeploying containers
2. **Cost Optimization Friction**: Deleting/recreating SageMaker endpoints for cost savings was painful
3. **No Version History**: No way to track configuration changes over time
4. **Environment Confusion**: Mixing dev/staging/prod configurations was error-prone

### Benefits of SSM Parameter Store
1. ✅ **No Docker Rebuilds**: Update parameters without redeploying
2. ✅ **Cost Optimization**: Easily update endpoint names after recreation
3. ✅ **Version History**: Track all parameter changes
4. ✅ **Environment Separation**: Clean separation of dev/staging/prod
5. ✅ **Centralized Management**: Update via AWS Console, CLI, or CloudFormation
6. ✅ **Secure Storage**: Encrypt sensitive values with KMS

## Migration Steps

### Step 1: Deploy SSM Parameters

```bash
cd workshop4/ssm

# Deploy parameters for development environment
aws cloudformation create-stack \
  --stack-name teachassist-params-dev \
  --template-body file://teachassist-params.yaml \
  --parameters \
    ParameterKey=Environment,ParameterValue=dev \
    ParameterKey=BedrockModelId,ParameterValue=us.amazon.nova-2-lite-v1:0 \
    ParameterKey=StrandsKnowledgeBaseId,ParameterValue=YOUR_KB_ID \
    ParameterKey=SageMakerModelEndpoint,ParameterValue=YOUR_ENDPOINT_NAME \
    ParameterKey=SageMakerInferenceComponent,ParameterValue=YOUR_COMPONENT_NAME \
    ParameterKey=XGBoostEndpointName,ParameterValue=YOUR_XGBOOST_ENDPOINT

# Wait for completion
aws cloudformation wait stack-create-complete \
  --stack-name teachassist-params-dev
```

### Step 2: Update Environment Variable

**Before (many environment variables):**
```bash
export AWS_REGION="us-east-1"
export BEDROCK_MODEL_ID="us.amazon.nova-2-lite-v1:0"
export SAGEMAKER_MODEL_ENDPOINT="my-endpoint"
export SAGEMAKER_INFERENCE_COMPONENT="adapter-xyz"
export XGBOOST_ENDPOINT_NAME="xgboost-endpoint"
export STRANDS_KNOWLEDGE_BASE_ID="kb-id"
export STRANDS_MODEL_PROVIDER="bedrock"
export MAX_RESULTS="9"
export MIN_SCORE="0.000001"
```

**After (single environment variable):**
```bash
export TEACHASSIST_ENV=dev
```

That's it! All other configuration comes from SSM Parameter Store.

### Step 3: Test the Application

```bash
# Set environment
export TEACHASSIST_ENV=dev

# Run application
cd workshop4/multi_agent
streamlit run app.py
```

The application will automatically fetch all configuration from SSM Parameter Store.

## Parameter Mapping

| Old Environment Variable | New SSM Parameter Path |
|-------------------------|------------------------|
| `AWS_REGION` | `/teachassist/{env}/aws/region` |
| `BEDROCK_MODEL_ID` | `/teachassist/{env}/bedrock/model_id` |
| `STRANDS_MODEL_PROVIDER` | `/teachassist/{env}/strands/model_provider` |
| `SAGEMAKER_MODEL_ENDPOINT` | `/teachassist/{env}/sagemaker/model_endpoint` |
| `SAGEMAKER_INFERENCE_COMPONENT` | `/teachassist/{env}/sagemaker/inference_component` |
| `XGBOOST_ENDPOINT_NAME` | `/teachassist/{env}/xgboost/endpoint_name` |
| `STRANDS_KNOWLEDGE_BASE_ID` | `/teachassist/{env}/strands/knowledge_base_id` |
| `MAX_RESULTS` | `/teachassist/{env}/knowledge_base/max_results` |
| `MIN_SCORE` | `/teachassist/{env}/knowledge_base/min_score` |

## Updating Configuration

### Update a Single Parameter

```bash
# Update SageMaker endpoint after recreation
aws ssm put-parameter \
  --name "/teachassist/dev/sagemaker/model_endpoint" \
  --value "new-endpoint-name-1234567890" \
  --overwrite

# Update inference component
aws ssm put-parameter \
  --name "/teachassist/dev/sagemaker/inference_component" \
  --value "adapter-new-1234567890" \
  --overwrite
```

**No application restart needed!** Changes take effect on next request (parameters are cached per request).

### Update Multiple Parameters via CloudFormation

```bash
# Update the stack with new parameter values
aws cloudformation update-stack \
  --stack-name teachassist-params-dev \
  --template-body file://teachassist-params.yaml \
  --parameters \
    ParameterKey=SageMakerModelEndpoint,ParameterValue=new-endpoint-name \
    ParameterKey=SageMakerInferenceComponent,ParameterValue=new-component-name
```

## Cost Optimization Workflow

### Before (with Environment Variables)
1. Delete SageMaker endpoint to save costs
2. Update environment variables in code
3. Rebuild Docker image
4. Redeploy application
5. Wait for deployment to complete
6. **Total time: 10-15 minutes**

### After (with SSM Parameter Store)
1. Delete SageMaker endpoint to save costs
2. Update SSM parameter: `aws ssm put-parameter --name /teachassist/dev/sagemaker/model_endpoint --value new-name --overwrite`
3. **Total time: 10 seconds**

## Multiple Environments

Deploy separate parameter stacks for each environment:

```bash
# Development
aws cloudformation create-stack \
  --stack-name teachassist-params-dev \
  --template-body file://teachassist-params.yaml \
  --parameters ParameterKey=Environment,ParameterValue=dev

# Staging
aws cloudformation create-stack \
  --stack-name teachassist-params-staging \
  --template-body file://teachassist-params.yaml \
  --parameters ParameterKey=Environment,ParameterValue=staging

# Production
aws cloudformation create-stack \
  --stack-name teachassist-params-prod \
  --template-body file://teachassist-params.yaml \
  --parameters ParameterKey=Environment,ParameterValue=prod
```

Switch between environments by changing `TEACHASSIST_ENV`:

```bash
# Use development parameters
export TEACHASSIST_ENV=dev

# Use production parameters
export TEACHASSIST_ENV=prod
```

## IAM Permissions

The application needs these IAM permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:GetParameters",
        "ssm:GetParametersByPath"
      ],
      "Resource": "arn:aws:ssm:*:*:parameter/teachassist/*"
    }
  ]
}
```

## Troubleshooting

### Error: "Parameter not found in SSM Parameter Store"

**Cause**: Parameters haven't been deployed for the current environment.

**Solution**:
```bash
# Check current environment
echo $TEACHASSIST_ENV

# Deploy parameters
aws cloudformation create-stack \
  --stack-name teachassist-params-$TEACHASSIST_ENV \
  --template-body file://workshop4/ssm/teachassist-params.yaml \
  --parameters ParameterKey=Environment,ParameterValue=$TEACHASSIST_ENV
```

### Error: "Access Denied" when fetching parameters

**Cause**: IAM role/user lacks SSM permissions.

**Solution**: Add the IAM policy shown above to your role/user.

### Parameters not updating

**Cause**: Parameters are cached for the lifetime of the Python process.

**Solution**: Restart the application to pick up new parameter values.

## Rollback

If you need to rollback to environment variables temporarily:

1. The old environment variable approach is no longer supported
2. You must use SSM Parameter Store
3. For local development, deploy a "dev" parameter stack with default values

## Benefits Summary

| Aspect | Environment Variables | SSM Parameter Store |
|--------|----------------------|---------------------|
| Configuration Changes | Rebuild + Redeploy | Update parameter |
| Time to Update | 10-15 minutes | 10 seconds |
| Version History | None | Full history |
| Environment Separation | Manual | Automatic |
| Cost Optimization | Painful | Easy |
| Secrets Management | Exposed | Encrypted |
| Audit Trail | None | CloudTrail logs |

## Next Steps

1. Deploy SSM parameters for your environment
2. Set `TEACHASSIST_ENV` environment variable
3. Remove old environment variable exports from `.bashrc`
4. Test the application
5. Enjoy hassle-free configuration management!
