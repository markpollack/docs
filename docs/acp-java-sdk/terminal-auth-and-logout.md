---
title: "Terminal Auth and Logout"
sidebarTitle: "Auth & Logout"
description: "Interactive terminal authentication, and an agent's logout capability"
---

See the spec's [Authentication](https://agentclientprotocol.com/protocol/v1/authentication) page for
the protocol rules. This page covers the Java types.

## `AuthMethod` is a union

As of 0.80.0, `AuthMethod` is an interface, not a concrete record, with two implementations:

- **`AuthMethodAgent`**: the default; no `type` on the wire. This is also what an unknown method type
  reads as, for forward compatibility.
- **`AuthMethodTerminal(id, name, args, env)`**: an interactive login the **client** runs in a
  terminal on the agent's behalf.

The client advertises that it can run terminal auth with `ClientCapabilities.auth = new
AuthCapabilities(true)`; agents check `NegotiatedCapabilities.supportsTerminalAuth()` before offering
an `AuthMethodTerminal`.

```java
// client: advertise terminal auth support
ClientCapabilities.builder().auth(new AuthCapabilities(true)).build();
```

## The `@Authenticate` handler

An annotated agent can now serve `authenticate`, which previously answered `-32601` (method not
found) unconditionally:

```java
@Authenticate
AuthenticateResponse authenticate(AuthenticateRequest request) {
    // ...
    return new AuthenticateResponse();
}
```

The method takes an optional `AuthenticateRequest` parameter and returns an `AuthenticateResponse`
(or a `Mono` of one, for an async agent). Throw `AcpProtocolException` with
`AcpErrorCodes.AUTHENTICATION_REQUIRED` to reject the attempt.

## Logout

The agent advertises logout support with `AgentCapabilities.auth = AgentAuthCapabilities.withLogout()`.
Clients check `supportsLogout()` (or `requireLogout()`, which throws if the agent didn't advertise it)
before calling `logout(...)`:

```java
// agent: advertise logout
AgentCapabilities.builder().auth(AgentAuthCapabilities.withLogout()).build();

// client
if (negotiated.supportsLogout()) {
    client.logout(new LogoutRequest());
}
```

## Related

<CardGroup cols={2}>
  <Card title="Concepts" icon="compass" href="/docs/acp-java-sdk/concepts">
    Capabilities and NegotiatedCapabilities, which this page assumes
  </Card>
  <Card title="Config Options" icon="sliders" href="/docs/acp-java-sdk/config-options">
    Another capability-gated feature, with the same advertise-then-check pattern
  </Card>
</CardGroup>
