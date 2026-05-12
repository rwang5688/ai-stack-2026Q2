---
inclusion: fileMatch
fileMatchPattern: "workshop4/phase3/**"
---

# AgentCore Conventions (Phase 3)

## Project Overview
Phase 3 decomposes the monolithic Student Services app into AgentCore microservices:
- 5 AgentCore Runtimes (1 orchestrator + 4 specialists)
- 1 AgentCore Gateway aggregating specialist tools
- 1 AgentCore Memory (SEMANTIC, SUMMARIZATION, USER_PREFERENCE)
- Cedar policies for content safety
- Thin Streamlit client on ECS Fargate

## Tech Stack
- Python 3.13 (AgentCore runtime version)
- Strands Agents SDK for agent logic
- bedrock-agentcore for runtime entrypoint and memory
- FastMCP / mcp for MCP protocol
- httpx for OAuth2 token management
- AWS CDK (Python) for thin client infrastructure
- AgentCore CLI (`@aws/agentcore`) for deployment

## AgentCore CLI Usage
- Install: `npm install -g @aws/agentcore aws-cdk`
- Deploy: `agentcore deploy -y`
- Local dev: `agentcore dev`
- Status: `agentcore status`
- Invoke: `agentcore invoke "prompt"`
- Logs: `agentcore logs --agent <name> --since 5m`

## Agent Code Pattern (BedrockAgentCoreApp)

### Structure (in order)
1. Module docstring with description and usage
2. Imports
3. Configuration from environment variables (with hardcoded working defaults)
4. System prompt as module-level constant
5. OAuth2 token management with caching (refresh 300s before expiry)
6. MCP client factory using `streamablehttp_client` with auto-refreshing auth
7. `BedrockAgentCoreApp` entrypoint
8. `if __name__ == "__main__": app.run()`

### Critical Rules
- **NEVER** use `with mcp_client:` or call `mcp_client.start()` — Agent manages MCPClient lifecycle
- **HARDCODE** gateway config defaults — BedrockAgentCoreApp strips all payload keys except `prompt`
- **USE** `os.environ.get()` for overrides, but hardcoded value must be the working default
- **CACHE** agents keyed by `{session_id}/{user_id}` for session reuse
- **RETURN** `{"response": str(response)}` from entrypoint

### OAuth2 Token Pattern
```python
_token_cache: dict = {"token": None, "expires_at": 0.0}

def get_oauth_token() -> str:
    now = datetime.now().timestamp()
    if _token_cache["token"] and now < _token_cache["expires_at"]:
        return _token_cache["token"]
    resp = httpx.post(TOKEN_ENDPOINT, data={...}, auth=(CLIENT_ID, CLIENT_SECRET))
    data = resp.json()
    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = now + data["expires_in"] - 300
    return _token_cache["token"]
```

### MCPClient Factory Pattern
```python
def get_mcp_client() -> MCPClient:
    class _OAuthAuth(httpx.Auth):
        def auth_flow(self, request):
            request.headers["Authorization"] = f"Bearer {get_oauth_token()}"
            yield request
    return MCPClient(lambda: streamablehttp_client(url=GATEWAY_MCP_URL, auth=_OAuthAuth()))
```

## Memory Integration
- Env var: `MEMORY_<NAME>_ID` (uppercase, underscores)
- Use `AgentCoreMemorySessionManager` from `bedrock_agentcore`
- Return None when env var not set (graceful degradation)
- Extract `session_id` and `user_id` from entrypoint `context` parameter

## Cedar Policy Rules
- **Default deny** — everything blocked unless explicitly permitted
- **Forbid wins** — forbid overrides permit
- **Action format**: `<gateway_target_name>___<tool_name>` (three underscores)
- **Cedar only supports Long (integers)** for numeric comparisons
- **Modes**: `ENFORCE` (blocks) vs `LOG_ONLY` (logs only)
- Can switch from ENFORCE to LOG_ONLY in console without redeployment

## Region
All Phase 3 resources: **us-west-2**

## Model Configuration
- Use `BedrockModel` with cross-region inference prefix (`us.`)
- Default: `us.amazon.nova-2-lite-v1:0` (matching Phase 1 config)
- Set `region_name="us-west-2"`
