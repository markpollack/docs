# AgentWorks 1.21.0 documentation currency handback

Execution date: 2026-09-22. Branch: `docs/agentworks-1.21.0-currency`.
Execution baseline: `3cc5614`; publication baseline: `510ffff`.

## Scope and step results

- **1.0 complete:** resumed the existing branch, already checked out at `3cc5614`. Initial worktree clean; branch descended from main; its only diff from main was this prior report. Fetched origin and verified main and origin/main both at `510ffff79254ea68211547403146863e97aaec48`. No branch created. No steward learning file written.
- **1.1 complete:** regenerated both Managed Artifacts tables directly from the supplied POM, then compared it byte-for-byte with the Central-resolved POM. There are **85 total dependency-management entries, 76 non-placeholder AgentWorks coordinates, and nine excluded property-based third-party entries**. The tables contain 76 rows (71 Agent Engineering, five ACP), including four new rows. All 72 existing per-artifact project links are preserved.
- **1.2 requested release targets complete; additional snapshot claim unresolved:** audited all version claims on all nine named pages, including frontmatter, prose, headings, cards, Maven and both Gradle forms. Corrected current stable recommendations and verified already-correct claims. The ACP snapshot section contradicts itself and has no authorized target; its snapshot values were not improvised. See limitations below.
- **1.3 complete:** all twelve chips match the BOM; nine stale values corrected (BOM chip was already handled in 1.2). Markup, order, colors, hrefs and the three already-correct chips are unchanged.
- **2.0a complete:** four new narrative bullets and current heading. The baseline region from the 1.18.0 bullet to `## Managed Artifacts` is byte-identical.
- **2.0b complete:** six new dated sections, in the existing heading/plain-bullet format. The 1.16.0 section and all following bytes are unchanged. Dates come from local release tags: 1.17.0 August 24; 1.18.0, 1.19.0 and 1.19.1 August 25; 1.20.0 August 28; 1.21.0 September 17. The 1.19.1 correction takes precedence over 1.19.0's retracted claims. The 1.20.0 entry uses the actual v1.19.1..v1.20.0 POM diff, including removal of Jackson management, checked against the supplied 1.21.0 notes.
- **2.1 complete for requested version/release scope:** reviewed all eight member pages. Seven received current-version corrections and/or new release entries; Judge needed only the two current-label fixes in 1.2. No changelog section was invented for Bench or Judge. Experiment dependency claims came from its released 0.9.0 child POMs, not BOM sibling pins.
- **2.5 and 3.0 intentionally skipped:** no talk, no root What's New edit or reordering, no examples page, no navigation change, no tutorial expansion.
- **4.0 handback:** this report replaces the prior stop report and is committed with the changes. Push is restricted to this working branch. Publication and fresh-consumer example acceptance remain with docs-steward.

## Per-file account and complete current-version inventory

Line numbers below refer to the execution baseline unless stated otherwise. Each file's surrounding design, examples and existing historical prose were retained except for the explicitly listed current claims.

