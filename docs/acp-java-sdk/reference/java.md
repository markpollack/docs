---
title: "Java API Reference"
sidebarTitle: "Java"
description: "Complete API reference for the ACP Java SDK — client, agent, protocol types, transports, and test utilities."
---

Complete API reference for the ACP Java SDK, covering client, agent (all three styles), protocol types, transports, errors, and test utilities.

---

## Installation

Snapshot builds are published to Maven Central Snapshots. Add the snapshot repository to your build.

### Maven

Add the snapshot repository, then the dependency:

```xml
<repositories>
    <repository>
        <id>central-snapshots</id>
        <url>https://central.sonatype.com/repository/maven-snapshots/</url>
        <snapshots><enabled>true</enabled></snapshots>
        <releases><enabled>false</enabled></releases>
    </repository>
</repositories>
```

Core SDK (client + sync/async agent APIs):

```xml
<dependency>
    <groupId>com.agentclientprotocol</groupId>
    <artifactId>acp-core</artifactId>
    <version>0.11.0</version>
</dependency>
```

Annotation-based agent support (includes `acp-core` transitively):

```xml
<dependency>
    <groupId>com.agentclientprotocol</groupId>
    <artifactId>acp-agent-support</artifactId>
    <version>0.11.0</version>
</dependency>
```

Test utilities:

```xml
<dependency>
    <groupId>com.agentclientprotocol</groupId>
    <artifactId>acp-test</artifactId>
    <version>0.11.0</version>
    <scope>test</scope>
</dependency>
```

WebSocket server transport for agents:

```xml
<dependency>
    <groupId>com.agentclientprotocol</groupId>
    <artifactId>acp-websocket-jetty</artifactId>
    <version>0.11.0</version>
</dependency>
```

### Gradle

```groovy
// build.gradle
implementation 'com.agentclientprotocol:acp-core:0.11.0'

// Optional modules
implementation 'com.agentclientprotocol:acp-agent-support:0.11.0'
implementation 'com.agentclientprotocol:acp-websocket-jetty:0.11.0'
testImplementation 'com.agentclientprotocol:acp-test:0.11.0'
```

```kotlin
// build.gradle.kts
implementation("com.agentclientprotocol:acp-core:0.11.0")

// Optional modules
implementation("com.agentclientprotocol:acp-agent-support:0.11.0")
implementation("com.agentclientprotocol:acp-websocket-jetty:0.11.0")
testImplementation("com.agentclientprotocol:acp-test:0.11.0")
```

---

## Three Agent API Styles

### Quick Comparison

| Feature | Annotation-based | Sync | Async |
| :------ | :--------------- | :--- | :---- |
| **Entry Point** | `@AcpAgent` class | `AcpAgent.sync()` | `AcpAgent.async()` |
| **Handler Style** | Annotated methods | Lambda callbacks | Lambda callbacks returning `Mono` |
| **Return Values** | Auto-converted (`String` → `PromptResponse`) | Direct protocol types | `Mono<ProtocolType>` |
| **Boilerplate** | Lowest | Moderate | Moderate |
| **Best For** | Most applications | Simple blocking handlers | Reactive applications |
| **Runtime** | `AcpAgentSupport` | `AcpSyncAgent` | `AcpAsyncAgent` |

All three produce identical protocol behavior and support the same capabilities.

### When to Use Each

- **Annotation-based** — default choice. Least boilerplate, auto-converts return types, supports interceptors and custom argument resolvers.
- **Sync** — when you want explicit control over every handler without annotations. Blocking void methods for sending updates.
- **Async** — when your agent needs non-blocking I/O. Uses Project Reactor `Mono` for composable async chains.

---

## Client API

### `AcpClient` — Factory

| Method | Return Type | Description |
| :----- | :---------- | :---------- |
| `sync(transport)` | `AcpSyncClient.Builder` | Create blocking client builder |
| `async(transport)` | `AcpAsyncClient.Builder` | Create reactive client builder |

### `AcpSyncClient` — Blocking Client

