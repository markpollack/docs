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

Module 01 called `client.initialize()` with defaults. Here we set explicit capabilities on the client builder to control exactly what we advertise, then call `initialize()` the same way. The `InitializeResponse` tells us what the agent supports:

```java
// Capabilities are set on the builder: what the client advertises here is
// also what its handlers honor.
var clientCapabilities = new ClientCapabilities(
    new FileSystemCapability(true, true),  // read, write
    false  // terminalExecution
);

AcpSyncClient client = AcpClient.sync(transport)
    .clientCapabilities(clientCapabilities)
    .build();

var initResponse = client.initialize();

System.out.println("Protocol version: " + initResponse.protocolVersion());
System.out.println("Agent capabilities: " + initResponse.agentCapabilities());
System.out.println("Existing sessions: " + initResponse.sessionIds().size());
// Output: Protocol version: 1
//         Agent capabilities: AgentCapabilities[...]
//         Existing sessions: 0
```

<Note>
As of 0.80.0, `initialize(InitializeRequest)` is removed: capabilities are set only on the client builder, and `initialize()` sends them. See the [0.80.0 migration guide](/docs/acp-java-sdk/migration-0.80).
</Note>

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-02-protocol-basics)

## Running the Example

Requires the Grok CLI on your `PATH`, signed in once with `grok login`. The module launches it as `grok agent stdio`; no API key is needed.

```bash
./mvnw exec:java -pl module-02-protocol-basics
```

## Next Module

[Module 03: Sessions](/docs/acp-java-sdk/tutorial/03-sessions) — create and manage conversation sessions.