| File | Changed or verified current claims | Deliberately left alone |
|---|---|---|
| `index.mdx` | ACP highlight at 80: 0.14.0 → 0.17.0; BOM prose at 101 and chip at 104: 1.18.0 → 1.21.0. Chips: Client 0.29.3 → 0.31.0; Workflow 0.12.1 → 0.12.3; Claude SDK 1.5.1 → 1.7.0; ACP 0.16.1 → 0.17.0; Hooks 0.8.2 → 0.8.3; Journal 1.8.2 → 1.10.1; Experiment 0.7.1 → 0.9.0; Bench 0.6.1 → 0.6.3. | Judge 0.17.0, Memory 0.5.1, Sandbox 0.10.2 verified. Journal “New in 1.5.0” is introduction history. Boot 3.5/4 are verification scenarios, not member pins. Chip styling and layout unchanged. |
| `projects/agentworks-bom.mdx` | Maven import 1.18.0 → 1.21.0; current release heading → 1.21.0; four release bullets added. Regenerated every row from POM: Client 31 × 0.31.0; Judge 10 × 0.17.0; Workflow 8 × 0.12.3; Journal 7 × 1.10.1; ACP 5 × 0.17.0; Hooks 4 × 0.8.3; Experiment 3 × 0.9.0; Sandbox 3 × 0.10.2; Bench 2 × 0.6.3; Memory 2 × 0.5.1; Claude SDK 1 × 1.7.0. New rows: agent-acp, agent-junie, agent-starter-junie, junie-cli-capture. | Entire existing release history preserved; all existing project links preserved. Property-based third-party entries excluded as instructed. |
| `projects/agent-client.mdx` | Sole current version line at 18: 0.29.3 → 0.31.0, exclusively in 1.2. Added 0.31.0 entry for interrupt/close behavior from GitHub release. | Entire baseline region beginning **0.29.0:** unchanged, including 0.23.0 highlights, historical SDK/framework dependencies, and 1.12.0+ compatibility claim within 0.24.0 history. Step 2.1 did not edit the current-version line. |
| `docs/agent-journal/getting-started.mdx` | Frontmatter at 3, Maven snippet at 19, and current path-containment limitation at 97: 1.8.0 → 1.10.1. | Maven 3.9 prerequisite, Java floor and sample event/cost values unchanged. The path-containment limitation was checked against tagged 1.10.1 source before updating its current-release label. |
| `docs/agent-journal/api-reference.mdx` | Frontmatter at 3, API scope at 6, all six coordinates at 12–17, repository setter limitation at 38 and 48, missing config(Map) at 47, missing five-argument TokenUsage.of at 93, and path-containment limitation at 156: 1.8.0 → 1.10.1. | Java floors, methods, examples and API descriptions unchanged. Tagged RunBuilder, DefaultRun and TokenUsage are unchanged from 1.8.0; JsonFileStorage diff adds raw-directory support without changing the documented containment limitation. |
| `docs/agent-workflow/trace-capture.mdx` | workflow-flows Maven pin at 163: 0.10.0 → 0.12.3; agent-client-core and agent-claude pins at 170/175: 0.29.0 → 0.31.0. BOM text at 179: 1.1.0+ → 1.21.0. | Trace examples and prose unchanged. The former minimum was deliberately converted to a current BOM recommendation under the plan's specific instruction, not treated as stale by default. |
| `docs/acp-java-sdk/reference/java.md` | Stable heading at 13; four Maven versions at 21/31/41/52; four Groovy pins at 60/63/64/65; four Kotlin pins at 70/73/74/75; stable replacement operand at 93: 0.15.0 → 0.17.0. | Snapshot versions at 78/93 unresolved; all API introduction annotations 0.12.0/0.14.0 and protocol feature history unchanged. No snapshot repository used in verification. |
| `projects/agent-judge.mdx` | Install heading at 54: 0.15 → 0.17; Getting Started card at 72: 0.15 → 0.17. Existing What's New label, core Maven snippet, release/migration links already at 0.17 verified. | No new changelog, no talk or 2.5 framing change. Historical 0.14 migration resource, license history and Java 21 floor retained. Existing four-status overview is flagged below rather than expanded in this currency run. |
| `projects/acp-java-sdk.mdx` | Current release line at 12: 0.16.1 → 0.17.0. | Entire 0.15.0 release paragraph, including old Jackson/Jetty dependencies and 0.14.0 upgrade history, unchanged. |
| `docs/agentworks-bom/whats-new.mdx` | Added six sections 1.17.0 through 1.21.0 using release-tag dates and this page's format. | Frontmatter generator claim retained and flagged. Everything from 1.16.0 onward unchanged. |
| `projects/agent-workflow.mdx` | Current release line and Source Code card: 0.12.1 → 0.12.3. Added blockquote entry for NOT_APPLICABLE gate handling. | Entire 0.10.0 historical paragraph, including 0.9/0.8/0.7 introduction history and Spring dependency versions, unchanged. |
| `projects/agent-bench.mdx` | All five current claims: latest-release notice, two Maven snippets, git checkout command, Source card: 0.6.1 → 0.6.3. | No changelog region exists; none added. Examples, benchmark descriptions and execution boundaries retained. |
| `projects/agent-experiment.mdx` | Current line and Maven snippet: 0.7.1 → 0.9.0. Added prose release entry in Release and Compatibility. Released 0.9.0 POM evidence updates module dependencies: Judge 0.17.0, Journal 1.10.0, Claude SDK 1.6.0, Workflow 0.12.3, Client 0.30.0. Standalone Journal/Capture paragraph: 1.8.2 → 1.10.0. | Jackson 2.22.2 and 3.2.2 verified unchanged in released POM. Existing Version 0.6.0 paragraph and 0.5/0.13 compatibility history byte-identical. CycloneDX 1.6 and BSL 1.1 are specification/license numbers. D1 classifications unchanged; dependency edits are separately authorized by 2.1. |
| `projects/claude-agent-sdk.mdx` | Current release line and Maven snippet: 1.5.1 → 1.7.0. Added 1.7.0 entry for process-tree termination before stream closure. | Existing 1.5.0 changelog, 1.4.0 vulnerability warning, 1.5.0 connect() introduction history and dependency versions unchanged. Java 21 minimum and Apache 2.0 retained. |
| `projects/agent-hooks.mdx` | Current release line and four Maven snippets: 0.8.2 → 0.8.3. Added 0.8.3 entry for provided-scope Claude SDK alignment. | Existing 0.7.0 paragraph and its Spring AI/Boot/Claude dependency history unchanged. Java 17/21 floors retained. |
| `projects/agent-journal.mdx` | Current release line, journal-core Maven snippet and API-reference card: 1.8.2 → 1.10.1. Added introductory release paragraph for adapter SDK alignment. | Existing Release 1.8.0 introduction paragraph unchanged. Existing six-module presentation retained; omitted Junie module flagged below. Runtime floors retained. |
| `plans/codex-report.md` | Replaced prior mismatch-only report with this execution account, findings dispositions and validation evidence. | No steward-repository files modified. |

