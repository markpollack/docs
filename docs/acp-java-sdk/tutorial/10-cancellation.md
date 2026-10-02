# Module 10: Cancellation

Cancel an in-progress prompt from the client side.

## What You'll Learn

- Sending `CancelNotification` to interrupt a running prompt
- Running prompts in background threads
- How cancellation affects `StopReason`

## The Code

```java
// Run prompt in a background thread
AtomicReference<PromptResponse> responseRef = new AtomicReference<>();
CompletableFuture<Void> promptFuture = CompletableFuture.runAsync(() -> {
    var response = client.prompt(new PromptRequest(
        sessionId,
        List.of(new TextContent("Do a long task"))));
    responseRef.set(response);
});

// Wait, then cancel
Thread.sleep(1500);
client.cancel(new CancelNotification(sessionId));

// Wait for the cancelled prompt to answer: that ends the turn, and only
// then may the client send another prompt on this session
promptFuture.join();
System.out.println("Stop reason: " + responseRef.get().stopReason());
// Output: Stop reason: cancelled
```

## How It Works

`client.cancel()` sends a one-way notification (not a request) to the agent. The agent's `cancelHandler` receives it and sets a flag. The prompt handler checks this flag between steps and stops early when cancelled.

**`session/cancel` does not end the prompt turn by itself.** The turn ends only when the agent answers the cancelled `session/prompt`, and ACP v1 requires that answer to carry stop reason `cancelled`. Until then the session is still busy: a new prompt sent on it is rejected with `-32600` (invalid request), the same as any prompt sent while another is already running. If a handler never answers, the SDK answers `cancelled` for it after a grace period (60 seconds by default, set with `cancelGracePeriod` on the agent builder).

On the agent side:

```java
// Track cancellation per session
Map<String, Boolean> cancelledSessions = new ConcurrentHashMap<>();

AcpSyncAgent agent = AcpAgent.sync(transport)
    .cancelHandler(notification -> {
        // Set flag — no response needed (notification, not request)
        cancelledSessions.put(notification.sessionId(), true);
    })
    .promptHandler((req, context) -> {
        cancelledSessions.put(req.sessionId(), false);

        for (int i = 1; i <= 10; i++) {
            // Check flag before each step
            if (cancelledSessions.getOrDefault(req.sessionId(), false)) {
                context.sendMessage("[Cancelled at step " + i + "]");
                // Answer the cancelled prompt with CANCELLED: this ends the turn
                return new PromptResponse(StopReason.CANCELLED);
            }
            context.sendMessage("Step " + i + "/10... ");
            Thread.sleep(500);
        }
        context.sendMessage("All steps completed!");
        return PromptResponse.endTurn();
    })
    .build();
```

Cancellation is cooperative: the agent must check for it, since the SDK does not forcefully interrupt handler execution. But answering is not optional: a handler that reaches the cancelled branch must return `StopReason.CANCELLED`, not the ordinary `PromptResponse.endTurn()`, so the turn actually ends.

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-10-cancellation)

## Running the Example

```bash
./mvnw package -pl module-10-cancellation -q
./mvnw exec:java -pl module-10-cancellation
```

## Next Module

[Module 11: Error Handling](/docs/acp-java-sdk/tutorial/11-error-handling) — handle protocol errors from agents.
