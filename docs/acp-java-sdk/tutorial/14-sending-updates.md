# Module 14: Sending Updates

Send all types of session updates from an agent to its client.

## What You'll Learn

- Convenience methods: `sendMessage()`, `sendThought()`
- Full API: `sendUpdate()` for complex types (plans, tool calls, commands)
- All `SessionUpdate` types from the agent's perspective

## The Code

The prompt handler demonstrates each update type:

```java
.promptHandler((req, context) -> {
    String sessionId = context.getSessionId();

    // 1. Thought — show thinking process (convenience method)
    context.sendThought("Let me analyze this request...");

    // 2. Plan — show steps and progress (full API)
    context.sendUpdate(sessionId,
        new Plan("plan", List.of(
            new PlanEntry("Analyze the prompt",
                PlanEntryPriority.HIGH, PlanEntryStatus.IN_PROGRESS),
            new PlanEntry("Generate response",
                PlanEntryPriority.HIGH, PlanEntryStatus.PENDING),
            new PlanEntry("Format output",
                PlanEntryPriority.MEDIUM, PlanEntryStatus.PENDING)
        )));

    // 3. Tool Call — show tool execution starting
    context.sendUpdate(sessionId,
        new ToolCall("tool_call",
            "tool-1", "Analyzing prompt", ToolKind.THINK,
            ToolCallStatus.IN_PROGRESS,
            List.of(), null, null, null, null));

    // 4. Tool Call Update — show progress
    context.sendUpdate(sessionId,
        new ToolCallUpdateNotification("tool_call_update",
            "tool-1", "Analyzing prompt", ToolKind.THINK,
            ToolCallStatus.COMPLETED,
            List.of(), null, null, null, null));

    // 5. Available Commands — advertise slash commands
    context.sendUpdate(sessionId,
        new AvailableCommandsUpdate("available_commands_update", List.of(
            new AvailableCommand("help", "Show help",
                new AvailableCommandInput("topic")),
            new AvailableCommand("clear", "Clear context", null)
        )));

    // 6. Mode Update — report current mode
    context.sendUpdate(sessionId,
        new CurrentModeUpdate("current_mode_update", "default"));

    // 7. Usage Update — report token usage and cost (unstable)
    context.sendUpdate(sessionId,
        new UsageUpdate("usage_update", 53000L, 200000L));

    // 8. Message chunks — the actual response (convenience method)
    context.sendMessage("Here is my response ");
    context.sendMessage("streamed in ");
    context.sendMessage("multiple chunks.");

    return PromptResponse.endTurn();
})
```

## Convenience vs Full API

| Method | Sends | When to Use |
|--------|-------|-------------|
| `context.sendMessage(text)` | `AgentMessageChunk` | Response text |
| `context.sendThought(text)` | `AgentThoughtChunk` | Thinking process |
| `context.sendUpdate(sessionId, update)` | Any `SessionUpdate` | Plans, tool calls, commands, modes |

Convenience methods handle wrapping in `TextContent` and setting the `type` field. Use `sendUpdate()` for complex types that need full control over their structure.

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-14-sending-updates)

## Running the Example

```bash
./mvnw package -pl module-14-sending-updates -q
./mvnw exec:java -pl module-14-sending-updates
```

## Next Module

[Module 15: Agent Requests](/acp-java-sdk/tutorial/15-agent-requests) — read files, write files, and request permissions from the client.
