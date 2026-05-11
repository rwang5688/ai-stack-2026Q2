# Design Document: Workshop4 Multi-Agent Model Selection

## Overview

This design enhances the workshop4 multi-agent application's model selection capabilities by adding support for Bedrock Custom Model Deployment and improving the SageMaker model display. The feature enables users to select and use custom-trained Bedrock models via ARN while providing clearer visibility into which specific models are being used.

The implementation follows the existing architecture pattern of SSM Parameter Store for configuration management, Streamlit for UI, and the Strands Agents SDK for model integration. Changes are minimal and focused on extending the existing model selection dropdown and configuration module.

## Architecture

### System Context

The workshop4 multi-agent application is a Streamlit-based educational assistant that routes queries to specialized agents (Math, English, Language, Computer Science, Loan Offering, General) based on the query content. The application supports multiple model providers (Bedrock and SageMaker) with configuration managed through AWS Systems Manager Parameter Store.

### Component Interaction

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI Layer                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Model Selection Dropdown                              │ │
│  │  - Amazon Nova Pro (us.amazon.nova-pro-v1:0)           │ │
│  │  - Amazon Nova 2 Lite (us.amazon.nova-2-lite-v1:0)     │ │
│  │  - Anthropic Claude Haiku 4.5 (us.anthropic...)        │ │
│  │  - Anthropic Claude Sonnet 4.5 (us.anthropic...)       │ │
│  │  - Bedrock Custom Model Deployment (ARN)  ← NEW        │ │
│  │  - SageMaker Model (endpoint-name)        ← IMPROVED   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Configuration Layer                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  config.py Module                                      │ │
│  │  - get_bedrock_custom_model_deployment_arn()      ← NEW        │ │
│  │  - get_sagemaker_model_endpoint()                      │ │
│  │  - get_sagemaker_model_inference_component()           │ │
│  │  - Other configuration getters                         │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              AWS Systems Manager Parameter Store             │
│  /teachers_assistant/{environment}/                          │
│  - bedrock-custom-model-deployment-arn            ← NEW             │
│  - sagemaker_model_endpoint                                  │
│  - sagemaker_model_inference_component                       │
│  - default_model_id                                          │
│  - temperature                                               │
│  - Other parameters                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Model Creation Layer                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  bedrock_model.py                                      │ │
│  │  - create_bedrock_model(model_id, temperature)         │ │
│  │  - Accepts ARN as model_id                ← ENHANCED   │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  sagemaker_model.py                                    │ │
│  │  - create_sagemaker_model(endpoint, component, ...)    │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Strands Agents SDK                         │
│  - BedrockModel (accepts ARN as model_id)                    │
│  - SageMakerAIModel                                          │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **ARN as Model ID**: Bedrock Custom Model Deployments use an ARN as the model identifier. The existing `create_bedrock_model()` function will accept ARNs in addition to standard model IDs. The BedrockModel class from Strands Agents SDK already supports this pattern.

2. **Dynamic Dropdown Labels**: Model selection dropdown labels will be dynamically generated to include the actual ARN or endpoint name, providing immediate visibility to users about which specific model they're using.

3. **Minimal Code Changes**: The implementation extends existing patterns rather than introducing new abstractions. The model_options dictionary structure remains unchanged, only the display labels and values are enhanced.

4. **Configuration Consistency**: Both local development (multi_agent/app.py) and deployed (deploy_multi_agent/docker_app/app.py) versions will receive identical changes to maintain feature parity.

## Components and Interfaces

### 1. CloudFormation Template Enhancement

**File**: `workshop4/ssm/teachers-assistant-params.yaml`

**Changes**:
- Add new parameter `BedrockCustomModelDeploymentArn` with default value `my-bedrock-custom-model-deployment-arn`
- Add parameter description explaining its purpose
- Add corresponding SSM Parameter resource `ParamBedrockCustomModelDeploymentArn`
- Add output `BedrockCustomModelDeploymentArnParameter` for reference

