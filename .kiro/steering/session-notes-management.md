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
- Create session notes under `.kiro/session-notes/`
- Use naming convention: `yyyymmdd-session-notes.md`
- Where `yyyymmdd` is the date in format: YYYYMMDD (e.g., 20260115)
- **CORRECT**: `20260115-session-notes.md`
- **WRONG**: `20260115-model-provider-fix.md`, `20260115-temperature-fix.md`, `20260115-comprehensive-review.md`

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