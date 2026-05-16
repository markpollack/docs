# Module 22: Async Agent

The reactive, non-blocking version of Module 12 (Echo Agent).

## What You'll Learn

- `AcpAgent.async()` instead of `AcpAgent.sync()`
- Handlers returning `Mono<T>` instead of `T`
- Chaining `sendMessage()` with `then()` before returning the response
- Agent lifecycle: `start().block()` + `awaitTermination().block()`

## The Code

```java
AcpAsyncAgent agent = AcpAgent.async(transport)
    // Returns Mono<InitializeResponse>
    .initializeHandler(req ->
        Mono.just(InitializeResponse.ok()))

    // Returns Mono<NewSessionResponse>
    .newSessionHandler(req ->
        Mono.just(new NewSessionResponse(
            UUID.randomUUID().toString(), null, null)))

    // Returns Mono<PromptResponse>
    .promptHandler((req, context) -> {
        String text = req.text();

        // sendMessage() returns Mono<Void> — must chain with then()
        return context.sendMessage("Async Echo: " + text)
            .then(Mono.just(PromptResponse.endTurn()));
    })
    .build();

// Start and block until transport closes
agent.start().block();
agent.awaitTermination().block();
```

## Sync vs Async Agent Comparison

| Aspect | `AcpAgent.sync()` | `AcpAgent.async()` |
|--------|-------------------|-------------------|
| Handler return | `T` | `Mono<T>` |
| `sendMessage()` | `void` (blocking) | `Mono<Void>` (must chain) |
| Lifecycle | `agent.run()` | `agent.start().block()` + `awaitTermination().block()` |

The critical difference: in the async agent, `context.sendMessage()` returns `Mono<Void>`. You must chain it with `.then()` before returning the response `Mono`. If you skip the chain, the message won't be sent before the response.

```java
// Wrong — message may not be sent before response
context.sendMessage("text");
return Mono.just(PromptResponse.endTurn());

// Right — message is sent, then response follows
return context.sendMessage("text")
    .then(Mono.just(PromptResponse.endTurn()));
```

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-22-async-agent)

## Running the Example

```bash
./mvnw package -pl module-22-async-agent -q
./mvnw exec:java -pl module-22-async-agent
```

## Key Points

- **No API key** — the async agent runs entirely locally, same as Module 12
- **Same protocol** — sync and async agents are interchangeable from the client's perspective
- **Reactive integration** — async agents work naturally with Project Reactor, R2DBC, and other reactive libraries

## Previous Module

[Module 21: Async Client](/acp-java-sdk/tutorial/21-async-client) — the reactive client API.
