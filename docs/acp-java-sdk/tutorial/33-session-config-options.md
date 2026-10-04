# Module 33: Session Config Options

Expose per-session settings (a model picker, a mode, and a capability-gated boolean) as session config options, change them with `session/set_config_option`, and push an agent-initiated change with a `config_option_update`. One agent, written twice: builder API and annotations.

## What You'll Learn

- Building a model picker with `SessionConfigSelect.model(...)`, and a categorized select with `SessionConfigSelect.builder()`
- Offering a `SessionConfigBoolean` only to clients that advertised support for it
- Returning the full option list from `session/new` and every subsequent change, never a delta
- Sending `ConfigOptionUpdate` only when the agent changes a setting itself
- Rejecting a bad request with `-32602`, since the SDK validates nothing about a `set_config_option` call
- Keeping legacy `session/set_mode` in step with a `category: "mode"` config option
- Dispatching option types with `instanceof` and an `UnknownSessionConfigOption` branch

## The Code

### Declaring the options

Three options, one state object shared by both agent variants below. The model picker uses the dedicated factory; the mode select and the boolean use the builders:

```java
// A grouped select with category "model": clients recognize it as the model picker.
var model = AcpSchema.SessionConfigSelect.model(MODEL, "Model", state.model,
        new AcpSchema.GroupedSelectOptions(List.of(
                new AcpSchema.SessionConfigSelectGroup("hosted", "Hosted", List.of(
                        new AcpSchema.SessionConfigSelectOption("orbit-1-mini", "Orbit 1 Mini"),
                        new AcpSchema.SessionConfigSelectOption("orbit-1", "Orbit 1"),
                        new AcpSchema.SessionConfigSelectOption(PREVIEW_MODEL, "Orbit 2 (preview)"))),
                new AcpSchema.SessionConfigSelectGroup("local", "Local", List.of(
                        new AcpSchema.SessionConfigSelectOption("local-7b", "Local 7B"))))));

// Any other categorized select: the builder. Category "mode" marks the successor of session modes.
var mode = AcpSchema.SessionConfigSelect.builder()
        .id(MODE).name("Mode").category(AcpSchema.SessionConfigOptionCategory.MODE)
        .currentValue(state.mode)
        .options(List.of(
                new AcpSchema.SessionConfigSelectOption("ask", "Ask"),
                new AcpSchema.SessionConfigSelectOption("code", "Code")))
        .build();

List<AcpSchema.SessionConfigOption> all = new ArrayList<>(List.of(model, mode));
if (state.booleansSupported) {
    // Boolean options go only to clients that advertised session.configOptions.boolean.
    all.add(AcpSchema.SessionConfigBoolean.builder()
            .id(VERBOSE).name("Verbose answers").description("Explain each step in the answer")
            .currentValue(state.verbose)
            .build());
}
```

The SDK does not filter the boolean option for you: the agent checks the client's advertised capabilities itself, once, at `session/new`.

### Annotated agent

```java
@NewSession
AcpSchema.NewSessionResponse newSession(AcpSchema.NewSessionRequest req, NegotiatedCapabilities clientCaps) {
    String sessionId = UUID.randomUUID().toString();
    List<AcpSchema.SessionConfigOption> options = settings.open(sessionId, clientCaps.supportsBooleanConfigOptions());
    return new AcpSchema.NewSessionResponse(sessionId, settings.modes(sessionId), options);
}

@Prompt
AcpSchema.PromptResponse prompt(AcpSchema.PromptRequest req, @SessionId String sessionId,
        SyncPromptContext ctx, AcpSyncAgent agent) {
    List<AcpSchema.SessionConfigOption> changed = settings.fallBackIfRateLimited(sessionId);
    if (changed != null) {
        // Agent-initiated change: push the full list, here through the connection's agent.
        agent.sendSessionUpdate(sessionId, new AcpSchema.ConfigOptionUpdate(changed));
    }
    ctx.sendMessage(settings.answer(sessionId, "annotated agent"));
    return AcpSchema.PromptResponse.endTurn();
}
```

Any handler, not only `@Prompt`, may declare `NegotiatedCapabilities` and `AcpSyncAgent`/`AcpAsyncAgent` parameters, resolved by type, for the connection the request arrived on. That's why `@NewSession` reads `supportsBooleanConfigOptions()` straight from a parameter here, with no need to capture the built agent.

### The same agent, with the builder API

