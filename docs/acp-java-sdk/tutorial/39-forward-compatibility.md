# Module 39: Forward Compatibility and _meta

A newer peer's session updates, content blocks, and stop reasons are kept as `Unknown*` records and open values instead of failing a message. Dispatch with `instanceof` and a default branch, compare open values with `equals`, and carry your own data in `_meta`.

See [Forward Compatibility](/docs/acp-java-sdk/forward-compatibility) for the full catalog of open value types and `Unknown*` variants this module exercises.

## What You'll Learn

- Why no union dispatch in this SDK is exhaustive, and the `instanceof`-chain-plus-default pattern
- Reading and round-tripping an `Unknown*` record exactly as received
- Open value types (`StopReason` and friends): `equals`, `value()`, `known()`, `isKnown()`, never `==`
- `_meta` as the last component of (almost) every schema record, and namespacing your keys
- `acp-test`'s `InMemoryTransportPair`, for exercising forward compatibility without two processes

## The Code

### A "newer" agent, sending variants this SDK doesn't define

An agent built with this SDK can't invent a *protocol* variant the schema doesn't have, but it can model what a proxy or a newer peer would send by constructing the `Unknown*` record directly:

```java
AcpSyncAgent agent = AcpAgent.sync(pair.agentTransport())
    .promptHandler((req, ctx) -> {
        Object trace = req.meta() != null ? req.meta().get(TRACE_KEY) : null;
        // _meta on a session update: the record's last component.
        ctx.sendUpdate(new AcpSchema.AgentMessageChunk("agent_message_chunk",
                new AcpSchema.TextContent("the agent saw prompt _meta " + TRACE_KEY + "=" + trace), null,
                Map.of(TRACE_KEY, trace)));
        ctx.sendUpdate(new AcpSchema.UnknownSessionUpdate("usage_forecast",
                Map.of("tokensLeft", 1200)));
        ctx.sendUpdate(new AcpSchema.AgentMessageChunk(
                new AcpSchema.UnknownContentBlock("hologram", Map.of("frames", 3))));
        return new AcpSchema.PromptResponse(AcpSchema.StopReason.of("paused_for_review"),
                Map.of(TRACE_KEY, trace));
    })
    .build();
```

`StopReason.of("paused_for_review")` is a value this SDK's constants don't list; `of(...)` builds the open value anyway, exactly the way a genuinely newer peer's value would deserialize.

### Dispatch: known types, the `Unknown*` branch, then a default

```java
private static void handle(AcpSchema.SessionNotification notification) {
    AcpSchema.SessionUpdate update = notification.update();
    if (update instanceof AcpSchema.AgentMessageChunk chunk) {
        if (chunk.content() instanceof AcpSchema.TextContent text) {
            System.out.println("message: " + text.text());
        }
        else if (chunk.content() instanceof AcpSchema.UnknownContentBlock block) {
            System.out.println("unknown content block: type '" + block.type() + "', fields " + block.fields());
        }
        else {
            System.out.println("other content: " + chunk.content().getClass().getSimpleName());
        }
    }
    else if (update instanceof AcpSchema.UnknownSessionUpdate unknown) {
        System.out.println("unknown session update kept: '" + unknown.sessionUpdate() + "', fields " + unknown.fields());
    }
    else {
        System.out.println("other update: " + update.getClass().getSimpleName());
    }
}
```

The union interfaces are not sealed, and the SDK targets Java 17, so there's no exhaustive `switch` over them: write `instanceof` chains that end with the `Unknown*` branch and a final `else`. An `Unknown*` record keeps the discriminator and every field it received (`sessionUpdate()`, `fields()` here), and writes them back unchanged; it's how a proxy would pass a newer peer's messages on without understanding them.

`McpServer` defaults to stdio and `AuthMethod` to the agent method for an unrecognized type, rather than having their own `Unknown*` record: worth knowing those two are special cases of the same idea.

### Open values: compare with `equals`, never `==`

```java
AcpSchema.StopReason stop = response.stopReason();
stop.value();                                          // the wire string, even if unrecognized
stop.isKnown();                                        // false for "paused_for_review"
AcpSchema.StopReason.END_TURN.equals(stop);             // false
AcpSchema.StopReason.known();                           // the SDK's own constants, not an exhaustive list
```

`StopReason`, `ToolCallStatus`, `PermissionOptionKind`, `PlanEntryStatus`, `PlanEntryPriority`, `Role`, and `ElicitationAction` all follow this shape: a record over the wire string, with constants for the known values. `ToolKind` is the one exception that stays a plain enum; an unknown kind reads as `OTHER` rather than failing.

### `_meta`: your own data, namespaced

```java
var request = new AcpSchema.PromptRequest(sessionId, List.of(new AcpSchema.TextContent("hello")),
        Map.of("acptutorial.dev/traceId", "trace-42"));
```

Every schema record that carries `_meta` puts it as its **last** component: a free-form map for trace ids, vendor hints, or anything else peers should pass through even when they don't understand it. Namespace your keys (`acptutorial.dev/...` here) so they can't collide with another implementation's.

### Reading and writing raw JSON from a newer peer

```java
String json = "{\"sessionId\":\"s1\",\"update\":{\"sessionUpdate\":\"usage_forecast\","
        + "\"tokensLeft\":1200,\"resetsAt\":\"2026-10-04T00:00:00Z\"}}";
AcpJsonMapper mapper = AcpJsonMapper.createDefault();
AcpSchema.SessionNotification notification = mapper.readValue(json, new TypeRef<AcpSchema.SessionNotification>() {});
notification.update().getClass().getSimpleName(); // UnknownSessionUpdate
String written = mapper.writeValueAsString(notification);
json.equals(written); // true: round-trip fidelity, nothing lost
```

<Note>
This is the practical payoff of forward compatibility: a message this SDK has never seen the shape of still deserializes, dispatches to a safe default branch, and writes back byte-for-byte unchanged if you don't touch it. That's what lets a client built today keep working against an agent speaking a protocol version released after it shipped.
</Note>

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-39-forward-compatibility)

## Running the Example

```bash
./mvnw compile -pl module-39-forward-compatibility -q
./mvnw exec:java -pl module-39-forward-compatibility
```

The demo runs entirely in memory with `acp-test`'s `InMemoryTransportPair`: a "newer" agent sends a session update kind, a content block type, and a stop reason this SDK doesn't define, with `_meta` on the prompt and the response; then a raw JSON notification from a newer peer is read and written back unchanged. No API key, no subprocess required.

## Next Module

[Module 40: Micronaut](/docs/acp-java-sdk/tutorial/40-micronaut): the same annotated agent as a Micronaut bean, served over stdio and Streamable HTTP.
