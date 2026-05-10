# Design Document

## Overview

This design document outlines the solution for fixing an infinite loop issue in the workshop4 multi-agent Streamlit application when running in SageMaker AI's Code Editor environment. The issue is caused by recursive use of the `use_agent` tool in routing logic, which creates a chain of agents calling agents that never terminates.

The solution replaces agent-based routing with direct LLM classification, eliminating the recursive structure while maintaining the same functionality and user experience.

## Problem Analysis

### Root Cause

The infinite loop is caused by the following pattern in the current implementation:

```python
def determine_action(query, model, model_info):
    """Determine if query should go to teacher or knowledge base."""
    agent = Agent(
        model=model,
        tools=[use_agent]  # ← PROBLEM: Agent has use_agent tool
    )
    
    result = agent.tool.use_agent(  # ← PROBLEM: Calling use_agent creates another agent
        prompt=f"Query: {query}",
        system_prompt=ACTION_DETERMINATION_PROMPT,
        model_provider="bedrock",
        model_settings=model_settings
    )
```

**Why This Causes an Infinite Loop:**

1. Main agent is created with `use_agent` tool
2. Main agent calls `use_agent` tool, which creates a sub-agent
3. Sub-agent may also have access to `use_agent` tool (depending on framework defaults)
4. Sub-agent may call `use_agent` again, creating another sub-agent
5. This continues indefinitely, especially in certain environments where tool inheritance or default tool sets differ

**Environment-Specific Behavior:**

The issue manifests differently across environments:
- **Windows (WorkSpaces)**: May work due to specific Python/framework versions
- **Ubuntu (EC2)**: May work due to specific Python/framework versions
- **SageMaker Code Editor**: Triggers infinite loop due to SageMaker Distribution 3.4.10 configuration

The environment-specific behavior suggests that the Strands Agents framework may have different default tool configurations or inheritance patterns in different environments.

## Solution Architecture

### High-Level Approach

Replace agent-based routing with direct LLM classification:

```
BEFORE (Recursive):
User Query → Main Agent → use_agent tool → Sub-Agent → use_agent tool → Sub-Sub-Agent → ...

AFTER (Direct):
User Query → Main Agent → Direct LLM Call → Classification Result
```

### Key Changes

1. **Remove `use_agent` from routing agents**: Routing agents will NOT have the `use_agent` tool
2. **Use direct agent invocation**: Call the agent directly with a prompt, not through a tool
3. **Keep `use_agent` for answer generation**: Only use `use_agent` in `run_kb_agent()` for final answer generation

## Detailed Design

### 1. Updated `determine_action()` Function

**Purpose**: Determine if query should go to teacher agent or knowledge base agent.

**Current Implementation (Problematic)**:
```python
def determine_action(query, model, model_info):
    agent = Agent(
        model=model,
        tools=[use_agent]  # ← PROBLEM
    )
    
    result = agent.tool.use_agent(  # ← PROBLEM
        prompt=f"Query: {query}",
        system_prompt=ACTION_DETERMINATION_PROMPT,
        model_provider="bedrock",
        model_settings=model_settings
    )
```

**New Implementation (Fixed)**:
```python
def determine_action(query, model, model_info):
    """Determine if query should go to teacher or knowledge base."""
    # Create a simple classification agent WITHOUT use_agent tool
    agent = Agent(
        model=model,
        system_prompt=ACTION_DETERMINATION_PROMPT,
        tools=[]  # ← FIX: No tools, just direct LLM classification
    )
    
    try:
        # Call agent directly with the query
        result = agent(f"Query: {query}")
        
        # Extract classification from response
        action_text = str(result).lower().strip()
        
        # Parse the response
        if "knowledge" in action_text:
            return "knowledge"
        else:
            return "teacher"
    except Exception as e:
        st.error(f"Error determining action: {str(e)}")
        return "teacher"  # Safe fallback
```

**Key Differences**:
- No `use_agent` tool in the agent's tool list
- Direct agent invocation with `agent(prompt)` instead of `agent.tool.use_agent()`
- Simpler, more maintainable code
- No recursive agent creation

### 2. Updated `determine_kb_action()` Function

**Purpose**: Determine if knowledge base query is a store or retrieve action.

