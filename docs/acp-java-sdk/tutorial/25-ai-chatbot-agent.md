# Module 25: AI Chatbot Agent

Give the echo agent a brain: the prompt handler calls Claude and streams the answer back. This is also the point where the tutorial switches to the `@AcpAgent` annotation API.

## Prerequisites

- Completed [Module 12: Echo Agent](/docs/acp-java-sdk/tutorial/12-echo-agent)
- An `ANTHROPIC_API_KEY` from [console.anthropic.com](https://console.anthropic.com/). Unlike the client modules, this key is actually used: `AnthropicOkHttpClient.fromEnv()` authenticates with it
- Java 17+

## What You'll Learn

- Writing an agent as annotated methods: `@Initialize`, `@NewSession`, `@Prompt`
- Running an annotated agent without Spring, using `AcpAgentSupport`
- Streaming model output to the client as `agent_message_chunk` updates
- Keeping per-session conversation history so follow-up prompts have context

## The Code

Module 12 used the fluent builder. Once the prompt handler does real work, a labelled `@Prompt` method reads better than a builder lambda. `@Initialize` and `@NewSession` are the same boilerplate as the echo agent; only `@Prompt` changes:

```java
@AcpAgent(name = "chatbot-agent", version = "1.0")
public class ChatbotAgent {

    private static final Model MODEL = Model.CLAUDE_SONNET_4_6;

    // fromEnv() reads ANTHROPIC_API_KEY
    private final AnthropicClient anthropic = AnthropicOkHttpClient.fromEnv();

    // Per-session conversation history
    private final Map<String, List<MessageParam>> history = new ConcurrentHashMap<>();

    @Initialize
    public InitializeResponse initialize(InitializeRequest request) {
        return InitializeResponse.ok();
    }

    @NewSession
    public NewSessionResponse newSession(NewSessionRequest request) {
        return new NewSessionResponse(UUID.randomUUID().toString(), null, null);
    }

    @Prompt
    public PromptResponse prompt(PromptRequest request, SyncPromptContext context) {
        String userText = request.text();
        List<MessageParam> turns = history.computeIfAbsent(
            context.getSessionId(), k -> new ArrayList<>());

        MessageCreateParams.Builder params = MessageCreateParams.builder()
            .model(MODEL)
            .maxTokens(1024)
            .system("You are a concise, friendly assistant running as an ACP agent inside an IDE.");
        turns.forEach(params::addMessage);
        params.addUserMessage(userText);

        // Stream Claude's answer back, chunk by chunk
        StringBuilder full = new StringBuilder();
        try (StreamResponse<RawMessageStreamEvent> stream =
                 anthropic.messages().createStreaming(params.build())) {
            stream.stream().forEach(event -> event.contentBlockDelta()
                .flatMap(deltaEvent -> deltaEvent.delta().text())
                .ifPresent(textDelta -> {
                    full.append(textDelta.text());
                    context.sendMessage(textDelta.text());
                }));
        }

        // Remember this turn for the next prompt in the session
        turns.add(MessageParam.builder()
            .role(MessageParam.Role.USER).content(userText).build());
        turns.add(MessageParam.builder()
            .role(MessageParam.Role.ASSISTANT).content(full.toString()).build());

        return PromptResponse.endTurn();
    }
}
```

### Running an annotated agent without Spring

`AcpAgentSupport` scans the instance for the annotated methods and wires each one to the transport. `run()` starts the agent and blocks until the client disconnects:

```java
AcpAgentSupport.create(new ChatbotAgent())
    .transport(new StdioAcpAgentTransport())
    .build()
    .run();
```

[Module 23](/docs/acp-java-sdk/tutorial/23-spring-boot-agent) uses the same annotations and lets Spring Boot discover the bean and manage its lifecycle instead.

## Echo Agent vs Chatbot Agent

| | Echo agent (Module 12) | Chatbot agent (this module) |
|---|---|---|
| API style | Fluent builder | Annotations |
| Prompt handler | `context.sendMessage("Echo: " + text)` | Calls Claude and streams the answer |
| State | None | Per-session history |

The client coalesces consecutive `agent_message_chunk` updates into one growing assistant message, so streaming needs nothing extra on the client side.

### The non-streaming version

If you want the answer in one piece, the handler body is shorter:

```java
Message msg = anthropic.messages().create(
    MessageCreateParams.builder()
        .model(Model.CLAUDE_SONNET_4_6)
        .maxTokens(1024)
        .addUserMessage(request.text())
        .build());
String answer = msg.content().stream()
    .filter(ContentBlock::isText).map(b -> b.asText().text())
    .collect(Collectors.joining());
context.sendMessage(answer);
return PromptResponse.endTurn();
```

## Not Locked to One Provider

The module calls the Anthropic Java SDK directly because it makes the AI call site obvious. The ACP handlers do not depend on it. [Module 26](/docs/acp-java-sdk/tutorial/26-spring-ai-chatbot) builds the same agent with Spring AI's `ChatClient`, and [Module 27](/docs/acp-java-sdk/tutorial/27-langchain4j-chatbot) with LangChain4j's `ChatModel`.

To use the agent in an editor, point the IDE configuration from [Module 29](/docs/acp-java-sdk/tutorial/29-jetbrains-integration) at `chatbot-agent.jar` instead of `echo-agent.jar`.

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-25-ai-chatbot-agent)

## Running the Example

```bash
export ANTHROPIC_API_KEY=sk-ant-...
./mvnw package -pl module-25-ai-chatbot-agent -q
./mvnw exec:java -pl module-25-ai-chatbot-agent
```

The demo launches the agent as a subprocess, asks it for a haiku about debugging, then asks it to turn that haiku into a limerick. The follow-up only works because the agent keeps per-session history.

## Next Module

[Module 26: Spring AI Chatbot](/docs/acp-java-sdk/tutorial/26-spring-ai-chatbot) — the same agent, with the model behind Spring AI's `ChatClient`.
