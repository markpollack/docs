# Module 13: Agent Handlers

Implement all handler types that an ACP agent can provide.

## What You'll Learn

- All five handler types: initialize, newSession, loadSession, prompt, cancel
- Session tracking with `ConcurrentHashMap`
- Logging to stderr (stdout is reserved for the protocol)

## The Code

An ACP agent has five handler types. Three are required (`initialize`, `newSession`, `prompt`) and two are optional (`loadSession`, `cancel`). This example shows all five wired up with the sync builder API. Note that `stdout` is reserved for the JSON-RPC protocol — agent logging goes to `stderr`:

```java
import com.agentclientprotocol.sdk.agent.*;
import com.agentclientprotocol.sdk.agent.transport.*;
import com.agentclientprotocol.sdk.spec.AcpSchema.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

var sessions = new ConcurrentHashMap<String, String>();
var transport = new StdioAcpAgentTransport();

AcpSyncAgent agent = AcpAgent.sync(transport)

    .initializeHandler(req -> {
        System.err.println("Protocol version: " + req.protocolVersion());
        return InitializeResponse.ok();
    })

    .newSessionHandler(req -> {
        String sessionId = UUID.randomUUID().toString();
        sessions.put(sessionId, req.cwd());
        System.err.println("New session: " + sessionId);
        return new NewSessionResponse(sessionId, null, null);
    })

    .loadSessionHandler(req -> {
        System.err.println("Loading session: " + req.sessionId());
        return new LoadSessionResponse(List.of(), List.of());
    })

    .promptHandler((req, context) -> {
        context.sendMessage("Received: " + req.text());
        return PromptResponse.endTurn();
    })

    .cancelHandler(notification -> {
        System.err.println("Cancel requested for: " +
            notification.sessionId());
    })

    .build();

agent.run();
```

## Handler Reference

| Handler | Method | Required | Description |
|---------|--------|----------|-------------|
| `initializeHandler` | `initialize` | Yes | Protocol handshake, capability exchange |
| `newSessionHandler` | `session/new` | Yes | Create session with working directory |
| `loadSessionHandler` | `session/load` | No | Resume an existing session by ID |
| `promptHandler` | `session/prompt` | Yes | Process user prompts |
| `cancelHandler` | `session/cancel` | No | Handle cancellation (fire-and-forget notification) |

The `cancelHandler` receives a `CancelNotification`, not a request — it has no response. This is the JSON-RPC notification pattern: the client sends it and does not expect a reply.

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-13-agent-handlers)

## Running the Example

```bash
./mvnw package -pl module-13-agent-handlers -q
./mvnw exec:java -pl module-13-agent-handlers
```

## Next Module

[Module 14: Sending Updates](/acp-java-sdk/tutorial/14-sending-updates) — send all types of session updates to clients.
