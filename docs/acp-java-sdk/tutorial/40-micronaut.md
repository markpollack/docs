# Module 40: Micronaut

Make an annotated ACP agent a Micronaut bean with `com.agentclientprotocol:acp-micronaut`: the same application runs as a stdio agent and over Streamable HTTP and WebSocket, with no `@Initialize` method, a Micronaut `@Around` interceptor, and a `Publisher` return.

## What You'll Learn

- `@Singleton` plus `@AcpAgent`: compile-time bean discovery, no classpath scan, exactly one agent
- Reading the `initialize` answer a client receives, and matching each field back to the annotation that produced it
- Configuring the agent (`acp.agent.*`) and a client (`acp.client.*`) from the same module
- A Micronaut `@Around` interceptor running around a prompt handler through the SDK's discovery
- Returning a Reactive Streams `Publisher` instead of a plain value

## The Code

### The agent bean

```java
@Singleton
@AcpAgent(name = "micronaut-greeting-agent", version = "1.0.0", title = "Micronaut Greeting Agent")
public class GreetingAgent {

    private final Greeter greeter;
    private final Map<String, String> sessions = new ConcurrentHashMap<>();

    public GreetingAgent(Greeter greeter) {
        this.greeter = greeter;
    }

    @NewSession
    public Publisher<NewSessionResponse> newSession(NewSessionRequest req) {
        String sessionId = UUID.randomUUID().toString();
        sessions.put(sessionId, req.cwd());
        return Mono.just(new NewSessionResponse(sessionId, null, null));
    }

    @Prompt(embeddedContext = true)
    @Audited
    public Publisher<String> prompt(PromptRequest req, SyncPromptContext ctx) {
        return Mono.just(greeter.greet(req.text()));
    }

    @ListSessions
    public ListSessionsResponse listSessions(ListSessionsRequest req) {
        var infos = sessions.entrySet().stream()
                .map(e -> new SessionInfo(e.getKey(), e.getValue()))
                .toList();
        return new ListSessionsResponse(infos);
    }

    @CloseSession
    public CloseSessionResponse closeSession(CloseSessionRequest req) {
        sessions.remove(req.sessionId());
        return new CloseSessionResponse();
    }
}
```

