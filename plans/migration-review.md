I'll read the document first to review it.Let me see the truncated middle section before giving a full review.I have the full picture now. Let me review.

# Review: docs-migration-roadmap.md

Overall this is a careful, well-structured roadmap. The staging is clear, the policy is explicit, and the verification commands are good. A handful of real issues, in roughly descending order of importance:

## Substantive issues

**1. agent-client groupId inconsistency between table and callout (line 24 vs lines 350–357).** The mapping table says agent-client's *old* groupId is `org.springaicommunity.agents`. The Step 3.1 callout copy says exactly that. But the inventory and verification greps throughout Stage 2 only search for `org.springaicommunity` — which matches `org.springaicommunity.agents` as a prefix, so verification *works*. The risk is the other direction: Step 2.4's package-name list (lines 254–257) and Step 1.0's package-name greps (line 94) treat `org.springaicommunity.agents.*` as one of several siblings. That's fine, but the mapping at line 32 (`org.springaicommunity.agents.*` → `io.github.markpollack.agents.*`) silently assumes the package roots actually use `.agents.` after `springaicommunity`. The note at line 38 catches this ("verify actual package roots from source"), which is good — but worth being explicit that agent-client is the project where the package root may *not* match the simple sibling pattern, since it had a different groupId. Consider adding a one-line note next to agent-client in the package mapping.

**2. Step 2.2 mentions `claude-code-sdk` (line 197).** Every other mention in the doc is `claude-agent-sdk` or `claude-agent-sdk-java`. This is either a typo or a leftover from an older naming. If `claude-code-sdk` is a real BOM entry name, call that out; otherwise fix it to `claude-agent-sdk`.

**3. Step 2.5 BOM cleanup contradicts itself on `org.springaicommunity.agents` (lines 286, 291).** Line 286 says "Remove 'Agent Client (org.springaicommunity.agents)' section entirely (those are now in the markpollack section)." Line 291 says "Remove any `org.springaicommunity` or `org.springaicommunity.agents` entries (migrated projects should already be under `io.github.markpollack`)." These are consistent in *intent* but the parenthetical on line 286 ("those are now in the markpollack section") implies the entries were *moved* in Step 2.2, while line 291 implies they may still be lingering. Pick one model: either Step 2.2 moves them and Step 2.5 just verifies, or Step 2.2 deletes the old section and Step 2.5 sweeps for stragglers. Right now a reader can't tell whether line 291 is belt-and-suspenders or actual work.

**4. Step 4.1 banner template references the wrong project (lines 471–478).** The instruction says "ADD banner to each migrated project's top-level page" and lists six pages including `agent-judge`, `agent-sandbox`, `agent-bench`, `agent-journal`, `claude-agent-sdk`. The banner template hardcodes `agent-client` URLs. The parenthetical "adjust URLs per project" addresses this, but in a roadmap where every other code block is copy-pasteable, this one isn't. Either provide a placeholder like `{project-slug}` or note explicitly "replace `agent-client` with the project slug in both URLs."

**5. Step 4.2 nav edit is missing `claude-agent-sdk-java-tutorial`.** The overview (line 10) says the tutorial repo is part of the 7 migrated repos and needs URL/link updates. Stage 4 moves the tutorial *site content* under "Claude Agent SDK" group (line 519), but doesn't say what happens to any community-site nav entry specifically for the tutorial repo. If the 23-module tutorial tree on the community site is *all* under `claude-agent-sdk/`, the current line 519 covers it. If there's a separate `claude-agent-sdk-java-tutorial` reference anywhere in the community site nav, it'll be missed. Worth a quick check during Step 4.0 inventory.

**6. Stage 4 banner content uses `<Info>` despite Stage 4 being a content-stale state (line 473–477).** The banner says "The content below may be outdated." Mintlify's `<Info>` is the friendliest callout type — `<Warning>` or `<Note>` would more honestly signal staleness. Minor stylistic call, but "may be outdated" + cheerful blue Info box reads slightly off.

## Smaller issues

**7. Line 10 phrasing: "6 Maven-published project pages need coordinate callouts."** Step 3.1 lists 5 pages getting the standard callout (`agent-client`, `agent-sandbox`, `agent-bench`, `claude-agent-sdk`, `agent-journal`) plus `agent-judge` getting a different callout — total 6, matches. Good. But the overview at line 10 also says "The tutorial needs URL/link updates but no Maven coordinate callout" — so the 7th repo gets no callout. Worth saying explicitly in line 10: "6 of the 7 migrated repos need Maven coordinate callouts; the tutorial repo needs only URL updates."

**8. Step 2.2 verification grep uses `-v "agent-utils\|testing-skills\|spring-ai-a2a"` (line 204)** but the policy at line 40 says the non-migrated projects are `spring-ai-a2a`, `spring-ai-agent-utils`, `spring-testing-skills`. The grep filter uses substrings that work — `agent-utils` matches `spring-ai-agent-utils` and `testing-skills` matches `spring-testing-skills` — but it's slightly fragile and depends on those substrings being unique. Cheap robustness improvement: use the full names. Same comment applies to Steps 2.4, 3.2.

**9. Line 67: "agent-judge 0.10.0 ... Confirmed (2026-05-16)"** is the only release with a date. The others say just "Confirmed." Either add dates to all, or remove the date from agent-judge — inconsistency suggests it was added late and might mean something different.

**10. Step 4.2 line 530 says "RENAME nav group from 'Attic' to 'Moved Projects'"** but line 521 already includes the rename in the EDIT block. Duplicate instruction.

**11. Line 196 "Move ... from 'Community Libraries' and 'Agent Client' sections to 'Agent Engineering (io.github.markpollack)' section"** — this is the first mention of an "Agent Engineering" section. If that section already exists in the BOM page, fine; if it's new, the step should say "create or move to." Worth a one-word clarification.

**12. The overview (line 8) calls this a "three-layer approach"** but the doc has four stages. Stages 1–3 are the three layers (central page, mechanical sweep, per-page notes). Stage 4 was added later (per revision history line 581). Update the overview to mention Stage 4 — currently a reader hits Stage 4 unexpectedly.

## Things that look right but worth double-checking

- The release gates table only lists the 6 published projects. The tutorial repo (no Maven publish) is correctly omitted. Good.
- `acp-java-sdk` handling is consistent throughout (lines 10, 45–48, 283, 292, 296). Good.
- The audit trail (learnings files per step) is consistent. Good.
- The BOM ownership rule (lines 50–52) is clear and the future-task callout at line 296 is the right place for the ACP migration note.

## Net

Issues 1, 3, 4, and 12 are the ones I'd fix before sharing this with anyone else. 2 is probably a typo worth a 10-second check. 