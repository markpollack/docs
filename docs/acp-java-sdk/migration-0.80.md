---
title: "Migrating to 0.80.0"
sidebarTitle: "Migrating to 0.80.0"
description: "What changes for existing ACP Java SDK consumers upgrading from 0.18.0: a recompile, two removed APIs, open value types, new constructor signatures, and the session/cancel behavior change"
---

**0.80.0 is binary-incompatible with 0.18.0. Applications must recompile against it**, not just
redeploy a new jar. The example below is representative, not exhaustive: `NewSessionResponse(String,
SessionModeState, SessionModelState)` was removed along with `session/set_model`, so any caller
built against the old three-argument constructor fails to link against 0.80.0, even though a
three-argument overload still exists (its third parameter is now `List<SessionConfigOption>`, a
different type). The sections below name every breaking change; this page is the complete list, not
a sample.

## Spring Boot support moved into the SDK

`acp-spring-boot-starter` and `acp-spring-boot-autoconfigure` are now modules of the ACP Java SDK
itself, built and versioned together with it, replacing the separate `spring-ai-community/acp-autoconfig`
project:

| | Before (0.13.0 and earlier) | As of 0.80.0 |
|---|---|---|
| Group ID | `org.springaicommunity` | `com.agentclientprotocol` |
| Package | `com.agentclientprotocol.autoconfigure` | `com.agentclientprotocol.sdk.spring.boot.autoconfigure` |
| Version | Independent (`0.13.0`) | `0.80.0`, matching the SDK |

The `spring.acp.*` property names are unchanged. There is no relocation POM for this move: update the
coordinate and any imports directly rather than relying on a transitive redirect. See the
[Spring Boot Starter page](/docs/acp-java-sdk/autoconfig), now the canonical home for this
integration's documentation.

## Removed: `session/set_model` and the WebSocket-only agent transport

Two APIs that were deprecated for removal are gone.

**`session/set_model` and the session-model API.** Deprecated for removal in 0.14.0; the ACP schema
1.9.1 no longer defines the method, its request and response, or the `models` field on session
responses. Removed: `AcpSchema.METHOD_SESSION_SET_MODEL`, `SetSessionModelRequest`,
`SetSessionModelResponse`, `SessionModelState`, `ModelInfo`; the `models` component of
`NewSessionResponse`, `LoadSessionResponse`, `ResumeSessionResponse`, and `ForkSessionResponse`;
`AcpAgent.SetSessionModelHandler`, `SyncSetSessionModelHandler`, and the builders'
`setSessionModelHandler`; `AcpAsyncClient.setSessionModel` and `AcpSyncClient.setSessionModel`; the
`@SetSessionModel` annotation and `SetSessionModelRequestResolver`; the method's Streamable HTTP
routing entries. An agent built on 0.80.0 no longer answers `session/set_model`: a peer that sends
it gets "method not found".

Migration: expose model selection as a session config option whose `category` is `"model"`, and
change it with `session/set_config_option` (`setSessionConfigOptionHandler`,
`@SetSessionConfigOption`, `AcpAsyncClient.setSessionConfigOption`). This is the same mechanism
already used for session modes (`category: "mode"`) and reasoning level (`category: "thought_level"`).

**The `acp-websocket-jetty` module and `WebSocketAcpAgentTransport`.** Deprecated for removal in
0.18.0; the module held only that class, a WebSocket agent transport that served a single client.

Migration: depend on `acp-streamable-http-jetty` and serve agents with
`StreamableHttpAcpAgentTransport`, which accepts WebSocket upgrades at `/acp` (and the Streamable
HTTP profile on the same path) and creates one agent per connection through an `AcpAgentFactory`:

```java
// Before (removed)
AcpAgent.async(new WebSocketAcpAgentTransport(port, mapper))...build();

// After
new StreamableHttpAcpAgentTransport(port, mapper,
    AcpAgentFactory.async(t -> AcpAgent.async(t)...build()));
```

`WebSocketAcpClientTransport` (`acp-core`) is unchanged and connects to it as before; only the
agent-side, single-client transport is gone.