**Parameter Structure**:
```yaml
Parameters:
  BedrockCustomModelDeploymentArn:
    Type: String
    Default: my-bedrock-custom-model-deployment-arn
    Description: Amazon Resource Name (ARN) for Bedrock Custom Model Deployment

Resources:
  ParamBedrockCustomModelDeploymentArn:
    Type: AWS::SSM::Parameter
    Properties:
      Name: !Sub '/teachers_assistant/${Environment}/bedrock_custom_model_deployment_arn'
      Description: ARN for Bedrock Custom Model Deployment
      Type: String
      Value: !Ref BedrockCustomModelDeploymentArn
      Tags:
        Environment: !Ref Environment
        Application: TeacherAssistant
        ManagedBy: CloudFormation
```

### 2. Configuration Module Enhancement

**File**: `workshop4/deploy_multi_agent/docker_app/config.py`

**Changes**:
- Add `get_bedrock_custom_model_deployment_arn()` function
- Maintain alphabetical ordering of getter functions

**Function Signature**:
```python
def get_bedrock_custom_model_deployment_arn() -> str:
    """
    Get Bedrock Custom Model Deployment ARN from SSM Parameter Store.
    
    Parameter: /teachers_assistant/{env}/bedrock_custom_model_deployment_arn
    Default: my-bedrock-custom-model-deployment-arn
    
    Returns:
        ARN for Bedrock Custom Model Deployment
    
    Example:
        >>> arn = get_bedrock_custom_model_deployment_arn()
        >>> print(arn)
        'arn:aws:bedrock:us-east-1:123456789012:provisioned-model/abc123'
    """
    return _get_parameter('bedrock_custom_model_deployment_arn', default='my-bedrock-custom-model-deployment-arn')
```

**Placement**: Insert alphabetically between `get_aws_region()` and `get_default_model_id()`

### 3. Application UI Enhancement

**Files**: 
- `workshop4/deploy_multi_agent/docker_app/app.py`
- `workshop4/multi_agent/app.py`

**Changes to model_options Dictionary**:

**Before**:
```python
model_options = {
    "Custom SageMaker Model": {
        "provider": "sagemaker",
        "model_id": "sagemaker-endpoint",
        "display_name": "Custom SageMaker Model"
    }
}
```

**After**:
```python
# Fetch configuration values
custom_model_arn = get_bedrock_custom_model_deployment_arn()
sagemaker_endpoint = get_sagemaker_model_endpoint()

model_options = {
    # ... existing Bedrock options ...
    f"Bedrock Custom Model Deployment ({custom_model_arn})": {
        "provider": "bedrock",
        "model_id": custom_model_arn,
        "display_name": "Bedrock Custom Model Deployment"
    },
    f"SageMaker Model ({sagemaker_endpoint})": {
        "provider": "sagemaker",
        "model_id": "sagemaker-endpoint",
        "display_name": "SageMaker Model"
    }
}
```

**Information Display Enhancement**:

Add conditional information display in the sidebar when custom model deployment is selected:

```python
# Display active model information
st.info(f"**Active Model**: {selected_model_info['display_name']}\n\n**Provider**: {provider_display}")

# Add custom model deployment information
if selected_model_info['display_name'] == "Bedrock Custom Model Deployment":
    st.markdown("""
    **About Custom Model Deployments:**
    
    When you invoke the model, specify the Amazon Resource Name (ARN) for your 
    on-demand deployment. This ARN uniquely identifies your deployed model endpoint 
    and enables you to access it for inference.
    
    In other words, in the case of Bedrock Custom Model Deployment, the model id 
    is simply the value of the bedrock-custom-model-deployment-arn parameter.
    """)
```

### 4. Model Creation Layer

**File**: `workshop4/deploy_multi_agent/docker_app/bedrock_model.py`

**Changes**: None required - the existing `create_bedrock_model()` function already accepts any string as `model_id`, including ARNs. The BedrockModel class from Strands Agents SDK handles ARNs natively.

**Validation Enhancement** (Optional):

The current implementation validates model_id against a list of supported models. For custom model deployments, we can either:

