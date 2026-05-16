# Module 15: Agent Requests

Agents can request file operations and permissions from the client.

## What You'll Learn

- Reading files from the client with `context.readFile()`
- Writing files with `context.writeFile()`
- Requesting permissions with `context.requestPermission()`
- The client-side handler pattern for responding to agent requests

## The Agent

The prompt handler uses `SyncPromptContext` convenience methods:

```java
.promptHandler((req, context) -> {
    String sessionId = context.getSessionId();

    // 1. Read a file (convenience method)
    context.sendMessage("Reading pom.xml from your system...\n");
    String content = context.readFile("pom.xml", 0, 10);
    context.sendMessage("File content (first 10 lines):\n" + content + "\n\n");

    // 2. Request permission (full API for complex permissions)
    ToolCallUpdate toolCall = new ToolCallUpdate(
        "tool-write-1", "Create summary.txt",
        ToolKind.EDIT, ToolCallStatus.PENDING,
        null, null, null, null
    );

    List<PermissionOption> options = List.of(
        new PermissionOption("allow", "Allow this once",
            PermissionOptionKind.ALLOW_ONCE),
        new PermissionOption("allow_always", "Always allow",
            PermissionOptionKind.ALLOW_ALWAYS),
        new PermissionOption("deny", "Deny",
            PermissionOptionKind.REJECT_ONCE)
    );

    var permissionResponse = context.requestPermission(
        new RequestPermissionRequest(sessionId, toolCall, options));

    context.sendMessage("Permission: " + permissionResponse.outcome() + "\n");

    // 3. Write a file (convenience method)
    context.writeFile("summary.txt",
        "Created by the FileRequestingAgent.\n");

    context.sendMessage("Successfully wrote summary.txt!\n");
    return PromptResponse.endTurn();
})
```

## The Client

The client registers handlers to respond to agent requests:

```java
AcpSyncClient client = AcpClient.sync(transport)
    .readTextFileHandler(req -> {
        String fileContent = Files.readString(Path.of(req.path()));
        return new ReadTextFileResponse(fileContent);
    })
    .writeTextFileHandler(req -> {
        Files.writeString(Path.of(req.path()), req.content());
        return new WriteTextFileResponse();
    })
    .requestPermissionHandler(req -> {
        // Auto-approve with first option
        return new RequestPermissionResponse(
            req.options().getFirst().id());
    })
    .build();
```

<Warning>
Throw exceptions from handlers for errors. The SDK converts exceptions to JSON-RPC error responses. Do not return error strings as content — agents will misinterpret them as file content.
</Warning>

## Client Capabilities

The client must advertise file system support during initialization:

```java
client.initialize(new InitializeRequest(1,
    new ClientCapabilities(
        new FileSystemCapability(true, true),  // read=true, write=true
        false  // terminalExecution
    )));
```

Agents can check capabilities before using them:

```java
NegotiatedCapabilities caps = context.getClientCapabilities();
if (caps.supportsReadTextFile()) {
    String content = context.readFile("file.txt");
}
```

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-15-agent-requests)

## Running the Example

```bash
./mvnw package -pl module-15-agent-requests -q
./mvnw exec:java -pl module-15-agent-requests
```

## Next Module

[Module 16: In-Memory Testing](/acp-java-sdk/tutorial/16-in-memory-testing) — test agents without subprocess launching.
