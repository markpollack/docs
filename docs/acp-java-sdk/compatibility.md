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
| Spring Boot (MVC) | verified | verified | verified |
| Spring Boot (WebFlux) | n/a: always a web application | verified | verified |
| Quarkus | verified | verified | verified |
| Micronaut | verified | verified | verified |

Each framework's own client is verified too, over HTTP (the one client transport the framework smoke
matrix drives today), except Spring Boot (WebFlux): its smoke cell is agent-only, no client leg yet.

<Note>
Every framework row above comes from the framework smoke matrix
(`integration-testing/smoke.json`), the release gate for the framework integrations, landed at
`ffc3b74` and green in CI on every `main` commit since (most recently run `37263353533`, on `57e0b55`,
the commit that added the Spring Boot (WebFlux) cells).
It replaces the narrower, hand-written cells an earlier round of this page described.
</Note>

Each peer SDK is tested against its own `main` (`master` for Kotlin) branch, not a pinned release, so
this matrix reflects an actively moving target on both sides. Each Java-to-peer cell runs **75
catalogue steps** (`integration-testing/steps.json`) covering initialization and capability negotiation, session
lifecycle (new, load, list, resume, close, delete), prompts and streamed updates of every content
type, tool calls and permission requests, file system and terminal operations, elicitation (form and
URL modes), session config options, cancellation (`session/cancel` and `$/cancel_request`), and
extension methods; one further step (`session.fork`) runs separately, since session fork is
`@UnstableAcpApi`.

The framework cells above are narrower than the peer-SDK cells: a TypeScript client against each
framework's own sample agent, running the framework smoke matrix's own step list (initialization and
capability negotiation, session lifecycle, a streamed message, permission requests, form-mode
elicitation, cancellation, one extension method, and connection close, on every transport each
framework serves), not the full 75-step catalogue the peer-SDK cells run.

## Feature comparison across the ACP SDKs

How this Java SDK's 0.80.0 feature set compares to the TypeScript, Python, Rust and Kotlin SDKs, each
checked against its own current `main` (`master` for Kotlin), not a pinned release.

| Feature | Java | TypeScript | Python | Rust | Kotlin |
|---|---|---|---|---|---|
| Annotation programming model | Yes: `@AcpAgent`, `@Prompt`, and the rest | No | No | No | No |
| Framework integrations | Spring Boot, Quarkus, Micronaut | None | None | None | Ktor modules provide transport helpers, not a full framework integration |
| Session config options | Stable | Implemented (typed method, reference docs only) | Implemented, documented in its 0.11 migration guide | Implemented (a migration-table entry only) | Implemented, documented in the README's v2 samples |
| Request cancellation (`$/cancel_request`) | Stable | Implemented | Not yet exposed by the runtime; only a generated method name exists | Implemented, and the most thoroughly documented of the four (a book chapter and a rustdoc concepts chapter) | Implemented |
| Cancel grace period / max prompt duration | Both, each configurable | Neither | Neither | Neither | A grace period only, fixed at one second and not configurable; no max prompt duration |
| Response-follows-its-updates ordering | Documented and guaranteed | Not documented as a guarantee | Not documented as a guarantee | Documented and guaranteed, with its own concepts chapter | Not documented as a guarantee |
| Elicitation | Stable | Stable since 1.4.0 | Still called unstable in its own docs | Implemented, used in its Testy test scenarios; no explicit stability statement found | Still behind `@UnstableApi` |
| Terminal authentication | Documented | Implemented (reference docs only) | One sentence, in the quickstart | Not found | Implemented, code only, no prose |
| Logout | Documented | Implemented (reference docs only) | Documented, called stable | Implemented, used in its Testy method list | Implemented, code only |
| Extension methods (`_`-prefixed) | Stable, typed on every client and agent builder | Documented in its migration guide | Only in its examples | Documented | Implemented, code only |
| Streamable HTTP and WebSocket | Both, stable | Both | Both | Both, on the same page | WebSocket, via Ktor; HTTP infrastructure exists in the README but isn't yet in the cross-SDK interop suite above |
| Forward compatibility (open enums, `_meta`) | Stable: `Unknown*` fallback variants, `_meta` on every record | Partial: extensible-union guards only | Documented: `_meta`, plus `**kwargs` collecting future keys | Partial: `_meta` preserved by its MCP bridge | Implemented: `_meta` is a parameter on every sample method |
| Published cross-SDK compatibility suite | Yes, this page | Not found | Not found | Not found | Not found |

No peer SDK documents all of the rows above; each has its own strengths; Rust's cancellation and
ordering docs and Python's web-transport page are both worth reading regardless of which SDK you use.

Checked against: TypeScript SDK commit `605f3e0a` (v1.7.0, 2026-10-02); Python SDK commit `9d07d787`
(1.0.0rc2, 2026-09-21); Rust SDK commit `65347cfb` (v2.2.0, 2026-10-02); Kotlin SDK commit `3af219ae`
(v0.32.0, 2026-10-01, branch `master`). An SDK's own `main` moves; re-check before relying on an exact
cell.

## Related

<CardGroup cols={2}>
  <Card title="What's New" icon="sparkles" href="/docs/acp-java-sdk/whats-new">
    The short form of this page's interop matrix, in context
  </Card>
  <Card title="ACP Resources" icon="compass" href="/docs/acp-java-sdk/resources">
    The spec site, the other language SDKs, and the wider ecosystem
  </Card>
</CardGroup>
