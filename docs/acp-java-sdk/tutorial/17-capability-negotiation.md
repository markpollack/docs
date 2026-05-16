# Module 17: Capability Negotiation

Client and agent agree on what each supports during initialization.

## What You'll Learn

- Advertising `ClientCapabilities` during `initialize()`
- Checking `NegotiatedCapabilities` from the agent side
- Graceful degradation when a capability is missing

## The Code

### Client: Advertise capabilities

```java
// Tell the agent what we support
var clientCaps = new ClientCapabilities(
    new FileSystemCapability(true, true),  // readTextFile, writeTextFile
    true                                    // terminal
);

client.initialize(new InitializeRequest(1, clientCaps));

// Check what the agent supports
NegotiatedCapabilities agentCaps = client.getAgentCapabilities();
System.out.println("loadSession: " + agentCaps.supportsLoadSession());
System.out.println("mcpHttp: " + agentCaps.supportsMcpHttp());
System.out.println("mcpSse: " + agentCaps.supportsMcpSse());
```

### Agent: Advertise and check capabilities

```java
.initializeHandler(req -> {
    // Read what the client supports
    var clientCaps = req.clientCapabilities();

    // Advertise our own capabilities
    var agentCaps = new AgentCapabilities(
        true,                                    // loadSession
        new McpCapabilities(false, false),        // no MCP
        new PromptCapabilities(false, false, true) // embeddedContext only
    );

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

[Module 18: Terminal Operations](/acp-java-sdk/tutorial/18-terminal-operations) — execute shell commands through the terminal API.
