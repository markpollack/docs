---
title: "Errors"
sidebarTitle: "Errors"
description: "Throwing AcpProtocolException in a handler, receiving AcpError as a caller, and the full v1 error code table"
---

The spec's own [error reference](https://agentclientprotocol.com/protocol/v1/schema#errorcode) page
says "Documentation coming soon"; the codes exist only in the schema's `ErrorCode` definition. This
page is where this SDK writes them down.

## The rule

A handler throws `AcpProtocolException` (`com.agentclientprotocol.sdk.error`) to answer a request
with an error; the SDK converts it to a JSON-RPC error response before sending it. Everything else is
what a *caller* sees:

| | Type | When |
|---|---|---|
| A peer's error response, or a response the SDK rejects locally | `AcpError` (`com.agentclientprotocol.sdk.spec`) | Any failed request, for either reason; see below for telling the two apart |
| A request timed out | `AcpTimeoutException` (sync), a plain `TimeoutException` (async) | `requestTimeout` or `promptTimeout` elapsed before an answer arrived |
| The blocked thread was interrupted | `CancellationException` | Sync API only; the interrupt flag is left set |
| The call wasn't something the peer advertised | `AcpCapabilityException` | Capability negotiation ruled it out before anything was sent |
| The call came before `initialize()` answered | `IllegalStateException` | Every call but `initialize` itself; extension calls are exempt |

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
// As a caller: one type covers every failed request
try {
    client.setSessionConfigOption(SetSessionConfigOptionRequest.select(sid, "model", "gpt-99"));
}
catch (AcpError e) {
    System.out.println("rejected: code " + e.getCode() + ": " + e.getMessage());
}
```

<Note>
Some Javadoc on `AcpProtocolException` still shows it being caught after a client call, from before
`AcpError` was split out as its own type ([CL 469]) and before api1 unified the SDK's own local
rejections onto it too. A handler throwing `AcpProtocolException` is now the whole of that type's
job: a caller never catches it, only the `AcpError` the SDK builds from it on the wire.
</Note>

## Telling the peer's error from the SDK's own rejection

`AcpError` covers two different causes, and `getData()` is how to tell them apart. A peer's actual
error response carries the peer's own code, message and data, unchanged. A response the SDK rejected
locally always has code `-32603` (JSON-RPC 2.0 defines no code for an invalid response) and a `data`
map with a `"reason"` and the request's `"method"`:

| `reason` | When |
|---|---|
| `missing-required-field` | A success response was missing a field the ACP schema requires (`"field"` names its path, for example `modes.currentModeId`) |
| `missing-result` | A success response had no `result` at all |
| `unreadable-result` | The `result` couldn't be read as the method's result type |
| `unoffered-option` | `askChoice` was answered with an option id it never offered (`"optionId"` names it) |

```java
try {
    var response = client.prompt(request);
}
catch (AcpError e) {
    if (e.getData() instanceof Map<?, ?> data && "missing-required-field".equals(data.get("reason"))) {
        // "The response to session/prompt lacks the required field stopReason"
    }
}
```

Before 0.80.0, only inbound *params* were checked against the schema's required fields; a peer's `{}`
silently read as a `PromptResponse` with a null `stopReason`. A result is now checked the same way, on
both sides and down into nested records. `AcpError.rejectedResponse(method, reason, message, detail)`
builds the error for the three response-shape reasons above; it's public because the SDK's own two
sides both call it, not for application code to throw (a handler throwing an error uses
`AcpProtocolException` instead, which the SDK never rejects as malformed, since it reads from the
handler's own return value, not off the wire).

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

## Two more exceptions, specific to the sync API

A blocking call (`AcpSyncClient`, `AcpSyncAgent`, `SyncPromptContext`) can also fail with one of two
exceptions that have nothing to do with a JSON-RPC error at all, peer-sent or locally detected:

```java
try {
    var response = client.prompt(request);
}
catch (AcpTimeoutException e) {
    // the request (or, with promptTimeout set, the turn) timed out; e.getCause() is a TimeoutException
}
catch (CancellationException e) {
    // this thread was interrupted while blocked; the interrupt flag is still set
}
```

`com.agentclientprotocol.sdk.error.AcpTimeoutException` (an `AcpException`) replaces what used to
escape as Reactor's internal `Exceptions$ReactiveException`. `java.util.concurrent.CancellationException`
is thrown, with the thread's interrupt flag left set, when a blocked call's thread is interrupted, the
same mechanism the SDK itself uses to cancel a sync handler. The async API doesn't throw either of
these: its `Mono` fails with the plain `TimeoutException` directly.

<Note>
Timeouts and interrupts keep their own types rather than folding into `AcpError`: neither is a
JSON-RPC error at all, peer-sent or locally detected, so there's nothing for `AcpError`'s code and
data to describe.
</Note>

## Two exceptions that mean the request was never sent

`AcpCapabilityException` and `IllegalStateException` both happen *before* a request leaves: capability
negotiation, or connection lifecycle, ruled the call out, so there was nothing to send and nothing to
time out.

```java
try {
    client.closeSession(new CloseSessionRequest(sessionId));
}
catch (AcpCapabilityException e) {
    // "Capability not supported by peer: sessionCapabilities.close" -- e.getCapability()
}
```

A client call other than `initialize` fails locally with `AcpCapabilityException`, naming the
capability, when the agent's `initialize` answer didn't advertise it: `loadSession`, `listSessions`,
`closeSession`, `deleteSession`, `resumeSession`, `forkSession`, `logout`, and the `providers/*` calls.
An agent call works the same way in the other direction for a client capability the client didn't
advertise (`readTextFile`, a terminal method, `createElicitation` for a mode the client didn't
announce), covered on [Agent-to-Client Calls](/docs/acp-java-sdk/agent-to-client-calls) and
[Elicitation](/docs/acp-java-sdk/elicitation). `AcpCapabilityException.toProtocolException()` turns it
into the `-32600` a handler would send for the equivalent case on the wire, for code that needs to
answer a request rather than make one.

```java
client.newSession(new NewSessionRequest(cwd));   // IllegalStateException: Call initialize() first
client.initialize();
client.newSession(new NewSessionRequest(cwd));   // fine
```

Every `AcpAsyncClient`/`AcpSyncClient` call but `initialize` itself fails with `IllegalStateException`
("Call initialize() first") until `initialize` has answered; before 0.80.0's api1 batch it was sent
anyway, relying on the agent to reject it. The check runs when the call is subscribed, not when it's
built, so `client.initialize().then(client.newSession(request))` is fine without waiting for the
first call to complete first. Extension calls (`sendExtRequest`, `sendExtNotification`) are outside
ACP's lifecycle and skip both checks.

## Related

<CardGroup cols={2}>
  <Card title="Forward Compatibility" icon="shield-check" href="/docs/acp-java-sdk/forward-compatibility">
    Open value types and Unknown* variants: the other half of staying safe against a newer peer
  </Card>
  <Card title="Migration Guide" icon="arrow-right-arrow-left" href="/docs/acp-java-sdk/migration-0.80">
    Every error-code renumbering from 0.18.0, in one table
  </Card>
</CardGroup>
