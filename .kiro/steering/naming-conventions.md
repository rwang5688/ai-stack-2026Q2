---
inclusion: always
---

# Naming Conventions

## CRITICAL: Consistency Rules

- **Imports**: ALWAYS in alphabetical order
- **Dependencies** (requirements.txt, pyproject.toml): ALWAYS in alphabetical order
- **Never use abstract/generic names** like "orchestrator", "gateway-oauth", "policy-engine" — use the actual service/product name
- **Pool naming**: Match the runtime/service name exactly (e.g., `student-services-pool` for the Student Services Agent)
- **No word "Agent" in infrastructure names** — pools, domains, resource servers are infrastructure, not agents

## Naming Patterns

| Resource Type | Pattern | Example |
|--------------|---------|---------|
| Cognito Pool | `{service-name}-pool` | `student-services-gateway-pool`, `course-registration-pool` |
| Cognito Domain | `{service-name}-{AccountId}` | `student-services-gateway-149057604171` |
| Resource Server ID | `{service-name}` | `student-services`, `course-registration` |
| OAuth Scope | `{resource-server-id}/access` | `student-services/access` |
| AgentCore Runtime (HTTP) | `StudentServicesAgent` | PascalCase, ends with "Agent" |
| AgentCore Runtime (MCP) | `CourseRegistrationMcp` | PascalCase, ends with "Mcp" for MCP servers |
| OAuth Credential | `{RuntimeName}-oauth` | `CourseRegistrationMcp-oauth` |
| Gateway | `studentservicesgateway` | Alphanumeric only (AgentCore constraint) |

## Code Style

- Python imports: alphabetical, stdlib first, then third-party, then local
- All lists/arrays in config files: alphabetical where order doesn't matter
- Environment variables: UPPER_SNAKE_CASE
- File names: snake_case
