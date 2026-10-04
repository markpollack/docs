# Module 18: Terminal Operations

Execute shell commands on the client through the terminal API.

## What You'll Learn

- The four-step terminal lifecycle: create, wait, output, release, plus `kill` to end a command early
- Implementing terminal handlers on the client, all five: advertising `terminal` needs every one
- Using the terminal API from the agent side

## The Code

### Client: Implement terminal handlers

```java
var clientCaps = new ClientCapabilities(
    new FileSystemCapability(false, false),
    true  // terminal enabled
);

AcpSyncClient client = AcpClient.sync(transport)
    .clientCapabilities(clientCaps)
    .createTerminalHandler(req -> {
        List<String> cmd = new ArrayList<>();
        cmd.add(req.command());
        if (req.args() != null) cmd.addAll(req.args());

        Process process = new ProcessBuilder(cmd)
            .redirectErrorStream(true)
            .start();

        terminals.put(terminalId, process);
        return new CreateTerminalResponse(terminalId);
    })
    .waitForTerminalExitHandler(req -> {
        Process process = terminals.get(req.terminalId()).process();
        int exitCode = process.waitFor();
        return new WaitForTerminalExitResponse(exitCode, null);
    })
    .terminalOutputHandler(req -> {
        // Drained live by a reader thread as the process writes, not read only at the end,
        // so a terminal/output call mid-run sees everything printed so far
        String output = capturedOutput.get(req.terminalId());
        return new TerminalOutputResponse(output, false, null);
    })
    .killTerminalHandler(req -> {
        // Ends a still-running command early; the terminal stays valid, so its output can
        // still be read and the agent releases it afterwards, same as a terminal that exited
        terminals.get(req.terminalId()).process().destroyForcibly();
        return new KillTerminalCommandResponse();
    })
    .releaseTerminalHandler(req -> {
        Process process = terminals.remove(req.terminalId()).process();
        process.destroyForcibly();
        return new ReleaseTerminalResponse();
    })
    .build();

client.initialize();
```

<Note>
As of 0.80.0, `initialize(InitializeRequest)` is removed: capabilities are set only on the client builder (`.clientCapabilities(...)`), and `initialize()` sends them. See the [0.80.0 migration guide](/docs/acp-java-sdk/migration-0.80).
</Note>

<Note>
Advertising `terminal` needs all five handlers registered: `build()` fails, naming the missing ones,
for any advertised capability without its full set. `createTerminalHandler` starts a background
thread that drains the process's output as it arrives, so `terminalOutputHandler` can answer with
everything printed so far even while the command is still running; `waitForTerminalExitHandler`
joins that thread before answering, so a `terminal/output` call right after exit still sees the
command's last lines.
</Note>

### Agent: Use terminal API

```java
.promptHandler((req, context) -> {
    // Check capability first
    if (!context.getClientCapabilities().supportsTerminal()) {
        context.sendMessage("Terminal not supported");
        return PromptResponse.endTurn();
    }

    String terminalId = null;
    try {
        // Step 1: Create terminal
        var createResp = context.createTerminal(
            new CreateTerminalRequest(
                context.getSessionId(),
                "sh", List.of("-c", command),
                null, null, null));
        terminalId = createResp.terminalId();

        // Step 2: Wait for exit
        var exitResp = context.waitForTerminalExit(
            new WaitForTerminalExitRequest(context.getSessionId(), terminalId));

        // Step 3: Get output
        var outputResp = context.getTerminalOutput(
            new TerminalOutputRequest(context.getSessionId(), terminalId));

        context.sendMessage("Exit: " + exitResp.exitCode() +
            "\nOutput:\n" + outputResp.output());
    } finally {
        // Step 4: Always release
        if (terminalId != null) {
            context.releaseTerminal(
                new ReleaseTerminalRequest(context.getSessionId(), terminalId));
        }
    }
    return PromptResponse.endTurn();
})
```

## Terminal Lifecycle

| Step | Agent calls | Client handles | Purpose |
|------|-------------|----------------|---------|
| 1 | `createTerminal()` | `createTerminalHandler` | Spawn process |
| 2 | `waitForTerminalExit()` | `waitForTerminalExitHandler` | Block until done |
| 3 | `getTerminalOutput()` | `terminalOutputHandler` | Read stdout/stderr |
| 4 | `releaseTerminal()` | `releaseTerminalHandler` | Clean up resources |

`killTerminal()` / `killTerminalHandler` ends a still-running command early, outside this four-step
sequence: the terminal stays valid afterward, so its output can still be read and it's released the
same as any other terminal. All five handlers are required to advertise `terminal` at all, not only
the four in the table above.

The agent requests command execution, but the client controls what actually runs. This keeps command execution under the user's control — the client decides whether to allow, sandbox, or deny terminal requests.

<Note>
The SDK also provides `context.execute()` as a convenience method that combines all four steps.
</Note>

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-18-terminal-operations)

## Running the Example

```bash
./mvnw package -pl module-18-terminal-operations -q
./mvnw exec:java -pl module-18-terminal-operations
```

## Next Module

[Module 19: MCP Servers](/docs/acp-java-sdk/tutorial/19-mcp-servers) — pass MCP server configurations to agents.
