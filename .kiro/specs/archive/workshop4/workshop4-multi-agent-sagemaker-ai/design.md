# Design Document

## Overview

This design document outlines the architecture and implementation approach for expanding the workshop4 multi-agent application to support multiple reasoning LLM choices (Amazon Bedrock and Amazon SageMaker) and integrating a loan prediction assistant powered by a SageMaker XGBoost model.

The design follows the consolidated architecture pattern where:
- `multi_agent/` contains the local implementation
- `deploy_multi_agent/docker_app/` contains the cloud deployment implementation

Both implementations share the same core logic through modular Python files for configuration, model creation, and specialized assistants.

## Architecture

### Development and Deployment Strategy

**Local-First Development Approach**:
1. All new features are built and tested in `multi_agent/` directory first
2. Local implementation uses `multi_agent/app.py` without authentication
3. Once local implementation is complete and tested, merge to `deploy_multi_agent/docker_app/`
4. Deployment implementation preserves Cognito authentication logic in `deploy_multi_agent/docker_app/app.py`

**Merge Strategy**:
- New modules (config.py, bedrock_model.py, sagemaker_model.py, loan_assistant.py) are copied to both directories
- Application logic from `multi_agent/app.py` is merged into `deploy_multi_agent/docker_app/app.py`
- Authentication section in deployed app remains at the top (lines 1-25)
- Application logic section is updated with new features
- Sidebar authentication UI is preserved in deployed app

**Rationale**: This approach ensures:
- Faster iteration during development (no authentication overhead)
- Easier testing and debugging locally
- Clean separation between application logic and deployment concerns
- Smooth transition to workshop4-architecture-refactoring completion

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Application                     │
│                         (app.py)                             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─────────────────────────────────────────────┐
                 │                                             │
        ┌────────▼────────┐                          ┌────────▼────────┐
        │  Teacher Agent  │                          │  Config Module  │
        │  (Orchestrator) │                          │   (config.py)   │
        └────────┬────────┘                          └─────────────────┘
                 │
                 │ Routes to specialized agents
                 │
    ┌────────────┼────────────┬──────────────┬──────────────┐
    │            │            │              │              │
┌───▼───┐  ┌────▼────┐  ┌────▼────┐  ┌─────▼─────┐  ┌─────▼─────┐
│ Math  │  │ English │  │Language │  │ Computer  │  │   Loan    │
│ Agent │  │  Agent  │  │  Agent  │  │  Science  │  │ Assistant │
└───────┘  └─────────┘  └─────────┘  └───────────┘  └─────┬─────┘
                                                            │
                                                            │
                                                   ┌────────▼────────┐
                                                   │  XGBoost Model  │
                                                   │   (SageMaker    │
                                                   │   Serverless)   │
                                                   └─────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Reasoning LLM Layer                             │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  Bedrock Models  │         │ SageMaker Models │         │
│  │  ┌────────────┐  │         │  ┌────────────┐  │         │
│  │  │ Nova Pro   │  │         │  │ Custom LLM │  │         │
│  │  │ Nova Lite  │  │         │  │ Endpoint   │  │         │
│  │  │ Claude 4.5 │  │         │  └────────────┘  │         │
│  │  └────────────┘  │         │                  │         │
│  └──────────────────┘         └──────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Module Structure

```
multi_agent/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration management (NEW)
├── bedrock_model.py            # Bedrock model creation (NEW)
├── sagemaker_model.py          # SageMaker model creation (NEW)
├── loan_assistant.py           # Loan prediction assistant (NEW)
├── math_assistant.py           # Existing math assistant
├── english_assistant.py        # Existing English assistant
├── language_assistant.py       # Existing language assistant
├── computer_science_assistant.py  # Existing CS assistant
├── no_expertise.py             # Existing general assistant
├── teachers_assistant.py       # Existing teacher orchestrator
└── cross_platform_tools.py     # Existing cross-platform tools

deploy_multi_agent/docker_app/
├── app.py                      # Main Streamlit application (with auth)
├── config_file.py              # Deployment configuration (existing)
├── config.py                   # Configuration management (NEW)
├── bedrock_model.py            # Bedrock model creation (NEW)
├── sagemaker_model.py          # SageMaker model creation (NEW)
├── loan_assistant.py           # Loan prediction assistant (NEW)
├── [other assistants...]       # Existing assistants
└── utils/
    ├── auth.py                 # Authentication utilities
    └── llm.py                  # LLM utilities (existing)

workshop4/sagemaker/
├── config.py                   # Existing SageMaker config
├── sagemaker_model.py          # Existing SageMaker model
├── validate_sagemaker_endpoint.py      # SageMaker agent model validation script (NEW)
└── validate_xgboost_endpoint.py        # XGBoost model validation script (NEW)
```

## Components and Interfaces

