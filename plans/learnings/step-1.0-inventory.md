# Step 1.0 Inventory — 2026-05-16

## Release Gate Verification

All 6 Maven-published artifacts confirmed live on Maven Central:

| Project | GroupId | ArtifactId (checked) | Version | Maven Central URL |
|---|---|---|---|---|
| claude-agent-sdk-java | `io.github.markpollack` | `claude-code-sdk` | 1.1.0 | https://central.sonatype.com/artifact/io.github.markpollack/claude-code-sdk/1.1.0 |
| agent-sandbox | `io.github.markpollack` | `agent-sandbox-core` | 0.9.2 | https://central.sonatype.com/artifact/io.github.markpollack/agent-sandbox-core/0.9.2 |
| agent-client | `io.github.markpollack` | `agent-client-core` | 0.18.0 | https://central.sonatype.com/artifact/io.github.markpollack/agent-client-core/0.18.0 |
| agent-journal | `io.github.markpollack` | `journal-core` | 1.1.0 | https://central.sonatype.com/artifact/io.github.markpollack/journal-core/1.1.0 |
| agent-bench | `io.github.markpollack` | `agent-bench-core` | 0.3.0 | https://central.sonatype.com/artifact/io.github.markpollack/agent-bench-core/0.3.0 |
| agent-judge | `io.github.markpollack` | `agent-judge-core` | 0.10.0 | https://central.sonatype.com/artifact/io.github.markpollack/agent-judge-core/0.10.0 |

## Classified Hit List

### 1. GitHub URLs (`github.com/spring-ai-community`)

#### MIGRATED — needs update

| File | Line | Reference | Target |
|---|---|---|---|
| `docs/agent-bench/getting-started.mdx` | 19 | clone URL `agent-bench.git` | → `markpollack/agent-bench` |
| `projects/claude-agent-sdk.mdx` | 52 | source code card `claude-agent-sdk-java` | → `markpollack/claude-agent-sdk-java` |
| `projects/claude-agent-sdk.mdx` | 55 | tutorial code card `claude-agent-sdk-java-tutorial` | → `markpollack/claude-agent-sdk-java-tutorial` |
| `projects/agent-bench.mdx` | 54 | clone URL `agent-bench.git` | → `markpollack/agent-bench` |
| `projects/agent-bench.mdx` | 95 | GitHub card `agent-bench` | → `markpollack/agent-bench` |
| `projects/agent-sandbox.mdx` | 60 | source code card `agent-sandbox` | → `markpollack/agent-sandbox` |
| `projects/agent-client.mdx` | 51 | source code card `agent-client` | → `markpollack/agent-client` |

#### NON-MIGRATED — leave alone

| File | Line | Reference | Reason |
|---|---|---|---|
| `experiments/code-coverage-v3.mdx` | 34 | `spring-testing-skills` | Non-migrated project |
| `projects/spring-ai-a2a.mdx` | 13 | `spring-ai-a2a` | Non-migrated project |
| `projects/acp-java-sdk.mdx` | 46 | `acp-java-sdk` | Separate ownership (ACP community org) |
| `projects/agent-tools.mdx` | 41 | `spring-ai-agent-utils` | Non-migrated project |
| `projects/agent-skills.mdx` | 41, 80 | `spring-testing-skills` | Non-migrated project |

### 2. Maven GroupIds (`org.springaicommunity`)

#### MIGRATED — needs update

| File | Line | Content | Action |
|---|---|---|---|
| `projects/agent-client.mdx` | 10 | Version 0.16.0 + `org.springaicommunity.agents` search link | → version 0.18.0, groupId `io.github.markpollack` |
| `projects/agentworks-bom.mdx` | 8 | Overview text mentions both groupIds | → remove `org.springaicommunity` from description |
| `projects/agentworks-bom.mdx` | 68-83 | "Community Libraries" section: agent-bench, agent-judge, agent-sandbox, claude-code-sdk under old groupId | → move to io.github.markpollack section with new versions; remove spring-ai-agent-utils + spring-testing-skills entirely |
| `projects/agentworks-bom.mdx` | 85-101 | "Agent Client" section under old groupId | → move to io.github.markpollack section with new versions; remove agent-advisor-judge (no longer exists) |

