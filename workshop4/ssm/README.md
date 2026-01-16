# TeachAssist SSM Parameter Store Configuration

This directory contains CloudFormation templates for deploying application configuration to AWS Systems Manager Parameter Store.

## Why SSM Parameter Store?

Using SSM Parameter Store instead of environment variables provides several benefits:

1. **No Docker Rebuilds**: Update configuration without rebuilding containers
2. **Environment Separation**: Different parameters for dev/staging/prod
3. **Centralized Management**: Update parameters via AWS Console or CLI
4. **Version History**: Track parameter changes over time
5. **Secure Storage**: Encrypt sensitive values with KMS

## Quick Start

### 1. Deploy Parameters (First Time)

```bash
# Deploy with default values for development
aws cloudformation create-stack \
  --stack-name teachassist-params-dev \
  --template-body file://teachassist-params.yaml \
  --parameters ParameterKey=Environment,ParameterValue=dev

# Wait for stack creation to complete
aws cloudformation wait stack-create-complete \
  --stack-name teachassist-params-dev
```

### 2. Customize Parameters

Edit the CloudFormation template or provide parameter overrides:

```bash
# Deploy with custom values
aws cloudformation create-stack \
  --stack-name teachassist-params-dev \
  --template-body file://teachassist-params.yaml \
  --parameters \
    ParameterKey=Environment,ParameterValue=dev \
    ParameterKey=BedrockModelId,ParameterValue=us.amazon.nova-pro-v1:0 \
    ParameterKey=StrandsKnowledgeBaseId,ParameterValue=IMW46CITZE \
    ParameterKey=SageMakerModelEndpoint,ParameterValue=my-gpt-oss-20b-1-1768457329 \
    ParameterKey=SageMakerInferenceComponent,ParameterValue=adapter-my-gpt-oss-20b-1-1768457329-1768457350 \
    ParameterKey=XGBoostEndpointName,ParameterValue=xgboost-serverless-ep2026-01-12-05-31-16
```

### 3. Update Parameters

```bash
# Update existing stack with new values
aws cloudformation update-stack \
  --stack-name teachassist-params-dev \
  --template-body file://teachassist-params.yaml \
  --parameters \
    ParameterKey=SageMakerModelEndpoint,ParameterValue=new-endpoint-name

# Wait for update to complete
aws cloudformation wait stack-update-complete \
  --stack-name teachassist-params-dev
```

### 4. View Parameters

```bash
# List all parameters for an environment
aws ssm get-parameters-by-path \
  --path "/teachassist/dev" \
  --recursive

# Get a specific parameter
aws ssm get-parameter \
  --name "/teachassist/dev/sagemaker/model_endpoint"
```

## Parameter Structure

All parameters follow this naming convention:
```
/teachassist/{environment}/{category}/{parameter_name}
```

### Available Parameters

| Parameter Path | Description | Default Value |
|---------------|-------------|---------------|
| `/teachassist/{env}/aws/region` | AWS region for all services | `us-east-1` |
| `/teachassist/{env}/bedrock/model_id` | Bedrock model ID | `us.amazon.nova-2-lite-v1:0` |
| `/teachassist/{env}/strands/model_provider` | Model provider (bedrock/sagemaker) | `bedrock` |
| `/teachassist/{env}/sagemaker/model_endpoint` | SageMaker model endpoint name | `my-llm-endpoint` |
| `/teachassist/{env}/sagemaker/inference_component` | SageMaker inference component | `my-llm-inference-component` |
| `/teachassist/{env}/xgboost/endpoint_name` | XGBoost endpoint name | `my-xgboost-endpoint` |
| `/teachassist/{env}/strands/knowledge_base_id` | Strands knowledge base ID | `my-kb-id` |
| `/teachassist/{env}/knowledge_base/max_results` | Max KB query results | `9` |
| `/teachassist/{env}/knowledge_base/min_score` | Min KB query score | `0.000001` |

## Environment Configuration

The application reads the environment from the `TEACHASSIST_ENV` environment variable:

```bash
# Set environment (only env var needed!)
export TEACHASSIST_ENV=dev

# Application will read from /teachassist/dev/* parameters
python app.py
```

## Multiple Environments

Deploy separate stacks for each environment:

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

## Cost Optimization: Ephemeral SageMaker Endpoints

If you're deleting and recreating SageMaker endpoints to save costs, simply update the parameter:

```bash
# Update endpoint name after recreating endpoint
aws ssm put-parameter \
  --name "/teachassist/dev/sagemaker/model_endpoint" \
  --value "new-endpoint-name-1234567890" \
  --overwrite

# Update inference component
aws ssm put-parameter \
  --name "/teachassist/dev/sagemaker/inference_component" \
  --value "adapter-new-endpoint-1234567890" \
  --overwrite
```

**No Docker rebuild or redeployment needed!** The application will pick up the new values on next request.

## Cleanup

```bash
# Delete the CloudFormation stack (removes all parameters)
aws cloudformation delete-stack \
  --stack-name teachassist-params-dev

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete \
  --stack-name teachassist-params-dev
```

## IAM Permissions Required

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

### Parameters Not Found

```bash
# Verify stack exists
aws cloudformation describe-stacks --stack-name teachassist-params-dev

# List all parameters
aws ssm get-parameters-by-path --path "/teachassist/dev" --recursive
```

### Permission Denied

Ensure your IAM role/user has `ssm:GetParameter` permissions for `/teachassist/*` parameters.

### Wrong Environment

Check the `TEACHASSIST_ENV` environment variable:

```bash
echo $TEACHASSIST_ENV
```

## Best Practices

1. **Use CloudFormation**: Always deploy parameters via CloudFormation for version control
2. **Tag Parameters**: All parameters are tagged with Environment and Application
3. **Separate Environments**: Use different stacks for dev/staging/prod
4. **Document Changes**: Use CloudFormation change sets to review updates
5. **Backup**: CloudFormation templates serve as configuration backup

## Next Steps

After deploying parameters:

1. Set `TEACHASSIST_ENV` environment variable
2. Run the application - it will automatically fetch parameters
3. Update parameters as needed without redeploying the application
