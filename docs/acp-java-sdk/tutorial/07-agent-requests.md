# Module 07: Agent Requests (Client Side)

Handle file read/write requests from agents on the client side.

## What You'll Learn

- Registering `readTextFileHandler` and `writeTextFileHandler`
- Advertising file system capabilities, derived from the handlers themselves
- The inverted request flow: agents request, clients serve

## Inverted Request Flow

In ACP, the request direction is inverted for file operations compared to traditional client-server: the **agent** requests files from the **client**. This allows agents to access the user's local filesystem through a controlled interface — the client decides which files to expose and how to handle writes.

## The Code

To enable this, the client registers file handlers on its builder. As of 0.80.0, that's enough: the
two handlers below are also what the client advertises, so `initialize()` sends `fs.readTextFile` and
`fs.writeTextFile` because these handlers are registered, with no separate `clientCapabilities(..)`
call needed. When the agent calls `context.readFile()` or `context.writeFile()`, these handlers are
invoked:

```java
AcpSyncClient client = AcpClient.sync(transport)
    .readTextFileHandler(req -> {
        Path path = Path.of(req.path());
        if (!Files.exists(path)) {
            // AcpProtocolException's code and message are the answer the agent gets.
            throw new AcpProtocolException(AcpErrorCodes.RESOURCE_NOT_FOUND,
                    "File not found: " + req.path());
        }
        return new ReadTextFileResponse(Files.readString(path));
    })
    .writeTextFileHandler(req -> {
        Files.writeString(Path.of(req.path()), req.content());
        return new WriteTextFileResponse();
    })
    .sessionUpdateHandler(notification -> { /* handle updates */ })
    .build();

client.initialize();
```

<Note>
As of 0.80.0, `initialize(InitializeRequest)` is removed: capabilities are set only on the client builder, and `initialize()` sends them. See the [0.80.0 migration guide](/docs/acp-java-sdk/migration-0.80).
</Note>

<Warning>
Throw exceptions from handlers for errors; do not return error strings as content. Throw
`AcpProtocolException` with a code from `AcpErrorCodes` (`RESOURCE_NOT_FOUND` above) when the agent
should see the message: its code and message become the answer as they are. Any other exception is
still converted to a JSON-RPC error response, but answered `-32603` with the generic message
"Internal error" only; the real exception's own message is withheld from the agent (it can carry
paths or other details the client shouldn't expose) and logged on the client's own side instead.
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
