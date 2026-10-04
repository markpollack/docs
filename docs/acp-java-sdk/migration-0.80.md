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

## Annotation model: capabilities derived from handlers, and new return/parameter support

An annotated agent with no `@Initialize` method now gets one derived from the class: each handler
annotation advertises the capability its method needs, `@Prompt`'s `image`/`audio`/`embeddedContext`
attributes and `@AcpAgent`'s `mcpHttp`/`mcpSse` declare the rest, and `agentInfo`/`authMethods` come
from `@AcpAgent`'s own attributes. See
[Clients and Agents in Java](/docs/acp-java-sdk/clients-and-agents) for the full shape. This is
additive (an existing `@Initialize` method keeps working, now overlaid on the derived response), but
it changes several things enough to call out directly:

- **`@SetSessionMode` or `@SetSessionConfigOption` without a `@NewSession` method is now a build
  error.** Those two set state a session needs to exist first; an agent offering either must also
  offer a way to create the session with the options they set.
- **Every agent needs a `@Prompt` method (or a prompt handler, on the plain builder).** Building one
  without it now fails with `IllegalStateException`, rather than silently answering "Method not
  found" for every prompt at runtime.
- **A handler-implied capability can no longer be withdrawn by an `@Initialize` method.** Capabilities
  merge by OR: a handler's presence always means "advertised," even if the `@Initialize` response
  returned doesn't mention it. If you relied on `@Initialize` to selectively suppress a capability a
  handler would otherwise imply, remove the handler instead (or gate it so it isn't registered).
- **Misuse of the annotation model now fails at registration, not at the first call.** Two handler
  methods for one annotation, two handler annotations on one method, a parameter no resolver can
  supply, `@SessionId`/`@ConfigId`/`@ConfigValue` on a method that doesn't have a session or config
  option to supply it from, and a request handler declared `void` or returning the wrong type: all of
  these now throw when the agent is built, each naming the class, method, and fix, instead of
  behaving unpredictably (or not at all) once traffic arrives.
- **`MonoHandler` is renamed `AsyncValueHandler`**, and now also handles `CompletionStage` and any
  single-value Reactive Streams `Publisher`, not only `Mono`. Code referencing the class by name
  (a custom `ReturnValueHandler` composed alongside it, say) needs the new name. A `Publisher` that
  emits more than one value now fails the call, where it previously wasn't a supported return type at
  all.
- **`PromptContext` and `SyncPromptContext` gain abstract methods**: `isCancelled()` on both,
  `onCancel(Runnable)` on `SyncPromptContext`, `whenCancelled()` on `PromptContext`. A custom
  implementation of either interface, typically a test double, must implement the new methods.
- **`AcpAgentSupport.Builder.buildFactory()` now throws if `transport(...)` was also set** (a listener
  supplies its own transport per connection, so the two are mutually exclusive), and both `build()`
  and `buildFactory()` throw `IllegalStateException` if no agent bean was given at all. Previously
  these cases either weren't checked or failed less clearly downstream.

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
request's `Mono` before the response arrives, or its timeout firing (60s default on both sides as of
api1; see below), sends `$/cancel_request {"requestId": ...}` to the peer once; a peer that honors it
answers `-32800` and the caller's `Mono` is cancelled at once regardless. Migration: raise
`requestTimeout` for long prompts if the old behavior (agent keeps running after a client timeout)
is load-bearing anywhere, since 0.80.0 now actually stops the work.

## The fix4 batch: lifecycle renames, sync exceptions, timeouts, and more

A large, later batch of breaking changes, verified against the CHANGELOG at the exact commit that
introduced them (`74fa003`), not just a relayed summary.

### Lifecycle names line up, and both sync facades close gracefully

- **`AcpSyncAgent.await()` is renamed `awaitTermination()`**, matching `AcpAsyncAgent` and the
  transports. Migration: rename the call.
- **`AcpSyncAgent` and `AcpAgentSupport` implement `AutoCloseable`**, and `close()` now means what it
  means on `AcpSyncClient`: close gracefully, waiting at most 10 seconds, then close at once if that
  failed or took longer (`AcpSyncAgent.close()` used to close at once; `AcpAgentSupport.close()` used
  to wait up to the 5-minute block timeout and never force). For the old immediate close, call
  `agent.async().close()`. New `AcpSyncClient.async()` returns the `AcpAsyncClient` it blocks on.
  Migration: use try-with-resources on the sync agent and the annotated agent, the same pattern
  already shown for `AcpSyncClient`.
