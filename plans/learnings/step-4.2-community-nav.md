# Step 4.2 Learnings — Community Site Navigation

## Changes to mint.json

### Removed from navigation
- "Claude Agent SDK" group (full tutorial tree with 23 modules + reference) — removed entirely from Projects
- From "Agentic" group:
  - Agent Client (with nested Tutorial, How-to, Reference, Explanation groups)
  - agent-judge
  - agent-sandbox
  - agent-bench

### Added to "Moved Projects" (formerly "Attic")
- `projects/incubating/agent-client` (single page)
- `projects/incubating/agent-judge` (single page)
- `projects/incubating/agent-sandbox` (single page)
- `projects/incubating/agent-bench` (single page)
- `claude-agent-sdk/index` (single page)

### Remains in "Agentic"
- `projects/incubating/spring-ai-agent-utils`
- `projects/incubating/github-collector`
- `projects/incubating/spring-ai-tool-search-tool`

## Verification
- JSON validates
- Agentic group has exactly 3 non-migrated projects
- Moved Projects has moonshot, qianfan + 5 migrated projects
- Tutorial pages still exist as files (accessible by direct URL)
- No content deleted
