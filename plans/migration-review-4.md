# Fourth review

Most of the prior items are addressed. The doc is in solid shape. A few remaining items:

## Real issues

**1. Stage 4 heading still says "Attic Migration" (line 424 wasn't shown in my last view — let me note the line).** Looking at the doc: line 519 still reads "Step 4.2: Move Migrated Projects to Attic in Navigation" but the actual nav group is renamed to "Moved Projects" (line 533). The Stage 4 principle at line 428 was correctly updated to say "Move migrated projects from 'Agentic' to 'Moved Projects' in navigation." So Step 4.2's title is now inconsistent with both the principle and what the step actually does. Suggest: "Move Migrated Projects to 'Moved Projects' Group in Navigation."

**2. "Last updated" timestamp (line 4) is stale again.** It says `2026-05-16T14:30-04:00` but the most recent revision history entry is `2026-05-16T15:00-04:00`. Same issue as last round.

**3. Step 4.2 nav listing under "Agentic" expected (line 551).** "Only `spring-ai-agent-utils`, `github-collector`, `spring-ai-tool-search-tool` remain." But Step 2.5 line 287 removes `spring-ai-agent-utils` from the **lab.pollack.ai BOM** and the lab.pollack.ai nav (line 280: removed from "AgentWorks" group). Stage 4 is operating on the **spring-ai-community site** (`~/community/mintlify-docs/`), which is a separate site. The expectation is correct — `spring-ai-agent-utils` *should* remain under "Agentic" on the community site since it's a community project. No actual bug here, just worth double-checking the reader doesn't conflate the two sites. The current wording is fine; only flagging because I had to re-trace it.

**4. Stage 4 title (line 424, not shown above but visible in earlier views): "Spring AI Community Site — Attic Migration"** — still uses "Attic Migration." The principle below it talks about "Moved Projects" navigation. Suggest renaming to "Spring AI Community Site — Banner and Nav Updates" or "Spring AI Community Site — Move Migrated Projects to Attic" (if you prefer to keep the "attic" metaphor). The Overview (line 8) already calls Stage 4 "spring-ai-community site banner/nav updates" — using that exact phrasing would be most consistent.

**5. `claude-code-sdk` (Step 2.2 line 197) was not addressed in the last round.** I flagged it in review 2 ("clarified it's the Maven artifactId" per your reply), but the doc still asserts the artifactId is `claude-code-sdk` without verification. If the published artifactId on Maven Central is actually `claude-agent-sdk` (matching the repo `claude-agent-sdk-java`), this instruction targets a non-existent BOM entry. I'd be more comfortable if there were a `bash` line like `# Confirm artifactId: search Maven Central for io.github.markpollack` next to it, or if a Step 1.0 inventory item recorded the actual artifactId. Even just a `[ ] VERIFY artifactId on Maven Central before editing` checkbox would do.

## Smaller

**6. Revision history compaction (line 596)** — followed the suggestion to compact, good. But the compacted entry says "Three review passes" while this is now a fourth review. Will need another bump after this round if you make changes; otherwise, the entry is already accurate as of when it was written.

**7. Title (line 1) "Documentation Migration"** — left as-is per our prior decision. No fix needed; just noting it's still there for awareness.

## Net

Just three items worth touching: 1 (Step 4.2 title), 2 (timestamp), and 4 (Stage 4 title — same family as 1). Item 5 is the one substantive technical risk remaining (unverified artifactId).

