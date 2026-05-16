# Module 19: MCP Servers

Pass MCP server configurations to agents when creating sessions.

## What You'll Learn

- Passing `McpServer` configs via `NewSessionRequest`
- Three MCP server types: `McpServerStdio`, `McpServerHttp`, `McpServerSse`
- Checking agent MCP capabilities
- Receiving MCP configs on the agent side

## The Code

### Client: Pass MCP servers to agent

```java
// Check what MCP transports the agent supports
NegotiatedCapabilities agentCaps = client.getAgentCapabilities();
System.out.println("HTTP: " + agentCaps.supportsMcpHttp());
System.out.println("SSE: " + agentCaps.supportsMcpSse());

// Session with STDIO MCP server
var session1 = client.newSession(new NewSessionRequest(cwd, List.of(
    new McpServerStdio(
        "filesystem",
        "npx",
        List.of("-y", "@modelcontextprotocol/server-filesystem", "/tmp"),
        List.of())
)));

// Session with multiple server types
var session2 = client.newSession(new NewSessionRequest(cwd, List.of(
    new McpServerStdio("git", "npx",
        List.of("-y", "@modelcontextprotocol/server-git"), List.of()),
    new McpServerHttp("weather-api",
        "https://api.weather.example.com/mcp", List.of()),
    new McpServerSse("live-data",
        "https://stream.example.com/mcp/events", List.of())
)));
```

### Agent: Receive and advertise MCP support

```java
.initializeHandler(req -> {
    var mcpCaps = new McpCapabilities(true, true); // HTTP and SSE
    var agentCaps = new AgentCapabilities(
        true, mcpCaps, new PromptCapabilities());
    return InitializeResponse.ok(agentCaps);
})

.newSessionHandler(req -> {
    // MCP servers arrive with the session
    List<McpServer> servers = req.mcpServers();
    for (McpServer server : servers) {
        switch (server) {
            case McpServerStdio s ->
                System.out.println("STDIO: " + s.name() + " " + s.command());
            case McpServerHttp h ->
                System.out.println("HTTP: " + h.name() + " " + h.url());
            case McpServerSse s ->
                System.out.println("SSE: " + s.name() + " " + s.url());
            default -> {}
        }
    }
    return new NewSessionResponse(sessionId, null, null);
})
```

## MCP Server Types

| Type | Transport | Use Case |
|------|-----------|----------|
| `McpServerStdio` | Stdin/stdout subprocess | Local tools (filesystem, git) |
| `McpServerHttp` | HTTP endpoint | Remote APIs |
| `McpServerSse` | Server-sent events | Streaming data |

The client tells the agent which MCP servers are available. The agent is responsible for connecting to them using an MCP client library. ACP handles the configuration exchange — not the MCP connection itself.

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-19-mcp-servers)

## Running the Example

```bash
./mvnw package -pl module-19-mcp-servers -q
./mvnw exec:java -pl module-19-mcp-servers
```

## Next Module

[Module 21: Async Client](/acp-java-sdk/tutorial/21-async-client) — use the reactive, non-blocking client API.
