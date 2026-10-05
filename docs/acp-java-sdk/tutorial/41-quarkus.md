# Module 41: Quarkus

Serve an annotated ACP agent with the Quarkus extension: `@AcpAgent` alone makes the class a CDI bean, served over Streamable HTTP and WebSocket on Quarkus's own HTTP server, with Mutiny `Uni`/`Multi` return types and a cancellable stream.

## What You'll Learn

- `@AcpAgent` alone, with no bean-scope annotation needed: build-time CDI discovery, one agent only
- `@NewSession` returning a `Uni`, and `@Prompt` streaming a `Multi`
- `session/cancel` cancelling a `Multi`'s subscription, and detecting it with `onCancellation()`
- A CDI interceptor binding (`@InterceptorBinding`/`@AroundInvoke`) around a prompt handler
- Why `quarkus dev` can't run this module's stdio default, and what to use instead

## The Code

### The agent bean

```java
@AcpAgent(name = "quarkus-streaming-agent", version = "1.0.0", title = "Quarkus Streaming Agent")
public class StreamingAgent {

    private static final int CHUNKS = 10;
    private final Greeting greeting;
    private final Map<String, String> lastStream = new ConcurrentHashMap<>();

    StreamingAgent(Greeting greeting) {
        this.greeting = greeting;
    }

    @NewSession
    public Uni<NewSessionResponse> newSession(NewSessionRequest req) {
        return Uni.createFrom().item(() -> new NewSessionResponse(UUID.randomUUID().toString(), null, null));
    }

    @Prompt(image = true)
    @Audited
    public Multi<String> prompt(PromptRequest req, SyncPromptContext ctx) {
        String sessionId = ctx.getSessionId();
        if (req.text().startsWith("count")) {
            AtomicInteger sent = new AtomicInteger();
            return Multi.createFrom().ticks().every(Duration.ofMillis(300))
                    .select().first(CHUNKS)
                    .map(tick -> "chunk " + sent.incrementAndGet())
                    .onCancellation().invoke(() -> lastStream.put(sessionId,
                            "your last stream was cancelled after " + sent.get() + " of " + CHUNKS + " chunks"));
        }
        if (req.text().startsWith("status")) {
            return Multi.createFrom().item(lastStream.getOrDefault(sessionId, "no stream was cancelled"));
        }
        return Multi.createFrom().item(greeting.greet(req.text()));
    }

    @CloseSession
    public CloseSessionResponse closeSession(CloseSessionRequest req) {
        lastStream.remove(req.sessionId());
        return new CloseSessionResponse();
    }
}
```

`@AcpAgent` alone makes this a CDI bean: a singleton, found at build time (a second `@AcpAgent` class
fails the build), into which other beans (`Greeting`) inject normally. No `@Singleton` or
`@ApplicationScoped` needed. No `@Initialize` method either: the SDK derives `agentInfo` from
`@AcpAgent(name, version, title)`, `sessionCapabilities.close` from `@CloseSession`, and
`promptCapabilities.image` from `@Prompt(image = true)`. See
[Clients and Agents in Java](/docs/acp-java-sdk/clients-and-agents) for the full derivation rules.

### Streaming with `Multi`, and cancelling it

`@Prompt` returns a `Multi<String>`: each item is sent as an agent message chunk as it's emitted, and
the turn ends `end_turn` when the stream completes. When the client sends `session/cancel`, the SDK
cancels the `Multi`'s subscription and ends the turn `cancelled`; the stream sees this through
`onCancellation()`, with no `@Cancel` handler needed on the agent's side at all:

```java
return Multi.createFrom().ticks().every(Duration.ofMillis(300))
        .select().first(CHUNKS)
        .map(tick -> "chunk " + sent.incrementAndGet())
        .onCancellation().invoke(() -> lastStream.put(sessionId,
                "your last stream was cancelled after " + sent.get() + " of " + CHUNKS + " chunks"));
```

