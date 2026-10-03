---
title: "Errors"
sidebarTitle: "Errors"
description: "Throwing AcpProtocolException in a handler, receiving AcpError as a caller, and the full v1 error code table"
---

The spec's own [error reference](https://agentclientprotocol.com/protocol/v1/schema#errorcode) page
says "Documentation coming soon"; the codes exist only in the schema's `ErrorCode` definition. This
page is where this SDK writes them down.

## Two different types, two different directions

| | Type | Where it's used |
|---|---|---|
| **Your handler signals an error** | `AcpProtocolException` (`com.agentclientprotocol.sdk.error`) | Thrown from an agent or client handler; the SDK converts it to a JSON-RPC error response before it's sent |
| **You receive the peer's error** | `AcpError` (`com.agentclientprotocol.sdk.spec`) | The request's `Mono` fails with it (async), or it's thrown from the blocking call (sync) |

```java
// In a handler: signal an error to send back
@SetSessionConfigOption
SetSessionConfigOptionResponse setConfigOption(SetSessionConfigOptionRequest req) {
    if (!knownOptionIds.contains(req.configId())) {
        throw new AcpProtocolException(AcpErrorCodes.INVALID_PARAMS, "Unknown config option: " + req.configId());
    }
    // ...
}
```

```java
// As a caller: receive the peer's error
try {
    client.setSessionConfigOption(SetSessionConfigOptionRequest.select(sid, "model", "gpt-99"));
}
catch (AcpError e) {
    System.out.println("rejected: code " + e.getCode() + ": " + e.getMessage());
}
```

<Note>
Some Javadoc on `AcpProtocolException` still shows it being caught after a client call, from before
`AcpError` was split out as its own type (0.80.0, [CL 469]). Trust the pattern above, verified against
the SDK's own dispatch code (`AcpProtocolException` is thrown only inside handler/dispatch code and
converted to a JSON-RPC response there; a caller always receives `AcpError`), not that Javadoc text.
</Note>

`AcpError.getCode()` returns the numeric code. `getMessage()` is the peer's message text, plus any
detail from the error's data, with the code left out on purpose, so `e.getCode() + " " + e.getMessage()`
names an error exactly once; `toString()` (what a stack trace prints) includes the code.

## The v1 error codes

Every code in 0.80.0 matches the ACP v1 schema exactly; nothing is this SDK's own invention.

| Code | Constant | When |
|---|---|---|
| `-32600` | `INVALID_REQUEST` | A concurrent prompt: `session/prompt` while that session already has one active |
| `-32601` | `METHOD_NOT_FOUND` | No handler registered for the method (protocol or extension) |
| `-32602` | `INVALID_PARAMS` | Malformed or semantically invalid params; the SDK itself throws this for input it can't parse |
| `-32603` | `INTERNAL_ERROR` | A handler threw, including a bare `Error` escaping it, or an annotated handler returned `null` |
| `-32002` | `RESOURCE_NOT_FOUND` | A session, resource, or similar ID that doesn't exist (replaces the old `SESSION_NOT_FOUND`) |
| `-32000` | `AUTHENTICATION_REQUIRED` | The peer must authenticate before this call succeeds |
| `-32800` | `REQUEST_CANCELLED` | A request ended via `$/cancel_request`, the cancel grace period, or `maxPromptDuration` |

All seven live on `AcpErrorCodes` as `int` constants; throw `AcpProtocolException` with one of them
from a handler, and compare `AcpError.getCode()` against them as a caller.

## Converting between the two

```java
JSONRPCError.from(acpProtocolException)   // the wire error for what a handler threw; the SDK uses this internally
jsonRpcError.toException()                 // a JSONRPCError back as an AcpProtocolException, e.g. for a proxy
```

Prefer `JSONRPCError.from(...)` over hand-building a wire error; it's what the SDK's own dispatch code
uses to turn a thrown `AcpProtocolException` into the response it sends. `toException()` is a public
utility with no internal caller of its own, useful if you're building something (a proxy, a bridge)
that needs to re-throw a peer's error using this SDK's exception type rather than `AcpError`.

## Related

<CardGroup cols={2}>
  <Card title="Forward Compatibility" icon="shield-check" href="/docs/acp-java-sdk/forward-compatibility">
    Open value types and Unknown* variants: the other half of staying safe against a newer peer
  </Card>
  <Card title="Migration Guide" icon="arrow-right-arrow-left" href="/docs/acp-java-sdk/migration-0.80">
    Every error-code renumbering from 0.18.0, in one table
  </Card>
</CardGroup>