**Option A**: Remove validation entirely (allows any model_id including ARNs)
**Option B**: Add ARN pattern detection to skip validation for ARNs

Recommended approach: **Option B** - Add ARN detection

```python
import re

# ARN pattern for Bedrock custom model deployments
ARN_PATTERN = r'^arn:aws:bedrock:[a-z0-9-]+:\d{12}:custom-model-deployment/[a-zA-Z0-9]+$'

def create_bedrock_model(
    model_id: str = None,
    temperature: float = 0.3
) -> BedrockModel:
    # Get model ID from parameter or config
    if model_id is None:
        model_id = get_default_model_id()
    
    # Validate model ID (skip validation for ARNs)
    is_arn = re.match(ARN_PATTERN, model_id)
    if not is_arn and model_id not in SUPPORTED_MODELS:
        raise ValueError(
            f"Invalid Bedrock model ID: '{model_id}'. "
            f"Supported models: {', '.join(SUPPORTED_MODELS)}"
        )
    
    # Create and return Bedrock model
    return BedrockModel(
        model_id=model_id,
        region_name=get_aws_region(),
        temperature=temperature
    )
```

### 5. Validation Script

**File**: `workshop4/validate/validate_bedrock_custom_model_deployment.py` (NEW)

**Purpose**: Standalone script to validate Bedrock Custom Model Deployment endpoint before running the full application.

**Interface**:
```python
def validate_bedrock_custom_model_deployment() -> bool:
    """
    Validate Bedrock Custom Model Deployment with sample prompt.
    
    Returns:
        True if validation succeeds, False otherwise
    """
```

**Implementation Details**:
- Retrieve bedrock-custom-model-deployment-arn from SSM Parameter Store using config module
- Use BedrockModel to create model instance with ARN
- Invoke model with simple test prompt (e.g., "Hello, please respond with 'OK'")
- Print clear success or failure messages
- Execute independently without full application
- Handle errors gracefully with descriptive messages

**Sample Prompt**: Uses a simple reasoning task to verify model functionality.

**Validation Steps**:
- Import config module to get custom model deployment ARN
- Create BedrockModel instance with ARN
- Invoke model with sample prompt
- Verify response is received
- Print validation result

**File**: `workshop4/validate/validate_all.py` (UPDATE)

**Changes**:
- Import validation functions in correct order:
  1. `validate_ssm_parameters` from `validate_ssm_parameters.py`
  2. `validate_bedrock_custom_model_deployment` from `validate_bedrock_custom_model_deployment.py`
  3. `validate_sagemaker_endpoint` from `validate_sagemaker_endpoint.py`
  4. `validate_xgboost_endpoint` from `validate_xgboost_endpoint.py`
- Execute validations in the sequence above
- Report validation status for each script
- Maintain existing validation logic for other components
- Exit with appropriate status code based on all validation results

**File**: `workshop4/validate/validate_ssm_parameters.py` (UPDATE)

**Changes**:
- Update `expected_parameters` list to include `'bedrock_custom_model_deployment_arn'`
- Maintain alphabetical ordering of parameters in the list
- Updated list should be:
  ```python
  expected_parameters = [
      'bedrock_custom_model_deployment_arn',  # NEW
      'default_model_id',
      'max_results',
      'min_score',
      'sagemaker_model_endpoint',
      'sagemaker_model_inference_component',
      'temperature',
      'xgboost_model_endpoint'
  ]
  ```
- Note: `strands_knowledge_base_id` is removed as it's now an environment variable (STRANDS_KNOWLEDGE_BASE_ID) rather than SSM parameter
- Add placeholder check for `'my-bedrock-custom-model-deployment-arn'` in placeholder_values list

## Data Models

### Configuration Data

**SSM Parameter Structure**:
```
/teachers_assistant/{environment}/
├── bedrock_custom_model_deployment_arn          (NEW)
├── default_model_id
├── max_results
├── min_score
├── sagemaker_model_endpoint
├── sagemaker_model_inference_component
├── strands_knowledge_base_id
├── temperature
└── xgboost_model_endpoint
```

