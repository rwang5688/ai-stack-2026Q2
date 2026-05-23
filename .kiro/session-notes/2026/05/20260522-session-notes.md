# Session Notes - May 22, 2026

## Session Overview
Debugged Phase 3 AgentCore app — Course Review MCP server could find course catalog (Knowledge Base) but not course reviews (DynamoDB). Root-caused to two issues: tool name mismatch and weak inner agent prompting.

## Key Accomplishments
- Identified tool name mismatch across ALL four MCP servers (gateway `toolDefinitions.name` vs actual FastMCP function names)
- Fixed all four with `@mcp.tool(name="...")` explicit naming
- Strengthened Course Review inner agent system prompt to always call both `search_course_catalog` AND `get_course_reviews`
- Added `routing_path` metadata to all four MCP tool responses for instructional visibility
- Updated orchestrator system prompt to display routing path in responses

## Issues & Resolutions

### Issue 1: Course Review MCP server not returning DynamoDB reviews
- **Symptom**: "Find courses about artificial intelligence" returned catalog results but no student reviews
- **Root Cause (minor)**: Gateway `toolDefinitions` advertised tool name `course_review`, but FastMCP exposed `course_review_assistant`. Same mismatch on all four agents. Mitigated by `enableSemanticSearch: true` on the gateway (semantic matching acted as safety net for the other three).
- **Root Cause (major)**: The inner Strands Agent inside `course_review_assistant` has two sub-tools (`search_course_catalog` + `get_course_reviews`). For vague queries like "find courses about AI", the model only called the catalog search and skipped the reviews lookup because it didn't have a specific course name yet.
- **Resolution**: 
  1. Added `@mcp.tool(name="course_review")` (and equivalent for all four agents)
  2. Rewrote inner agent system prompt with CRITICAL WORKFLOW instructions to always call both tools

### Issue 2: No visibility into distributed routing
- **Symptom**: Students can't tell which AgentCore runtime handled their request
- **Resolution**: Added `routing_path` field to all MCP tool responses showing the full chain (e.g., `StudentServicesAgent → AgentCore Gateway → CourseReviewMcp → course_review_assistant (search_course_catalog + get_course_reviews)`)

## Decisions Made
- Use `@mcp.tool(name="...")` to explicitly match gateway `toolDefinitions` names — don't rely on semantic search as the primary routing mechanism
- Display routing path in UI to demonstrate AgentCore Gateway's distributed routing capability
- Keep `enableSemanticSearch: true` as a safety net but not as the primary matching strategy

## Files Modified
- `workshop4/phase3/studentservices/course_review/agent.py` — tool name fix, stronger system prompt, routing_path
- `workshop4/phase3/studentservices/course_registration/agent.py` — tool name fix, routing_path
- `workshop4/phase3/studentservices/loan_application/agent.py` — tool name fix, routing_path
- `workshop4/phase3/studentservices/math_teaching/agent.py` — tool name fix, routing_path
- `workshop4/phase3/studentservices/student_services/agent.py` — orchestrator prompt updated to display routing_path
- `workshop4/phase1/streamlit_app/app.py` — added 🎓 favicon, upgraded routing display to show full path
- `workshop4/phase2/deploy-streamlit-app/docker_app/app.py` — added 🎓 favicon, upgraded routing display to show full path

## Next Steps
- [ ] `agentcore deploy -y` to push Phase 3 fixes
- [ ] Upload Phase 1 & 2 Streamlit app changes to code-server for deploy
- [ ] Re-test "Find courses about artificial intelligence" after deploy to confirm reviews now appear
- [ ] Verify routing path displays correctly across all three phases
- [ ] Verify favicon shows 🎓 across all three phases

## Lessons Learned
- When using AgentCore Gateway with `toolDefinitions`, the `name` field must exactly match the MCP tool name exposed by the server — semantic search can mask this bug for simple single-tool servers
- Inner agents with multiple tools need explicit workflow instructions in their system prompt — the model won't reliably call all tools without being told to
