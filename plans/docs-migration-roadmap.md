# Roadmap: Documentation Migration — spring-ai-community to markpollack

> **Created**: 2026-05-16T12:30-04:00
> **Last updated**: 2026-05-16T15:15-04:00

## Overview

Update the lab.pollack.ai docs site (`~/projects/docs/`) and the spring-ai-community site (`~/community/mintlify-docs/`) to reflect 7 migrated repositories. Four stages: inventory and central migration page (Stage 1), mechanical coordinate sweep (Stage 2), per-page migration notes (Stage 3), and spring-ai-community site banner/nav updates (Stage 4).

**Scope**: 7 repositories migrated. 6 of the 7 need Maven coordinate callouts on lab.pollack.ai; the 7th (`claude-agent-sdk-java-tutorial`) needs only URL updates, not a Maven callout. Non-migrated Spring AI Community projects (`spring-ai-a2a`, `spring-ai-agent-utils`, `spring-testing-skills`) are not rewritten, but are removed from active lab.pollack.ai navigation because they are outside the AgentWorks ownership boundary. `acp-java-sdk` is separate: official ACP community repo, `com.agentclientprotocol` groupId, kept on lab.pollack.ai.

**Policy**: Old coordinates and old URLs are allowed only on the central migration page and inside explicit `<Info>` migration callouts. Everywhere else must show the new canonical coordinates.

> **Before every commit**: Verify ALL exit criteria for the current step are met. Do NOT remove exit criteria to mark a step complete — fulfill them.

---

## Mapping Table (reference for all steps)

| Project | Old GitHub | New GitHub | Old GroupId | New GroupId | Version |
|---|---|---|---|---|---|
| claude-agent-sdk-java | `spring-ai-community/` | `markpollack/` | `org.springaicommunity` | `io.github.markpollack` | 1.1.0 |
| agent-sandbox | `spring-ai-community/` | `markpollack/` | `org.springaicommunity` | `io.github.markpollack` | 0.9.2 |
| agent-client | `spring-ai-community/` | `markpollack/` | `org.springaicommunity.agents` | `io.github.markpollack` | 0.18.0 |
| agent-journal | `spring-ai-community/` | `markpollack/` | `org.springaicommunity` | `io.github.markpollack` | 1.1.0 |
| agent-bench | `spring-ai-community/` | `markpollack/` | `org.springaicommunity` | `io.github.markpollack` | 0.3.0 |
| agent-judge | `markpollack/` (already) | `markpollack/` | `org.springaicommunity` | `io.github.markpollack` | 0.10.0 |
| claude-agent-sdk-java-tutorial | `spring-ai-community/` | `markpollack/` | — | — | — (not published) |

**Package name migration**:
- `org.springaicommunity.claude.*` → `io.github.markpollack.claude.*` (claude-agent-sdk-java)
- `org.springaicommunity.agents.*` → `io.github.markpollack.agents.*` (agent-client — note: had a different groupId `org.springaicommunity.agents`, so the package root may not follow the sibling pattern; verify from source)
- `org.springaicommunity.judge.*` → `io.github.markpollack.judge.*` (agent-judge)
- `org.springaicommunity.sandbox.*` → `io.github.markpollack.sandbox.*` (agent-sandbox)
- `org.springaicommunity.journal.*` → `io.github.markpollack.journal.*` (agent-journal)
- `org.springaicommunity.bench.*` → `io.github.markpollack.bench.*` (agent-bench)

> Verify actual package roots from source before replacing — these are the expected patterns but exact sub-packages may differ.

**DO NOT change** (still spring-ai-community, `org.springaicommunity` groupId):
- `spring-ai-a2a` — `spring-ai-community/spring-ai-a2a`
- `spring-ai-agent-utils` — `spring-ai-community/spring-ai-agent-utils`
- `spring-testing-skills` — `spring-ai-community/spring-testing-skills`

**ACP Java SDK** (separate ownership — official ACP community, not spring-ai-community):
- `acp-java-sdk` — `com.agentclientprotocol` groupId, official ACP org repo
- Kept on lab.pollack.ai because it is intentionally supported by AgentWorks
- Do not describe as spring-ai-community

