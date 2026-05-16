# Module 02: Protocol Basics

Deep dive into the ACP initialize handshake and version negotiation.

## What You'll Learn

- The `InitializeRequest` and `InitializeResponse` structure
- Protocol version negotiation semantics
- Client and agent capability exchange

## How It Works

The initialize handshake is the first message exchange in ACP — it must complete before any session or prompt operations. Both sides exchange:

1. **Protocol version** — they agree on a compatible version
2. **Client capabilities** — what the client can provide (file system access, terminal execution)
3. **Agent capabilities** — what the agent supports (session loading, image content, MCP)

## The Code

Module 01 called `client.initialize()` with defaults. Here we use the explicit form to control exactly what capabilities we advertise. The `InitializeResponse` tells us what the agent supports:

```java
// Initialize with explicit protocol version and capabilities
var initResponse = client.initialize(
    new InitializeRequest(1, new ClientCapabilities(
        new FileSystemCapability(true, true),  // read, write
        false  // terminalExecution
    )));

System.out.println("Protocol version: " + initResponse.protocolVersion());
System.out.println("Agent capabilities: " + initResponse.agentCapabilities());
System.out.println("Existing sessions: " + initResponse.sessionIds().size());
// Output: Protocol version: 1
//         Agent capabilities: AgentCapabilities[...]
//         Existing sessions: 0
```

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-02-protocol-basics)

## Running the Example

```bash
export GEMINI_API_KEY=your-key-here
./mvnw exec:java -pl module-02-protocol-basics
```

## Next Module

[Module 03: Sessions](/acp-java-sdk/tutorial/03-sessions) — create and manage conversation sessions.
