# Phase 3: AgentCore Microservices — Prerequisites & Tooling

## Required Tools

| Tool | Version | Install Command |
|------|---------|----------------|
| Python | 3.12+ | OS-specific |
| Node.js | 20+ | `nvm install 20 && nvm use 20` |
| AWS CLI | v2 | [Install guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) |
| AgentCore CLI | latest | `npm install -g @aws/agentcore` |
| AWS CDK | latest | `npm install -g aws-cdk` |

## Verify Installation

```bash
python3 --version        # 3.12+
node --version           # 20+
aws --version            # aws-cli/2.x
agentcore --version      # prints version
cdk --version            # prints version
```

## AgentCore Project Scaffolding (Inside an Existing Git Repo)

**⚠️ IMPORTANT: The AgentCore CLI (`agentcore create`) defaults to initializing a new Git repository. If you're working inside an existing repo, you MUST use `--skip-git` to avoid creating a nested `.git` directory.**

The AgentCore CLI generates critical infrastructure files (CDK project, `.llm-context/` type definitions, `.cli/` state tracking) that are required for `agentcore deploy` to work. You cannot just create `agentcore.json` by hand — the CLI scaffolding is mandatory.

### The Workflow

```bash
# 1. Scaffold the project — skip git, python venv, and npm install
#    (we manage our own git repo and will install deps separately)
agentcore create --name <projectname> --no-agent \
  --skip-git --skip-python-setup --skip-install \
  --output-dir <target-parent-directory>

# 2. Install CDK dependencies (required for agentcore deploy)
cd <target-parent-directory>/<projectname>/agentcore/cdk
npm install

# 3. Add your agent code as sibling directories of agentcore/
#    e.g., my_agent/agent.py, another_agent/agent.py

# 4. Edit agentcore/agentcore.json to declare your runtimes
#    (codeLocation paths are relative to the project root)

# 5. Edit agentcore/aws-targets.json with your account and region

# 6. Validate
cd <target-parent-directory>/<projectname>
agentcore validate

# 7. Deploy
agentcore deploy -y
```

### What the Scaffold Creates

```
<projectname>/
├── agentcore/                    # Config + infrastructure (DO NOT put agent code here)
│   ├── .cli/                     # CLI state tracking (deployed-state.json)
│   ├── .llm-context/             # TypeScript type defs for AI assistants
│   ├── cdk/                      # CDK infrastructure project (TypeScript)
│   │   ├── bin/cdk.ts
│   │   ├── lib/cdk-stack.ts
│   │   ├── package.json          # CDK dependencies
│   │   └── ...
│   ├── .env.local                # API keys (gitignored)
│   ├── .gitignore
│   ├── agentcore.json            # Project config (runtimes, memory, credentials, gateways, policies)
│   └── aws-targets.json          # Deployment targets (account, region)
├── AGENTS.md                     # Agent documentation (auto-generated)
└── README.md                     # Project readme (auto-generated)
```

### Key Rules

- **Agent code goes at the project root level** (siblings of `agentcore/`), NOT inside `agentcore/`
- **`codeLocation` in agentcore.json** resolves relative to the project root (e.g., `"./my_agent/"`)
- **`agentcore deploy` must be run from the project root** (the directory containing `agentcore/`)
- **The `agentcore/cdk/` directory is mandatory** — without it, deploy fails with "CDK project not found"
- **`node_modules/` inside `agentcore/cdk/`** should be in `.gitignore` — regenerate with `npm install`

### Naming Constraints

- **Project name**: Must start with a letter, alphanumeric only, max 23 chars (no hyphens, no underscores)
- **Runtime names**: Start with letter, alphanumeric + underscores, max 48 chars
- **Policy engine names**: Start with letter, alphanumeric + underscores, max 48 chars
- **Credential names**: Alphanumeric + hyphens + underscores

### If You Already Have Agent Code

If you're adding AgentCore to an existing project (like we did):

1. Scaffold to a temp directory: `agentcore create --name X --no-agent --skip-git --skip-python-setup --skip-install --output-dir /tmp`
2. Copy the generated `<projectname>/` directory into your repo at the desired location
3. Copy your existing agent code into the project root as sibling directories
4. Edit `agentcore.json` to point `codeLocation` at your agent directories
5. Run `npm install` in `agentcore/cdk/`
6. Validate and deploy

