# Module 01: First Contact

Your first ACP client — launch an agent as a subprocess and send it a prompt.

## What You'll Learn

- How ACP communication works (subprocess + stdin/stdout JSON-RPC)
- Configuring agent process parameters with `AgentParameters`
- Registering a `sessionUpdateConsumer` to see the agent's response
- The three-phase lifecycle: initialize → newSession → prompt

## Prerequisites

1. **[Gemini CLI](https://github.com/google-gemini/gemini-cli) with ACP support** — the tutorial uses Gemini as a real ACP agent. Your client will launch it as a subprocess and talk to it over stdin/stdout.
   ```bash
   gemini --experimental-acp --version
   ```

2. **API key**
   ```bash
   export GEMINI_API_KEY=your-key-here
   ```

3. **Java 17 or later**

## The Code

The client launches `gemini --experimental-acp` as a child process. `AgentParameters` builds the command line. `StdioAcpClientTransport` spawns the process and handles JSON-RPC message framing over its stdin/stdout.

The `sessionUpdateConsumer` is how you see the agent's response. During `prompt()`, the agent streams back `AgentMessageChunk` updates containing the response text. Without a consumer, the prompt completes but you only get the stop reason — not the actual answer.

From there, ACP follows a three-phase lifecycle: initialize the connection, create a session (with a working directory context), then send prompts.

```java
import com.agentclientprotocol.sdk.client.*;
import com.agentclientprotocol.sdk.client.transport.*;
import com.agentclientprotocol.sdk.spec.AcpSchema.*;
import java.util.List;

// 1. Build the command: "gemini --experimental-acp"
var params = AgentParameters.builder("gemini")
    .arg("--experimental-acp")
    .build();

// 2. Launch it as a subprocess, communicate over stdin/stdout
var transport = new StdioAcpClientTransport(params);

// 3. Build client with update consumer to print the agent's response
AcpSyncClient client = AcpClient.sync(transport)
    .sessionUpdateConsumer(notification -> {
        if (notification.update() instanceof AgentMessageChunk msg) {
            System.out.print(((TextContent) msg.content()).text());
        }
    })
    .build();

// 4. Initialize — exchange protocol versions and capabilities
client.initialize();

// 5. Create session — set working directory context
var session = client.newSession(
    new NewSessionRequest(".", List.of()));

// 6. Send prompt — blocks until agent responds, updates stream to consumer
var response = client.prompt(new PromptRequest(
    session.sessionId(),
    List.of(new TextContent("What is 2+2? Reply with just the number."))
));

System.out.println("\nStop reason: " + response.stopReason());
client.close();
// Output: 4
// Stop reason: END_TURN
```

## How It Works

ACP communication follows a three-phase lifecycle:

1. **Initialize** — client and agent exchange protocol versions and capabilities
2. **New Session** — establishes a working directory context for the conversation
3. **Prompt** — sends content and receives a response with a stop reason

The stdio transport is not Gemini-specific. Any executable that speaks ACP over stdin/stdout works — Gemini CLI, a custom agent JAR, or any other ACP-compliant tool. This is the same mechanism Zed, JetBrains, and VS Code use to talk to agents.

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-01-first-contact)

## Running the Example

```bash
export GEMINI_API_KEY=your-key-here
./mvnw exec:java -pl module-01-first-contact
```

## Next Module

[Module 05: Streaming Updates](/acp-java-sdk/tutorial/05-streaming-updates) — receive real-time updates while the agent processes your prompt.

Or skip to [Module 12: Echo Agent](/acp-java-sdk/tutorial/12-echo-agent) to build your own agent (no API key required).
