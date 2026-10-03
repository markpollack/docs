# Module 34: Extension Methods

Add your own `_`-prefixed requests and notifications to ACP, in both directions, typed and raw: builder handlers, annotations, and the senders on all four facades.

## What You'll Learn

- Why a custom method name must start with `_`, and what happens if it doesn't
- Typed extension handlers (`TypeRef`) versus raw ones (the plain JSON value)
- `@ExtRequest` and `@ExtNotification` on an annotated agent
- Sending with `sendExtRequest`/`sendExtNotification` from a client or an agent
- What happens when nothing serves a method: `-32601` for a request, silence for a notification

## The Code

### Naming the extension

A shared contract both sides agree on. ACP reserves every name without a leading `_` for the protocol itself, so a custom method must start with it:

```java
public final class Extensions {
    // client -> agent
    public static final String WORD_COUNT = "_acptutorial/word_count";   // request, typed
    public static final String ECHO = "_acptutorial/echo";               // request, raw
    public static final String LOG = "_acptutorial/log";                 // notification, typed

    // agent -> client
    public static final String SELECTION = "_acptutorial/editor/selection"; // request, typed
    public static final String STATUS = "_acptutorial/status";              // notification, raw
    public static final String ACK = "_acptutorial/ack";                    // notification, raw

    public record WordCountParams(String text) {}
    public record WordCountResult(int words, int characters) {}
    public record LogEvent(String level, String message) {}
    public record SelectionQuery(String file) {}
    public record Selection(String file, int startLine, int endLine, String text) {}
}
```

Registering a handler or sending to a name without the prefix throws `IllegalArgumentException` before anything leaves the process, so an extension can never collide with or shadow a protocol method. Namespacing the rest of the name with a domain you control (`_acptutorial/...`) keeps it from colliding with someone else's extension.

### Serving, on the builder agent

```java
AcpSyncAgent agent = AcpAgent.sync(new StdioAcpAgentTransport())
    // Typed request: params read as WordCountParams, result written as JSON.
    .extRequestHandler(Extensions.WORD_COUNT, new TypeRef<WordCountParams>() {},
            params -> new WordCountResult(params.text().split("\\s+").length, params.text().length()))

    // Raw request: params arrive as the plain JSON value.
    .extRequestHandler(Extensions.ECHO, params -> Extensions.ordered(
            "echoed", params, "agentSawJavaType", params.getClass().getSimpleName()))

    // Typed notification: no answer, so the agent acknowledges with a notification of its own.
    .extNotificationHandler(Extensions.LOG, new TypeRef<LogEvent>() {},
            event -> self.get().sendExtNotification(Extensions.ACK,
                    Extensions.ordered("received", event.level() + ": " + event.message(), "by", "builder agent")))
    .build();
```

A handler must not return `null`: a `null` result answers `-32603`; return an empty map when there's nothing to say.

### Serving, with annotations

```java
@ExtRequest(Extensions.WORD_COUNT)
WordCountResult wordCount(WordCountParams params) {
    return new WordCountResult(params.text().split("\\s+").length, params.text().length());
}

@ExtRequest(Extensions.ECHO)
Map<String, Object> echo(Map<String, Object> params) {
    return Extensions.ordered("echoed", params, "agentSawJavaType", params.getClass().getSimpleName());
}

@ExtNotification(Extensions.LOG)
void log(LogEvent event, AcpSyncAgent agent) {
    agent.sendExtNotification(Extensions.ACK,
            Extensions.ordered("received", event.level() + ": " + event.message(), "by", "annotated agent"));
}
```

The annotation names the method; discovery fails if it doesn't start with `_`. A handler takes at most one params parameter (a record for typed params, `Map<String, Object>` for raw), plus, like any other annotated handler, the connection's `AcpSyncAgent`/`AcpAsyncAgent` and `NegotiatedCapabilities`.

### Calling the other side, from a prompt handler

```java
@Prompt
AcpSchema.PromptResponse prompt(AcpSchema.PromptRequest req, SyncPromptContext ctx, AcpSyncAgent agent) {
    Selection selection = agent.sendExtRequest(Extensions.SELECTION, new SelectionQuery("src/Main.java"),
            new TypeRef<Selection>() {});
    agent.sendExtNotification(Extensions.STATUS, Extensions.ordered("state", "reviewing", "file", selection.file()));
    try {
        agent.sendExtRequest(Extensions.NOT_SERVED, Map.of());
    }
    catch (AcpError e) {
        ctx.sendThought("the client does not serve " + Extensions.NOT_SERVED + " (code " + e.getCode() + ")");
    }
    ctx.sendMessage("Reviewed " + selection.file() + " lines " + selection.startLine() + "-"
            + selection.endLine() + ": '" + selection.text() + "' looks fine.");
    return AcpSchema.PromptResponse.endTurn();
}
```

A builder agent reaches the built agent through an `AtomicReference` set right after `build()`; an annotated handler just takes `AcpSyncAgent` as a parameter, as shown here.

### Client: serving the agent's calls, and calling back

```java
AcpSyncClient client = AcpClient.sync(transport)
    // Agent -> client, typed request: params read as SelectionQuery.
    .extRequestHandler(Extensions.SELECTION, new TypeRef<SelectionQuery>() {}, query ->
            new Selection(query.file(), 12, 14, "int total = a + b;"))
    // Agent -> client, raw notifications: params arrive as a Map.
    .extNotificationHandler(Extensions.STATUS, status -> System.out.println("status: " + status))
    .extNotificationHandler(Extensions.ACK, ack -> acks.countDown())
    .build();

client.initialize();

// Typed request.
WordCountResult count = client.sendExtRequest(Extensions.WORD_COUNT,
        new WordCountParams("extension methods are just JSON-RPC"), new TypeRef<WordCountResult>() {});

// Raw request: Map in, raw JSON value out.
Object echoed = client.sendExtRequest(Extensions.ECHO, Map.of("numbers", List.of(1, 2, 3)));

// Notification: no answer.
client.sendExtNotification(Extensions.LOG, new LogEvent("info", "client started"));
```

### What happens without a handler

```java
try {
    client.sendExtRequest(Extensions.NOT_SERVED, Map.of());
}
catch (AcpError e) {
    System.out.println(Extensions.NOT_SERVED + " -> AcpError code " + e.getCode()); // -32601
}

try {
    client.sendExtRequest("acptutorial/word_count", Map.of()); // missing the leading "_"
}
catch (IllegalArgumentException e) {
    System.out.println("refused locally, nothing was sent");
}
```

<Note>
A request nobody serves fails with `-32601` (method not found), the same as any unhandled protocol method. A notification nobody handles is silently ignored, since a notification has no response to fail. Both behaviors match the spec's extensibility rules, not just this SDK's convenience.
</Note>

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-34-extension-methods)

## Running the Example

```bash
./mvnw package -pl module-34-extension-methods -q
./mvnw exec:java -pl module-34-extension-methods
```

The demo runs the same six steps against the builder agent and the annotated agent: a typed request, a raw request, a notification with an agent-sent acknowledgement, a method nobody serves, a name without the leading underscore, and a prompt during which the agent calls two of the client's extension methods. No API key required.

## Next Module

[Module 35: Cancellation and Timeouts](/docs/acp-java-sdk/tutorial/35-cancellation-timeouts): the two ways to cancel in ACP, and the Java SDK's prompt timeouts.
