# Agent Suite Release Roadmap

> **Goal**: Make every project referenced in the "I Read My Agent's Diary" blog post publicly accessible and released to Maven Central (where applicable), then bundle into an agentworks BOM.
>
> **Last updated**: 2026-03-31 (ALL PHASES COMPLETE — 11 projects + BOM on Maven Central, renamed to AgentWorks)

---

## Phase 1: Make Repos Public

Three markpollack/ repos currently return 404. All have been audited: zero tuvium references in tracked files, zero commits between 9am-5pm EST.

- [x] `markpollack/agent-journal` — **PUBLIC**
- [x] `markpollack/agent-experiment` — **PUBLIC**
- [x] `markpollack/experiment-code-coverage-v1` — **PUBLIC** (squashed to 6 commits)
- [x] `markpollack/experiment-code-coverage-v2` — **PUBLIC** (has v2.0.0 tag)

### Verification
```bash
for repo in agent-journal agent-experiment experiment-code-coverage-v1 experiment-code-coverage-v2; do
  curl -s -o /dev/null -w "$repo: %{http_code}\n" "https://github.com/markpollack/$repo"
done
# All should return 200
```

---

## Phase 2: Rename agent-harness -> agent-workflow

Per `~/projects/agent-harness/plans/ROADMAP.md`. Git remote already points to `markpollack/agent-workflow`. Rename before first public release so names are correct from day one.

### Module renames
| Current | Target |
|---------|--------|
| harness-api | workflow-api |
| harness-patterns | workflow-core |
| agent-flows | workflow-flows |
| harness-tools | workflow-tools |
| harness-agents | workflow-agents |
| harness-examples | workflow-examples |

### Package rename
`io.github.markpollack.harness.*` -> `io.github.markpollack.workflow.*`

### Steps
- [x] Rename module directories (git mv)
- [x] Update all pom.xml (artifactId, module, dependency references)
- [x] Update all Java package declarations and imports
- [x] Update agent-workflow CLAUDE.md module references (done — 34 harness refs -> 0)
- [x] Rename local directory: ~/projects/agent-harness -> ~/projects/agent-workflow
- [x] Build passes (workflow-api, workflow-core, workflow-tools, workflow-flows)
- [x] Commit and push

> **Note**: workflow-agents and workflow-examples have pre-existing compilation failures (Spring AI API breaking changes in AnthropicChatModel). These are unrelated to the rename and need separate fixing before release.

---

## Phase 3: Release Infrastructure

### Community repos (spring-ai-community/)
- **Org-level shared secrets** already configured: MAVEN_USERNAME, MAVEN_PASSWORD, GPG_SECRET_KEY, GPG_PASSPHRASE
- **Parent POM**: `spring-ai-community-parent:1.0.1` (defines release profile with central-publishing-maven-plugin, GPG signing)
- **Shared workflows**: `community-workflows` repo provides `maven-central-release.yml`, `publish-snapshot.yml`
- **Release trigger**: Manual `workflow_dispatch` with version input
- **No per-repo secret setup needed** — org secrets inherited automatically

### Personal repos (markpollack/)
- **No shared secrets** (GitHub limitation for personal orgs)
- **Each repo needs 4 secrets**: MAVEN_USERNAME, MAVEN_PASSWORD, GPG_SECRET_KEY, GPG_PASSPHRASE
- **Shared workflows**: `build-tools` repo provides same workflow pattern
- **Parent POM**: Self-contained in each project (defines release profile inline)

### Secrets status

