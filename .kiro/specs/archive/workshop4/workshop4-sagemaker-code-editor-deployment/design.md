# Design Document

## Overview

This design describes the deployment workflow for fixing and deploying a multi-agent Streamlit application from SageMaker Code Editor to AWS ECS Fargate. The solution applies an infinite loop fix to the production code by replacing agent-based routing with direct LLM classification, while preserving all Cognito authentication functionality.

The deployment leverages AWS CDK for infrastructure-as-code, Docker for containerization, and establishes SageMaker Code Editor as the primary development and deployment environment.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ SageMaker Code Editor (Development Environment)             │
│ - ml.c5.large (x86_64 architecture)                         │
│                                                               │
│  ┌──────────────────┐      ┌─────────────────┐             │
│  │ Source Code      │      │ CDK Stack       │             │
│  │ - app.py (fixed) │─────▶│ - Infrastructure│────┐        │
│  │ - Dockerfile     │      │ - Deployment    │    │        │
│  │   (x86_64)       │      └─────────────────┘    │        │
│  └──────────────────┘                             │        │
│                                                     │        │
└─────────────────────────────────────────────────────┼────────┘
                                                      │
                                                      ▼
┌─────────────────────────────────────────────────────────────┐
│ AWS Cloud (Production Environment)                          │
│ - x86_64 ECS Fargate instances                              │
│                                                               │
│  ┌──────────────┐      ┌─────────────────┐                 │
│  │ AWS Cognito  │      │ Application     │                 │
│  │ User Pool    │◀────▶│ Load Balancer   │                 │
│  └──────────────┘      └────────┬────────┘                 │
│                                  │                           │
│                         ┌────────▼────────┐                 │
│                         │ ECS Fargate     │                 │
│                         │ Service         │                 │
│                         │ (x86_64)        │                 │
│                         │                 │                 │
│                         │ ┌─────────────┐ │                 │
│                         │ │ Container   │ │                 │
│                         │ │ - Streamlit │ │                 │
│                         │ │ - Fixed App │ │                 │
│                         │ └─────────────┘ │                 │
│                         └─────────────────┘                 │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Architecture Decision: x86_64 vs ARM64/Graviton

**Context**:
The original Dockerfile specified `--platform=linux/arm64` for Graviton (ARM64) architecture, but SageMaker Code Editor runs on ml.c5.large instances which use x86_64 architecture. This creates an architecture mismatch between the development environment and the Docker build target.

**Problem**:
Building ARM64 containers on x86_64 hosts requires QEMU emulation, which:
- Significantly slows down Docker builds (10x+ slower)
- Can cause build failures for packages with native compilation
- Adds complexity and potential compatibility issues
- Makes debugging more difficult

**Options Evaluated**:

1. **Keep ARM64, Use QEMU Emulation**
   - Pros: Lower ECS Fargate runtime costs (Graviton pricing)
   - Cons: Very slow builds, potential failures, poor developer experience

2. **Switch to x86_64 Architecture** ✅ SELECTED
   - Pros: Fast native builds, no emulation, better stability, consistent architecture
   - Cons: Slightly higher ECS Fargate runtime costs

3. **Use Graviton Build Instance (ml.m6g.large)**
   - Pros: Native ARM64 builds, lower runtime costs
   - Cons: Requires switching instance types, less stable than Code Editor

**Decision**: Switch to x86_64 architecture

**Rationale**:
1. **Stability Priority**: SageMaker AI Code Editor is AWS service team supported and significantly more stable than custom code-server deployments
2. **Developer Experience**: Native builds are 10x+ faster and more reliable
3. **Maintainability**: Consistent architecture between development (x86_64) and deployment (x86_64) simplifies debugging
4. **Cost Trade-off Acceptable**: The incremental cost difference between x86_64 and Graviton ECS Fargate is acceptable given the stability and productivity gains
5. **Backup Option Available**: Can always deploy a custom Graviton-based VS Code Server (code-server) if cost optimization becomes critical

**Implementation**:
```dockerfile
# BEFORE (ARM64/Graviton):
FROM --platform=linux/arm64 python:3.12

# AFTER (x86_64):
FROM --platform=linux/amd64 python:3.12
```

**Impact**:
- Docker builds complete in seconds instead of minutes
- No emulation-related build failures
- Consistent architecture across development and production
- Approximately 20% higher ECS Fargate costs (x86_64 vs Graviton)
- Improved developer workflow and reduced friction

### Component Interaction Flow

