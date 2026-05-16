# Module 12: Echo Agent

Build a minimal ACP agent in ~25 lines. No API key required.

## What You'll Learn

- Building an agent with `AcpAgent.sync()`
- Implementing the three required handlers: initialize, newSession, prompt
- Sending messages back to the client
- Running a self-contained agent + client demo

## The Agent

```java
import com.agentclientprotocol.sdk.agent.*;
import com.agentclientprotocol.sdk.agent.transport.*;
import com.agentclientprotocol.sdk.spec.AcpSchema.*;
import java.util.UUID;

var transport = new StdioAcpAgentTransport();

AcpSyncAgent agent = AcpAgent.sync(transport)
    .initializeHandler(req -> InitializeResponse.ok())

    .newSessionHandler(req ->
        new NewSessionResponse(UUID.randomUUID().toString(), null, null))

    .promptHandler((req, context) -> {
        // Echo it back using convenience method
        context.sendMessage("Echo: " + req.text());
        return PromptResponse.endTurn();
    })
    .build();

agent.run();  // Blocks until client disconnects
```

## How It Works

An ACP agent needs three handlers:

| Handler | Purpose |
|---------|---------|
| `initializeHandler` | Protocol handshake — return capabilities |
| `newSessionHandler` | Create a session — return a unique session ID |
| `promptHandler` | Process prompts — send updates and return a stop reason |

`agent.run()` starts the agent and blocks. The agent reads JSON-RPC requests from stdin and writes responses to stdout. This is the stdio transport — the same mechanism Zed and JetBrains use to talk to agents.

The `context` parameter in the prompt handler gives access to `sendMessage()`, `sendThought()`, and other convenience methods for sending updates back to the client.

## The Demo Client

The module also includes `EchoAgentDemo.java`, which launches the echo agent as a subprocess and exercises it:

```java
// Launch echo agent as subprocess (from packaged JAR)
var params = AgentParameters.builder("java")
    .arg("-jar")
    .arg(jarPath)
    .build();

var transport = new StdioAcpClientTransport(params);

AcpSyncClient client = AcpClient.sync(transport)
    .sessionUpdateConsumer(notification -> {
        if (notification.update() instanceof AgentMessageChunk msg) {
            System.out.println(((TextContent) msg.content()).text());
        }
    })
    .build();

client.initialize();
var session = client.newSession(new NewSessionRequest(".", List.of()));
client.prompt(new PromptRequest(
    session.sessionId(),
    List.of(new TextContent("Hello, Echo Agent!"))
));
// Output: Echo: Hello, Echo Agent!
```

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-12-echo-agent)

## Running the Example

```bash
./mvnw package -pl module-12-echo-agent -q
./mvnw exec:java -pl module-12-echo-agent
```

## Key Points

- **No API key** — the agent runs entirely locally
- **Stdio transport** — same protocol mechanism used by Zed, JetBrains, VS Code
- **`agent.run()`** — combines `start()` and `awaitTermination()`
- **`context.sendMessage()`** — convenience for sending `AgentMessageChunk` updates

## Next Module

[Module 13: Agent Handlers](/acp-java-sdk/tutorial/13-agent-handlers) — implement all handler types including load session and cancel.