### 1. SageMaker Agent Model Endpoint Validation Script

**Purpose**: Standalone script to validate SageMaker reasoning model endpoint before running the full application.

**Interface**:
```python
def validate_sagemaker_endpoint(endpoint_name: str) -> bool:
    """
    Validate SageMaker agent model endpoint with sample prompt.
    
    Args:
        endpoint_name: SageMaker endpoint name
        
    Returns:
        True if validation succeeds, False otherwise
    """
```

**Sample Prompt**: Uses a simple reasoning task to verify model functionality.

**Validation Steps**:
- Extract invocation logic from Jupyter notebook
- Use environment variables for endpoint configuration
- Invoke endpoint with sample prompt
- Print clear success or failure messages
- Execute independently without full application

### 2. XGBoost Model Endpoint Validation Script

**Purpose**: Standalone script to validate XGBoost serverless endpoint before building the loan assistant.

**Interface**:
```python
def validate_xgboost_endpoint(endpoint_name: str) -> bool:
    """
    Validate XGBoost model endpoint with sample data.
    
    Args:
        endpoint_name: SageMaker endpoint name
        
    Returns:
        True if validation succeeds, False otherwise
    """
```

**Sample Data**: Uses a representative customer profile from the training dataset.

**Validation Steps**:
- Extract invocation logic from Jupyter notebook
- Use environment variables for endpoint configuration
- Invoke endpoint with sample customer data
- Print clear success or failure messages
- Execute independently without full application

### 3. Configuration Module (config.py)

**Purpose**: Centralize environment variable management and provide validated configuration values.

**Interface**:
```python
def get_sagemaker_model_endpoint() -> str:
    """Get SageMaker model endpoint name from SSM Parameter Store."""
    
def get_sagemaker_model_inference_component() -> Optional[str]:
    """Get SageMaker model inference component name from SSM Parameter Store."""
    
def get_strands_knowledge_base_id() -> str:
    """
    Get Strands knowledge base ID from SSM Parameter Store.
    
    IMPORTANT: This parameter MUST be named 'strands_knowledge_base_id' because
    the Strands Agents framework requires the STRANDS_KNOWLEDGE_BASE_ID environment
    variable to integrate with Bedrock Knowledge Base. This is a framework requirement
    and cannot be renamed.
    
    Reference: https://strandsagents.com/latest/documentation/docs/examples/python/knowledge_base_agent/
    """
    
def get_aws_region() -> str:
    """Get AWS region from SSM Parameter Store."""
    
def get_default_model_id() -> str:
    """Get default model ID from SSM Parameter Store."""
    
def get_max_results() -> int:
    """Get maximum results for knowledge base queries from SSM Parameter Store."""
    
def get_min_score() -> float:
    """Get minimum score threshold for knowledge base queries from SSM Parameter Store."""
    
def get_temperature() -> float:
    """Get model temperature setting from SSM Parameter Store."""
    
def get_xgboost_model_endpoint() -> str:
    """Get XGBoost model endpoint name from SSM Parameter Store."""
```

**SSM Parameters** (alphabetically sorted):
- `/teachers_assistant/{env}/default_model_id`: Default model ID (default: us.amazon.nova-2-lite-v1:0)
- `/teachers_assistant/{env}/max_results`: Maximum results for knowledge base queries (default: 9)
- `/teachers_assistant/{env}/min_score`: Minimum score threshold for knowledge base queries (default: 0.000001)
- `/teachers_assistant/{env}/sagemaker_model_endpoint`: SageMaker model endpoint name (default: my-sagemaker-model-endpoint)
- `/teachers_assistant/{env}/sagemaker_model_inference_component`: SageMaker model inference component (default: my-sagemaker-model-inference-component)
- `/teachers_assistant/{env}/strands_knowledge_base_id`: Strands knowledge base ID (REQUIRED - Framework integration point with Bedrock Knowledge Base)
- `/teachers_assistant/{env}/temperature`: Model temperature setting (default: 0.3)
- `/teachers_assistant/{env}/xgboost_model_endpoint`: XGBoost loan prediction endpoint name (default: my-xgboost-model-endpoint)

**Environment Variables**:
- `TEACHERS_ASSISTANT_ENV`: Determines which parameter path to use (dev, staging, or prod)
- `AWS_REGION`: AWS region for all AWS services (default: us-east-1) - standard AWS SDK environment variable

**Note**: The model provider is NOT an environment variable or SSM parameter. It is determined dynamically at runtime based on the user's model selection in the UI:
- If user selects a Bedrock model (Nova, Claude) → provider = "bedrock"
- If user selects the SageMaker model (gpt-oss-20b) → provider = "sagemaker"

### 4. Bedrock Model Module (bedrock_model.py)

**Purpose**: Create and configure Bedrock models with support for multiple cross-region inference profiles.