1. **Development Phase**: Developer modifies `app.py` in SageMaker Code Editor
2. **Build Phase**: Docker builds container image with fixed code
3. **Deployment Phase**: CDK synthesizes and deploys infrastructure to AWS
4. **Runtime Phase**: User accesses application via ALB → Cognito auth → ECS container

## Components and Interfaces

### 1. Application Code (`app.py`)

**Purpose**: Multi-agent Streamlit application with fixed routing logic

**Key Functions**:
- `determine_action(user_query: str) -> str`: Classifies user queries into action categories
- `determine_kb_action(user_query: str) -> str`: Classifies knowledge base queries
- `main()`: Streamlit application entry point with Cognito authentication

**Infinite Loop Fix Pattern**:
```python
# BEFORE (Infinite Loop - uses agent tool):
def determine_action(user_query):
    response = agent.run(
        prompt=f"Classify: {user_query}",
        tools=[use_agent]  # ❌ Causes infinite recursion
    )
    return response

# AFTER (Fixed - direct LLM classification):
def determine_action(user_query):
    response = llm.generate(
        prompt=f"""Classify the following query into one of these categories:
        - educational_query
        - knowledge_base_query
        - general_query
        
        Query: {user_query}
        
        Return ONLY the category name."""
    )
    return response.strip()
```

**Interfaces**:
- Input: User queries via Streamlit UI
- Output: Classified responses from appropriate agents
- Authentication: Cognito session tokens via environment variables

### 2. Docker Container

**Purpose**: Containerized application package for ECS deployment

**Dockerfile Structure**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY [other files] .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Build Process**:
- Executed from SageMaker Code Editor terminal
- Uses local Docker daemon
- Pushes to Amazon ECR for ECS deployment

### 3. CDK Stack

**Purpose**: Infrastructure-as-code for AWS resource provisioning

**Key Resources**:
- **VPC**: Network infrastructure with public/private subnets
- **Application Load Balancer**: Public-facing entry point
- **ECS Fargate Service**: Containerized application runtime
- **Cognito User Pool**: Authentication and authorization
- **ECR Repository**: Container image storage
- **IAM Roles**: Service permissions

**Deployment Interface**:
```bash
# From SageMaker Code Editor terminal
cd workshop4/deploy_multi_agent/cdk
cdk synth    # Synthesize CloudFormation
cdk deploy   # Deploy to AWS
```

### 4. Cognito Authentication

**Purpose**: User authentication and session management

**Authentication Flow**:
1. User accesses ALB URL
2. ALB redirects to Cognito hosted UI
3. User logs in with credentials
4. Cognito returns session tokens
5. ALB forwards request to ECS with tokens in headers
6. Application validates tokens and creates session

**Session Management**:
- Tokens stored in Streamlit session state
- Logout clears session and redirects to Cognito logout
- Token refresh handled automatically by Cognito

## Data Models

### User Query Classification

```python
class QueryClassification:
    """Result of query classification"""
    category: str  # One of: educational_query, knowledge_base_query, general_query
    confidence: float  # Classification confidence (0.0 to 1.0)
    original_query: str  # Original user input
```

### Agent Response

```python
class AgentResponse:
    """Response from agent execution"""
    content: str  # Response text
    agent_type: str  # Which agent generated response
    execution_time: float  # Time taken to generate response
    error: Optional[str]  # Error message if failed
```

### Cognito Session

```python
class CognitoSession:
    """User authentication session"""
    access_token: str  # Cognito access token
    id_token: str  # Cognito ID token
    username: str  # Authenticated username
    expires_at: datetime  # Token expiration time
```

### Deployment Configuration

