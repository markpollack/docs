# Module 09: Session Resume

Load and resume existing sessions.

## What You'll Learn

- Using `client.loadSession()` to resume a session by ID
- `LoadSessionRequest` and `LoadSessionResponse` structure
- Session state persistence across load operations

## How It Works

`loadSession()` tells the agent to resume a previously created session. The agent looks up its stored state for that session ID and restores the conversation context. Whether state actually persists depends on the agent implementation — the demo includes a `StatefulAgent` that stores session history in a `ConcurrentHashMap`.

## The Code

This example creates a session, sends messages to build history, then loads the same session by ID. After loading, the agent has access to the previous conversation context:

```java
// Create a session and send some messages
var session = client.newSession(new NewSessionRequest(".", List.of()));
client.prompt(new PromptRequest(session.sessionId(),
    List.of(new TextContent("Remember: my favorite color is blue."))));

// Later: resume the same session by ID
var loadResponse = client.loadSession(
    new LoadSessionRequest(session.sessionId(), ".", List.of()));

// Continue the conversation with context preserved
client.prompt(new PromptRequest(session.sessionId(),
    List.of(new TextContent("What is my favorite color?"))));
// The agent remembers the previous conversation
```

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-09-session-resume)

## Running the Example

```bash
./mvnw package -pl module-09-session-resume -q
./mvnw exec:java -pl module-09-session-resume
```

## Next Module

[Module 10: Cancellation](/acp-java-sdk/tutorial/10-cancellation) — cancel an in-progress prompt.
