# Learnings: Documentation Migration

> **Last compacted**: 2026-05-16
> **Covers through**: Stage 3 (lab.pollack.ai complete)

This is the **Tier 1 compacted summary**. For details on specific steps, see the per-step files (Tier 2).

---

## Key Discoveries

- **Zero import/package statements** existed in code examples for migrated projects. Step 2.4 was a no-op.
- **`agent-advisor-judge` no longer exists** in agent-client 0.18.0. Removed from BOM docs and POM.
- **`acp-spring-boot-autoconfigure` / `acp-spring-boot-starter`** (org.springaicommunity) were removed from BOM — consumers manage locally per ownership rule.
- **Tutorial/reference content** for Claude SDK and Agent Client lives only on springaicommunity.mintlify.app — lab.pollack.ai links now point to GitHub tutorial repos instead.
- **springaicommunity.mintlify.app links** remain for non-migrated projects (ACP, agent-tools, spring-ai-a2a) — this is intentional, not stale.

## Patterns Established

- **Migration callout copy variants**: 3 templates used depending on context:
  1. Standard (moved from spring-ai-community, new groupId + packages)
  2. Agent-client specific (mentions old groupId `org.springaicommunity.agents`)
  3. Agent-judge (groupId-only change, repo was already markpollack)
- **BOM ownership rule**: `io.github.markpollack` + `com.agentclientprotocol` only. No `org.springaicommunity`.
- **Non-migrated pages**: removed from nav but kept accessible by direct URL with `<Info>` note

## Deviations from Design

- Roadmap expected "zero hits" for springaicommunity.mintlify.app grep but non-migrated projects (ACP, agent-tools, spring-ai-a2a) legitimately link there. Updated exit criteria to "zero for migrated projects."
- Added `projects/agent-skills` to nav removal (roadmap only listed agent-tools and spring-ai-a2a explicitly, but scope statement includes all three non-migrated projects).
- Migration page "why" section rewritten with architectural rationale (not Spring AI extensions, don't depend on Spring AI) rather than dry "coordinate cleanup" language.

## Common Pitfalls

- agent-client had groupId `org.springaicommunity.agents` (not plain `org.springaicommunity`) — easy to miss in grep filters.
- Claude SDK publishable artifact is `claude-code-sdk` (not `claude-agent-sdk` or `claude-agent-sdk-java`).
- BOM POM changes are in a separate repo (`~/projects/agentworks/`) — must commit separately.

---

## Per-Step Detail Files (Tier 2)

| File | Step | Topic |
|------|------|-------|
| `step-0-pre-execution-context.md` | 0 | Release context and clarifications |
| `step-1.0-inventory.md` | 1.0 | Full classified hit list, Maven Central URLs |
| `step-1.1-migration-page.md` | 1.1 | Migration page decisions |
| `step-2.1-github-urls.md` | 2.1 | GitHub URL changes |
| `step-2.2-maven-coordinates.md` | 2.2 | BOM restructure, version updates |
| `step-2.3-external-links.md` | 2.3 | External docs link changes |
| `step-2.5-remove-community-projects.md` | 2.5 | Nav removal, BOM POM cleanup |
| `step-3.1-migration-notes.md` | 3.1 | Per-page callout additions |

---

## Revision History

| Timestamp | Change | Trigger |
|-----------|--------|---------|
| 2026-05-16T12:30-04:00 | Initial draft | — |
| 2026-05-16 | Compacted through Stage 3 | Stage 3 verification complete |
