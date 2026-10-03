---
title: "Testing"
sidebarTitle: "Testing"
description: "acp-test: InMemoryTransportPair, MockAcpAgent, MockAcpClient, and the deterministic-agent pattern behind the new 0.80.0 tutorial modules"
---

`acp-test` gives you a client and an agent that talk to each other without a subprocess, a socket, or
a real LLM in the loop, so unit-style tests (and several tutorial modules) run in milliseconds and
produce the same result every time.

## `InMemoryTransportPair`: two transports, no process

```java
var pair = InMemoryTransportPair.create();
AcpAsyncClient client = ... AcpClient.async(pair.clientTransport()) ...
AcpAsyncAgent agent = ... AcpAgent.async(pair.agentTransport()) ...
```

`clientTransport()` and `agentTransport()` are linked in memory: whatever one side sends, the other
receives, with no serialization round trip and no network or process boundary. This is what
[Module 39](/docs/acp-java-sdk/tutorial/39-forward-compatibility) uses to run a "newer" agent against
a real client in the same JVM.

## `MockAcpAgent`: for testing a client

```java
MockAcpAgent mockAgent = MockAcpAgent.builder(pair.agentTransport())
    .initializeResponse(new InitializeResponse(1, new AgentCapabilities(), List.of()))
    .promptResponse(request -> new PromptResponse(StopReason.END_TURN))
    .build();
mockAgent.start();

// ...exercise your client against pair.clientTransport()...

mockAgent.expectPrompts(1);
mockAgent.awaitPrompts(Duration.ofSeconds(5));
assertThat(mockAgent.getReceivedPrompts()).hasSize(1);
mockAgent.close();
```

Every request it receives is recorded: `getReceivedInitRequests()`, `getReceivedNewSessionRequests()`,
`getReceivedPrompts()`, `getReceivedCancellations()`. `expectPrompts(n)` plus `awaitPrompts(timeout)`
is the pattern for waiting on an async interaction before asserting, rather than polling or sleeping.
`sendSessionUpdate(sessionId, update)` pushes an update from the mock at a time you choose, for
testing how a client handles updates arriving mid-turn. `createDefault(transport)` builds one with
reasonable defaults when you don't need to customize responses.

## `MockAcpClient`: for testing an agent

```java
MockAcpClient mockClient = MockAcpClient.builder(pair.clientTransport())
    .fileContent("NOTES.md", "- [ ] write docs")
    .permissionResponse(req -> new RequestPermissionResponse(req.options().getFirst().id()))
    .build();

mockClient.initialize();
String sessionId = mockClient.newSession(cwd).sessionId();
PromptResponse response = mockClient.prompt("hello");
```

Convenience methods (`initialize()`, `newSession(cwd)`, `prompt(text)`) skip the request-object
boilerplate for the common case; `getReceivedUpdates()`,
`getReceivedPermissionRequests()`/`getReceivedFileReadRequests()`/`getReceivedFileWriteRequests()`
record what your agent asked for, the same recording pattern as `MockAcpAgent`.

## The directive-driven deterministic agent pattern

For a scenario more elaborate than one canned response, give the mock agent's prompt handler a small
language of its own, driven by the prompt text, so the same test agent can exercise many behaviors
deterministically. [Module 35](/docs/acp-java-sdk/tutorial/35-cancellation-timeouts)'s agent is a
tutorial-scale example: `#slow` ticks and checks for cancellation, `#stubborn` ignores
`session/cancel`, `#hang` never answers, anything else answers immediately.

The SDK's own cross-SDK interop suite takes this further with directives like `#permission allow`,
`#emit <update>`, `#elicit form|url`, `#ext request|notify`, `#config grouped`, `#terminal run`,
`#fs`, `#meta`, run over all three transports. It's test code, not a published artifact, so a project
either builds it from the SDK repository or copies the pattern (a directive-driven agent written into
the project's own tests). Both this SDK's approach and the Rust SDK's equivalent (`Testy`, its
deterministic test agent) follow the same idea: a small set of text directives standing in for an
LLM, so client and tutorial code can demonstrate cancellation, elicitation, and permission flows
without one.

## Related

<CardGroup cols={2}>
  <Card title="Cancellation" icon="ban" href="/docs/acp-java-sdk/cancellation">
    The #slow/#stubborn/#hang pattern this page's deterministic-agent section is based on
  </Card>
  <Card title="Module 16: In-Memory Testing" icon="graduation-cap" href="/docs/acp-java-sdk/tutorial/16-in-memory-testing">
    A full worked tutorial module built on InMemoryTransportPair
  </Card>
</CardGroup>