```python
class DeploymentConfig:
    """CDK deployment configuration"""
    stack_name: str  # CloudFormation stack name
    region: str  # AWS region
    account_id: str  # AWS account ID
    container_image: str  # ECR image URI
    cognito_user_pool_id: str  # Existing or new user pool
    vpc_id: Optional[str]  # Existing VPC or create new
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Authentication Preservation

*For any* user with valid Cognito credentials, authenticating before and after applying the infinite loop fix should result in successful authentication and session creation in both cases.

**Validates: Requirements 1.4, 2.4**

### Property 2: Infinite Loop Prevention

*For any* user query (educational, knowledge base, or general), when submitted to the routing functions, the query classification should complete within a reasonable timeout (e.g., 10 seconds) without entering infinite recursion.

**Validates: Requirements 2.5, 4.3, 4.4, 6.1, 6.2**

### Property 3: No Recursive Agent Calls

*For any* query processed by the routing functions, the application logs should contain no evidence of recursive `use_agent` tool calls or agent-within-agent invocations.

**Validates: Requirements 6.4**

### Property 4: UI State Preservation

*For any* user session, after applying the infinite loop fix, all UI elements (model selection, agent type selection, clear conversation button) should remain functional and session state should persist correctly across interactions.

**Validates: Requirements 1.5**

### Property 5: Dependency Completeness

*For any* package listed in requirements.txt, when the Docker container is built, that package should be importable within the container environment.

**Validates: Requirements 2.2**

## Error Handling

### Application-Level Error Handling

**Query Processing Errors**:
- Catch exceptions during LLM classification calls
- Display user-friendly error messages in Streamlit UI
- Log detailed error information for debugging
- Fallback to default routing behavior on classification failure

**Authentication Errors**:
- Handle Cognito token expiration gracefully
- Redirect to login page on authentication failure
- Display clear error messages for invalid credentials
- Preserve user's intended destination after re-authentication

**Agent Execution Errors**:
- Catch exceptions during agent tool execution
- Display error messages without exposing internal details
- Log full stack traces for debugging
- Provide retry options for transient failures

### Infrastructure-Level Error Handling

**Container Startup Failures**:
- ECS health checks detect failed containers
- Automatic container restart on failure
- CloudWatch logs capture startup errors
- ALB removes unhealthy targets from rotation

**Deployment Failures**:
- CDK rollback on stack update failure
- Preserve previous working version during failed deployments
- CloudFormation change sets for preview before deployment
- Clear error messages from CDK CLI

**Network and Load Balancer Errors**:
- ALB health checks monitor container health
- Automatic failover to healthy containers
- Connection timeout handling
- 503 errors during zero-healthy-target scenarios

### Monitoring and Alerting

**Key Metrics to Monitor**:
- Query processing time (detect infinite loops)
- Container CPU and memory usage
- Authentication success/failure rates
- Error rates by error type
- Container restart frequency

**Alerting Thresholds**:
- Query processing time > 10 seconds
- Container CPU > 80% for 5 minutes
- Error rate > 5% of requests
- Container restart > 3 times in 10 minutes

## Testing Strategy

### Dual Testing Approach

This deployment requires both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests**: Focus on specific examples, edge cases, and integration points
- Test specific query examples (educational, knowledge base, general)
- Test authentication flow with mock Cognito responses
- Test Docker build with sample configurations
- Test CDK synthesis with known stack configurations
- Test error handling with specific error scenarios

**Property Tests**: Verify universal properties across all inputs
- Test query classification with randomly generated queries
- Test authentication with various credential formats
- Test concurrent request handling with random user counts
- Test dependency installation with random package subsets
- Minimum 100 iterations per property test

### Property-Based Testing Configuration

**Testing Library**: Use `hypothesis` for Python property-based testing

**Test Configuration**:
```python
from hypothesis import given, settings
import hypothesis.strategies as st

@settings(max_examples=100)
@given(query=st.text(min_size=1, max_size=500))
def test_query_classification_completes(query):
    """
    Feature: workshop4-sagemaker-code-editor-deployment
    Property 2: Infinite Loop Prevention
    
    For any user query, classification should complete within timeout.
    """
    # Test implementation
    pass
```

**Test Tags**: Each property test must include a comment referencing the design property:
```python
# Feature: workshop4-sagemaker-code-editor-deployment, Property 2: Infinite Loop Prevention
```

### Testing Phases

**Phase 1: Local Development Testing**
- Run unit tests in SageMaker Code Editor
- Test application locally with `streamlit run app.py`
- Verify infinite loop fix with sample queries
- Test Docker build locally

**Phase 2: Container Testing**
- Build Docker container locally
- Run container with `docker run`
- Test authentication flows in container
- Verify query processing in containerized environment
- Run property tests against containerized application

**Phase 3: Deployment Testing**
- Deploy to AWS using CDK
- Test production URL accessibility
- Test Cognito authentication in production
- Run property tests against production deployment
- Monitor CloudWatch logs for errors

**Phase 4: Production Validation**
- Submit various query types to production
- Monitor query processing times
- Verify no infinite loops in CloudWatch logs
- Test concurrent user scenarios
- Validate authentication flows with real users

### Test Coverage Goals

- Unit test coverage: > 80% of application code
- Property test coverage: All 5 correctness properties
- Integration test coverage: All AWS service interactions
- End-to-end test coverage: Complete user workflows (login → query → logout)