Two annotations make this an agent bean: `@Singleton` makes it a bean at all, so `Greeter` injects
into its constructor like into any other bean; `@AcpAgent` makes it *the* agent. Micronaut finds it
from the bean definition its annotation processor wrote at compile time, with no classpath scan, and
exactly one such bean is allowed (startup names them all if there's more than one).

### No `@Initialize` method

Nothing here answers `initialize` directly. The SDK derives it from the class:

- `agentInfo` from `@AcpAgent(name, version, title)`.
- `sessionCapabilities.list` from `@ListSessions`, `sessionCapabilities.close` from `@CloseSession`.
- `promptCapabilities.embeddedContext` from `@Prompt(embeddedContext = true)`.
- No `loadSession` (there's no `@LoadSession` method).

The demo prints the exact `initialize` answer a client receives, field by field, matched back to the
annotation that produced it:

```java
var init = acp.initialize();
System.out.println(AcpJsonMapper.createDefault().writeValueAsString(init));
System.out.println("agentInfo (from @AcpAgent): " + init.agentInfo().name() + " " + init.agentInfo().version());
System.out.println("sessionCapabilities.list (from @ListSessions): "
        + (init.agentCapabilities().sessionCapabilities().list() != null));
System.out.println("promptCapabilities.embeddedContext (from @Prompt(embeddedContext = true)): "
        + init.agentCapabilities().promptCapabilities().embeddedContext());
```

See [Clients and Agents in Java](/docs/acp-java-sdk/clients-and-agents) for the full derivation rules
this applies.

### The `@Around` interceptor

```java
@Singleton
@InterceptorBean(Audited.class)
public class AuditInterceptor implements MethodInterceptor<Object, Object> {

    private final AtomicInteger calls = new AtomicInteger();

    @Override
    public Object intercept(MethodInvocationContext<Object, Object> context) {
        int call = calls.incrementAndGet();
        for (Object argument : context.getParameterValues()) {
            if (argument instanceof SyncPromptContext prompt) {
                prompt.sendThought("[audit] " + context.getMethodName() + " call #" + call
                        + ", intercepted by a Micronaut @Around interceptor");
            }
        }
        return context.proceed();
    }
}
```

`@Audited` (a plain `@Around`-advised annotation, nothing ACP-specific) applies this interceptor to
the prompt handler. Applying advice makes Micronaut generate a subclass of the agent class at compile
time, an "intercepted" bean carrying no `@AcpAgent` annotation of its own. The SDK finds the handlers
through the class the subclass *extends*, and invokes them on the generated subclass, so the
interceptor actually runs. No special ACP-side wiring is needed beyond the ordinary Micronaut AOP
annotations; the SDK's own `AcpInterceptor` beans remain the ACP-aware alternative, applied to every
handler regardless of which method it serves.

### Return types: `Mono`, `Flux`, `CompletionStage`, or any `Publisher`

Both handlers above return `Publisher<T>` rather than `T` directly or a bare `Mono<T>`: any
single-value Reactive Streams `Publisher` works, not only `Mono`, which lets handler code use
whichever reactive type a Micronaut data or HTTP client call already hands back. Its first element
becomes the response.

<Warning>
If you build the `Publisher` with Micronaut's own `Publishers` helper rather than Reactor or Mutiny
directly, add `micronaut-core-reactive` to the classpath; `acp-micronaut` alone doesn't pull it in.
Returning a `Mono`/`Flux` built directly needs nothing extra.
</Warning>

### A client, and sharing the classpath with the agent

```properties
# The agent: stdio by default.
acp.agent.transport.type=stdio
```

```java
// A client application launches the packaged agent as a subprocess
try (ApplicationContext client = context(Map.of(
        "acp.agent.enabled", false,
        "acp.client.transport.stdio.command", java,
        "acp.client.transport.stdio.args", List.of("-jar", jar)))) {
    AcpSyncClient acp = client.getBean(AcpSyncClient.class);
    var init = acp.initialize();
    // ...
}
```

Each client application in this module sets `acp.agent.enabled=false`, since it shares this module's
classpath (and so the agent's own bean definition) with the agent application; in production they're
separate applications entirely. `acp.client.transport.http.uri` and `.websocket.uri` build the other
two transports the same way, against `acp.agent.transport.type=http`'s listener. Customize the
autoconfigured client with an `AcpClientCustomizer` bean, guarded by
`@Requires(property = "acp.client.transport")` so it's absent from the agent-only application:

```java
@Singleton
@Requires(property = "acp.client.transport")
public class PrintingCustomizer implements AcpClientCustomizer {

    public void customize(AcpClient.AsyncSpec spec) {
        spec.sessionUpdateHandler(notification -> {
            // ...
            return Mono.empty();
        });
    }
}
```

`AcpClientCustomizer` is `com.agentclientprotocol.sdk.integration.AcpClientCustomizer`, the
framework-neutral type Spring Boot and Quarkus customizers implement too, not a Micronaut-specific
interface.

### Over HTTP: one bean, many connections

As of the listener-key rename, the port (and host) live under `acp.agent.transport.http.listener.*`,
matching Spring Boot: the listener binds `127.0.0.1` by default unless
`acp.agent.transport.http.listener.host` says otherwise. An ACP WebSocket is a long-lived session, so
ACP has its own idle timeout, separate from HTTP keep-alive tuning; the initialize deadline closes
connections that never start. This module sets both explicitly, at their defaults:

```properties
acp.agent.transport.http.web-socket-idle-timeout=30m
acp.agent.transport.http.initialize-timeout=30s
```

```java
try (ApplicationContext agent = context(Map.of(
        "acp.agent.transport.type", "http",
        "acp.agent.transport.http.listener.port", 0))) {
    int port = agent.getBean(AcpAgentRuntime.class).port().orElseThrow();
    // ...
}
```

Port `0` picks a free port; `AcpAgentRuntime.port()` reads back what was actually bound. A
Streamable HTTP client and a WebSocket client, each its own application context, connect to the same
listener; the `@Around` interceptor's call count keeps climbing across both connections, since one
agent bean serves every connection the listener accepts.

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-40-micronaut)

## Running the Example

```bash
./mvnw package -pl module-40-micronaut -q
./mvnw exec:java -pl module-40-micronaut

# The agent application on its own, over stdio or on port 8080:
java -jar module-40-micronaut/target/micronaut-agent.jar
java -jar module-40-micronaut/target/micronaut-agent.jar --acp.agent.transport.type=http
```

The demo runs the agent two ways: a stdio client launches the packaged agent as a subprocess, prints
the derived `initialize` answer, prompts it (through the interceptor), lists sessions, then closes
one; then the same application serves HTTP and WebSocket on one listener, with a client on each
transport talking to the same agent bean. No API key required.

## Next Module

[Module 41: Quarkus](/docs/acp-java-sdk/tutorial/41-quarkus): the same shape, on the Quarkus extension, with Mutiny `Uni`/`Multi` and a cancellable stream.
