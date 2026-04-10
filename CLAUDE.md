# CLAUDE.md

## Project

Mintlify documentation site for Pollack AI Lab. Published at `lab.pollack.ai`.

**Repo**: `markpollack/docs` (GitHub)
**Local**: `~/projects/pollack-ai-lab/`

## Deploy

Mintlify auto-deploys on push to `main`. No build step, no CI config.

```bash
git push   # deploys to lab.pollack.ai
```

## Local Dev

Mintlify CLI installed globally (`v4.2.255`).

```bash
# Local preview (hot-reloading)
mintlify dev              # http://localhost:3000
mintlify dev --port 3333  # custom port

# Update CLI
mintlify update
```

## Structure

- `mint.json` — navigation, colors, anchors, analytics
- `custom.css` — Geist Mono typography, dark theme, component styling
- `index.mdx` / `about.mdx` — top-level pages
- `projects/` — project overview pages (thin, link to docs/)
- `docs/` — tutorials, guides, reference (Diataxis-organized)
- `experiments/` — experiment write-ups with status badges
- `methodology/` — six pillars: thesis, forge, KB design, SAE, jury, markov

## Internal Reference

`.agent/` — unpublished reference material (ignored by Mintlify):
- `documentation-framework.md` — Diataxis framework, landscape analysis, agent-consumption weighting, writing conventions, per-project doc standards, site-specific patterns. Read this before writing new docs.

## Conventions

- Dark mode default (`"appearance": "dark"` in mint.json)
- Components: `<CardGroup>`, `<Card>`, `<Steps>`, `<Step>`, `<Note>`, `<Warning>`
- Status badges: inline `<span style={{...}}>` with green (#22c55e), blue (#3b82f6), gray (#334155)
- Frontmatter: `title` and `description` on every page
- Internal links: absolute from doc root (e.g., `/docs/loopy/extending`)
- Images: `/images/` directory
- Ignored files: `DESIGN.md`, `README.md`, `CLAUDE.md`, `plans/**`