## Removed: `@SessionState` and `@AcpExceptionHandler`

Both annotations were declared in `acp-annotations` but nothing implemented them: a `@SessionState`
parameter failed every call with "No resolver for parameter", and an `@AcpExceptionHandler` method
was never called. They are removed in 0.80.0, not merely deprecated.

Migration: keep per-session state in the agent itself, in a thread-safe map keyed by the session ID
(an `@SessionId String` parameter or the request's `sessionId()`), and remove it in the
`@CloseSession`/`@DeleteSession` handler. Handle exceptions in the handler method itself, or in an
`AcpInterceptor`'s `onError`, and throw `AcpProtocolException` to answer with a specific JSON-RPC
error.

## Client `initialize(InitializeRequest)` is removed

A client's capabilities and info are now set **only** on its builder, not on the `initialize` call.

**Before:** the builder's `clientCapabilities(...)` was used only by the no-argument `initialize()`;
the request-taking overload silently replaced it. A client that set capabilities on the builder and
then called `initialize(new InitializeRequest(1, new ClientCapabilities()))` advertised nothing,
while its own handlers enforced what the builder said: a real trap, not just an inconsistency.

**Now:**
- `AcpClient.async(...)` / `AcpClient.sync(...)`: `.clientCapabilities(ClientCapabilities)` (as
  before) and the new `.clientInfo(Implementation)`.
- `initialize()` sends protocol version 1 with the builder's capabilities and client info.
- `initialize(int protocolVersion, Map<String, Object> meta)` (new) sends a chosen protocol version
  and `_meta` with the same builder values; for `_meta` and version-negotiation tests, not for
  capabilities.

Migration: move the request's capabilities to `.clientCapabilities(...)` on the builder and its
`clientInfo` to `.clientInfo(...)`, then call `initialize()`; pass `_meta` through
`initialize(1, meta)` instead. A client that passed `new InitializeRequest(1, null)` now advertises
the default `new ClientCapabilities()` (no file system, no terminal) instead of omitting
`clientCapabilities` entirely; check code that relied on omission meaning "nothing negotiated."

```java
// Before (removed)
AcpSyncClient client = AcpClient.sync(transport).build();
client.initialize(new InitializeRequest(1, myCapabilities));

// After
AcpSyncClient client = AcpClient.sync(transport)
    .clientCapabilities(myCapabilities)
    .build();
client.initialize();
```

## Session-update short constructors drop the discriminator

The short constructors of the session-update types no longer take the discriminator string: it
could only ever be the variant's own name, so writing it was noise.

| Was | Now |
|---|---|
| `new ConfigOptionUpdate(null, options)` | `new ConfigOptionUpdate(options)` |
| `new Plan("plan", entries)` | `new Plan(entries)` |
| `new AvailableCommandsUpdate("available_commands_update", commands)` | `new AvailableCommandsUpdate(commands)` |
| `new CurrentModeUpdate("current_mode_update", modeId)` | `new CurrentModeUpdate(modeId)` |
| `new UsageUpdate("usage_update", used, size)` | `new UsageUpdate(used, size)` |
| `new UserMessageChunk(...)`, `AgentMessageChunk(...)`, `AgentThoughtChunk(...)` | `(content)` and `(content, messageId)` overloads, discriminator dropped |

The canonical constructors (discriminator first, `null` or the variant's own name) are unchanged;
`SessionInfoUpdate(title, updatedAt)` already had this shape before 0.80.0. Migration: drop the
first argument wherever one of these short constructors is called, e.g.
`new AgentMessageChunk("agent_message_chunk", content)` becomes `new AgentMessageChunk(content)`.

## Error codes now follow the ACP v1 schema

A prompt sent while the session already has an active prompt used to answer `-32000`, which ACP
defines as "Authentication required", so a client could ask its user to log in when the user had
only sent a second prompt. It now answers **`-32600`** (invalid request), message `There is already an
active prompt on session <id>`, data `{"sessionId": "<id>"}`.

`AcpErrorCodes` keeps only the codes the schema defines:

| Was | Now |
|---|---|
| `AUTHENTICATION_REQUIRED` (`-32004`) | `-32000`; `AcpProtocolException.isAuthenticationRequired()` is new |
| `SESSION_NOT_FOUND` (`-32002`) | renamed `RESOURCE_NOT_FOUND`, the schema's name for the code |
| `CONCURRENT_PROMPT` (`-32000`) | **removed**: a concurrent prompt is `INVALID_REQUEST` (`-32600`) |
| `CAPABILITY_NOT_SUPPORTED` (`-32001`), `NOT_INITIALIZED` (`-32003`), `PERMISSION_DENIED` (`-32005`) | **removed**: these were inside the range ACP reserves for itself. `AcpCapabilityException.toProtocolException()` now answers `-32600` with the capability name as data |

The error a request fails with when the peer answers with a JSON-RPC error is now **one type**,
`com.agentclientprotocol.sdk.spec.AcpError`, on both sides. It replaces the two identical nested
classes `AcpClientSession.AcpError` and `AcpAgentSession.AcpError`. Migration: import
`com.agentclientprotocol.sdk.spec.AcpError` instead. `AcpProtocolException` no longer converts to or
from `JSONRPCError`: use `AcpSchema.JSONRPCError.from(exception)` instead of
`exception.toJsonRpcError()`, and `error.toException()` instead of `new AcpProtocolException(error)`.

## Elicitation is stable

Promoted in protocol v1.7.0; its API is no longer `@UnstableAcpApi`. Three changes come with
stability:

- **The elicitation capability's modes are typed, and the no-argument `ElicitationCapabilities()`
  constructor is removed.** `form` and `url` were `Object`; they are now
  `ElicitationFormCapabilities` and `ElicitationUrlCapabilities`. Migration: `new
  ElicitationCapabilities()` becomes `ElicitationCapabilities.formOnly()`; `urlOnly()` and
  `formAndUrl()` advertise the other modes.
- **`ElicitationAction` is an open value, not an enum** (see the next section): compare with
  `equals`, not `==`; replace a `switch` with `if`/`else` or a switch over `action().value()`.
- **`StringPropertySchema` and `MultiSelectPropertySchema` have only their canonical constructors**,
  which end with `_meta`. Migration: pass `null` as the last argument, or use
  `StringPropertySchema.text(...)` and `singleSelect(...)`.

Two behavior changes follow from the capability now being checked precisely: an agent's
`createElicitation` fails with `AcpCapabilityException` when the client did not advertise the
request's mode (before, any `elicitation` object, even `{}`, let both modes through), and a client
with a typed `createElicitationHandler` answers a request for an unadvertised mode with `-32602`
without calling the handler. Migration: advertise the modes your handler supports in
`clientCapabilities.elicitation`.

## Open value types replace six enums

`StopReason`, `ToolCallStatus`, `PermissionOptionKind`, `PlanEntryStatus`, `PlanEntryPriority`, and
`Role` are now records over the wire string instead of enums, so an unknown value from a newer peer
no longer fails the whole message. The constants keep their names (`StopReason.END_TURN`); `of(String)`
resolves a known value; an unknown value is kept and written back.

| Was | Now |
|---|---|
| `==` comparison | `.equals(...)`: a value built with `new` is not the constant |
| `switch` over the enum | `if`/`equals`, or a switch on `.value()` |
| `values()` | `known()`: lists only the defined values |
| `.name()` | `.value()`: the wire name, e.g. `end_turn`, not `END_TURN` |

`ElicitationAction` (`ACCEPT`, `DECLINE`, `CANCEL`) follows the same rule. `ToolKind` is unaffected:
it stays an enum and reads an unknown kind as `OTHER`, the schema's catch-all; it gains `value()` and
`of(String)` for symmetry.

<Warning>
**Any page or example that prints a status or reason now sees the wire value, not the Java constant
name**: `end_turn`, not `END_TURN`; `cancelled`, not `CANCELLED`. Code that asserts or displays an
exact string needs updating, not just recompiling.
</Warning>

## Constructor signatures changed

Several canonical constructors gained or reordered components. Each example below shows the
canonical (longest) constructor; shorter convenience constructors are listed where they still work
unchanged.

- **`NewSessionResponse`, `LoadSessionResponse`, `ResumeSessionResponse` take `configOptions` before
  `_meta`.** `new NewSessionResponse(id, modes, null)` and `new LoadSessionResponse(modes, null)`
  still compile (the `null` is now the config options), but a call that passed a `_meta` map in
  that position no longer compiles. Migration: pass `(id, modes, configOptions, meta)` or `(modes,
  configOptions, meta)`.
- **`ToolCall`, `ToolCallUpdate`, `ToolCallUpdateNotification` take `name` after `title`.** Migration:
  insert the tool's name, or `null`, after the title argument.
- **`AuthMethod` is an interface; construct `AuthMethodAgent`.** The schema makes `AuthMethod` a
  union. Migration: `new AuthMethod(id, name, description)` becomes `new
  AcpSchema.AuthMethodAgent(id, name, description)`; `id()`, `name()`, and `description()` stay on
  the interface.
- **`ClientCapabilities` takes `session` and `auth` after `terminal`**, in schema order. Migration:
  `new ClientCapabilities(fs, terminal, elicitation, meta)` becomes `new
  ClientCapabilities(fs, terminal, session, auth, elicitation, meta)` (both may be `null`).
- **`AgentCapabilities` takes `auth` after `promptCapabilities`.** Migration: `new
  AgentCapabilities(loadSession, session, mcp, prompt, providers, meta)` becomes `new
  AgentCapabilities(loadSession, session, mcp, prompt, auth, providers, meta)` (`auth` may be `null`).
- **Union records write their own discriminator and reject a wrong one.** A canonical constructor
  now turns `null` into the record's own wire name and throws `IllegalArgumentException` for any
  other value (`new AgentMessageChunk("agentMessage", ...)` used to be silently corrected).
  Migration: pass the variant's wire name (e.g. `"agent_message_chunk"`) or `null`, or use the
  convenience constructors, which already do this. An exhaustive `switch` over a union's known
  records needs a branch for its new `Unknown*` record (below).
- `_meta` was added to 48 records; old-signature constructors are kept except where noted above.

## Session config options: flat or grouped

A select config option's `options()` now returns `SessionConfigSelectOptions`, either
`UngroupedSelectOptions` or `GroupedSelectOptions`: the schema allows a flat list or a list of
groups, and a grouped list used to fail to read. Migration: `select.options()` used as a list becomes
`select.options().allOptions()` (flattens across groups), or match on the two records directly. The
canonical constructor takes `SessionConfigSelectOptions.ungrouped(list)` or `grouped(groups)`; the
`(id, name, currentValue, List<SessionConfigSelectOption>)` constructor is unchanged.

## Forward compatibility: unknown variants no longer fail the message

A newer agent's `sessionUpdate` type, an unknown content block, tool call content type, config
option type, or permission outcome used to fail the whole message, which the client then dropped
with an error log. Each union now reads an unknown variant as its own `Unknown*` record
(`UnknownSessionUpdate`, `UnknownContentBlock`, `UnknownToolCallContent`,
`UnknownSessionConfigOption`, `UnknownPermissionOutcome`), keeping the discriminator and every other
field, and writes it back unchanged. Code that does not know the variant can simply ignore it; code
with an exhaustive switch needs the new branch.

## `session/cancel` no longer ends the prompt turn

This is a behavior change, not just a signature change, and it affects anything that cancels a
prompt and then sends another.

**Before:** the agent session freed the session for a new prompt as soon as the cancel notification
arrived, so a client could start a second prompt while the cancelled one's handler was still
running.

**Now:** ACP v1 says the agent may still send `session/update`s after the cancel and must answer the
original `session/prompt` with stop reason `cancelled`, and that the client may send another prompt
only once that answer arrives. A prompt sent in between is rejected with `-32600` (invalid request),
like any prompt during an active turn. The turn ends when the cancelled prompt's answer is
published, the handler fails, the request is cancelled outright, the session closes, or the cancel
grace period passes.

**New default: a cancelled prompt is answered within 60 seconds.** If the prompt handler has not
answered 60 seconds after `session/cancel`, the agent cancels the handler's subscription and answers
the prompt with stop reason `cancelled` itself. Before, a handler that never answered a cancelled
prompt kept its session busy indefinitely. `cancelGracePeriod(Duration.ZERO)` restores the old
behavior exactly (no grace period, no self-answer).

Migration: clients send the next prompt only after the cancelled one has answered (the SDK client
sends nothing on its own after `cancel`), and agent prompt handlers must answer a cancelled prompt
rather than assume the session is already free.

### `$/cancel_request`, both directions

Separately from `session/cancel`, a request whose caller gives up now tells the peer. Disposing a
request's `Mono` before the response arrives, or its timeout firing (30s default on the client, 60s
on the agent), sends `$/cancel_request {"requestId": ...}` to the peer once; a peer that honors it
answers `-32800` and the caller's `Mono` is cancelled at once regardless. Migration: raise
`requestTimeout` for long prompts if the old behavior (agent keeps running after a client timeout)
is load-bearing anywhere, since 0.80.0 now actually stops the work.

## Smaller breaking changes

| Surface | Change |
|---|---|
| `AcpError.getMessage()` | No longer ends with `[code=N]`: it is the peer's plain message, so `e.getCode() + " " + e.getMessage()` names the code once instead of twice. `toString()` (what stack traces show) still includes `[code=N]`. Code that parsed the code out of the message should call `getCode()` instead |
| `SyncPromptContext.askChoice` | Returns `Optional<String>`, empty on client cancellation (was documented to return `null` and failed instead) |
| `SyncPromptContext` | Gains an abstract `async()` method, returning the `PromptContext` it blocks on (same session, turn, and client). A custom implementation (a test double, say) must implement it |
| `StreamableHttpAcpAgentTransportOptions` | Gains `shutdownTimeout` (builder `shutdownTimeout(Duration)`, default 5 seconds): how long closing the servlet or listener waits for connected agents before closing the rest at once. Breaking only for code calling the record's canonical constructor directly; the builder is unaffected |
| `CommandResult` | `(String output, @Nullable Integer exitCode, @Nullable String signal)`: no `timedOut` flag; a signal-killed command has no exit code |
| `Command.env()` | Never `null`; empty when no variables are set. Migration: test `.isEmpty()` instead of `== null` |
| `AcpInvocationContext`, `AcpMethodParameter` | Moved to `com.agentclientprotocol.sdk.agent.support.invocation`: update imports in custom `ArgumentResolver`, `ReturnValueHandler`, and `AcpInterceptor` implementations |
| Unstable providers API | `ProviderInfo`, `SetProviderRequest`, `DisableProviderRequest` rename `id()` to `providerId()`, matching the unstable schema's actual wire property. `session/fork` and `providers/*` are now consistently marked `@UnstableAcpApi` everywhere they appear |
| Every package | Null-marked (JSpecify `@NullMarked`); Java callers compile unchanged, Kotlin and other nullness-aware callers see the new annotations |

## Fixes worth knowing about, even though nothing to migrate

These don't require a code change, but they change observed behavior, so code that worked around the
old behavior should be revisited.

- **A handler that threw an `Error` used to leave the peer waiting forever.** Any `Throwable`
  escaping a request handler (sync or async, agent or client, annotation-based included) now answers
  `-32603` (Internal error) instead, and the connection keeps serving. This matters directly for the
  0.18.0-to-0.80.0 upgrade itself: a handler calling a removed 0.18.0 constructor throws
  `NoSuchMethodError` at runtime, and before this fix that hung the caller instead of failing fast.
- **`AcpAgentSupport.Builder` can now be built more than once.** Previously, `build()` appended
  custom resolvers/handlers to the builder's own lists, so a second `build()` duplicated them, a
  custom entry added after the first `build()` call never ran, and agents already built silently
  shared (and saw later changes to) the builder's lists. `build()` now snapshots a composed
  configuration without mutating the builder, enabling `AcpAgentSupport.Builder.buildFactory()` (an
  `AcpAgentFactory` that creates a fresh agent per connection from one shared, thread-safe handler
  bean), a new-feature page held until the architecture brief is approved, but the underlying bug fix
  applies now to anyone who builds an `AcpAgentSupport` agent more than once.
- **A client's `prompt()` now returns only after every earlier notification on that connection has
  been handled.** Before, a response could complete its caller while the session-update consumer was
  still processing the turn's last updates, so a caller that read what it had collected right after
  `prompt()` returned could silently miss some. Code that slept, polled, or otherwise waited for
  "trailing" updates after `prompt()` returns can drop that workaround; the guarantee is now built
  in. A slow consumer delays the response and still counts against the request timeout, so a
  consumer that sends its own request and waits for it cannot deadlock against a prompt in flight,
  but must not itself wait for that prompt to complete.
- **The stdio client's graceful close lets the agent exit on its own, instead of always killing it.**
  `closeGracefully()` used to send SIGTERM immediately, without closing the agent's standard input,
  so an SDK stdio agent's own end-of-input handling never ran and every close ended in exit code 143.
  It now closes the agent's standard input first and waits up to two seconds for the agent to exit
  by itself; only an agent still running after that is sent SIGTERM. Code that checked for exit code
  143 as the normal/expected close outcome should check for exit `0` instead. Closing twice (for
  example `closeGracefully()` followed by try-with-resources `close()`) no longer stops the process
  or logs the stop message a second time.

## What you may have to change: a quick checklist

1. **Recompile.** This is not a drop-in jar swap.
2. Grep for `session/set_model`, `SetSessionModel`, `SessionModelState`, replacing with a `"model"`
   category config option.
3. Grep for `acp-websocket-jetty`, `WebSocketAcpAgentTransport`, switching to
   `acp-streamable-http-jetty` and `StreamableHttpAcpAgentTransport`.
4. Grep for `== ` comparisons against `StopReason`, `ToolCallStatus`, `Role`,
   `PermissionOptionKind`, `PlanEntryStatus`, `PlanEntryPriority`, or `ElicitationAction` constants,
   switching to `.equals(...)`.
5. Grep for exhaustive `switch` statements over any of the above, or over a union type
   (`SessionUpdate`, `ContentBlock`, `ToolCallContent`, `SessionConfigOption`,
   `PermissionOutcome`), adding the new `Unknown*` branch, or the open-value fallback.
6. Check any code that sends a second prompt immediately after `session/cancel`: it now needs to
   wait for the cancelled prompt's answer.
7. Check any test or display code that asserts an exact status string: it now sees the wire value
   (`end_turn`), not the enum name (`END_TURN`).
8. Grep for `@SessionState` and `@AcpExceptionHandler`: both are removed (they were non-functional
   placeholders). Move session state into the agent itself; handle exceptions in the handler or an
   `AcpInterceptor`.
9. Grep for `initialize(new InitializeRequest(`: move capabilities to `.clientCapabilities(...)` on
   the client builder and call `initialize()` instead.
10. Grep for discriminator-first short constructors of `Plan`, `AvailableCommandsUpdate`,
    `CurrentModeUpdate`, `UsageUpdate`, `ConfigOptionUpdate`, `UserMessageChunk`, `AgentMessageChunk`,
    and `AgentThoughtChunk` (e.g. `new Plan("plan", ...)`): drop the first argument.
11. If any code constructs `StreamableHttpAcpAgentTransportOptions` via its canonical constructor
    (not the builder), add the new `shutdownTimeout` component.
12. If any `SyncPromptContext` is implemented directly (a test double, typically), implement the new
    abstract `async()` method.
13. If you use Spring Boot support, change `org.springaicommunity:acp-spring-boot-starter`/
    `acp-spring-boot-autoconfigure` to `com.agentclientprotocol`, update the version to `0.80.0`, and
    fix any import of `com.agentclientprotocol.autoconfigure.*` to
    `com.agentclientprotocol.sdk.spring.boot.autoconfigure.*`. Property names are unchanged.