```java
AcpSyncAgent agent = AcpAgent.sync(new StdioAcpAgentTransport())
    .newSessionHandler(req -> {
        String sessionId = UUID.randomUUID().toString();
        boolean booleans = self.get().getClientCapabilities().supportsBooleanConfigOptions();
        List<AcpSchema.SessionConfigOption> options = settings.open(sessionId, booleans);
        // (sessionId, modes, configOptions): both, during the modes-to-config-options transition
        return new AcpSchema.NewSessionResponse(sessionId, settings.modes(sessionId), options);
    })
    .setSessionConfigOptionHandler(req ->
            // A client-initiated change: the response carries the full list.
            new AcpSchema.SetSessionConfigOptionResponse(settings.apply(req)))
    .setSessionModeHandler(req -> {
        // A client that only knows session modes still works: same state.
        settings.applyMode(req);
        return new AcpSchema.SetSessionModeResponse();
    })
    .promptHandler((req, ctx) -> {
        List<AcpSchema.SessionConfigOption> changed = settings.fallBackIfRateLimited(ctx.getSessionId());
        if (changed != null) {
            // The agent changed a setting on its own: tell the client, with the full list.
            ctx.sendUpdate(new AcpSchema.ConfigOptionUpdate(changed));
        }
        ctx.sendMessage(settings.answer(ctx.getSessionId(), "builder agent"));
        return AcpSchema.PromptResponse.endTurn();
    })
    .build();
```

A builder handler other than the prompt handler receives only its request, so `session/new` reaches the client's capabilities through the built agent (`self.get().getClientCapabilities()`), instead of a parameter.

### Rejecting a bad request

The spec defines no error for an invalid `set_config_option`; this agent answers `-32602`:

```java
case VERBOSE -> {
    if (!state.booleansSupported) {
        // Never offered to this client, so for this session it does not exist.
        throw invalid("Unknown config option '" + VERBOSE + "'");
    }
    if (!(value instanceof Boolean on)) {
        throw invalid("Option 'verbose' takes a boolean, got '" + value + "'");
    }
    state.verbose = on;
}
```

```java
private static AcpProtocolException invalid(String message) {
    return new AcpProtocolException(AcpErrorCodes.INVALID_PARAMS, message, null);
}
```

`req.value()` is an `Object`: a `String` for a select, a `Boolean` for a boolean, so the handler checks its type before trusting it, the same as the id.

### Client: read, change, and watch for agent-initiated changes

```java
var capabilities = AcpSchema.ClientCapabilities.builder()
        .session(AcpSchema.ClientSessionCapabilities.withBooleanConfigOptions())
        .build();

AcpSyncClient client = AcpClient.sync(transport)
        .clientCapabilities(capabilities)
        .sessionUpdateConsumer(ConfigOptionsDemo::printUpdate)
        .build();

client.initialize();
var session = client.newSession(new NewSessionRequest(cwd, List.of()));
printOptions(session.configOptions());

// Change: the response carries the full list, replace your copy with it.
printOptions(client.setSessionConfigOption(
        SetSessionConfigOptionRequest.select(sid, SessionSettings.MODEL, "orbit-1"))
        .configOptions());

printOptions(client.setSessionConfigOption(
        SetSessionConfigOptionRequest.bool(sid, SessionSettings.VERBOSE, true))
        .configOptions());
```

Dispatch option types with `instanceof` and keep a branch for a type a newer agent might send:

```java
if (o instanceof AcpSchema.SessionConfigSelect select) {
    // ...
}
else if (o instanceof AcpSchema.SessionConfigBoolean bool) {
    // ...
}
else if (o instanceof AcpSchema.UnknownSessionConfigOption unknown) {
    System.out.println("  (unknown option type " + unknown.type() + ", ignored)");
}
```

An agent-initiated change (the demo's rate-limited preview model falling back) arrives as a `ConfigOptionUpdate` session update, handled before `prompt()` returns:

```java
else if (update instanceof AcpSchema.ConfigOptionUpdate config) {
    System.out.println("  config_option_update from the agent:");
    printOptions(config.configOptions());
}
```

<Note>
Setting an option the client was never offered (a boolean to a client that didn't advertise support, or a model id that isn't in the list) is rejected with `-32602`, received as an `AcpError`. A client that predates config options can still work through the legacy `session/set_mode`: the agent keeps both representations of the same state in sync.
</Note>

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-33-session-config-options)

## Running the Example

```bash
./mvnw package -pl module-33-session-config-options -q
./mvnw exec:java -pl module-33-session-config-options
```

The demo runs three passes: the builder agent and the annotated agent, both advertising boolean config options, then the builder agent again without that capability, where the `verbose` option is never offered and setting it is rejected, and a legacy `session/set_mode` call is shown keeping the same state.

## Next Module

[Module 34: Extension Methods](/docs/acp-java-sdk/tutorial/34-extension-methods): add your own `_`-prefixed requests and notifications to ACP.
