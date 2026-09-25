# Module 31: Elicitation

An agent asks the user for structured input in the middle of a prompt: a form the client renders, and the user accepts, declines, or cancels.

## What You'll Learn

- Sending an elicitation request from an agent with `createElicitation`
- Building a form schema: text, single-select, multi-select, boolean, and integer fields
- Handling accept, decline, and cancel responses in the agent
- Advertising elicitation support and answering requests on the client

## The Code

### Agent: ask for a form mid-prompt

Elicitation is an agent-to-client request, so the prompt handler needs a reference to the agent. The async API makes the request-then-continue flow a `flatMap`:

```java
AtomicReference<AcpAsyncAgent> agentRef = new AtomicReference<>();

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
                null, null),
            "javaVersion", new IntegerPropertySchema("integer",
                "Java Version", null, 17L, 11L, 21L),
            "gitInit", new BooleanPropertySchema("boolean",
                "Initialize Git?", null, true));

        // name and template are required
        var schema = new ElicitationSchema(fields, List.of("name", "template"));

        return agentRef.get()
            .createElicitation(CreateElicitationRequest.form(
                req.sessionId(), "Configure your new project:", schema))
            .flatMap(response -> {
                if (response.action() == ElicitationAction.ACCEPT) {
                    var content = response.content();
                    return context.sendMessage("Project configured: "
                            + content.get("name") + " (" + content.get("template") + ")\n")
                        .then(Mono.just(PromptResponse.endTurn()));
                }
                // DECLINE or CANCEL
                return context.sendMessage(
                        "User " + response.action().name().toLowerCase() + "d the form.\n")
                    .then(Mono.just(PromptResponse.endTurn()));
            });
    })
    .build();

agentRef.set(agent);
agent.start().then(agent.awaitTermination()).block();
```

### Client: advertise support and answer

The client declares elicitation support in its capabilities and registers a handler. A real client shows the form to the user; the demo fills it in automatically:

```java
AcpSyncClient client = AcpClient.sync(transport)
    .createElicitationHandler(req -> {
        System.out.println("Agent asks: " + req.message());
        ElicitationSchema schema = req.requestedSchema();

        Map<String, Object> values = new HashMap<>();
        for (var entry : schema.properties().entrySet()) {
            values.put(entry.getKey(), autoFill(entry.getKey(), entry.getValue()));
        }
        return CreateElicitationResponse.accept(values);
        // or CreateElicitationResponse.decline() / CreateElicitationResponse.cancel()
    })
    .build();

var caps = new ClientCapabilities(
    new FileSystemCapability(), false,
    new ElicitationCapabilities(), null);
client.initialize(new InitializeRequest(1, caps));
```

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
Elicitation was added in SDK 0.12.0 as an unstable protocol element, marked `@UnstableAcpApi`. It may change in a minor release.
</Note>

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-31-elicitation)

## Running the Example

```bash
./mvnw package -pl module-31-elicitation -q
./mvnw exec:java -pl module-31-elicitation
```

The demo runs four exchanges against the agent: a simple single-select that the user accepts, the full project form accepted with every field type, a form the user declines, and one the user cancels. No API key required.

## Next Module

[Module 32: Agent-Client Agent](/docs/acp-java-sdk/tutorial/32-agent-client) — from chatbot to agent: an ACP agent whose prompt handler runs a tool-using agent loop.
