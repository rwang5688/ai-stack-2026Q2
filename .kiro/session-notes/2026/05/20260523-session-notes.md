# Session Notes - May 23, 2026

## RECOVERY PLAN (DO THIS FIRST)

### What Happened
On May 22, we upgraded AgentCore CLI from 0.13.1 to 0.15.0 and redeployed Phase 3. The new runtime environment ships FastMCP 3.3.1 which is incompatible with the AgentCore Gateway. ALL four MCP specialist tools (math, loan, registration, course review) stopped working. The orchestrator can't get tool results back from any specialist.

### What Was Working Before (May 14, agentcore@0.13.1)
- All 4 specialists worked: math, loan, registration, course review
- Agent-inside-MCP pattern (Strands Agent wrapped in FastMCP @mcp.tool()) worked perfectly
- Only issue was course review not looking up DynamoDB reviews (prompt issue, not transport)

### Current Broken State
- AgentCore CLI: 0.15.0
- Runtime installs FastMCP 3.3.1 (ignores requirements.txt pin)
- 307 redirect fixed (path="/mcp/" in constructor) — MCP servers now return 200
- BUT tool results still don't reach the orchestrator — all tool calls "fail" silently
- Orchestrator falls back to answering directly or says "system initialization delay"

### Recovery Steps

**Step 1: Downgrade AgentCore CLI (Windows)**
```powershell
Remove-Item -Recurse -Force "$env:APPDATA\npm\node_modules\@aws\agentcore"
npm install -g @aws/agentcore@0.13.1
agentcore --version
```
If Remove-Item fails with EPERM: close ALL terminals/PowerShell windows, open a fresh one, try again.

**Step 1b: Downgrade AgentCore CLI (Ubuntu/code-server)**
```bash
sudo rm -rf /usr/lib/node_modules/@aws/agentcore
sudo npm install -g @aws/agentcore@0.13.1
agentcore --version
```

**Step 2: Deploy (from Windows)**
```powershell
cd D:\Users\wangrob\workspace\ai-stack-2026Q2\workshop4\phase3\studentservices
agentcore deploy -y
```

**Step 3: Test ALL specialists**
```powershell
agentcore invoke --runtime StudentServicesAgent "What is 2 + 2?"
agentcore invoke --runtime StudentServicesAgent "Find courses about artificial intelligence"
agentcore invoke --runtime StudentServicesAgent "Register student STU001 for CS 441 in Fall 2026"
agentcore invoke --runtime StudentServicesAgent "Will a person with these features accept the loan: 29,2,999,0,1,0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0"
```

**Step 4: If Step 3 works → verify course review pulls BOTH catalog AND reviews**
The course review system prompt was strengthened to force both tools. Test with:
```powershell
agentcore invoke --runtime StudentServicesAgent "What are the most challenging courses?"
```
Expected: Should show difficulty ratings, workload hours, student ratings (from DynamoDB) — not just course names (from catalog).

**Step 5: If Step 3 fails → check logs**
```powershell
agentcore logs --runtime StudentServicesAgent --since 5m --level debug -n 50
agentcore logs --runtime MathTeachingMcp --since 5m -n 20
```

### If Downgrade to 0.13.1 Fails (npm install error)
Try:
```powershell
Remove-Item -Recurse -Force "$env:APPDATA\npm\node_modules\@aws\agentcore"
npm install -g @aws/agentcore@0.13.1
```

### Code Changes Made (ALL are correct, do NOT revert)
1. `@mcp.tool(name="course_review")` etc. — fixes tool name mismatch with gateway
2. Course review system prompt — forces both catalog + reviews lookup
3. `routing_path` in all MCP tool responses — shows distributed routing in UI
4. Orchestrator system prompt — aggressive routing, displays routing_path
5. `path="/mcp/"` in FastMCP constructor — fixes 307 redirect (needed for 3.3.1)
6. `path="/mcp/"` in mcp.run() — same fix at runtime level
7. `fastmcp==3.0.0` in requirements.txt — attempted pin (runtime ignores it)
8. Phase 1 & 2 favicon + routing display — UI consistency

### Original Bug (what started this session)
"Find courses about artificial intelligence" returned catalog results but NO student reviews.
- Root cause: inner agent only called search_course_catalog, skipped get_course_reviews
- Fix: strengthened system prompt with CRITICAL WORKFLOW instructions
- This fix is in the code and will work once the runtime is restored

## What Phase 1 and Phase 2 Look Like (CONFIRMED WORKING)
- Phase 1: 🎓 favicon ✓, routing display ✓, course reviews ✓
- Phase 2: 🎓 favicon ✓, routing display ✓, course reviews ✓
- Phase 3: BROKEN (runtime environment issue from 0.15.0 upgrade)