**BOM ownership rule**:
- AgentWorks BOM manages: `io.github.markpollack` artifacts + `com.agentclientprotocol` ACP entries intentionally supported by AgentWorks
- AgentWorks BOM does NOT manage: `org.springaicommunity` artifacts

> Do not change their GitHub URLs, Maven coordinates, package names, or ownership language. It is okay to move them between documentation sections only if the section title is being clarified and their coordinates remain unchanged.

---

## Release Gates

| Project | Gate | Status |
|---|---|---|
| claude-agent-sdk-java 1.1.0 | Maven Central | Confirmed |
| agent-sandbox 0.9.2 | Maven Central | Confirmed |
| agent-client 0.18.0 | Maven Central | Confirmed |
| agent-journal 1.1.0 | Maven Central | Confirmed |
| agent-bench 0.3.0 | Maven Central | Confirmed |
| agent-judge 0.10.0 | Maven Central | Confirmed |

> **Rule**: Do not update docs for any project until its Maven Central release is confirmed. If a release is not yet available, leave current coordinates/version in place and add a TODO in the inventory learnings.

---

## Stage 1: Inventory and Migration Page

### Step 1.0: Inventory and Context Load

**Entry criteria**:
- [x] Read this roadmap fully
- [x] Read: `~/projects/docs/mint.json` (navigation structure)

**Work items**:
- [x] RUN inventory commands to confirm current state:
  ```bash
  # GitHub URLs
  grep -rn "github.com/spring-ai-community" --include="*.mdx" .
  
  # Maven groupIds
  grep -rn "org.springaicommunity" --include="*.mdx" .
  
  # External docs URLs
  grep -rn "springaicommunity.mintlify.app" --include="*.mdx" .
  
  # Package/import names in code examples
  grep -rn "import org.springaicommunity\|package org.springaicommunity" --include="*.mdx" .
  grep -rn "org\.springaicommunity" --include="*.mdx" .
  
  # Badges, shields, Maven Central search links
  grep -rn "central.sonatype.com.*springaicommunity" --include="*.mdx" .
  ```
- [x] CLASSIFY each hit:
  - Migrated project reference → needs update
  - Non-migrated project reference → leave alone
  - Historical/migration context → allowed
- [x] VERIFY release gates: confirm all 6 Maven-published projects are on Maven Central
- [x] RECORD Maven Central artifact URLs in `plans/learnings/step-1.0-inventory.md` (makes "confirmed" auditable)
- [x] DOCUMENT any additional references found beyond this roadmap's mapping table

**Exit criteria**:
- [x] Inventory complete with classified hit list
- [x] All release gates confirmed
- [x] Create: `plans/learnings/step-1.0-inventory.md`
- [x] Update `ROADMAP.md` checkboxes
- [x] COMMIT

---

### Step 1.1: Create Central Migration Page

**Entry criteria**:
- [x] Step 1.0 complete
- [x] Read: `plans/learnings/step-1.0-inventory.md`

**Work items**:
- [x] CREATE `docs/migration/spring-ai-community-to-markpollack.mdx` with:
  - Which repositories moved and why (factual: "repository and release-coordinate cleanup")
  - Old vs new Maven coordinates table (from mapping above)
  - Which Spring AI Community repositories did NOT move (list the three `org.springaicommunity` projects with their correct coordinates)
  - Separate note: `acp-java-sdk` belongs to the official ACP community, not spring-ai-community, and is not part of this migration
  - What users should change in their builds (before/after XML snippets)
  - Package name changes (old imports → new imports)
  - Tone: factual, respectful — not a deprecation of spring-ai-community:
    > Several projects have moved from the `spring-ai-community` GitHub organization to Mark Pollack's personal GitHub namespace as part of a repository and release-coordinate cleanup. Projects that remain under `spring-ai-community` continue to use their existing repositories and coordinates.
- [x] ADD the migration page to `mint.json` navigation
- [ ] VERIFY the page renders locally if Mintlify dev server is available

**Exit criteria**:
- [x] Migration page created with complete coordinate and package mapping
- [x] Page accessible from site navigation
- [x] Create: `plans/learnings/step-1.1-migration-page.md`
- [x] Update `ROADMAP.md` checkboxes
- [x] COMMIT

---

## Stage 2: Mechanical Sweep

### Step 2.0: Stage 2 Entry

**Entry criteria**:
- [x] Stage 1 complete
- [x] Read: `plans/learnings/step-1.1-migration-page.md`

