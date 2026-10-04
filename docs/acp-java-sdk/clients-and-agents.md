---
title: "Clients and Agents in Java"
sidebarTitle: "Clients & Agents"
description: "Sync vs async facades, and the two ways to build an agent: annotations (the recommended way in) and the builder API"
---

This page is where to start once you know the [Concepts](/docs/acp-java-sdk/concepts) vocabulary and
want to write code. It covers two independent choices: sync or async, and, for an agent only,
annotations or the builder API.

## Building an agent: annotations, the recommended way in

For nearly every agent, write a plain class, annotate it, and let `AcpAgentSupport` wire it up. No
`@Initialize` method is needed: the response is derived from the class, covered below.

```java
@AcpAgent(name = "echo-agent", version = "1.0.0")
class EchoAgent {

    @NewSession
    NewSessionResponse newSession() {
        return new NewSessionResponse(UUID.randomUUID().toString(), null, null);
    }

    @Prompt
    String prompt(PromptRequest req) {
        return "Echo: " + req.text();
    }
}

AcpAgentSupport.create(new EchoAgent())
    .transport(new StdioAcpAgentTransport())
    .run();
```

One annotation per ACP method (`@Initialize`, `@NewSession`, `@Prompt`, `@Cancel`, `@Authenticate`,
`@Logout`, `@SetSessionConfigOption`, `@ExtRequest`/`@ExtNotification` for your own methods, and
more), discovered once when `AcpAgentSupport` builds, on the class and its superclasses, so a
framework-generated proxy (Spring CGLIB, Quarkus ArC, Micronaut AOP) is found through the annotated
class it extends and invoked on the proxy itself, so its interceptors still run. A handler method
takes its request type (optional), `@SessionId String`, and, in any handler, the connection's
`NegotiatedCapabilities` and `AcpSyncAgent`/`AcpAsyncAgent`; a `@Prompt` method additionally takes
`SyncPromptContext` (or the async `PromptContext`, reachable from a sync one via `ctx.async()`).

### Capabilities, `agentInfo`, and auth methods are derived from the class

With no `@Initialize` method, the response the agent sends is derived entirely from what the class
declares:

- Each handler annotation advertises the capability its method needs: `@LoadSession` sets
  `loadSession`; `@ListSessions`/`@CloseSession`/`@ResumeSession`/`@DeleteSession`/`@ForkSession` each
  set their `sessionCapabilities` flag; `@Logout` sets `auth.logout`. `@NewSession`, `@Prompt`, and
  `@Cancel` advertise nothing; ACP requires every agent to support them. `@SetSessionMode` and
  `@SetSessionConfigOption` advertise nothing at the `initialize` level either: what they offer is
  per-session, in the modes or config options a `session/new`/`load`/`resume` response carries.
- `@Prompt(image, audio, embeddedContext)` declares the prompt content the agent accepts, advertised
  as `promptCapabilities`.
- `@AcpAgent(mcpHttp, mcpSse)` declares which MCP transports the agent connects to.
- `@AcpAgent(name, version, title)` becomes `agentInfo`: an empty `name` sends the class's simple
  name; an empty `version` sends the jar manifest's `Implementation-Version`, or `"unknown"` with
  neither; an empty `title` sends none.
- `@AcpAgent(authMethods = @AuthMethod(...))` becomes `authMethods`. A terminal method is advertised
  only to a client that announced `clientCapabilities.auth.terminal`; an agent-type method requires an
  `@Authenticate` handler to serve it, checked when the agent is built.

```java
@AcpAgent(name = "notes-agent", version = "1.0.0",
    authMethods = @AuthMethod(id = "api-key", name = "API key")) // type AGENT is the default
class NotesAgent {

    @Authenticate
    AuthenticateResponse authenticate(AuthenticateRequest req) { /* ... */ }

    @LoadSession
    LoadSessionResponse loadSession(LoadSessionRequest req) { /* ... */ } // implies loadSession: true

    @Logout
    LogoutResponse logout(LogoutRequest req) { /* ... */ } // implies auth.logout: true

    @Prompt(image = true)
    String prompt(PromptRequest req) { /* ... */ } // implies promptCapabilities.image: true
}
```

### Adding `@Initialize`: it overlays the derived response, it doesn't replace it

An `@Initialize` method's return value is layered **over** the derived one, not instead of it: a
capability is advertised if *either* side advertises it (so a handler's implied capability can never
be silently withdrawn by returning a response that omits it); returned auth methods are appended to
the derived ones, replacing any with the same id; a returned `agentInfo`, protocol version, or
`_meta` wins over the derived value when it's non-null. In short, `@Initialize` is for adding to or
overriding specific fields, not for restating the whole response.

### Return values

