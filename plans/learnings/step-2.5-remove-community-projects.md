# Step 2.5 Learnings — Remove Community Projects from lab.pollack.ai

## Changes made

### mint.json navigation
- Removed `projects/agent-tools` from "AgentWorks" group
- Removed `projects/agent-skills` from "AgentWorks" group
- Removed `projects/spring-ai-a2a` from "Supporting Projects" group
- "Supporting Projects" now contains only: `claude-agent-sdk`, `acp-java-sdk`

### Page files (kept accessible by direct URL)
- `projects/agent-tools.mdx` — added `<Info>` note about community ownership
- `projects/agent-skills.mdx` — added `<Info>` note about community ownership
- `projects/spring-ai-a2a.mdx` — added `<Info>` note about community ownership

### projects/agentworks-bom.mdx
- Removed "Community Libraries (org.springaicommunity)" section entirely
- Page now has only: "Agent Engineering (io.github.markpollack)" and "Agent Client Protocol (com.agentclientprotocol)"

### ~/projects/agentworks/pom.xml (BOM POM)
- Removed all `org.springaicommunity` entries (spring-ai-agent-utils, spring-testing-skills, acp-spring-boot-autoconfigure, acp-spring-boot-starter)
- Removed all `org.springaicommunity.agents` entries (old agent-client coordinates)
- Removed `agent-advisor-judge` (no longer exists)
- Added `io.github.markpollack` entries for all migrated projects at current versions:
  - claude-code-sdk 1.1.0
  - agent-bench-core/agents 0.3.0
  - agent-judge-core/llm/exec/file 0.10.0
  - agent-sandbox-core/docker/e2b 0.9.2
  - agent-client-core + models + starters 0.18.0
- Updated journal-core and claude-code-capture from 1.0.0 → 1.1.0
- Kept all `com.agentclientprotocol` entries unchanged

## Verification
- Zero `org.springaicommunity` in BOM POM
- mint.json validates as valid JSON
- No dangling nav references (removed pages still exist as files)

## Notes
- `acp-spring-boot-autoconfigure` and `acp-spring-boot-starter` (org.springaicommunity) were removed from the BOM. Projects consuming these will need to manage versions locally. This follows the BOM ownership rule.
- `agent-skills` page was also removed from nav (spring-testing-skills is a non-migrated community project, same category as agent-tools).