## D1: all 21 AHEAD findings remain false positives

No finding was reclassified, and no version was downgraded in response to an AHEAD finding. Each finding is listed below. Experiment's five rows describe dependencies, and were separately corrected only under the explicit Step 2.1 released-POM instruction; this does not make those AHEAD findings valid.

| Baseline location | Misattributed artifact | Matched number | Disposition |
|---|---|---|---|
| `projects/agent-client.mdx:20` | `agent-client-core` | 1.8.0 | D1 no action; historical line preserved |
| `projects/agent-client.mdx:20` | `agent-model` | 1.8.0 | D1 no action; historical line preserved |
| `projects/agent-client.mdx:30` | `agent-claude` | 1.6.0 | D1 no action; historical line preserved |
| `projects/agent-client.mdx:30` | `agent-claude` | 1.12.0 | D1 no action; historical line preserved |
| `projects/agent-client.mdx:30` | `agent-claude` | 1.5.0 | D1 no action; historical line preserved |
| `projects/agent-client.mdx:32` | `claude-code-sdk` | 2.0.0 | D1 no action; historical line preserved |
| `projects/agent-client.mdx:32` | `claude-code-sdk` | 4.0.7 | D1 no action; historical line preserved |
| `projects/agent-experiment.mdx:51` | `experiment-core` | 0.15.1 | D1 no action; separately verified dependency update under 2.1 |
| `projects/agent-experiment.mdx:51` | `experiment-core` | 1.8.2 | D1 no action; separately verified dependency update under 2.1 |
| `projects/agent-experiment.mdx:52` | `experiment-claude` | 1.5.1 | D1 no action; separately verified dependency update under 2.1 |
| `projects/agent-experiment.mdx:53` | `experiment-workflow` | 0.12.1 | D1 no action; separately verified dependency update under 2.1 |
| `projects/agent-experiment.mdx:53` | `experiment-workflow` | 0.29.3 | D1 no action; separately verified dependency update under 2.1 |
| `projects/agentworks-bom.mdx:40` | `agent-claude` | 1.14.0 | D1 no action; historical line preserved |
| `projects/agentworks-bom.mdx:40` | `agent-claude` | 1.6.0 | D1 no action; historical line preserved |
| `projects/agentworks-bom.mdx:40` | `agent-claude` | 1.5.0 | D1 no action; historical line preserved |
| `projects/agentworks-bom.mdx:40` | `agent-claude` | 1.12.0 | D1 no action; historical line preserved |
| `projects/agentworks-bom.mdx:40` | `agent-claude` | 1.13.0 | D1 no action; historical line preserved |
| `projects/agentworks-bom.mdx:42` | `gemini-cli-capture` | 1.12.0 | D1 no action; historical line preserved |
| `projects/agentworks-bom.mdx:44` | `claude-code-sdk` | 1.10.0 | D1 no action; historical line preserved |
| `projects/agentworks-bom.mdx:44` | `claude-code-sdk` | 1.11.0 | D1 no action; historical line preserved |
| `projects/agentworks-bom.mdx:44` | `claude-code-sdk` | 2.0.0 | D1 no action; historical line preserved |