#### NON-MIGRATED — leave alone

| File | Line | Content | Reason |
|---|---|---|---|
| `projects/agent-tools.mdx` | 27 | `<groupId>org.springaicommunity</groupId>` | spring-ai-agent-utils, non-migrated |

### 3. External Docs URLs (`springaicommunity.mintlify.app`)

#### MIGRATED — needs update

| File | Lines | Count | Content |
|---|---|---|---|
| `projects/agent-client.mdx` | 42, 45, 48 | 3 | Getting Started, Reference, Tutorial links |
| `projects/claude-agent-sdk.mdx` | 13, 16, 26, 29, 32, 35, 38, 41, 49 | 9 | Overview, tutorial modules, API reference |
| `projects/agent-sandbox.mdx` | 57 | 1 | "Full Documentation" link |

#### NON-MIGRATED / SEPARATE — leave alone

| File | Lines | Count | Content | Reason |
|---|---|---|---|---|
| `projects/acp-java-sdk.mdx` | 13, 16, 26, 29, 32, 35, 43 | 7 | ACP tutorial and reference links | ACP separate ownership |
| `projects/index.mdx` | 123 | 1 | "Supporting Projects" description with community link | Update in Step 2.3 or leave (describes non-migrated projects) |
| `projects/spring-ai-a2a.mdx` | 4 | 1 | URL redirect in frontmatter | Non-migrated |
| `projects/agent-tools.mdx` | 38, 49 | 2 | Project overview + blog links | Non-migrated |

### 4. Maven Central Search Links

| File | Line | Content | Action |
|---|---|---|---|
| `projects/agent-client.mdx` | 10 | `central.sonatype.com/search?q=g:org.springaicommunity.agents` | → `central.sonatype.com/search?q=g:io.github.markpollack` |

### 5. Java Import/Package Statements in Code Examples

**Zero hits.** No `import org.springaicommunity` or `package org.springaicommunity` found in any `.mdx` file.

## Additional Observations

1. **BOM page is significantly stale**: Shows agent-client at 0.12.2 (current: 0.18.0), agent-bench at 0.2.1 (current: 0.3.0), agent-judge at 0.9.1 (current: 0.10.0), agent-sandbox at 0.9.1 (current: 0.9.2), claude-code-sdk at 1.0.0 (current: 1.1.0), journal-core at 1.0.0 (current: 1.1.0). All under wrong groupIds.

2. **BOM page lists `agent-advisor-judge`**: This module no longer exists in agent-client 0.18.0 (removed per pre-execution context). Must be removed.

3. **BOM page lists `agent-launcher` and `agent-qwen-code`**: Need to verify these still exist in agent-client 0.18.0. They may have been removed or renamed.

4. **`projects/index.mdx:123`**: Describes "Supporting Projects" with link to springaicommunity.mintlify.app — needs review in Step 2.3 since some of those projects migrated.

5. **Navigation note**: `projects/agent-tools` (= spring-ai-agent-utils) is in "AgentWorks" group currently. Per roadmap Step 2.5, it should be removed from nav.

6. **`projects/agent-journal.mdx`**: Not in the inventory hits — no stale references found there. It appears to already have correct (or no) external URLs. It does not appear to link to spring-ai-community GitHub or springaicommunity.mintlify.app.

## Summary Counts

- **GitHub URLs to update**: 7 hits across 5 files
- **Maven groupIds to update**: 4 areas across 2 files
- **External docs URLs to update**: 13 links across 3 files
- **Maven Central search links to update**: 1 link
- **Import/package statements**: 0
- **Total files needing changes**: 6 unique files (agent-client.mdx, agent-bench.mdx, agent-sandbox.mdx, claude-agent-sdk.mdx, agentworks-bom.mdx, docs/agent-bench/getting-started.mdx)
