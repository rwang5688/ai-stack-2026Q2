# Session Notes Management

## Purpose
Maintain organized session notes to track daily progress, decisions, and learnings across development sessions.

## CRITICAL RULES

### ONE FILE PER DAY - NO EXCEPTIONS
- **NEVER create multiple session note files for the same day**
- **ALWAYS use ONLY the standard naming convention**: `yyyymmdd-session-notes.md`
- **NO topic-specific files** (e.g., NO "model-provider-fix.md", NO "temperature-fix.md")
- **NO descriptive suffixes** - just the date
- **ALL content for a day goes in ONE file**
- User STRONGLY prefers streamlined documentation - extraneous files are wasteful and noisy

### File Structure
- Create session notes under `.kiro/session-notes/yyyy/mm/`
- Directory convention: `.kiro/session-notes/{year}/{month}/`
  - e.g., `.kiro/session-notes/2026/05/`
- File naming convention: `yyyymmdd-session-notes.md`
- Full path example: `.kiro/session-notes/2026/05/20260511-session-notes.md`
- **CORRECT**: `.kiro/session-notes/2026/01/20260115-session-notes.md`
- **WRONG**: `.kiro/session-notes/20260115-session-notes.md` (flat, no year/month dirs)
- **WRONG**: `.kiro/session-notes/2026/01/20260115-model-provider-fix.md` (topic-specific)

### Content Guidelines
- **Session Overview**: Brief summary of what was accomplished
- **Key Decisions**: Important technical or architectural decisions made
- **Issues Encountered**: Problems faced and how they were resolved
- **Next Steps**: Action items for future sessions
- **Resources**: Links, documentation, or references discovered

### Example Structure
```markdown
# Session Notes - December 18, 2025

## Session Overview
Brief description of the session's focus and goals.

## Key Accomplishments
- Item 1
- Item 2

## Issues & Resolutions
- **Issue**: Description
  - **Resolution**: How it was solved

## Decisions Made
- Decision 1 with rationale
- Decision 2 with rationale

## Next Steps
- [ ] Action item 1
- [ ] Action item 2

## Resources
- [Link 1](url) - Description
- [Link 2](url) - Description
```

### Maintenance
- Update session notes throughout the day as work progresses
- Review previous session notes at the start of new sessions
- Archive or organize notes monthly for long-term reference

### Checkpoint Commit Workflow
When the user says "checkpoint" or "commit":
1. **IMMEDIATELY** produce a list of **directories containing changed files** (alphabetical order)
2. Include the root-level standalone files that changed (e.g., `workshop4/phase3/README.md` → listed as `workshop4/phase3/`)
3. Remind user to upload to code-server for commit/push (cannot push from Windows PC)
4. Do NOT ask questions, do NOT delay — just produce the list