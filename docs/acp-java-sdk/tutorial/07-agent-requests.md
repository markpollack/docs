# Module 07: Agent Requests (Client Side)

Handle file read/write requests from agents on the client side.

## What You'll Learn

- Registering `readTextFileHandler` and `writeTextFileHandler`
- Advertising file system capabilities via `ClientCapabilities`
- The inverted request flow: agents request, clients serve

## Inverted Request Flow

In ACP, the request direction is inverted for file operations compared to traditional client-server: the **agent** requests files from the **client**. This allows agents to access the user's local filesystem through a controlled interface — the client decides which files to expose and how to handle writes.

## The Code

To enable this, the client registers file handlers on its builder and advertises file system capabilities on the same builder. When the agent calls `context.readFile()` or `context.writeFile()`, these handlers are invoked:

```java
AcpSyncClient client = AcpClient.sync(transport)
    .clientCapabilities(new ClientCapabilities(
        new FileSystemCapability(true, true),  // read=true, write=true
        false  // terminalExecution
    ))
    .readTextFileHandler(req -> {
        Path path = Path.of(req.path());
        if (!Files.exists(path)) {
            throw new RuntimeException("File not found: " + req.path());
        }
        return new ReadTextFileResponse(Files.readString(path));
    })
    .writeTextFileHandler(req -> {
        Files.writeString(Path.of(req.path()), req.content());
        return new WriteTextFileResponse();
    })
    .sessionUpdateConsumer(notification -> { /* handle updates */ })
    .build();

client.initialize();
```

<Note>
As of 0.80.0, `initialize(InitializeRequest)` is removed: capabilities are set only on the client builder, and `initialize()` sends them. See the [0.80.0 migration guide](/docs/acp-java-sdk/migration-0.80).
</Note>

<Warning>
Throw exceptions from handlers for errors. The SDK converts exceptions to JSON-RPC error responses. Do not return error strings as content.
</Warning>

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-07-agent-requests)

## Running the Example

Requires the Grok CLI on your `PATH`, signed in once with `grok login`. The module launches it as `grok agent --always-approve stdio`; no API key is needed.

```bash
./mvnw exec:java -pl module-07-agent-requests
```

## Next Module

[Module 08: Permissions](/docs/acp-java-sdk/tutorial/08-permissions) — handle permission requests from agents.
