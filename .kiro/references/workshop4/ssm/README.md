# Teacher's Assistant SSM Parameter Store Configuration

This directory contains CloudFormation templates for deploying application configuration to AWS Systems Manager Parameter Store.

## Why SSM Parameter Store?

Using SSM Parameter Store instead of environment variables provides several benefits:

1. **No Docker Rebuilds**: Update configuration without rebuilding containers
2. **Environment Separation**: Different parameters for dev/staging/prod
3. **Centralized Management**: Update parameters via AWS Console or CLI
4. **Version History**: Track parameter changes over time
5. **Secure Storage**: Encrypt sensitive values with KMS

## Quick Start

### 1. Deploy Parameters with Placeholder Defaults

**Important**: Deploy the CloudFormation template "as is" with the generic placeholder defaults. You'll customize the actual values afterward using AWS Console or CLI.

```bash
# Deploy with placeholder defaults for development
aws cloudformation create-stack \
  --stack-name teachers-assistant-params-dev \
  --template-body file://teachers-assistant-params.yaml \
  --parameters ParameterKey=Environment,ParameterValue=dev

# Wait for stack creation to complete
aws cloudformation wait stack-create-complete \
  --stack-name teachers-assistant-params-dev
```

### 2. Update Parameter Values

After deployment, update the parameter values with your actual AWS resource names.

**Using AWS Console**:
1. Navigate to AWS Systems Manager → Parameter Store
2. Find parameters under `/teachers_assistant/dev/`
3. Click on each parameter and update its value
4. Click "Save changes"

**Using AWS CLI**:
```bash
# Update SageMaker model endpoint
aws ssm put-parameter \
  --name "/teachers_assistant/dev/sagemaker_model_endpoint" \
  --value "your-actual-endpoint-name" \
  --overwrite

# Update SageMaker model inference component (if using multi-model endpoints)
aws ssm put-parameter \
  --name "/teachers_assistant/dev/sagemaker_model_inference_component" \
  --value "your-actual-inference-component-name" \
  --overwrite

# Update strands knowledge base ID
aws ssm put-parameter \
  --name "/teachers_assistant/dev/strands_knowledge_base_id" \
  --value "your-actual-knowledge-base-id" \
  --overwrite

# Update XGBoost model endpoint
aws ssm put-parameter \
  --name "/teachers_assistant/dev/xgboost_model_endpoint" \
  --value "your-actual-xgboost-endpoint-name" \
  --overwrite
```

### 3. View Parameters

```bash
# List all parameters for an environment
aws ssm get-parameters-by-path \
  --path "/teachers_assistant/dev" \
  --recursive

# Get a specific parameter
aws ssm get-parameter \
  --name "/teachers_assistant/dev/sagemaker_model_endpoint"
```

## Why Not Use CloudFormation Stack Updates?

**CloudFormation stack updates cannot be used to change parameter values** because:

1. Changing CloudFormation **input parameter values** alone doesn't trigger SSM resource updates
2. The SSM parameter values are set at stack **creation time** via `Value: !Ref`
3. Only changes to **resource configurations** trigger CloudFormation updates
4. To change values, you must update SSM parameters directly (not via CloudFormation)

**Example**: If you change `SageMakerModelEndpoint` input parameter from `my-sagemaker-model-endpoint` to `new-endpoint-name` and run `aws cloudformation update-stack`, the SSM parameter value will **not** change because the resource configuration (`ParamSageMakerModelEndpoint`) hasn't changed.

## Parameter Structure

All parameters follow this single-level naming convention:
```
/teachers_assistant/{environment}/{parameter_name}
```

### Available Parameters

| Parameter Path | Description | Default Value |
|---------------|-------------|---------------|
| `/teachers_assistant/{env}/default_model_id` | Default model ID | `us.amazon.nova-2-lite-v1:0` |
| `/teachers_assistant/{env}/max_results` | Max KB query results | `9` |
| `/teachers_assistant/{env}/min_score` | Min KB query score | `0.000001` |
| `/teachers_assistant/{env}/sagemaker_model_endpoint` | SageMaker model endpoint name | `my-sagemaker-model-endpoint` |
| `/teachers_assistant/{env}/sagemaker_model_inference_component` | SageMaker model inference component | `my-sagemaker-model-inference-component` |
| `/teachers_assistant/{env}/strands_knowledge_base_id` | Strands knowledge base ID (Framework requirement) | `my-strands-knowledge-base-id` |
| `/teachers_assistant/{env}/temperature` | Model temperature setting | `0.3` |
| `/teachers_assistant/{env}/xgboost_model_endpoint` | XGBoost model endpoint name | `my-xgboost-model-endpoint` |

