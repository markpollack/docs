# Tutorial repository sweep — scope report

> Raised: 2026-08-22
> Source work order: `agent-release-manager/plans/inbox/2026-08-22-docs-and-tutorials-release-currency.md`, Phase A item 4
> Status: **survey only — no tutorial repository was edited under this work order**

All version claims below were resolved against `repo1.maven.org` on 2026-08-22, not inferred
from the repositories themselves.

## Summary

| Repository | Stale property | Current | Target | Modules affected | Sizing |
|---|---|---|---|---|---|
| `claude-agent-sdk-java-tutorial` | `claude-agent-sdk.version` | 1.4.0 | **1.5.0** | 26 poms, 4 call sites | Small — do first |
| `acp-java-tutorial` | `agentworks.version` | 1.6.0 | **1.16.0** | 1 pom, 2 java files | Small |
| `agent-judge-tutorial` | `agent-judge.version` | 0.14.0 | **0.15.0** | 11 poms | Small, but gated |
| `agent-judge-tutorial-steward` | prose only | 0.11.0 / 0.14.0 | **0.15.0** | no poms | Trivial, follows the above |

Each repository is a single-property bump. There is no coordinate sprawl: every module
inherits its portfolio version from one root `<properties>` entry. The work is in verifying
behaviour, not in editing poms.

## `claude-agent-sdk-java-tutorial` — highest value, lowest risk

`claude-agent-sdk.version` is **1.4.0**; **1.5.0** has been released since 2026-08-19. The repo
has not been touched since 2026-06-16 and is clean.

The 1.5.0 release notes state that no public API changed and that every 1.4.0 program compiles
against 1.5.0 unmodified, so the bump itself is mechanical. What makes this the one to do first
is that 1.5.0 corrects a behaviour the tutorial actively demonstrates:

- On 1.4.0, a no-argument `connect()` substitutes the literal string `"Hello"` and sends it as a
  user message, contradicting the documented contract and billing a model turn the caller never
  requested. 1.5.0 starts and initialises the session and writes nothing.
- There are exactly four no-argument `connect()` call sites:
  - `doc-fragments/.../SessionsFragments.java:88` — commented `// Connect without initial prompt`
  - `doc-fragments/.../SessionsFragments.java:128`
  - `module-12-session-fork/.../SessionForkExample.java:58`
  - `module-12-session-fork/.../SessionForkExample.java:78`

The first of those is a tutorial teaching, in a comment, exactly the behaviour that 1.4.0 does
not deliver. Today the tutorial is wrong about its own example. The bump fixes it.

Also worth carrying: the 1.5.0 dependency-floor correction. A no-BOM consumer on 1.4.0 resolves
Jackson 2.21.2 / 3.0.3 with 23 known vulnerabilities, 8 HIGH. This tutorial is a no-BOM consumer.

**Sizing:** one property, then rebuild and re-run module-12 and confirm the fork example still
reads correctly with the corrected semantics. Prose in `doc-fragments` may need a sentence about
what `connect()` now does.

## `acp-java-tutorial` — small, but crosses a breaking release

ACP's own coordinates are already current: `acp-sdk.version` is **0.15.0** and
`acp-autoconfig.version` is **0.11.1**, both the head of their Maven Central metadata. The repo
was updated for the released 0.15.0 SDK on 2026-08-21. Nothing to do there.

The stale entry is `agentworks.version`, still **1.6.0** against a released **1.16.0**. That is
not a cosmetic gap: BOM 1.6.0 pins `agent-client-core` and `agent-claude` at **0.20.0**, while
1.16.0 pins **0.28.0**. The jump crosses 0.26.0's intentional breaking cleanup and 0.25.0's
Spring Boot auto-configuration fix.

Exposure is contained. Only `module-32-agent-client` consumes the BOM, it holds two Java files,
and neither references the Vendir context advisor or the Git-repository DSL that 0.26.0 removed.
The bump therefore looks mechanical, but it should be compiled and run rather than assumed.

**Sizing:** one property, one module, one build-and-run check.

## `agent-judge-tutorial` — small, but gated

`agent-judge.version` is **0.14.0** against a released **0.15.0**, inherited by 11 poms from one
root property.

**This one should not move yet.** The source work order holds `agent-judge` out of scope because
an unresolved release-truth investigation is in flight on branch `release-truth-sbom` in
`/home/mark/worktrees/agent-judge-release-truth`. Bumping the tutorial asserts that 0.15.0 is the
version to teach, which is the very question that investigation is settling. Sequence this after
it closes.

Two secondary items to fold in when it does:

- `langchain4j.version` is **1.18.1**. The documentation site's Agent Judge matrix has been
  corrected to **1.19.0** on branch `step-2.4e-langchain4j-1.19.0-docs-correction`. The tutorial
  and the matrix should land on the same number, whichever is chosen.
- `koog.version` is **1.1.1**; not verified against upstream in this sweep.

## `agent-judge-tutorial-steward` — prose only

No `pom.xml` anywhere. It carries agent-judge references at **0.11.0**, **0.14.0**, and
**0.15.0** simultaneously in markdown. Historical records in a steward log are legitimately
frozen, so this needs a read rather than a substitution: date-stamped acceptance records stay,
"the current version is" statements do not.

**Sizing:** trivial, and it should follow `agent-judge-tutorial` so both land on one number.

## Recommended sequence

1. `claude-agent-sdk-java-tutorial` → 1.5.0. Unblocked, fixes a demonstrably wrong example, and
   clears a real dependency-floor exposure.
2. `acp-java-tutorial` → `agentworks.version` 1.16.0. Unblocked, one module.
3. Wait for the agent-judge release-truth investigation to close.
4. `agent-judge-tutorial` → 0.15.0, with the LangChain4j number reconciled against the site matrix.
5. `agent-judge-tutorial-steward` prose, following step 4.

Steps 1 and 2 are independent and can run in parallel.
