# Design Document

## Overview

This design covers the refactoring of workshop4 phases 1, 2, and 3 to achieve:
1. **Singular naming** — rename `course_reviews` → `course_review` across all infrastructure (DynamoDB, Cognito, AgentCore, MCP server directory)
2. **Directory flattening** — Phase 1 and Phase 2 move from per-agent subdirectories to a flat `student_services/` package
3. **Agent modularization** — Phase 3 splits the monolithic `agent.py` into one file per agent within `student_services/`

Execution order: Singular Naming (infra) → Phase 1 Flattening → Phase 2 Flattening → Phase 3 Modularization.

All deployments run on the Ubuntu code-server. The DynamoDB table rename is destructive (CloudFormation DELETE + CREATE) — data must be re-seeded after stack update.

## Architecture

### Before (Current State)

```
workshop4/
├── phase1/
│   ├── cloudformation/student-services-infra.yaml  (course_reviews table)
│   ├── streamlit_app/
│   │   ├── course_review_agent/agent.py
│   │   ├── course_registration_agent/agent.py
│   │   ├── loan_application_agent/agent.py
│   │   ├── math_teaching_agent/agent.py
│   │   ├── student_services_agent/agent.py
│   │   └── shared/
│   └── config.py  (get_course_reviews_table)
├── phase2/
│   └── deploy-streamlit-app/docker_app/
│       ├── course_review_agent/agent.py
│       ├── course_registration_agent/agent.py
│       ├── loan_application_agent/agent.py
│       ├── math_teaching_agent/agent.py
│       ├── student_services_agent/agent.py
│       ├── shared/
│       └── utils/
└── phase3/
    ├── cloudformation/student-services-agentcore-infra.yaml  (CourseReviews* resources)
    └── studentservices/
        ├── agentcore/agentcore.json  (CourseReviewsMcp)
        ├── course_reviews/server.py
        └── student_services/agent.py  (monolithic)
```

### After (Target State)

```
workshop4/
├── phase1/
│   ├── cloudformation/student-services-infra.yaml  (course_review table)
│   ├── streamlit_app/
│   │   ├── student_services/
│   │   │   ├── __init__.py
│   │   │   ├── student_services_agent.py
│   │   │   ├── course_review_agent.py
│   │   │   ├── course_registration_agent.py
│   │   │   ├── loan_application_agent.py
│   │   │   └── math_teaching_agent.py
│   │   └── shared/
│   └── config.py  (get_course_review_table)
├── phase2/
│   └── deploy-streamlit-app/docker_app/
│       ├── student_services/
│       │   ├── __init__.py
│       │   ├── student_services_agent.py
│       │   ├── course_review_agent.py
│       │   ├── course_registration_agent.py
│       │   ├── loan_application_agent.py
│       │   └── math_teaching_agent.py
│       ├── shared/
│       └── utils/
└── phase3/
    ├── cloudformation/student-services-agentcore-infra.yaml  (CourseReview* resources)
    └── studentservices/
        ├── agentcore/agentcore.json  (CourseReviewMcp)
        ├── course_review/server.py
        └── student_services/
            ├── __init__.py
            ├── student_services_agent.py
            ├── course_review_agent.py
            ├── course_registration_agent.py
            ├── loan_application_agent.py
            ├── math_teaching_agent.py
            └── calculator.py
```

## Components and Interfaces

### Component 1: CloudFormation Infrastructure (Phase 1 stack)

**File**: `workshop4/phase1/cloudformation/student-services-infra.yaml`

Changes:
- `CourseReviewsTable` → `CourseReviewTable` (logical ID)
- `course_reviews` → `course_review` (physical table name)
- `SSMCourseReviewsTable` → `SSMCourseReviewTable` (logical ID)
- `/student-services/course-reviews-table` → `/student-services/course-review-table` (SSM path)
- Output key `CourseReviewsTableName` → `CourseReviewTableName`
- Export name `${AWS::StackName}-CourseReviewsTable` → `${AWS::StackName}-CourseReviewTable`

**Impact**: Stack update will DELETE the old `course_reviews` table and CREATE `course_review`. Data loss is expected — re-seed after update.

### Component 2: CloudFormation Infrastructure (Phase 3 stack)

**File**: `workshop4/phase3/cloudformation/student-services-agentcore-infra.yaml`

Changes (all `CourseReviews*` → `CourseReview*`):
- `CourseReviewsExecutionRole` → `CourseReviewExecutionRole`
- Role name: `CourseReviews-execution-role` → `CourseReview-execution-role`
- `CourseReviewsUserPool` → `CourseReviewUserPool`
- Pool name: `course-reviews-user-pool` → `course-review-user-pool`
- `CourseReviewsUserPoolDomain` → `CourseReviewUserPoolDomain`
- Domain: `course-reviews-${AccountId}` → `course-review-${AccountId}`
- `CourseReviewsResourceServer` → `CourseReviewResourceServer`
- Identifier: `course-reviews` → `course-review`
- `CourseReviewsAppClient` → `CourseReviewAppClient`
- Scope: `course-reviews/access` → `course-review/access`
- All corresponding outputs renamed