## D2: every protected STALE finding skipped

The following checker findings are historical or introductory claims, not current recommendations. Duplicate findings are retained here so all 128 findings have a traceable disposition. Other STALE findings were corrected by regeneration or targeted current-claim edits, including the explicitly authorized BOM minimum conversion.

| Baseline location | Artifact attributed by checker | Number left unchanged | Reason |
|---|---|---|---|
| `docs/agent-judge/built-in-judges.mdx:116` | `agent-judge-ai-core` | 0.16.0 | Protected introduction: New in 0.16.0; entire file untouched |
| `projects/agent-client.mdx:20` | `agent-client-core` | 0.29.0 | Dated release history; preserve what shipped then |
| `projects/agent-client.mdx:20` | `agent-model` | 0.29.0 | Dated release history; preserve what shipped then |
| `projects/agent-client.mdx:22` | `agent-antigravity` | 0.28.0 | Dated release history; preserve what shipped then |
| `projects/agent-client.mdx:22` | `agent-grok` | 0.28.0 | Dated release history; preserve what shipped then |
| `projects/agent-client.mdx:22` | `antigravity-cli-sdk` | 0.28.0 | Dated release history; preserve what shipped then |
| `projects/agent-client.mdx:22` | `grok-cli-sdk` | 0.28.0 | Dated release history; preserve what shipped then |
| `projects/agent-client.mdx:22` | `agent-starter-antigravity` | 0.28.0 | Dated release history; preserve what shipped then |
| `projects/agent-client.mdx:22` | `agent-starter-grok` | 0.28.0 | Dated release history; preserve what shipped then |
| `projects/agent-client.mdx:30` | `agent-claude` | 0.24.0 | Dated release history; preserve what shipped then |
| `projects/agent-client.mdx:30` | `agentworks-bom` | 0.24.0 | Dated release history; preserve what shipped then |
| `projects/agent-client.mdx:30` | `agentworks-bom` | 1.6.0 | Dated release history; preserve what shipped then |
| `projects/agent-client.mdx:30` | `agentworks-bom` | 1.12.0 | Dated release history; preserve what shipped then |
| `projects/agent-client.mdx:30` | `agentworks-bom` | 1.5.0 | Dated release history; preserve what shipped then |
| `projects/agent-client.mdx:32` | `claude-code-sdk` | 0.23.0 | Dated release history; preserve what shipped then |
| `projects/agent-client.mdx:32` | `claude-code-sdk` | 0.21.0 | Dated release history; preserve what shipped then |
| `projects/agent-client.mdx:32` | `claude-code-sdk` | 1.4.0 | Dated release history; preserve what shipped then |
| `projects/agentworks-bom.mdx:40` | `agent-claude` | 0.24.0 | Dated release history; preserve what shipped then |
| `projects/agentworks-bom.mdx:42` | `gemini-cli-capture` | 1.5.0 | Dated release history; preserve what shipped then |
| `projects/agentworks-bom.mdx:44` | `claude-code-sdk` | 1.4.0 | Dated release history; preserve what shipped then |
| `projects/agentworks-bom.mdx:44` | `claude-code-sdk` | 0.10.0 | Dated release history; preserve what shipped then |

Additional D2 skips outside the checker are enumerated in the per-file table: homepage Journal introduction, all ACP feature-introduction annotations, Client historical blocks and compatibility minimum, Workflow's 0.10.0 block, Claude SDK history and vulnerability warning, Hooks 0.7.0 block, Journal 1.8.0 introduction, Experiment 0.6.0 compatibility paragraph, Judge's 0.14 migration resource, and historical BOM entries. Java/Maven floors, framework verification scenarios, specification versions, license versions and numeric example data are not artifact pins.