**Current Implementation (Problematic)**:
```python
def determine_kb_action(query, model, model_info):
    agent = Agent(
        model=model,
        tools=[use_agent]  # ← PROBLEM
    )
    
    result = agent.tool.use_agent(  # ← PROBLEM
        prompt=f"Query: {query}",
        system_prompt=KB_ACTION_SYSTEM_PROMPT,
        model_provider="bedrock",
        model_settings=model_settings
    )
```

**New Implementation (Fixed)**:
```python
def determine_kb_action(query, model, model_info):
    """Determine if knowledge base query is store or retrieve."""
    # Create a simple classification agent WITHOUT use_agent tool
    agent = Agent(
        model=model,
        system_prompt=KB_ACTION_SYSTEM_PROMPT,
        tools=[]  # ← FIX: No tools, just direct LLM classification
    )
    
    try:
        # Call agent directly with the query
        result = agent(f"Query: {query}")
        
        # Extract classification from response
        action_text = str(result).lower().strip()
        
        # Parse the response
        if "store" in action_text:
            return "store"
        else:
            return "retrieve"
    except Exception as e:
        st.error(f"Error determining KB action: {str(e)}")
        return "retrieve"  # Safe fallback
```

**Key Differences**:
- Same pattern as `determine_action()` fix
- No recursive agent creation
- Direct LLM classification

### 3. Updated `run_kb_agent()` Function

**Purpose**: Process knowledge base queries (store or retrieve).

**Current Implementation**:
```python
def run_kb_agent(query, model, model_info):
    agent = Agent(
        model=model,
        tools=[memory, use_agent]  # ← use_agent used for answer generation
    )
    
    # ... store/retrieve logic ...
    
    # Generate answer using use_agent
    answer = agent.tool.use_agent(
        prompt=f"User question: \"{query}\"\n\nInformation: {result_str}",
        system_prompt=KB_ANSWER_SYSTEM_PROMPT,
        model_provider="bedrock",
        model_settings=model_settings
    )
```

**New Implementation (Partial Fix)**:
```python
def run_kb_agent(query, model, model_info):
    """Process knowledge base query."""
    # Agent needs memory tool for KB operations
    agent = Agent(
        model=model,
        tools=[memory]  # ← Only memory tool, no use_agent
    )
    
    # Determine action using fixed function
    action = determine_kb_action(query, model, model_info)
    
    if action == "store":
        # Store logic unchanged
        result = agent.tool.memory(action="store", content=query)
        return "✅ I've stored this information."
    else:
        # Retrieve logic
        result = agent.tool.memory(
            action="retrieve",
            query=query,
            min_score=MIN_SCORE,
            max_results=MAX_RESULTS
        )
        
        # Generate answer using a SEPARATE agent with use_agent tool
        # This is safe because it's not part of routing logic
        answer_agent = Agent(
            model=model,
            system_prompt=KB_ANSWER_SYSTEM_PROMPT,
            tools=[use_agent]  # ← OK: Only for final answer generation
        )
        
        answer = answer_agent.tool.use_agent(
            prompt=f"User question: \"{query}\"\n\nInformation: {result}",
            system_prompt=KB_ANSWER_SYSTEM_PROMPT,
            model_provider="bedrock",
            model_settings=model_settings
        )
        
        # Parse and return answer
        return parse_answer(answer)
```

**Key Differences**:
- Routing logic uses fixed `determine_kb_action()` function
- Answer generation still uses `use_agent` but in a controlled, non-recursive way
- Clear separation between routing and answer generation

### 4. Alternative Approach: Remove use_agent Entirely from run_kb_agent

**Even Simpler Implementation**:
```python
def run_kb_agent(query, model, model_info):
    """Process knowledge base query."""
    agent = Agent(
        model=model,
        tools=[memory]
    )
    
    action = determine_kb_action(query, model, model_info)
    
    if action == "store":
        result = agent.tool.memory(action="store", content=query)
        return "✅ I've stored this information."
    else:
        result = agent.tool.memory(
            action="retrieve",
            query=query,
            min_score=MIN_SCORE,
            max_results=MAX_RESULTS
        )
        
        # Generate answer using direct agent call (no use_agent tool)
        answer_agent = Agent(
            model=model,
            system_prompt=KB_ANSWER_SYSTEM_PROMPT,
            tools=[]  # ← No tools needed for answer generation
        )
        
        answer = answer_agent(
            f"User question: \"{query}\"\n\nInformation from knowledge base:\n{result}\n\n"
            "Provide a helpful answer based on this information."
        )
        
        return str(answer).strip()
```

