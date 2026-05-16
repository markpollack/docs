# Module 06: Update Types

Comprehensive coverage of all `SessionUpdate` types in ACP.

## What You'll Learn

- All `SessionUpdate` types and when they appear
- Dispatching on update types with `instanceof`
- Building rich UIs that show agent activity

## The Code

The client registers a `sessionUpdateConsumer` and uses `instanceof` to handle each type:

```java
AcpSyncClient client = AcpClient.sync(transport)
    .sessionUpdateConsumer(notification -> {
        SessionUpdate update = notification.update();
        if (update instanceof AgentMessageChunk msg) {
            System.out.print(((TextContent) msg.content()).text());
        } else if (update instanceof AgentThoughtChunk thought) {
            System.out.println("[Thought] " +
                ((TextContent) thought.content()).text());
        } else if (update instanceof ToolCall tc) {
            System.out.println("[Tool] " + tc.title() +
                " | " + tc.kind() + " | " + tc.status());
        } else if (update instanceof ToolCallUpdateNotification tcUpdate) {
            System.out.println("[ToolUpdate] " +
                tcUpdate.toolCallId() + " -> " + tcUpdate.status());
        } else if (update instanceof Plan plan) {
            System.out.println("[Plan] " + plan.entries().size() + " entries:");
            plan.entries().forEach(entry ->
                System.out.println("  - " + entry.content() +
                    " [" + entry.status() + "]"));
        } else if (update instanceof AvailableCommandsUpdate commands) {
            System.out.println("[Commands] " +
                commands.availableCommands().size() + " available");
        } else if (update instanceof CurrentModeUpdate mode) {
            System.out.println("[Mode] " + mode.currentModeId());
        } else if (update instanceof UsageUpdate usage) {
            System.out.printf("[Usage] %d/%d tokens%n", usage.used(), usage.size());
            if (usage.cost() != null) {
                System.out.printf("  Cost: %.4f %s%n",
                    usage.cost().amount(), usage.cost().currency());
            }
        }
    })
    .build();
```

## Update Types Reference

| Type | Content | Typical Use |
|------|---------|-------------|
| `AgentMessageChunk` | Incremental response text | Main output, streamed word by word |
| `AgentThoughtChunk` | Agent's thinking process | Show reasoning in a collapsible panel |
| `ToolCall` | Tool execution start | Show tool name, kind, and status |
| `ToolCallUpdateNotification` | Tool progress | Update status of in-progress tool |
| `Plan` | Agent's planned steps | Show step list with priorities and completion |
| `AvailableCommandsUpdate` | Slash commands | Populate command palette |
| `CurrentModeUpdate` | Mode change | Update UI mode indicator |
| `UsageUpdate` | Token usage and cost | Show context window usage bar (unstable) |

This module extends Module 05 by handling every update type rather than just messages.

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-06-update-types)

## Running the Example

```bash
export GEMINI_API_KEY=your-key-here
./mvnw exec:java -pl module-06-update-types
```

## Next Module

[Module 07: Agent Requests](/acp-java-sdk/tutorial/07-agent-requests) — handle file read/write requests from agents.
