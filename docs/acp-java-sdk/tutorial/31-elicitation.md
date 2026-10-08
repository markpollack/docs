# Module 31: Elicitation

An agent asks the user for structured input in the middle of a prompt, or sends them to a URL for an out-of-band interaction such as signing in.

## What You'll Learn

- Sending an elicitation request from an agent through `context.client().createElicitation`
- Building a form schema: text, single-select, multi-select, boolean, and integer fields
- Handling accept, decline, and cancel responses in the agent
- URL mode: no schema, no content in the answer, and a separate `elicitation/complete` notification when the out-of-band interaction finishes
- Advertising elicitation support (`.elicitationForm()`/`.elicitationUrl()`) and answering requests on the client

## The Code

### Agent: ask for a form mid-prompt

Elicitation is an agent-to-client request. As of 0.80.0 the prompt handler reaches it through
`context.client()`, the raw ACP requests of the prompt's own session, so the agent needs no reference
to itself. The async API makes the request-then-continue flow a `flatMap`:

```java
AcpAsyncAgent agent = AcpAgent.async(transport)
    .initializeHandler(req -> Mono.just(InitializeResponse.ok()))
    .newSessionHandler(req -> Mono.just(
        new NewSessionResponse(UUID.randomUUID().toString(), null, null)))
    .promptHandler((req, context) -> {
        // A form with several field types
        Map<String, ElicitationPropertySchema> fields = Map.of(
            "name", StringPropertySchema.text("Project Name"),
            "template", StringPropertySchema.singleSelect("Template",
                List.of(new EnumOption("web", "Web Application"),
                        new EnumOption("cli", "CLI Tool"),
                        new EnumOption("lib", "Library"))),
            "features", new MultiSelectPropertySchema("array", "Features",
                null, null,
                new UntitledMultiSelectItems("string",
                    List.of("testing", "docker", "ci", "docs")),
                null, null, null),   // minItems, maxItems, _meta
            "javaVersion", new IntegerPropertySchema("integer",
                "Java Version", null, 17L, 11L, 21L),
            "gitInit", new BooleanPropertySchema("boolean",
                "Initialize Git?", null, true));

        // name and template are required
        var schema = new ElicitationSchema(fields, List.of("name", "template"));

        return context.client()
            .createElicitation(CreateElicitationRequest.form(
                req.sessionId(), "Configure your new project:", schema))
            .flatMap(response -> {
                // ElicitationAction is an open value type, not an enum: compare
                // with equals, never ==
                if (ElicitationAction.ACCEPT.equals(response.action())) {
                    var content = response.content();
                    return context.sendMessage("Project configured: "
                            + content.get("name") + " (" + content.get("template") + ")\n")
                        .then(Mono.just(PromptResponse.endTurn()));
                }
                // DECLINE or CANCEL
                String outcome = ElicitationAction.DECLINE.equals(response.action())
                    ? "declined" : "cancelled";
                return context.sendMessage("User " + outcome + " the form.\n")
                    .then(Mono.just(PromptResponse.endTurn()));
            });
    })
    .build();

agent.start().then(agent.awaitTermination()).block();
```

### URL mode: sign-in pages and other out-of-band flows

A form isn't the only kind of elicitation. In URL mode, the agent sends a link (a sign-in page, a payment page) that the client opens out of band with the user's consent: no schema, and the accept answer carries no content. When the external interaction finishes (an OAuth callback, for example), the agent tells the client with a separate `elicitation/complete` notification carrying the same elicitation id:

```java
String elicitationId = "signin-" + UUID.randomUUID();
return context.client()
    .createElicitation(CreateElicitationRequest.url(sessionId,
        "Sign in to the issue tracker to continue",
        elicitationId, "https://tracker.example.com/oauth/authorize?state=" + elicitationId))
    .flatMap(response -> {
        if (!ElicitationAction.ACCEPT.equals(response.action())) {
            return context.sendMessage("User did not open the sign-in page.\n")
                .then(Mono.just(PromptResponse.endTurn()));
        }
        // ...the user signs in on that page (the agent learns of it out of band, e.g. an
        // OAuth callback). Then tell the client it is done:
        return context.client()
            .completeElicitation(new CompleteElicitationNotification(elicitationId))
            .then(context.sendMessage("Signed in; the sign-in page can be closed.\n"))
            .then(Mono.just(PromptResponse.endTurn()));
    });
```

