# Step 2.1 Learnings — GitHub URLs Updated

## Changes made

| File | Change |
|---|---|
| `projects/agent-client.mdx:51` | Source code card → `markpollack/agent-client` |
| `projects/agent-sandbox.mdx:60` | Source code card → `markpollack/agent-sandbox` |
| `projects/agent-bench.mdx:54` | Clone URL → `markpollack/agent-bench` |
| `projects/agent-bench.mdx:95` | GitHub card → `markpollack/agent-bench` |
| `projects/claude-agent-sdk.mdx:52` | Source code card → `markpollack/claude-agent-sdk-java` |
| `projects/claude-agent-sdk.mdx:55` | Tutorial code card → `markpollack/claude-agent-sdk-java-tutorial` |
| `docs/agent-bench/getting-started.mdx:19` | Clone URL → `markpollack/agent-bench` |

## Verification

Post-change grep for `github.com/spring-ai-community` in `.mdx` files shows only:
- `spring-testing-skills` (non-migrated) — 3 hits
- `spring-ai-a2a` (non-migrated) — 1 hit
- `acp-java-sdk` (separate ACP org) — 1 hit
- `spring-ai-agent-utils` (non-migrated) — 1 hit

Zero hits for any migrated project.

## Notes for next steps

- `projects/agent-client.mdx` still has stale version (0.16.0) and old groupId — addressed in Step 2.2
- `projects/claude-agent-sdk.mdx` still links to `springaicommunity.mintlify.app` for tutorials — addressed in Step 2.3
