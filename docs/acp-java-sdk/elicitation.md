---
title: "Elicitation"
sidebarTitle: "Elicitation"
description: "An agent asks the user for structured input or to visit a URL, now a stable part of the protocol"
---

See the spec's [Elicitation](https://agentclientprotocol.com/protocol/v1/elicitation) page for the
form schema and the protocol rules. This page covers the Java API and the mode-checking behavior
that's specific to this SDK.

<Note>
Stable since protocol v1.7.0; `@UnstableAcpApi` was removed from the elicitation types in 0.80.0.
For a worked tutorial example, see [Module 31: Elicitation](/docs/acp-java-sdk/tutorial/31-elicitation).
</Note>

## The two modes

An agent requests either a **form** (structured fields the client renders) or a **URL** (the client
opens a link, and the agent is notified when the user completes it):

```java
agent.createElicitation(CreateElicitationRequest.form(sessionId, "Configure your project:", schema));
agent.createElicitation(CreateElicitationRequest.url(sessionId, "Sign in to continue", elicitationId, url));
// later, for URL mode:
agent.completeElicitation(new CompleteElicitationNotification(elicitationId));
```

The client advertises which modes it handles with the typed capability builders, not the removed
no-argument constructor:

```java
ElicitationCapabilities.formOnly()
ElicitationCapabilities.urlOnly()
ElicitationCapabilities.formAndUrl()
```

## Mode checking is enforced, not just advertised

This is the behavior worth knowing, not just the API shape. If an agent requests a mode the client
never advertised, the call fails with `AcpCapabilityException` before any message is sent. On the
client side, a **typed** `createElicitationHandler` answers a request for an unadvertised mode with
`-32602` (invalid params) without ever invoking the handler. Advertise only the modes your handler
actually implements.

## Responding

```java
var client = AcpClient.sync(transport)
    .createElicitationHandler(req -> {
        // build values from req.requestedSchema()
        return CreateElicitationResponse.accept(values);
        // or CreateElicitationResponse.decline() / .cancel()
    })
    .build();
```

`ElicitationAction` (the outcome: accept, decline, cancel) is an open value, not an enum, as of
0.80.0: compare with `.equals(...)`, never `==`, and see
[Forward compatibility](/docs/acp-java-sdk/forward-compatibility) for why. An unknown property
schema type reads as `UnknownElicitationPropertySchema` rather than failing the message.

## Related

<CardGroup cols={2}>
  <Card title="Module 31: Elicitation" icon="graduation-cap" href="/docs/acp-java-sdk/tutorial/31-elicitation">
    A complete worked example: building a form, handling all three outcomes
  </Card>
  <Card title="Migration Guide" icon="arrow-right-arrow-left" href="/docs/acp-java-sdk/migration-0.80">
    What changed from the unstable 0.18.0 elicitation API
  </Card>
</CardGroup>
