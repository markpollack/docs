# Module 24: Spring Boot Client

Use the autoconfigured ACP client in a Spring Boot application. Connect to agents with just properties — no manual transport or client construction.

## Prerequisites

- Java 21+ (Spring Boot 4.x requirement)
- [Module 23: Spring Boot Agent](/docs/acp-java-sdk/tutorial/23-spring-boot-agent) built and available

## What You'll Learn

- Injecting `AcpSyncClient` from autoconfiguration
- Configuring the client transport via `application.properties`
- Property-driven transport selection (stdio vs WebSocket)

## Dependencies

Same starter as the agent side:

```xml
<dependency>
    <groupId>com.agentclientprotocol</groupId>
    <artifactId>acp-spring-boot-starter</artifactId>
    <version>0.80.0</version>
</dependency>
```

<Note>
As of 0.80.0, the starter is a module of the ACP Java SDK itself (`com.agentclientprotocol`, replacing
`org.springaicommunity`); see the [0.80.0 migration guide](/docs/acp-java-sdk/migration-0.80). The
downloadable module builds against the released starter (SDK 0.18.0) by default; build with
`-Psdk-candidate` to use the SDK's own starter at the coordinates shown above.
</Note>

## The Client

The autoconfigured `AcpSyncClient` is injected like any Spring bean:

```java
@SpringBootApplication
public class ClientApplication {

    public static void main(String[] args) {
        SpringApplication.run(ClientApplication.class, args);
    }

    @Bean
    CommandLineRunner demo(AcpSyncClient client) {
        return args -> {
            // Initialize the connection
            client.initialize();

            // Create a session
            String cwd = System.getProperty("user.dir");
            var session = client.newSession(new NewSessionRequest(cwd, List.of()));

            // Send a prompt
            var response = client.prompt(new PromptRequest(
                session.sessionId(),
                List.of(new TextContent("Hello from Spring Boot client!"))));

            System.out.println("Stop reason: " + response.stopReason());
        };
    }
}
```

## Configuration

**application.properties:**
```properties
# Connect to the module-23 agent via stdio transport
spring.acp.client.transport.stdio.command=java
spring.acp.client.transport.stdio.args=-jar,module-23-spring-boot-agent/target/module-23-spring-boot-agent-1.0.0-SNAPSHOT.jar

# Increase timeout for Spring Boot agent startup
spring.acp.client.request-timeout=60s
```

The autoconfiguration detects the `stdio.command` property and creates a `StdioAcpClientTransport` that launches the agent as a subprocess.

The explicit `request-timeout=60s` above now just restates the default (it used to raise it from 30s); it's harmless to leave in, and makes the intent explicit regardless of what the default happens to be.

## What the Autoconfiguration Does

1. **Detects transport properties**: `stdio.command` triggers stdio transport; `websocket.uri` triggers WebSocket; `http.uri` triggers Streamable HTTP
2. **Creates `AcpSyncClient` and `AcpAsyncClient`**: configured with timeout and client capabilities
3. **Manages shutdown**: the client, transport, and agent beans are closed once by the autoconfiguration's own lifecycle, not left to Spring's inferred `close()`

## Transport Selection

The autoconfiguration picks the transport based on which properties are set:

| Properties Set | Transport Created |
|---------------|------------------|
| `spring.acp.client.transport.stdio.command` | `StdioAcpClientTransport` |
| `spring.acp.client.transport.websocket.uri` | `WebSocketAcpClientTransport` |
| `spring.acp.client.transport.http.uri` | `StreamableHttpAcpClientTransport` |
| `spring.acp.client.transport.type=stdio` | Explicit stdio selection |
| `spring.acp.client.transport.type=websocket` | Explicit WebSocket selection |
| `spring.acp.client.transport.type=http` | Explicit Streamable HTTP selection (fails at startup, naming the property, if `http.uri` is missing) |

## Build & Run

```bash
# Build both the agent and client
./mvnw package -pl module-23-spring-boot-agent,module-24-spring-boot-client -q

# Run the client (from repo root)
./mvnw spring-boot:run -pl module-24-spring-boot-client
```

## Client Configuration Properties

| Property | Default | Description |
|----------|---------|-------------|
| `spring.acp.client.request-timeout` | `60s` | Request timeout |
| `spring.acp.client.transport.type` | auto-detect | `stdio`, `websocket`, or `http` |
| `spring.acp.client.transport.stdio.command` | — | Command to launch agent |
| `spring.acp.client.transport.stdio.args` | — | Command arguments |
| `spring.acp.client.transport.stdio.env.*` | — | Environment variables |
| `spring.acp.client.transport.websocket.uri` | — | WebSocket URI |
| `spring.acp.client.transport.websocket.connect-timeout` | `10s` | Connection timeout |
| `spring.acp.client.transport.http.uri` | — | Streamable HTTP endpoint of the agent |
| `spring.acp.client.capabilities.read-text-file` | `false` | Advertise file read capability; enable it with a file handler registered through an `AcpClientCustomizer` |
| `spring.acp.client.capabilities.write-text-file` | `false` | Advertise file write capability; enable it with a file handler registered through an `AcpClientCustomizer` |
| `spring.acp.client.capabilities.terminal` | `false` | Advertise terminal capability |

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-24-spring-boot-client)
