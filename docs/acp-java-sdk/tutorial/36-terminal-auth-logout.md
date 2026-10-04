# Module 36: Terminal Auth and Logout

An agent that requires sign-in before any session can open, offering two auth methods (one the agent handles itself, one an interactive terminal login the client runs as a separate process) plus a logout capability.

## What You'll Learn

- Declaring `authMethods` on `@AcpAgent`, with no `@Initialize` method needed
- `AuthMethod` as an open union: `AuthMethodAgent` versus `AuthMethodTerminal`
- Why a terminal method reaches only a client that advertised `auth.terminal`, with no hand-written check
- `@Authenticate`, and why the client never calls it for a terminal method
- Rejecting `session/new` with `AUTHENTICATION_REQUIRED` (`-32000`) before sign-in
- `@Logout`, derived `agentCapabilities.auth.logout`, and checking `supportsLogout()` first

## The Code

### Declaring auth methods on `@AcpAgent`, with no `@Initialize` method

```java
@AcpAgent(name = "auth-agent", version = "1.0.0", authMethods = {
        @AuthMethod(id = AuthAgent.API_KEY_METHOD, name = "API key",
                description = "Use the key configured for this machine"),
        @AuthMethod(id = AuthAgent.TERMINAL_METHOD, name = "Log in in a terminal", type = AuthMethod.Type.TERMINAL,
                args = AuthAgent.LOGIN_ARG, env = "AUTH_AGENT_LOGIN_STYLE=plain") })
public class AuthAgent {
    // ...
}
```

There's no `@Initialize` method: the SDK derives everything a client needs from the class.
`@AcpAgent(authMethods = @AuthMethod(...))` becomes `authMethods`; `@Logout` (below) advertises
`agentCapabilities.auth.logout`; `agentInfo` comes from `@AcpAgent(name, version)`. A terminal method
is advertised **only** to a client that announced `clientCapabilities.auth.terminal`: the SDK does
that per-client check itself now, rather than the agent checking `NegotiatedCapabilities` by hand in
a written `@Initialize` method. Declaring an agent-type method (the default, as `api-key` is here)
without an `@Authenticate` handler to serve it fails the build, naming the method.

`AuthMethod` is an open union of two kinds. An agent-handled method (`AuthMethodAgent`, type `AGENT`,
the default) is the one the client calls `authenticate` for; a terminal method (`AuthMethodTerminal`,
type `TERMINAL`) is an interactive login the **client** runs, not something passed to `authenticate`.
An unknown auth method type from a newer agent reads as `AuthMethodAgent`.

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
System.out.println("agentInfo (from @AcpAgent): " + init.agentInfo().name() + " " + init.agentInfo().version());
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
