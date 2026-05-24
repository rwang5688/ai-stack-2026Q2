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

## FINAL ROOT CAUSE ANALYSIS (Confirmed May 23, 2026)

### Two Separate Problems (Don't Confuse Them)

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | **307 Redirect Loop** — Gateway sends `POST /mcp/`, MCP server redirects to `/mcp`, Gateway doesn't follow redirect, retries forever | FastMCP 3.3.1 registers endpoint at `/mcp` but Gateway sends to `/mcp/`. Starlette's `redirect_slashes=True` causes 307. | Add `path="/mcp/"` to `FastMCP()` constructor so server listens on `/mcp/` directly. **Proven fix** — logs showed 200 OK after applying. |
| 2 | **Tool Result Timeout** — Even after 307 is fixed, orchestrator says "issue with tool" and falls back to answering directly | Inner Strands Agent inside MCP server makes its own Bedrock LLM call (30+ seconds). Gateway/orchestrator times out waiting for the response. | Remove inner agent from MCP server. Make MCP tools dumb (direct AWS SDK call, returns in <1 second). **Architectural fix** — eliminates the timeout entirely. |

**Key insight:** Problem 1 (307) is a URL routing bug. Problem 2 (timeout) is an architectural anti-pattern. They are independent issues that happened to surface together.

### Key Findings
1. **Wrapping Strands Agent inside MCP server is an anti-pattern.** The "Agent-inside-MCP" pattern (inner Strands Agent with its own Bedrock LLM loop inside an MCP tool) creates double-inference latency, state fragmentation, and fragility to library version changes.

2. **It worked before by luck.** On the previous AgentCore runtime (pre-FastMCP 3.3.1), 3 out of 4 MCP servers with inner agents happened to work. The 4th (course review) worked partially — it hit the catalog but never the reviews (prompt issue). The architecture was always fragile.

3. **Any future `agentcore deploy -y` would have broken it anyway.** AgentCore manages the runtime base image server-side. FastMCP 3.3.1 is now baked in regardless of CLI version (confirmed: CLI 0.13.1 still deploys FastMCP 3.3.1 runtime). The 307 redirect issue (`POST /mcp/` → 307 → `POST /mcp`) is permanent in the current runtime. Even with `path="/mcp/"` workaround, the inner agent's Bedrock call takes 30+ seconds which exceeds the gateway's tool-call timeout.

4. **CLI version is irrelevant.** Downgrading from 0.15.0 to 0.13.1 did NOT change the runtime environment. The runtime Python packages (FastMCP, etc.) are managed server-side by AgentCore infrastructure, not by the CLI.

5. **The correct architecture** (confirmed by AWS docs, Gemini, and travelplanner reference): Keep ALL agent intelligence in ONE AgentCore Runtime (Agent-as-Tool pattern locally). MCP servers behind the Gateway should be DUMB deterministic tools only (DynamoDB read/write, KB retrieve, SageMaker invoke). No LLM calls inside MCP servers.

