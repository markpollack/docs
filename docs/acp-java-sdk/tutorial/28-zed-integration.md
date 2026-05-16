# Module 28: Zed Integration

Run your Java ACP agent inside the Zed editor.

## What You'll Learn

- Building an agent JAR for editor integration
- Configuring Zed to launch your agent
- The stdio transport mechanism editors use to communicate with agents

## Prerequisites

- [Zed editor](https://zed.dev/download) installed
- Java 17+
- Agent JAR built (see below)

## The Agent

The agent is the same sync builder pattern from Module 12, with conversational responses:

```java
var transport = new StdioAcpAgentTransport();

AcpSyncAgent agent = AcpAgent.sync(transport)
    .initializeHandler(req -> {
        System.err.println("[ZedAgent] Received initialize request");
        return InitializeResponse.ok();
    })

    .newSessionHandler(req -> {
        System.err.println("[ZedAgent] Creating session for cwd: " + req.cwd());
        return new NewSessionResponse(
            UUID.randomUUID().toString(), null, null);
    })

    .promptHandler((req, context) -> {
        String promptText = req.text();

        context.sendThought("Processing your request...");

        String response = generateResponse(promptText);
        context.sendMessage(response);

        return PromptResponse.endTurn();
    })
    .build();

agent.run();
```

Logging goes to stderr because Zed captures stdout for the JSON-RPC protocol.

## Build and Configure

### 1. Build the JAR

```bash
./mvnw package -pl module-28-zed-integration -q
```

### 2. Get the absolute path

```bash
realpath module-28-zed-integration/target/zed-agent.jar
```

### 3. Configure Zed

Open Zed settings (`Ctrl+,` on Linux, `Cmd+,` on Mac) and add:

```json
{
  "agent_servers": {
    "Java Tutorial Agent": {
      "type": "custom",
      "command": "java",
      "args": ["-jar", "/absolute/path/to/zed-agent.jar"]
    }
  }
}
```

### 4. Use in Zed

Open the Agent Panel (`Ctrl+?`), click **+**, select **Java Tutorial Agent**, and start chatting.

## How It Works

Zed launches your agent as a subprocess and communicates via JSON-RPC over stdio. This is the same mechanism used by LSP language servers. Your agent receives `initialize`, `session/new`, and `session/prompt` requests, and responds with JSON-RPC responses and notifications.

No code changes are needed for different editors. The same JAR works in Zed, JetBrains, and VS Code.

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-28-zed-integration)

## Running the Example

```bash
./mvnw package -pl module-28-zed-integration -q
./mvnw exec:java -pl module-28-zed-integration
```

## Next Module

[Module 29: JetBrains Integration](/acp-java-sdk/tutorial/29-jetbrains-integration) — configure the same agent for IntelliJ, PyCharm, and other JetBrains IDEs.
