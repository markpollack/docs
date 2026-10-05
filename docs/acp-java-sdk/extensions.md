---
title: "Extension Methods"
sidebarTitle: "Extensions"
description: "Custom _-prefixed requests and notifications, for functionality the protocol doesn't define"
---

See the spec's [Extensibility](https://agentclientprotocol.com/protocol/v1/extensibility) page for
the protocol rules. This page covers the Java API.

## The rule

A custom method's name must start with `_`. `ExtensionMethods.requireExtension` throws
`IllegalArgumentException` for a name that doesn't, specifically so a custom handler can never
collide with or replace a protocol method.

## Annotated agents: the recommended way in

```java
@ExtRequest("_test/ping")
Pong ping(Ping ping) {
    return new Pong("pong: " + ping.text());
}

@ExtNotification("_test/typed")
void typed(Ping ping) { ... }
```

An extension handler method takes at most one parameter for the extension's own params; it may also
take the connection's `AcpSyncAgent`/`AcpAsyncAgent` and `NegotiatedCapabilities`, like any other
annotated handler (see [Clients and Agents in Java](/docs/acp-java-sdk/clients-and-agents)).

## The builder form

For a client (no annotation model exists for clients), or an agent built with the lower-level
builder API, register handlers directly:

```java
// Typed
AcpAgent.async(transport)
    .extRequestHandler("_example/ping", TypeRef.of(Ping.class), ping -> Mono.just(new Pong(...)))
    .extNotificationHandler("_example/event", TypeRef.of(Event.class), event -> Mono.empty());

// Raw (Map, List, String, Number, or Boolean params)
AcpClient.async(transport)
    .extRequestHandler("_interop/ping", params -> Mono.just(Map.of("pong", 1)));
```

As of 0.80.0, both agent builders' `extRequestHandler` and `extNotificationHandler` also have
agent-aware overloads: a two-argument lambda receives the params and the agent `build()` is about to
return, for a handler that needs to call the client back or send a session update:

```java
AcpSyncAgent agent = AcpAgent.sync(transport)
    .extRequestHandler("_example.com/ask", ASK, (ask, self) ->
        self.sendExtRequest("_example.com/confirm", ask, ANSWER))
    .build();
```

Name the second parameter something other than the local variable the built agent is assigned to
(`self` above), since a lambda parameter can't shadow a local variable in scope.

## Sending, on either side

From a client or agent directly:

```java
client.sendExtRequest("_interop/ping", Map.of("n", 1));
client.sendExtRequest("_interop/ping", Map.of("n", 1), TypeRef.of(PingResult.class));
client.sendExtNotification("_example/event", event);
```

As of 0.80.0, a prompt handler reaches the same calls through `context.client()`, to send an extension
request or notification to the client mid-prompt, without needing a reference to the agent:

```java
context.client().sendExtRequest("_example.com/ping", params, PONG);
context.client().sendExtNotification("_example/event", event);
```

The same methods exist on `AcpAsyncAgent`/`AcpSyncAgent` directly, for calling the client's extension
methods from outside a prompt handler.

## Behavior when nothing handles a method

- An unhandled extension **request** fails with `-32601` (method not found), same as any unhandled
  protocol method.
- An unhandled extension **notification** is silently ignored, since notifications have no response
  to fail.
- A result of `"result": null` completes as an empty `Mono` (async) or `null` (sync).
- A handler that produces genuinely nothing should still answer with an empty map; returning nothing
  at all from a request handler answers `-32603` (internal error), since a request always needs
  *some* result.

## Related

<CardGroup cols={2}>
  <Card title="Forward Compatibility" icon="shield-check" href="/docs/acp-java-sdk/forward-compatibility">
    How unknown methods, variants, and enum values are handled elsewhere in the protocol
  </Card>
  <Card title="Concepts" icon="compass" href="/docs/acp-java-sdk/concepts">
    Client and agent roles, and the rest of the vocabulary this page assumes
  </Card>
</CardGroup>
