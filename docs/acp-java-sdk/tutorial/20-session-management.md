# Module 20: Session Management

List, resume, and close sessions: the full session lifecycle from both sides.

## What You'll Learn

- Enumerating sessions with `session/list`, optionally filtered by working directory
- Reconnecting to a session with `session/resume`, without history replay
- Closing a session with `session/close` to free its resources
- The difference between `resumeSession` and `loadSession` ([Module 09](/docs/acp-java-sdk/tutorial/09-session-resume))

## The Code

### Client: list, resume, close

```java
// Create a few sessions, two in the project directory and one in /tmp
var session1 = client.newSession(new NewSessionRequest(cwd, List.of()));
var session2 = client.newSession(new NewSessionRequest(cwd, List.of()));
var session3 = client.newSession(new NewSessionRequest("/tmp", List.of()));

// List all sessions (null = no cwd filter)
var allSessions = client.listSessions(new ListSessionsRequest(null));
for (var info : allSessions.sessions()) {
    System.out.println(info.sessionId() + " | cwd: " + info.cwd()
        + " | " + info.title() + " | updated: " + info.updatedAt());
}

// List only the sessions in one working directory
var tmpSessions = client.listSessions(new ListSessionsRequest("/tmp"));

// Resume: reconnect without replaying history
var resumed = client.resumeSession(new ResumeSessionRequest(
    session1.sessionId(), cwd, List.of()));

// The session state is still there, so the conversation continues
client.prompt(new PromptRequest(session1.sessionId(),
    List.of(new TextContent("Message after resuming!"))));

// Close: the agent frees the session's resources
client.closeSession(new CloseSessionRequest(session3.sessionId()));
```

### Agent: implement the lifecycle handlers

The agent keeps its own session state. Each lifecycle method has its own handler:

```java
AcpSyncAgent agent = AcpAgent.sync(transport)
    .initializeHandler(req -> InitializeResponse.ok())

    .newSessionHandler(req -> {
        String sessionId = "sess-" + UUID.randomUUID().toString().substring(0, 8);
        sessions.put(sessionId, new SessionState(
            req.cwd(), null, Instant.now(), new ArrayList<>()));
        return new NewSessionResponse(sessionId, null, null);
    })

    // Return SessionInfo metadata, honoring the optional cwd filter
    .listSessionsHandler(req -> {
        List<SessionInfo> infos = new ArrayList<>();
        for (var entry : sessions.entrySet()) {
            SessionState state = entry.getValue();
            if (req.cwd() != null && !req.cwd().equals(state.cwd())) {
                continue;
            }
            infos.add(new SessionInfo(
                entry.getKey(),
                state.cwd(),
                "Session with " + state.messages().size() + " messages",
                state.createdAt().toString(),
                null,
                null));
        }
        return new ListSessionsResponse(infos);
    })

    // Unlike loadSession, resumeSession sends no session/update notifications
    .resumeSessionHandler(req -> {
        sessions.putIfAbsent(req.sessionId(), new SessionState(
            req.cwd(), null, Instant.now(), new ArrayList<>()));
        return new ResumeSessionResponse(null, null);
    })

    .closeSessionHandler(req -> {
        sessions.remove(req.sessionId());
        return new CloseSessionResponse();
    })

    .promptHandler((req, context) -> {
        SessionState state = sessions.get(req.sessionId());
        if (state != null) {
            state.messages().add(req.text());
        }
        context.sendMessage("Active sessions: " + sessions.size() + "\n"
            + "You said: " + req.text() + "\n");
        return PromptResponse.endTurn();
    })
    .build();
```

## Resume vs Load

| | `loadSession` (Module 09) | `resumeSession` (this module) |
|---|---|---|
| History | Replayed to the client as `session/update` notifications | Not replayed |
| Use when | The client needs to rebuild the conversation on screen | The client already has the history, or does not need it |
| Cost | Proportional to the conversation length | Constant |

`session/list`, `session/resume`, and `session/close` were added in SDK 0.12.0.

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-20-session-management)

## Running the Example

```bash
./mvnw package -pl module-20-session-management -q
./mvnw exec:java -pl module-20-session-management
```

The demo launches the agent, creates three sessions, lists them with and without a `cwd` filter, resumes one and keeps talking to it, then closes all three and lists again to show they are gone. No API key required.

## Next Module

[Module 21: Async Client](/docs/acp-java-sdk/tutorial/21-async-client) — use the reactive, non-blocking client API.
