# Pre-execution context — 2026-05-16

Context built during the release and planning session that informs roadmap execution.

## Releases confirmed on Maven Central

| Artifact | GroupId | Version | ArtifactId(s) |
|---|---|---|---|
| claude-agent-sdk-java | `io.github.markpollack` | 1.1.0 | `claude-code-sdk` (the publishable module) |
| agent-sandbox | `io.github.markpollack` | 0.9.2 | `agent-sandbox-core`, `agent-sandbox-docker`, `agent-sandbox-e2b` |
| agent-client | `io.github.markpollack` | 0.18.0 | `agent-client-core`, `agent-model`, `agent-claude`, `agent-gemini`, `agent-codex`, `agent-amp`, `agent-amazon-q`, starters |
| agent-journal | `io.github.markpollack` | 1.1.0 | `journal-core`, `claude-code-capture` |
| agent-bench | `io.github.markpollack` | 0.3.0 | `agent-bench-core`, `agent-bench-agents` |
| agent-judge | `io.github.markpollack` | 0.10.0 | `agent-judge-core`, `agent-judge-exec`, `agent-judge-file`, `agent-judge-llm`, `agent-judge-rag`, `agent-judge-spring-ai`, `agent-judge-langchain4j`, `agent-judge-koog`, `agent-judge-agent-client` |

## Key clarifications

- **`claude-code-sdk`** is the Maven artifactId. The GitHub repo is `claude-agent-sdk-java`. The parent POM artifactId is `claude-agent-sdk-parent`. Users depend on `claude-code-sdk`.

- **ACP Java SDK** is NOT spring-ai-community. It's in the official ACP community org (`agentclientprotocol`). GroupId is `com.agentclientprotocol`. Authored by Mark, kept on lab.pollack.ai, managed by AgentWorks BOM. Future migration to `markpollack` GitHub is a separate task.

- **agent-client 0.18.0** no longer contains judge modules. `AgentJudge`, `JudgeAdvisor`, `JuryAdvisor`, and `code-coverage-agent` were removed. `AgentClientResponse` no longer has `getJudgment()`/`getVerdict()`/`isJudgmentPassed()`/`isVerdictPassed()`. The canonical AgentClient→Judge bridge is `agent-judge-agent-client` (in the agent-judge repo).

- **agent-client package root**: uses `io.github.markpollack.agents.*` (note the `.agents.` segment) because it had groupId `org.springaicommunity.agents` (not plain `org.springaicommunity`). Verify from source before replacing in docs.

## BOM ownership rule

- AgentWorks BOM manages: `io.github.markpollack` + `com.agentclientprotocol`
- AgentWorks BOM does NOT manage: `org.springaicommunity`

## What stays on spring-ai-community (do not touch)

- `spring-ai-a2a` — `org.springaicommunity`
- `spring-ai-agent-utils` — `org.springaicommunity`
- `spring-testing-skills` — `org.springaicommunity`

## Docs site paths

- lab.pollack.ai: `~/projects/docs/` (Mintlify, `mint.json`)
- springaicommunity.mintlify.app: `~/community/mintlify-docs/` (Mintlify, `mint.json`)

## springaicommunity.mintlify.app tutorial URLs

The `claude-agent-sdk.mdx` and `agent-client.mdx` pages on lab.pollack.ai link to `springaicommunity.mintlify.app` for tutorials. After Stage 4, those tutorials will have `<Warning>` banners pointing back to lab.pollack.ai. The lab.pollack.ai links should be updated in Stage 2 (Step 2.3) to point locally or to lab.pollack.ai paths.