**Advantages**:
- Completely eliminates `use_agent` tool from the application
- Simpler, more maintainable code
- No risk of recursive agent creation anywhere
- Easier to debug and understand

**Disadvantages**:
- May lose some answer quality if `use_agent` provides better formatting
- Need to test answer quality to ensure it's acceptable

## Implementation Strategy

### Phase 1: Fix Routing Logic (Critical)

1. Update `determine_action()` to remove `use_agent` tool
2. Update `determine_kb_action()` to remove `use_agent` tool
3. Test routing decisions work correctly
4. Verify no infinite loops in SageMaker Code Editor

### Phase 2: Update Answer Generation (Optional)

1. Decide whether to keep `use_agent` for answer generation or remove it entirely
2. If keeping: Ensure it's only used for final answer generation, not routing
3. If removing: Test answer quality and adjust prompts as needed
4. Verify answers are clear and conversational

### Phase 3: Deploy and Test

1. Apply fix to `multi_agent/app.py`
2. Test in SageMaker Code Editor environment
3. Test in Windows and Ubuntu environments
4. Copy fix to `deploy_multi_agent/docker_app/app.py`
5. Deploy to ECS Fargate and test

## Testing Strategy

### Unit Tests

1. **Test `determine_action()` classification**:
   - Educational queries → "teacher"
   - Knowledge base queries → "knowledge"
   - Edge cases and ambiguous queries

2. **Test `determine_kb_action()` classification**:
   - Store queries → "store"
   - Retrieve queries → "retrieve"
   - Edge cases and ambiguous queries

3. **Test `run_kb_agent()` functionality**:
   - Store operations work correctly
   - Retrieve operations work correctly
   - Answer generation produces clear responses

### Integration Tests

1. **Test full user flows**:
   - Educational query → Teacher agent → Specialized assistant → Response
   - Knowledge store → Confirmation message
   - Knowledge retrieve → Clear answer
   - Auto-route correctly determines agent type

2. **Test in all environments**:
   - Windows (Amazon WorkSpaces)
   - Ubuntu (Graviton EC2)
   - SageMaker Code Editor (ml.c5.large)

### Performance Tests

1. **Response time**: Queries should complete in < 30 seconds
2. **No infinite loops**: Application should never hang or loop indefinitely
3. **Resource usage**: Memory and CPU should remain reasonable

## Correctness Properties

### Property 1: Routing Termination
*For any* user query, the routing logic SHALL complete within a finite number of steps and return a classification decision.

### Property 2: Classification Consistency
*For any* user query, calling the routing function multiple times with the same query SHALL return the same classification (within the same session).

### Property 3: No Recursive Agent Creation
*For any* routing decision, the implementation SHALL NOT create agents that have the `use_agent` tool in their tool list.

### Property 4: Answer Quality Preservation
*For any* knowledge base retrieval, the generated answer SHALL be clear, conversational, and based on the retrieved information.

### Property 5: Environment Portability
*For any* supported environment (Windows, Ubuntu, SageMaker Code Editor), the application SHALL function identically without environment-specific code.

## Error Handling

### Routing Errors
- **LLM returns unclear response**: Default to safe fallback ("teacher" or "retrieve")
- **Agent creation fails**: Log error, return fallback value
- **Timeout**: Return fallback value after reasonable timeout

### Knowledge Base Errors
- **Store fails**: Return error message to user
- **Retrieve fails**: Return "no information found" message
- **Answer generation fails**: Return raw retrieved data or error message

## Rollback Plan

If the fix causes issues:
1. Revert to previous version of `app.py`
2. Document the specific failure mode
3. Analyze why the fix didn't work
4. Develop alternative solution

## Future Improvements

1. **Add caching**: Cache routing decisions for identical queries
2. **Add metrics**: Track routing accuracy and response times
3. **Add logging**: Log all routing decisions for debugging
4. **Optimize prompts**: Improve classification accuracy with better prompts
5. **Add retry logic**: Retry failed classifications with exponential backoff
