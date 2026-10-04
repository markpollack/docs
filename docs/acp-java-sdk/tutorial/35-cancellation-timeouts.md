# Module 35: Cancellation and Timeouts

The two ways to cancel in ACP (`session/cancel` for a prompt turn, `$/cancel_request` for any request), graceful cancellation with `RequestCancellation.cancelWhen`, and the Java SDK's own prompt timeouts: `cancelGracePeriod` and `maxPromptDuration`.

See the spec's [Cancellation](https://agentclientprotocol.com/protocol/v1/cancellation) page for the protocol rules this module builds on.

## What You'll Learn

- Why `session/cancel` doesn't end a turn by itself, and what happens to a prompt sent in between
- `$/cancel_request` as a graceful cancel (`cancelWhen`) versus disposing the request's `Mono`
- `cancelGracePeriod` and `maxPromptDuration`: Java SDK policy, not protocol, and why they exist
- Writing a cooperative handler that checks for cancellation between steps
- Why a client-side request timeout now cancels the turn at a Java agent
- `promptTimeout(Duration)`: the client-side bound a prompt turn needs now that `requestTimeout` no longer provides one

## The Code

### A deterministic agent, driven by the prompt text

```java
AcpSyncAgent agent = AcpAgent.sync(new StdioAcpAgentTransport())
    .cancelGracePeriod(Duration.ofSeconds(1))     // 60s by default
    .maxPromptDuration(Duration.ofSeconds(3))     // off by default
    .cancelHandler(notification -> cancelled.add(notification.sessionId()))
    .promptHandler((req, ctx) -> {
        cancelled.remove(ctx.getSessionId());
        try {
            if (req.text().contains("#slow")) {
                return slow(ctx);       // cooperative: checks for cancellation between ticks
            }
            if (req.text().contains("#stubborn")) {
                return stubborn(ctx);   // ignores session/cancel entirely
            }
            if (req.text().contains("#hang")) {
                Thread.sleep(Duration.ofMinutes(5).toMillis());  // never answers on its own
            }
            ctx.sendMessage("pong");
            return AcpSchema.PromptResponse.endTurn();
        }
        catch (InterruptedException e) {
            // The SDK interrupted this handler: $/cancel_request, the grace period, or
            // maxPromptDuration. It has already answered the prompt; this return is dropped.
            Thread.currentThread().interrupt();
            return new AcpSchema.PromptResponse(AcpSchema.StopReason.CANCELLED);
        }
    })
    .build();
```

`session/cancel` is a notification: the `cancelHandler` runs (here it just records the session id), but the turn is **not** over. It stays active until the cancelled prompt actually answers. A new prompt on that session sent before that happens is rejected with `-32600`.

A cooperative handler checks for cancellation itself and wraps up on its own terms:

```java
private static AcpSchema.PromptResponse slow(SyncPromptContext ctx) throws InterruptedException {
    for (int tick = 1; tick <= 10; tick++) {
        if (cancelled.remove(ctx.getSessionId())) {
            ctx.sendMessage("cancelled after tick " + (tick - 1) + "; wrapping up");
            Thread.sleep(500); // still the active turn: a prompt sent now is rejected
            return new AcpSchema.PromptResponse(AcpSchema.StopReason.CANCELLED);
        }
        ctx.sendMessage("tick " + tick);
        Thread.sleep(200);
    }
    return AcpSchema.PromptResponse.endTurn();
}
```

A handler that ignores `session/cancel` entirely (`stubborn`, above) just keeps running: the SDK's grace period is what eventually ends it.

### Client: `session/cancel`