| Method | Return Type | Description |
| :----- | :---------- | :---------- |
| `initialize()` | `InitializeResponse` | Protocol handshake with defaults |
| `initialize(request)` | `InitializeResponse` | Handshake with custom capabilities |
| `newSession(request)` | `NewSessionResponse` | Create a new session |
| `loadSession(request)` | `LoadSessionResponse` | Resume an existing session |
| `prompt(request)` | `PromptResponse` | Send prompt, block until response |
| `cancel(notification)` | `void` | Cancel current prompt (fire-and-forget) |
| `getAgentCapabilities()` | `NegotiatedCapabilities` | Capabilities reported by agent |
| `close()` | `void` | Close connection |

### Builder Configuration

```java
AcpSyncClient client = AcpClient.sync(transport)
    .sessionUpdateConsumer(notification -> {
        // Handle streaming updates during prompt()
    })
    .readTextFileHandler(req -> {
        // Agent requests a file read
        return new ReadTextFileResponse(Files.readString(Path.of(req.path())));
    })
    .writeTextFileHandler(req -> {
        // Agent requests a file write
        Files.writeString(Path.of(req.path()), req.content());
        return new WriteTextFileResponse();
    })
    .requestPermissionHandler(req -> {
        // Agent requests permission
        return new RequestPermissionResponse(req.options().getFirst().id());
    })
    .build();
```

### Example — Complete client lifecycle

This launches Gemini CLI as an ACP agent subprocess and sends it a prompt. `AgentParameters` builds the command line; `StdioAcpClientTransport` spawns the process and handles JSON-RPC framing over stdin/stdout.

```java
// Launch "gemini --experimental-acp" as a subprocess
var params = AgentParameters.builder("gemini")
    .arg("--experimental-acp")
    .build();

var transport = new StdioAcpClientTransport(params);
AcpSyncClient client = AcpClient.sync(transport)
    .sessionUpdateConsumer(notification -> {
        var update = notification.update();
        if (update instanceof AgentMessageChunk msg) {
            System.out.print(((TextContent) msg.content()).text());
        }
    })
    .build();

client.initialize();
var session = client.newSession(new NewSessionRequest("/workspace", List.of()));

var response = client.prompt(new PromptRequest(
    session.sessionId(),
    List.of(new TextContent("Hello, world!"))
));

System.out.println("Stop reason: " + response.stopReason());
client.close();
```

---

## Agent API — Annotation-Based

The `acp-agent-support` module provides a declarative programming model using annotations.

### Annotations

#### Class-Level

| Annotation | Description |
|------------|-------------|
| `@AcpAgent` | Marks a class as an ACP agent. Optional `name` and `version` attributes. |

#### Handler Methods

| Annotation | JSON-RPC Method | Description |
|------------|-----------------|-------------|
| `@Initialize` | `initialize` | Protocol initialization and capability negotiation |
| `@NewSession` | `session/new` | Creates a new agent session |
| `@LoadSession` | `session/load` | Loads an existing session by ID |
| `@Prompt` | `session/prompt` | Handles user prompts |
| `@SetSessionMode` | `session/set_mode` | Changes operational mode |
| `@SetSessionModel` | `session/set_model` | Changes the AI model |
| `@Cancel` | `session/cancel` | Cancellation notification (fire-and-forget) |

#### Parameter Annotations

| Annotation | Description |
|------------|-------------|
| `@SessionId` | Injects the current session ID as `String` |
| `@SessionState` | Injects session-specific state |

### Flexible Method Signatures

Handler methods support flexible parameter resolution:

```java
// Minimal
@Initialize
InitializeResponse init() { return InitializeResponse.ok(); }

// With request
@Prompt
PromptResponse answer(PromptRequest req) { ... }

// With context
@Prompt
PromptResponse answer(PromptRequest req, SyncPromptContext ctx) { ... }

// Auto-converted return types
@Prompt
String simpleAnswer(PromptRequest req) { ... }  // → PromptResponse.text(value)

@Prompt
void streaming(PromptRequest req, SyncPromptContext ctx) { ... }  // → endTurn()
```

### Return Value Handling

| Return Type | Conversion |
|-------------|------------|
| Protocol response type | Passed through directly |
| `String` | Converted to `PromptResponse.text(value)` |
| `void` | Converted to `PromptResponse.endTurn()` |
| `Mono<PromptResponse>` | Unwrapped and returned |

