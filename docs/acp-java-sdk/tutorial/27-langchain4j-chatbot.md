# Module 27: LangChain4j Chatbot

The [Module 25](/docs/acp-java-sdk/tutorial/25-ai-chatbot-agent) chatbot built with LangChain4j. Same ACP agent, a different way to reach the model.

## Prerequisites

- Completed [Module 12: Echo Agent](/docs/acp-java-sdk/tutorial/12-echo-agent)
- `ANTHROPIC_API_KEY` exported (used by `AnthropicChatModel`)
- Java 17+

## What You'll Learn

- Calling the model through LangChain4j's provider-neutral `ChatModel`
- Switching providers by swapping a dependency and a model builder
- Why the ACP handlers never change when the model does

## Dependencies

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-anthropic</artifactId>
    <version>1.16.1</version>
</dependency>
<!-- swap for langchain4j-open-ai, langchain4j-google-ai-gemini, langchain4j-ollama -->
```

## The Code

The ACP skeleton is the fluent builder from the echo agent. Only the prompt handler changes:

```java
// ChatModel is LangChain4j's provider-agnostic interface
ChatModel model = AnthropicChatModel.builder()
    .apiKey(System.getenv("ANTHROPIC_API_KEY"))
    .modelName("claude-sonnet-4-6")
    .maxTokens(1024)
    .build();

var transport = new StdioAcpAgentTransport();

AcpSyncAgent agent = AcpAgent.sync(transport)
    // Identical to the echo agent (Module 12)
    .initializeHandler(req -> InitializeResponse.ok())
    .newSessionHandler(req ->
        new NewSessionResponse(UUID.randomUUID().toString(), null, null))

    // The only change from echo: ask the model
    .promptHandler((req, context) -> {
        String answer = model.chat(req.text());
        context.sendMessage(answer);
        return PromptResponse.endTurn();
    })
    .build();

agent.run();
```

To use another provider, build a different `ChatModel` (for example an OpenAI or Ollama model) and change the dependency. The ACP handler is untouched.

## Conversation Memory

This module keeps to a single turn for clarity: each prompt is answered on its own. LangChain4j adds memory through `MessageWindowChatMemory`, or through an `AiServices` interface with `@MemoryId`. Keying that memory on the ACP session ID gives each editor chat its own history, as [Module 26](/docs/acp-java-sdk/tutorial/26-spring-ai-chatbot) does with Spring AI.

## Three Flavors, One Agent

| Module | How it calls the model |
|--------|------------------------|
| [25](/docs/acp-java-sdk/tutorial/25-ai-chatbot-agent) | Anthropic Java SDK directly (clearest call site) |
| [26](/docs/acp-java-sdk/tutorial/26-spring-ai-chatbot) | Spring AI `ChatClient` |
| **27** | **LangChain4j `ChatModel`** |

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-27-langchain4j-chatbot)

## Running the Example

```bash
export ANTHROPIC_API_KEY=sk-ant-...
./mvnw package -pl module-27-langchain4j-chatbot -q
./mvnw exec:java -pl module-27-langchain4j-chatbot
```

## Next Module

[Module 28: Zed Integration](/docs/acp-java-sdk/tutorial/28-zed-integration) — run your agent inside the Zed editor.