### Model Selection Data Structure

**model_options Dictionary**:
```python
{
    "Display Label (with dynamic value)": {
        "provider": str,        # "bedrock" or "sagemaker"
        "model_id": str,        # Model identifier or ARN
        "display_name": str     # Short name for display
    }
}
```

**Example**:
```python
{
    "Bedrock Custom Model Deployment (arn:aws:bedrock:us-east-1:123456789012:custom-model-deployment/10bnyrrf7js9)": {
        "provider": "bedrock",
        "model_id": "arn:aws:bedrock:us-east-1:123456789012:custom-model-deployment/10bnyrrf7js9",
        "display_name": "Bedrock Custom Model Deployment"
    },
    "SageMaker Model (jumpstart-dft-mistral-small-3-2-24b-20260122-002833)": {
        "provider": "sagemaker",
        "model_id": "sagemaker-endpoint",
        "display_name": "SageMaker Model"
    }
}
```

### ARN Format

**Bedrock Custom Model Deployment ARN**:
```
arn:aws:bedrock:{region}:{account-id}:custom-model-deployment/{deployment-id}
```

**Example**:
```
arn:aws:bedrock:us-east-1:123456789012:custom-model-deployment/10bnyrrf7js9
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After reviewing the prework analysis, most acceptance criteria are either:
- Infrastructure/deployment concerns (CloudFormation template structure)
- UI rendering and display concerns (dropdown labels, information display)
- Process/workflow concerns (development and deployment process)
- Backward compatibility regression tests (existing functionality preservation)

The testable properties are primarily example-based tests for specific scenarios rather than universal properties. The main universal property identified is:

**Property 1: Inference component conditional logic**
- This tests the conditional behavior across different inference component values
- Can be generalized to test with various placeholder and non-placeholder values

**Property 2: ARN acceptance by Bedrock model**
- This tests that BedrockModel can accept various ARN formats
- Can be generalized to test with different valid ARN patterns

Most other criteria are better suited for:
- Unit tests (specific function behavior)
- Integration tests (UI rendering, configuration retrieval)
- Regression tests (backward compatibility)
- Manual verification (deployment process, code organization)

### Testable Properties

**Property 1: Inference Component Conditional Setting**

*For any* SageMaker inference component value, when creating a SageMaker model, the inference component should only be included in the endpoint configuration if the value exists and is not equal to the placeholder value "my-sagemaker-model-inference-component"

**Validates: Requirements 4.3**

**Property 2: ARN Format Acceptance**

*For any* valid Bedrock Custom Model Deployment ARN format, the BedrockModel creation function should successfully create a model instance without raising a validation error

**Validates: Requirements 2.4**

### Example-Based Tests

The following criteria are best tested with specific examples rather than property-based testing:

1. **Configuration Getter Function** (Requirement 1.4)
   - Test that `get_bedrock_custom_model_deployment_arn()` returns a string value
   - Test with mocked SSM parameter values

2. **Dropdown Option Inclusion** (Requirement 2.1)
   - Test that model_options dictionary contains custom model deployment key
   - Test that the key includes the ARN value from configuration

3. **Model Provider Setting** (Requirement 2.2)
   - Test that selecting custom model deployment sets provider to "bedrock"

4. **Model ID Setting** (Requirement 2.3)
   - Test that selecting custom model deployment sets model_id to ARN value

5. **Existing Options Preservation** (Requirement 2.5)
   - Test that all existing model options remain in model_options dictionary
   - Test that existing options have unchanged provider and model_id values

6. **Information Display** (Requirements 3.1, 3.2, 3.3)
   - Test that custom model deployment information is displayed when selected
   - Test that information contains expected text about ARN usage

7. **SageMaker Display Enhancement** (Requirement 4.1)
   - Test that SageMaker option label includes endpoint name
   - Test that label format matches expected pattern

8. **SageMaker Behavior Preservation** (Requirement 4.2)
   - Test that SageMaker model creation still works with existing parameters

9. **Configuration Retrieval** (Requirement 4.4)
   - Test that SageMaker endpoint name is retrieved using getter function

10. **Backward Compatibility** (Requirements 7.1, 7.2, 7.3)
    - Test that all existing Bedrock options still work
    - Test that SageMaker integration still works
    - Test that model invocation parameters are unchanged

## Error Handling

### Configuration Errors

**Missing SSM Parameters**:
- If `bedrock_custom_model_deployment_arn` parameter is not found, use default value `my-bedrock-custom-model-deployment-arn`
- Display warning in UI if default placeholder value is detected
- Log configuration errors for debugging

**Invalid ARN Format**:
- If ARN format is invalid, BedrockModel will raise an error during invocation
- Display user-friendly error message in Streamlit UI
- Suggest checking SSM parameter value

### Model Creation Errors

**Bedrock Model Creation**:
- If ARN is invalid or model is not accessible, BedrockModel will raise an error
- Catch exception and display error message to user
- Provide fallback to default model if configured

**SageMaker Model Creation**:
- Existing error handling remains unchanged
- If endpoint is not accessible, display error and suggest checking configuration

### UI Error Handling

**Model Selection**:
- If selected model fails to create, display error message
- Allow user to select different model
- Maintain conversation history across model changes

**Configuration Display**:
- If configuration values cannot be retrieved, display placeholder text
- Log errors for debugging
- Application remains functional with default values

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests**: Verify specific examples, edge cases, and error conditions
- Configuration getter function returns expected values
- Model options dictionary contains expected entries
- UI displays correct information for each model type
- Backward compatibility with existing model options
- Error handling for missing or invalid configuration

**Property Tests**: Verify universal properties across all inputs
- Inference component conditional logic works for all possible values
- ARN format acceptance works for all valid ARN patterns

Both testing approaches are complementary and necessary. Unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across a wide range of inputs.

### Property-Based Testing Configuration

**Library**: Use `hypothesis` for Python property-based testing

**Test Configuration**:
- Minimum 100 iterations per property test
- Each property test must reference its design document property
- Tag format: **Feature: workshop4-multi-agent-model-selection, Property {number}: {property_text}**

**Property Test Examples**:

```python
from hypothesis import given, strategies as st
import pytest