**Work items**:
- [x] REVIEW Stage 1 learnings for any scope changes

**Exit criteria**:
- [x] Ready to proceed with sweep
- [x] Update `ROADMAP.md` checkboxes

---

### Step 2.1: Update GitHub URLs for Migrated Projects

**Entry criteria**:
- [x] Step 2.0 complete

**Work items**:
- [x] UPDATE `projects/agent-client.mdx`: GitHub URL → `markpollack/agent-client`
- [x] UPDATE `projects/agent-sandbox.mdx`: GitHub URL → `markpollack/agent-sandbox`
- [x] UPDATE `projects/agent-bench.mdx`: GitHub URL + clone URL → `markpollack/agent-bench`
- [x] UPDATE `projects/claude-agent-sdk.mdx`: source URL → `markpollack/claude-agent-sdk-java`, tutorial URL → `markpollack/claude-agent-sdk-java-tutorial`
- [x] UPDATE `docs/agent-bench/getting-started.mdx`: clone URL → `markpollack/agent-bench`
- [x] VERIFY:
  ```bash
  grep -rn "github.com/spring-ai-community" --include="*.mdx" . | grep -v "acp-java-sdk\|spring-ai-a2a\|spring-ai-agent-utils\|spring-testing-skills" | grep -v migration
  ```
  Expected: zero hits.

**Exit criteria**:
- [x] Zero old GitHub URLs for migrated repos (except migration page)
- [x] Non-migrated repos unchanged
- [x] Create: `plans/learnings/step-2.1-github-urls.md`
- [x] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

### Step 2.2: Update Maven Coordinates and Versions

**Entry criteria**:
- [x] Step 2.1 complete
- [x] Read: `plans/learnings/step-2.1-github-urls.md`

