# Module 32: Agent-Client Agent

From chatbot to agent. The chatbot in [Module 25](/docs/acp-java-sdk/tutorial/25-ai-chatbot-agent) answers from the model's head with one completion call. This agent's prompt handler hands the user's goal to an agent loop that reads and edits files and runs tools in the open project, for as many turns as the goal needs, then reports back.

## Prerequisites

- Completed [Module 25: AI Chatbot Agent](/docs/acp-java-sdk/tutorial/25-ai-chatbot-agent)
- The Claude CLI (Claude Code) installed and logged in. Run `claude` once to confirm it opens without asking for a key
- Java 17+

<Warning>
Run this agent **without** `ANTHROPIC_API_KEY` in its environment. The module drives the local Claude CLI, not the Anthropic HTTP API. The CLI uses your Claude subscription when `ANTHROPIC_API_KEY` is absent, and bills the API when it is present.
</Warning>

## What You'll Learn

- Putting a tool-using agent loop behind an ACP `@Prompt` handler
- Using the session's working directory as the directory the agent acts in
- How [Agent Client](/projects/agent-client) (`AgentClient`) wraps a CLI agent as a reusable model

## The Code

The ACP skeleton is identical to the chatbot. `@NewSession` additionally remembers the working directory the client opened, and the body of `@Prompt` runs an agent instead of a completion:

```java
@AcpAgent(name = "agent-client-agent", version = "1.0")
public class AgentClientAgent {

    // The project the IDE has open, per session: the agent's working directory
    private final Map<String, String> sessionCwds = new ConcurrentHashMap<>();

    @Initialize
    public InitializeResponse initialize(InitializeRequest request) {
        return InitializeResponse.ok();
    }

    @NewSession
    public NewSessionResponse newSession(NewSessionRequest request) {
        String sessionId = UUID.randomUUID().toString();
        sessionCwds.put(sessionId, request.cwd());
        return new NewSessionResponse(sessionId, null, null);
    }

    @Prompt
    public PromptResponse prompt(PromptRequest request, SyncPromptContext context) {
        Path workingDir = Path.of(sessionCwds.getOrDefault(
            context.getSessionId(), System.getProperty("user.dir")));

        context.sendMessage("Running an agent in " + workingDir
            + " - it can read and edit files and may take a moment...\n\n");

        ClaudeAgentOptions options = ClaudeAgentOptions.builder()
            .model("claude-sonnet-4-20250514")
            .maxTurns(40)
            .yolo(true) // non-interactive: don't pause for permission prompts
            .build();

        // ClaudeAgentModel wraps the local Claude CLI as a reusable model
        try (ClaudeAgentModel model = ClaudeAgentModel.builder()
                .workingDirectory(workingDir)
                .defaultOptions(options)
                .build()) {

            // AgentClient drives the model through as many tool-using turns as the goal needs
            AgentClientResponse response = AgentClient.create(model)
                .goal(request.text())
                .workingDirectory(workingDir)
                .run();

            context.sendMessage(response.getResult());
        }
        catch (Exception e) {
            context.sendMessage("Agent run failed: " + e.getMessage());
        }
        return PromptResponse.endTurn();
    }
}
```

`main` is the same `AcpAgentSupport` bootstrap as Module 25.

<Warning>
`yolo(true)` lets the agent edit files and run commands without asking. The demo runs it in a throwaway directory. In an editor it acts on whatever project the window has open.
</Warning>

## Chatbot vs Agent

| | Chatbot (Module 25) | Agent (this module) |
|---|---|---|
| `@Prompt` | One completion call | `AgentClient...goal(text).run()`, a tool-using loop |
| Reads your files? | No, answers from training | Yes, reads and edits files in the working directory |
| Backend | Anthropic HTTP API | The local `claude` CLI |
| Speed | Streams in seconds | Several tool-using turns; noticeably slower |

The three ACP handlers are unchanged. That is the jump from chatbot to agent.

## Swapping the Provider

`agent-claude` has siblings for other CLI agents, such as `agent-gemini` and `agent-codex`. Build a different `AgentModel` and the rest of the handler, and the ACP wire protocol, stay the same.

## Using It in Your IDE

Plug it in like the other agents ([Module 29](/docs/acp-java-sdk/tutorial/29-jetbrains-integration)), but launch it through a wrapper script that unsets `ANTHROPIC_API_KEY` and then runs its arguments:

```json
"Agent-Client": {
  "command": "/path/to/acp-no-key.sh",
  "args": ["java", "-jar", "/abs/path/to/module-32-agent-client/target/agent-client-agent.jar"]
}
```

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-32-agent-client)

## Running the Example

```bash
./mvnw package -pl module-32-agent-client -q
./mvnw exec:java -pl module-32-agent-client
```

The demo starts the agent in a temporary working directory and gives it a goal that requires action: create `haiku.txt` containing a haiku about AI agents. It then reads the file back from disk to show the agent wrote it.

## Back to the Overview

[Tutorial Overview](/docs/acp-java-sdk/tutorial/index) — all modules and the recommended paths through them.
