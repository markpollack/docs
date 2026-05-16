# Module 07: Agent Requests (Client Side)

Handle file read/write requests from agents on the client side.

## What You'll Learn

- Registering `readTextFileHandler` and `writeTextFileHandler`
- Advertising file system capabilities via `ClientCapabilities`
- The inverted request flow: agents request, clients serve

## Inverted Request Flow

In ACP, the request direction is inverted for file operations compared to traditional client-server: the **agent** requests files from the **client**. This allows agents to access the user's local filesystem through a controlled interface — the client decides which files to expose and how to handle writes.

## The Code

To enable this, the client registers file handlers on its builder and advertises file system capabilities during initialize. When the agent calls `context.readFile()` or `context.writeFile()`, these handlers are invoked:

```java
AcpSyncClient client = AcpClient.sync(transport)
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

// Advertise file system capabilities
client.initialize(new InitializeRequest(1,
    new ClientCapabilities(
        new FileSystemCapability(true, true),  // read=true, write=true
        false  // terminalExecution
    )));
```

<Warning>
Throw exceptions from handlers for errors. The SDK converts exceptions to JSON-RPC error responses. Do not return error strings as content.
</Warning>

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-07-agent-requests)

## Running the Example

```bash
export GEMINI_API_KEY=your-key-here
./mvnw exec:java -pl module-07-agent-requests
```

## Next Module

[Module 08: Permissions](/acp-java-sdk/tutorial/08-permissions) — handle permission requests from agents.
