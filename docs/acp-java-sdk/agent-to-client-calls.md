---
title: "Agent-to-Client Calls"
sidebarTitle: "Agent → Client Calls"
description: "Files, terminals, and permission: the requests an agent makes of the client mid-turn, and how a client serves them"
---

Most of ACP flows client-to-agent, but three families of call run the other way, mid-prompt, back
into the client: file access, terminal execution, and permission requests. The agent calls them
exactly like any other request; the client answers them with a handler it registered on its builder.

## File access

```java
// Agent, from a prompt handler
String content = ctx.readFile("src/Main.java");               // convenience: throws if unreadable
Optional<String> maybe = ctx.tryReadFile("src/Main.java");     // convenience: empty if unreadable
ctx.writeFile("output.txt", "generated content");

// The full request/response form, with an offset and line limit
var response = ctx.readTextFile(new ReadTextFileRequest(sessionId, "large-file.txt", 100, 50));
```

```java
// Client
AcpSyncClient client = AcpClient.sync(transport)
    .readTextFileHandler(req -> new ReadTextFileResponse(Files.readString(Path.of(req.path()))))
    .writeTextFileHandler(req -> {
        Files.writeString(Path.of(req.path()), req.content());
        return new WriteTextFileResponse();
    })
    .build();
```

<Warning>
**acp-autoconfig's file capabilities default to `false`.** A Spring Boot client built with the
starter advertises neither `fs.readTextFile` nor `fs.writeTextFile` until you register a handler
with an `AcpClientCustomizer` **and** turn on the matching property
(`spring.acp.client.capabilities.read-text-file`/`write-text-file`). See
[the Boot HTTP page](/docs/acp-java-sdk/autoconfig#enabling-file-access-over-http-or-any-transport).
A handler built with the plain SDK builder, as above, advertises the capability for you from
whether a handler is registered.
</Warning>

The agent checks `NegotiatedCapabilities.supportsReadTextFile()`/`supportsWriteTextFile()` before
calling; calling without the capability throws `AcpCapabilityException` locally, before anything is
sent.

## Terminal execution

A four-step lifecycle, because the client (not the agent) controls what actually runs and may want to
stream output as it happens:

| Step | Agent calls | Client handles | Purpose |
|---|---|---|---|
| 1 | `createTerminal(...)` | `createTerminalHandler` | Spawn the process |
| 2 | `waitForTerminalExit(...)` | `waitForTerminalExitHandler` | Block until it finishes |
| 3 | `getTerminalOutput(...)` | `terminalOutputHandler` | Read accumulated stdout/stderr |
| 4 | `releaseTerminal(...)` | `releaseTerminalHandler` | Free the client's resources |

`killTerminal(...)` ends a still-running terminal early, outside the normal wait-then-release flow.
`ctx.execute(Command)` is a convenience that runs all four steps for the common case: spawn, wait,
read, release, in one call, returning a `CommandResult` (`output()`, `exitCode()`: `Integer`, nullable
as of 0.80.0 for a process a signal terminated, `signal()`, and a `success()` convenience for
`exitCode() == 0`; no more `timedOut()`):

```java
CommandResult result = ctx.execute("ls", "-la");
```

See [Module 18: Terminal Operations](/docs/acp-java-sdk/tutorial/18-terminal-operations) for the full
four-step version and why you'd use it instead of `execute(...)` (streaming output while the command
is still running, for one).

## Permission

```java
// Agent
boolean allowed = ctx.askPermission("Delete files in /tmp?");                       // convenience
String choice = ctx.askChoice("Which format?", "JSON", "XML", "YAML");              // convenience

// Full form
var response = ctx.requestPermission(new RequestPermissionRequest(sessionId, toolCall, options));
```

```java
// Client
.requestPermissionHandler(req -> new RequestPermissionResponse(req.options().getFirst().id()))
```

`PermissionOptionKind` (allow-once, allow-always, reject-once, reject-always, and others) is an open
value, the same discipline as `StopReason`: compare with `.equals(...)`, and keep a default case for a
kind a newer agent might send. See
[Forward Compatibility](/docs/acp-java-sdk/forward-compatibility) for why.

## Related

<CardGroup cols={2}>
  <Card title="Concepts" icon="compass" href="/docs/acp-java-sdk/concepts">
    Capabilities and NegotiatedCapabilities, which every call on this page is gated by
  </Card>
  <Card title="Testing" icon="flask" href="/docs/acp-java-sdk/testing">
    Exercising these calls without a real client or agent process
  </Card>
</CardGroup>
