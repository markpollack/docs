# Brief: Code Coverage v2 Page Update

**Date**: 2026-03-19
**Status**: Experiment COMPLETE. Page at `experiments/code-coverage-v2.mdx` is stale and must be rewritten.

---

## What Changed

The N=3 sweep is done. 7 variants, 20 sessions, full Markov analysis, two LaTeX reports compiled.
The GitHub release `v2.0.0` is published at https://github.com/markpollack/code-coverage-v2/releases/tag/v2.0.0

Variant names were renamed from internal codenames to publication names:
- `+sae` -> `+preanalysis`
- `+forge` -> `+plan-act`
- "SAE" (Structured Analysis and Exploration) -> "pre-analysis" everywhere

---

## Files to Update

### 1. `experiments/code-coverage-v2.mdx` — REWRITE

Current page is wrong in almost every field. Corrected content below.

**Status badge**: Change from IN PROGRESS (blue) to COMPLETE (green).

**Variant table** (the correct 7 variants):

| # | Name | What it adds |
|---|------|-------------|
| 1 | simple | Minimal prompt, no knowledge, no stopping condition |
| 2 | hardened | Structured prompt + explicit stopping condition |
| 3 | hardened+kb | Hardened + flat knowledge base (Spring test imports, JaCoCo config) |
| 4 | hardened+skills | Hardened + SkillsJars (structured, modular knowledge packages) |
| 5 | hardened+preanalysis | Hardened + mandatory pre-analysis pass before writing tests |
| 6 | hardened+skills+preanalysis | Skills + pre-analysis together |
| 7 | hardened+skills+preanalysis+plan-act | Two-phase: deep exploration then sustained action |

**Target**: spring-petclinic only (remove gs-rest-service — that was v1).

**Key results** (final, N=3):

| Variant | Mean Steps | Mean Cost | T3 Quality |
|---------|-----------|-----------|------------|
| hardened+skills+preanalysis | 75.0 | $3.39 | 0.850 |
| hardened+preanalysis | 80.3 | $3.41 | 0.789 |
| hardened+kb | 83.3 | $3.21 | 0.847 |
| hardened+skills+preanalysis+plan-act | 95.0 | $5.11 | 0.878 |
| hardened+skills | 101.7 | $3.70 | 0.856 |
| hardened | 103.0 | $4.08 | 0.850 |
| simple | 109.5 | $3.47 | 0.783 |

**Key findings** (replace "Preliminary Results" section entirely):

1. **Prompt hardening is the biggest quality driver** — simple -> hardened: +0.067 quality, -6% steps. Free gain from structural discipline.
2. **Pre-analysis drives efficiency at a quality cost** — hardened+preanalysis: -22% steps but quality drops to 0.789 (near simple). Tight plans miss edge cases.
3. **Skills fix pre-analysis's quality regression** — hardened+skills+preanalysis: -31% steps AND quality = 0.850 (matches hardened). Best tradeoff in the experiment.
4. **KB is a pure efficiency play on known codebases** — hardened+kb: -24% steps, quality flat. On novel codebases the effect should be larger.
5. **Plan-act is high variance** — highest quality ceiling (0.878) but also highest cost ($5.11) and rework spiral risk.
6. **Markov model predicts step counts** — zero mean bias in leave-one-out cross-validation despite formal rejection of first-order.

**Remove**: "What's Next" section (the sweeps are done). Replace with a "What Comes Next" pointing to the Fineract follow-up experiment.

**Resources section**: Add cards for:
- GitHub release v2.0.0 (dataset download)
- Blog post: "I Read My Agent's Diary" at https://blog.pollack.ai/i-read-my-agents-diary/
- Results report PDF (link to `/images/results-v3.pdf`)
- Reading Agent Behavior PDF (link to `/images/markov-primer-v2.pdf`)
- v1 baseline experiment (keep existing link)

### 2. `experiments/index.mdx` — Move v2 from "Active" to "Completed"

Move the Code Coverage v2 card from "Active Experiments" to "Completed Experiments". Update the card description to reflect final results:

> Skills vs flat knowledge bases — 7 variants on Spring PetClinic. Skills+preanalysis achieves -31% steps with no quality loss. Full Markov behavioral analysis.

### 3. Copy PDFs to `/images/`

Source files (already compiled with updated figure paths):
- `/home/mark/tuvium/projects/tuvium-code-coverage-v2/docs/latex/results-v3.pdf`
- `/home/mark/tuvium/projects/tuvium-code-coverage-v2/docs/latex/markov-primer-v2.pdf`

Copy to:
- `/home/mark/projects/docs/images/results-v3.pdf`
- `/home/mark/projects/docs/images/markov-primer-v2.pdf`

---

## What NOT to Change

- `experiments/code-coverage-v1.mdx` — accurate as-is
- `methodology/` pages — separate concern
- Historical plans in the experiment repo — time-stamped records, not updated

---

## Source Material for the Doc Writer

| Material | Location |
|----------|----------|
| Final results report (LaTeX) | `~/tuvium/projects/tuvium-code-coverage-v2/docs/latex/results-v3.tex` |
| Markov primer (LaTeX) | `~/tuvium/projects/tuvium-code-coverage-v2/docs/latex/markov-primer-v2.tex` |
| Compiled PDFs | `~/tuvium/projects/tuvium-code-coverage-v2/docs/latex/results-v3.pdf`, `markov-primer-v2.pdf` |
| README with correct variant table | `~/tuvium/projects/tuvium-code-coverage-v2/README.md` |
| REPRODUCIBILITY guide | `~/tuvium/projects/tuvium-code-coverage-v2/REPRODUCIBILITY.md` |
| Blog post (narrative) | `~/projects/pollack-ai-blog-content/content/posts/2026/03/i-read-my-agents-diary/` |
| GitHub release | https://github.com/markpollack/code-coverage-v2/releases/tag/v2.0.0 |
| Markov analysis library | https://github.com/markpollack/markov-agent-analysis (needs to be made public — currently tuvium org only) |

---

## Naming Conventions (for consistency)

- "pre-analysis" (hyphenated in prose, no hyphen in variant names: `+preanalysis`)
- "plan-act" (always hyphenated)
- Never use "SAE" or "forge" in new content
- "SkillsJars" (one word, camelCase) when referring to the technology
- "skills" (lowercase) when referring to the variant modifier
