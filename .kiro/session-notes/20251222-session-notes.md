# Session Notes - December 20 to 22, 2025

## Session Overview
Working backwards from workshop_4 preparation, starting with code-server directory structure improvements and spec organization.

## Key Accomplishments
- Renamed `code_server` directory to `code-server` for consistency with upstream repository

## Issues & Resolutions
- **Issue**: Directory naming inconsistency with upstream coder/code-server repository
  - **Resolution**: Renamed `code_server` to `code-server` to match the official GitHub repository naming convention

## Decisions Made
- **Directory Naming Convention**: Adopted kebab-case naming (`code-server`) to align with the official coder/code-server open source repository at https://github.com/coder/code-server
  - **Rationale**: Maintains consistency with upstream project conventions, making it easier for developers familiar with the official repository to navigate our codebase
  - **Impact**: All references and documentation should use `code-server` going forward

## Next Steps
- [ ] Create new spec for workshop_4 preparation (agentic-ai-workshop)
- [ ] Focus on end-to-end deployment of multi-agent example from Strands SDK and AgentCore workshop
- [ ] Plan variation: Replace BedrockModel with SageMakerAIModel interface class
- [ ] Gather reference code for spec development

## Resources
- [coder/code-server](https://github.com/coder/code-server) - VS Code in the browser (official repository)
- Agentic AI with Strands SDK and AgentCore workshop - Target for workshop_4 preparation
- Multi-agent example deployment - End-to-end focus
- BedrockModel vs SageMakerAIModel interface classes - Planned variation

## Current Workspace Structure
```
.kiro/
├── session-notes/
│   ├── 20251217-session-notes.md
│   └── 20251220-session-notes.md (today)
├── specs/
│   └── code-server-deployment/
│       ├── design.md
│       ├── file-history-documentation.md
│       ├── requirements.md
│       └── tasks.md
└── steering/
    ├── session-notes-management.md
    └── specs-management.md
```

## Updated Plan
- Separate feature specs will be created later for:
  - multi-agent-bedrock implementation
  - multi-agent-sagemaker implementation
- Code will be provided as starting point for requirements analysis

## Workshop4-Preparation Spec Completed
- Created comprehensive spec with requirements, design, and task list
- Focused on content organization rather than technical implementation
- Simplified SageMaker approach to focus on core comparison with Bedrock
- Ready for manual implementation starting with Task 2

## Current Plan
- User will manually create workshop4 directory
- User will work on Task 2 (content framework) independently
- User may request troubleshooting help during sample code testing
- Document any tweaks/modifications needed along the way
- Mark tasks 2, 2.1, 2.2 as complete when manual work is finished
## Cross-Platform Setup Analysis

### UV Compatibility
- ✅ UV works on both Windows and Linux
- Different installation methods per OS but same functionality
- Virtual environment and package management commands are identical

### OS-Independent Components
- Python 3.12 installation via UV
- Virtual environment creation (`uv venv`)
- Package installation (`uv pip install -r requirements.txt`)
- Same requirements.txt file
- Same Python code execution

### OS-Specific Differences to Address
**Linux:**
- Shell completion: `~/.bashrc` modifications
- Virtual env activation: `source ~/.venv/bin/activate`
- jq installation: `sudo apt install -y jq`

**Windows:**
- Shell completion: PowerShell profile modifications
- Virtual env activation: `.venv\Scripts\activate` or `.venv\Scripts\Activate.ps1`
- jq installation: Via Chocolatey, Scoop, or manual download

### Workshop Setup Strategy
- Provide parallel setup instructions for both OS
- Focus on UV as the common tool
- Document activation script differences
- Make jq optional or provide alternatives

## December 22, 2025 - Module 3 IAM Cleanup Fix

### Key Accomplishments
- Fixed critical IAM policy cleanup bug in Module 3 (Knowledge Base)
- Successfully resolved "policy already exists" error that was blocking knowledge base recreation

### Issues & Resolutions
- **Issue**: Module 3 cleanup.py was not deleting orphaned IAM policies, causing "AmazonBedrockOSSPolicyForKnowledgeBase_5393 already exists" error
  - **Root Cause**: Cleanup script only deleted policies attached to roles, but policies became orphaned when roles were deleted first
  - **Specific Policies**: Found 3 orphaned policies with suffix `_5393`:
    - `AmazonBedrockFoundationModelPolicyForKnowledgeBase_5393`
    - `AmazonBedrockOSSPolicyForKnowledgeBase_5393` 
    - `AmazonBedrockS3PolicyForKnowledgeBase_5393`
  - **Resolution**: Enhanced cleanup.py to search for and delete orphaned Bedrock policies using pattern matching

### Technical Fix Details
- Added orphaned policy detection logic to `cleanup_iam_roles()` function
- Uses IAM paginator to scan all customer-managed policies
- Identifies policies with "AmazonBedrock" and "KnowledgeBase" in name
- Successfully tested - cleanup now removes all 3 orphaned policies

### Workflow Improvement
- **Critical Requirement**: Users MUST run `cleanup.py` before `create_knowledge_base.py`
- This ensures IAM roles and policies are aligned with S3, OpenSearch, and Bedrock resources
- Prevents resource conflicts and "already exists" errors

### Validation Results
```
✅ Cleaned up 1 IAM roles and 3 policies
Found orphaned policy: AmazonBedrockFoundationModelPolicyForKnowledgeBase_5393
Found orphaned policy: AmazonBedrockOSSPolicyForKnowledgeBase_5393
Found orphaned policy: AmazonBedrockS3PolicyForKnowledgeBase_5393
✅ Deleted policy: AmazonBedrockOSSPolicyForKnowledgeBase_5393
✅ Deleted policy: AmazonBedrockFoundationModelPolicyForKnowledgeBase_5393
✅ Deleted policy: AmazonBedrockS3PolicyForKnowledgeBase_5393
```

### Next Steps
- [ ] Update workshop documentation to emphasize cleanup-first workflow
- [ ] Update Module 3 documentation in WORKSHOP_MODULES.md
- [ ] Update workshop4-preparation spec task 3.3 status

### Module 3 Completion and Testing

#### Key Accomplishments
- **Module 3 fully implemented and tested** - Knowledge Base agent working end-to-end
- **Documentation updated** - Added comprehensive Module 3 section to WORKSHOP_MODULES.md
- **Cleanup workflow documented** - Emphasized cleanup-first approach in all documentation
- **Task 3.3 marked complete** in workshop4-preparation spec

#### Validation Results
- ✅ **Knowledge Base Creation**: Automated setup works without IAM conflicts
- ✅ **Console Testing**: Knowledge Base queries work from AWS console  
- ✅ **Agent Integration**: Strands agent successfully connects and functions
- ✅ **Dual Functionality**: Both health information retrieval AND personal memory storage working
- ✅ **Memory Persistence**: Memory files visible and accessible in KB console
- ✅ **Cross-platform**: Works reliably on Windows Git Bash environment

#### Documentation Updates
- **WORKSHOP_MODULES.md**: Added complete Module 3 section with cleanup workflow
- **Session Notes**: Documented IAM cleanup fix and testing results
- **Task Spec**: Updated task 3.3 with completion details and fix summary

### Session Summary
Successfully transformed Module 3 from "a pain in the ass" to a reliable, well-documented workshop module. The IAM cleanup fix and cleanup-first workflow ensure students won't encounter the resource conflict issues that were blocking progress.

**Status**: Module 3 complete and ready for workshop delivery.

## UV Virtual Environment Optimization

### Issue Discovered
- **Problem**: `workshop4/setup-environment.sh` was slow on Windows despite existing venv
- **Root Cause**: Script used `uv venv --clear` flag which always recreates virtual environment
- **Impact**: Windows file operations are slower, causing noticeable delay even with existing venv

### Investigation & Solution
- **Research**: Found `uv venv --allow-existing` flag in UV documentation
- **Flag Behavior**: 
  - `--clear`: Always deletes and recreates venv (slow)
  - `--allow-existing`: Preserves existing venv, only creates if missing (fast)
- **Fix Applied**: Replaced `--clear` with `--allow-existing` in setup script

### Performance Impact
- **Before**: Always recreates venv (slow on Windows)
- **After**: 
  - First run: Creates venv (same speed as before)
  - Subsequent runs: Preserves existing venv (much faster, especially on Windows)

### Technical Details
```bash
# Before (slow)
uv venv venv --python "$PYTHON_CMD" --clear

# After (optimized)
uv venv venv --python "$PYTHON_CMD" --allow-existing
```

### Cross-Platform Benefits
- **Linux**: Faster subsequent runs (already fast, now even faster)
- **Windows**: Significant speed improvement on subsequent runs
- **Consistency**: Same behavior across platforms

### Resources
- [UV CLI Reference](https://docs.astral.sh/uv/reference/cli/) - Command line options
- [Linux Command Library - uv venv](https://linuxcommandlibrary.com/man/uv-venv) - Flag documentation