---
title: "Clients and Agents in Java"
sidebarTitle: "Clients & Agents"
description: "Sync vs async facades, and the two ways to build an agent: annotations (the recommended way in) and the builder API"
---

This page is where to start once you know the [Concepts](/docs/acp-java-sdk/concepts) vocabulary and
want to write code. It covers two independent choices: sync or async, and, for an agent only,
annotations or the builder API.

## Building an agent: annotations, the recommended way in

For nearly every agent, write a plain class, annotate it, and let `AcpAgentSupport` wire it up:

```java
@AcpAgent(name = "echo-agent", version = "1.0.0")
class EchoAgent {

    @Initialize
    InitializeResponse init() {
        return InitializeResponse.ok();
    }

    @NewSession
    NewSessionResponse newSession() {
        return new NewSessionResponse(UUID.randomUUID().toString(), null, null);
    }

    @Prompt
    PromptResponse prompt(PromptRequest req, SyncPromptContext ctx) {
        ctx.sendMessage("Echo: " + req.text());
        return PromptResponse.endTurn();
    }
}

AcpAgentSupport.create(new EchoAgent())
    .transport(new StdioAcpAgentTransport())
    .build()
    .run();
```

One annotation per ACP method (`@Initialize`, `@NewSession`, `@Prompt`, `@Cancel`, `@Authenticate`,
`@Logout`, `@SetSessionConfigOption`, `@ExtRequest`/`@ExtNotification` for your own methods, and
more), discovered once when `AcpAgentSupport` builds. A handler method takes its request type
(optional), `@SessionId String`, and, in any handler, the connection's `NegotiatedCapabilities` and
`AcpSyncAgent`/`AcpAsyncAgent`; a `@Prompt` method additionally takes `SyncPromptContext` (or the
async `PromptContext`, reachable from a sync one via `ctx.async()`). Returning the response type (or
a `Mono` of it) answers normally; `void` from `@Prompt` answers `endTurn()`.

<Warning>
**Don't return a `String` from `@Prompt` today.** It's meant to send the string as a message and end
the turn, but a current bug routes it through `PromptResponse.text(...)`, which silently drops the
text and sends nothing. A fix is coming with the next SDK candidate. Until then, call
`ctx.sendMessage(...)` explicitly and return `PromptResponse.endTurn()`, as the example above does.
</Warning>

There's no session-state or exception-handler annotation: keep per-session state in a thread-safe map
keyed by session id, dropped in `@CloseSession`/`@DeleteSession`, and handle errors in the method
itself or an `AcpInterceptor.onError`.

For serving many remote connections (Streamable HTTP, WebSocket) from one annotated agent,
`AcpAgentSupport.Builder#buildFactory()` returns an `AcpAgentFactory` instead of running one agent
directly: every connection gets its own runtime, all dispatching to this one bean, which is why the
bean itself must be thread-safe. See [Transports](/docs/acp-java-sdk/transports).

<Warning>
**In flight, not yet landed**: a change due with the next SDK candidate makes the annotation model
derive advertised capabilities from which handlers a class declares, instead of requiring them spelled
out separately. This page will be updated with the exact shape once that lands; don't take the
capability-declaration code above as final for that part.
</Warning>

## Building an agent: the builder API

The lower-level option, for cases the annotation model doesn't fit: dynamic handler registration,
building an agent without a dedicated class, or needing a fresh agent instance (not a shared bean)
per connection.

```java
AcpSyncAgent agent = AcpAgent.sync(new StdioAcpAgentTransport())
    .initializeHandler(req -> InitializeResponse.ok())
    .newSessionHandler(req -> new NewSessionResponse(UUID.randomUUID().toString(), null, null))
    .promptHandler((req, ctx) -> {
        ctx.sendMessage("Echo: " + req.text());
        return PromptResponse.endTurn();
    })
    .build();

agent.run();
```

The same shape as the annotated version, one `xxxHandler(...)` setter per ACP method instead of one
annotated method. A builder handler other than the prompt handler receives only its request; to call
back into the client (or read `NegotiatedCapabilities`) from one of those handlers, reach the built
agent through a reference captured after `build()`, rather than a parameter:

```java
AtomicReference<AcpSyncAgent> self = new AtomicReference<>();
AcpSyncAgent agent = AcpAgent.sync(transport)
    .newSessionHandler(req -> {
        boolean canElicit = self.get().getClientCapabilities().supportsElicitation();
        // ...
    })
    .build();
self.set(agent);
```

`AcpAgentFactory.sync(transport -> AcpAgent.sync(transport)...build())` is the builder-API way to
serve many connections, building a fresh agent instance (not a shared bean) from the lambda each
time; see [Transports](/docs/acp-java-sdk/transports) for when that distinction matters.

## Clients: builder-only

There's no annotation model for clients (handlers you register are mostly one-shot: a file handler,
a permission handler, a session-update consumer), so `AcpClient.sync(transport)`/`AcpClient.async(transport)`
is the only entry point:

```java
AcpSyncClient client = AcpClient.sync(transport)
    .clientCapabilities(ClientCapabilities.builder().fs(new FileSystemCapability(true, true)).build())
    .sessionUpdateConsumer(notification -> { /* ... */ })
    .readTextFileHandler(req -> new ReadTextFileResponse(Files.readString(Path.of(req.path()))))
    .build();

client.initialize();
var session = client.newSession(new NewSessionRequest(cwd, List.of()));
var response = client.prompt(new PromptRequest(session.sessionId(), content));
```

`AcpSyncClient` implements `AutoCloseable`; a try-with-resources block is the usual shape for a
short-lived client (a tutorial module, a CLI run). A long-lived client (a Spring Boot application)
closes it from the owning context's lifecycle instead.

## Sync vs async, on either side

Independent of annotations-vs-builder: pick sync for straightforward blocking code (most agents and
most client code), async (Project Reactor `Mono`) when you're already reactive, need non-blocking
I/O, or are composing several in-flight requests (as in
[graceful cancellation](/docs/acp-java-sdk/cancellation)). `AcpSyncAgent`/`AcpSyncClient` each wrap
an `AcpAsyncAgent`/`AcpAsyncClient` internally; `.async()` on either sync facade reaches the
underlying async one directly, if you need to mix styles in one call.

| Role | Sync | Async |
|---|---|---|
| Agent, annotated | `SyncPromptContext` parameter (default) | `PromptContext`, via `ctx.async()` |
| Agent, builder | `AcpAgent.sync(transport)` | `AcpAgent.async(transport)` |
| Client | `AcpClient.sync(transport)` | `AcpClient.async(transport)` |

## Related

<CardGroup cols={2}>
  <Card title="Concepts" icon="compass" href="/docs/acp-java-sdk/concepts">
    The vocabulary this page assumes: sessions, the prompt turn, capabilities
  </Card>
  <Card title="Transports" icon="server" href="/docs/acp-java-sdk/transports">
    buildFactory() and AcpAgentFactory.sync(...) for serving many connections
  </Card>
</CardGroup>