### `SyncPromptContext`

Available in `@Prompt` handlers. Provides blocking methods for agent-client interaction:

```java
@Prompt
PromptResponse handle(PromptRequest req, SyncPromptContext ctx) {
    // Session info
    String sessionId = ctx.getSessionId();
    NegotiatedCapabilities caps = ctx.getClientCapabilities();

    // Messages and thoughts
    ctx.sendMessage("Working on it...");
    ctx.sendThought("Let me analyze this...");

    // File operations (requires client capabilities)
    String content = ctx.readFile("/path/to/file.txt");
    ctx.writeFile("/path/to/output.txt", "content");
    Optional<String> maybe = ctx.tryReadFile("/path/to/file.txt");

    // Permissions
    boolean allowed = ctx.askPermission("Delete files in /tmp?");
    String choice = ctx.askChoice("Which format?", "JSON", "XML", "YAML");

    // Terminal execution (requires client capabilities)
    CommandResult result = ctx.execute("ls", "-la");

    return PromptResponse.endTurn();
}
```

### `AcpAgentSupport` — Bootstrap

```java
AcpAgentSupport.create(new MyAgent())
    .transport(StdioAcpAgentTransport.create())
    .requestTimeout(Duration.ofSeconds(60))   // Optional
    .interceptor(new LoggingInterceptor())     // Optional
    .argumentResolver(new UserResolver())      // Optional
    .returnValueHandler(new FutureHandler())   // Optional
    .run();  // Blocks until client disconnects
```

### Interceptors

Cross-cutting concerns like logging, metrics, or error handling:

```java
public class LoggingInterceptor implements AcpInterceptor {

    @Override
    public boolean preInvoke(AcpInvocationContext context) {
        log.info("Invoking: {}", context.getAcpMethod());
        return true;  // Continue processing
    }

    @Override
    public Object postInvoke(AcpInvocationContext context, Object result) {
        log.info("Result: {}", result);
        return result;
    }

    @Override
    public int getOrder() { return 0; }  // Lower values execute first
}
```

### Example — Complete annotation-based agent

```java
@AcpAgent(name = "code-assistant", version = "1.0.0")
class CodeAssistant {

    private final Map<String, List<String>> sessionHistory = new ConcurrentHashMap<>();

    @Initialize
    InitializeResponse init() { return InitializeResponse.ok(); }

    @NewSession
    NewSessionResponse newSession(NewSessionRequest req) {
        String sessionId = UUID.randomUUID().toString();
        sessionHistory.put(sessionId, new ArrayList<>());
        return new NewSessionResponse(sessionId, List.of(), List.of());
    }

    @Prompt
    PromptResponse prompt(PromptRequest req, SyncPromptContext ctx) {
        ctx.sendThought("Analyzing the code...");

        if (ctx.getClientCapabilities().readTextFile()) {
            ctx.sendMessage("I can access files if needed.");
        }

        ctx.sendMessage("Here's my analysis...");
        return PromptResponse.endTurn();
    }

    @Cancel
    void onCancel(CancelNotification notification, @SessionId String sessionId) {
        sessionHistory.remove(sessionId);
    }
}
```

---

## Agent API — Sync (Builder)

Blocking handlers with plain return values. No annotations.

### Builder Methods

| Method | Description |
| :----- | :---------- |
| `initializeHandler(handler)` | Handle `initialize` requests |
| `newSessionHandler(handler)` | Handle `session/new` requests |
| `loadSessionHandler(handler)` | Handle `session/load` requests |
| `promptHandler(handler)` | Handle `session/prompt` requests |
| `cancelHandler(handler)` | Handle `session/cancel` notifications |

### Example

```java
AcpSyncAgent agent = AcpAgent.sync(transport)
    .initializeHandler(req -> InitializeResponse.ok())

    .newSessionHandler(req ->
        new NewSessionResponse(UUID.randomUUID().toString(), null, null))

    .promptHandler((req, context) -> {
        context.sendMessage("Hello!");
        return PromptResponse.endTurn();
    })
    .build();

agent.run();  // Blocks until client disconnects
```

