# Module 37: Streamable HTTP and WebSocket

Serve an agent over the network instead of stdio, with one agent runtime per connection, and connect to it with both Streamable HTTP and WebSocket at once.

See [Transports](/docs/acp-java-sdk/transports) for the identity and routing tables this module builds on, and the RFD [Streamable HTTP and WebSocket Transport](https://agentclientprotocol.com/rfds/streamable-http-websocket-transport) for the wire rules.

## What You'll Learn

- Why a network listener takes an `AcpAgentFactory`, not an agent, and what that means for state
- Starting `StreamableHttpAcpAgentTransport` on port `0` and reading the bound port with `getPort()`
- Connecting with `StreamableHttpAcpClientTransport` and `WebSocketAcpClientTransport` to the same listener
- Plain `http://` negotiating HTTP/2 (h2c) automatically
- `AcpAgentSupport.Builder#buildFactory()` for an annotated agent behind a listener, and why the bean must be thread-safe
- The built-in listener's limits in 0.80.0: no TLS, no WebSocket inside a servlet container

## The Code

### One factory, many agents

Over stdio, one process is one connection is one agent. A network listener accepts many connections, so it takes a factory that builds a fresh agent for every one, bound to that connection's own transport:

```java
static AcpAgentFactory factory() {
    return AcpAgentFactory.sync(transport -> {
        int connection = CONNECTIONS.incrementAndGet();
        return AcpAgent.sync(transport)
                .initializeHandler(req -> AcpSchema.InitializeResponse.ok())
                .newSessionHandler(req -> new AcpSchema.NewSessionResponse(UUID.randomUUID().toString(), null, null))
                .promptHandler((req, ctx) -> {
                    ctx.sendMessage("agent for connection #" + connection + " echoes: " + req.text());
                    return AcpSchema.PromptResponse.endTurn();
                })
                .build();
    });
}
```

Each connection's lambda invocation closes over its own `connection` number, so every agent instance remembers which connection it belongs to: this is what lets the demo show that two concurrent clients get two different agents.

### Starting the listener

```java
var server = new StreamableHttpAcpAgentTransport(0, AcpJsonMapper.createDefault(), factory());
server.start().block();
int port = server.getPort();  // port 0 picked a free one
System.out.println("ACP agent listening on http://localhost:" + port + "/acp");
```

`StreamableHttpAcpAgentTransport` (module `acp-streamable-http-jetty`) runs an embedded Jetty listener on `/acp` that speaks Streamable HTTP (POST requests, SSE responses: one stream for the connection, one per ACP session, routed by the `Acp-Connection-Id` and `Acp-Session-Id` headers), HTTP/2 over plain `http://` (h2c), and a WebSocket upgrade on the same path. The listener itself is not an `AcpAgentTransport`; each connection gets its own, created inside the SDK.

### Connecting with both transports at once

```java
AcpSyncClient httpClient = AcpClient.sync(new StreamableHttpAcpClientTransport(
        URI.create("http://localhost:" + port + "/acp"), AcpJsonMapper.createDefault()))
        .build();

AcpSyncClient wsClient = AcpClient.sync(new WebSocketAcpClientTransport(
        URI.create("ws://localhost:" + port + "/acp"), AcpJsonMapper.createDefault()))
        .build();
```

Client code is otherwise unchanged from stdio: `AcpClient.sync(transport)`, `initialize()`, `newSession(...)`, `prompt(...)` all work exactly the same regardless of transport. Each connection gets its own agent from the factory, so the HTTP client and the WebSocket client see different connection numbers in their answers, but opening a second ACP session on the *same* HTTP connection is still served by the same agent instance.

### Checking the HTTP/2 upgrade

```java
HttpClient http = HttpClient.newBuilder().version(HttpClient.Version.HTTP_2).build();
HttpResponse<Void> response = http.send(
        HttpRequest.newBuilder(URI.create("http://localhost:" + port + "/acp")).GET().build(),
        HttpResponse.BodyHandlers.discarding());
response.version(); // HTTP_2, since the server speaks h2c
```

The Streamable HTTP client sends this same bodiless GET first, so later requests reuse an already-upgraded HTTP/2 connection over plain `http://`. A server that doesn't upgrade just makes the client pin HTTP/1.1; both work.

### An annotated agent behind a listener

```java
AcpAgentFactory factory = AcpAgentSupport.create(new AnnotatedHttpAgent()).buildFactory();
var server = new StreamableHttpAcpAgentTransport(0, AcpJsonMapper.createDefault(), factory);
```

`buildFactory()` returns an `AcpAgentFactory`: every connection gets its own agent runtime, but they all dispatch to **this one bean**. State on the bean itself (an `AtomicInteger` counting prompts across every connection, in this module) must be thread-safe; per-session state belongs in a concurrent map keyed by session id instead, as in [Module 33](/docs/acp-java-sdk/tutorial/33-session-config-options).

### Closing

```java
server.closeGracefully().block(Duration.ofSeconds(10)); // waits up to shutdownTimeout (5s default)
```

<Note>
**Limits of the built-in listener in 0.80.0**: a plain connector only (terminate TLS in front of it, or mount `StreamableHttpAcpServlet` in your own container instead, which serves HTTP/SSE but not the WebSocket upgrade). [Module 38](/docs/acp-java-sdk/tutorial/38-spring-boot-http) shows the Spring Boot setup for both the standalone listener and the servlet case.
</Note>

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-37-streamable-http-websocket)

## Running the Example

```bash
./mvnw compile -pl module-37-streamable-http-websocket -q
./mvnw exec:java -pl module-37-streamable-http-websocket

# The listener on its own, on port 8080:
./mvnw exec:java -pl module-37-streamable-http-websocket \
    -Dexec.mainClass=com.acptutorial.module37.HttpAgent -Dexec.args=8080
```

The demo starts a listener on a free port, probes the HTTP/2 upgrade, connects a Streamable HTTP client and a WebSocket client concurrently (two sessions on the HTTP connection, one on the WebSocket connection), confirms they got different agents, then starts a second listener for an annotated agent built with `buildFactory()`. No API key required.

## Next Module

[Module 38: Spring Boot over HTTP](/docs/acp-java-sdk/tutorial/38-spring-boot-http): the same transport, wired through acp-autoconfig's properties instead of by hand.
