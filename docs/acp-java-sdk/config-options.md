---
title: "Session Config Options"
sidebarTitle: "Config Options"
description: "The general mechanism that replaces session/set_model: declaring, reading, and changing agent-exposed session settings"
---

See the spec's [Session Config Options](https://agentclientprotocol.com/protocol/v1/session-config-options)
page for the protocol rules; this page covers the Java types and the decisions the spec leaves open.

## Why this replaced `session/set_model`

A dedicated model-selection method turned out to be too narrow: agents wanted selectors for
reasoning effort, variants, and other settings too, and each new hard-coded method would leave the
protocol carrying methods nobody uses once agents move past them. So ACP lets an agent declare its
own selectors, each with an ID and an optional semantic category, and model choice becomes just one
selector with `category: "model"`. `session/set_model`, `SetSessionModelRequest`/`Response`,
`SessionModelState`, `ModelInfo`, and `@SetSessionModel` are removed entirely in 0.80.0; see the
[migration guide](/docs/acp-java-sdk/migration-0.80) if you're upgrading.

## The types

A config option is one of two kinds, both exposed through `AcpSchema`:

- **`SessionConfigSelect`**: a choice from a fixed set of options.
- **`SessionConfigBoolean`**: an on/off switch.

Build a model picker with the dedicated factory:

```java
var model = SessionConfigSelect.model("model", "Model", "model-a", List.of(
    new SessionConfigSelectOption("model-a", "Model A"),
    new SessionConfigSelectOption("model-b", "Model B")));
```

For anything else, use the builders:

```java
var effort = SessionConfigSelect.builder()
    .id("effort").name("Effort").category(SessionConfigOptionCategory.THOUGHT_LEVEL)
    .currentValue("effort-low")
    .groups(List.of(new SessionConfigSelectGroup("fast", "Fast",
        List.of(new SessionConfigSelectOption("effort-low", "Low")))))
    .build();

var verbose = SessionConfigBoolean.builder()
    .id("verbose").name("Verbose").currentValue(false)
    .build();
```

`build()` throws `IllegalStateException` naming the first missing required field. `options()` on a
select can be flat (`List<SessionConfigSelectOption>`) or grouped
(`List<SessionConfigSelectGroup>`); `SessionConfigSelectOptions.allOptions()` flattens either shape,
which is what most code should call rather than branching on `UngroupedSelectOptions` vs
`GroupedSelectOptions` directly.

`AcpSchema.SessionConfigOptionCategory` holds the categories the protocol reserves, as plain
`String` constants: `MODE`, `MODEL`, `MODEL_CONFIG`, `THOUGHT_LEVEL`. `category` is a free string,
not a closed enum: a custom category is allowed as long as it starts with `_`, and clients must
tolerate a missing or unrecognized one. In Java, always write the reserved categories through the
`SessionConfigOptionCategory` constants rather than string literals.

## Advertising config options

The agent lists the full set on `NewSessionResponse`, `LoadSessionResponse`, and
`ResumeSessionResponse`:

```java
new NewSessionResponse(sessionId, null, List.of(model, effort, verbose));  // (id, modes, configOptions)
```

Boolean options are stable, but only send one to a client that advertised support for them
(`clientCapabilities.session.configOptions.boolean`, spelled in Java as
`ClientSessionCapabilities.withBooleanConfigOptions()`). The SDK does not filter this for you:
check the connection's `NegotiatedCapabilities.supportsBooleanConfigOptions()` yourself before
including a boolean option.

```java
// client, advertising boolean config-option support
AcpSyncClient client = AcpClient.sync(transport)
    .clientCapabilities(ClientCapabilities.builder()
        .session(ClientSessionCapabilities.withBooleanConfigOptions())
        .build())
    .build();
client.initialize();
```

## Changing an option

The client calls `setSessionConfigOption`; the agent's handler returns the **complete** new list,
not a delta:

```java
// client
client.setSessionConfigOption(SetSessionConfigOptionRequest.select(sessionId, "model", "model-b"));
client.setSessionConfigOption(SetSessionConfigOptionRequest.bool(sessionId, "verbose", true));
```

```java
// agent, annotated
@SetSessionConfigOption
SetSessionConfigOptionResponse setConfigOption(SetSessionConfigOptionRequest req) {
    return new SetSessionConfigOptionResponse(fullOptionsList);
}
```

The builder form is the same handler under a different name:
`.setSessionConfigOptionHandler(req -> new SetSessionConfigOptionResponse(fullOptionsList))`.

`req.value()` is untyped (`Object`): a `String` for a select, a `Boolean` for a boolean.
`req.type()` is `null` for a select and `"boolean"` for a boolean, so dispatch on `req.configId()`
and check with `instanceof` rather than trusting `type()` to disambiguate. The SDK validates none of
this: a bad option ID, a value not on offer, or a value of the wrong type all reach the handler as
sent. The spec defines no error for these cases either; the natural answer, and what this page
recommends, is `-32602` (Invalid params):

```java
if (!knownOptionIds.contains(req.configId())) {
    throw new AcpProtocolException(AcpErrorCodes.INVALID_PARAMS, "Unknown config option: " + req.configId());
}
```

The same applies to a boolean option set by a client that never advertised boolean support: treat
the ID as unknown and answer `-32602`, the same as any option you didn't offer that client.

## When the agent sends `ConfigOptionUpdate`

Send a `ConfigOptionUpdate` session update when **the agent itself** changes an option, for example
switching a mode after planning, falling back to a different model after a rate limit, or exposing
an option that depends on discovered context. It always carries the full, current list:

```java
context.sendUpdate(sessionId, new ConfigOptionUpdate(fullOptionsList));
```

The spec is silent on whether the agent should *also* send an update after a **client-initiated**
change. Since `SetSessionConfigOptionResponse` already carries the complete new state, don't send a
redundant `ConfigOptionUpdate` for that case.

## Relationship to session modes

Config options supersede `session/set_mode`, but not yet: the spec says modes will be removed in a
future protocol version, and during the transition an agent with mode-like settings should send
**both** a `category: "mode"` config option and the separate `modes` field, while a client that
supports config options should prefer them and ignore `modes`. `session/set_mode` stays in the SDK
for now; don't remove it just because config options exist.

## Related

<CardGroup cols={2}>
  <Card title="Concepts" icon="compass" href="/docs/acp-java-sdk/concepts">
    Capabilities, sessions, and the rest of the vocabulary this page assumes
  </Card>
  <Card title="Migration Guide" icon="arrow-right-arrow-left" href="/docs/acp-java-sdk/migration-0.80">
    Every breaking change from 0.18.0, including the full session/set_model removal
  </Card>
</CardGroup>