- **`StdioAcpClientTransport.awaitForExit()` is renamed `awaitProcessExit()`**, so it doesn't sit
  beside `awaitTermination()` (which completes when the transport ends, not the process). Interrupted,
  it now throws `CancellationException` (interrupt flag kept) instead of a plain `RuntimeException`
  (interrupt flag cleared). Migration: rename the call; catch `CancellationException` instead.

### The sync API's exceptions change shape

**Breaking:** the sync API throws `AcpTimeoutException` for a timeout, and `CancellationException`
when interrupted, instead of Reactor's internal `Exceptions$ReactiveException`. Every blocking method
of `AcpSyncClient`, `AcpSyncAgent`, and `SyncPromptContext` used to let a request timeout escape as
`reactor.core.Exceptions$ReactiveException` (cause `TimeoutException`); both now throw
`com.agentclientprotocol.sdk.error.AcpTimeoutException` (an `AcpException`), whose cause is the
`TimeoutException`. A blocked call whose thread is interrupted (the SDK interrupts a sync handler to
cancel it) throws `java.util.concurrent.CancellationException` and leaves the interrupt flag set. The
async API is unchanged (its `Mono` still fails with the `TimeoutException` itself). Migration: replace
`catch (RuntimeException e) { if (e.getCause() instanceof TimeoutException) ... }` (or
`Exceptions.unwrap(e)`) with `catch (AcpTimeoutException e)`, and catch `CancellationException` where
you handled an interrupt. See [Errors](/docs/acp-java-sdk/errors) for the full exception picture.

### A client's prompt is no longer bounded by the request timeout {#prompt-no-longer-bounded-by-request-timeout}

**Breaking (behavior):** a prompt's answer comes only at the end of its turn, so the request timeout
(30 seconds by default on the client at the time this landed, in fix4; one default of 60 seconds
everywhere came later, in api1, see below) used to cancel every turn that ran longer, sending the
agent `$/cancel_request` and failing the call with a `TimeoutException`. `session/prompt` now waits for the
end of the turn however long it takes; every other request keeps the request timeout. Migration: to
keep a bound on turns, set `.promptTimeout(Duration.ofMinutes(10))` on the client builder (any
positive duration; it fails the call with a `TimeoutException` and sends `$/cancel_request`, as
before); code that raised `requestTimeout` only to let long turns finish can drop that workaround. In
Spring Boot, `spring.acp.client.prompt-timeout`; in Micronaut, `acp.client.prompt-timeout`; in
Quarkus, `quarkus.acp.client.prompt-timeout` (unset by default on all three).

### `sendUpdate` drops the session ID

**Breaking:** `PromptContext.sendUpdate(update)` and `SyncPromptContext.sendUpdate(update)` replace
the two-argument `sendUpdate(sessionId, update)`. The context already belongs to one prompt's
session, so the ID was redundant (and a wrong one silently sent the update to another session).
Migration: drop the first argument, `context.sendUpdate(sessionId, update)` becomes
`context.sendUpdate(update)`; to update a *different* session from outside its own prompt handler,
call `AcpAsyncAgent.sendSessionUpdate(sessionId, update)` (or `AcpSyncAgent.sendSessionUpdate`)
instead, which is unchanged. A custom `PromptContext`/`SyncPromptContext` implementation (a test
double) implements the new one-argument method.

### Builders reject a null handler and a duplicate registration

**Breaking:** the typed setters of `AcpAgent.AsyncAgentBuilder` and `AcpAgent.SyncAgentBuilder` used
to accept `null` (every request for that method was then answered `-32603`), and registering a
handler for a method a second time silently replaced the first. A null handler now fails with
`IllegalArgumentException` at the setter; a second registration for the same method (protocol or
extension) fails with `IllegalStateException` naming the setter, for example "A handler for
session/prompt is already registered; promptHandler was called twice on this builder." Migration:
register each handler once; decide which handler to use before calling the setter, not after.

