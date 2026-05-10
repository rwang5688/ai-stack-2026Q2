# Requirements Document

## Introduction

This feature addresses an infinite loop issue occurring when running the workshop4 multi-agent Streamlit application in SageMaker AI's Code Editor environment (VS Code Server on SageMaker AI). The issue manifests as repeated "Use agent tool" calls that never terminate, preventing the application from functioning properly. This fix will enable developers to build and test the application locally in Code Editor before deploying to ECS Fargate.

## Glossary

- **SageMaker_Code_Editor**: VS Code Server running on SageMaker AI's managed infrastructure (ml.c5.large instance with SageMaker Distribution 3.4.10)
- **Infinite_Loop**: A condition where the application repeatedly calls the same tool without terminating
- **Use_Agent_Tool**: A Strands Agents framework tool that allows one agent to invoke another agent
- **Routing_Agent**: An agent used to determine which specialized agent should handle a query
- **Teacher_Agent**: The main orchestrator agent that routes queries to specialized assistants
- **Knowledge_Base_Agent**: An agent that handles storing and retrieving personal information
- **Tool_Recursion**: When a tool calls itself or creates a circular dependency chain
- **Direct_Classification**: Using the LLM's native capabilities to classify queries without creating additional agents

## Requirements

### Requirement 1: Identify Root Cause of Infinite Loop

**User Story:** As a developer, I want to understand why the infinite loop occurs in SageMaker Code Editor, so that I can implement an appropriate fix.

#### Acceptance Criteria

1. THE investigation SHALL analyze the `determine_action()` function that uses `use_agent` tool
2. THE investigation SHALL analyze the `determine_kb_action()` function that uses `use_agent` tool
3. THE investigation SHALL analyze the `run_kb_agent()` function that uses `use_agent` tool
4. THE investigation SHALL identify if the issue is environment-specific (SageMaker Code Editor vs Windows vs Ubuntu)
5. THE investigation SHALL document the exact sequence of tool calls that creates the loop
6. THE investigation SHALL determine if the issue is related to agent recursion or tool configuration

### Requirement 2: Eliminate Use of use_agent Tool for Routing

**User Story:** As a developer, I want to remove the use_agent tool from routing logic, so that the application doesn't create recursive agent calls.

#### Acceptance Criteria

1. THE `determine_action()` function SHALL NOT use the `use_agent` tool
2. THE `determine_kb_action()` function SHALL NOT use the `use_agent` tool
3. THE `run_kb_agent()` function SHALL use `use_agent` tool ONLY for final answer generation (not for routing)
4. WHEN routing decisions are needed, THE application SHALL use direct LLM calls instead of creating new agents
5. THE routing logic SHALL maintain the same classification accuracy as the original implementation
6. THE routing logic SHALL be simpler and more maintainable than the original implementation

### Requirement 3: Implement Direct LLM Classification for Routing

**User Story:** As a developer, I want to use direct LLM calls for routing decisions, so that I avoid creating recursive agent structures.

#### Acceptance Criteria

1. THE `determine_action()` function SHALL create a simple Agent instance without the `use_agent` tool
2. THE `determine_kb_action()` function SHALL create a simple Agent instance without the `use_agent` tool
3. WHEN determining routing, THE agent SHALL use its native LLM capabilities to classify the query
4. THE agent SHALL return a simple text response ("teacher" or "knowledge", "store" or "retrieve")
5. THE implementation SHALL parse the LLM response to extract the classification decision
6. THE implementation SHALL handle edge cases where the LLM response is unclear or malformed
7. THE implementation SHALL default to safe fallback values when classification fails

### Requirement 4: Maintain Knowledge Base Answer Generation

**User Story:** As a user, I want knowledge base answers to remain clear and conversational, so that the user experience is not degraded by the fix.

#### Acceptance Criteria

1. THE `run_kb_agent()` function SHALL continue using `use_agent` tool for answer generation ONLY
2. WHEN generating answers from knowledge base results, THE function SHALL use `use_agent` with Bedrock model
3. THE answer generation SHALL NOT be part of the routing logic
4. THE answer generation SHALL occur AFTER the store/retrieve action is determined
5. THE answer quality SHALL be equivalent to the original implementation

### Requirement 5: Test in SageMaker Code Editor Environment

**User Story:** As a developer, I want to verify the fix works in SageMaker Code Editor, so that I can confidently develop and test locally before deploying.

#### Acceptance Criteria

1. THE application SHALL run without infinite loops in SageMaker Code Editor environment
2. WHEN a user submits a query, THE application SHALL respond within a reasonable time (< 30 seconds)
3. THE application SHALL correctly route educational queries to the teacher agent
4. THE application SHALL correctly route knowledge base queries to the knowledge base agent
5. THE application SHALL correctly determine store vs retrieve actions for knowledge base queries
6. THE application SHALL generate clear, conversational answers for knowledge base retrievals
7. THE testing SHALL verify all three agent types: Auto-Route, Teacher Agent, and Knowledge Base

### Requirement 6: Maintain Compatibility with Other Environments

**User Story:** As a developer, I want the fix to work across all environments (Windows, Ubuntu, SageMaker Code Editor), so that the application is portable.

#### Acceptance Criteria

1. THE fix SHALL work on Windows (Amazon WorkSpaces)
2. THE fix SHALL work on Ubuntu (Graviton EC2 instances)
3. THE fix SHALL work on SageMaker Code Editor (ml.c5.large with SageMaker Distribution 3.4.10)
4. THE fix SHALL NOT introduce environment-specific code or configuration
5. THE fix SHALL maintain the same functionality across all environments

### Requirement 7: Update Deployment Application

**User Story:** As a developer, I want the fix applied to the deployment version, so that the deployed application also benefits from the fix.

#### Acceptance Criteria

1. THE fix SHALL be applied to `multi_agent/app.py` first (local development)
2. THE fix SHALL be copied to `deploy_multi_agent/docker_app/app.py` (cloud deployment)
3. THE deployment version SHALL preserve Cognito authentication logic
4. THE deployment version SHALL maintain all existing functionality
5. THE fix SHALL be tested in both local and deployed environments

### Requirement 8: Document the Issue and Solution

**User Story:** As a developer, I want clear documentation of the issue and solution, so that future developers understand the fix and can avoid similar issues.

#### Acceptance Criteria

1. THE session notes SHALL document the infinite loop issue
2. THE session notes SHALL document the root cause analysis
3. THE session notes SHALL document the solution approach
4. THE session notes SHALL document testing results in SageMaker Code Editor
5. THE documentation SHALL include recommendations for avoiding similar issues in the future
6. THE documentation SHALL explain why `use_agent` tool should not be used for routing logic

## Out of Scope

- Refactoring the entire multi-agent architecture
- Changing the Strands Agents framework itself
- Optimizing performance beyond fixing the infinite loop
- Adding new features or capabilities to the application
- Modifying the specialized assistant agents (math, english, etc.)

## Success Criteria

The feature is successful when:
1. The application runs without infinite loops in SageMaker Code Editor
2. All routing logic works correctly without using `use_agent` tool for classification
3. Knowledge base answer generation continues to work with `use_agent` tool
4. The application works across all three environments (Windows, Ubuntu, SageMaker Code Editor)
5. The fix is deployed to both local and cloud versions
6. Documentation clearly explains the issue and solution