**Impact**: Stack update will DELETE old Cognito pools and CREATE new ones. New pool IDs must be captured and updated in `agentcore.json`.

### Component 3: AgentCore Configuration

**File**: `workshop4/phase3/studentservices/agentcore/agentcore.json`

Changes:
- Runtime name: `CourseReviewsMcp` → `CourseReviewMcp`
- Runtime `executionRoleArn`: references `CourseReview-execution-role`
- Runtime `codeLocation`: `./course_reviews/` → `./course_review/`
- Runtime `allowedScopes`: `course-reviews/access` → `course-review/access`
- Runtime `discoveryUrl`: updated to new Cognito pool ID (from stack output)
- Credential name: `CourseReviewsMcp-oauth` → `CourseReviewMcp-oauth`
- Credential `scopes`: `course-reviews/access` → `course-review/access`
- Credential `discoveryUrl`: updated to new Cognito pool ID
- Gateway target name: `coursereviews` → `coursereview`
- Gateway target `credentialName`: `CourseReviewsMcp-oauth` → `CourseReviewMcp-oauth`
- Gateway target `endpoint`: will contain new runtime ARN after deploy

### Component 4: MCP Server Directory Rename

**Action**: Rename `studentservices/course_reviews/` → `studentservices/course_review/`

**File change in `course_review/server.py`**:
- `COURSE_REVIEWS_TABLE` env var → `COURSE_REVIEW_TABLE`
- Default value: `"course_reviews"` → `"course_review"`
- Tool name `get_course_reviews` remains unchanged (public API)

### Component 5: Phase 1 Directory Flattening

**Strategy**: Create new `streamlit_app/student_services/` package, move agent code from `{agent_name}/agent.py` into `student_services/{agent_name}.py`, delete old subdirectories.

Each agent file keeps its existing logic but updates imports:
- `sys.path` hacks removed (no longer needed with flat package)
- `from config import ...` stays the same (config.py is at streamlit_app level)
- `from shared.model_factory import ...` stays the same

**`student_services/__init__.py`**:
```python
from .student_services_agent import create_orchestrator
```

**`app.py` import change**:
```python
# Before:
from student_services_agent.agent import create_orchestrator
# After:
from student_services.student_services_agent import create_orchestrator
```

**`config.py` change**:
```python
# Before:
def get_course_reviews_table() -> str:
    return _get_param("course-reviews-table", "COURSE_REVIEWS_TABLE", "course_reviews")
# After:
def get_course_review_table() -> str:
    return _get_param("course-review-table", "COURSE_REVIEW_TABLE", "course_review")
```

### Component 6: Phase 2 Directory Flattening

Identical pattern to Phase 1. Create `docker_app/student_services/` package, move agent code, delete old subdirectories.

**`app.py` import change**:
```python
# Before:
from student_services_agent.agent import create_orchestrator
# After:
from student_services.student_services_agent import create_orchestrator
```

**`config.py` change**: Same as Phase 1 (`get_course_reviews_table` → `get_course_review_table`).

### Component 7: Phase 3 Agent Modularization

**Strategy**: Split the monolithic `student_services/agent.py` (~280 lines) into:

| File | Contents |
|------|----------|
| `student_services_agent.py` | BedrockAgentCoreApp, orchestrator prompt, `get_model_config`, OAuth2 token mgmt, `get_mcp_client`, `invoke` entrypoint, `if __name__` |
| `course_review_agent.py` | `COURSE_REVIEW_AGENT_PROMPT`, `@tool course_review_agent()` function |
| `course_registration_agent.py` | `COURSE_REGISTRATION_AGENT_PROMPT`, `@tool course_registration_agent()` function |
| `loan_application_agent.py` | `LOAN_APPLICATION_AGENT_PROMPT`, `@tool loan_application_agent()` function |
| `math_teaching_agent.py` | `MATH_TEACHING_AGENT_PROMPT`, `@tool math_teaching_agent()` function, imports `calculator` from sibling |
| `calculator.py` | `ALLOWED_NAMES` dict, `@tool calculator()` function |
| `__init__.py` | Empty or minimal (enables package imports) |

**Import pattern** (specialist agents):
```python
# In course_review_agent.py:
from .student_services_agent import get_model_config, get_mcp_client
```

**Import pattern** (orchestrator):
```python
# In student_services_agent.py:
from .course_review_agent import course_review_agent
from .course_registration_agent import course_registration_agent
from .loan_application_agent import loan_application_agent
from .math_teaching_agent import math_teaching_agent
```

