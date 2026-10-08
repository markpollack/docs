# Module 17: Capability Negotiation

Client and agent agree on what each supports during initialization.

## What You'll Learn

- Advertising `ClientCapabilities` during `initialize()`
- Checking `NegotiatedCapabilities` from the agent side
- Graceful degradation when a capability is missing

## The Code

### Client: Advertise capabilities

```java
// Tell the agent what we support: set on the client builder, not on initialize(). As of 0.80.0,
// a client without this call would advertise what its handlers serve instead (Module 02); setting
// it explicitly here means it's sent exactly as given, which is this module's lesson.
var clientCaps = ClientCapabilities.builder()
    .readTextFile()
    .writeTextFile()  // no .terminal(): no terminal handlers here (see Module 18)
    .build();

AcpSyncClient client = AcpClient.sync(transport)
    .clientCapabilities(clientCaps)
    // A handler for each advertised capability, and only those: build() fails naming any
    // advertised capability with no handler, and warns about a handler for one not advertised.
    .readTextFileHandler(req -> new ReadTextFileResponse(Files.readString(Path.of(req.path()))))
    .writeTextFileHandler(req -> {
        Files.writeString(Path.of(req.path()), req.content());
        return new WriteTextFileResponse();
    })
    .build();

client.initialize();

// Check what the agent supports
NegotiatedCapabilities agentCaps = client.getAgentCapabilities();
System.out.println("loadSession: " + agentCaps.supportsLoadSession());
System.out.println("mcpHttp: " + agentCaps.supportsMcpHttp());
System.out.println("mcpSse: " + agentCaps.supportsMcpSse());
```

<Note>
As of 0.80.0, `initialize(InitializeRequest)` is removed: capabilities (and now `clientInfo`) are set only on the client builder, and `initialize()` sends them. See the [0.80.0 migration guide](/docs/acp-java-sdk/migration-0.80).
</Note>

<Note>
Advertising `terminal` here would need all five terminal handlers registered too
(`createTerminalHandler`, `terminalOutputHandler`, `waitForTerminalExitHandler`,
`killTerminalHandler`, `releaseTerminalHandler`): `build()` checks every advertised capability has
its handler, so this module keeps terminal out of its demo and leaves it to
[Module 18](/docs/acp-java-sdk/tutorial/18-terminal-operations), which serves all five.
</Note>

### Agent: Advertise and check capabilities

```java
.initializeHandler(req -> {
    // Read what the client supports
    var clientCaps = req.clientCapabilities();

    // Advertise our own capabilities
    var agentCaps = AgentCapabilities.builder()
        .loadSession()            // we support session resume
        .promptEmbeddedContext()  // only embeddedContext; no MCP, image or audio
        .build();

    return InitializeResponse.ok(agentCaps);
})

.promptHandler((req, context) -> {
    // Check capabilities before attempting operations
    NegotiatedCapabilities caps = context.getClientCapabilities();

    if (caps.supportsReadTextFile()) {
        String content = context.readFile("/etc/hostname");
    } else {
        // Graceful degradation
        context.sendMessage("File read not supported by client");
    }

    return PromptResponse.endTurn();
})
```

## Capability Categories

| Capability | Client | Agent |
|-----------|--------|-------|
| `FileSystemCapability` | readTextFile, writeTextFile | — |
| Terminal | terminal execution | — |
| `AgentCapabilities` | — | loadSession |
| `McpCapabilities` | — | HTTP, SSE |
| `PromptCapabilities` | — | imageContent, audioContent, embeddedContext |

Clients advertise file system and terminal support. Agents advertise session resume, MCP server types, and content format support. Both sides can call `getClientCapabilities()` or `getAgentCapabilities()` after initialization to check what was negotiated.

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-17-capability-negotiation)

## Running the Example

```bash
./mvnw package -pl module-17-capability-negotiation -q
./mvnw exec:java -pl module-17-capability-negotiation
```

## Next Module

[Module 18: Terminal Operations](/docs/acp-java-sdk/tutorial/18-terminal-operations) — execute shell commands through the terminal API.