### Client: advertise support and answer

The client declares elicitation support in its capabilities and registers a handler. A real client shows the form to the user; the demo fills it in automatically:

```java
// Advertise the elicitation modes this client handles: form and URL. The agent may not
// request a mode the client did not advertise. A createElicitationHandler on its own
// advertises form mode automatically (as of 0.80.0); URL mode has no handler of its own to
// derive from, so it's set explicitly here, and explicit capabilities are sent as they are.
var caps = ClientCapabilities.builder()
    .elicitationForm()
    .elicitationUrl()
    .build();

AcpSyncClient client = AcpClient.sync(transport)
    .clientCapabilities(caps)
    .createElicitationHandler(req -> {
        System.out.println("Agent asks: " + req.message());

        if (AcpSchema.CreateElicitationRequest.MODE_URL.equals(req.mode())) {
            // A real client shows the URL and opens it in a browser if the user agrees.
            System.out.println("URL mode: open " + req.url() + " (id " + req.elicitationId() + ")");
            return CreateElicitationResponse.accept();  // no content for URL mode
            // or CreateElicitationResponse.decline()
        }

        ElicitationSchema schema = req.requestedSchema();
        Map<String, Object> values = new HashMap<>();
        for (var entry : schema.properties().entrySet()) {
            values.put(entry.getKey(), autoFill(entry.getKey(), entry.getValue()));
        }
        return CreateElicitationResponse.accept(values);
        // or CreateElicitationResponse.decline() / CreateElicitationResponse.cancel()
    })
    // URL mode: the agent reports that the external interaction finished.
    // Ignore ids you do not know or have already completed.
    .completeElicitationHandler(done ->
            System.out.println("elicitation/complete for " + done.elicitationId()))
    .build();

client.initialize();
```

<Note>
As of 0.80.0, `initialize(InitializeRequest)` is removed: capabilities are set only on the client builder, and `initialize()` sends them. See the [0.80.0 migration guide](/docs/acp-java-sdk/migration-0.80).
</Note>

## Form Field Types

| Field | Schema | Renders as |
|-------|--------|------------|
| Text | `StringPropertySchema.text(title)` | Text input |
| Single select | `StringPropertySchema.singleSelect(title, options)` | Dropdown |
| Multi select | `MultiSelectPropertySchema` with `UntitledMultiSelectItems` | Checkboxes |
| Boolean | `BooleanPropertySchema` | Toggle |
| Integer | `IntegerPropertySchema` (default, minimum, maximum) | Number input |

## Responses

| Action | Factory | Meaning |
|--------|---------|---------|
| `ACCEPT` | `CreateElicitationResponse.accept(values)` | The user submitted the form; `content()` holds the values |
| `DECLINE` | `CreateElicitationResponse.decline()` | The user explicitly refused |
| `CANCEL` | `CreateElicitationResponse.cancel()` | The user dismissed the form without choosing |

The agent must handle all three. A prompt that depends on the form still has to end its turn when the user declines or cancels.

<Note>
Elicitation was added in SDK 0.12.0 as an unstable protocol element, marked `@UnstableAcpApi`. It is **stable as of 0.80.0** (promoted in protocol v1.7.0), and its API is no longer `@UnstableAcpApi`. The elicitation capability's modes are now typed (`ElicitationFormCapabilities`, `ElicitationUrlCapabilities`), the no-argument `ElicitationCapabilities()` constructor is removed in favor of `formOnly()`/`urlOnly()`/`formAndUrl()`, and `ElicitationAction` is an open value type, not an enum: compare with `equals`, not `==`. The agent may only request a mode the client advertised.
</Note>

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-31-elicitation)

## Running the Example

```bash
./mvnw package -pl module-31-elicitation -q
./mvnw exec:java -pl module-31-elicitation
```

The demo runs five exchanges against the agent: a simple single-select that the user accepts, the full project form accepted with every field type, a form the user declines, one the user cancels, and a URL-mode sign-in the user agrees to open, followed by the agent's `elicitation/complete`. No API key required.

## Next Module

[Module 32: Agent-Client Agent](/docs/acp-java-sdk/tutorial/32-agent-client) — from chatbot to agent: an ACP agent whose prompt handler runs a tool-using agent loop.
