# Session Notes - May 15, 2026

## Session Overview
Reorganized the repository structure to position code-server CloudFormation content under Workshop 1, and added high-level README documentation across all workshop directories.

## Key Accomplishments
- Reviewed the commit that moved `code-server/` from repo root into `workshop1/code-server/`
- Fixed stale internal path references in `DEPLOYMENT.md` and `README.md` (spec paths, session note paths)
- Created top-level `README.md` with workshop table and progression diagram
- Created `workshop1/README.md`, `workshop2/README.md`, `workshop3/README.md` summaries
- Updated `.kiro/steering/specs-management.md` to reflect new `workshop1/` spec directory structure
- Fixed typo in `workshop4/README.md` title ("Microservicess" → "Microservices")
- Refined workshop progression diagram to accurately show relationships:
  - Workshop 1 is independent (optional infra topic, useful for Workshop 4)
  - Workshops 2 → 3 are sequential (train → deploy)
  - Workshop 4 Phases 1 → 2 → 3 are sequential (monolith → container → microservices)
- Removed incorrect claim about us-east-1 (all resources deploy to us-west-2)

## Decisions Made
- Workshop 1 is positioned as optional supplementary material covering CloudFormation and code-server deployment
- README files kept high-level and professional — details left to sub-tree docs
- Workshop 4 theme formalized: "Agentic AI Application Development - From Monolith to Agents as Microservices"

## Next Steps
- [ ] Upload changed files to code-server, commit, and push
- [ ] Prepare PowerPoint slides for workshop presentation