**Interface**:
```python
def create_bedrock_model(
    model_id: str = None,
    temperature: float = 0.3
) -> BedrockModel:
    """
    Create a Bedrock model instance.
    
    Args:
        model_id: Bedrock model ID or cross-region profile
        temperature: Model temperature setting
        
    Returns:
        Configured BedrockModel instance
    """
```

**Supported Models**:
- `us.amazon.nova-pro-v1:0` (default)
- `us.amazon.nova-2-lite-v1:0`
- `us.anthropic.claude-haiku-4-5-20251001-v1:0`
- `us.anthropic.claude-sonnet-4-5-20250929-v1:0`

### 5. SageMaker Model Module (sagemaker_model.py)

**Purpose**: Create and configure SageMaker AI models for Strands Agents.

**Interface**:
```python
def create_sagemaker_model(
    endpoint_name: str = None,
    region: str = None,
    max_tokens: int = 1000,
    temperature: float = 0.7
) -> SageMakerAIModel:
    """
    Create a SageMaker AI model for Strands Agents.
    
    Args:
        endpoint_name: SageMaker endpoint name
        region: AWS region
        max_tokens: Maximum tokens to generate
        temperature: Model temperature setting
        
    Returns:
        Configured SageMakerAIModel instance
    """
```

### 6. Loan Offering Assistant Module (loan_offering_assistant.py)

**Purpose**: Provide loan acceptance prediction using XGBoost model on SageMaker, similar to how math_assistant uses calculator tools.

**Interface**:
```python
@tool
def loan_offering_assistant(query: str) -> str:
    """
    Process and respond to loan offering prediction queries using XGBoost model.
    
    Args:
        query: A loan prediction question with CSV feature payload from the user
        
    Returns:
        A detailed prediction with raw score, label, and confidence
    """

@tool  
def loan_offering_prediction(payload: str) -> str:
    """
    Predict loan acceptance using XGBoost model endpoint.
    
    Args:
        payload: CSV string with 59 features (same format as validate_xgboost_endpoint)
        
    Returns:
        Prediction result with raw score, label (Accept/Reject), and confidence percentage
    """
```

**Implementation Details**:
- Similar structure to math_assistant.py
- Uses loan_offering_prediction tool (similar to calculator in math_assistant)
- loan_offering_prediction works like validate_xgboost_endpoint function
- Accepts CSV payload string with 59 comma-separated features
- Invokes SageMaker XGBoost endpoint using boto3 sagemaker-runtime client
- Parses numeric prediction (0-1 range)
- Returns formatted response with:
  - Feature payload
  - Raw prediction score
  - Prediction label: "Accept" if >= 0.5, else "Reject"  
  - Confidence: prediction * 100 formatted to 2 decimal places

## Data Models

### Loan Prediction Request

```python
# Simple CSV payload string (59 comma-separated features)
# Example: "29,2,999,0,1,0,0.0,1.0,0.0,..."
payload: str
```

### Loan Prediction Response

