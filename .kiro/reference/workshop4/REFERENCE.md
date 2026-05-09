# Reference Guide

Comprehensive troubleshooting, cross-platform compatibility, authentication details, and technical reference for Workshop 4.

## Table of Contents

- [Cross-Platform Compatibility](#cross-platform-compatibility)
- [Authentication Analysis](#authentication-analysis)
- [Application Merge Guide](#application-merge-guide)
- [Troubleshooting](#troubleshooting)
- [AWS Configuration](#aws-configuration)
- [Environment Variables](#environment-variables)
- [Known Issues](#known-issues)
- [Performance Optimization](#performance-optimization)
- [Security Considerations](#security-considerations)

## Cross-Platform Compatibility

### Platform Requirements

**Python Version Requirements:**
- **Recommended**: Python 3.12.x or 3.13.x for optimal experience
- **Cross-Platform Consistency**: Same versions work


## Known Issues

### Model Provider Limitations

#### SageMaker Model Tool Calling - Model Version Specific Limitation

**Issue**: Some SageMaker model versions have **incompatible tool-calling implementations** with the multi-agent system.

**Confirmed Model Compatibility**:
- ✅ **Mistral Small 3 24b Instruct (2501)** - Works correctly with tool calling
- ❌ **Mistral Small 3.2 24b Instruct (2506)** - Does NOT work with tool calling (returns empty responses)

**Symptoms** (when using incompatible models):
- Empty responses when using SageMaker models
- Error message: "The selected model returned an empty response"
- Bedrock models work fine with the same code

**Root Cause**: 
The teacher agent architecture requires reliable tool calling to route queries to specialized assistants (`math_assistant`, `english_assistant`, `computer_science_assistant`, etc.). Some SageMaker model versions (like Mistral Small 3.2) don't return content when making these tool calls, resulting in empty `AgentResult` objects with `message['content'] = []`.

**Affected Modes** (for incompatible models):
- **Auto-Route Mode**: ❌ Fails - requires tool calling for routing decisions
- **Teacher Agent Mode**: ❌ Fails - requires tool calling for specialized assistants  
- **Knowledge Base Mode**: ✅ Works - doesn't require specialized assistant tools

**Workaround Options**:
1. **Use Compatible SageMaker Models**: Deploy Mistral Small 3 (2501) Instruct or test other model versions
2. **Use Bedrock Models**: Switch to Amazon Nova or Claude models which have reliable tool-calling support
3. **Use Knowledge Base Mode**: If you only need knowledge base operations, this mode works with all models
4. **Test Before Deploying**: Always test new SageMaker model versions with tool calling before production use

**Recommended Models**:
- ✅ **Amazon Nova 2 Lite** - Fast, reliable, cost-effective
- ✅ **Amazon Nova Pro** - Balanced performance
- ✅ **Claude Haiku 4.5** - Advanced reasoning
- ✅ **Claude Sonnet 4.5** - Best for complex tasks
- ✅ **Mistral Small 3 (2501) Instruct** - Works with SageMaker
- ❌ **Mistral Small 3.2 (2506) Instruct** - Incompatible tool calling

**Technical Details**:
```python
# When incompatible SageMaker model fails, the response looks like:
AgentResult(
    stop_reason='end_turn',
    message={'role': 'assistant', 'content': []},  # Empty!
    metrics=EventLoopMetrics(...)
)

# Compatible models (Bedrock or Mistral Small 3 2501) return proper content:
AgentResult(
    stop_reason='end_turn', 
    message={'role': 'assistant', 'content': [{'text': '...response...'}]},
    metrics=EventLoopMetrics(...)
)
```

**Code Location**:
- `workshop4/multi_agent/app.py` - Lines ~620-670 (response extraction logic)
- `workshop4/deploy_multi_agent/docker_app/app.py` - Lines ~670-720

**Future Considerations**:
- Always test new SageMaker model versions with tool calling before production deployment
- Monitor Strands Agents SDK updates for improved SageMaker compatibility
- Consider maintaining a list of tested/compatible SageMaker models
- Newer model versions may have different tool-calling implementations

#### use_agent Tool - Bedrock Only Support

**Issue**: The `use_agent` tool from `strands_tools` only supports the "bedrock" model provider, not "sagemaker".

**Impact**: When using SageMaker models as the main agent model, the application uses Bedrock models for internal routing decisions.

**Affected Functionality**:
- **Auto-Route Mode**: Query classification (teacher vs knowledge base)
- **Knowledge Base Operations**: Action determination (store vs retrieve) and answer generation

**Implementation Details**:
The application uses `use_agent` for three internal operations:
1. `determine_action()` - Routes queries to teacher agent or knowledge base
2. `determine_kb_action()` - Determines store vs retrieve for knowledge base queries  
3. `run_kb_agent()` - Generates conversational answers from knowledge base results

**Workaround**: 
All `use_agent` calls use `bedrock` provider with `us.amazon.nova-2-lite-v1:0` model, regardless of the user's selected model. This is acceptable because:
- These are simple classification tasks that don't require advanced model capabilities
- Using a lightweight Bedrock model for routing is more cost-effective
- The user's selected model (SageMaker or Bedrock) is still used for actual teacher agent responses
- No functional impact on end-user experience

**Code Location**:
- `workshop4/multi_agent/app.py` - Lines ~400-550
- `workshop4/deploy_multi_agent/docker_app/app.py` - Lines ~420-570

**Example**:
```python
# Always use bedrock for use_agent calls
model_settings = {
    'model_id': 'us.amazon.nova-2-lite-v1:0',
    'temperature': TEMPERATURE
}

result = agent.tool.use_agent(
    prompt=f"Query: {query}",
    system_prompt=ACTION_DETERMINATION_PROMPT,
    model_provider="bedrock",  # Always bedrock, not sagemaker
    model_settings=model_settings
)
```

**Future Considerations**:
If `strands_tools` adds SageMaker support to `use_agent`, the code can be updated to use the user's selected model for all operations.

## AWS Configuration

### SSM Parameter Store

The application uses AWS Systems Manager Parameter Store for centralized configuration management.

**Parameter Path**: `/teachers_assistant/{environment}/`

**Required Parameters**:
- `bedrock_custom_model_deployment_arn` - ARN for Bedrock custom model deployments
- `default_model_id` - Default Bedrock model ID
- `max_results` - Maximum results for knowledge base queries
- `min_score` - Minimum score threshold for knowledge base queries
- `sagemaker_model_endpoint` - SageMaker endpoint name
- `sagemaker_model_inference_component` - SageMaker inference component (optional)
- `temperature` - Model temperature setting
- `xgboost_model_endpoint` - XGBoost endpoint for loan predictions

**Deployment**:
```bash
cd workshop4/ssm
aws cloudformation create-stack \
  --stack-name teachers-assistant-params-dev \
  --template-body file://teachers-assistant-params.yaml \
  --parameters ParameterKey=Environment,ParameterValue=dev
```

## Environment Variables

### Required Environment Variables

**TEACHERS_ASSISTANT_ENV**
- Description: Environment name (dev, staging, prod)
- Default: `dev`
- Used for: SSM parameter path construction

**AWS_REGION**
- Description: AWS region for all services
- Default: `us-east-1`
- Used for: Bedrock, SageMaker, SSM clients

**STRANDS_KNOWLEDGE_BASE_ID**
- Description: Bedrock Knowledge Base ID for memory operations
- Default: `my-bedrock-knowledge-base-id`
- Required: Yes (must be set before starting application)
- Note: Framework requirement - must be environment variable, not SSM parameter

### Setting Environment Variables

**Linux/macOS**:
```bash
export TEACHERS_ASSISTANT_ENV=dev
export AWS_REGION=us-east-1
export STRANDS_KNOWLEDGE_BASE_ID=IMW46CITZE
```

**Windows (PowerShell)**:
```powershell
$env:TEACHERS_ASSISTANT_ENV="dev"
$env:AWS_REGION="us-east-1"
$env:STRANDS_KNOWLEDGE_BASE_ID="IMW46CITZE"
```

**Windows (CMD)**:
```cmd
set TEACHERS_ASSISTANT_ENV=dev
set AWS_REGION=us-east-1
set STRANDS_KNOWLEDGE_BASE_ID=IMW46CITZE
```

## Troubleshooting

### Common Issues

#### "Unknown model provider: sagemaker" Error

**Symptom**: Error message when selecting SageMaker model in dropdown

**Cause**: `use_agent` tool only supports "bedrock" provider

**Solution**: This has been fixed in the application code. All `use_agent` calls now use bedrock provider. See [Known Issues](#model-provider-limitations) for details.

#### SSM Parameter Not Found

**Symptom**: Error retrieving parameters from SSM Parameter Store

**Cause**: CloudFormation stack not deployed or parameters not created

**Solution**:
1. Deploy CloudFormation stack: `cd workshop4/ssm && aws cloudformation create-stack ...`
2. Verify parameters: `python workshop4/validate/validate_ssm_parameters.py`
3. Check environment variable: `echo $TEACHERS_ASSISTANT_ENV`

#### Bedrock Custom Model Deployment Validation Skipped

**Symptom**: Validation shows "SKIPPED" for custom model deployment

**Cause**: Parameter still has placeholder value `my-bedrock-custom-model-deployment-arn`

**Solution**: Update SSM parameter with actual ARN:
```bash
aws ssm put-parameter \
  --name '/teachers_assistant/dev/bedrock_custom_model_deployment_arn' \
  --value 'arn:aws:bedrock:us-east-1:123456789012:custom-model-deployment/abc123' \
  --overwrite
```

## Performance Optimization

### Model Selection Guidelines

**For Educational Queries**:
- **Lightweight**: Amazon Nova 2 Lite - Fast, cost-effective for simple queries
- **Balanced**: Amazon Nova Pro - Good balance of speed and capability
- **Advanced**: Claude Sonnet 4.5 - Best for complex reasoning

**For Knowledge Base Operations**:
- Internal routing always uses Nova 2 Lite (hardcoded for efficiency)
- User-selected model only affects teacher agent responses

**For SageMaker Models**:
- Ensure model supports OpenAI-compatible chat completion API
- Verify tool calling capabilities if using specialized assistants
- Consider inference component for multi-model endpoints

## Security Considerations

### IAM Permissions

**Required Permissions**:
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
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/*",
        "arn:aws:bedrock:*:*:custom-model-deployment/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:InvokeEndpoint"
      ],
      "Resource": "arn:aws:sagemaker:*:*:endpoint/*"
    }
  ]
}
```

### Best Practices

1. **Use IAM Roles**: Prefer IAM roles over access keys for EC2/ECS deployments
2. **Least Privilege**: Grant only necessary permissions
3. **Parameter Encryption**: Use SecureString for sensitive SSM parameters
4. **Network Security**: Deploy in private subnets with VPC endpoints for AWS services
5. **Audit Logging**: Enable CloudTrail for API call auditing
