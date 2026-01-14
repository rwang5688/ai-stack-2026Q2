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
├── validate_xgboost_endpoint.py      # XGBoost validation script (NEW)
└── validate_reasoning_endpoint.py    # Reasoning model validation script (NEW)
```

## Components and Interfaces

### 1. Configuration Module (config.py)

**Purpose**: Centralize environment variable management and provide validated configuration values.

**Interface**:
```python
def get_aws_region() -> str:
    """Get AWS region from environment variable."""
    
def get_bedrock_model_id() -> str:
    """Get Bedrock model ID from environment variable."""
    
def get_sagemaker_endpoint_name() -> str:
    """Get SageMaker reasoning endpoint name from environment variable."""
    
def get_xgboost_endpoint_name() -> str:
    """Get XGBoost model endpoint name from environment variable."""
    
def get_reasoning_llm_provider() -> str:
    """Get reasoning LLM provider (bedrock or sagemaker)."""
    
def get_knowledge_base_id() -> str:
    """Get Strands knowledge base ID from environment variable."""
```

**Environment Variables**:
- `AWS_REGION`: AWS region for all services (default: us-west-2)
- `BEDROCK_MODEL_ID`: Bedrock model ID (default: us.amazon.nova-pro-v1:0)
- `SAGEMAKER_REASONING_ENDPOINT`: SageMaker reasoning model endpoint name
- `XGBOOST_ENDPOINT_NAME`: XGBoost loan prediction endpoint name
- `REASONING_LLM_PROVIDER`: Provider choice (bedrock or sagemaker, default: bedrock)
- `STRANDS_KNOWLEDGE_BASE_ID`: Knowledge base ID (existing)

### 2. Bedrock Model Module (bedrock_model.py)

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

### 3. SageMaker Model Module (sagemaker_model.py)

**Purpose**: Create and configure SageMaker AI models for reasoning tasks.

**Interface**:
```python
def create_sagemaker_reasoning_model(
    endpoint_name: str = None,
    region: str = None,
    max_tokens: int = 1000,
    temperature: float = 0.7
) -> SageMakerAIModel:
    """
    Create a SageMaker AI model for reasoning tasks.
    
    Args:
        endpoint_name: SageMaker endpoint name
        region: AWS region
        max_tokens: Maximum tokens to generate
        temperature: Model temperature setting
        
    Returns:
        Configured SageMakerAIModel instance
    """
```

### 4. Loan Assistant Module (loan_assistant.py)

**Purpose**: Provide loan acceptance prediction using XGBoost model on SageMaker.

**Interface**:
```python
@tool
def loan_assistant(
    age: int,
    job: str,
    marital: str,
    education: str,
    default: str,
    housing: str,
    loan: str,
    contact: str,
    month: str,
    day_of_week: str,
    campaign: int,
    pdays: int,
    previous: int,
    poutcome: str
) -> str:
    """
    Predict whether a customer will accept a loan offer.
    
    Args:
        age: Customer age
        job: Job type (admin, services, technician, etc.)
        marital: Marital status (married, single, divorced)
        education: Education level (basic.4y, high.school, university.degree, etc.)
        default: Has credit in default? (yes, no, unknown)
        housing: Has housing loan? (yes, no, unknown)
        loan: Has personal loan? (yes, no, unknown)
        contact: Contact communication type (cellular, telephone)
        month: Last contact month (jan, feb, mar, etc.)
        day_of_week: Last contact day (mon, tue, wed, etc.)
        campaign: Number of contacts during this campaign
        pdays: Days since last contact from previous campaign (999 = not contacted)
        previous: Number of contacts before this campaign
        poutcome: Outcome of previous campaign (nonexistent, failure, success)
        
    Returns:
        Prediction result with confidence score
    """
```

**Implementation Details**:
- Converts input parameters to one-hot encoded CSV format
- Invokes SageMaker serverless inference endpoint
- Parses numeric prediction (0-1 range)
- Returns human-readable result with confidence

### 5. XGBoost Endpoint Validation Script

**Purpose**: Standalone script to validate XGBoost serverless endpoint.

**Interface**:
```python
def validate_xgboost_endpoint(endpoint_name: str) -> bool:
    """
    Validate XGBoost endpoint with sample data.
    
    Args:
        endpoint_name: SageMaker endpoint name
        
    Returns:
        True if validation succeeds, False otherwise
    """
