---
title: "Java API Reference"
sidebarTitle: "Java"
description: "Complete API reference for the ACP Java SDK — client, agent, protocol types, transports, and test utilities."
---

Complete API reference for the ACP Java SDK, covering client, agent (all three styles), protocol types, transports, errors, and test utilities.

---

## Installation

### Maven (0.12.0 — stable)

Core SDK (client + sync/async agent APIs):

```xml
<dependency>
    <groupId>com.agentclientprotocol</groupId>
    <artifactId>acp-core</artifactId>
    <version>0.12.0</version>
</dependency>
```

Annotation-based agent support (includes `acp-core` transitively):

```xml
<dependency>
    <groupId>com.agentclientprotocol</groupId>
    <artifactId>acp-agent-support</artifactId>
    <version>0.12.0</version>
</dependency>
```

Test utilities:

```xml
<dependency>
    <groupId>com.agentclientprotocol</groupId>
    <artifactId>acp-test</artifactId>
    <version>0.12.0</version>
    <scope>test</scope>
</dependency>
```

WebSocket server transport for agents:

```xml
<dependency>
    <groupId>com.agentclientprotocol</groupId>
    <artifactId>acp-websocket-jetty</artifactId>
    <version>0.12.0</version>
</dependency>
```

### Gradle

```groovy
// build.gradle
implementation 'com.agentclientprotocol:acp-core:0.12.0'

// Optional modules
implementation 'com.agentclientprotocol:acp-agent-support:0.12.0'
implementation 'com.agentclientprotocol:acp-websocket-jetty:0.12.0'
testImplementation 'com.agentclientprotocol:acp-test:0.12.0'
```

```kotlin
// build.gradle.kts
implementation("com.agentclientprotocol:acp-core:0.12.0")

// Optional modules
implementation("com.agentclientprotocol:acp-agent-support:0.12.0")
implementation("com.agentclientprotocol:acp-websocket-jetty:0.12.0")
testImplementation("com.agentclientprotocol:acp-test:0.12.0")
```

### Snapshot (0.13.0-SNAPSHOT)

For unreleased features, add the snapshot repository and use the snapshot version:

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