### Prompt Handler Context

The `context` parameter in `promptHandler` provides:

| Method | Description |
| :----- | :---------- |
| `getSessionId()` | Current session ID |
| `sendMessage(text)` | Send `AgentMessageChunk` |
| `sendThought(text)` | Send `AgentThoughtChunk` |
| `sendUpdate(sessionId, update)` | Send any `SessionUpdate` |
| `readFile(path, offset, limit)` | Read file from client |
| `writeFile(path, content)` | Write file on client |
| `requestPermission(request)` | Ask client for permission |
| `getClientCapabilities()` | Check client capabilities |

---

## Agent API — Async (Builder)

Reactive handlers returning `Mono`. Uses Project Reactor.

### Example

```java
AcpAsyncAgent agent = AcpAgent.async(transport)
    .initializeHandler(req ->
        Mono.just(InitializeResponse.ok()))

    .newSessionHandler(req ->
        Mono.just(new NewSessionResponse(
            UUID.randomUUID().toString(), null, null)))

    .promptHandler((req, context) ->
        context.sendMessage("Hello!")
            .then(Mono.just(PromptResponse.endTurn())))
    .build();

agent.start().then(agent.awaitTermination()).block();
```

The async context's `sendMessage()`, `sendUpdate()`, etc. return `Mono<Void>`, composable with `.then()` and `.flatMap()`.

---

## Convenience Methods vs Full API

The SDK provides convenience methods that cover the most common operations. Use these by default — they produce cleaner code and handle the protocol details for you.

### When convenience methods are enough (~80% of cases)

```java
// Response factories
InitializeResponse.ok()                        // default capabilities
InitializeResponse.ok(customCapabilities)      // custom capabilities
PromptResponse.endTurn()                       // stop reason END_TURN
PromptResponse.text("response")                // message + endTurn in one call

// Sending updates (on SyncPromptContext or async equivalent)
context.sendMessage("Hello");                  // AgentMessageChunk with TextContent
context.sendThought("Analyzing...");           // AgentThoughtChunk with TextContent

// File operations
String content = context.readFile("pom.xml");  // read with defaults
context.writeFile("output.txt", "content");    // write file

// Terminal
CommandResult result = context.execute("ls", "-la");

// Permissions
boolean ok = context.askPermission("Delete temp files?");
String choice = context.askChoice("Format?", "JSON", "XML", "YAML");
```

### When to use the full API (~20% of cases)

Drop to the full API when you need control that convenience methods don't expose:

```java
// Custom AgentCapabilities with specific MCP and prompt settings
var caps = new AgentCapabilities(
    true,                                          // loadSession
    new McpCapabilities(true, true),               // HTTP + SSE
    new PromptCapabilities(true, false, true)       // imageContent, audioContent, embeddedContext
);
return InitializeResponse.ok(caps);

// Send non-text update types (Plan, ToolCall, AvailableCommandsUpdate, etc.)
context.sendUpdate(sessionId, new Plan("plan", List.of(
    new PlanStep("Analyze code", PlanStepStatus.IN_PROGRESS),
    new PlanStep("Generate tests", PlanStepStatus.PENDING)
)));

context.sendUpdate(sessionId, new ToolCall("tool_call",
    "search", "code-search", ToolCallStatus.IN_PROGRESS, null));

// Read file with offset and line limit
var response = context.readTextFile(
    new ReadTextFileRequest(sessionId, "large-file.txt", 100, 50));

// Request permission with custom options
var permResponse = context.requestPermission(new RequestPermissionRequest(
    sessionId, "Run deployment script?", List.of(
        new PermissionOption("allow-once", "Allow once", PermissionOptionKind.ALLOW_ONCE),
        new PermissionOption("always", "Always allow", PermissionOptionKind.ALLOW_ALWAYS),
        new PermissionOption("reject", "Reject", PermissionOptionKind.REJECT_ONCE)
    )));
```

The convenience methods are wrappers around the full API — they call the same underlying protocol methods. You can mix and match freely within a single handler.

---

## Protocol Types

