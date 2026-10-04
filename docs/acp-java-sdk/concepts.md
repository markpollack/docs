---
title: "Concepts"
sidebarTitle: "Concepts"
description: "The vocabulary ACP and this SDK use: roles, sessions, prompt turns, capabilities, session updates, and the ordering guarantee"
---

This page is the orientation most of the rest of the docs assume. Read it once; everything else
links back to it rather than re-explaining these terms.

## Client and agent

ACP is one JSON-RPC connection with two roles. The **client** sends `initialize`, session methods
(`session/new`, `session/prompt`, ...), and the **agent** answers them, but the agent also calls
*back into* the client for file access (`fs/*`), terminal operations (`terminal/*`), permission
(`session/request_permission`), and elicitation. Neither role is purely a server: both sides send
requests the other must answer.

In Java, the facades are `AcpAsyncClient`/`AcpSyncClient` and `AcpAsyncAgent`/`AcpSyncAgent`. Pick
sync for straightforward blocking code, async (Project Reactor) when you're already reactive or need
non-blocking I/O.

## The naming trap: "session" means two different things

This is the single most common source of confusion in the API, so it gets its own heading.

| Term | What it is | Type |
|---|---|---|
| **ACP session** | The logical conversation your application cares about: a working directory, a history, named by a `sessionId` string that `session/new` returns | Just a `String`; there's no Java type for it |
| **protocol session** (`AcpAgentSession`/`AcpClientSession`) | The JSON-RPC engine running over *one transport*: request IDs, pending responses, timeouts, handler dispatch | `AcpAgentSession`, `AcpClientSession` |

**One `AcpAgentSession` carries many ACP sessions.** A single stdio agent process, or a single
Streamable HTTP connection, has one protocol session underneath it, but a client can open several
ACP sessions (several `sessionId`s) over that same connection. When this doc or the Javadoc says
"session" without qualifying it, assume the ACP session (the `sessionId`) unless the context is
clearly about transport-level plumbing.

## The prompt turn

One `session/prompt` call, from the request to its `PromptResponse` (which carries a `StopReason`).
**A session has at most one active turn at a time**: a second `session/prompt` sent while one is
still running is rejected with `-32600` (invalid request). `session/cancel` does **not** end a turn
by itself; the turn ends when the prompt's answer is published. See
[Cancellation](/docs/acp-java-sdk/cancellation) for the full lifecycle.

Inside a prompt handler, `PromptContext` (async) or `SyncPromptContext` (sync) is the handler's view
of that one turn: the session ID, a way to send updates, and the agent-to-client calls
(`readFile`, `requestPermission`, `createElicitation`, ...).

## Capabilities

Each side advertises what it supports at `initialize`: `ClientCapabilities` and `AgentCapabilities`.
The *other* side's advertised capabilities come back as `NegotiatedCapabilities`, which answers
`supportsX()` (safe to check anytime) and `requireX()` (throws if the capability wasn't advertised).
As of 0.80.0, a client's capabilities are set only on its builder
(`.clientCapabilities(...)`); see [Client setup](/docs/acp-java-sdk/reference/java#client-capabilities).

## Session updates and the ordering guarantee

During a prompt turn, the agent streams `session/update` notifications: message and thought chunks,
tool calls, plans, mode changes, usage, config option changes, and more. The client receives each one
as a `SessionUpdate` variant through its `sessionUpdateConsumer`.

**Ordering guarantee, new in 0.80.0 (client, sync and async):** a response completes its caller only
after every notification received *before* it on the same connection has been handled by the
session-update consumer. In practice: **once `prompt()` returns, that turn's updates have already
been fully handled**: there's no need to wait, poll, or sleep for trailing updates afterward. This
holds for every client request, not only `prompt()`.

Two costs worth knowing:
- A slow consumer delays the response it's blocking, and that delay still counts against the
  request timeout.
- A consumer must not itself block waiting for a prompt that's still in flight: that would deadlock
  it against its own notifications. (To prevent exactly this, a response is never held behind a
  handler that was already running when the response's request was sent, so a consumer *may* safely
  send its own request and wait for that one.)

**The guarantee covers agent-to-client requests too, not only responses.** An agent request
(`session/request_permission`, `fs/*`, `terminal/*`) takes its place in the same ordered drain as a
response: it reaches its client-side handler only after every session update the agent sent before
it has been handled. A `session/request_permission` that follows a `tool_call` update, for example,
is guaranteed to reach its handler after the client has already processed that update, so looking the
tool call up by ID always finds it. The same deadlock-avoidance rule applies: a request already being
handled when another one arrives isn't held up behind it.

This is a Java SDK guarantee, not a protocol one. Rust also guarantees "handled," Kotlin only
guarantees in-order dispatch, and TypeScript and Python make no connection-level promise. Don't
assume it carries over to another SDK.

The union types carrying these updates (`SessionUpdate`, `ContentBlock`, `SessionConfigOption`, and
others) are **not sealed**, so no `instanceof` chain over them is ever exhaustive. Always end with an
`Unknown*` branch and a final default; see
[Forward compatibility](/docs/acp-java-sdk/forward-compatibility).

## Agent-to-client calls

The agent can call back into the client mid-turn: `readFile`/`writeFile` (`fs/*`), terminal
operations (`terminal/*`), `requestPermission`, and `createElicitation`. These are ordinary
request/response calls in the opposite direction from the usual client-to-agent flow: the same
JSON-RPC connection, just initiated by the agent.

## Where handlers run

A sync handler (agent or client) blocks, so it needs a thread from somewhere. By default it runs on
the SDK's own daemon thread pool, the same one used throughout the connection's lifetime. Using the
plain builder API directly, an application can supply its own executor instead with
`handlerExecutor(ExecutorService)`, for example a virtual-thread-per-task executor; the SDK cancels a
handler by cancelling its task (interrupting the thread) and never shuts the executor down itself.
See [Clients and Agents in Java](/docs/acp-java-sdk/clients-and-agents) for where this fits into the
annotated vs. builder picture. None of the three framework integrations
([Spring Boot](/docs/acp-java-sdk/autoconfig), [Micronaut](/docs/acp-java-sdk/micronaut),
[Quarkus](/docs/acp-java-sdk/quarkus)) expose `handlerExecutor` as a property or bean yet; they run
handlers on the SDK's default pool.

## Related

<CardGroup cols={2}>
  <Card title="Session Config Options" icon="sliders" href="/docs/acp-java-sdk/config-options">
    The replacement for session/set_model, and the general mechanism behind it
  </Card>
  <Card title="Cancellation" icon="ban" href="/docs/acp-java-sdk/cancellation">
    The full prompt-cancel and request-cancel lifecycle, with a sequence diagram
  </Card>
  <Card title="Transports" icon="server" href="/docs/acp-java-sdk/transports">
    stdio, Streamable HTTP, WebSocket, and the mountable servlet
  </Card>
  <Card title="Stable vs Unstable" icon="flask" href="/docs/acp-java-sdk/stability">
    The one convention this SDK uses, and what it currently marks unstable
  </Card>
</CardGroup>
