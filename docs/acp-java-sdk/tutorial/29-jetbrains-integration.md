# Module 29: JetBrains Integration

Run your Java ACP agent in IntelliJ IDEA, PyCharm, WebStorm, and other JetBrains IDEs.

## What You'll Learn

- Configuring JetBrains IDEs for ACP agents
- The `~/.jetbrains/acp.json` configuration format
- MCP server access from JetBrains

## Prerequisites

- JetBrains IDE version 25.3 RC or later
- JetBrains AI Assistant plugin enabled
- Java 17+

## The Agent

Same code as Module 28 (Zed). The agent is identical — only the IDE configuration differs:

```java
AcpSyncAgent agent = AcpAgent.sync(transport)
    .initializeHandler(req -> InitializeResponse.ok())
    .newSessionHandler(req ->
        new NewSessionResponse(UUID.randomUUID().toString(), null, null))
    .promptHandler((req, context) -> {
        String promptText = /* extract from req */;
        context.sendThought("Analyzing your request...");
        context.sendMessage(generateResponse(promptText));
        return PromptResponse.endTurn();
    })
    .build();

agent.run();
```

## Build and Configure

### 1. Build the JAR

```bash
./mvnw package -pl module-29-jetbrains-integration -q
```

### 2. Configure JetBrains

Create or edit `~/.jetbrains/acp.json`:

```json
{
  "agent_servers": {
    "Java Tutorial Agent": {
      "command": "java",
      "args": ["-jar", "/absolute/path/to/jetbrains-agent.jar"]
    }
  }
}
```

Or use the IDE: AI Chat tool window → gear icon → Configure ACP Agents.

### 3. Use the agent

Open AI Chat (`Alt+Shift+C`), select **Java Tutorial Agent** from the agent dropdown.

## Configuration Options

### With environment variables

```json
{
  "agent_servers": {
    "Java Tutorial Agent": {
      "command": "java",
      "args": ["-jar", "/path/to/jetbrains-agent.jar"],
      "env": {
        "MY_API_KEY": "your-key-here"
      }
    }
  }
}
```

### With IDE MCP server access

```json
{
  "agent_servers": {
    "Java Tutorial Agent": {
      "command": "java",
      "args": ["-jar", "/path/to/jetbrains-agent.jar"],
      "use_idea_mcp": true,
      "use_custom_mcp": true
    }
  }
}
```

## Supported IDEs

All JetBrains IDEs with AI Assistant support ACP in version 25.3 RC and later: IntelliJ IDEA, PyCharm, WebStorm, GoLand, PhpStorm, Rider, CLion, RubyMine, DataGrip.

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-29-jetbrains-integration)

## Running the Example

```bash
./mvnw package -pl module-29-jetbrains-integration -q
./mvnw exec:java -pl module-29-jetbrains-integration
```

## Next Module

[Module 30: VS Code Integration](/acp-java-sdk/tutorial/30-vscode-integration) — connect to VS Code using the community extension.
