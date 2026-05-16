# Module 03: Sessions

Understanding session creation and lifecycle in ACP.

## What You'll Learn

- Creating sessions with `NewSessionRequest`
- Working directory context and context documents
- Multiple independent sessions

## How Sessions Work

Sessions are workspaces for conversations. Each session has a unique ID assigned by the agent, a working directory context, and its own conversation history. Multiple sessions on the same connection are fully independent.

## The Code

After initializing (Module 01/02), the next step is creating a session. `NewSessionRequest` takes a working directory path and an optional list of MCP server configs. The agent returns a session ID that you use for all subsequent prompts:

```java
// Create a session with working directory context
var session = client.newSession(
    new NewSessionRequest("/workspace", List.of()));

System.out.println("Session ID: " + session.sessionId());
// Output: Session ID: 53d1a1ee-c7eb-4500-b25c-7bc2fdffa0e4
```

You can create multiple sessions on the same connection. Each maintains its own conversation history — prompts in one session don't affect the other:

```java
var session1 = client.newSession(new NewSessionRequest("/project-a", List.of()));
var session2 = client.newSession(new NewSessionRequest("/project-b", List.of()));

// Prompts in session1 don't affect session2
client.prompt(new PromptRequest(session1.sessionId(),
    List.of(new TextContent("Analyze this project"))));
```

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-03-sessions)

## Running the Example

```bash
export GEMINI_API_KEY=your-key-here
./mvnw exec:java -pl module-03-sessions
```

## Next Module

[Module 04: Prompts](/acp-java-sdk/tutorial/04-prompts) — prompt requests and response handling in depth.