| Repo | MAVEN_USERNAME | MAVEN_PASSWORD | GPG_SECRET_KEY | GPG_PASSPHRASE | Ready |
|------|:-:|:-:|:-:|:-:|:-:|
| spring-ai-community/* (org-level) | Y | Y | Y | Y | Y |
| markpollack/agent-journal | Y | Y | Y | Y | Y |
| markpollack/agent-experiment | Y | Y | Y | Y | Y |
| markpollack/agent-workflow | Y | Y | Y | Y | Y |
| markpollack/loopy | - | - | - | - | **Needs all 4** |

---

## Phase 4: Release to Maven Central

### Tier 0 — No internal SNAPSHOT deps (release first)

| Project | GroupId | Release Version | Maven Central | Git Tag | Status |
|---------|---------|----------------|:---:|:---:|--------|
| claude-agent-sdk-java | org.springaicommunity | 1.0.0 | **Released** | v1.0.0 | Previously released Dec 2025, tag added |
| agent-judge | org.springaicommunity | 0.9.1 | **Released** | v0.9.1 | Released, tag created manually |
| agent-sandbox | org.springaicommunity | 0.9.1 | **Released** | v0.9.1 | Released, tag created manually |
| spring-testing-skills | org.springaicommunity | 0.9.0 | **Released** | v0.9.0 | Full workflow success |
| agent-journal | io.github.markpollack | 0.9.0 | **Released** | v0.9.0 | Released, tag created manually |

### Tier 0 Post-Release — Docs & Discoverability

Each released project needs a minimal public presence before Tier 1 proceeds. Community projects link to https://springaicommunity.mintlify.app, personal projects link to https://lab.pollack.ai.

#### README.md for each released project
- [x] **claude-agent-sdk-java** — Updated to 1.0.0, removed SNAPSHOT note
- [x] **agent-judge** — Created README with Maven Central coordinates and docs link
- [x] **agent-sandbox** — Created README with Maven Central coordinates and docs link
- [x] **spring-testing-skills** — Updated to 0.9.0, removed snapshot repo block
- [x] **agent-journal** — Updated to 0.9.0

#### Tutorial & docs version bumps
- [x] **claude-agent-sdk-java-tutorial** — Bumped SDK dependency to 1.0.0
- [x] **~/community/mintlify-docs** — Updated agent-judge (0.9.1) and agent-sandbox (0.9.1) doc pages
- [x] **~/projects/docs** (lab.pollack.ai) — agent-experiment updated to 0.1.0

#### Workflow fix applied
- [x] `permissions: contents: write` added to release.yml in agent-judge, agent-sandbox, agent-journal (root cause: checkout@v4 uses limited token by default)

### Tier 1 — Depends on Tier 0

| Project | GroupId | Release Version | Maven Central | Git Tag | Status |
|---------|---------|----------------|:---:|:---:|--------|
| agent-client | org.springaicommunity.agents | 0.10.0 | **Released** | v0.10.0 | Released, tag created manually |
| agent-workflow | io.github.markpollack | 0.1.0 | **Released** | v0.1.0 | Full workflow success |

> **Note**: agent-bench is held — still in active development.

#### Tier 1 post-release — Docs & Discoverability
- [x] **agent-client** — Updated community mintlify-docs to 0.10.0
- [x] **agent-client** — README.md updated with 0.10.0 Maven coordinates
- [x] **agent-workflow** — README.md updated with 0.1.0 Maven coordinates and module table

### Tier 2 — Depends on Tier 0+1

| Project | GroupId | Release Version | Maven Central | Git Tag | Status |
|---------|---------|----------------|:---:|:---:|--------|
| agent-experiment | io.github.markpollack | 0.1.0 | **Released** | v0.1.0 | Full workflow success |
| spring-ai-agent-utils | org.springaicommunity | 0.6.0 | **Released** | v0.6.0 | Released (unblocked loopy) |
| loopy | io.github.markpollack | 0.3.0 | **Released** | v0.3.0 | Published, tag existed from prior release |

#### Tier 2 post-release — Docs & Discoverability
- [x] **agent-experiment** — lab.pollack.ai docs updated to 0.1.0
- [x] **loopy** — README.md updated with 0.3.0 Maven coordinates and download link

---

## Phase 5: Experiment Repos (GitHub Release Only)

These are data/analysis repos, not libraries. Published as GitHub Releases, not Maven Central.

### experiment-code-coverage-v2 (reference)
- [x] Made public
- Already has v2.0.0 GitHub Release with reproducibility scripts and data
- Use as the template for v1 alignment

### experiment-code-coverage-v1
- [x] Made public
- Less mature than v2 — needs alignment before creating a GitHub Release
- [x] Investigate v2 GitHub Release structure (tarball contents, release notes, scripts)
- [x] Align v1 repo structure to match v2 conventions:
  - [x] Add README with experiment description, how to reproduce, links to blog
  - [x] Add result + analysis tarballs as release assets
- [x] Create GitHub Release v1.0.0 matching v2 pattern
- [x] Blog link updated from `code-coverage-experiment` to `experiment-code-coverage-v1`

---

## Phase 6: Create agentworks BOM

### 6.1 Create repo `markpollack/agentworks`
- GroupId: `io.github.markpollack`
- ArtifactId: `agentworks-bom`
- Version: `1.0.0`
- Packaging: `pom`

### 6.2 BOM contents (all leaf JARs)
```
io.github.markpollack:journal-core
io.github.markpollack:claude-code-capture
io.github.markpollack:workflow-api
io.github.markpollack:workflow-core
io.github.markpollack:workflow-flows
io.github.markpollack:experiment-core
io.github.markpollack:experiment-claude
org.springaicommunity:spring-testing-skills
org.springaicommunity:agent-judge-core
org.springaicommunity:agent-judge-llm
org.springaicommunity:agent-judge-exec
org.springaicommunity:agent-judge-file
org.springaicommunity:agent-bench-core
org.springaicommunity:agent-sandbox-core
org.springaicommunity:agent-sandbox-docker
org.springaicommunity:agent-sandbox-e2b
org.springaicommunity.agents:TBD (agent-client submodules)
org.springaicommunity:TBD (claude-agent-sdk submodules)
```

### 6.3 Setup
- [x] Create repo with BOM pom.xml
- [x] Add release workflow (build-tools pattern)
- [x] Configure Maven Central secrets
- [x] Release 1.0.0

### 6.4 User experience
```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>io.github.markpollack</groupId>
      <artifactId>agentworks-bom</artifactId>
      <version>1.0.0</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

---

## Execution Order

1. ~~**Phase 1** — Make 4 repos public~~ **DONE**
2. ~~**Phase 2** — Rename agent-harness -> agent-workflow~~ **DONE**
3. ~~**Phase 3** — Verify secrets~~ **DONE**
4. ~~**Phase 4 Tier 0** — Release foundation projects~~ **DONE** (5 projects)
5. ~~**Phase 4 Tier 0 Post-Release** — README.md, tutorial bumps, docs~~ **DONE** (mostly)
6. ~~**Phase 4 Tier 1** — Release agent-client, agent-workflow~~ **DONE**
7. ~~**Phase 4 Tier 2** — Release agent-experiment, loopy, spring-ai-agent-utils~~ **DONE**
8. **Phase 4 Post-Release** — Remaining README.md and docs version updates (in progress)
9. ~~**Phase 5** — Align experiment-code-coverage-v1 with v2 and create GitHub Release~~ **DONE** (v1.0.0 with 2 tarballs)
10. ~~**Phase 6** — Create and release agentworks BOM~~ **DONE** (1.0.0 on Maven Central)

---

---

## Post-Release Plan

All releases shipped. The items below are improvements for the next release cycle, grouped by priority.

### P1 — Do before next release

**agent-client cleanup** (assessed + completed 2026-03-31)
- [x] ~~Rename `spring-ai-agents-starters`~~ — Actively used, 5 provider starters, name is fine
- [x] Renamed `spring-ai-agents-core` to `spring-ai-agent-launcher`
- [x] ~~Rename `spring-ai-agents-judge`~~ — Not a thin wrapper; provides Spring-aware agent-as-judge integration, name is fine
- [x] ~~`spring-ai-spring-boot-starters/spring-ai-starter-agent`~~ — Doesn't exist on disk, removed dead comment
- [x] ~~`agent-models/spring-ai-swebench-agent`~~ — Doesn't exist on disk, removed dead comment
- [x] ~~GroupId `org.springaicommunity.agents` vs `org.springaicommunity`~~ — Intentional: `.agents` for this repo's modules, base for external deps
- [x] ~~Samples version property~~ — Already using `agent-client.version`, not the old name
- [x] Cleaned dead module references from pom.xml and updated README agent list

**Infrastructure**
- [x] Upgraded `flatten-maven-plugin` to 1.6.0 and `central-publishing-maven-plugin` to 0.10.0 in community-parent
- [x] ~~`permissions: contents: write` in reusable workflows~~ — Must be set in each caller (GitHub limitation for `workflow_call`), already applied to all repos

### P2 — Nice to have

**Build consolidation**
- [x] ~~Consolidate build-parent~~ — **Decision**: keep inline release profile for Spring Boot projects. Duplication is minimal (one profile block). A shared parent coupling all projects to a specific Boot version is worse.

**Tools & descriptions**
- [x] Simplified Bash tool description in spring-ai-agent-utils (removed 78 lines of git protocol/examples that caused model fixation, replaced with 13-line concise version)

**Docs & examples**
- [ ] Extract AgentWorks examples from workflow-dsl-examples (competitive analysis repo) into a clean public examples repo — `~/projects/workflow-dsl-examples/` has the "ours" examples, need to strip LC4j comparison code
- [x] Update agent-workflow CLAUDE.md module references (34 harness refs -> 0)

**Agent bench**
- [x] Added `release.yml` to agent-bench
- [x] ~~Push 22 commits~~ — Already pushed

---

## Post-Release Cleanup: agent-client

Deferred cleanup discovered during agent-client 0.10.0 release. Not blocking anything but should be addressed before 0.11.0.

### Legacy naming (assessed 2026-03-31)
- [x] ~~`spring-ai-agents-starters`~~ — Active, 5 provider starters, name is fine
- [x] ~~`spring-ai-agents-core` → `spring-ai-agent-launcher`~~ Done

**agent-client 0.11.0 naming cleanup** — DONE
- [x] Renamed all 19 artifactIds: dropped `spring-ai-` prefix
- [x] Released agent-client 0.11.0 to Maven Central
- [x] Updated AgentWorks BOM to 1.0.2 with new names
- [x] ~~`spring-ai-agents-judge`~~ — Spring-aware agent-as-judge integration, name is fine
- [x] ~~`spring-ai-spring-boot-starters/spring-ai-starter-agent`~~ — Doesn't exist on disk, comment removed
- [x] ~~`agent-models/spring-ai-swebench-agent`~~ — Doesn't exist on disk, comment removed
- [x] ~~GroupId verification~~ — `org.springaicommunity.agents` is intentional for this repo

### Dead code removed during release
- [x] `docs/` module removed (Antora, replaced by Mintlify)
- [x] `samples/` removed from reactor (standalone projects, not published to Central)

### Build infrastructure fixed during release
- [x] Adopted `spring-ai-community-parent` (was missing — no flatten, source, javadoc plugins)
- [x] Removed duplicate plugin declarations from pluginManagement (conflicted with parent)
- [x] Removed stale repo-level GPG secrets overriding org secrets (Sep 2025 keys)
- [x] Upgraded Maven wrapper to 3.9.10 (old 3.8.6 wrapper returned 403)
- [x] Replaced `spring-ai-agents.version` property with `${project.version}`
- [x] Pinned micrometer-observation-test and reactor-test versions (flatten plugin 1.5.0 doesn't resolve BOM-imported dep versions)
- [x] Added `permissions: contents: write` to release.yml for git tagging
- [x] Updated samples to released 0.10.0 version

### Samples
- [x] ~~Samples version property~~ — Already using `agent-client.version` (not the old name)
- [x] ~~Hardcoded version~~ — Samples use `0.10.0` which matches the release

### Community parent gap
- [x] ~~`flatten-maven-plugin` 1.5.0~~ — Upgraded to 1.6.0 in community-parent (also bumped central-publishing to 0.10.0)