| Command | Description |
|---------|-------------|
| `agentcore create --name <project> --no-agent` | Scaffold project (no default runtime) |
| `agentcore add runtime --name X --type byo --code-location ./dir --entrypoint agent.py --protocol HTTP` | Add BYO agent runtime |
| `agentcore add runtime --name X --framework Strands --model-provider Bedrock` | Add Strands template agent |
| `agentcore add gateway --name X` | Add a gateway |
| `agentcore add gateway-target --name X --type mcp-server --endpoint <url> --gateway <gw>` | Add gateway target |
| `agentcore add memory --name X --strategies SEMANTIC,SUMMARIZATION --expiry 30` | Add memory |
| `agentcore dev` | Start local dev server |
| `agentcore dev --invoke list-tools` | Test MCP tools locally |
| `agentcore deploy -y` | Deploy all resources to AWS |
| `agentcore invoke "prompt"` | Invoke deployed agent |
| `agentcore status` | Check deployment status |
| `agentcore logs --agent <name> --since 5m` | View CloudWatch logs |
| `agentcore remove runtime --name X` | Remove a resource |

## Project Structure (AgentCore CLI)

```
workshop4/phase3/
├── cloudformation/                     # Identity stack (Cognito pools)
│   ├── stack-outputs.json
│   └── student-services-identity.yaml
├── deploy-streamlit-app/               # Thin client ECS deployment
├── streamlit_app/                      # Local dev thin client
├── studentservices/                    # AgentCore project
│   ├── agentcore/                      # Config ONLY
│   │   ├── agentcore.json
│   │   ├── aws-targets.json
│   │   ├── .env.local                  # API keys (gitignored)
│   │   └── cdk/                        # CDK infrastructure (auto-generated)
│   ├── course_registration/            # Specialist agent runtime
│   ├── course_review/                  # Specialist agent runtime
│   ├── loan_application/               # Specialist agent runtime
│   ├── math_teaching/                  # Specialist agent runtime
│   ├── policies/                       # Cedar policy files
│   └── student_services/               # Orchestrator agent runtime
├── .gitignore
├── PREREQUISITES.md
└── README.md
```

## Agent Code Pattern (BedrockAgentCoreApp)

Every agent runtime follows this structure:

1. Module docstring
2. Imports
3. Configuration from environment variables (with hardcoded defaults)
4. System prompt as module-level constant
5. OAuth2 token management with caching (refresh 5 min before expiry)
6. MCP client factory using `streamablehttp_client` with auto-refreshing auth
7. `BedrockAgentCoreApp` entrypoint
8. `if __name__ == "__main__": app.run()`

### Key Rules

- **NEVER** manually call `mcp_client.start()` or use `with mcp_client:` — the Agent manages MCPClient lifecycle
- **Hardcode** gateway config defaults — `BedrockAgentCoreApp` strips all payload keys except `prompt`
- **Use** `os.environ.get()` for overrides, but working defaults must be hardcoded
- **Cache** agents keyed by `{session_id}/{user_id}` for session reuse

## Memory Integration

- Each memory gets env var: `MEMORY_<NAME>_ID` (uppercase, underscores)
- Example: memory named `StudentServicesMemory` → `MEMORY_STUDENTSERVICESMEMORY_ID`
- Use `AgentCoreMemorySessionManager` from `bedrock_agentcore`
- Return `None` when env var is not set (graceful degradation)

## Cedar Policy Notes

- **Default deny** — everything blocked unless explicitly permitted
- **Forbid wins** — if any `forbid` matches, access denied even if `permit` also matches
- **Action format**: `<gateway_target_name>___<tool_name>` (three underscores)
- **Cedar only supports Long (integers)** for numeric comparisons, not floats
- **Modes**: `ENFORCE` (blocks) vs `LOG_ONLY` (logs only, useful for testing)

## AWS Region

All Phase 3 resources deploy to **us-west-2** (matching Phase 1 infrastructure).

## Existing Infrastructure (from Phase 1)

- DynamoDB: `course_registration`, `course_review`
- Bedrock Knowledge Base: `NCGF0S9LJR`
- SageMaker endpoint: `xgboost-serverless-ep2026-05-10-06-08-28`
- SSM parameters: `/student-services/*`
- Identity stack: `student-services-identity` (5 Cognito pools, deployed)