### Decision
- **Upgrade CLI back to 0.15.0** (CLI version doesn't matter for runtime)
- **Proceed with architectural refactor** — move all agent intelligence into orchestrator runtime, make MCP servers dumb tools
- **Do NOT attempt to fix the Agent-inside-MCP pattern** — it's an anti-pattern regardless of whether it can be made to work

## ARCHITECTURAL REFACTOR PLAN (Phase 3 Redesign)

### The Lesson Learned
Wrapping specialist Strands Agents inside MCP servers (Agent-inside-MCP pattern) is an anti-pattern:
- **Double-inference latency**: Orchestrator calls MCP → MCP spins up inner agent → inner agent calls Bedrock → result travels back through MCP → orchestrator processes. Too many network roundtrips.
- **Container anti-pattern**: AgentCore Runtime is single-process. Forcing an agentic reasoning loop inside an MCP server conflates the Reasoning Layer with the Capability Layer.
- **State fragmentation**: Conversational state, session tokens, and memory can't flow across MCP protocol boundaries cleanly.
- **Fragile to library version changes**: FastMCP version incompatibilities break the entire chain (as we experienced).

### The Correct Pattern (Gemini + AWS docs confirmed)
- **Reasoning Layer** (AgentCore Runtime): ALL agent intelligence lives in ONE runtime. Orchestrator + specialist agents run locally using Strands Agent-as-Tool pattern.
- **Capability Layer** (AgentCore Gateway → MCP Servers): ONLY dumb deterministic data access functions. No LLM calls. No reasoning.

### New Phase 3 Architecture

```
Thin Client → StudentServicesAgent (HTTP Runtime)
                    │
                    ├── course_review_agent (local Agent-as-Tool)
                    │       ├── system prompt: course review specialist
                    │       └── tools: search_course_catalog, get_course_reviews
                    │                   (routed via Gateway → MCP servers)
                    │
                    ├── course_registration_agent (local Agent-as-Tool)
                    │       ├── system prompt: registration specialist
                    │       └── tool: register_course (via Gateway → MCP server)
                    │
                    ├── loan_application_agent (local Agent-as-Tool)
                    │       ├── system prompt: loan prediction specialist
                    │       └── tool: predict_loan (via Gateway → MCP server)
                    │
                    └── math_teaching_agent (local Agent-as-Tool)
                            ├── system prompt: math tutor
                            └── tool: calculator (LOCAL, no MCP needed)
```

### MCP Servers (Dumb Tools Only)

| MCP Server | Tool Name | What It Does | Backend |
|-----------|-----------|--------------|---------|
| CourseCatalogMcp | search_course_catalog | Vector search for courses | Bedrock Knowledge Base |
| CourseReviewsMcp | get_course_reviews | Lookup student reviews | DynamoDB read |
| CourseRegistrationMcp | register_course | Write registration record | DynamoDB write |
| LoanApplicationMcp | predict_loan | Invoke XGBoost model | SageMaker Serverless Endpoint |

### Key Design Decisions
1. **Math agent stays fully local** — calculator is a pure function, no external service needed, no MCP server
2. **Course review agent gets TWO MCP tools** — catalog (KB) and reviews (DynamoDB) are separate MCP servers because they're separate backends
3. **Agent-as-Tool pattern** — each specialist keeps its own system prompt and reasoning, invoked locally by the orchestrator (same as Phase 2)
4. **Gateway still provides value** — OAuth, Cedar policies, semantic routing, observability — even for dumb tools
5. **Single Bedrock model call chain** — Orchestrator calls Bedrock → routes to specialist → specialist calls Bedrock → specialist calls MCP tool → data returns → specialist reasons → orchestrator returns. Only TWO Bedrock calls max (orchestrator + specialist), not three (orchestrator + MCP-wrapped-agent + inner-agent)

### Workshop Progression Story
- **Phase 1**: Monolithic — all agents + tools in one process, one Streamlit app
- **Phase 2**: Multi-agent — Agent-as-Tool pattern, Cognito auth, ECS Fargate deployment
- **Phase 3**: Microservices — Same Agent-as-Tool intelligence, but data access decoupled behind AgentCore Gateway + MCP servers. Demonstrates: independent scaling, Cedar policies, OAuth per-service, observability per-tool

### What Changes from Current Phase 3
- **DELETE**: Inner Strands Agents from all 4 MCP servers (they become simple functions)
- **MOVE**: Specialist agent logic (system prompts, reasoning) INTO the orchestrator runtime
- **KEEP**: Gateway, Cognito pools, Cedar policies, credentials, memory
- **KEEP**: MCP server runtimes (but simplified to just tool functions)
- **ADD**: MCP client in orchestrator that passes tools to specialist agents (not to orchestrator directly)

### Timeline
- Spec creation → today
- Implementation → today/tomorrow
- Testing → before Tuesday demo



## CONTINUED: May 24, 2026 (Late Night Session)

### Key Decision

**DECISION: After major architectural refactoring, ALWAYS start clean.**

Delete the old AgentCore CDK stack and deploy fresh. Don't try to incrementally update an existing stack with fundamentally different runtimes.

**Rule going forward:** If the runtime count changes, runtime names change, or protocol types change — nuke and pave. The agentcore.json + code is the source of truth; the stack is disposable.

### Mistakes Made (Root Cause Analysis) — Two Nights Lost (~8 hours)

#### Mistake 1: Did not compare against reference implementation BEFORE writing code
- **Impact**: ~3 hours wasted
- **What happened**: Wrote agentcore.json from memory/docs instead of copying the working travelplanner reference pattern field-by-field.
- **What was missed**: `"instrumentation": {"enableOtel": false}` on every MCP runtime. Without this, AgentCore expects OpenTelemetry dependencies bundled in the CodeZip — which we don't have because our MCP servers are minimal.
- **Rule**: ALWAYS diff your config against the reference implementation before deploying. Field by field. No exceptions.

#### Mistake 2: Tried to incrementally update a fundamentally changed stack
- **Impact**: ~2 hours wasted
- **What happened**: The old stack had MathTeachingMcp + CourseReviewMcp runtimes. The new topology removes those and adds CourseCatalogMcp + CourseReviewsMcp. Tried to `agentcore deploy -y` on top of the existing stack instead of deleting it first.
- **What went wrong**: CDK drift, orphaned resources, credential providers pointing to deleted Cognito pools, DELETE_FAILED loops.
- **Rule**: Major topology changes = delete stack first. Always.

#### Mistake 3: Did not validate agentcore.json against reference before FIRST deploy attempt
- **Impact**: ~1 hour wasted (deploy, wait, fail, diagnose, fix, delete stack, redeploy)
- **What happened**: The OTEL error only surfaces AFTER the runtime is created and the zip is uploaded. By then the stack is in ROLLBACK_COMPLETE and must be manually deleted before retrying.
- **Rule**: Before ANY `agentcore deploy`, run a mental (or actual) checklist:
  1. Does every MCP runtime have `"instrumentation": {"enableOtel": false}`?
  2. Are gateway targets empty for first deploy?
  3. Are all credentials registered?
  4. Is deployed-state.json deleted (if starting fresh)?

#### Mistake 4: Put architectural decisions in tasks.md instead of session notes
- **Rule**: Tasks.md is a disposable checklist. Decisions go in session notes. Patterns go in steering files.

#### Mistake 5: Excessive back-and-forth instead of acting
- **Rule**: When the user says "go" — go. Don't ask, don't explain, don't repeat. Act.

### AgentCore Deploy Checklist (NEVER skip this)

Before running `agentcore deploy -y`:
- [ ] Every MCP runtime has `"instrumentation": {"enableOtel": false}`
- [ ] Gateway targets are `[]` on first deploy (add real URLs on second deploy)
- [ ] All credentials registered (`bash register-credentials.sh`)
- [ ] `deployed-state.json` deleted if starting fresh
- [ ] No stale ROLLBACK_COMPLETE stack exists
- [ ] `agentcore.json` matches reference implementation structure field-by-field

### Clean Deployment Procedure

1. Refresh AWS credentials
2. `aws cloudformation delete-stack --stack-name AgentCore-studentservices-default --region us-west-2`
3. `aws cloudformation wait stack-delete-complete --stack-name AgentCore-studentservices-default --region us-west-2`
4. `Remove-Item "workshop4\phase3\studentservices\agentcore\.cli\deployed-state.json" -Force`
5. Empty gateway targets in agentcore.json (`"targets": []`)
6. `bash register-credentials.sh` (stack deletion kills credential providers)
7. `agentcore deploy -y` (first pass — creates runtimes, empty gateway)
8. `agentcore status` → grab runtime URLs
9. Add targets with real URLs to agentcore.json
10. `agentcore deploy -y` (second pass — gateway gets targets)
11. Update orchestrator hardcoded gateway URL if changed


#### Mistake 6: Left `path="/mcp/"` in FastMCP constructor from old architecture
- **Impact**: 2 failed gateway target deployments (~40 min each)
- **What happened**: The old Agent-inside-MCP architecture needed `path="/mcp/"` to fix a 307 redirect with FastMCP 3.3.1. The new dumb MCP servers don't need it. The gateway health check connects on the DEFAULT path — with `path="/mcp/"` set, the server listens on `/mcp/` but the health check hits `/`, gets no response, times out after 30s, and fails.
- **What the error said**: "Runtime initialization time exceeded. Please make sure that initialization completes in 30s." — MISLEADING. It's not a cold start issue. It's a path mismatch.
- **Rule**: Match the reference implementation EXACTLY. No `path="/mcp/"` in FastMCP constructor. The reference uses `FastMCP("flights-mcp-server")` with no path argument.
- **Broader rule**: When an error message says X, verify X is actually the cause before acting on it. "Initialization time exceeded" made me think cold start, but it was actually a path routing issue.


#### Mistake 6: Left `path="/mcp/"` in FastMCP constructor from old architecture
- **Impact**: 2 failed gateway deployments (~30 min each wasted)
- **What happened**: The old Agent-inside-MCP architecture needed `path="/mcp/"` to fix a 307 redirect with FastMCP 3.3.1. The new dumb MCP servers don't need it. The gateway health check connects on the DEFAULT path — if the server only listens on `/mcp/`, the health check times out.
- **What the error said**: "Runtime initialization time exceeded. Please make sure that initialization completes in 30s." — misleading error message that sounds like cold start but is actually a path mismatch.
- **Rule**: Match the reference implementation EXACTLY. The reference uses `FastMCP("name")` with NO path argument. Do the same.

#### Mistake 7: Gave multiple conflicting explanations for the same error
- **Impact**: User confusion, lost trust
- **What happened**: First said "cold start timeout", then said "path mismatch", then flip-flopped. Should have checked the reference implementation FIRST before speculating.
- **Rule**: Don't speculate. Check the reference. Give ONE explanation backed by evidence.


#### Mistake 6: Left `path="/mcp/"` in FastMCP constructor from old architecture
- **Impact**: 2 failed gateway deploys (~30 min each wasted)
- **What happened**: The old Agent-inside-MCP architecture needed `path="/mcp/"` to fix a 307 redirect with FastMCP 3.3.1. The new dumb MCP servers don't need it. The gateway health check connects on the DEFAULT path — with `path="/mcp/"` set, the server listens on `/mcp/` but the gateway hits `/`, gets no response, times out after 30s, and fails.
- **Rule**: Match the reference implementation EXACTLY. The reference has `FastMCP("flights-mcp-server")` with NO path argument. Do the same.

#### Mistake 7: Speculated about causes instead of checking the reference
- **Impact**: Confused the user with multiple contradictory explanations
- **What happened**: First said "cold start timeout", then said "path issue", then reverted, then re-applied. Should have checked the reference FIRST and given ONE answer.
- **Rule**: When something fails, check the reference implementation FIRST. Give ONE explanation. Don't speculate.