Then use `0.13.0-SNAPSHOT` in place of `0.12.0` in your dependencies.

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
| `authenticate(request)` | `AuthenticateResponse` | Authenticate with a method ID |
| `logout(request)` | `LogoutResponse` | Clear stored credentials *(0.13.0)* |
| `newSession(request)` | `NewSessionResponse` | Create a new session |
| `loadSession(request)` | `LoadSessionResponse` | Resume an existing session (replays history) |
| `listSessions(request)` | `ListSessionsResponse` | List sessions, optional cwd filter *(0.12.0)* |
| `resumeSession(request)` | `ResumeSessionResponse` | Reconnect to session without history replay *(0.12.0)* |
| `closeSession(request)` | `CloseSessionResponse` | Close session and free resources *(0.12.0)* |
| `deleteSession(request)` | `DeleteSessionResponse` | Permanently delete a stored session *(0.13.0)* |
| `forkSession(request)` | `ForkSessionResponse` | Fork a session into a new branch *(0.12.0, unstable)* |
| `setSessionConfigOption(request)` | `SetSessionConfigOptionResponse` | Set a session config value *(0.12.0)* |
| `listProviders(request)` | `ListProvidersResponse` | List configurable model/backend providers *(0.13.0, unstable)* |
| `setProvider(request)` | `SetProviderResponse` | Configure a provider (protocol, base URL, headers) *(0.13.0, unstable)* |
| `disableProvider(request)` | `DisableProviderResponse` | Disable a provider by id *(0.13.0, unstable)* |
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
    .createElicitationHandler(req -> {
        // Agent requests structured user input (unstable)
        return CreateElicitationResponse.accept(Map.of("choice", "option-a"));
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
| `@Logout` | `logout` | Clears stored credentials *(0.13.0)* |
| `@NewSession` | `session/new` | Creates a new agent session |
| `@LoadSession` | `session/load` | Loads an existing session by ID (replays history) |
| `@ListSessions` | `session/list` | Lists sessions with optional cwd filter *(0.12.0)* |
| `@ResumeSession` | `session/resume` | Reconnects to session without history replay *(0.12.0)* |
| `@CloseSession` | `session/close` | Closes session and frees resources *(0.12.0)* |
| `@DeleteSession` | `session/delete` | Permanently deletes a stored session *(0.13.0)* |
| `@ForkSession` | `session/fork` | Forks a session into a new branch *(0.12.0, unstable)* |
| `@SetSessionConfigOption` | `session/set_config_option` | Sets a session config value *(0.12.0)* |
| `@ListProviders` | `providers/list` | Lists configurable providers *(0.13.0, unstable)* |
| `@SetProvider` | `providers/set` | Configures a provider *(0.13.0, unstable)* |
| `@DisableProvider` | `providers/disable` | Disables a provider by id *(0.13.0, unstable)* |
| `@Prompt` | `session/prompt` | Handles user prompts |
| `@SetSessionMode` | `session/set_mode` | Changes operational mode |
| `@SetSessionModel` | `session/set_model` | **Deprecated** — removed from the spec; use `@SetSessionConfigOption` with a `"model"` category option |
| `@Cancel` | `session/cancel` | Cancellation notification (fire-and-forget) |

> **Deprecated: the session-model API (0.13.0).** `session/set_model` and the related types
> (`@SetSessionModel`, `SetSessionModelRequest`/`Response`, `SessionModelState`, `ModelInfo`, and the
> `models` field on session responses) were removed from the ACP spec in June 2026 and are marked
> `@Deprecated(forRemoval = true)`. They still work for now but will be removed in a future release.
> Expose model selection through `session/set_config_option` instead: advertise a `select` config
> option whose `category` is `"model"`, and switch models with `setSessionConfigOption(...)`. This is
> the same mechanism used for session modes (`category: "mode"`) and reasoning level
> (`category: "thought_level"`).

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

    // Tag streamed chunks with a message ID (0.13.0) — chunks sharing an id
    // form one logical message; a new id starts a new message
    ctx.sendMessage("First part...", "msg-1");
    ctx.sendThought("Reasoning...", "msg-1");

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

        if (ctx.getClientCapabilities().supportsReadTextFile()) {
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
| `authenticateHandler(handler)` | Handle `authenticate` requests |
| `logoutHandler(handler)` | Handle `logout` requests *(0.13.0)* |
| `newSessionHandler(handler)` | Handle `session/new` requests |
| `loadSessionHandler(handler)` | Handle `session/load` requests |
| `listSessionsHandler(handler)` | Handle `session/list` requests *(0.12.0)* |
| `resumeSessionHandler(handler)` | Handle `session/resume` requests *(0.12.0)* |
| `closeSessionHandler(handler)` | Handle `session/close` requests *(0.12.0)* |
| `deleteSessionHandler(handler)` | Handle `session/delete` requests *(0.13.0)* |
| `forkSessionHandler(handler)` | Handle `session/fork` requests *(0.12.0, unstable)* |
| `setSessionConfigOptionHandler(handler)` | Handle `session/set_config_option` requests *(0.12.0)* |
| `listProvidersHandler(handler)` | Handle `providers/list` requests *(0.13.0, unstable)* |
| `setProviderHandler(handler)` | Handle `providers/set` requests *(0.13.0, unstable)* |
| `disableProviderHandler(handler)` | Handle `providers/disable` requests *(0.13.0, unstable)* |
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
    new PromptCapabilities(true, false, true)       // audio, embeddedContext, image
);
return InitializeResponse.ok(caps);

// Send non-text update types (Plan, ToolCall, AvailableCommandsUpdate, etc.)
context.sendUpdate(sessionId, new Plan("plan", List.of(
    new PlanEntry("Analyze code", PlanEntryPriority.HIGH, PlanEntryStatus.IN_PROGRESS),
    new PlanEntry("Generate tests", PlanEntryPriority.MEDIUM, PlanEntryStatus.PENDING)
)));

context.sendUpdate(sessionId, new ToolCall("tool_call",
    "search-1", "code-search", ToolKind.SEARCH, ToolCallStatus.IN_PROGRESS,
    null, null, null, null, null));

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
| `InitializeResponse` | `protocolVersion`, `agentCapabilities`, `authMethods`, `agentInfo` |
| `AuthenticateRequest` | `methodId` |
| `AuthenticateResponse` | *(empty)* |
| `LogoutRequest` | *(empty)* *(0.13.0)* |
| `LogoutResponse` | *(empty)* *(0.13.0)* |
| `NewSessionRequest` | `cwd`, `mcpServers`, `additionalDirectories` *(`additionalDirectories` 0.13.0)* |
| `NewSessionResponse` | `sessionId`, `modes`, ~~`models`~~ *(`models` deprecated — see below)* |
| `LoadSessionRequest` | `sessionId`, `cwd`, `mcpServers`, `additionalDirectories` *(`additionalDirectories` 0.13.0)* |
| `LoadSessionResponse` | `modes`, ~~`models`~~ *(deprecated)* |
| `ListSessionsRequest` | `cwd` (optional filter), `cursor` (pagination) *(0.12.0)* |
| `ListSessionsResponse` | `sessions` (list of `SessionInfo`), `nextCursor` *(0.12.0)* |
| `ResumeSessionRequest` | `sessionId`, `cwd`, `mcpServers`, `additionalDirectories` *(0.12.0; `additionalDirectories` 0.13.0)* |
| `ResumeSessionResponse` | `modes`, ~~`models`~~ *(0.12.0; `models` deprecated)* |
| `CloseSessionRequest` | `sessionId` *(0.12.0)* |
| `CloseSessionResponse` | *(empty)* *(0.12.0)* |
| `DeleteSessionRequest` | `sessionId` *(0.13.0)* |
| `DeleteSessionResponse` | *(empty)* *(0.13.0)* |
| `ForkSessionRequest` | `sessionId`, `cwd`, `mcpServers`, `additionalDirectories` *(0.12.0, unstable)* |
| `ForkSessionResponse` | `sessionId`, `modes`, ~~`models`~~, `configOptions` *(0.12.0, unstable; `models` deprecated)* |
| `SetSessionConfigOptionRequest` | `sessionId`, `configId`, `value`, `type` *(0.12.0)* |
| `SetSessionConfigOptionResponse` | `configOptions` (full config state) *(0.12.0)* |
| `ListProvidersRequest` | *(empty)* *(0.13.0, unstable)* |
| `ListProvidersResponse` | `providers` (list of `ProviderInfo`) *(0.13.0, unstable)* |
| `SetProviderRequest` | `id`, `apiType`, `baseUrl`, `headers` *(0.13.0, unstable)* |
| `SetProviderResponse` | *(empty)* *(0.13.0, unstable)* |
| `DisableProviderRequest` | `id` *(0.13.0, unstable)* |
| `DisableProviderResponse` | *(empty)* *(0.13.0, unstable)* |
| `CreateElicitationRequest` | `sessionId`, `message`, `mode`, `requestedSchema` *(0.12.0, unstable)* |
| `CreateElicitationResponse` | `action` (accept/decline/cancel), `content` *(0.12.0, unstable)* |
| `CompleteElicitationNotification` | `elicitationId` *(0.12.0, unstable)* |
| `PromptRequest` | `sessionId`, `prompt` (list of `ContentBlock`) |
| `PromptResponse` | `stopReason` |
| `CancelNotification` | `sessionId` |

### Session Types *(0.12.0)*

| Type | Fields | Description |
| :--- | :----- | :---------- |
| `SessionInfo` | `sessionId`, `cwd`, `title`, `updatedAt`, `additionalDirectories` | Session metadata returned by `session/list` *(`additionalDirectories` 0.13.0)* |
| `SessionCapabilities` | `list`, `close`, `resume`, `delete`, `additionalDirectories`, `fork` | Nested capability flags on `AgentCapabilities` *(`delete`, `additionalDirectories` 0.13.0; `fork` unstable)* |

### Config Option Types *(0.12.0)*

`session/set_config_option` is stable. The `select` variant is the stable shape; `boolean` is an SDK extension.

| Type | Description |
| :--- | :---------- |
| `SessionConfigOption` | Polymorphic: `SessionConfigSelect` or `SessionConfigBoolean` |
| `SessionConfigSelect` | Select-type config with `currentValue`, `category`, and `options` list |
| `SessionConfigBoolean` | Boolean toggle with `currentValue` *(unstable extension)* |
| `SessionConfigSelectOption` | A named value within a select config (`value`, `name`) |
| `ConfigOptionUpdate` | SessionUpdate variant for agent-pushed config changes |

### Provider Types *(0.13.0, unstable)*

Model/backend routing configuration. The agent advertises support with a `providers` capability; the
client manages providers via `listProviders` / `setProvider` / `disableProvider`.

| Type | Description |
| :--- | :---------- |
| `ProviderInfo` | A configurable provider: `id`, `supported` (protocol ids), `required`, `current` |
| `ProviderCurrentConfig` | Current effective routing: `apiType`, `baseUrl` |
| `ProvidersCapabilities` | Agent capability marker (presence = supported), on `AgentCapabilities` |

`apiType` / `supported` use well-known `LlmProtocol` ids (`anthropic`, `openai`, `azure`, `vertex`, `bedrock`) or a custom string, modeled as `String` in the SDK.

### Elicitation Types *(0.12.0, unstable)*

| Type | Description |
| :--- | :---------- |
| `ElicitationSchema` | JSON Schema describing form fields (`properties`, `required`) |
| `ElicitationPropertySchema` | Polymorphic: `StringPropertySchema`, `NumberPropertySchema`, `IntegerPropertySchema`, `BooleanPropertySchema`, `MultiSelectPropertySchema` |
| `EnumOption` | Named value for select/multi-select (`const`, `title`) |
| `ElicitationCapabilities` | Client capability for form and/or URL elicitation |
| `ElicitationAction` | Enum: `ACCEPT`, `DECLINE`, `CANCEL` |

### Content Types

| Type | Description |
| :--- | :---------- |
| `TextContent` | Text content with `text` field |
| `ImageContent` | Image content (base64 or URL) |

### Session Update Types

| Type | Description |
| :--- | :---------- |
| `UserMessageChunk` | Incremental user message text (optional `messageId`) |
| `AgentMessageChunk` | Incremental response text (optional `messageId` — 0.13.0) |
| `AgentThoughtChunk` | Agent thinking process (optional `messageId` — 0.13.0) |
| `ToolCall` | Tool execution start |
| `ToolCallUpdateNotification` | Tool progress update |
| `Plan` | Agent's planned steps |
| `AvailableCommandsUpdate` | Advertised slash commands |
| `CurrentModeUpdate` | Agent mode change |
| `UsageUpdate` | Context window and cost usage |
| `ConfigOptionUpdate` | Session config option changes |

Content chunks (`UserMessageChunk`, `AgentMessageChunk`, `AgentThoughtChunk`) carry an optional `messageId`: chunks sharing the same id belong to one logical message, and a change in id starts a new message *(0.13.0)*.

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

### Session Capabilities *(0.12.0)*

Agents advertise session management support via `SessionCapabilities`. The
`NegotiatedCapabilities` accessors are: `supportsListSessions()`, `supportsCloseSession()`,
`supportsResumeSession()`, `supportsDeleteSession()` *(0.13.0)*,
`supportsAdditionalDirectories()` *(0.13.0)*, and `supportsForkSession()` *(unstable)* — each with a
matching `require*()` that throws `AcpCapabilityException`.

```java
NegotiatedCapabilities caps = client.getAgentCapabilities();
if (caps.supportsListSessions()) {
    client.listSessions(new ListSessionsRequest(null));
}
if (caps.supportsDeleteSession()) {
    client.deleteSession(new DeleteSessionRequest(sessionId));
}
if (caps.supportsAdditionalDirectories()) {
    client.newSession(new NewSessionRequest(cwd, List.of(), List.of("/extra/dir")));
}
```

### Elicitation Capabilities *(0.12.0, unstable)*

Clients advertise elicitation support during initialization:

```java
// Client: advertise form-mode elicitation support
var caps = new ClientCapabilities(
    new FileSystemCapability(), false,
    new ElicitationCapabilities(), null);
client.initialize(new InitializeRequest(1, caps));
```

```java
// Agent: check before sending elicitation
if (context.getClientCapabilities().supportsElicitation()) {
    var response = context.createElicitation(
        CreateElicitationRequest.form(sessionId, "Pick one:", schema));
}
```

### `@UnstableAcpApi`

APIs marked `@UnstableAcpApi` correspond to protocol elements in `schema.unstable.json`. They are public and functional but may change in any minor release. When the protocol element stabilizes, the annotation is removed (compatible change). See [Versioning](#versioning) for the full policy.

IntelliJ users can configure the *Unstable API Usage* inspection (*Settings > Inspections > JVM languages*) to flag usages.

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
    AcpJsonMapper.createDefault()
);
```

**Agent (requires acp-websocket-jetty):**
```java
var transport = new WebSocketAcpAgentTransport(
    8080, "/acp", AcpJsonMapper.createDefault()
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