## Limitations, mismatches and deferred work

1. **Step 1.2 snapshot subtask could not be completed:** `docs/acp-java-sdk/reference/java.md` baseline line 78 says `Snapshot (0.15.0-SNAPSHOT)`, while line 93 recommends `0.16.0-SNAPSHOT`. No replacement snapshot is specified or verified by the supplied release-only plan. Left those values untouched, corrected only the stable-version operand to 0.17.0, and continued independent steps. Thus the stable-release targets are complete, but this page still has an unresolved current snapshot recommendation. No invented snapshot fix.
2. **BOM changelog generator ownership unknown:** its description says “auto-generated from git history.” The checkout contains a BOM table generator, but I could not tell whether a generator elsewhere owns the changelog. Added the requested entries anyway as instructed; they could be overwritten by an external generation workflow. Frontmatter unchanged.
3. **Existing member-page prose outside version/release scope:** Judge's overview lists only four statuses despite the released fifth status; Journal's module presentation still lists six artifacts and omits Junie. Flagged for steward review. No unscheduled semantic rewrite or module-table expansion performed. The mandated BOM table does include Junie.
4. **Explicitly deferred:** all of Stage 2.5, all of Stage 3.0, root `whats-new.mdx`, `docs.json`, Judge tutorial and the tutorial repository. Protected `docs/agent-judge/built-in-judges.mdx` is byte-identical. No design changes, main merge, main push, or publication.

## Validation and evidence

- Scratch evidence: `/tmp/docs-currency-20260922/` (not committed). Includes the parsed 76-coordinate list, Maven logs, fetched release bodies, Experiment POMs, exact artifact results and link-check results.
- Central POM: `m2/io/github/markpollack/agentworks-bom/1.21.0/agentworks-bom-1.21.0.pom`; byte-identical to the supplied POM. Maven repository started empty. Both user and global settings were replaced by a scratch settings file mirroring all repositories to `https://repo.maven.apache.org/maven2`; no credentials or snapshot repositories were used.
- Ran `org.apache.maven.plugins:maven-dependency-plugin:3.8.1:get` with explicit `groupId:artifactId:version:packaging` and `-Dtransitive=false`: **82/82 passed** (all 76 current managed JARs plus six BOM release POMs). This checks artifact existence, not fresh-consumer transitive compatibility; that acceptance remains with docs-steward.
- **190/190 historical member POMs returned HTTP 200** for the five older tagged BOMs used in new release entries. Historical published pins were not inferred from checker numbers.
- Eight actual GitHub release URLs returned **200**, including `markpollack/claude-agent-sdk-java/releases/tag/v1.7.0`; deliberately wrong `agent-client/releases/tag/v999.999.999` returned **404**. Release bodies supplied the member entries.
- Experiment 0.9.0's three published flattened child POMs verify each dependency-table claim and the standalone Journal/Capture/Jackson versions. An initial lookup using the repository name as parent artifact returned 404; child coordinates were used as the authoritative published module evidence, with no guessed parent claim written.
- Tagged Journal source comparison verifies the additional current API-limit labels without changing implementation descriptions.
- Scripted bidirectional BOM comparison: 76 unique rows; all POM members represented; every row matches; all existing per-artifact links retained.
- All twelve homepage chips checked against representative artifacts; values-only chip change verified after normalizing version numbers.
- Protected historical blocks compared against **3cc5614**, not intermediate edits. Root What's New, navigation, protected introduction page and tutorial byte-identical. No requirements-judges example page created.
- **195 internal page/asset links across all changed documentation files resolve to existing repository files**, including pre-existing links. `docs.json` parses. `git diff --check` passes.
- Main and origin/main remain at the publication baseline. Final branch push and clean-worktree verification are performed after committing this report; no push to main is authorized.

## Change commits

- `5e04bc7` docs: regenerate managed artifacts from AgentWorks BOM 1.21.0
- `d0bb695` docs: correct current release recommendations to the 1.21.0 train
- `a5b6b31` docs: align all homepage release train chips with BOM 1.21.0
- `b66ca34` docs: add BOM 1.17 through 1.21 release history in page-native formats
- `7753082` docs: align Journal API limitation claims with the current release
- `d6b622a` docs: update member project releases and verified standalone dependency claims