```java
CompletableFuture<PromptResponse> slow = client.prompt(prompt(sid, "#slow")).toFuture();
// ...wait for a few ticks...

client.cancel(new AcpSchema.CancelNotification(sid)).block();

try {
    client.prompt(prompt(sid, "ping")).block();  // sent before the cancelled turn answered
}
catch (AcpError e) {
    // AcpErrorCodes.INVALID_REQUEST (-32600): the previous turn is still active
}

AcpSchema.PromptResponse answer = slow.get(10, TimeUnit.SECONDS);
// StopReason is an open value: compare with equals, never ==.
boolean cancelled = AcpSchema.StopReason.CANCELLED.equals(answer.stopReason());
```

### Client: `$/cancel_request`, graceful and immediate

```java
// Graceful: the SDK sends $/cancel_request when the trigger completes, but keeps waiting
// for the peer's actual answer.
Mono<Void> twoTicks = Mono.fromFuture(CompletableFuture.runAsync(() -> awaitQuietly(latch)));
try {
    client.prompt(prompt(sid, "#slow"))
            .contextWrite(RequestCancellation.cancelWhen(twoTicks))
            .block(Duration.ofSeconds(10));
}
catch (AcpError e) {
    // AcpErrorCodes.REQUEST_CANCELLED (-32800): the real answer, just a cancelled one
}

// Disposing the Mono (here via .timeout()) also sends $/cancel_request, but returns at once;
// the peer's late answer is discarded.
try {
    client.prompt(prompt(sid2, "#slow")).timeout(Duration.ofMillis(300)).block();
}
catch (RuntimeException e) {
    // the client sees a timeout locally; the agent's eventual answer is dropped
}
```

### `cancelGracePeriod` and `maxPromptDuration`

Neither exists in the protocol; this SDK adds them because the spec requires every cancelled prompt to be answered `cancelled`, and a session allows only one active turn, so a handler that never answers would leave its session busy for good.

```java
client.cancel(new AcpSchema.CancelNotification(sid)).block();
// The "stubborn" handler ignores this. After cancelGracePeriod (1s here, 60s by default),
// the SDK cancels the handler itself (interrupting a sync handler's thread) and answers
// `cancelled` on its behalf.
AcpSchema.PromptResponse answer = stubborn.get(10, TimeUnit.SECONDS);
```

```java
// "#hang" never answers. After maxPromptDuration (3s here, off by default), the SDK answers
// -32800 with data {"maxPromptDuration": "<ISO-8601>"}.
try {
    client.prompt(prompt(sid, "#hang")).block(Duration.ofSeconds(15));
}
catch (AcpError e) {
    System.out.println(e.getError().message() + "; data " + e.getData());
}
```

`Duration.ZERO` turns either off; exactly one answer is ever sent per prompt. Both are also available on `AcpAgentSupport.Builder` for annotated agents.

<Note>
**Document `cancelGracePeriod` and `maxPromptDuration` as SDK policy, not protocol behavior.** No other ACP SDK has an exact equivalent, and the spec defines neither.

Two behavior changes worth knowing if you're upgrading from 0.18.0:

- A client-side request timeout now sends `$/cancel_request`, so it actually cancels the work at a
  Java agent instead of leaving it running after the client gives up.
- **A prompt is no longer bounded by the client's `requestTimeout` at all**, since its answer comes
  only at the end of the turn, however long that takes. To put a bound back, set
  `promptTimeout(Duration)` on the client builder (none by default); it fails the call with a
  `TimeoutException` and sends `$/cancel_request`, the same as a plain `requestTimeout` used to. A
  one-off bound on a single prompt, without changing the client's configuration, still works too:
  `client.prompt(request).timeout(Duration.ofSeconds(5))`.
</Note>

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-35-cancellation-timeouts)

## Running the Example

```bash
./mvnw package -pl module-35-cancellation-timeouts -q
./mvnw exec:java -pl module-35-cancellation-timeouts
```

The demo runs all four scenarios with short timeouts (1s grace period, 3s max duration) so it finishes in a few seconds. No API key required.

## Next Module

[Module 36: Terminal Auth and Logout](/docs/acp-java-sdk/tutorial/36-terminal-auth-logout): an agent that requires sign-in, with two auth methods and a logout capability.
