# Step 2.2 Learnings — Maven Coordinates Updated

## Changes made

### agent-client.mdx
- Version 0.16.0 → 0.18.0
- Maven Central search URL: `g:org.springaicommunity.agents` → `g:io.github.markpollack+a:agent-client-core`

### agentworks-bom.mdx (major restructure)
- Overview text: removed mention of `org.springaicommunity` (BOM ownership rule)
- Moved to "Agent Engineering (io.github.markpollack)" section:
  - claude-code-sdk 1.0.0 → 1.1.0
  - agent-bench-core/agents 0.2.1 → 0.3.0
  - agent-judge-core/llm/exec/file 0.9.1 → 0.10.0
  - agent-sandbox-core/docker/e2b 0.9.1 → 0.9.2
  - agent-client-core + all models/starters 0.12.2 → 0.18.0
- Updated in-place:
  - journal-core 1.0.0 → 1.1.0
  - claude-code-capture 1.0.0 → 1.1.0
- Removed:
  - `agent-advisor-judge` (already done in prior commit)
  - "Agent Client (org.springaicommunity.agents)" section header (entries moved up)
- Kept temporarily in "Community Libraries":
  - `spring-ai-agent-utils` 0.7.0
  - `spring-testing-skills` 1.0.0
  - (Step 2.5 removes this section entirely)

## Verification

grep for `org.springaicommunity` excluding migration page and non-migrated projects returns:
- `agentworks-bom.mdx:90` — "Community Libraries" section header (temporary, for spring-ai-agent-utils + spring-testing-skills)

Zero stale references for migrated projects.

## Notes

- agent-client 0.18.0 has new modules not yet in BOM docs: `agent-swe`, `agent-client-spring-boot-autoconfigure`, `agent-tck`, and provider-sdk modules. These can be added when the BOM POM is updated (Step 2.5 or separate task).
- agent-judge 0.10.0 has additional modules beyond the 4 listed (agent-judge-rag, agent-judge-spring-ai, agent-judge-langchain4j, agent-judge-koog, agent-judge-agent-client). These can be added when BOM catches up.