All protocol types are defined in `AcpSchema` as Java records.

### Request/Response Types

| Type | Fields |
| :--- | :----- |
| `InitializeRequest` | `protocolVersion`, `clientCapabilities` |
| `InitializeResponse` | `protocolVersion`, `agentCapabilities`, `sessionIds` |
| `NewSessionRequest` | `cwd`, `mcpServers` |
| `NewSessionResponse` | `sessionId`, `restoredSessionState`, `contextDocuments` |
| `LoadSessionRequest` | `sessionId`, `cwd`, `mcpServers` |
| `LoadSessionResponse` | `restoredSessionState`, `contextDocuments` |
| `PromptRequest` | `sessionId`, `prompt` (list of `Content`) |
| `PromptResponse` | `stopReason` |
| `CancelNotification` | `sessionId` |

### Content Types

| Type | Description |
| :--- | :---------- |
| `TextContent` | Text content with `text` field |
| `ImageContent` | Image content (base64 or URL) |

### Session Update Types

| Type | Description |
| :--- | :---------- |
| `AgentMessageChunk` | Incremental response text |
| `AgentThoughtChunk` | Agent thinking process |
| `ToolCall` | Tool execution start |
| `ToolCallUpdateNotification` | Tool progress update |
| `Plan` | Agent's planned steps |
| `AvailableCommandsUpdate` | Advertised slash commands |
| `CurrentModeUpdate` | Agent mode change |
| `UsageUpdate` | Context window and cost usage (unstable) |

### Stop Reasons

| Value | Description |
| :---- | :---------- |
| `END_TURN` | Agent finished responding |
| `MAX_TOKENS` | Token limit reached |
| `REFUSAL` | Agent refused the request |
| `CANCELLED` | Prompt was cancelled |

### Convenience Methods

```java
// Static factory methods
InitializeResponse.ok()
PromptResponse.endTurn()
PromptResponse.text("response")
```

---

## Capabilities

### Client Capabilities

Advertised during `initialize`:

```java
client.initialize(new InitializeRequest(1,
    new ClientCapabilities(
        new FileSystemCapability(true, true),  // read, write
        true  // terminalExecution
    )));
```

### `NegotiatedCapabilities`

Check capabilities before using them:

```java
NegotiatedCapabilities caps = context.getClientCapabilities();
if (caps.supportsReadTextFile()) {
    String content = context.readFile("file.txt");
}
if (caps.supportsWriteTextFile()) {
    context.writeFile("output.txt", "content");
}
```

Or use `require` methods that throw `AcpCapabilityException` if unsupported:

```java
caps.requireWriteTextFile();
context.writeFile("output.txt", "content");
```

---

## Transports

| Transport | Client Class | Agent Class | Module |
|-----------|-------------|-------------|--------|
| **Stdio** | `StdioAcpClientTransport` | `StdioAcpAgentTransport` | acp-core |
| **WebSocket** | `WebSocketAcpClientTransport` | `WebSocketAcpAgentTransport` | acp-core / acp-websocket-jetty |
| **In-Memory** | via `InMemoryTransportPair` | via `InMemoryTransportPair` | acp-test |

### Stdio Transport

The default transport. The client launches the agent as a subprocess and communicates via JSON-RPC over stdin/stdout. This is the same mechanism Zed, JetBrains, and VS Code use to talk to agents.

**Client side** — `AgentParameters` specifies the command to launch. Any executable that speaks ACP over stdin/stdout works (Gemini CLI, your own agent JAR, etc.):
```java
var params = AgentParameters.builder("gemini")
    .arg("--experimental-acp")
    .build();
var transport = new StdioAcpClientTransport(params);
```

**Agent side** — reads JSON-RPC from stdin, writes responses to stdout. The agent doesn't need to know what launched it:
```java
var transport = new StdioAcpAgentTransport();
```

### WebSocket Transport

For network-based communication.

**Client (JDK-native, no extra dependencies):**
```java
var transport = new WebSocketAcpClientTransport(
    URI.create("ws://localhost:8080/acp"),
    McpJsonMapper.getDefault()
);
```

