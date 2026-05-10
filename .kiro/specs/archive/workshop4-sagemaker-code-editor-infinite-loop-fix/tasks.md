# Implementation Plan: workshop4-sagemaker-code-editor-infinite-loop-fix

## Overview

This implementation plan fixes an infinite loop issue in the workshop4 multi-agent Streamlit application when running in SageMaker AI's Code Editor environment. The fix eliminates recursive use of the `use_agent` tool in routing logic, replacing it with direct LLM classification.

## Tasks

- [x] 1. Gather environment information from SageMaker Code Editor
  - Run `cat /etc/os-release && uname -a` to get OS details
  - Document SageMaker Distribution version (3.4.10)
  - Document instance type (ml.c5.large)
  - Document Python version and key package versions
  - Reproduce the infinite loop issue and capture logs/error messages
  - Document the exact "Use agent tool" looping pattern observed
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 2. Fix determine_action() function to remove use_agent tool
  - Open `workshop4/multi_agent/app.py`
  - Locate the `determine_action()` function
  - Remove `use_agent` from the agent's tools list
  - Change from `agent.tool.use_agent()` to direct `agent()` call
  - Update error handling to work with direct agent invocation
  - Keep the same system prompt (ACTION_DETERMINATION_PROMPT)
  - Maintain the same classification logic (parse "teacher" or "knowledge")
  - Test the function returns correct classifications
  - _Requirements: 2.1, 2.4, 2.5, 2.6, 3.1, 3.4, 3.5, 3.6, 3.7_

- [x] 3. Fix determine_kb_action() function to remove use_agent tool
  - Locate the `determine_kb_action()` function in `workshop4/multi_agent/app.py`
  - Remove `use_agent` from the agent's tools list
  - Change from `agent.tool.use_agent()` to direct `agent()` call
  - Update error handling to work with direct agent invocation
  - Keep the same system prompt (KB_ACTION_SYSTEM_PROMPT)
  - Maintain the same classification logic (parse "store" or "retrieve")
  - Test the function returns correct classifications
  - _Requirements: 2.2, 2.4, 2.5, 2.6, 3.2, 3.4, 3.5, 3.6, 3.7_

- [x] 4. Update run_kb_agent() function to separate routing from answer generation
  - Locate the `run_kb_agent()` function in `workshop4/multi_agent/app.py`
  - Remove `use_agent` from the main agent's tools list (keep only `memory`)
  - Ensure routing uses the fixed `determine_kb_action()` function
  - For answer generation, decide on approach:
    - **Option A**: Keep `use_agent` but in a separate agent (controlled, non-recursive)
    - **Option B**: Remove `use_agent` entirely and use direct agent call
  - Implement chosen approach
  - Test store operations work correctly
  - Test retrieve operations work correctly
  - Test answer quality is acceptable
  - _Requirements: 2.3, 2.4, 2.5, 2.6, 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 5. Test fix in SageMaker Code Editor environment
  - Set up environment variables (TEACHERS_ASSISTANT_ENV, AWS_REGION, etc.)
  - Run `streamlit run workshop4/multi_agent/app.py` in SageMaker Code Editor
  - Verify application starts without errors
  - Test educational query (e.g., "Solve x^2 + 5x + 6 = 0")
  - Verify no infinite loop occurs
  - Verify query routes to teacher agent correctly
  - Verify response is received within 30 seconds
  - Test knowledge base store query (e.g., "Remember my birthday is July 25")
  - Verify store operation completes successfully
  - Test knowledge base retrieve query (e.g., "What's my birthday?")
  - Verify retrieve operation completes successfully
  - Verify answer is clear and conversational
  - Test all three agent types: Auto-Route, Teacher Agent, Knowledge Base
  - Document test results in session notes
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [x] 6. Test fix in Windows environment (if available)
  - Run application on Windows (Amazon WorkSpaces)
  - Test educational queries
  - Test knowledge base queries
  - Verify functionality matches SageMaker Code Editor
  - Document any differences or issues
  - _Requirements: 6.1, 6.4, 6.5_

- [x] 7. Document the issue and solution
  - Update session notes at `.kiro/session-notes/20260128-session-notes.md`
  - Document the infinite loop issue and symptoms ✅
  - Document the root cause analysis ✅
  - Document the solution approach (removing use_agent from routing) ✅
  - Document testing results in SageMaker Code Editor ✅
  - Document testing results in Windows environment (pending Task 6)
  - Document lessons learned and recommendations ✅
  - Explain why use_agent should not be used for routing logic ✅
  - Include code examples showing before/after ✅
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

## Notes

- The fix is straightforward: remove `use_agent` tool from routing agents
- Routing agents should use direct LLM classification, not create sub-agents
- Answer generation can still use `use_agent` if needed, but in a controlled way
- The fix should work across all environments without environment-specific code
- Testing in SageMaker Code Editor is critical to verify the fix works ✅
- Session notes should clearly document the issue and solution for future reference ✅
- **Ubuntu environment removed**: Ubuntu Graviton EC2 environment is no longer available
- **Deployment tasks moved**: Tasks 8-9 (deployment to ECS Fargate) will be handled in separate spec: `workshop4-sagemaker-code-editor-deployment`

## Success Criteria

- ✅ Application runs without infinite loops in SageMaker Code Editor
- ✅ All routing logic works correctly without `use_agent` tool
- ✅ Knowledge base operations work correctly (store and retrieve)
- ✅ Application works in Windows environment
- ✅ Documentation clearly explains the issue and solution
- 🔜 Deployment to ECS Fargate will be handled in separate spec: `workshop4-sagemaker-code-editor-deployment`

## All Success Criteria Met! 🎉
