# Module 08: Permissions

Handle permission requests from agents on the client side.

## What You'll Learn

- Registering a `requestPermissionHandler`
- `PermissionOption` and `PermissionOptionKind` types
- Permission outcomes: selected vs cancelled

## The Code

When an agent wants to perform a sensitive operation (like writing a file or running a command), it can ask the client for permission first. The client registers a `requestPermissionHandler` that receives the request details and a list of options (allow once, allow always, reject). Your handler decides which option to select — typically by showing a dialog to the user:

```java
AcpSyncClient client = AcpClient.sync(transport)
    .requestPermissionHandler(req -> {
        System.out.println("Agent wants to: " + req.toolCall().title());
        System.out.println("Options:");
        for (var option : req.options()) {
            System.out.println("  " + option.id() + ": " +
                option.name() + " (" + option.kind() + ")");
        }
        // Auto-approve with first option
        return new RequestPermissionResponse(
            req.options().getFirst().id());
    })
    .readTextFileHandler(req -> /* file handler */)
    .writeTextFileHandler(req -> /* file handler */)
    .build();
```

## Permission Option Kinds

| Kind | Description |
|------|-------------|
| `ALLOW_ONCE` | Allow this specific operation |
| `ALLOW_ALWAYS` | Allow all similar operations |
| `REJECT_ONCE` | Deny this specific operation |
| `REJECT_ALWAYS` | Deny all similar operations |

The agent sends a `RequestPermissionRequest` containing the tool call details and a list of options. The client presents choices to the user and returns the selected option ID. This completes the bidirectional request flow (with Module 07 for files).

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-08-permissions)

## Running the Example

```bash
export GEMINI_API_KEY=your-key-here
./mvnw exec:java -pl module-08-permissions
```

## Next Module

[Module 09: Session Resume](/acp-java-sdk/tutorial/09-session-resume) — load and resume existing sessions.
