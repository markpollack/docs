# Module 21: Async Client

The reactive, non-blocking version of Module 01.

## What You'll Learn

- `AcpClient.async()` instead of `AcpClient.sync()`
- Chaining operations with `Mono` and `flatMap`
- Async session update consumers returning `Mono<Void>`
- When to use async vs sync

## The Code

```java
// Build async client — note AcpAsyncClient return type
AcpAsyncClient client = AcpClient.async(transport)
    .sessionUpdateConsumer(notification -> {
        // Async consumer must return Mono<Void>
        var update = notification.update();
        if (update instanceof AgentMessageChunk msg) {
            if (msg.content() instanceof TextContent text) {
                System.out.print(text.text());
            }
        }
        return Mono.empty();
    })
    .build();

// Chain operations reactively with flatMap
client.initialize()
    .flatMap(init -> client.newSession(
        new NewSessionRequest(".", List.of())))
    .flatMap(session -> client.prompt(
        new PromptRequest(session.sessionId(),
            List.of(new TextContent("What is 2+2?")))))
    .flatMap(response -> client.closeGracefully())
    .subscribe(
        unused -> {},
        error -> System.err.println("Error: " + error.getMessage()),
        () -> System.out.println("Done!")
    );
```

## Sync vs Async Comparison

| Aspect | `AcpClient.sync()` | `AcpClient.async()` |
|--------|--------------------|--------------------|
| Return type | `T` | `Mono<T>` |
| Chaining | Sequential statements | `flatMap` |
| Update consumer | `void` | `Mono<Void>` |
| Blocking | Yes | No (unless you call `block()`) |

The async client wraps every operation in Project Reactor's `Mono`. If you're already using a reactive framework, the async client integrates naturally. For CLI tools and scripts, the sync client is simpler.

## Alternative: block()

For scripts where you want async types but don't care about non-blocking I/O:

```java
var init = client.initialize().block();
var session = client.newSession(new NewSessionRequest(".", List.of())).block();
var response = client.prompt(new PromptRequest(
    session.sessionId(),
    List.of(new TextContent("Hello")))).block();
client.closeGracefully().block();
```

This defeats the purpose of async but can be useful during prototyping.

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-21-async-client)

## Running the Example

```bash
export GEMINI_API_KEY=your-key-here
./mvnw compile exec:java -pl module-21-async-client
```

## Next Module

[Module 22: Async Agent](/acp-java-sdk/tutorial/22-async-agent) — build an agent with reactive handlers.
