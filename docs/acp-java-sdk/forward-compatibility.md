---
title: "Forward Compatibility"
sidebarTitle: "Forward Compat"
description: "Open value types, Unknown* variants, _meta, and the error-code table: how this SDK stays usable against a newer protocol version"
---

ACP evolves by adding new variants and values a client built yesterday has never heard of. 0.80.0
reworks several Java types specifically so that "unrecognized" doesn't mean "crashes."

## Open value types, not enums

`StopReason`, `ToolCallStatus`, `ToolKind`, `PermissionOptionKind`, `PlanEntryStatus`,
`PlanEntryPriority`, and `Role` are now records wrapping a `String`, not Java enums. This means:

| Don't | Do |
|---|---|
| `stopReason == StopReason.END_TURN` | `stopReason.equals(StopReason.END_TURN)` |
| `switch (stopReason)` | `switch (stopReason.value())` (or compare with `.equals(...)`) |
| `StopReason.values()` | `StopReason.known()` |
| `stopReason.name()` | `stopReason.value()` |

A value the running code has never heard of (because the peer speaks a newer protocol version)
still round-trips correctly: it deserializes to the same record type, just holding a string
`.known()` doesn't list. Treating these as enums was never source-compatible with a hypothetical
future protocol version; 0.80.0 makes that explicit in the type itself.

## `Unknown*` variants

Several unions gained an explicit fallback member for a shape the running code doesn't recognize:
`UnknownSessionUpdate`, `UnknownContentBlock`, `UnknownToolCallContent`, `UnknownPermissionOutcome`,
`UnknownSessionConfigOption`, `UnknownElicitationPropertySchema`, `UnknownMultiSelectItems`,
`UnknownAuthMethod` (reading as `AuthMethodAgent`, in that specific case). Deserializing unrecognized
data into a typed fallback, rather than failing the whole message, is what makes it safe to run this
SDK's client against a newer agent (or vice versa) without an immediate crash on day one of some
future protocol version.

**No union in this SDK is sealed.** Any `instanceof` chain over `SessionUpdate`, `ContentBlock`, or
similar must end with the `Unknown*` branch and a default, never assume the listed cases are
exhaustive:

```java
String rendered = switch (update) {
    case AgentMessageChunk c -> renderChunk(c.content());
    case ToolCallUpdate t -> renderToolCall(t);
    case UnknownSessionUpdate u -> ""; // or log u.raw() for diagnostics
    default -> ""; // a variant added after this code was compiled
};
```

## `_meta` everywhere

Nearly every request, response, and notification carries an optional `_meta: Map<String, Object>`
field for implementation-specific extension data. Round-trip it even when you don't understand it:
if you're building a proxy, forwarding `_meta` verbatim is what keeps it useful for the two
specific endpoints that defined it.

## Error codes

0.80.0 aligns every error code with the ACP v1 schema exactly; the previous ad hoc choices are gone.
The spec's own error-code page is thin ("Documentation coming soon"); the schema's `ErrorCode` is the
source of truth, and this table is this SDK's copy of it:

| Code | Name | When |
|---|---|---|
| `-32600` | `INVALID_REQUEST` | A concurrent prompt on a session that already has one active |
| `-32601` | `METHOD_NOT_FOUND` | No handler registered for the method |
| `-32602` | `INVALID_PARAMS` | Malformed or semantically invalid params (e.g. an unadvertised elicitation mode) |
| `-32603` | `INTERNAL_ERROR` | A handler threw, including a bare `Error` escaping a handler |
| `-32002` | `RESOURCE_NOT_FOUND` | Replaces the old `SESSION_NOT_FOUND`; a session, resource, or similar ID that doesn't exist |
| `-32000` | `AUTHENTICATION_REQUIRED` | Replaces the old code of the same name at a different number |
| `-32800` | `REQUEST_CANCELLED` | A request ended via `$/cancel_request`, grace-period expiry, or `maxPromptDuration` |

`AcpError.getCode()` returns the numeric code; `getMessage()` is the peer's message text (plus any
detail from its error data), no longer `[code=N] message`; `toString()` still includes `[code=N]`
for logs. Use `error.toException()` on the receiving side and `JSONRPCError.from(e)` when answering,
rather than hand-building either direction.

## Related

<CardGroup cols={2}>
  <Card title="Concepts" icon="compass" href="/docs/acp-java-sdk/concepts">
    Session updates and the ordering guarantee these open types flow through
  </Card>
  <Card title="Migration Guide" icon="arrow-right-arrow-left" href="/docs/acp-java-sdk/migration-0.80">
    Every error-code and constructor-signature change from 0.18.0, in one table
  </Card>
</CardGroup>
