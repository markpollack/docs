---
title: "Cross-SDK Compatibility"
sidebarTitle: "Compatibility"
description: "What the Java SDK is actually tested against: the other ACP SDKs, every transport, and how the two feature tables are kept honest"
---

This page is the detail behind the compatibility claims on [What's New](/docs/acp-java-sdk/whats-new):
what's actually interop-tested today, what's "coming," and how the Java SDK's feature set compares to
its peers. Both tables are re-verified against each SDK's own source, not carried forward from memory;
each cell's source is named below it.

## Cross-SDK interop matrix

The Java SDK's `integration-testing` suite runs real client and agent processes in each language
against each other, over every transport each one supports, and checks what they print. It's not part
of the release build (`./mvnw verify` never runs it); it runs in CI (`cross-sdk.yml`, nightly and on
demand) and locally via `integration-testing/scripts/run-all.sh`.

| | stdio | Streamable HTTP | WebSocket |
|---|---|---|---|
| TypeScript SDK | verified | verified | verified |
| Rust SDK | verified | verified | verified |
| Python SDK | verified | verified | verified |
| Kotlin SDK | verified | n/a: Kotlin has no HTTP transport | verified |
| Spring Boot | coming | coming | coming |
| Quarkus | coming | verified | verified |
| Micronaut | verified | verified | coming |

<Note>
**"Coming" means a cell with no interop test yet, not a feature gap.** A framework smoke-test matrix
(Spring Boot, Quarkus, Micronaut, each against the TypeScript SDK on every transport they support) is
being built now and is expected to land before 0.80.0 ships; this table will be updated the moment it
does, cell by cell, not all at once.
</Note>

Each peer SDK is tested against its own `main` (`master` for Kotlin) branch, not a pinned release, so
this matrix reflects an actively moving target on both sides. Each Java-to-peer cell runs **75
catalogue steps** (`integration-testing/steps.json`) covering initialization and capability negotiation, session
lifecycle (new, load, list, resume, close, delete), prompts and streamed updates of every content
type, tool calls and permission requests, file system and terminal operations, elicitation (form and
URL modes), session config options, cancellation (`session/cancel` and `$/cancel_request`), and
extension methods; one further step (`session.fork`) runs separately, since session fork is
`@UnstableAcpApi`.

The Quarkus and Micronaut cells above are narrower than the peer-SDK cells: they're a TypeScript client
against that framework's own sample agent, running the steps a plain echo agent answers (initialize,
sessions, echo chunks, stop reasons, `-32601`, large prompts and updates), not the full 75-step
catalogue.

## Feature comparison across the ACP SDKs

{/* TABLE PENDING: re-verifying each non-Java cell against each peer's current main/latest release. Filling in once verification completes. */}

## Related

<CardGroup cols={2}>
  <Card title="What's New" icon="sparkles" href="/docs/acp-java-sdk/whats-new">
    The short form of this page's interop matrix, in context
  </Card>
  <Card title="ACP Resources" icon="compass" href="/docs/acp-java-sdk/resources">
    The spec site, the other language SDKs, and the wider ecosystem
  </Card>
</CardGroup>
