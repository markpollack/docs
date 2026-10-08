# Module 23: Spring Boot Agent

Build an ACP agent as a Spring Boot application. No manual transport or lifecycle wiring required.

## Prerequisites

- Java 21+ (Spring Boot 4.x requirement)
- Completed [Module 12: Echo Agent](/docs/acp-java-sdk/tutorial/12-echo-agent)

## What You'll Learn

- Using `@AcpAgent` annotations with Spring Boot autoconfiguration
- How the starter eliminates boilerplate transport and lifecycle code
- Why no `@Initialize` method is needed: the SDK derives it from the class
- Redirecting logging to stderr for stdio agents

## Dependencies

Add the ACP Spring Boot Starter:

```xml
<dependency>
    <groupId>com.agentclientprotocol</groupId>
    <artifactId>acp-spring-boot-starter</artifactId>
    <version>0.80.0</version>
</dependency>
```

As of 0.80.0, the starter is a module of the ACP Java SDK itself (`com.agentclientprotocol`, replacing
`org.springaicommunity`), versioned together with it; see the
[0.80.0 migration guide](/docs/acp-java-sdk/migration-0.80). It brings the Jackson 3 JSON module,
`acp-json-jackson3`, so you add no JSON dependency yourself.

<Note>
The downloadable module builds against the released starter (`org.springaicommunity`, SDK 0.18.0) by
default; build with `-Psdk-candidate` to use the SDK's own starter at the coordinates shown above.
</Note>

## The Agent

Compare this with [Module 12's builder-based agent](/docs/acp-java-sdk/tutorial/12-echo-agent). The annotation approach replaces the builder chain with annotated methods on a Spring bean:

```java
@Component
@AcpAgent(name = "echo-agent", version = "1.0")
public class EchoAgentBean {

    @NewSession
    public NewSessionResponse newSession(NewSessionRequest request) {
        return new NewSessionResponse(UUID.randomUUID().toString(), null, null);
    }

    @Prompt
    public PromptResponse prompt(PromptRequest request, SyncPromptContext context) {
        context.sendMessage("Echo: " + request.text());
        return PromptResponse.endTurn();
    }
}
```

No `@Initialize` method: as of 0.80.0, the SDK derives the `initialize` answer from the class itself
(`agentInfo` from `@AcpAgent(name, version)` here). See
[Clients and Agents in Java](/docs/acp-java-sdk/clients-and-agents) for the full derivation rules.

The application class is a standard `@SpringBootApplication`:

```java
@SpringBootApplication
public class EchoAgentApplication {

    public static void main(String[] args) {
        SpringApplication.run(EchoAgentApplication.class, args);
    }
}
```

## What the Autoconfiguration Does

When Spring Boot starts, the ACP autoconfiguration:

1. **Creates a `StdioAcpAgentTransport`** — the default for agents (reads stdin, writes stdout)
2. **Discovers the `@AcpAgent` bean** — scans the application context for exactly one `@AcpAgent`-annotated bean
3. **Wires through `AcpAgentSupport`**: resolves `@NewSession`, `@Prompt`, and any other handler methods; derives `initialize` from the class if there's no `@Initialize`
4. **Starts via `SmartLifecycle`** — the agent starts after the application context refreshes and stops on shutdown

No explicit `agent.run()` call. No manual transport creation. Spring manages it all.

## Stdio and Logging

Agent stdout is reserved for the JSON-RPC protocol. Spring Boot's default logging writes to stdout, which would corrupt the protocol stream.

Three configuration changes fix this:

**application.properties:**
```properties
# Disable banner — stdout is reserved for JSON-RPC
spring.main.banner-mode=off

# Keep the JVM alive (no web server to block)
spring.main.keep-alive=true
```

The `keep-alive` setting is essential. Without it, the Spring Boot application starts the agent, then exits immediately because there's no web server keeping the JVM alive.

**logback-spring.xml:**
```xml
<configuration>
    <appender name="STDERR" class="ch.qos.logback.core.ConsoleAppender">
        <target>System.err</target>
        <encoder>
            <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    <root level="INFO">
        <appender-ref ref="STDERR"/>
    </root>
</configuration>
```

## Build & Run

```bash
# Package the Spring Boot agent
./mvnw package -pl module-23-spring-boot-agent -q

# Run the demo (launches agent as subprocess and talks to it)
./mvnw exec:java -pl module-23-spring-boot-agent
```

## Module 12 vs Module 23

| Aspect | Module 12 (Builder) | Module 23 (Spring Boot) |
|--------|-------------------|----------------------|
| Transport | Manual `new StdioAcpAgentTransport()` | Autoconfigured |
| Handlers | Lambda callbacks via builder | Annotated methods on a bean |
| Lifecycle | Explicit `agent.run()` | `SmartLifecycle` (automatic) |
| Configuration | Hardcoded in Java | `application.properties` |
| Dependencies | `acp-core` and `acp-json-jackson2` | `acp-spring-boot-starter` |

## Configuration Properties

| Property | Default | Description |
|----------|---------|-------------|
| `spring.acp.agent.enabled` | `true` | Enable/disable agent autoconfiguration |
| `spring.acp.agent.request-timeout` | `60s` | Request processing timeout |
| `spring.acp.agent.transport.type` | `stdio` | `stdio` or `http` (remote agents; see [Remote Agents over Streamable HTTP](/docs/acp-java-sdk/autoconfig#remote-agents-over-streamable-http)) |

## Next

[Module 24: Spring Boot Client](/docs/acp-java-sdk/tutorial/24-spring-boot-client) — use the autoconfigured client to connect to agents.

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-23-spring-boot-agent)