**Agent (requires acp-websocket-jetty):**
```java
var transport = new WebSocketAcpAgentTransport(
    8080, "/acp", McpJsonMapper.getDefault()
);
```

### In-Memory Transport

For testing. No subprocess or network I/O.

```java
var pair = InMemoryTransportPair.create();
// pair.clientTransport() — for client
// pair.agentTransport() — for agent
// pair.closeGracefully() — cleanup
```

---

## Errors

### Exception Hierarchy

| Exception | Description |
| :-------- | :---------- |
| `AcpProtocolException` | JSON-RPC protocol error with code and message |
| `AcpCapabilityException` | Tried to use an unsupported capability |
| `AcpConnectionException` | Transport-level connection failure |

### Error Codes

```java
try {
    client.prompt(request);
} catch (AcpProtocolException e) {
    if (e.isConcurrentPrompt()) {
        // Another prompt is already in progress
    } else if (e.isMethodNotFound()) {
        // Agent doesn't support this method
    }
    System.err.println("Error " + e.getCode() + ": " + e.getMessage());
} catch (AcpCapabilityException e) {
    System.err.println("Not supported: " + e.getCapability());
}
```

### Agent-Side Error Handling

Throw `AcpProtocolException` from handlers to send structured errors to clients:

```java
.promptHandler((req, context) -> {
    if (req.prompt().isEmpty()) {
        throw new AcpProtocolException(
            AcpErrorCodes.INVALID_PARAMS, "Empty prompt");
    }
    // ...
})
```

---

## Test Utilities

The `acp-test` module provides utilities for testing without subprocesses.

### `InMemoryTransportPair`

```java
var pair = InMemoryTransportPair.create();

// Wire up agent
AcpAsyncAgent agent = AcpAgent.async(pair.agentTransport())
    .initializeHandler(req -> Mono.just(InitializeResponse.ok()))
    .newSessionHandler(req -> Mono.just(
        new NewSessionResponse(UUID.randomUUID().toString(), null, null)))
    .promptHandler((req, context) ->
        context.sendMessage("response")
            .then(Mono.just(PromptResponse.endTurn())))
    .build();

agent.start().subscribe();

// Wire up client
AcpSyncClient client = AcpClient.sync(pair.clientTransport()).build();
client.initialize();
// ... test ...

pair.closeGracefully().block();
```

---

## Packages

| Package | Description |
|---------|-------------|
| `com.agentclientprotocol.sdk.spec` | Protocol types (`AcpSchema.*`) |
| `com.agentclientprotocol.sdk.client` | Client SDK (`AcpClient`, `AcpAsyncClient`, `AcpSyncClient`) |
| `com.agentclientprotocol.sdk.agent` | Agent SDK (`AcpAgent`, `AcpAsyncAgent`, `AcpSyncAgent`) |
| `com.agentclientprotocol.sdk.agent.support` | Annotation-based agent runtime (`AcpAgentSupport`) |
| `com.agentclientprotocol.sdk.annotation` | Agent annotations (`@AcpAgent`, `@Prompt`, etc.) |
| `com.agentclientprotocol.sdk.capabilities` | Capability negotiation (`NegotiatedCapabilities`) |
| `com.agentclientprotocol.sdk.error` | Exceptions (`AcpProtocolException`, `AcpCapabilityException`) |
| `com.agentclientprotocol.sdk.test` | Test utilities (`InMemoryTransportPair`) |

## Maven Artifacts

| Artifact | Description |
|----------|-------------|
| `acp-core` | Client and Agent SDKs, stdio and WebSocket client transports |
| `acp-annotations` | `@AcpAgent`, `@Prompt`, and other annotations |
| `acp-agent-support` | Annotation-based agent runtime (includes acp-annotations + acp-core) |
| `acp-test` | In-memory transport and test utilities |
| `acp-websocket-jetty` | Jetty-based WebSocket server transport for agents |

---

## See Also

- [ACP Java SDK GitHub](https://github.com/agentclientprotocol/java-sdk) — Source code
- [ACP Java Tutorial](https://github.com/markpollack/acp-java-tutorial) — 30 hands-on modules
- [Agent Client Protocol](https://agentclientprotocol.com/) — Official specification
