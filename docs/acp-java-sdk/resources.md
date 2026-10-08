# ACP Resources

The Agent Client Protocol has a life outside this SDK: a specification site, other language SDKs, and
coverage from the editors and IDEs that implement it. This page is a central, curated pointer to that
wider ecosystem, not a restatement of it.

## The spec site, agentclientprotocol.com

- **[Get Started](https://agentclientprotocol.com/get-started/introduction)**: the protocol's own
  introduction, [architecture](https://agentclientprotocol.com/get-started/architecture) overview, and
  separate guides for building an [agent](https://agentclientprotocol.com/get-started/agents) or a
  [client](https://agentclientprotocol.com/get-started/clients).
- **[Protocol reference](https://agentclientprotocol.com/protocol/v1/overview)**: the stable v1 schema
  and every method, in the spec's own words. This SDK's [Errors](/docs/acp-java-sdk/errors) and
  [Concepts](/docs/acp-java-sdk/concepts) pages link back to specific protocol pages rather than
  repeating them.
- **[RFDs](https://agentclientprotocol.com/rfds/about)** (Requests for Discussion): how the protocol
  itself changes, from draft through active, preview, and completed. The
  [Streamable HTTP and WebSocket transport RFD](https://agentclientprotocol.com/rfds/streamable-http-websocket-transport)
  is the authoritative source this SDK's [Transports](/docs/acp-java-sdk/transports) page builds on.
- **[Updates](https://agentclientprotocol.com/updates)** and its
  **[Announcements](https://agentclientprotocol.com/announcements/elicitation-stabilized)**: one post
  per protocol stabilization (elicitation, request cancellation, logout, session config options, and
  more), each explaining what changed and why.
- **[Publications](https://agentclientprotocol.com/publications)**: talks and write-ups about the
  protocol from outside the spec repository itself.
- **[Libraries](https://agentclientprotocol.com/libraries/community)**: every known ACP
  implementation, by language, including the spec's own
  **[Java page](https://agentclientprotocol.com/libraries/java)** pointing back at this SDK.
- **[Registry](https://agentclientprotocol.com/get-started/registry)**: published, ACP-compatible
  agents an editor or IDE can connect to without writing one yourself.

## Editors and IDEs

- **[Zed: "Bring Your Own Agent"](https://zed.dev/blog/bring-your-own-agent-to-zed)**: the announcement
  that introduced ACP, from the editor that originated it; see
  [Zed's own ACP docs](https://zed.dev/docs/ai/external-agents) for how to connect an agent today.
- **[JetBrains: Agent Client Protocol](https://www.jetbrains.com/help/ai-assistant/acp.html)**: ACP
  support across the JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, and the rest), connecting
  external agents into AI Assistant's chat.
- **[VS Code ACP extension](https://github.com/formulahendry/vscode-acp)**: a community extension
  bringing ACP agents into VS Code, not an official Microsoft integration.

## Other language SDKs

This Java SDK is one of several official implementations. Each has its own documentation, release
cadence, and feature coverage; see [Libraries](https://agentclientprotocol.com/libraries/community) on
the spec site for the complete, current list, including community implementations. The SDKs actively
maintained by the protocol's own organization:

- **[TypeScript](https://github.com/agentclientprotocol/typescript-sdk)**
- **[Python](https://github.com/agentclientprotocol/python-sdk)**
- **[Rust](https://github.com/agentclientprotocol/rust-sdk)**
- **[Kotlin](https://github.com/agentclientprotocol/kotlin-sdk)**

See [Cross-SDK Compatibility](/docs/acp-java-sdk/compatibility) for how this Java SDK is interop-tested
against each one, and how its feature set compares.

## Related

<CardGroup cols={2}>
  <Card title="What's New" icon="sparkles" href="/docs/acp-java-sdk/whats-new">
    What changed in each ACP Java SDK release, and why it matters
  </Card>
  <Card title="Cross-SDK Compatibility" icon="shuffle" href="/docs/acp-java-sdk/compatibility">
    Interop testing and a feature comparison against the other SDKs
  </Card>
  <Card title="Concepts" icon="compass" href="/docs/acp-java-sdk/concepts">
    The vocabulary this SDK and the protocol share
  </Card>
</CardGroup>
