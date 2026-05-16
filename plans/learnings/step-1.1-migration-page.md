# Step 1.1 Learnings — Migration Page Created

## What was done

- Created `docs/migration/spring-ai-community-to-markpollack.mdx` with:
  - Repository migration table (7 repos)
  - Maven coordinate changes table (6 published artifacts)
  - Before/after XML snippets using `<Steps>` component
  - Package name migration table (6 projects)
  - "What did NOT move" section (3 spring-ai-community projects)
  - ACP Java SDK `<Note>` clarifying separate ownership
  - Tone follows roadmap guidance (factual, not deprecation language)

- Added "Migration" navigation group to `mint.json` between "Supporting Projects" and "Experiments"

## Decisions made

- Used `<Steps>` for the build-change walkthrough (standard pattern, BOM usage as third step)
- Used `<Note>` (not `<Warning>`) for the ACP clarification — it's informational, not a caution
- Listed `agent-judge` in the "What moved" table noting it was already under `markpollack` — included because the groupId still changed
- Listed `claude-agent-sdk-java-tutorial` in the repo table with no Maven coordinates (it's not published)
- Put migration group after Supporting Projects in nav — logical placement since it references those projects

## Open items for Stage 2

- The `projects/index.mdx:123` "Supporting Projects" description links to `springaicommunity.mintlify.app` and says "Foundational SDKs maintained in the Spring AI Community" — this needs rewording since only ACP and A2A remain community-maintained on that site. Claude SDK and agent-client are now markpollack-maintained.