### Environment Variables

| Environment Variable | Description | Default Value |
|---------------------|-------------|---------------|
| `TEACHERS_ASSISTANT_ENV` | Environment name (dev, staging, prod) | `dev` |
| `AWS_REGION` | AWS region for all services | `us-east-1` |

**Note**: `AWS_REGION` is a standard AWS SDK environment variable. In EC2/ECS deployments, this is automatically set from instance metadata.

## Environment Configuration

The application reads configuration from two sources:

1. **Environment Variables**:
   - `TEACHERS_ASSISTANT_ENV`: Determines which SSM parameter path to use (dev, staging, prod)
   - `AWS_REGION`: AWS region for all AWS service calls

2. **SSM Parameter Store**: All other configuration parameters

```bash
# Set environment variables
export TEACHERS_ASSISTANT_ENV=dev
export AWS_REGION=us-east-1

# Application will read from /teachers_assistant/dev/* parameters
python app.py
```

## Multiple Environments

Deploy separate stacks for each environment:

```bash
# Development
aws cloudformation create-stack \
  --stack-name teachers-assistant-params-dev \
  --template-body file://teachers-assistant-params.yaml \
  --parameters ParameterKey=Environment,ParameterValue=dev

# Staging
aws cloudformation create-stack \
  --stack-name teachers-assistant-params-staging \
  --template-body file://teachers-assistant-params.yaml \
  --parameters ParameterKey=Environment,ParameterValue=staging

# Production
aws cloudformation create-stack \
  --stack-name teachers-assistant-params-prod \
  --template-body file://teachers-assistant-params.yaml \
  --parameters ParameterKey=Environment,ParameterValue=prod
```

## Cost Optimization: Ephemeral SageMaker Endpoints

If you're deleting and recreating SageMaker endpoints to save costs, simply update the parameter:

```bash
# Update endpoint name after recreating endpoint
aws ssm put-parameter \
  --name "/teachers_assistant/dev/sagemaker_model_endpoint" \
  --value "new-endpoint-name-1234567890" \
  --overwrite

# Update inference component
aws ssm put-parameter \
  --name "/teachers_assistant/dev/sagemaker_model_inference_component" \
  --value "adapter-new-endpoint-1234567890" \
  --overwrite
```

**No Docker rebuild or redeployment needed!** The application will pick up the new values on next request.

## Cleanup

```bash
# Delete the CloudFormation stack (removes all parameters)
aws cloudformation delete-stack \
  --stack-name teachers-assistant-params-dev

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete \
  --stack-name teachers-assistant-params-dev
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
      "Resource": "arn:aws:ssm:*:*:parameter/teachers_assistant/*"
    }
  ]
}
```

## Troubleshooting

### Parameters Not Found

```bash
# Verify stack exists
aws cloudformation describe-stacks --stack-name teachers-assistant-params-dev

# List all parameters
aws ssm get-parameters-by-path --path "/teachers_assistant/dev" --recursive
```

### Permission Denied

Ensure your IAM role/user has `ssm:GetParameter` permissions for `/teachers_assistant/*` parameters.

### Wrong Environment

Check the `TEACHERS_ASSISTANT_ENV` environment variable:

```bash
echo $TEACHERS_ASSISTANT_ENV
```

## Best Practices

1. **Deploy Once**: Deploy CloudFormation template once with placeholder defaults
2. **Update via SSM**: Update actual values directly in SSM Parameter Store (not via CloudFormation)
3. **Tag Parameters**: All parameters are tagged with Environment and Application
4. **Separate Environments**: Use different stacks for dev/staging/prod
5. **Document Changes**: Keep track of parameter value changes in your documentation

## Next Steps

After deploying parameters:

1. Update parameter values with your actual AWS resource names (via Console or CLI)
2. Set `TEACHERS_ASSISTANT_ENV` environment variable
3. Run the application - it will automatically fetch parameters from SSM
4. Update parameters as needed without redeploying the application
