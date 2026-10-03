# Module 36: Terminal Auth and Logout

An agent that requires sign-in before any session can open, offering two auth methods (one the agent handles itself, one an interactive terminal login the client runs as a separate process) plus a logout capability.

## What You'll Learn

- `AuthMethod` as an open union: `AuthMethodAgent` versus `AuthMethodTerminal`
- Offering a terminal method only to a client that advertised `auth.terminal`
- `@Authenticate`, and why the client never calls it for a terminal method
- Rejecting `session/new` with `AUTHENTICATION_REQUIRED` (`-32000`) before sign-in
- `AgentAuthCapabilities.withLogout()`, `@Logout`, and checking `supportsLogout()` first

## The Code

### Offering auth methods at `initialize`

```java
@Initialize
AcpSchema.InitializeResponse initialize(AcpSchema.InitializeRequest req, NegotiatedCapabilities client) {
    List<AcpSchema.AuthMethod> methods = new ArrayList<>();
    methods.add(new AcpSchema.AuthMethodAgent(API_KEY_METHOD, "API key", "Use the key configured for this machine"));
    if (client.supportsTerminalAuth()) {
        methods.add(new AcpSchema.AuthMethodTerminal(TERMINAL_METHOD, "Log in in a terminal",
                List.of(LOGIN_ARG), Map.of("AUTH_AGENT_LOGIN_STYLE", "plain")));
    }
    var capabilities = AcpSchema.AgentCapabilities.builder()
            .auth(AcpSchema.AgentAuthCapabilities.withLogout())
            .build();
    return new AcpSchema.InitializeResponse(1, capabilities, methods);
}
```

`AuthMethod` is an open union of two kinds. An agent-handled method (`AuthMethodAgent`) is the one the client calls `authenticate` for; a terminal method (`AuthMethodTerminal`) is an interactive login the **client** runs, not something passed to `authenticate`. `@Initialize` takes the connection's `NegotiatedCapabilities` directly as a parameter, so the agent decides which methods to offer from the client's own advertised capabilities: here, whether to offer the terminal method at all depends on `supportsTerminalAuth()`. An unknown auth method type from a newer agent reads as `AuthMethodAgent`.

### Requiring sign-in

```java
@NewSession
AcpSchema.NewSessionResponse newSession(AcpSchema.NewSessionRequest req) {
    if (signedInAs() == null) {
        throw new AcpProtocolException(AcpErrorCodes.AUTHENTICATION_REQUIRED, "Authentication required", null);
    }
    return new AcpSchema.NewSessionResponse(UUID.randomUUID().toString(), null, null);
}
```

### The agent-handled method

```java
@Authenticate
AcpSchema.AuthenticateResponse authenticate(AcpSchema.AuthenticateRequest req) {
    if (API_KEY_METHOD.equals(req.methodId())) {
        apiKeyUser = "api-key user";
        return new AcpSchema.AuthenticateResponse();
    }
    if (TERMINAL_METHOD.equals(req.methodId())) {
        throw new AcpProtocolException(AcpErrorCodes.INVALID_PARAMS,
                "Terminal login is run by the client, not passed to authenticate", null);
    }
    throw new AcpProtocolException(AcpErrorCodes.INVALID_PARAMS, "Unknown auth method " + req.methodId(), null);
}
```

### The terminal method

The client runs the agent's own program again, as a separate process, with the method's `args` and `env` added: not a different login tool, the same binary in a different mode.

```java
// Agent: reads --login, runs an interactive prompt, writes credentials to a file, exits.
public static void main(String[] args) throws IOException {
    if (List.of(args).contains(LOGIN_ARG)) {
        terminalLogin();
        return;
    }
    // ...normal agent startup...
}
```

```java
// Client: for an AuthMethodTerminal, run the agent's command with the method's args and env.
List<String> command = new ArrayList<>(List.of("java", "-jar", jar));
command.addAll(method.args());
ProcessBuilder pb = new ProcessBuilder(command).redirectErrorStream(true);
pb.environment().putAll(method.env());
Process login = pb.start();
// the client shows the terminal to the user; this demo types a name into its input
login.waitFor(30, TimeUnit.SECONDS);
```

The login stores credentials where the running agent process can find them; the client does **not** call `authenticate` for this method at all.

### Logout

```java
@Logout
AcpSchema.LogoutResponse logout(AcpSchema.LogoutRequest req) {
    apiKeyUser = null;
    Files.deleteIfExists(credentials);
    return new AcpSchema.LogoutResponse();
}
```

```java
// Client
if (client.getAgentCapabilities().supportsLogout()) {
    client.logout(new AcpSchema.LogoutRequest());
}
```

### Client: advertising terminal auth, and dispatching the union

```java
var terminalCapable = AcpSchema.ClientCapabilities.builder()
        .auth(new AcpSchema.AuthCapabilities(true))
        .build();

AcpSyncClient client = AcpClient.sync(transport)
        .clientCapabilities(terminalCapable)
        .build();

AcpSchema.InitializeResponse init = client.initialize();
for (AcpSchema.AuthMethod method : init.authMethods()) {
    if (method instanceof AcpSchema.AuthMethodTerminal t) {
        // run the agent program with t.args() and t.env()
    }
    else if (method instanceof AcpSchema.AuthMethodAgent a) {
        // call client.authenticate(new AuthenticateRequest(a.id()))
    }
}
```

A client that never advertises `auth.terminal` sees only the agent method in `authMethods()`: the agent leaves the terminal method out entirely, rather than offering something the client can't run.

<Note>
`session/new` fails with `AcpErrorCodes.AUTHENTICATION_REQUIRED` (`-32000`) until the user is signed in, by either method, and fails again immediately after logout. `AuthMethod` is an open union: dispatch with `instanceof`, the same discipline as every other union type in the schema.
</Note>

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-36-terminal-auth-logout)

## Running the Example

```bash
./mvnw package -pl module-36-terminal-auth-logout -q
./mvnw exec:java -pl module-36-terminal-auth-logout
```

The demo runs seven steps against one client advertising terminal auth (initialize, a rejected `session/new`, the terminal login, a working `session/new`, logout, re-authenticating with the agent method) and a second client that doesn't advertise terminal auth, which is offered only the agent method. No API key required.

## Next Module

[Module 37: Streamable HTTP and WebSocket](/docs/acp-java-sdk/tutorial/37-streamable-http-websocket): serve an agent over the network instead of stdio.
