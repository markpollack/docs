# Third review

The 10 prior items are addressed cleanly. A few remaining things, mostly leftover terminology from the "migrate vs update" discussion plus a couple of small new issues:

## Real issues

**1. "Migrate" terminology is only half-fixed.** The Overview was updated to "Update," but the same word remains throughout:
- Title (line 1): "Documentation Migration — spring-ai-community to markpollack"
- Stage 1 heading (line 73): "Migration Page and Inventory" — this one is fine because Stage 1 *creates* a page about the migration
- Stage 3 heading (line 311): "Migration Notes and Final Verification" — also fine, the notes describe the migration
- Stage 4 heading (line 424): "Spring AI Community Site — **Attic Migration**" — this one is the same problem you flagged in the Overview. The site isn't migrating to an attic; pages are being moved to an attic *section* of the existing site. "Attic Reorganization" or "Move to Attic" would be more accurate.
- Step 4.2 title (line 519): "Move Migrated Projects to Attic in Navigation" — this one is actually fine: it's moving projects (already-migrated ones) to the attic nav. Reads correctly.

So really just the title and Stage 4 heading. Whether to fix the title is a judgment call — you flagged before that you didn't want to churn the filename. The Stage 4 heading is easy to fix.

**2. Stage 1 title (line 73): "Migration Page and Inventory"** — Step 1.0 is Inventory, Step 1.1 is Migration Page. The title presents them in reverse order. Trivial: "Inventory and Migration Page" matches step order.

**3. Step 2.2 BOM ambiguity is partly resolved but introduces a new one (line 197).** The move list now reads: "agent-judge, agent-sandbox, agent-bench, agent-journal, `claude-code-sdk` (the SDK's Maven artifactId), and agent-client." Good. But `claude-code-sdk` as the artifactId is asserted, not verified. If the artifactId is actually `claude-agent-sdk` or `claude-agent-sdk-java`, the move instruction targets a non-existent entry. This is exactly the kind of detail that would benefit from a verification step like "confirm artifactId by checking Maven Central" before the move, especially since the original review flagged `claude-code-sdk` as suspect.

**4. Step 4.1 shorter banner still references `{slug}` (lines 498–503).** The top banner template was disambiguated into `{github-repo}` and `{lab-path}` with a mapping table — good. But the shorter banner below still uses `{slug}` for both. For the tutorial/reference index pages, the slug needs to be the `{lab-path}` value (since the link points to lab.pollack.ai), but `{slug}` is ambiguous after the rename. Quick fix: change `{slug}` to `{lab-path}` in lines 501. Even better, add a note that for the three listed pages the value is always `agent-client` or `claude-agent-sdk` (no `-java` suffix since this is the lab path, not the repo).

**5. Stage 4 verification grep replaced with `jq` — good — but the `jq` query assumes a specific schema (line 546).** `.navigation[] | select(.group=="Agentic") | .pages` works for the classic Mintlify v1 schema where navigation is a flat array of groups. Mintlify migrated to a nested schema some time ago (with `tabs`, `groups`, `pages`, possibly `versions`), and the actual structure depends on the version of `mint.json` you're using. If the schema is nested, this query returns empty and the verification passes trivially — a false negative that would let migrated entries silently remain in "Agentic". Worth either:
- adding a sanity assertion line: `jq '.navigation[] | select(.group=="Agentic")' mint.json` (no `.pages`) — if this returns the group object, the deeper query works
- or noting "adjust path for actual mint.json schema"

**6. Stage 4 principle (line 428) still says "Move migrated projects from 'Agentic' to 'Attic' in navigation"** but Step 4.2 renames "Attic" to "Moved Projects." The principle paragraph is now mildly out of sync. Minor but easy to fix.

## Smaller

**7. Step 2.5's `<Info>` rationale is now explicit (line 282) — good.** But the parenthetical is long and breaks the work-item flow. Consider pulling it into a short note above the bullet, or just trusting the reader. Stylistic only.

**8. Revision history entries 7 and 8 (lines 596–597)** label themselves as "First review pass" and "Second review pass" — but earlier entries already covered review feedback. This is now the third and fourth review pass. Minor labeling inconsistency.

**9. Line 16 separator after the policy block** — the doc has consistent `---` separators between major sections; the spacing is fine, just noting that the doc structure is clean and readable. No fix needed.

## Net

Items 1 (Stage 4 heading), 3 (verify artifactId), 4 (`{slug}` in shorter banner), and 5 (`jq` schema) are the ones worth addressing. The rest is polish.

One observation across the three review rounds: the doc has tightened significantly each pass but the revision history is also getting long. At this point you might consider compacting entries 2–8 into a single "Iterative review pass refinements" line, leaving the initial draft, Stage 4 addition, and a "final" entry. Just a thought — your call.