**Work items**:
- [x] UPDATE `projects/agent-client.mdx`: version 0.16.0 → 0.18.0, groupId → `io.github.markpollack`, Maven Central search URL
- [x] UPDATE `projects/agentworks-bom.mdx`:
  - Move agent-judge, agent-sandbox, agent-bench, agent-journal, `claude-code-sdk` (confirmed artifactId — the publishable module inside the `claude-agent-sdk-java` repo), and agent-client entries from "Community Libraries" and "Agent Client" sections to the "Agent Engineering (io.github.markpollack)" section (create if it doesn't already exist). Note: if `agent-journal` is not currently in the BOM docs page, add it — it is a released `io.github.markpollack` artifact (1.1.0)
  - Update versions to current releases
  - Remove `agent-advisor-judge` (no longer exists in agent-client)
  - After moving migrated entries out, any remaining `org.springaicommunity` entries (`spring-ai-agent-utils`, `spring-testing-skills`) stay temporarily; Step 2.5 removes them and the now-redundant community section header
- [x] UPDATE any other pages with stale Maven coordinates found in Step 1.0 inventory
- [x] VERIFY:
  ```bash
  grep -rn "org.springaicommunity" --include="*.mdx" . | grep -v migration | grep -v "spring-ai-agent-utils\|spring-testing-skills\|spring-ai-a2a"
  ```
  Expected: zero hits (only non-migrated projects should remain).

**Exit criteria**:
- [x] All migrated projects show `io.github.markpollack` with correct versions
- [x] BOM page accurately reflects current architecture
- [x] Non-migrated projects unchanged
- [x] Create: `plans/learnings/step-2.2-maven-coordinates.md`
- [x] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

### Step 2.3: Update External Docs Links

**Entry criteria**:
- [ ] Step 2.2 complete
- [ ] Read: `plans/learnings/step-2.2-maven-coordinates.md`

**Work items**:
- [ ] UPDATE `projects/claude-agent-sdk.mdx`: all `springaicommunity.mintlify.app` links → `lab.pollack.ai` equivalents (or internal paths if content is on this site)
- [ ] UPDATE `projects/agent-client.mdx`: `springaicommunity.mintlify.app` links → `lab.pollack.ai`
- [ ] UPDATE `projects/agent-sandbox.mdx`: `springaicommunity.mintlify.app` link → `lab.pollack.ai`
- [ ] VERIFY:
  ```bash
  grep -rn "springaicommunity.mintlify.app" --include="*.mdx" .
  ```
  Expected: zero hits.

**Exit criteria**:
- [ ] Zero `springaicommunity.mintlify.app` references
- [ ] Create: `plans/learnings/step-2.3-external-links.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

### Step 2.4: Update Package Names in Code Examples

**Entry criteria**:
- [ ] Step 2.3 complete
- [ ] Read: `plans/learnings/step-2.3-external-links.md`

**Work items**:
- [ ] SEARCH for stale package/import references in code examples:
  ```bash
  grep -rn "org\.springaicommunity" --include="*.mdx" . | grep -v migration | grep -v "spring-ai-agent-utils\|spring-testing-skills\|spring-ai-a2a"
  ```
- [ ] UPDATE Java imports/packages in code snippets for migrated projects:
  - `org.springaicommunity.claude.agent.sdk` → `io.github.markpollack.claude.agent.sdk`
  - `org.springaicommunity.agents.*` → `io.github.markpollack.agents.*`
  - `org.springaicommunity.judge.*` → `io.github.markpollack.judge.*`
  - `org.springaicommunity.sandbox.*` → `io.github.markpollack.sandbox.*`
  - `org.springaicommunity.journal.*` → `io.github.markpollack.journal.*`
  - `org.springaicommunity.bench.*` → `io.github.markpollack.bench.*`
- [ ] DO NOT change package names for non-migrated projects (`spring-ai-agent-utils`, etc.)
- [ ] VERIFY no stale package names remain for migrated projects

**Exit criteria**:
- [ ] Code examples use correct `io.github.markpollack` package names
- [ ] Non-migrated projects unchanged
- [ ] Create: `plans/learnings/step-2.4-package-names.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

### Step 2.5: Remove Community-Owned Projects from lab.pollack.ai

**Entry criteria**:
- [ ] Step 2.4 complete
- [ ] Read: `plans/learnings/step-2.4-package-names.md`

**Work items**:
- [ ] REMOVE from `mint.json` navigation:
  - `projects/agent-tools` (= `spring-ai-agent-utils`) — currently in "AgentWorks" group
  - `projects/spring-ai-a2a` — currently in "Supporting Projects" group
- [ ] KEEP page files accessible by direct URL (don't break inbound links), but add a short `<Info>` note explaining these are community projects no longer covered by AgentWorks (use `<Info>` not `<Warning>` — content is accurate, just out of scope; different from Stage 4's `<Warning>` which signals potentially stale content):
  - `projects/agent-tools.mdx`
  - `projects/spring-ai-a2a.mdx`
- [ ] KEEP `projects/acp-java-sdk` in "Supporting Projects" — official ACP community project, intentionally supported by AgentWorks for now; future migration to `markpollack` is a separate task
- [ ] REMOVE all community deps from `projects/agentworks-bom.mdx`:
  - Remove "Community Libraries (org.springaicommunity)" section entirely (`spring-ai-agent-utils`, `spring-testing-skills`, and any old migrated-project entries)
  - Remove "Agent Client (org.springaicommunity.agents)" section header (should already be empty after Step 2.2 moved its entries to the markpollack section)
  - Projects that need `spring-ai-agent-utils` or `spring-testing-skills` already manage versions locally
- [ ] REMOVE community deps from the actual BOM POM at `~/projects/agentworks/pom.xml`:
  - Remove `spring-ai-agent-utils` managed dependency
  - Remove `spring-testing-skills` managed dependency
  - Remove any `org.springaicommunity` or `org.springaicommunity.agents` entries (migrated projects should already be under `io.github.markpollack`)
  - Keep `com.agentclientprotocol` ACP entries — intentionally managed by AgentWorks; future migration is a separate task
- [ ] UPDATE "Supporting Projects" nav group — now contains only `claude-agent-sdk` and `acp-java-sdk`
- [ ] VERIFY no dangling nav references in `mint.json`

> **Future task (not this roadmap)**: Migrate `acp-java-sdk` repo from ACP org to `markpollack` GitHub. Update groupId from `com.agentclientprotocol` to `io.github.markpollack`. Same pattern as the other migrations.

**Exit criteria**:
- [ ] Community-owned projects (`agent-tools`, `spring-ai-a2a`) no longer in lab.pollack.ai navigation
- [ ] ACP and Claude SDK remain in "Supporting Projects"
- [ ] BOM page cleaned of community deps that are managed locally by consumers
- [ ] No broken nav links
- [ ] Create: `plans/learnings/step-2.5-remove-community-projects.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

## Stage 3: Migration Notes and Final Verification

### Step 3.0: Stage 3 Entry

**Entry criteria**:
- [ ] Stage 2 complete
- [ ] Read all Stage 2 learnings files

**Work items**:
- [ ] REVIEW for any remaining issues from Stage 2

**Exit criteria**:
- [ ] Ready for migration notes
- [ ] Update `ROADMAP.md` checkboxes

---

### Step 3.1: Add Per-Page Migration Callouts

**Entry criteria**:
- [ ] Step 3.0 complete

**Work items**:
- [ ] ADD migration note to pages for repos that moved from spring-ai-community GitHub:
  - `projects/agent-client.mdx`
  - `projects/agent-sandbox.mdx`
  - `projects/agent-bench.mdx`
  - `projects/claude-agent-sdk.mdx`
  - `projects/agent-journal.mdx`

  Use this callout:
  ```mdx
  <Info>
  This project has moved from the `spring-ai-community` GitHub organization to
  `markpollack`. New releases are published under the Maven groupId
  `io.github.markpollack`, and Java packages now use the `io.github.markpollack`
  namespace. If you previously used `org.springaicommunity`, update your
  dependency coordinates and imports to the current values shown below.
  </Info>
  ```

  For **agent-client** specifically, mention the special old groupId:
  ```mdx
  <Info>
  This project has moved from `spring-ai-community/agent-client` to
  `markpollack/agent-client`. The Maven groupId changed from
  `org.springaicommunity.agents` to `io.github.markpollack`.
  </Info>
  ```

- [ ] ADD migration note to `projects/agent-judge.mdx` (different copy — repo was already markpollack, only groupId changed):
  ```mdx
  <Info>
  This project now publishes new releases under the Maven groupId
  `io.github.markpollack`. If you previously used `org.springaicommunity`,
  update your dependency coordinates to the current values shown below.
  </Info>
  ```

- [ ] VERIFY `claude-agent-sdk-java-tutorial` references already point to new GitHub URL (fixed in Step 2.1); no Maven callout needed

**Exit criteria**:
- [ ] All 6 Maven-published project pages have appropriate migration notes
- [ ] Tutorial references point to new GitHub URL
- [ ] Notes are factual, non-alarming, and use correct variant copy per project
- [ ] Create: `plans/learnings/step-3.1-migration-notes.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

### Step 3.2: Final Verification and Consolidation

**Entry criteria**:
- [ ] Step 3.1 complete
- [ ] Read: `plans/learnings/step-3.1-migration-notes.md`

**Work items**:
- [ ] RUN full verification suite:
  ```bash
  # Broad sweep — any remaining spring-ai-community refs for migrated repos?
  grep -rn "spring-ai-community" --include="*.mdx" . | grep -v migration | grep -v "acp-java-sdk\|spring-ai-a2a\|spring-ai-agent-utils\|spring-testing-skills"
  
  # Any remaining old groupIds for migrated repos?
  grep -rn "org.springaicommunity" --include="*.mdx" . | grep -v migration | grep -v "spring-ai-agent-utils\|spring-testing-skills\|spring-ai-a2a"
  
  # Any stale external docs URLs?
  grep -rn "springaicommunity.mintlify.app" --include="*.mdx" .
  
  # Non-migrated spring-ai-community projects (should still exist if pages kept)
  grep -rn "spring-ai-community/spring-ai-a2a\|spring-ai-community/spring-ai-agent-utils\|spring-ai-community/spring-testing-skills" --include="*.mdx" .
  
  # Stale package names?
  grep -rn "import org.springaicommunity\|package org.springaicommunity" --include="*.mdx" . | grep -v migration | grep -v "spring-ai-agent-utils\|spring-testing-skills"
  
  # Raw broad sweep (no negative filters) for final manual classification
  grep -rn "spring-ai-community\|org.springaicommunity\|springaicommunity.mintlify.app" --include="*.mdx" .
  ```
- [ ] MANUALLY classify ALL hits from the raw broad sweep:
  - Intentional non-migrated reference → OK
  - Migration page/callout reference → OK
  - Missed stale reference → fix
- [ ] COMPACT learnings into `plans/learnings/LEARNINGS.md`
- [ ] UPDATE this roadmap — mark all steps complete

**Exit criteria**:
- [ ] Filtered verification commands pass clean; raw broad sweep has only manually classified expected hits
- [ ] `plans/learnings/LEARNINGS.md` updated with full migration learnings
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

## Stage 4: Spring AI Community Site — Move to "Moved Projects"

> **Repo**: `~/community/mintlify-docs/` (published at `springaicommunity.mintlify.app`)
>
> **Principle**: Leave existing content in place (don't break links). Add banners pointing to new home. Move migrated projects from "Agentic" to "Moved Projects" in navigation. Content goes stale naturally — that's fine because the banner redirects people.

### Step 4.0: Stage 4 Entry

**Entry criteria**:
- [ ] Stage 3 complete (lab.pollack.ai docs are canonical and correct)
- [ ] Read: `plans/learnings/LEARNINGS.md`

**Work items**:
- [ ] INVENTORY migrated project pages on spring-ai-community site:
  ```bash
  cd ~/community/mintlify-docs
  ls projects/incubating/agent-client.mdx projects/incubating/agent-judge.mdx \
     projects/incubating/agent-sandbox.mdx projects/incubating/agent-bench.mdx
  ls claude-agent-sdk/index.mdx
  ```
- [ ] VERIFY whether `agent-journal` has a community-site page:
  ```bash
  ls projects/incubating/agent-journal.mdx 2>/dev/null || echo "No community page for agent-journal"
  ```
  If present, include it in Steps 4.1 and 4.2. If absent, record in learnings.
- [ ] IDENTIFY all tutorial/reference/howto pages for migrated projects (Agent Client has full doc tree, Claude SDK has 23-module tutorial)
- [ ] CHECK if `claude-agent-sdk-java-tutorial` has a separate nav entry beyond the Claude SDK tutorial tree; if so, include it in Step 4.2 moves
- [ ] VERIFY each target `lab.pollack.ai/projects/...` URL exists before adding banners that link to it

**Exit criteria**:
- [ ] Full list of pages to add banners to (including agent-journal if it exists)
- [ ] All banner target URLs verified to exist on lab.pollack.ai
- [ ] Update `ROADMAP.md` checkboxes

---

### Step 4.1: Add Redirect Banners to Migrated Project Pages

**Entry criteria**:
- [ ] Step 4.0 complete

**Work items**:
- [ ] ADD banner to each migrated project's **top-level page**:
  - `projects/incubating/agent-client.mdx`
  - `projects/incubating/agent-judge.mdx`
  - `projects/incubating/agent-sandbox.mdx`
  - `projects/incubating/agent-bench.mdx`
  - `projects/incubating/agent-journal.mdx` (if it exists — checked in Step 4.0)
  - `claude-agent-sdk/index.mdx`

  Use this banner (replace `{github-repo}` and `{lab-path}` per project):
  ```mdx
  <Warning>
  This project has moved to [markpollack/{github-repo}](https://github.com/markpollack/{github-repo}).
  Current documentation is at [lab.pollack.ai/projects/{lab-path}](https://lab.pollack.ai/projects/{lab-path}).
  The content below may be outdated.
  </Warning>
  ```

  Slug mapping:
  | Community page | `{github-repo}` | `{lab-path}` |
  |---|---|---|
  | agent-client | `agent-client` | `agent-client` |
  | agent-judge | `agent-judge` | `agent-judge` |
  | agent-sandbox | `agent-sandbox` | `agent-sandbox` |
  | agent-bench | `agent-bench` | `agent-bench` |
  | agent-journal | `agent-journal` | `agent-journal` |
  | claude-agent-sdk | `claude-agent-sdk-java` | `claude-agent-sdk` |

- [ ] ADD banner to **tutorial/reference index pages** for migrated projects:
  - `agent-client/tutorial/index.mdx`
  - `agent-client/howto/getting-started.mdx`
  - `claude-agent-sdk/tutorial/index.mdx`

  Use shorter banner (use `{lab-path}` from the slug mapping table above):
  ```mdx
  <Warning>
  This project has moved. Current docs: [lab.pollack.ai/projects/{lab-path}](https://lab.pollack.ai/projects/{lab-path}).
  </Warning>
  ```

- [ ] DO NOT add banners to individual tutorial pages (too noisy, the index banner is sufficient)
- [ ] DO NOT delete or modify existing content below the banner
- [ ] OPTIONAL: Add a short notice to the community-site project index (`projects/index.mdx`) or homepage explaining that several agent-related projects have moved to `markpollack` and current docs live at `lab.pollack.ai`

**Exit criteria**:
- [ ] All migrated project top-level pages have redirect banners
- [ ] Tutorial/reference index pages have short banners
- [ ] Existing content below banners is untouched
- [ ] Create: `plans/learnings/step-4.1-community-banners.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

### Step 4.2: Move Migrated Projects to "Moved Projects" in Navigation

**Entry criteria**:
- [ ] Step 4.1 complete
- [ ] Read: `plans/learnings/step-4.1-community-banners.md`

**Work items**:
- [ ] EDIT `~/community/mintlify-docs/mint.json`:
  - Remove from "Agentic" group:
    - `projects/incubating/agent-client` (and its nested tutorial/howto/reference/explanation groups)
    - `projects/incubating/agent-judge`
    - `projects/incubating/agent-sandbox`
    - `projects/incubating/agent-bench`
  - Remove "Claude Agent SDK" group from top-level Projects (the full tutorial tree)
  - Rename "Attic" group to "Moved Projects"
  - Add to "Moved Projects" group (after moonshot/qianfan):
    - `projects/incubating/agent-client` (single page, no nested tree)
    - `projects/incubating/agent-judge`
    - `projects/incubating/agent-sandbox`
    - `projects/incubating/agent-bench`
    - `projects/incubating/agent-journal` (if it exists)
    - `claude-agent-sdk/index` (single page, no nested tutorial tree)
  - Keep in "Agentic": `spring-ai-agent-utils`, `github-collector`, `spring-ai-tool-search-tool`

- [ ] VERIFY nav renders correctly (no broken references)
- [ ] VERIFY migrated projects no longer appear in "Agentic" group:
  ```bash
  # First confirm the query matches the schema (should return the group object)
  jq '.navigation[] | select(.group=="Agentic")' mint.json
  # Then check its pages
  jq '.navigation[] | select(.group=="Agentic") | .pages' mint.json
  ```
  Expected: only `spring-ai-agent-utils`, `github-collector`, `spring-ai-tool-search-tool` remain. If the first query returns empty, adjust path for actual `mint.json` schema (Mintlify nested nav varies by version).

**Exit criteria**:
- [ ] Migrated projects appear under "Moved Projects" in navigation
- [ ] "Agentic" group contains only non-migrated projects
- [ ] Claude SDK tutorial pages still accessible via direct URL (content not deleted)
- [ ] Agent Client tutorial/howto/reference pages still accessible via direct URL
- [ ] Create: `plans/learnings/step-4.2-community-nav.md`
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

### Step 4.3: Stage 4 Verification

**Entry criteria**:
- [ ] Step 4.2 complete
- [ ] Read: `plans/learnings/step-4.2-community-nav.md`

**Work items**:
- [ ] VERIFY direct URLs to tutorial pages still work (content not deleted):
  ```
  claude-agent-sdk/tutorial/01-hello-world
  agent-client/tutorial/01-first-task
  agent-client/howto/getting-started
  ```
- [ ] VERIFY Moved Projects pages have banners visible
- [ ] VERIFY non-migrated projects unaffected in nav and content
- [ ] COMPACT Stage 4 learnings into `plans/learnings/LEARNINGS.md`

**Exit criteria**:
- [ ] Spring-ai-community site reflects migration without breaking existing links
- [ ] `plans/learnings/LEARNINGS.md` updated
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

## Revision History

| Timestamp | Change | Trigger |
|-----------|--------|---------|
| 2026-05-16T12:30-04:00 | Initial draft | Migration from spring-ai-community complete |
| 2026-05-16T13:30-04:00 | Add Stage 4: spring-ai-community site nav reorganization | User request |
| 2026-05-16T14:00-04:00 | ACP ownership corrected (separate from spring-ai-community); BOM rule established | User clarification |
| 2026-05-16T15:15-04:00 | Four review passes: terminology, verification, template disambiguation, schema awareness, artifactId confirmed | Iterative review |
