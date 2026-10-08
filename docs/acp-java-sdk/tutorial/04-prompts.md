# Module 04: Prompts

Deep dive into prompt requests and response handling.

## What You'll Learn

- `PromptRequest` structure — session ID and content list
- `PromptResponse` and `StopReason` values
- Content types for prompts

## The Code

`PromptRequest` takes a session ID (from Module 03) and a list of content items. The response includes a `StopReason` that tells you why the agent stopped generating: check this to know if the response is complete, truncated, or refused. A session update consumer prints the agent's streamed answer as it arrives, so each prompt's response is visible, not just its stop reason:

```java
// Send a prompt with text content
var response = client.prompt(new PromptRequest(
    session.sessionId(),
    List.of(new TextContent("Explain ACP in one sentence."))
));

System.out.println("Stop reason: " + response.stopReason());
// Output: Stop reason: end_turn
```

## Stop Reasons

`StopReason` is an open value type, not an enum: a stop reason this SDK does not know is kept and returned instead of failing the response. Compare with `.equals(...)`, never `==` or an exhaustive `switch`, and always have a fallback for an unrecognized value:

| StopReason | Wire value | Description |
|------------|------------|-------------|
| `END_TURN` | `end_turn` | Agent finished responding normally |
| `MAX_TOKENS` | `max_tokens` | Token limit reached |
| `REFUSAL` | `refusal` | Agent refused the request |
| `CANCELLED` | `cancelled` | Prompt was cancelled by the client |

Understanding stop reasons helps handle different agent behaviors. `END_TURN` is the normal case. `MAX_TOKENS` means the response was truncated. `REFUSAL` may require rephrasing the prompt. Printing a stop reason now prints its wire value (`end_turn`), not the Java constant name (`END_TURN`).

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-04-prompts)

## Running the Example

Requires the Grok CLI on your `PATH`, signed in once with `grok login`. The module launches it as `grok agent stdio`; no API key is needed.

```bash
./mvnw exec:java -pl module-04-prompts
```

## Next Module

[Module 05: Streaming Updates](/docs/acp-java-sdk/tutorial/05-streaming-updates) — receive real-time updates during prompt processing.
