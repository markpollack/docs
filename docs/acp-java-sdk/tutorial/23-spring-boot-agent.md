# Module 23: Spring Boot Agent

Build an ACP agent as a Spring Boot application. No manual transport or lifecycle wiring required.

## Prerequisites

- Java 21+ (Spring Boot 4.x requirement)
- Completed [Module 12: Echo Agent](/acp-java-sdk/tutorial/12-echo-agent)

## What You'll Learn

- Using `@AcpAgent` annotations with Spring Boot autoconfiguration
- How the starter eliminates boilerplate transport and lifecycle code
- Redirecting logging to stderr for stdio agents

## Dependencies

Add the ACP Spring Boot Starter:

```xml
<dependency>
    <groupId>org.springaicommunity</groupId>
    <artifactId>acp-spring-boot-starter</artifactId>
    <version>0.11.0</version>
</dependency>
```

## The Agent

Compare this with [Module 12's builder-based agent](/acp-java-sdk/tutorial/12-echo-agent). The annotation approach replaces the builder chain with annotated methods on a Spring bean:

```java
@Component
@AcpAgent(name = "echo-agent", version = "1.0")
public class EchoAgentBean {

    @Initialize
    public InitializeResponse initialize(InitializeRequest request) {
        return InitializeResponse.ok();
    }

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
3. **Wires through `AcpAgentSupport`** — resolves `@Initialize`, `@NewSession`, `@Prompt` handler methods
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
| Dependencies | `acp-core` only | `acp-spring-boot-starter` |

## Configuration Properties

| Property | Default | Description |
|----------|---------|-------------|
| `spring.acp.agent.enabled` | `true` | Enable/disable agent autoconfiguration |
| `spring.acp.agent.request-timeout` | `60s` | Request processing timeout |
| `spring.acp.agent.transport.type` | `stdio` | Transport type (currently only `stdio`) |

## Next

[Module 24: Spring Boot Client](/acp-java-sdk/tutorial/24-spring-boot-client) — use the autoconfigured client to connect to agents.

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-23-spring-boot-agent)