```

**Sample Data**: Uses a representative customer profile from the training dataset.

### 6. Reasoning Model Endpoint Validation Script

**Purpose**: Standalone script to validate SageMaker reasoning model endpoint.

**Interface**:
```python
def validate_reasoning_endpoint(endpoint_name: str) -> bool:
    """
    Validate reasoning model endpoint with sample prompt.
    
    Args:
        endpoint_name: SageMaker endpoint name
        
    Returns:
        True if validation succeeds, False otherwise
    """
```

**Sample Prompt**: Uses a simple reasoning task to verify model functionality.

## Data Models

### Customer Attributes (for Loan Prediction)

```python
@dataclass
class CustomerAttributes:
    """Customer attributes for loan prediction."""
    age: int
    job: str  # Categorical: admin, services, technician, etc.
    marital: str  # Categorical: married, single, divorced
    education: str  # Categorical: basic.4y, high.school, university.degree, etc.
    default: str  # Categorical: yes, no, unknown
    housing: str  # Categorical: yes, no, unknown
    loan: str  # Categorical: yes, no, unknown
    contact: str  # Categorical: cellular, telephone
    month: str  # Categorical: jan, feb, mar, etc.
    day_of_week: str  # Categorical: mon, tue, wed, etc.
    campaign: int  # Numeric: number of contacts
    pdays: int  # Numeric: days since last contact (999 = not contacted)
    previous: int  # Numeric: number of previous contacts
    poutcome: str  # Categorical: nonexistent, failure, success
```

### One-Hot Encoding Mapping

The XGBoost model expects one-hot encoded features. The loan assistant must transform categorical variables into binary indicators following the training data schema:

- Job types: admin, blue-collar, entrepreneur, housemaid, management, retired, self-employed, services, student, technician, unemployed, unknown
- Marital status: divorced, married, single, unknown
- Education: basic.4y, basic.6y, basic.9y, high.school, illiterate, professional.course, university.degree, unknown
- Default: no, yes, unknown
- Housing: no, yes, unknown
- Loan: no, yes, unknown
- Contact: cellular, telephone
- Month: jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec
- Day of week: mon, tue, wed, thu, fri
- Poutcome: failure, nonexistent, success

### Prediction Response

```python
@dataclass
class LoanPrediction:
    """Loan prediction result."""
    prediction: str  # "accept" or "reject"
    confidence: float  # 0.0 to 1.0
    raw_score: float  # Raw model output
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Configuration Consistency
*For any* environment variable getter function, calling it multiple times in the same execution should return the same value.
**Validates: Requirements 1.1, 1.2**

### Property 2: Model Creation Idempotence
*For any* model ID and configuration parameters, creating a model instance twice with the same parameters should produce functionally equivalent models.
**Validates: Requirements 2.2, 3.2**

### Property 3: Bedrock Model ID Validation
*For any* Bedrock model ID provided, if it matches one of the supported cross-region profiles, the model creation should succeed; otherwise, it should raise a descriptive error.
**Validates: Requirements 2.3**

### Property 4: CSV Payload Format Correctness
*For any* valid CustomerAttributes instance, the generated CSV payload should have exactly 59 comma-separated values (matching the XGBoost model's expected input format).
**Validates: Requirements 5.2, 5.3**

### Property 5: One-Hot Encoding Completeness
*For any* categorical feature value in CustomerAttributes, exactly one corresponding one-hot encoded feature should be set to 1.0, and all others for that category should be 0.0.
**Validates: Requirements 5.3**

### Property 6: Prediction Output Range
*For any* XGBoost model response, the parsed prediction value should be in the range [0.0, 1.0].
**Validates: Requirements 5.5**

### Property 7: Binary Classification Mapping
*For any* prediction score from the XGBoost model, scores >= 0.5 should map to "accept" and scores < 0.5 should map to "reject".
**Validates: Requirements 4.4**

### Property 8: Error Handling Graceful Degradation
*For any* endpoint invocation failure, the assistant should return a descriptive error message rather than raising an unhandled exception.
**Validates: Requirements 4.6, 6.5**

### Property 9: Provider Selection Consistency
*For any* value of REASONING_LLM_PROVIDER environment variable, the application should use exactly one reasoning LLM provider (Bedrock or SageMaker), never both simultaneously.
**Validates: Requirements 8.2, 8.3, 8.4**

### Property 10: Validation Script Independence
*For any* validation script execution, the script should complete successfully without requiring the full application to be running.
**Validates: Requirements 6.1, 6.3**

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
