# Module 11: Error Handling

Handle protocol errors from agents on the client side.

## What You'll Learn

- Catching `AcpClientSession.AcpError`
- Standard error codes in `AcpErrorCodes`
- Throwing `AcpProtocolException` from agent handlers
- Error recovery — continuing after errors

## The Code

ACP uses structured errors based on JSON-RPC error codes. On the **client side**, protocol errors arrive as `AcpClientSession.AcpError` exceptions. You can inspect the error code to determine what went wrong:

```java
// Client: catch protocol errors
try {
    client.prompt(new PromptRequest(sessionId,
        List.of(new TextContent("this is invalid input"))));
} catch (AcpClientSession.AcpError e) {
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

| Code | Constant | When to Use |
|------|----------|-------------|
| `-32602` | `INVALID_PARAMS` | Bad input from client |
| `-32603` | `INTERNAL_ERROR` | Unexpected agent failure |
| `-32001` | `SESSION_NOT_FOUND` | Unknown session ID |
| `-32002` | `PERMISSION_DENIED` | Client lacks permission |

Agents throw `AcpProtocolException` with one of these codes. The SDK converts it to a JSON-RPC error response. Clients catch it as `AcpClientSession.AcpError`.

## Error Recovery

Errors do not terminate the connection. After catching an error, the client can continue sending requests on the same session:

```java
// This works — errors don't break the connection
try {
    client.prompt(/* bad input */);
} catch (AcpClientSession.AcpError e) {
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

[Module 12: Echo Agent](/acp-java-sdk/tutorial/12-echo-agent) — build your first agent.
