---
title: "Tutorial"
sidebarTitle: "Overview"
description: "A progressive tutorial for learning the ACP Java SDK — from client basics to IDE integration."
---

A progressive, hands-on tutorial. Each module focuses on one concept and includes runnable source code.

## Prerequisites

- Java 17 or later
- Maven 3.8+ (or use the included `./mvnw` wrapper)
- For client modules (01-11, 21): [Gemini CLI](https://github.com/google-gemini/gemini-cli) with `--experimental-acp` flag, and a `GEMINI_API_KEY`. The tutorial uses Gemini as a real ACP agent to talk to — the SDK launches it as a subprocess and communicates over stdin/stdout.
- For agent modules (12-20, 22, 31): no external dependencies. You build the agent and the tutorial provides a test client that launches it.
- For the AI chatbot modules (25-27): an `ANTHROPIC_API_KEY`, which the agent actually uses to call the model.
- For the agent-client module (32): the Claude CLI installed and logged in, run without `ANTHROPIC_API_KEY`.

## Tutorial Structure

| Part | Modules | Topics |
|------|---------|--------|
| **1. Client Basics** | 01-11 | Connect, sessions, prompts, streaming, updates, file handlers, permissions, resume, cancel, errors |
| **2. Building Agents** | 12-20 | Echo agent, handlers, updates, requests, testing, capabilities, terminal, MCP, session management |
| **3. Advanced** | 21-24 | Async client, async agent (Project Reactor), Spring Boot agent and client |
| **4. AI-Backed Agents** | 25-27 | The echo agent with a real model behind it: Anthropic Java SDK, Spring AI, LangChain4j |
| **5. IDE Integration** | 28-30 | Zed, JetBrains, VS Code |
| **6. Beyond Chat** | 31-32 | Elicitation (structured user input), an agent loop behind an ACP agent |

## Getting the Code

```bash
git clone https://github.com/markpollack/acp-java-tutorial.git
cd acp-java-tutorial
./mvnw compile
```

## Running a Module

Agent modules run locally with no API key:

```bash
./mvnw package -pl module-12-echo-agent -q
./mvnw exec:java -pl module-12-echo-agent
```

Client modules require `GEMINI_API_KEY`:

```bash
export GEMINI_API_KEY=your-key-here
./mvnw exec:java -pl module-01-first-contact
```

## Three Agent API Styles

The SDK provides three ways to build agents:

| Style | Entry Point | Programming Model |
|-------|-------------|-------------------|
| **Annotation-based** | `@AcpAgent`, `@Prompt` | Declarative, least boilerplate |
| **Sync** | `AcpAgent.sync()` | Blocking handlers, plain return values |
| **Async** | `AcpAgent.async()` | Reactive, Project Reactor `Mono` |

The tutorial uses Sync for agent examples (most accessible to most developers) and introduces annotations and async where relevant.

## Start Learning

Begin with [Module 01: First Contact](/docs/acp-java-sdk/tutorial/01-first-contact) to connect to your first ACP agent.

Or jump to [Module 12: Echo Agent](/docs/acp-java-sdk/tutorial/12-echo-agent) to build an agent without any API key, then give it a brain in [Module 25: AI Chatbot Agent](/docs/acp-java-sdk/tutorial/25-ai-chatbot-agent).
