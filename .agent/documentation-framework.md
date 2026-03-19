# Documentation Framework Reference

Internal reference for the documentation approach used on lab.pollack.ai. Not published.

---

## Foundation: Diataxis (Daniele Procida)

Four document types on two axes:

|  | **Acquisition** (learning) | **Application** (working) |
|--|---|---|
| **Action** (practical) | **Tutorial** | **How-to Guide** |
| **Cognition** (theoretical) | **Explanation** | **Reference** |

**Source**: [diataxis.fr](https://diataxis.fr/)

### Agent-Consumption Weighting

Agents don't read docs the way humans do. Priority inverted:

| Type | Agent Value | Why |
|------|------------|-----|
| **Reference** | Highest | Structured, greppable, predictable format |
| **How-to** | High | Action recipes map to agent tasks |
| **Explanation** | Medium | Context on demand, costs tokens |
| **Tutorial** | Low | Pedagogical scaffolding wastes tokens |

### Rules per Type

**Tutorial** — the teacher is responsible for the learner's success:
- Minimize explanation — learn by doing
- Eliminate choices — one path that works
- Deliver early results
- Every step must succeed
- Language: "We will...", "First, do X."

**How-to** — solve a specific problem:
- Address a real-world problem, not an abstract concept
- Focus on action — no digressions
- Assume competence
- Allow adaptation
- Name it precisely ("How to integrate X", not "X")

**Reference** — describe the machinery:
- Describe, and only describe
- Structure mirrors the machinery, not the user's journey
- Consistency is paramount — same format for every entry
- Austere, authoritative, zero ambiguity

**Explanation** — understanding and context:
- Step back from the machinery
- Make connections to other concepts
- Provide design decision context
- Embrace perspective — all explanation contains viewpoint

### The Compass

When writing, ask two questions:
1. Is this about **doing** or **understanding**?
2. Is the reader **learning** or **working**?

If content belongs in a different quadrant, move it to a separate page and link.

---

## Extensions Beyond Diataxis

Three additional doc types that don't fit the four quadrants:

| Type | What | Where on site |
|------|------|--------------|
| **Glossary** | All key terms in one place | `docs/glossary.mdx` |
| **ADR** | Architecture decision records | Not yet on site (low priority per Mark) |
| **Changelog** | Version history for humans | Not yet on site (low priority per Mark) |

---

## Layered Composition

No single framework covers everything. We compose:

| Layer | Framework | Covers |
|-------|-----------|--------|
| Content taxonomy | Diataxis | *What types* of docs to write |
| Architecture docs | Arc42 (lightweight) + C4 | System structure at zoom levels |
| Decision history | ADRs (Nygard) | *Why* things are the way they are |
| Release comms | Keep a Changelog | Version history for humans |
| API reference | JavaDoc | Generated from source |
| Writing style | Google dev docs (adapted) | Consistent prose quality |
| Process | Docs as Code | Git, PRs, CI verification |

---

## Landscape Analysis (evaluated Mar 2026)

### Frameworks

| Framework | Scope | Best for |
|-----------|-------|----------|
| **Diataxis** | Full doc taxonomy (4 types) | Libraries, frameworks, dev tools |
| **Google Style Guide** | Writing style | Any technical writing |
| **Microsoft Style Guide** | Dev content patterns | Developer-facing docs |
| **Write the Docs** | Community practices | Connecting with community |
| **Doc-Driven Development** | Dev process | Greenfield projects |
| **README Driven Dev** | Dev process | New libraries, open source |
| **Docs as Code** | Process + tooling | Any project wanting eng rigor |
| **Arc42** | Architecture docs (12 sections) | System architecture |
| **C4 Model** | Architecture diagrams (4 levels) | Visual architecture comms |
| **ADRs** | Decision records | Architecture decisions |
| **Keep a Changelog** | Release comms (6 categories) | Any versioned software |
| **JavaDoc** | API reference | Java libraries |
| **Spring patterns** | Reference + API docs | Spring ecosystem |

### Agent/AI Project Patterns

- **LangChain**: Explicitly follows Diataxis (Tutorials, How-to, Conceptual, API Reference)
- **Semantic Kernel**: ADRs in repo (`docs/decisions/`). Microsoft Learn hosting.
- **CrewAI**: Role-based docs matching role-based agents
- **AutoGen**: Documentation lag acknowledged. ADRs in repo.

### Emerging Agent Doc Types

1. **Pattern catalogs** — reusable agent patterns (half-reference, half-explanation)
2. **Experiment results** — reproducible findings with structured metadata
3. **KB architecture docs** — how agent knowledge is structured and updated

### Practitioner Consensus

- Emmanuel Bernard (Quarkus): Diataxis's best contribution is "deciding what to *exclude*"
- Tom Johnson: AI/chatbot interfaces may reduce importance of information architecture
- Consensus: "soft apply" as a decision-making lens, not a rigid rule

---

## Writing Conventions

Adapted from Google Developer Documentation Style Guide:

- **Second person** ("you"), **present tense**, **active voice**
- **Serial comma** (Oxford comma)
- Code in backticks, commands in code blocks with language tag
- One sentence per line in source (aids diffing)
- No emojis in docs
- Link rather than duplicate

---

## Per-Project Documentation Set

Every project should have at minimum:

```
project/
├── README.md              # Product overview, quick start, links to docs
├── CLAUDE.md              # Agent session bridge
└── docs/
    ├── getting-started     # Tutorial: first use
    ├── concepts/           # Explanation: architecture, rationale
    ├── guides/             # How-to: task-oriented recipes
    └── reference/          # Reference: API, config, glossary
```

Optional:
- `docs/guides/troubleshooting` — when users report recurring issues
- `docs/guides/migration` — when breaking changes ship
- `docs/guides/extending` — when extension points exist (SPI, plugins, skills)

---

## Site-Specific: lab.pollack.ai

### Navigation Groups

| Group | Content |
|-------|---------|
| Lab | Home, About |
| Projects | Catalog, Loopy |
| Agent Suite | agent-workflow through agent-tools-and-skills |
| Supporting Projects | claude-agent-sdk, acp-java-sdk, spring-ai-a2a |
| Documentation | Hub, Glossary |
| {Project} Docs | Getting started, guides, reference per project |
| Experiments | Index, v1, v2, issue classification |
| Methodology | Six pillars |

### Methodology: Six Pillars

1. **The Thesis** — knowledge + structured execution > model
2. **Forge** — deterministic customization pipeline
3. **KB Design** — structuring knowledge for agent consumption
4. **SAE** — structured agent execution with checkpoints
5. **Four-Tier Jury** — cascaded evaluation (T0-T3)
6. **Markov Fingerprinting** — behavioral analysis of tool-call traces

### Mintlify Components

- `<CardGroup cols={2|3}>` + `<Card>` — navigation grids
- `<Steps>` + `<Step>` — procedural content
- `<Note>` / `<Warning>` — callouts
- Status badges: `<span style={{background: '#22c55e', ...}}>COMPLETE</span>`
- Tables: pipe-delimited markdown
- Code blocks: triple backticks with language tag

### Cross-Linking Strategy

| From | To | Pattern |
|------|----|---------|
| Project page | Docs | CardGroup with getting-started, guides, reference |
| Experiment | Project | "Built with agent-judge" |
| Methodology | Experiments | "Applied in: Code Coverage v1, v2" |
| Docs page | Related docs | CardGroup at bottom |

---

## Sources

- [Diataxis](https://diataxis.fr/) (Daniele Procida)
- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/welcome/)
- [Write the Docs](https://www.writethedocs.org/guide/index.html)
- [Arc42](https://arc42.org/)
- [C4 Model](https://c4model.com/)
- [ADRs](https://adr.github.io/) (Michael Nygard, 2011)
- [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
- [SkillsBench](https://arxiv.org/abs/2602.12670) — +16.2pp curated skills, -2.9pp comprehensive
- Emmanuel Bernard: [Diataxis exploration](https://emmanuelbernard.com/blog/2024/12/19/diataxis/)
- Tom Johnson: [Diataxis analysis](https://idratherbewriting.com/blog/what-is-diataxis-documentation-framework)