### `handlerExecutor` replaces the static handler pools; two public constants are gone

**Breaking:** sync handlers (and a sync client's session-update consumers) used to run on static,
unbounded, JVM-wide cached thread pools exposed as `AcpAgent.SYNC_HANDLER_SCHEDULER` and
`AcpClient.SYNC_HANDLER_SCHEDULER`. New `handlerExecutor(ExecutorService)` on `AcpAgent.SyncAgentBuilder`,
`AcpClient.SyncSpec`, and `AcpAgentSupport.Builder` (for annotated agents) lets you pass an executor
of your own, for example `Executors.newVirtualThreadPerTaskExecutor()`, or a framework's own worker
pool (Quarkus's, Micronaut's `TaskExecutors.BLOCKING`); the SDK cancels a handler by cancelling its
task (interrupting the thread) and never shuts the executor down itself. Without one, handlers keep
running on the same daemon pools as before, so this is additive for most applications. `AcpAgent.DEFAULT_REQUEST_TIMEOUT`
is also removed; the default (60 seconds) is just stated on `requestTimeout`'s own Javadoc now.
Migration: drop any reference to `AcpAgent.SYNC_HANDLER_SCHEDULER`/`AcpClient.SYNC_HANDLER_SCHEDULER`
(use your own scheduler, or `handlerExecutor(...)` to choose where handlers run), and replace
`AcpAgent.DEFAULT_REQUEST_TIMEOUT` with `Duration.ofSeconds(60)` directly. See
[Clients and Agents in Java](/docs/acp-java-sdk/clients-and-agents) for where this fits into the
bigger annotation/builder picture, and the framework integration pages for the executor each one
recommends.

### `askPermission`/`askChoice` now announce a tool call

**Breaking (behavior):** `askPermission` and `askChoice` used to ask about a tool-call ID the client
had never been told about (a client that looked it up in its own tool-call list found nothing), and
`askPermission` always labeled the action `edit`. Both now announce the tool call first with a
`tool_call` session update (status `pending`), ask about it, and settle it with a `tool_call_update`
(`completed` once answered, `failed` if the client cancelled the request): session-update consumers
now see two more updates per call. `askPermission(action)` uses kind `other`; a new overload,
`askPermission(action, ToolKind kind)`, sets it explicitly, for example
`askPermission("Run the tests", ToolKind.EXECUTE)`. Migration: none needed to keep working; to keep
the old `edit` kind, call `askPermission(action, ToolKind.EDIT)`. Separately, `askChoice` used to parse
the chosen option ID as an index and fail with `NumberFormatException` or
`ArrayIndexOutOfBoundsException` on an unexpected answer; it now fails clearly, naming the ID (reason
`unoffered-option`, as `AcpError` since api1, see below). Implementations of `PromptContext`/
`SyncPromptContext` (test doubles) add the new `askPermission` overload.

## The api1 batch: one error type, stricter client builders, and a few new conveniences

The next batch after fix4, verified against the CHANGELOG and the code at the commit that introduced
it (`bc11736`).

### A caller catches one type, `AcpError`, for every failed request

**Breaking:** the two-type split this guide and [Errors](/docs/acp-java-sdk/errors) described through
fix4 (`AcpError` for a peer's own error; `AcpProtocolException` for the SDK's own local rejection of a
malformed response) collapses to one type a caller ever catches. A missing required field, a response
with no result (reason `missing-result`), a result that can't be read as the method's type (reason
`unreadable-result`), and `askChoice` answered with an option it never offered (reason
`unoffered-option`, see above) all now fail with `AcpError`, code `-32603`, `getData()` a map with
that `reason` and the request's `method`. `AcpTimeoutException`, `CancellationException`, and
`AcpCapabilityException` keep their own types; they were never JSON-RPC errors in the first place.
Migration: replace `catch (AcpProtocolException e)` around a client or agent call with
`catch (AcpError e)`; `AcpProtocolException` remains exactly what a handler throws to answer with an
error, it just no longer crosses to the caller's side on its own. See
[Errors](/docs/acp-java-sdk/errors) for the full picture, including the two exceptions, now also
living on that page, that mean a call was never sent at all: `AcpCapabilityException` and
`IllegalStateException`, both covered next.

### A client initializes first, and calls only what the agent advertised

**Breaking (behavior):** every `AcpAsyncClient`/`AcpSyncClient` call but `initialize` itself now fails
with `IllegalStateException` ("Call initialize() first: the agent has not answered initialize yet")
until the agent has answered; it used to be sent regardless, relying on the agent to reject it.
`loadSession`, `listSessions`, `closeSession`, `deleteSession`, `resumeSession`, `forkSession`,
`logout`, and the `providers/*` calls additionally fail with `AcpCapabilityException` (naming the
capability, for example `sessionCapabilities.close`) when the agent's `initialize` answer didn't
advertise it, the same check the agent side already applies to the client's own capabilities. Neither
check sends anything. The check runs when the call is subscribed, not when it's built, so
`client.initialize().then(client.newSession(request))` works without waiting for `initialize` to
complete first; extension calls (`sendExtRequest`, `sendExtNotification`) are outside ACP's lifecycle
and skip both checks. Migration: call `initialize()` first; check `getAgentCapabilities()` before an
optional call, or catch `AcpCapabilityException`. A test agent with its own `initializeHandler` must
advertise the capabilities its handlers serve, or drop the handler (a builder agent's default
`initialize` advertises them for you).

### A client's advertised capabilities must have their handlers {#client-capabilities-must-have-their-handlers}

**Breaking (behavior):** `AcpClient.AsyncSpec`/`SyncSpec.build()` now throws `IllegalStateException`
("The client advertises capabilities it has no handler for: ...") when the client capabilities
advertise `fs.readTextFile` without `readTextFileHandler`, `fs.writeTextFile` without
`writeTextFileHandler`, `terminal` without all five terminal handlers, or an elicitation mode without
`createElicitationHandler`. Such a client used to build, and the agent's requests were answered
"Method not found" at runtime instead of failing at startup. A handler for a capability the client
does not advertise now also logs one WARN, since an SDK agent will never call it. The Spring Boot,
Micronaut, and Quarkus client beans add the specific property that advertised the capability to the
message. Migration: register the handlers (in an `AcpClientCustomizer` when the capabilities come from
properties), or stop advertising the capability. The test `MockAcpClient` (`acp-test`) no longer
advertises `terminal`, which it never served; a test that checked for it being advertised needs
updating.

### Client builders reject a null, duplicate, or misdirected handler too

**Breaking:** the same discipline fix4 added to the agent builders now applies to
`AcpClient.AsyncSpec`/`SyncSpec`. Registering a second handler for one method (a typed setter such as
`readTextFileHandler` called twice, `requestHandler`/`notificationHandler` for a method that already
has one, a raw handler and the typed setter for the same method) throws `IllegalStateException`
("A handler for `<method>` is already registered on this builder; `<setter>` cannot register a second
one"), instead of silently replacing the first; `sessionUpdateConsumer` stays additive. A raw
`requestHandler(method, ...)`/`notificationHandler(method, ...)` for a method the SDK already models
(`fs/read_text_file`, the five `terminal/*` methods, `session/request_permission`,
`elicitation/create`, `session/update`, `elicitation/complete`) now throws `IllegalArgumentException`
naming the typed setter to use instead: the raw handler bypassed the typed params and, for elicitation,
the mode check. `SyncSpec.notificationHandler` is now a blocking `Consumer<Object>`, run on the sync
handler threads like the sync builder's other handlers, instead of the async `NotificationHandler`
returning a `Mono`. Migration: register each handler once; use the named typed setter for a modelled
method; on the sync builder, drop the `Mono` from a raw notification handler body.

### `SessionConfigSelect.Builder.build()` checks the option's value

**Breaking:** it now throws `IllegalStateException` when the options (across every group) are empty,
or when `currentValue` isn't the value of one of them, instead of building an option no client could
display correctly. The record's canonical constructors stay lenient, since they also read other
agents' options over the wire, which might (by a bug on their side) be shaped this way; only the
builder, used to construct your own options, enforces it. Migration: pass at least one option, and set
`currentValue` to one of their values. See [Session Config Options](/docs/acp-java-sdk/config-options).

### Two new conveniences

- **One default request timeout, 60 seconds, everywhere.** The client builders
  (`AcpClient.sync`/`async`) and `AcpAgentSupport.Builder` defaulted to 30 seconds while the agent
  builders defaulted to 60; all four now default to 60. 60 seconds because an agent's own requests (a
  permission prompt, an elicitation) wait on a person, and a client's `session/new` may wait for the
  agent to start its MCP servers. `AcpAgentSupport.Builder.requestTimeout` now accepts `null`, meaning
  the SDK default. The Spring Boot (`spring.acp.client.request-timeout`) and Micronaut
  (`acp.client.request-timeout`) properties default to 60s too; Quarkus's
  `quarkus.acp.client.request-timeout`, left unset, already followed the SDK default either way.
  Migration: none needed; to keep the old 30-second client bound, set
  `requestTimeout(Duration.ofSeconds(30))` (or the property to `30s`).
- **`defaultSessionUpdateConsumer(..)` on `AcpClient.AsyncSpec`/`SyncSpec`**: a consumer that runs only
  while no `sessionUpdateConsumer` has been added, so a framework can supply a default (logging each
  update at DEBUG, say) that the application's own consumer replaces outright rather than running
  beside. The Spring Boot, Micronaut, and Quarkus client beans now register their DEBUG logging this
  way. `sessionUpdateConsumer` itself stays additive, as before.
- **Shortcuts for the messages real code writes most**: `new NewSessionRequest(cwd)` (no MCP servers),
  `new NewSessionResponse(sessionId)` (no modes or config options), and `PromptRequest.text(sessionId,
  text)` (a prompt of one text block). Each equals, and writes the same JSON as, the long form; prefer
  them in new code wherever the full form adds nothing.

## `acp-integration`: a shared layer under all three framework integrations, and what moves because of it

Verified against the CHANGELOG and the code at the commit that introduced it (`c5084f5`). Spring Boot,
Micronaut, and Quarkus support are now thin layers over one new module,
`com.agentclientprotocol.sdk.integration` (`acp-integration`): settings, transport selection,
discovery, agent/client assembly, and lifecycles, implemented once and shared. See
[Concepts: the framework-neutral layer](/docs/acp-java-sdk/concepts#the-framework-neutral-layer-acp-integration)
for what it actually contains; this section covers what moved or changed as a result, framework by
framework.

### `AcpClientCustomizer` and the transport-type enum move

**Breaking:** both types are now framework-neutral, in `com.agentclientprotocol.sdk.integration`,
replacing a separate copy (and a separate `TransportType` enum) in each framework's own package.
Migration: fix the import to `com.agentclientprotocol.sdk.integration.AcpClientCustomizer` and
`com.agentclientprotocol.sdk.integration.AcpTransportType`, wherever either was imported from a
framework-specific package.

### Spring Boot: several property changes

Migrating from `org.springaicommunity:acp-spring-boot-starter` 0.12.0, or from an earlier 0.80.0
candidate build of this same starter, several things change beyond the coordinate move already
described above:

- **`spring.acp.agent.request-timeout` and `spring.acp.client.request-timeout` have no default of
  their own** (an earlier candidate's `60s` row in each properties table was the SDK's default showing
  through, not Spring's own): unset, both keep following the SDK's one default request timeout, so a
  future SDK default change would reach these properties automatically.
- **Several client transports configured with no explicit `transport.type` now fail at startup**,
  naming them: `"Several ACP client transports are configured [...]; choose one with
  spring.acp.client.transport.type."` The stdio/websocket/http precedence order it used to pick
  silently is gone.
- **The listener-only agent properties move**: `spring.acp.agent.transport.http.port` becomes
  `spring.acp.agent.transport.http.listener.port`, and
  `...http.max-concurrent-streams-per-connection` becomes
  `...http.listener.max-concurrent-streams-per-connection`. They meant nothing in a servlet web
  application (which serves the endpoint on its own server and `server.port`) even before this move;
  now they're grouped under a prefix that makes that explicit.
- **`spring.acp.agent.transport.type=websocket` is accepted**, meaning the same as `http`: the endpoint
  takes WebSocket upgrades on its path either way.
- **New properties**: `spring.acp.client.capabilities.elicitation-form`, `.elicitation-url` and
  `.boolean-config-options` (the last needs no handler, unlike the others);
  `spring.acp.agent.cancel-grace-period` and `spring.acp.agent.max-prompt-duration`; and
  `spring.acp.agent.handler-executor`, see below.
- **`ArgumentResolver` and `ReturnValueHandler` beans are now added to the agent**, the same as
  `AcpInterceptor` beans already were: register one as a plain `@Bean` and it's picked up automatically,
  in bean order, with no further wiring.
- **The agent's handler methods can run on a Spring executor.** `spring.acp.agent.handler-executor`
  names an `Executor` bean (a plain `TaskExecutor` is adapted), or `none` for the SDK's own pool.
  Unset, they run on the context's `applicationTaskExecutor` only when
  `spring.threads.virtual.enabled=true` (a virtual thread per handler); without virtual threads that
  executor is a pool of 8 threads by default, which would cap the prompts served at once, so the SDK's
  own pool stays the default instead. See
  [Spring Boot: Where handlers run](/docs/acp-java-sdk/autoconfig#where-handlers-run).
- **Closing the client waits at most its request timeout plus 10 seconds, then closes it at once**,
  bounded rather than left to whatever Spring's own shutdown ordering happened to do.
- Everything else in this release's breaking changes still applies: Spring applications compile
  against the SDK's current API, same as any other consumer.

Migration: update any `transport.http.port`/`...max-concurrent-streams-per-connection` properties to
their `.listener.*` form; set `transport.type` explicitly wherever more than one transport property is
set; register `ArgumentResolver`/`ReturnValueHandler` beans the same way `AcpInterceptor` beans already
are, if you have any outside the autoconfiguration's own discovery.

### Micronaut: handler methods run on virtual threads on JDK 21+

**Behavior change, not a property:** on JDK 21 and later, the agent's handler methods run on
Micronaut's virtual-thread executor (`TaskExecutors.VIRTUAL`) instead of the SDK's own pool; on JDK 17
they stay on the SDK's pool. This is automatic, with nothing to configure, and deliberately not
`TaskExecutors.BLOCKING` (Micronaut's I/O pool): that pool's non-daemon threads would keep a stdio
application's process alive past the point its context closes. See
[Micronaut: Where handlers run](/docs/acp-java-sdk/micronaut#where-handlers-run).

### Quarkus: the same transport strictness, and handlers on the `ManagedExecutor`

**Breaking (behavior):** several client transports configured with no explicit
`quarkus.acp.client.transport.type` now fail at startup, naming them, the same as Spring Boot and
Micronaut; it used to infer WebSocket, then HTTP, then stdio, silently picking the first one
configured. Migration: set `transport.type` explicitly wherever more than one transport property is
set.

**Additive:** the agent's handler methods now run on the `ManagedExecutor` (Quarkus' own worker pool,
with the application's contexts propagated) instead of a second pool of the SDK's; nothing to
configure. See [Quarkus: Where handlers run](/docs/acp-java-sdk/quarkus#where-handlers-run).

## Smaller breaking changes

| Surface | Change |
|---|---|
| `AcpError.getMessage()` | No longer ends with `[code=N]`: it is the peer's plain message, so `e.getCode() + " " + e.getMessage()` names the code once instead of twice. `toString()` (what stack traces show) still includes `[code=N]`. Code that parsed the code out of the message should call `getCode()` instead |
| `SyncPromptContext.askChoice` | Returns `Optional<String>`, empty on client cancellation (was documented to return `null` and failed instead) |
| `SyncPromptContext` | Gains abstract `async()`, `isCancelled()`, and `onCancel(Runnable)` methods; `PromptContext` gains abstract `isCancelled()` and `whenCancelled()`. A custom implementation (a test double, say) must implement all of them |
| `StreamableHttpAcpAgentTransportOptions` | Gains `shutdownTimeout` (builder `shutdownTimeout(Duration)`, default 5 seconds): how long closing the servlet or listener waits for connected agents before closing the rest at once. Breaking only for code calling the record's canonical constructor directly; the builder is unaffected |
| `CommandResult` | Canonical constructor is now `(String output, @Nullable Integer exitCode, @Nullable String signal, boolean truncated)`; the old 3-argument form (`output`, `exitCode`, `signal`) still exists as a convenience constructor meaning complete (non-truncated) output. No `timedOut` flag; a signal-killed command has no exit code |
| `Command.env()` | Never `null`; empty when no variables are set. Migration: test `.isEmpty()` instead of `== null` |
| `AcpInvocationContext`, `AcpMethodParameter` | Moved to `com.agentclientprotocol.sdk.agent.support.invocation`: update imports in custom `ArgumentResolver`, `ReturnValueHandler`, and `AcpInterceptor` implementations |
| Unstable providers API | `ProviderInfo`, `SetProviderRequest`, `DisableProviderRequest` rename `id()` to `providerId()`, matching the unstable schema's actual wire property. `session/fork` and `providers/*` are now consistently marked `@UnstableAcpApi` everywhere they appear |
| Jackson floor | Each JSON module now checks its Jackson version at startup and fails with `IllegalStateException` if it's below the floor (`acp-json-jackson2`: Jackson 2.18.1; `acp-json-jackson3`: Jackson 3.0.0), naming the version found and required. Quarkus 3.40's and Spring Boot 4.1's managed Jacksons are both within the floor; migration is needed only for an older, unmanaged Jackson. See [JSON Mappers](/docs/acp-java-sdk/json-mappers) |
| Every package | Null-marked (JSpecify `@NullMarked`); Java callers compile unchanged, Kotlin and other nullness-aware callers see the new annotations |

**Additive, not breaking, but worth knowing about:**

- `AgentParameters.Builder.inheritEnvironment(boolean)`: a stdio agent's process inherits the whole
  client environment by default (unchanged; now documented as the explicit default rather than an
  accident of the old implementation), and `inheritEnvironment(false)` starts it from an empty
  environment plus only the safe defaults and whatever `addEnvVar(...)` adds, for a client that
  shouldn't hand every secret in its own environment to an agent subprocess.
- Mapper-less transport constructors: `StreamableHttpAcpClientTransport(URI)`,
  `WebSocketAcpClientTransport(URI)`, `StreamableHttpAcpAgentTransport(int port, AcpAgentFactory)`,
  and `StreamableHttpAcpServlet(AcpAgentFactory)` all default to `AcpJsonMapper.createDefault()`, as
  the stdio transports already did.

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
- **A response missing a required field now fails the request instead of silently passing nulls
  through.** A bare `{}` used to read as, say, a `PromptResponse` with a null `stopReason` or a
  `NewSessionResponse` with a null `sessionId`; only inbound params were checked for required fields
  before. Results are checked the same way now, on both sides and down into nested records: the
  caller's request fails with `AcpError` (`-32603`), data `{"reason": "missing-required-field",
  "method": <method>, "field": <path>}`, the path naming a nested field, such as
  `modes.currentModeId`, not just its containing object. See [Errors](/docs/acp-java-sdk/errors) for
  this and the other reasons an `AcpError` can mean the SDK rejected the response itself rather than
  the peer sending an error. Code that tolerated a peer answering less than the schema requires,
  intentionally or not, now sees that as a hard failure.
- **An agent-to-client request reaches its handler only after the session updates sent before it.**
  Requests used to be dispatched as they arrived, outside the ordered notification drain, so a
  `session/request_permission` could reach its handler before the client's session-update consumers
  had processed the `tool_call` update the agent sent just before it, leaving the tool call impossible
  to look up. A request now takes its place in the same drain as a response: dispatched once every
  notification before it has been handled (handlers still run concurrently with each other and with
  later updates; a request already being handled when a response comes in isn't held up behind it, to
  avoid deadlocking a consumer that's waiting on its own request). See
  [Concepts: the ordering guarantee](/docs/acp-java-sdk/concepts#session-updates-and-the-ordering-guarantee),
  now extended to cover this case too.
- **`execute` releases its terminal when the prompt is cancelled.** ACP requires an agent to release
  every terminal it creates. `execute` already released it when the command ended or a step failed,
  but not when the prompt was cancelled (the `session/cancel` grace period, `maxPromptDuration`, or
  `$/cancel_request`) while waiting in `terminal/wait_for_exit`, leaving the client holding a terminal
  the agent would never ask about again. It now sends `terminal/release` exactly once on every path.

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
14. If any annotated agent has `@SetSessionMode`/`@SetSessionConfigOption` without `@NewSession`, add
    one; building now fails without it.
15. If any custom `ReturnValueHandler` composition references `MonoHandler` by name, update it to
    `AsyncValueHandler`.
16. If any custom `PromptContext`/`SyncPromptContext` implementation exists (typically a test
    double), implement the new `isCancelled()`/`onCancel(Runnable)`/`whenCancelled()` methods.
17. If an `@Initialize` method's response was relied on to suppress a capability a handler would
    otherwise imply, remove or conditionally register the handler instead: capabilities now merge by
    OR, so a handler's presence always advertises.
18. Grep for `agent.await()` (rename to `agent.awaitTermination()`) and `awaitForExit()` (rename to
    `awaitProcessExit()`, and catch `CancellationException` instead of `RuntimeException` around it).
19. Grep for `context.sendUpdate(sessionId,` on a `PromptContext`/`SyncPromptContext`, dropping the
    first argument; leave `agent.sendSessionUpdate(sessionId, ...)` alone, it's unaffected.
20. Grep for `catch (RuntimeException` (or `Exceptions.unwrap`) around a blocking SDK call checking
    for a `TimeoutException` cause; replace with `catch (AcpTimeoutException e)`.
21. Grep for `AcpAgent.SYNC_HANDLER_SCHEDULER`, `AcpClient.SYNC_HANDLER_SCHEDULER`, and
    `AcpAgent.DEFAULT_REQUEST_TIMEOUT`; the first two have no replacement constant (use
    `handlerExecutor(...)` if you need a specific executor), the third becomes `Duration.ofSeconds(60)`.
22. If any code relied on a long-running prompt being cut off by the client's request timeout, set
    `.promptTimeout(...)` explicitly; the default is now unbounded.
23. If any code constructs `CommandResult` via its canonical constructor (not the 3-argument
    convenience one), add the new `truncated` component.
24. Grep for `catch (AcpProtocolException` around a client or agent call (not inside a handler, where
    throwing it is still correct): replace with `catch (AcpError e)`.
25. Grep for `client.` calls made before `client.initialize()`: every call but `initialize` itself now
    fails locally with `IllegalStateException` until it has answered.
26. If a client advertises `fs.readTextFile`, `fs.writeTextFile`, `terminal`, or an elicitation mode,
    confirm the matching handler is registered; `build()` now fails without it.
27. Grep for a raw `requestHandler`/`notificationHandler` registered for a method the SDK models
    (`fs/read_text_file`, a `terminal/*` method, `session/request_permission`, `elicitation/create`,
    `session/update`, `elicitation/complete`): switch to the named typed setter.
28. If a `SyncSpec.notificationHandler` is registered, drop the `Mono` from its body; it's now a
    blocking `Consumer<Object>`.
29. If any code relied on the client's 30-second default request timeout specifically (for example, a
    test asserting how long a stub takes to time out), it's now 60 seconds; set `requestTimeout(...)`
    explicitly if the old number matters.
30. If a `SessionConfigSelect.Builder` is ever built with no options, or a `currentValue` not among
    them, fix the options before `build()`; it now throws instead of building.
31. If a test specifically checked `MockAcpClient`'s `initialize()` response for a `terminal`
    capability, update it: the mock no longer advertises `terminal`.
32. Grep for `import com.agentclientprotocol.sdk.spring.boot.autoconfigure.client.AcpClientCustomizer`
    (or the equivalent Micronaut/Quarkus package) and `TransportType`: both now come from
    `com.agentclientprotocol.sdk.integration`.
33. If using Spring Boot, grep for `spring.acp.agent.transport.http.port` and
    `...max-concurrent-streams-per-connection`: both move under `...http.listener.*`.
34. If using Spring Boot, set `spring.acp.client.transport.type`/`spring.acp.agent.transport.type`
    explicitly wherever more than one transport property is set; it now fails at startup instead of
    picking one silently. Quarkus and Micronaut clients need the same check.
35. If a Spring `ArgumentResolver` or `ReturnValueHandler` was registered by hand (not as a `@Bean`),
    register it as one instead; it's now picked up automatically, the same as `AcpInterceptor`.
