# Module 11: Error Handling

Handle protocol errors from agents on the client side.

## What You'll Learn

- Catching `AcpError` (`com.agentclientprotocol.sdk.spec.AcpError`)
- Standard error codes in `AcpErrorCodes`
- Throwing `AcpProtocolException` from agent handlers
- Error recovery — continuing after errors

## The Code

ACP uses structured errors based on JSON-RPC error codes. On the **client side**, protocol errors arrive as `AcpError` exceptions. `AcpError` is one type on both sides (`com.agentclientprotocol.sdk.spec.AcpError`), replacing the older `AcpClientSession.AcpError` and `AcpAgentSession.AcpError`. You can inspect the error code to determine what went wrong:

```java
// Client: catch protocol errors
try {
    client.prompt(new PromptRequest(sessionId,
        List.of(new TextContent("this is invalid input"))));
} catch (AcpError e) {
    System.out.println("Code: " + e.getCode());
    System.out.println("Message: " + e.getMessage());
    // Output: Code: -32602
    //         Message: Invalid parameter in prompt: 'this is invalid input'
}
```

On the **agent side**, throw `AcpProtocolException` with a standard error code. The SDK converts it to a JSON-RPC error response:

```java
// Agent: throw protocol errors
.promptHandler((req, context) -> {
    String text = /* extract text from prompt */;

    if (text.contains("invalid")) {
        throw new AcpProtocolException(
            AcpErrorCodes.INVALID_PARAMS,
            "Invalid parameter in prompt: '" + text + "'");
    }

    if (text.contains("internal")) {
        throw new AcpProtocolException(
            AcpErrorCodes.INTERNAL_ERROR,
            "Simulated internal error");
    }

    context.sendMessage("Success! Processed: " + text);
    return PromptResponse.endTurn();
})
```

## Error Codes

`AcpErrorCodes` keeps only the codes the ACP v1 schema defines:

| Code | Constant | When to Use |
|------|----------|-------------|
| `-32602` | `INVALID_PARAMS` | Bad input from client |
| `-32603` | `INTERNAL_ERROR` | Unexpected agent failure |
| `-32600` | `INVALID_REQUEST` | A request invalid in the session's current state, including a second prompt sent while one is already running |
| `-32000` | `AUTHENTICATION_REQUIRED` | Client must authenticate before the agent will do this work |
| `-32002` | `RESOURCE_NOT_FOUND` | Unknown session, file, or other resource |

See the [0.80.0 migration guide](/docs/acp-java-sdk/migration-0.80) if you're carrying forward code that used `SESSION_NOT_FOUND`, `PERMISSION_DENIED`, `CAPABILITY_NOT_SUPPORTED`, `NOT_INITIALIZED`, or `CONCURRENT_PROMPT`: those names and codes changed or were removed.

Agents throw `AcpProtocolException` with one of these codes. The SDK converts it to a JSON-RPC error response. Clients catch it as `AcpError`.

## Error Recovery

Errors do not terminate the connection. After catching an error, the client can continue sending requests on the same session:

```java
// This works — errors don't break the connection
try {
    client.prompt(/* bad input */);
} catch (AcpError e) {
    // handle error
}

// Continue normally
var response = client.prompt(/* good input */);
// Works fine
```

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-11-error-handling)

## Running the Example

```bash
./mvnw package -pl module-11-error-handling -q
./mvnw exec:java -pl module-11-error-handling
```

## Next Module

[Module 12: Echo Agent](/docs/acp-java-sdk/tutorial/12-echo-agent) — build your first agent.
