# Module 30: VS Code Integration

Run your Java ACP agent in VS Code using the community vscode-acp extension.

## What You'll Learn

- Installing the vscode-acp extension
- Creating a PATH-discoverable wrapper script
- The differences between VS Code, Zed, and JetBrains ACP configuration

## Prerequisites

- VS Code installed
- Java 17+

## The Agent

Same code as Modules 28-29. No code changes needed for different editors.

## Build and Configure

### 1. Install the vscode-acp extension

```bash
code --install-extension omercnet.vscode-acp
```

Or search "VSCode ACP" in the Extensions panel (`Ctrl+Shift+X`).

### 2. Build the JAR

```bash
./mvnw package -pl module-30-vscode-integration -q
```

### 3. Create a wrapper script

The extension auto-detects agents from your PATH. Create a wrapper:

**Linux/macOS:**
```bash
cat > ~/.local/bin/java-tutorial-agent << 'EOF'
#!/bin/bash
exec java -jar /absolute/path/to/vscode-agent.jar "$@"
EOF

chmod +x ~/.local/bin/java-tutorial-agent
```

Replace `/absolute/path/to/vscode-agent.jar` with the output of:
```bash
realpath module-30-vscode-integration/target/vscode-agent.jar
```

**Windows:**
Create `%USERPROFILE%\bin\java-tutorial-agent.cmd`:
```cmd
@echo off
java -jar C:\path\to\vscode-agent.jar %*
```

### 4. Use in VS Code

Click the **VSCode ACP** icon in the Activity Bar, click **Connect**, select your agent.

## Configuration Comparison

| IDE | Configuration | Discovery |
|-----|--------------|-----------|
| **Zed** | `settings.json` — direct command + args | Explicit in settings |
| **JetBrains** | `~/.jetbrains/acp.json` — direct command + args | Explicit in config file |
| **VS Code** | PATH wrapper script | Auto-detected from PATH |

The same agent JAR works across all three editors. The only difference is how each editor finds and launches the agent.

## Native VS Code Support

VS Code does not have native ACP support yet. Microsoft is tracking it in [Issue #265496](https://github.com/microsoft/vscode/issues/265496). The community extension provides ACP functionality until native support arrives.

## Source Code

[View on GitHub](https://github.com/markpollack/acp-java-tutorial/tree/main/module-30-vscode-integration)

## Running the Example

```bash
./mvnw package -pl module-30-vscode-integration -q
./mvnw exec:java -pl module-30-vscode-integration
```
