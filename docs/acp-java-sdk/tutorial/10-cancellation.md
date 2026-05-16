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

// Wait for prompt to finish
promptFuture.join();
System.out.println("Stop reason: " + responseRef.get().stopReason());
```

## How It Works

`client.cancel()` sends a one-way notification (not a request) to the agent. The agent's `cancelHandler` receives it and sets a flag. The prompt handler checks this flag between steps and stops early when cancelled.

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
                return PromptResponse.endTurn();
            }
            context.sendMessage("Step " + i + "/10... ");
            Thread.sleep(500);
        }
        context.sendMessage("All steps completed!");
        return PromptResponse.endTurn();
    })
    .build();
```

Cancellation is cooperative. The agent must check for it — the SDK does not forcefully interrupt handler execution.

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-10-cancellation)

## Running the Example

```bash
./mvnw package -pl module-10-cancellation -q
./mvnw exec:java -pl module-10-cancellation
```

## Next Module

[Module 11: Error Handling](/acp-java-sdk/tutorial/11-error-handling) — handle protocol errors from agents.
