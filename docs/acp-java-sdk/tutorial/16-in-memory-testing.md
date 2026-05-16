# Module 16: In-Memory Testing

Test client-agent communication without subprocesses or I/O.

## What You'll Learn

- Using `InMemoryTransportPair` from `acp-test`
- Wiring a client and agent together in-process
- Fast, deterministic testing without external dependencies

## The Code

`InMemoryTransportPair` from the `acp-test` module creates a pair of connected transports — one for the client, one for the agent. Messages pass through in-memory buffers instead of subprocess stdin/stdout. This makes tests fast, deterministic, and free of external dependencies. The pattern below wires up an agent and client in the same JVM, sends a prompt, and verifies the round-trip:

```java
import com.agentclientprotocol.sdk.test.InMemoryTransportPair;
import com.agentclientprotocol.sdk.agent.*;
import com.agentclientprotocol.sdk.client.*;
import com.agentclientprotocol.sdk.spec.AcpSchema.*;
import reactor.core.publisher.Mono;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;

// 1. Create in-memory transport pair
var transportPair = InMemoryTransportPair.create();

// 2. Create agent (using async API here)
AtomicReference<String> receivedPrompt = new AtomicReference<>();

AcpAsyncAgent agent = AcpAgent.async(transportPair.agentTransport())
    .initializeHandler(req -> Mono.just(InitializeResponse.ok()))
    .newSessionHandler(req ->
        Mono.just(new NewSessionResponse(
            UUID.randomUUID().toString(), null, null)))
    .promptHandler((req, context) -> {
        String text = req.text();
        receivedPrompt.set(text);

        return context.sendMessage("Echo: " + text)
            .then(Mono.just(PromptResponse.endTurn()));
    })
    .build();

agent.start().subscribe();

// 3. Create client
AtomicReference<String> receivedMessage = new AtomicReference<>();

AcpSyncClient client = AcpClient.sync(transportPair.clientTransport())
    .sessionUpdateConsumer(notification -> {
        if (notification.update() instanceof AgentMessageChunk msg) {
            receivedMessage.set(((TextContent) msg.content()).text());
        }
    })
    .build();

// 4. Run test
client.initialize();
var session = client.newSession(new NewSessionRequest(".", List.of()));
client.prompt(new PromptRequest(
    session.sessionId(),
    List.of(new TextContent("Hello from in-memory test!"))
));

// 5. Verify
assert "Hello from in-memory test!".equals(receivedPrompt.get());
assert "Echo: Hello from in-memory test!".equals(receivedMessage.get());

// 6. Cleanup
client.close();
transportPair.closeGracefully().block();
```

## How It Works

`InMemoryTransportPair.create()` returns a pair of connected transports:

| Transport | Used By | Description |
|-----------|---------|-------------|
| `transportPair.clientTransport()` | Client | Sends to agent, receives from agent |
| `transportPair.agentTransport()` | Agent | Receives from client, sends to client |

Messages pass through in-memory buffers. No subprocess launching, no stdin/stdout, no network I/O. This makes tests fast and deterministic.

## Maven Dependency

```xml
<dependency>
    <groupId>com.agentclientprotocol</groupId>
    <artifactId>acp-test</artifactId>
    <version>0.11.0</version>
    <scope>test</scope>
</dependency>
```

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-16-in-memory-testing)

## Running the Example

```bash
./mvnw exec:java -pl module-16-in-memory-testing
```

## Next Module

[Module 17: Capability Negotiation](/acp-java-sdk/tutorial/17-capability-negotiation) — advertise and check capabilities between client and agent.
