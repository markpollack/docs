# Module 38: Spring Boot over HTTP

Serve a Spring Boot `@AcpAgent` over Streamable HTTP with acp-autoconfig, and talk to it from a Spring Boot client whose `AcpClientCustomizer` adds a file handler: property-driven on both sides.

**Requires Java 21+** (Spring Boot 4.x).

## What You'll Learn

- `spring.acp.agent.transport.type=http`: serving an `@AcpAgent` bean remotely, with no code changes to the bean itself
- Why a non-web application runs the SDK's own Jetty listener, and a servlet web application mounts a servlet instead
- `spring.acp.client.transport.http.uri` and `.websocket.uri`, the properties that create a client transport for you, no transport bean required
- `AcpClientCustomizer`, and how registering a handler relates to the capability property that advertises it
- Reading the bound port back from the listener bean when the port is `0`

## The Code

### The agent side: one property changes everything

Compared with a stdio Spring Boot agent (Module 23), only the transport property changes:

```properties
# agent.properties
spring.acp.agent.transport.type=http
spring.acp.agent.transport.http.port=8080
spring.acp.agent.transport.http.path=/acp
```

```xml
<dependency>
    <groupId>com.agentclientprotocol</groupId>
    <artifactId>acp-streamable-http-jetty</artifactId>
</dependency>
```

The `@AcpAgent` bean itself is unchanged:

```java
@Component
@AcpAgent(name = "notes-agent", version = "1.0.0")
public class NotesAgent {

    @NewSession
    AcpSchema.NewSessionResponse newSession(AcpSchema.NewSessionRequest req) {
        return new AcpSchema.NewSessionResponse(UUID.randomUUID().toString(), null, null);
    }

    @Prompt
    AcpSchema.PromptResponse prompt(AcpSchema.PromptRequest req, SyncPromptContext ctx, NegotiatedCapabilities client) {
        if (!client.supportsReadTextFile()) {
            ctx.sendMessage("This client did not advertise fs.readTextFile, so I will not ask for NOTES.md.");
            return AcpSchema.PromptResponse.endTurn();
        }
        String notes = ctx.readFile("NOTES.md");
        long todos = notes.lines().filter(line -> line.startsWith("- [ ]")).count();
        ctx.sendMessage("NOTES.md has " + notes.lines().count() + " lines and " + todos + " open to-dos.");
        return AcpSchema.PromptResponse.endTurn();
    }
}
```

With `transport.type=http`, acp-autoconfig builds an `AcpAgentFactory` from this bean (`AcpAgentSupport...buildFactory()`: one agent runtime per connection, all dispatching to this one bean). Because this particular application has no servlet container on the classpath, it's a non-web application, so the autoconfiguration also runs the SDK's `StreamableHttpAcpAgentTransport` listener bean: Jetty with HTTP/1.1, h2c, and the WebSocket upgrade, on `spring.acp.agent.transport.http.port`. In a servlet web application (`spring-boot-starter-web` present), it mounts `StreamableHttpAcpServlet` on the application's own server instead: HTTP/SSE only, no WebSocket upgrade.

With port `0`, read the bound port back from the listener bean:

```java
int port = context.getBean(StreamableHttpAcpAgentTransport.class).getPort();
```

Without `acp-streamable-http-jetty` on the classpath, `transport.type=http` now fails at startup with a message naming the missing module, rather than leaving the application with no agent and no explanation.

### The client side: a property, not a hand-made transport bean

```properties
# client.properties
spring.acp.client.transport.http.uri=http://localhost:8080/acp

# A handler is registered below, but the capability still needs advertising:
spring.acp.client.capabilities.read-text-file=true
```

Setting `spring.acp.client.transport.http.uri` creates the SDK's `StreamableHttpAcpClientTransport` for you: the same property, auto-detected, or set explicitly with `spring.acp.client.transport.type=http` (which fails at startup, naming the property, if the URI is missing). No transport bean to write by hand.

### `AcpClientCustomizer`: adding to the autoconfigured client

```java
@Bean
AcpClientCustomizer printAndServeFiles() {
    return spec -> spec
            .sessionUpdateConsumer(notification -> {
                if (notification.update() instanceof AcpSchema.AgentMessageChunk msg
                        && msg.content() instanceof AcpSchema.TextContent text) {
                    System.out.println("agent: " + text.text());
                }
                return Mono.empty();
            })
            .readTextFileHandler(req -> {
                String content = WORKSPACE.get(req.path());
                return content != null ? Mono.just(new AcpSchema.ReadTextFileResponse(content))
                        : Mono.error(new IllegalArgumentException("No such file: " + req.path()));
            });
}
```

Every `AcpClientCustomizer` bean is applied, in order, to the one builder behind both `AcpAsyncClient` and `AcpSyncClient`. Consumers add up: the autoconfiguration's own debug-logging consumer stays alongside this one. Registering a handler does **not** advertise it: the client's file capabilities come from `spring.acp.client.capabilities.read-text-file`/`write-text-file`, which default to `false`. A handler and its capability property go together, which is why `client.properties` turns `read-text-file` on next to registering the handler that serves it.

### A WebSocket client, the same way

The listener also accepts a WebSocket upgrade on the same path, and
`spring.acp.client.transport.websocket.uri=ws://host:port/acp` creates a WebSocket client from
properties exactly the same way as the Streamable HTTP property: no code change, just which property
is set. Only a property differs between the two runs; the client application's code is identical
either way:

```java
HttpClientApplication.run("--spring.acp.client.transport.http.uri=" + http);
HttpClientApplication.run("--spring.acp.client.transport.websocket.uri=" + ws);
```

<Note>
Earlier candidates kept the client WebSocket path out of this module: closing a WebSocket client
transport wasn't idempotent, and Spring's lifecycle could close a bean more than once. Both client,
transport, and agent-transport beans are now closed exactly once by the autoconfiguration's own
lifecycle, so the WebSocket run works the same as the Streamable HTTP one.
</Note>

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-38-spring-boot-http)

## Running the Example

```bash
./mvnw compile -pl module-38-spring-boot-http -q
./mvnw exec:java -pl module-38-spring-boot-http

# Or each side on its own: the agent on port 8080, then the client against it
./mvnw exec:java -pl module-38-spring-boot-http \
    -Dexec.mainClass=com.acptutorial.module38.agent.HttpAgentApplication
./mvnw exec:java -pl module-38-spring-boot-http \
    -Dexec.mainClass=com.acptutorial.module38.client.HttpClientApplication \
    -Dexec.args=--spring.acp.client.transport.http.uri=http://localhost:8080/acp
```

The demo starts the agent application on a free port, then runs the client application against it
three times: over Streamable HTTP with the file capability on (the agent reads `NOTES.md` through the
handler), over WebSocket to the same listener and path (the same read, the same answer), then over
Streamable HTTP again with the capability set to `false` on the command line (the handler stays
registered, but the agent never asks, since the capability was never advertised). No API key
required.

## Next Module

[Module 39: Forward Compatibility and _meta](/docs/acp-java-sdk/tutorial/39-forward-compatibility): what happens when the other side of a connection is newer than you.