# Property 1: Inference Component Conditional Setting
@given(inference_component=st.one_of(
    st.none(),
    st.just("my-sagemaker-model-inference-component"),
    st.text(min_size=1).filter(lambda x: x != "my-sagemaker-model-inference-component")
))
def test_inference_component_conditional_setting(inference_component):
    """
    Feature: workshop4-multi-agent-model-selection
    Property 1: Inference Component Conditional Setting
    
    For any SageMaker inference component value, when creating a SageMaker model,
    the inference component should only be included in the endpoint configuration
    if the value exists and is not equal to the placeholder value.
    """
    # Test implementation
    pass

# Property 2: ARN Format Acceptance
@given(arn=st.from_regex(
    r'^arn:aws:bedrock:[a-z0-9-]+:\d{12}:custom-model-deployment/[a-zA-Z0-9]+$',
    fullmatch=True
))
def test_arn_format_acceptance(arn):
    """
    Feature: workshop4-multi-agent-model-selection
    Property 2: ARN Format Acceptance
    
    For any valid Bedrock Custom Model Deployment ARN format, the BedrockModel
    creation function should successfully create a model instance without raising
    a validation error.
    """
    # Test implementation
    pass
```

### Unit Testing Focus

Unit tests should focus on:

1. **Configuration Module**:
   - Test `get_bedrock_custom_model_deployment_arn()` returns expected value
   - Test alphabetical ordering of getter functions
   - Test default value handling

2. **Model Options Dictionary**:
   - Test custom model deployment option is present
   - Test SageMaker option label includes endpoint name
   - Test all existing options are preserved

3. **UI Display**:
   - Test custom model deployment information is displayed
   - Test information contains expected text
   - Test information appears in correct location

4. **Model Creation**:
   - Test BedrockModel accepts ARN as model_id
   - Test SageMaker model creation with and without inference component
   - Test error handling for invalid configurations

5. **Backward Compatibility**:
   - Test all existing Bedrock options still work
   - Test SageMaker integration still works
   - Test model invocation parameters unchanged

### Integration Testing

**Local Development Testing** (PART-2-MULTI-AGENT.md):
1. Set up local environment with SSM parameters
2. Test model selection dropdown displays all options correctly
3. Test selecting custom model deployment option
4. Test selecting SageMaker option with endpoint name
5. Test model invocation with custom ARN
6. Test backward compatibility with existing models

**Remote Deployment Testing** (PART-3-DEPLOY-MULTI-AGENT.md):
1. Deploy CloudFormation template with new parameter
2. Deploy application to remote environment
3. Verify SSM parameters are accessible
4. Test model selection in deployed application
5. Test end-to-end functionality with custom model deployment
6. Verify backward compatibility in production environment

### Test Coverage Goals

- **Unit Test Coverage**: 90%+ for modified files
- **Integration Test Coverage**: All user-facing workflows
- **Property Test Coverage**: All identified universal properties
- **Regression Test Coverage**: All existing model selection options

## Implementation Notes

### Development Workflow

1. **Local Development** (PART-2-MULTI-AGENT.md):
   - Modify `workshop4/multi_agent/app.py`
   - Modify `workshop4/multi_agent/config.py`
   - Test locally with mock SSM parameters or local configuration
   - Verify all model selection options work correctly

2. **Deployment** (PART-3-DEPLOY-MULTI-AGENT.md):
   - Deploy CloudFormation template to create SSM parameters
   - Modify `workshop4/deploy_multi_agent/docker_app/app.py`
   - Modify `workshop4/deploy_multi_agent/docker_app/config.py`
   - Build and deploy Docker container
   - Test in remote environment

### Code Organization

**Files to Modify**:
1. `workshop4/ssm/teachers-assistant-params.yaml` - Add BedrockCustomModelDeploymentArn parameter
2. `workshop4/deploy_multi_agent/docker_app/config.py` - Add get_bedrock_custom_model_deployment_arn()
3. `workshop4/deploy_multi_agent/docker_app/app.py` - Update model_options and UI display
4. `workshop4/multi_agent/config.py` - Mirror changes for local development
5. `workshop4/multi_agent/app.py` - Mirror changes for local development
6. `workshop4/deploy_multi_agent/docker_app/bedrock_model.py` - Add ARN validation (optional)

**Files to Create**:
- `workshop4/validate/validate_bedrock_custom_model_deployment.py` - Validation script for custom model deployment

**Files to Update**:
- `workshop4/validate/validate_all.py` - Add custom model deployment validation

### Backward Compatibility Considerations

1. **Existing SSM Parameters**: No changes required to existing parameters
2. **Existing Model Options**: All existing options remain unchanged
3. **Model Invocation**: Existing model invocation logic unchanged
4. **Configuration API**: All existing getter functions unchanged
5. **UI Layout**: Existing UI elements remain in same locations

### Performance Considerations

1. **SSM Parameter Retrieval**: Parameters are cached using `@lru_cache`, no performance impact
2. **Model Creation**: No additional overhead for model creation
3. **UI Rendering**: Minimal impact from dynamic dropdown labels
4. **Model Invocation**: No performance difference between ARN and standard model ID

### Security Considerations

1. **ARN Validation**: Validate ARN format to prevent injection attacks
2. **SSM Parameter Access**: Ensure proper IAM permissions for parameter access
3. **Model Access**: Verify IAM permissions for custom model deployment access
4. **Error Messages**: Avoid exposing sensitive information in error messages

## References

- [AWS Bedrock Custom Model Deployment Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-deploy.html)
- [Strands Agents SDK - BedrockModel](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/bedrock/)
- [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
- [Streamlit Documentation](https://docs.streamlit.io/)
- PART-2-MULTI-AGENT.md - Local development instructions
- PART-3-DEPLOY-MULTI-AGENT.md - Deployment instructions
