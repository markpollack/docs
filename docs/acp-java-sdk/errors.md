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
| The connection is gone | `AcpConnectionException` | A request still pending when the connection ends, or sent after it ended or after `close()`; see below |
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
0.80.0, when `AcpError` was split out as its own type and the SDK's own local rejections were unified
onto it too. A handler throwing `AcpProtocolException` is now the whole of that type's job: a caller
never catches it, only the `AcpError` the SDK builds from it on the wire.
</Note>

## One base class for every one of these: `AcpException`

`AcpError`, `AcpProtocolException`, `AcpCapabilityException`, `AcpConnectionException`, and
`AcpTimeoutException` all extend `com.agentclientprotocol.sdk.error.AcpException`, so
`catch (AcpException e)` handles every failure of a call in one place, whichever of these it turns out
to be. `AcpError` extending `AcpException` is new: it used to extend `RuntimeException` directly, which
meant `catch (AcpException e)`, the one place the SDK itself documented for handling a call's failures,
silently missed every error the peer actually answered with.

```java
try {
    client.prompt(request);
}
catch (AcpException e) {
    // every failure above lands here: AcpError included, now that it extends AcpException
}
```

<Warning>
**A multi-catch `catch (AcpException | AcpError e)` no longer compiles**: `AcpError` is now a subtype
of `AcpException`, so listing both is redundant, not just unusual. Catch `AcpException` alone. If
separate `catch` blocks are needed for `AcpError` specifically and `AcpException` generally, put the
`AcpError` clause **before** the `AcpException` one, the usual Java rule for a subtype and its
supertype; the other order compiles but the `AcpException` clause now catches `AcpError` too, silently
taking over the more specific block.
</Warning>

`CancellationException` (`java.util.concurrent`) is the one type in the table above that is **not** an
`AcpException`: it's a JDK type reused for interrupt propagation, not an SDK-specific failure.

## What a handler's own exception becomes

Four different outcomes, depending on what the handler throws or lets escape:

1. **`AcpProtocolException`**: sent as the handler intended, code, message and data unchanged. The
   caller's `AcpError` carries exactly what was thrown.
2. **An `AcpError` the handler received from its own call to the peer, left to escape**: passed on
   unchanged, not rewrapped. A handler that calls out, finds nothing of its own to add, and lets the
   failure propagate does not need to convert it: the caller sees the original code, message and data,
   not a flattened `-32603`.
3. **A `CancellationException`, an interrupt, or an `AcpProtocolException` with code `-32800`**: all
   read as the handler cancelling its own work, ACP v1's internal cancellation, and are answered
   `-32800` with the exception's own message (or `"Request cancelled"` if it has none), not flattened
   to `-32603` the way an ordinary exception is. A handler that catches an interrupt from the SDK
   cancelling it and simply lets it propagate already gets the right answer without doing anything
   else.
4. **Anything else** (a bare `RuntimeException`, a bug, an `Error`): answered `-32603` with the
   generic message `"Internal error"` only. **The exception's own message is not sent to the peer**
   (a security fix: a database error, a file path, or a URL with credentials could otherwise reach
   whatever sent the request). The real exception, with its stack trace, is logged at `WARN` on the
   side that handled the request, so it's still visible to whoever runs that side.

```java
@Prompt
PromptResponse prompt(PromptRequest req, SyncPromptContext ctx) {
    if (req.text().isBlank()) {
        throw new AcpProtocolException(AcpErrorCodes.INVALID_PARAMS, "Prompt text must not be blank");
        // (1) the peer sees exactly this: code -32602, this message
    }
    try {
        return callDownstream(req);
    }
    catch (AcpError e) {
        throw e;
        // (2) the peer sees the downstream failure's own code and message, unchanged
    }
    // a CancellationException escaping here (3): the peer sees -32800, the exception's own
    // message or "Request cancelled"; any other exception (4): -32603 "Internal error" only,
    // with the real exception and its stack trace logged at WARN on this side
}
```

Migration: a handler whose exception message the peer genuinely needs to see throws
`AcpProtocolException` with that message explicitly; nothing else but a cancellation carries a message
to the peer anymore.

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
| `-32800` | `REQUEST_CANCELLED` | A request ended via `$/cancel_request`, the cancel grace period, or `maxPromptDuration`; or a handler answered it with a `CancellationException`, an interrupt, or an `AcpProtocolException` of this code itself |

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

## A lost connection: `AcpConnectionException`

A request can fail for a reason that has nothing to do with a JSON-RPC answer, peer-sent or locally
detected, and nothing to do with a timeout either: the connection itself is gone, on either side.

```java
try {
    client.sendExtNotification("_example.com/file_opened", Map.of("path", path));
}
catch (AcpConnectionException e) {
    // the transport is closed: start a new transport and client to go on
}
```

`com.agentclientprotocol.sdk.error.AcpConnectionException` covers every case where a message can't be
carried because the connection is gone, on the client and the agent side alike: a request still
waiting for its answer when the transport ends (`"ACP session with agent terminated"`), and a request
or notification sent after that (`"ACP client transport is not connected: ..."`) or after `close()`
(`"The transport is closed"`). Before 0.80.0 these were a plain `RuntimeException` and an
`IllegalStateException` respectively, so `catch (AcpConnectionException e)` missed the commonest
connection failure, a peer that simply went away. Its cause, when there is one, is why the connection
ended, such as the transport's own failure, or a stdio agent's exit code
(`"ACP agent process exited with code 137 (signal 9)"` from `awaitTermination()`). A closed transport
does not reopen: connect a new transport and client or agent to carry on.

<Note>
Building a client or agent on a transport that refuses to connect or start at once (one already in
use) still throws `IllegalStateException`, not `AcpConnectionException`: that's a misuse of the
transport, not a connection that was once alive and is now lost.
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
It also covers a `session/new`, `session/load`, `session/resume`, or `session/fork` that names
non-empty `additionalDirectories` when the agent doesn't advertise
`sessionCapabilities.additionalDirectories`: check `getAgentCapabilities().supportsAdditionalDirectories()`
before naming any. An agent call works the same way in the other direction for a client capability the
client didn't advertise: `readTextFile`, `writeTextFile`, any of the five terminal methods (`create`,
`output`, `waitForExit`, `kill`, and `release`, all checked as of 0.80.0, not only `create`), or
`createElicitation` for a mode the client didn't announce, covered on
[Agent-to-Client Calls](/docs/acp-java-sdk/agent-to-client-calls) and
[Elicitation](/docs/acp-java-sdk/elicitation).

<Note>
`AcpCapabilityException.toProtocolException()` is removed: it answered `-32600`, a code the SDK made
up for the case, while the one refusal ACP actually specifies (a client asked for an elicitation mode
it never declared) answers `-32602` directly, which the SDK's client already does without this method.
A handler that needs to answer its own capability check as an error throws `AcpProtocolException`
itself: `new AcpProtocolException(AcpErrorCodes.INVALID_PARAMS, e.getMessage(), e.getCapability())`.
</Note>

```java
client.newSession(new NewSessionRequest(cwd));   // IllegalStateException: Call initialize() first
client.initialize();
client.newSession(new NewSessionRequest(cwd));   // fine
```

Every `AcpAsyncClient`/`AcpSyncClient` call but `initialize` itself fails with `IllegalStateException`
("Call initialize() first") until `initialize` has answered; before 0.80.0 it was sent anyway, relying
on the agent to reject it. The check runs when the call is subscribed, not when it's
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
