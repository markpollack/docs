# lab.pollack.ai — Design Document

## Overview

**Domain**: `lab.pollack.ai`
**Platform**: Mintlify (hosted docs)
**Vibe**: Research lab + project showcase — "a small open research lab for AI engineering"
**Audience**: Deep technical readers, agent researchers, advanced Spring AI developers

## Ecosystem Position

```
pollack.ai        → Landing / visual identity (Next.js on Vercel)
blog.pollack.ai   → Ideas, essays, thesis narrative (Ghost)
lab.pollack.ai    → Projects + experiments (Mintlify) ← THIS SITE
```

**Knowledge Flow Principle** (from G1 conversation):
```
Blog idea → Lab experiment → Project implementation
```
Every layer cross-links bidirectionally. Blog posts link to lab experiments, experiments link to project docs, project docs link back to methodology.

## Brand Alignment

### Colors
Adapting the pollack.ai palette for Mintlify's color system:

| Token | Hex | Source |
|-------|-----|--------|
| Primary | `#4fc3f7` | Cyan from pollack.ai section labels |
| Light | `#81d4fa` | Lighter cyan for hover states |
| Dark | `#0097a7` | Deep teal for dark mode emphasis |

**Rationale**: The pollack.ai site uses gold (#ffd740) for interactive warmth and cyan (#4fc3f7) for structure/metadata. For a docs site, cyan reads as "technical/trustworthy" and pairs well with Mintlify's dark mode. Gold appears in card accents and callouts.

### Typography
Mintlify uses Inter by default, which is close to Geist Sans. The monospace technical identity carries through code blocks and inline code.

### Design Language
- Left-border cards (from pollack.ai and blog theme)
- Section labels: uppercase, spaced, with gradient line
- Physics metaphor: agent trajectories = particle tracks, tool calls = collisions, evaluation = detectors

## Information Architecture

```
lab.pollack.ai/
├── Home (index)                     — Lab overview, featured work, latest experiments
├── Projects/
│   ├── index                        — Project catalog with cards
│   ├── agent-workflow               — Agent harness / workflow engine (renamed)
│   ├── agent-client                 — CLI agent integrations (Claude, Gemini)
│   ├── agent-judge                  — Evaluation framework (4-tier jury)
│   ├── loopy                        — Interactive coding agent CLI
│   ├── spring-ai-bench              — Enterprise Java agent benchmarking
│   └── agent-journal                — Agent trace capture & analysis
├── Experiments/
│   ├── index                        — Experiment methodology, lab notebook style
│   ├── code-coverage-v1             — Knowledge injection baseline (9 variants)
│   ├── code-coverage-v2             — Skills vs flat KB ablation (7 variants)
│   ├── issue-classification         — (upcoming) IR experiment on SWE-bench
│   └── swe-bench-results            — (upcoming) Cross-experiment SWE-bench
├── Methodology/
│   ├── index                        — Research approach overview
│   ├── four-tier-jury               — T0-T3 evaluation system
│   ├── markov-fingerprinting        — Agent behavioral trace analysis
│   └── knowledge-directed-execution — The thesis: knowledge + structured execution > model
└── About/
    └── index                        — Lab mission, who is Mark Pollack
```

## Navigation Design

### Sidebar Groups
1. **Lab** — Home, About
2. **Projects** — The six core projects
3. **Experiments** — Active and completed experiments
4. **Methodology** — Cross-cutting research methods

### Top Anchors
- Blog (→ blog.pollack.ai)
- GitHub (→ github.com/markpollack or tuvium org)

### Top Bar CTA
- "View on GitHub" or "Latest Experiment"

## Project Pages — Template

Each project page follows this structure:
1. **Hero**: Title, one-line description, status badge
2. **Quick Links**: GitHub repo, Maven Central (if applicable), related blog post
3. **Overview**: What it does, why it matters
4. **Architecture**: Key abstractions, component diagram
5. **Getting Started**: Minimal code to try it
6. **Relationship to Lab**: How this project connects to experiments

## Experiment Pages — Template

Each experiment page follows this structure:
1. **Hero**: Experiment name, status (Complete/In Progress/Planned), date range
2. **Hypothesis**: What we're testing
3. **Setup**: Target project, variants, N-count, cost
4. **Results**: Key findings, charts/figures
5. **Markov Analysis**: Behavioral fingerprint (if applicable)
6. **Blog Posts**: Links to related blog.pollack.ai posts
7. **Raw Data**: Link to experiment repo for full traces

## Cross-Linking Strategy

| From | To | Link Pattern |
|------|----|-------------|
| Blog post | Lab experiment | "Full experiment details →" |
| Lab experiment | Project docs | "Built with agent-judge →" |
| Project page | Lab experiments | "Used in: Code Coverage v1, v2" |
| Lab experiment | Blog post | "Read the narrative →" |
| Methodology | Experiments | "Applied in: [list]" |

## Analytics

Plausible Analytics: domain `lab.pollack.ai`
Track cross-site flows: blog → lab, lab → GitHub

## Future Additions (Not in v1)

- Code Coverage v3 experiment (in progress, not ready to show)
- Liquibase/Flyway experiment
- Agento University showcase
- Interactive Markov chain visualizations
- Experiment comparison dashboards
