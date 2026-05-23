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
- [ ] `agentcore deploy -y` to push Phase 3 fixes (pinned fastmcp==3.0.0)
- [ ] Upload Phase 1 & 2 Streamlit app changes to code-server for deploy
- [ ] Re-test "Find courses about artificial intelligence" after deploy to confirm reviews now appear
- [ ] Verify routing path displays correctly across all three phases
- [ ] Verify favicon shows 🎓 across all three phases

## Known Issue: FastMCP Version Pinning (AgentCore Gateway Compatibility)

### Problem
AgentCore Gateway sends MCP tool calls to `/mcp/` (with trailing slash). FastMCP versions newer than 3.0.0 introduced strict trailing-slash redirect behavior (307 Temporary Redirect from `/mcp/` → `/mcp`). The 307 redirect strips the POST body, so the MCP server receives the request with no payload, returns an empty 200, and the gateway thinks the tool returned nothing. This causes an infinite retry loop (76+ tool calls with no results).

### Symptoms
- CloudWatch logs show: `POST /mcp/ HTTP/1.1" 307 Temporary Redirect` followed by `POST /mcp HTTP/1.1" 200 OK` in an infinite loop
- Orchestrator logs show tool calls being made repeatedly (Tool #1, #2, ... #76+) with no results
- Orchestrator eventually gives up and says "tools aren't responding as expected"
- `agentcore invoke --runtime StudentServicesAgent "What services do you offer?"` works (no tool call needed)
- Any query requiring a tool call hangs or times out

### Current Fix
All four MCP server `requirements.txt` files pin `fastmcp==3.0.0` (NOTE: AgentCore runtime ignores this pin — installs 3.3.1 from base image).

**Actual working fix**: Set `path="/mcp/"` in `mcp.run()` to match the trailing-slash path the gateway sends, preventing the 307 redirect.

```python
mcp.run(transport="streamable-http", host="0.0.0.0", stateless_http=True, path="/mcp/")
```

### How to Test if AgentCore Has Caught Up
1. Remove `path="/mcp/"` from all four MCP server `mcp.run()` calls (revert to no path argument)
2. Run `agentcore deploy -y`
3. Test: `agentcore invoke --runtime StudentServicesAgent "Find courses about artificial intelligence"`
4. Check logs: `agentcore logs --runtime CourseReviewMcp --since 5m -n 20`
5. **If you see the 307 redirect pattern** → re-add `path="/mcp/"`
6. **If tool calls succeed without 307 redirects** → AgentCore gateway is fixed, keep without path

### Files to Change
- `workshop4/phase3/studentservices/course_registration/agent.py` — `mcp.run()` path parameter
- `workshop4/phase3/studentservices/course_review/agent.py` — `mcp.run()` path parameter
- `workshop4/phase3/studentservices/loan_application/agent.py` — `mcp.run()` path parameter
- `workshop4/phase3/studentservices/math_teaching/agent.py` — `mcp.run()` path parameter

### Root Cause Timeline
- **Before 2026-05-23**: `fastmcp>=3.0.0,<4` worked (likely fastmcp 3.0.0 was installed)
- **2026-05-23**: Fresh deploy with agentcore 0.15.0 pulled fastmcp 3.3.1 (from base image, ignores requirements.txt pin)
- **FastMCP 3.3.1 behavior**: Default path is `/mcp/` per docs, but AgentCore runtime mounts at `/mcp` — Starlette's `redirect_slashes=True` causes 307 redirect from `/mcp/` → `/mcp`, stripping POST body
- **Fix**: Explicit `path="/mcp/"` in `mcp.run()` forces FastMCP to serve on the trailing-slash path the gateway sends to

## Recovery Plan (for next session)

**Problem**: AgentCore CLI 0.15.0 deploys FastMCP 3.3.1 runtime which breaks tool execution. The 307 redirect is fixed (path="/mcp/" in constructor) but tool results still don't reach the orchestrator.

**Previous working version**: `@aws/agentcore@0.13.1` (confirmed working May 14, 2026)

**Steps:**
1. `npm install -g @aws/agentcore@0.13.1`
2. `cd workshop4/phase3/studentservices`
3. `agentcore deploy -y`
4. `agentcore invoke --runtime StudentServicesAgent "What is 2 + 2?"`
5. If works → test all 4 specialists → done
6. If doesn't work → `agentcore logs --runtime StudentServicesAgent --since 5m --level debug -n 50` and debug from there

**Current code state**: All improvements applied (tool names, system prompts, routing_path, favicon, path="/mcp/"). Do NOT revert code. The issue is the runtime environment version, not the code.

## Lessons Learned
- When using AgentCore Gateway with `toolDefinitions`, the `name` field must exactly match the MCP tool name exposed by the server — semantic search can mask this bug for simple single-tool servers
- Inner agents with multiple tools need explicit workflow instructions in their system prompt — the model won't reliably call all tools without being told to