A request handler returns its response type, or a `Mono`, `CompletionStage`, or single-value
`Publisher` of it (the runtime waits for it on the handler's thread); a `null` or empty result
answers `-32603` (internal error), since a request always needs one. Only `@Prompt` may be `void`
(the same as `PromptResponse.endTurn()`); a `@Prompt` method may also return (or asynchronously
produce) a `String`, sent to the client as an agent message chunk before the turn ends the same way
(`null` or empty sends nothing): the simple form the example above uses. A notification handler
(`@Cancel`) returns `void`.

### Cancellation

`SyncPromptContext.isCancelled()` (poll it between steps) or `onCancel(Runnable)` (register a
callback, for work you can't poll, like a subprocess); the async `PromptContext.whenCancelled()`
composes into a Reactor pipeline. See [Cancellation](/docs/acp-java-sdk/cancellation) for the full
annotation-model lifecycle.

### Typed config values

A `@SetSessionConfigOption` method may take `@ConfigId String` and `@ConfigValue` (typed `String`,
`boolean`/`Boolean`, or `Object` for either kind); a value of the wrong kind for the parameter's type
answers `-32602` without calling the method. See
[Session Config Options](/docs/acp-java-sdk/config-options) for the full shape.

### When something's wrong

Registration errors are caught when the agent is built, each naming the class, the method, and the
fix: two handler methods for one annotation (or two annotations on one method), a parameter no
resolver can supply, `@SessionId`/`@ConfigId`/`@ConfigValue` on a method that doesn't have one, a
request handler declared `void` (or returning the wrong type), and `@SetSessionMode`/
`@SetSessionConfigOption` present without a `@NewSession` method to offer what they set. Every agent
needs a `@Prompt` method; building one without it fails the same way. There's no session-state or
exception-handler annotation: keep per-session state in a thread-safe map keyed by session id,
dropped in `@CloseSession`/`@DeleteSession`, and handle errors in the method itself or an
`AcpInterceptor.onError`.

For serving many remote connections (Streamable HTTP, WebSocket) from one annotated agent,
`AcpAgentSupport.Builder#buildFactory()` returns an `AcpAgentFactory` instead of running one agent
directly: every connection gets its own runtime, all dispatching to this one bean, which is why the
bean itself must be thread-safe. It refuses a builder that also has `transport(...)` set, since a
listener supplies its own transport per connection. See [Transports](/docs/acp-java-sdk/transports).

## Building an agent: the builder API

The lower-level option, for cases the annotation model doesn't fit: dynamic handler registration,
building an agent without a dedicated class, or needing a fresh agent instance (not a shared bean)
per connection.

```java
AcpSyncAgent agent = AcpAgent.sync(new StdioAcpAgentTransport())
    .agentInfo(new Implementation("echo-agent", "1.0.0"))
    .newSessionHandler(req -> new NewSessionResponse(UUID.randomUUID().toString(), null, null))
    .promptHandler((req, ctx) -> {
        ctx.sendMessage("Echo: " + req.text());
        return PromptResponse.endTurn();
    })
    .build();

agent.run();
```

The same shape as the annotated version, one `xxxHandler(...)` setter per ACP method instead of one
annotated method. Builder agents get a default `initialize` too, so `initializeHandler(...)` is
optional: it derives the same capabilities from which handlers are *registered* (no
`promptCapabilities` or `mcpCapabilities`, which need annotation attributes the plain builder has no
equivalent for), and `agentInfo(Implementation)` sets `agentInfo` on it without writing a handler.
(`AcpAgentSupport.Builder#run()`, the annotated builder's one-call `build().run()` convenience,
has no equivalent on this plain builder: call `.build()` then `.run()` on the result, as above.) A
builder handler other than the prompt handler receives only its request; to call back into the
client (or read `NegotiatedCapabilities`) from one of those handlers, reach the built agent through a
reference captured after `build()`, rather than a parameter:

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

A builder setter now rejects a `null` handler (`IllegalArgumentException`) and a second registration
for the same method (`IllegalStateException`, naming the setter: "A handler for session/prompt is
already registered; promptHandler was called twice on this builder"), instead of silently replacing
the first one. Register each handler once; decide which implementation to use before calling the
setter, not after.

`AcpSyncAgent` and `AcpAgentSupport` implement `AutoCloseable`, with the same close semantics as
`AcpSyncClient`: close gracefully, waiting up to 10 seconds, then close at once if that failed or took
too long. Use try-with-resources on either, the same pattern as the client below. `AcpSyncAgent.await()`
is renamed `awaitTermination()`, matching `AcpAsyncAgent`.

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
closes it from the owning context's lifecycle instead. `client.async()` returns the `AcpAsyncClient`
it blocks on, for composing one asynchronous call without switching the whole client over to the
async facade.

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
