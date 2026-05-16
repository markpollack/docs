# Module 05: Streaming Updates

Receive real-time updates from an agent while it processes your prompt.

## What You'll Learn

- Registering a `sessionUpdateConsumer` on the client
- Dispatching on `SessionUpdate` types with `instanceof`
- Handling message chunks, thoughts, tool calls, and plans

## The Code

The client registers an update consumer that receives each `SessionUpdate` as it arrives:

```java
AcpSyncClient client = AcpClient.sync(transport)
    .sessionUpdateConsumer(notification -> {
        handleSessionUpdate(notification.update());
    })
    .build();
```

The handler uses `instanceof` to dispatch on the `SessionUpdate` type:

```java
private static void handleSessionUpdate(SessionUpdate update) {
    if (update instanceof AgentMessageChunk msg) {
        System.out.print(((TextContent) msg.content()).text());
    } else if (update instanceof AgentThoughtChunk thought) {
        System.out.println("[Thought] " +
            ((TextContent) thought.content()).text());
    } else if (update instanceof ToolCall tool) {
        System.out.println("[Tool] " + tool.title() +
            " (" + tool.status() + ")");
    } else if (update instanceof ToolCallUpdateNotification toolUpdate) {
        System.out.println("[Tool Update] " + toolUpdate.title() +
            " -> " + toolUpdate.status());
    } else if (update instanceof Plan plan) {
        System.out.println("[Plan] " + plan.entries().size() + " steps");
    } else if (update instanceof AvailableCommandsUpdate commands) {
        System.out.println("[Commands] " + commands.availableCommands().size() +
            " available");
    } else if (update instanceof CurrentModeUpdate mode) {
        System.out.println("[Mode] " + mode.currentModeId());
    } else if (update instanceof UsageUpdate usage) {
        System.out.println("[Usage] " + usage.used() + "/" + usage.size());
    }
}
```

## Session Update Types

| Type | Description |
|------|-------------|
| `AgentMessageChunk` | Incremental response text (the main output) |
| `AgentThoughtChunk` | Agent's thinking process |
| `ToolCall` | Tool execution starting |
| `ToolCallUpdateNotification` | Tool progress update |
| `Plan` | Agent's planned steps with priorities and status |
| `AvailableCommandsUpdate` | Slash commands the agent supports |
| `CurrentModeUpdate` | Agent mode change |
| `UsageUpdate` | Context window and cost usage (unstable) |

Updates arrive during `client.prompt()`. The prompt call blocks until the agent returns a `PromptResponse`, but updates stream in continuously through the consumer.

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-05-streaming-updates)

## Running the Example

```bash
export GEMINI_API_KEY=your-key-here
./mvnw exec:java -pl module-05-streaming-updates
```

## Next Module

[Module 12: Echo Agent](/acp-java-sdk/tutorial/12-echo-agent) — build your first ACP agent (no API key required).
