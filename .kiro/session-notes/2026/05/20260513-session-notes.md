# Session Notes - May 13, 2026

## Session Overview
Phase 3 AgentCore microservices: completed full deployment from scratch. Resolved multiple issues with naming, protocol types, CDK scaffolding, and credential registration. All 5 runtimes + gateway + memory + credentials deployed and READY.

## Key Accomplishments

### Architecture Decisions Finalized
- Specialists are **Agent-inside-MCP** pattern (Strands Agent wrapped in FastMCP `@mcp.tool()`)
- Orchestrator is HTTP runtime (BedrockAgentCoreApp) — invoked via SigV4 from thin client
- Gateway aggregates 4 MCP specialist servers
- File names preserved as `agent.py` across Phase 1 and Phase 3 for easy `diff` comparison

### Naming Cleanup (Complete Redo)
- Orchestrator: `StudentServicesOrchestrator` → `StudentServicesAgent`
- Specialists: `*Agent` → `*Mcp` (CourseRegistrationMcp, CourseReviewMcp, LoanApplicationMcp, MathTeachingMcp)
- Gateway pool: `orchestrator-pool` → `student-services-gateway-pool`
- All pool names now match their directory/service names consistently

### Deployment Completed
- **CloudFormation stack** `student-services-identity` deployed (5 Cognito pools with proper naming)
- **AgentCore Deploy 1**: 5 runtimes (1 HTTP + 4 MCP) + memory + credentials
- **AgentCore Deploy 2**: Gateway with 4 MCP server targets
- All resources READY in us-west-2

### Documentation Created
- `workshop4/README.md` — architecture evolution + Phase 1→3 code mapping section
- `workshop4/phase3/README.md` — identity/auth explanation, full deployment runbook
- `workshop4/phase3/deploy-student-services-identity.sh` — CloudFormation deploy script
- `workshop4/phase3/register-credentials.sh` — OAuth credential registration script
- `workshop4/phase3/PREREQUISITES.md` — AgentCore scaffolding workflow documented
- `.kiro/steering/naming-conventions.md` — naming rules locked in
- `.kiro/steering/git-workflow.md` — deployment locations documented

## Issues & Resolutions

### Protocol Change Requires Runtime Deletion
- **Issue**: Deployed runtimes as HTTP, then tried to change to MCP. CDK can't update protocol in-place.
- **Resolution**: Manually deleted runtimes from AgentCore console, redeployed fresh as MCP.
- **Lesson**: Get the protocol right before first deploy. No in-place protocol changes.

### CDK Scaffolding Required for agentcore deploy
- **Issue**: `agentcore deploy` fails without `agentcore/cdk/` directory.
- **Resolution**: Use `agentcore create --skip-git --skip-python-setup --skip-install` to scaffold, then copy agent code in.
- **Lesson**: The CDK scaffold is mandatory infrastructure, not optional.

### Gateway Targets Need Real Endpoint URLs
- **Issue**: Can't deploy gateway without runtime URLs (chicken-and-egg).
- **Resolution**: Two-phase deploy — runtimes first, then gateway with real URLs.
- **Lesson**: Initial bootstrap always requires 2 deploys. Subsequent deploys are single-step.

### Cedar Policy Wildcard Resource Rejected
- **Issue**: `permit(principal, action, resource)` rejected — wildcard resource not allowed.
- **Resolution**: Changed to `permit(principal, action, resource is AgentCore::Gateway)`.
- **Lesson**: Cedar policies must scope to resource type or specific ARN.

### Credential Registration Not Persisted
- **Issue**: OAuth credentials showed "Local only" until gateway was deployed.
- **Resolution**: Credentials get provisioned to AWS when the gateway (which references them) is deployed.
- **Lesson**: Register credentials before Deploy 1 so they deploy with runtimes.

## Deployed Resources

| Resource | ARN/ID |
|----------|--------|
| StudentServicesAgent | studentservices_StudentServicesAgent-5PKaxz42VQ |
| CourseRegistrationMcp | studentservices_CourseRegistrationMcp-fc9OM8EnnA |
| CourseReviewMcp | studentservices_CourseReviewMcp-T1VwbM8olV |
| LoanApplicationMcp | studentservices_LoanApplicationMcp-km8B2G2zMx |
| MathTeachingMcp | studentservices_MathTeachingMcp-SBJLNa4zEW |
| StudentServicesMemory | studentservices_StudentServicesMemory-Uu3gM85RCx |
| Gateway | studentservices-studentservicesgateway-qizxrsubb4 |

## Cognito Pools (from student-services-identity stack)

| Pool Name | Pool ID | Client ID |
|-----------|---------|-----------|
| student-services-gateway-pool | us-west-2_xWeSNSeqc | 5520octlvdtcru9er9k9dsc9qk |
| course-registration-pool | us-west-2_GWmTz77Yw | 2d0n9b5vcpcie7eksovv83avu4 |
| course-review-pool | us-west-2_BOVHqDyyy | 6gqqkbt0r4487nik1tdut0l58s |
| loan-application-pool | us-west-2_zWhuXg4K8 | 1u49v5kajhdlk0percigfv6oml |
| math-teaching-pool | us-west-2_0v9KV3jDm | d2oedj4keb2o1on9rpr1vq3g7 |

## Decisions Made
- **Agent-inside-MCP** for specialists — preserves Phase 1 LLM reasoning behavior
- **student-services-gateway-pool** naming — makes it clear this pool protects the gateway
- **No "Agent" in infrastructure names** — pools, domains, resource servers are infrastructure
- **Alphabetical ordering** enforced for imports, dependencies, config arrays
- **`agentcore deploy` runs from Windows PC only** — CDK deploy (Streamlit) from code-server
- **Git commit/push from code-server only** — no push capability from Windows PC

## Next Steps
- [x] Test StudentServicesAgent in AgentCore Runtime Playground
- [x] Update orchestrator agent.py with real gateway URL + client secret
- [ ] Fix IAM permissions for CourseRegistrationMcp (dynamodb:PutItem) and LoanApplicationMcp (sagemaker:InvokeEndpoint)
- [ ] Build thin Streamlit client (streamlit_app/)
- [ ] Deploy thin client to ECS Fargate (deploy-streamlit-app/)
- [ ] Add Cedar policies (after end-to-end works)
- [ ] Commit and push from code-server

## IAM Permissions Fix Plan (Tonight)

**Problem:** Two AgentCore runtimes lack IAM permissions:
- `CourseRegistrationMcp` — needs `dynamodb:PutItem` on `arn:aws:dynamodb:us-west-2:149057604171:table/course_registration`
- `LoanApplicationMcp` — needs `sagemaker:InvokeEndpoint` on the XGBoost endpoint

**Plan:**
1. Find IAM execution roles (IAM → Roles → search `studentservices_CourseRegistration` and `studentservices_LoanApplication`)
2. Attach inline policies granting the specific permissions
3. Test registration and loan prompts again
4. Research whether `agentcore.json` supports declarative IAM policy attachment (so permissions survive redeployment)
5. If not, create a post-deploy script or separate CloudFormation stack for IAM policies
