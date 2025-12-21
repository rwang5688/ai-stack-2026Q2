# Code Server CloudFormation Templates

## Template Files

### `code-server.yaml` (Original Baseline)
- **Purpose**: Original workshop template - keep as reference baseline
- **Size**: 34,383 bytes
- **Usage**: Use for comparing against future updates from upstream
- **Status**: Unmodified original

### `code-server-improved.yaml` (Production Ready)
- **Purpose**: Deployment-ready template with minimal fixes
- **Size**: 34,333 bytes (99.85% identical to original)
- **Usage**: Use for actual deployments
- **Status**: Fixed critical deployment issues while preserving original structure

## Update Workflow

When new versions of `code-server.yaml` are released:

1. **Replace baseline**: Update `code-server.yaml` with new upstream version
2. **Compare changes**: Use diff tools to see what changed
3. **Apply minimal fixes**: Update `code-server-improved.yaml` with same fixes:
   - Quote all SSM Document shell commands (prevents YAML null values error)
   - Use instance ID targeting for SSM association (more reliable than tag-based)
4. **Test deployment**: Verify improved template deploys successfully

## Actual Fixes Applied

### 1. YAML Parsing Issues (Main Fix)
The original template had unquoted multi-line shell commands that caused CloudFormation to fail with "null values are not allowed in templates".

```yaml
# Original (causes null values error)
runCommand:
  - apt-get update && DEBIAN_FRONTEND=noninteractive apt-get
    install -y curl

# Fixed (properly quoted)
runCommand:
  - 'apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y curl'
```

### 2. SSM Association Reliability
Changed from tag-based targeting to instance ID targeting for more reliable bootstrap execution.

```yaml
# Original (less reliable)
Targets:
  - Key: tag:SSMBootstrap
    Values: [true]

# Fixed (more reliable)  
Targets:
  - Key: InstanceIds
    Values: [!Ref VSCodeInstanceEC2Instance]
```

## Design Philosophy

- **Minimal changes**: Preserve original structure and installation methods for easy maintenance
- **Deployment reliability**: Fix only critical issues that prevent deployment
- **Future compatibility**: Easy to merge upstream updates

## Related Documentation

- **Specification**: `.kiro/specs/code-server-deployment/`
- **Session Notes**: `.kiro/session-notes/20251217-session-notes.md`
- **Project README**: `../README.md`