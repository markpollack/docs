# Second review

The 12 items from the prior pass are all addressed cleanly. A few smaller things surfaced or remain:

## Real issues

**1. Step 4.2's "Agentic" verification grep is now over-broad.** Line 534 greps for `agent-client\|agent-judge\|agent-sandbox\|agent-bench\|claude-agent-sdk` and the expected result is "only in 'Moved Projects', not in 'Agentic'". But `claude-agent-sdk` also matches things like `claude-agent-sdk-java-tutorial` — and `agent-client` is a substring used in other places. More importantly, grep without context flags won't show which JSON group a hit belongs to. Better to pipe through `grep -B 5` or to use `jq` against the parsed nav, e.g.:
```bash
jq '.navigation[] | select(.group=="Agentic") | .pages' mint.json
```
Otherwise this verification can pass while the actual condition is violated.

**2. The "Last updated" timestamp (line 4) is stale.** It still says `2026-05-16T13:00-04:00`, but the revision history goes through `2026-05-16T14:00-04:00` plus this latest pass. Bump it to match the most recent revision-history entry.

**3. Revision history is missing an entry for the changes you just made.** All 12 items got fixed, but there's no row for that pass. Add one — otherwise the next reviewer can't tell which doc state corresponds to which review round.

**4. Line 8 says "Four stages"** ✓ but the sentence describes them as "central migration page (Stage 1), mechanical coordinate sweep (Stage 2), per-page migration notes (Stage 3), and spring-ai-community site attic/banner updates (Stage 4)." That's accurate, but minor: Stage 1 is broader than "central migration page" — it also includes inventory (Step 1.0). Trivial; consider "inventory and central migration page (Stage 1)."

**5. Line 197 BOM section refers to "Community Libraries" and "Agent Client" sections,** and line 285–286 says to remove "Community Libraries (org.springaicommunity)" and "Agent Client (org.springaicommunity.agents)". Step 2.2's parenthetical at line 200 says remaining `org.springaicommunity` entries (`spring-ai-agent-utils`, `spring-testing-skills`) "stay temporarily" — which means after Step 2.2 the "Community Libraries" section still exists with those two entries, and the "Agent Client" section has been emptied. Step 2.5 then removes both sections. Good, but: line 286 says "Remove 'Agent Client (org.springaicommunity.agents)' section entirely (those are now in the markpollack section)" — by the time Step 2.5 runs, the "Agent Client" section should already be empty (because Step 2.2 moved its entries out). So the line 286 instruction is really "remove the now-empty section header," which is worth saying explicitly so a reader doesn't think they're moving entries twice. Minor clarity polish.

**6. Step 2.4's package mappings (lines 253–257) are incomplete relative to the mapping table on lines 30–36.** The table lists six package roots (claude, agents, judge, sandbox, journal, bench); Step 2.4 only lists four (claude, agents, judge, sandbox) — `journal.*` and `bench.*` are missing. Easy fix:
```
- `org.springaicommunity.journal.*` → `io.github.markpollack.journal.*`
- `org.springaicommunity.bench.*` → `io.github.markpollack.bench.*`
```

**7. Line 280 still says `<Info>` for the "community projects no longer covered by AgentWorks" notes on `agent-tools.mdx` and `spring-ai-a2a.mdx`.** Stage 4 banners were changed to `<Warning>` for "content may be outdated" — these Step 2.5 notes are arguably similar in nature (the lab.pollack.ai page is being demoted to a non-canonical archived page). Not necessarily wrong to keep `<Info>` here since the content itself isn't claimed to be outdated, just out-of-scope. But worth a deliberate decision rather than inconsistency by accident.

**8. Step 2.5 line 286 parenthetical "those are now in the markpollack section" — verify this is true after Step 2.2.** Step 2.2 line 197 lists the entries being moved: `agent-judge, agent-sandbox, agent-bench, claude-code-sdk, agent-client`. The mapping table includes `agent-journal` and `claude-agent-sdk-java`. Is `agent-journal` in the BOM? The doc doesn't say. If it is, it should be added to the Step 2.2 move list. If it isn't, that's worth a sentence — currently `agent-journal` appears in the Maven coordinates table but not in the BOM movements, and the reader can't tell whether that's intentional or an oversight.

## Smaller

**9. Step 2.4 verification at line 251 uses the new full-name greps,** good. But there's no `**Exit criteria**` mention of running this verification — line 259 just says "VERIFY no stale package names remain for migrated projects" without referring to the grep. That's fine but slightly redundant with the verification grep itself.

**10. Line 472 says "replace `{slug}` with the project slug, e.g. `agent-sandbox`, `agent-bench`"** — note that `claude-agent-sdk/index.mdx` (line 470) doesn't fit the `projects/{slug}` URL pattern, since its lab.pollack.ai equivalent is presumably `projects/claude-agent-sdk` while its community-site path is `claude-agent-sdk/index`. The template `https://github.com/markpollack/{slug}` would also yield `markpollack/claude-agent-sdk`, but the actual repo is `markpollack/claude-agent-sdk-java`. So `{slug}` is overloaded — it's not the same string in the GitHub URL and the lab.pollack.ai URL for that project. Either use two placeholders (`{github-repo}` and `{lab-path}`) or just call out claude-agent-sdk as a special case under the template.