```python
@dataclass
class LoanPrediction:
    """Loan prediction result."""
    payload: str  # Original feature payload
    raw_prediction: float  # Raw model output (0.0 to 1.0)
    prediction_label: str  # "Accept" or "Reject"
    confidence: str  # Formatted as "{prediction * 100:.2f}%"
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Configuration Consistency
*For any* environment variable getter function, calling it multiple times in the same execution should return the same value.
**Validates: Requirements 3.1, 3.2**

### Property 2: Model Creation Idempotence
*For any* model ID and configuration parameters, creating a model instance twice with the same parameters should produce functionally equivalent models.
**Validates: Requirements 4.2, 5.2**

### Property 3: Bedrock Model ID Validation
*For any* Bedrock model ID provided, if it matches one of the supported cross-region profiles, the model creation should succeed; otherwise, it should raise a descriptive error.
**Validates: Requirements 4.3**

### Property 4: Prediction Output Range
*For any* XGBoost model response, the parsed prediction value should be in the range [0.0, 1.0].
**Validates: Requirements 7.6, 7.7**

### Property 5: Binary Classification Mapping
*For any* prediction score from the XGBoost model, scores >= 0.5 should map to "Accept" and scores < 0.5 should map to "Reject".
**Validates: Requirements 7.8**

### Property 6: Error Handling Graceful Degradation
*For any* endpoint invocation failure, the assistant should return a descriptive error message rather than raising an unhandled exception.
**Validates: Requirements 7.10**

### Property 7: Model Selection Consistency
*For any* user model selection in the UI, the application should use exactly one model provider (Bedrock or SageMaker) based on the selected model, never both simultaneously.
**Validates: Requirements 6.3, 6.4**

### Property 8: Validation Script Independence
*For any* validation script execution, the script should complete successfully without requiring the full application to be running.
**Validates: Requirements 1.5, 2.5**

## Error Handling

### Configuration Errors
- **Missing Required Environment Variable**: Raise `ValueError` with descriptive message indicating which variable is missing
- **Invalid Environment Variable Value**: Raise `ValueError` with descriptive message and list of valid values
- **Default Value Fallback**: Log warning when using default value instead of configured value

### Model Creation Errors
- **Invalid Bedrock Model ID**: Raise `ValueError` with list of supported model IDs
- **SageMaker Endpoint Not Found**: Raise `RuntimeError` with endpoint name and region
- **Authentication Failure**: Raise `RuntimeError` with AWS credential guidance

### Endpoint Invocation Errors
- **Endpoint Unavailable**: Return user-friendly error message, log technical details
- **Timeout**: Return timeout message with suggestion to retry
- **Invalid Payload Format**: Raise `ValueError` with payload format requirements
- **Malformed Response**: Log raw response, return generic error message to user

### Data Validation Errors
- **Invalid Customer Attributes**: Raise `ValueError` with specific validation failure
- **Unknown Categorical Value**: Raise `ValueError` with list of valid values for that category
- **Out of Range Numeric Value**: Raise `ValueError` with valid range

## Testing Strategy

### Unit Tests
Unit tests will verify specific examples, edge cases, and error conditions:

1. **Configuration Tests**:
   - Test default value returns when environment variable not set
   - Test validation of invalid environment variable values
   - Test each getter function with valid values

2. **Model Creation Tests**:
   - Test Bedrock model creation with each supported model ID
   - Test SageMaker model creation with valid endpoint name
   - Test error handling for invalid model IDs and missing endpoints

3. **Data Transformation Tests**:
   - Test one-hot encoding for each categorical feature
   - Test CSV payload generation for sample customer profiles
   - Test edge cases (unknown values, boundary numeric values)

4. **Prediction Parsing Tests**:
   - Test parsing of various prediction scores (0.0, 0.5, 1.0, intermediate values)
   - Test binary classification mapping at threshold boundary
   - Test error handling for malformed responses

5. **Integration Tests**:
   - Test loan assistant with sample customer data
   - Test teacher agent routing to loan assistant
   - Test error propagation through agent hierarchy

### Property-Based Tests
Property-based tests will verify universal properties across all inputs using a PBT library (e.g., Hypothesis for Python):

1. **Property Test 1: Configuration Consistency**
   - Generate random sequences of configuration getter calls
   - Verify same value returned for each call in same execution
   - **Feature: workshop4-multi-agent-sagemaker-ai, Property 1: Configuration Consistency**

2. **Property Test 2: Model Creation Idempotence**
   - Generate random model IDs and configuration parameters
   - Create models twice with same parameters
   - Verify functional equivalence
   - **Feature: workshop4-multi-agent-sagemaker-ai, Property 2: Model Creation Idempotence**

3. **Property Test 4: CSV Payload Format Correctness**
   - Generate random valid CustomerAttributes instances
   - Verify CSV payload has exactly 59 values
   - **Feature: workshop4-multi-agent-sagemaker-ai, Property 4: CSV Payload Format Correctness**

4. **Property Test 5: One-Hot Encoding Completeness**
   - Generate random categorical feature values
   - Verify exactly one indicator is 1.0 per category
   - **Feature: workshop4-multi-agent-sagemaker-ai, Property 5: One-Hot Encoding Completeness**

5. **Property Test 6: Prediction Output Range**
   - Generate random XGBoost responses
   - Verify parsed predictions in [0.0, 1.0]
   - **Feature: workshop4-multi-agent-sagemaker-ai, Property 6: Prediction Output Range**

6. **Property Test 7: Binary Classification Mapping**
   - Generate random prediction scores
   - Verify correct accept/reject mapping
   - **Feature: workshop4-multi-agent-sagemaker-ai, Property 7: Binary Classification Mapping**

### Validation Scripts
The validation scripts serve as integration tests for SageMaker endpoints:

1. **XGBoost Endpoint Validation**:
   - Verify endpoint is accessible
   - Verify endpoint accepts CSV payload
   - Verify endpoint returns valid prediction
   - Print clear success/failure message

2. **Reasoning Model Endpoint Validation**:
   - Verify endpoint is accessible
   - Verify endpoint accepts prompt
   - Verify endpoint returns coherent response
   - Print clear success/failure message

### Test Configuration
- Property tests: Minimum 100 iterations per test
- Unit tests: Cover all public functions and error paths
- Integration tests: Test end-to-end flows with mocked endpoints
- Validation scripts: Run before deploying application

### Testing Tools
- **Unit Testing**: pytest
- **Property-Based Testing**: Hypothesis
- **Mocking**: unittest.mock for AWS service calls
- **Coverage**: pytest-cov (target: >80% coverage)
