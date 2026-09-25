# Module 26: Spring AI Chatbot

The [Module 25](/docs/acp-java-sdk/tutorial/25-ai-chatbot-agent) chatbot rebuilt as a Spring Boot `@AcpAgent` bean that talks to the model through Spring AI's `ChatClient`.

## Prerequisites

- Completed [Module 23: Spring Boot Agent](/docs/acp-java-sdk/tutorial/23-spring-boot-agent) and [Module 25: AI Chatbot Agent](/docs/acp-java-sdk/tutorial/25-ai-chatbot-agent)
- Java 21+ (Spring Boot 4.x requirement)
- `ANTHROPIC_API_KEY` exported (read through `spring.ai.anthropic.api-key`)

## What You'll Learn

- Calling the model through Spring AI's provider-neutral `ChatClient`
- Switching model providers by swapping a starter dependency, without touching the agent
- Per-session conversation memory with `MessageWindowChatMemory` and an advisor

## Dependencies

The same ACP Spring Boot starter as Module 23, plus one Spring AI model starter:

```xml
<dependency>
    <groupId>org.springaicommunity</groupId>
    <artifactId>acp-spring-boot-starter</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-model-anthropic</artifactId>
</dependency>
<!-- swap for spring-ai-starter-model-openai, -ollama, ... -->
```

## The Agent

The ACP methods are identical to Module 23's echo bean. The only difference is the body of `@Prompt`:

```java
@Component
@AcpAgent(name = "spring-ai-chatbot", version = "1.0")
public class ChatbotAgentBean {

    private final ChatClient chatClient;

    // Spring AI autoconfigures ChatClient.Builder from the model starter on the classpath
    public ChatbotAgentBean(ChatClient.Builder builder) {
        ChatMemory chatMemory = MessageWindowChatMemory.builder().maxMessages(20).build();
        this.chatClient = builder
            .defaultSystem("You are a concise, friendly assistant running as an ACP agent inside an IDE.")
            .defaultAdvisors(MessageChatMemoryAdvisor.builder(chatMemory).build())
            .build();
    }

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
        // CONVERSATION_ID scopes the memory window to this ACP session
        String answer = chatClient.prompt()
            .user(request.text())
            .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, context.getSessionId()))
            .call()
            .content();
        context.sendMessage(answer);
        return PromptResponse.endTurn();
    }
}
```

Module 25 kept a `List<MessageParam>` per session by hand. Here a sliding window of the last 20 messages lives in a `ChatMemory`, and the advisor injects it into every call. Keying it on the ACP session ID gives each editor chat its own history.

## Configuration

stdout carries the JSON-RPC protocol, so the banner is off and there is no web server:

```properties
spring.main.banner-mode=off
spring.main.web-application-type=none
spring.main.keep-alive=true

spring.ai.anthropic.api-key=${ANTHROPIC_API_KEY}
spring.ai.anthropic.chat.options.model=claude-sonnet-4-6
spring.ai.anthropic.chat.options.max-tokens=1024
```

To use OpenAI, Gemini, or a local Ollama model, replace the starter and the `spring.ai.<provider>.*` properties. `ChatbotAgentBean` does not change.

## Streaming

`ChatClient` also streams. `.stream().content()` returns a `Flux<String>`:

```java
chatClient.prompt()
    .user(request.text())
    .advisors(a -> a.param(ChatMemory.CONVERSATION_ID, context.getSessionId()))
    .stream().content()
    .toStream().forEach(context::sendMessage);
```

## Three Flavors, One Agent

| Module | How it calls the model |
|--------|------------------------|
| [25](/docs/acp-java-sdk/tutorial/25-ai-chatbot-agent) | Anthropic Java SDK directly (clearest call site) |
| **26** | **Spring AI `ChatClient`, multi-provider** |
| [27](/docs/acp-java-sdk/tutorial/27-langchain4j-chatbot) | LangChain4j `ChatModel` |

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-26-spring-ai-chatbot)

## Running the Example

```bash
export ANTHROPIC_API_KEY=sk-ant-...
./mvnw package -pl module-26-spring-ai-chatbot -q
./mvnw exec:java -pl module-26-spring-ai-chatbot
```

The demo asks for a haiku, then asks for it as a limerick in the same session. The follow-up works because `ChatMemory` recalls the first answer.

## Next Module

[Module 27: LangChain4j Chatbot](/docs/acp-java-sdk/tutorial/27-langchain4j-chatbot) — the same agent on LangChain4j.