```java
// Client: cancel after the third chunk arrives
client.cancel(new CancelNotification(sessionId, null));
```

`@NewSession` returning a plain `Uni<NewSessionResponse>` follows the same rule as any other async
return: the runtime waits for its item on the handler's thread, the same as a `Mono`.

### The CDI interceptor binding

```java
@Audited
@Interceptor
@Priority(Interceptor.Priority.APPLICATION)
public class AuditInterceptor {

    private final AtomicInteger calls = new AtomicInteger();

    @AroundInvoke
    Object audit(InvocationContext invocation) throws Exception {
        int call = calls.incrementAndGet();
        for (Object argument : invocation.getParameters()) {
            if (argument instanceof SyncPromptContext prompt) {
                prompt.sendThought("[audit] " + invocation.getMethod().getName() + " call #" + call
                        + ", intercepted by a CDI interceptor");
            }
        }
        return invocation.proceed();
    }
}
```

`@Audited` is a plain CDI `@InterceptorBinding`, nothing ACP-specific. Binding it to the prompt
handler makes Quarkus's ArC generate a subclass of the agent bean at build time. The SDK finds the
handlers through the `@AcpAgent` class that subclass extends, and invokes them on the bean ArC hands
it, so the interceptor runs around the handler, the same discovery pattern
[Micronaut](/docs/acp-java-sdk/tutorial/40-micronaut) uses for its own `@Around` advice.

### Reading the derived `initialize` answer

```java
var init = client.initialize();
System.out.println(AcpJsonMapper.createDefault().writeValueAsString(init));
System.out.println("agentInfo (from @AcpAgent): " + init.agentInfo().name() + " " + init.agentInfo().version());
System.out.println("sessionCapabilities.close (from @CloseSession): "
        + (init.agentCapabilities().sessionCapabilities().close() != null));
System.out.println("promptCapabilities.image (from @Prompt(image = true)): "
        + init.agentCapabilities().promptCapabilities().image());
```

### Serving HTTP on Quarkus's own server

```properties
quarkus.acp.agent.transport.type=http

# An ACP WebSocket is a long-lived session, so ACP has its own idle timeout, separate from HTTP keep-alive tuning; the initialize deadline closes connections that never start. These are the defaults.
quarkus.acp.agent.transport.http.web-socket-idle-timeout=30m
quarkus.acp.agent.transport.http.initialize-timeout=30s
```

A Streamable HTTP client and a WebSocket client both connect to the same `/acp` path on
`quarkus.http.port`, the Quarkus application's own server, not a separate SDK listener. The path sits
under `quarkus.http.root-path` (`/` by default) and is served by one Vert.x route (the extension
depends on `quarkus-vertx-http`, not Undertow); no servlet container, no second server. The CDI
interceptor's call count keeps climbing across both connections: one bean serves every connection
Quarkus accepts.

<Warning>
**`quarkus dev` can't run a stdio agent.** Dev mode owns the terminal's standard input for its own
interactive commands, so this module's demo packages the application
(`quarkus-run.jar`) and runs it as a real process over HTTP instead of using `quarkus dev`, the shape
an editor actually launches in production. Develop a stdio agent in tests, or over HTTP as here.
</Warning>

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-41-quarkus)

## Running the Example

```bash
./mvnw package -pl module-41-quarkus -q
./mvnw exec:java -pl module-41-quarkus

# The Quarkus application on its own, on port 8080:
java -jar module-41-quarkus/target/quarkus-app/quarkus-run.jar
```

The demo packages and starts the Quarkus application as a separate process on a free port, connects a
Streamable HTTP client that prints the derived `initialize` answer, starts a `count to ten` stream,
cancels it after the third chunk (stop reason `cancelled`), asks what happened, then connects a
WebSocket client to the same server and path for one more prompt. No API key required.

## Back to the Overview

[Tutorial Overview](/docs/acp-java-sdk/tutorial/index): all modules and the recommended paths through them.
