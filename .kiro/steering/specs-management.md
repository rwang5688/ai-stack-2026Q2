# Specs Management

## Purpose
Organize feature development using structured specifications that follow spec-driven development methodology.

## Rules

### Directory Structure
- Specs are organized by major module under `.kiro/specs/`
- Top-level directories: `code-server/`, `workshop2/`, `workshop3/`, `workshop4/`
- Feature specs go under their module: `.kiro/specs/{module}/{feature-name}/`
- Archive completed/obsolete specs under: `.kiro/specs/archive/{module}/{feature-name}/`
- Feature names use kebab-case (e.g., `workshop4-phase1-monolithic-agents`)

#### Structure
```
.kiro/specs/
├── archive/
│   ├── code-server/
│   ├── workshop2/
│   ├── workshop3/
│   └── workshop4/
├── code-server/
│   └── code-server-deployment/
├── workshop2/
│   └── workshop2-transform-datasets/
├── workshop3/
│   └── workshop3-deploy-inference-endpoint/
└── workshop4/
    └── workshop4-phase1-monolithic-agents/
```

### Required Files per Spec
Each feature spec directory must contain:
1. **requirements.md** - User stories and acceptance criteria using EARS format
2. **design.md** - Technical design and architecture decisions
3. **tasks.md** - Implementation task breakdown and checklist

### Feature Naming Guidelines
- Use descriptive, kebab-case names
- Focus on the business capability, not implementation details
- Examples:
  - ✅ `user-authentication`
  - ✅ `code-server-deployment` 
  - ✅ `session-management`
  - ❌ `login-api`
  - ❌ `nginx-config`

### Spec Workflow
1. **Requirements Phase**: Define user stories and acceptance criteria
2. **Design Phase**: Create technical design and correctness properties
3. **Tasks Phase**: Break down into actionable implementation tasks
4. **Implementation**: Execute tasks while maintaining spec alignment

### Content Standards
- **Requirements**: Follow EARS (Easy Approach to Requirements Syntax) patterns
- **Design**: Include architecture, components, data models, and correctness properties
- **Tasks**: Actionable items with clear completion criteria

### Examples of Feature Categories
- **Infrastructure**: `aws-infrastructure`, `monitoring-setup`
- **Development Tools**: `code-server-deployment`, `ci-cd-pipeline`
- **Application Features**: `user-management`, `data-processing`
- **Integration**: `third-party-apis`, `external-services`

### Maintenance
- Keep specs updated as requirements evolve
- Archive completed specs but maintain for reference
- Use specs to guide all implementation decisions