**`agentcore.json` change**: `StudentServicesAgent` runtime `entrypoint`: `agent.py` → `student_services_agent.py`

### Component 8: Seed Data Script

**File**: `workshop4/phase1/scripts/populate_seed_data.py` (or `populate-seed-data.sh`)

Changes:
- Reference `CourseReviewTableName` output key (was `CourseReviewsTableName`)
- Variable assignment reads from new output key
- Still reads from `data/course_reviews.csv` (file unchanged)
- Still uploads to S3 as `dynamodb/course_reviews.csv` (key unchanged)

## Data Models

No data model changes. The DynamoDB table schema remains identical:
- Table: `course_review` (was `course_reviews`)
- Partition key: `course_name` (String)
- Billing: PAY_PER_REQUEST

The CSV data file `course_reviews.csv` retains its plural name.

## Error Handling

### Destructive Operations

| Operation | Risk | Mitigation |
|-----------|------|------------|
| Phase 1 CFn stack update (DynamoDB rename) | Table deleted, data lost | Re-run seed script after update |
| Phase 3 CFn stack update (Cognito rename) | Pools deleted, new IDs | Capture new pool IDs from outputs, update agentcore.json |
| AgentCore redeploy | Runtime endpoints change | Update gateway target endpoints in agentcore.json |

### Rollback Strategy

- **Phase 1 infra**: Revert CloudFormation template and update stack (recreates old table, re-seed)
- **Phase 3 infra**: Revert CloudFormation template and update stack (recreates old pools)
- **Code changes**: Git revert — all code changes are file moves/renames with no data dependencies
- **AgentCore**: Revert `agentcore.json` and `agentcore deploy -y`

### Validation Gates

Each phase must pass before proceeding:
1. **Singular Naming**: Stack updates succeed, seed data loads into new table
2. **Phase 1**: `streamlit run app.py` starts without import errors
3. **Phase 2**: Docker build succeeds, app starts without import errors
4. **Phase 3**: `agentcore deploy -y` succeeds, `agentcore invoke` returns valid response

## Correctness Properties

### Property 1: Structural Consistency

Each phase's `student_services/` directory contains exactly 5 agent Python files (`student_services_agent.py`, `course_registration_agent.py`, `course_review_agent.py`, `loan_application_agent.py`, `math_teaching_agent.py`) plus an `__init__.py`. No per-agent subdirectories remain in Phase 1 or Phase 2, and no monolithic `agent.py` remains in Phase 3.

**Validates: Requirements 5.1, 5.2, 6.1, 6.2, 7.1, 7.2**

### Property 2: Import Correctness

All Python modules across all three phases resolve without `ImportError` or `AttributeError` when the application starts. This is verified by running `python -c "from student_services.student_services_agent import ..."` in each phase's directory.

**Validates: Requirements 5.6, 6.8, 8.6**

### Property 3: Naming Consistency

All references to `course_reviews` (plural) are replaced with `course_review` (singular) in infrastructure (CloudFormation logical IDs, physical names, SSM parameters), configuration (`agentcore.json` runtime/credential/gateway names), and Python code (environment variables, config functions) — with the sole exception of the source data file `course_reviews.csv` and the MCP tool name `get_course_reviews`.

**Validates: Requirements 1.1, 1.2, 2.1, 2.4, 2.5, 3.1, 3.3, 3.4, 4.1, 8.1, 8.2, 8.3, 9.1**

### Property 4: Functional Equivalence

Each phase produces identical agent routing behavior before and after refactoring. A query about courses routes to the course review agent, a registration request routes to the registration agent, loan predictions route to the loan agent, and math questions route to the math agent.

**Validates: Requirements 7.8, 4.5**

## Testing Strategy

Property-based testing is **not applicable** to this feature. This is a refactoring of infrastructure configuration (CloudFormation), directory structure (file moves), and import paths — none of which involve pure functions with varying inputs.

### Appropriate Testing Approaches

1. **Import validation** (all phases): Run `python -c "from student_services import create_orchestrator"` to verify no import errors after restructuring.

2. **Smoke tests** (per phase):
   - Phase 1: Launch Streamlit app, verify it renders without errors
   - Phase 2: Docker build succeeds, container starts
   - Phase 3: `agentcore invoke "What courses are available?"` returns a valid response

3. **CloudFormation validation**: `aws cloudformation validate-template` on both modified templates before deploying.

4. **Manual verification**: After each phase, confirm the application routes a query to a specialist agent and returns a response.

### Why PBT Does Not Apply

- CloudFormation changes are declarative IaC configuration — validated by stack deployment, not property tests
- Directory restructuring is a one-time file move operation — no input variation
- Import path updates are deterministic string replacements — verified by Python's import system
- Config function renames are simple find-and-replace — verified by running the app
