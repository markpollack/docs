# Step 2.3 Learnings — External Docs Links Updated

## Changes made

### projects/agent-client.mdx
- Removed "Documentation" CardGroup with 3 springaicommunity.mintlify.app links (Getting Started, Reference, Tutorial)
- Replaced with single "Source" Card linking to GitHub repo
- Rationale: lab.pollack.ai doesn't host the full tutorial/reference pages; the community site content will be marked stale in Stage 4

### projects/agent-sandbox.mdx
- Removed "Documentation" CardGroup with "Full Documentation" link to springaicommunity
- Replaced with single "Source" Card linking to GitHub repo
- Page already has comprehensive content (backends, core API, module structure)

### projects/claude-agent-sdk.mdx
- Removed "Getting Started" section (2 cards linking to community overview + hello-world)
- Replaced tutorial links: springaicommunity.mintlify.app tutorial paths → GitHub tutorial repo module paths
- Removed "Java API Reference" card (community site link)
- Renamed "Reference" section to "Source" with SDK source + tutorial code cards

## Verification

Post-change grep for `springaicommunity.mintlify.app` shows only:
- `spring-ai-a2a.mdx` — non-migrated, URL redirect in frontmatter
- `acp-java-sdk.mdx` — 7 links to ACP tutorials/reference (separate ownership, not part of this migration)
- `agent-tools.mdx` — 2 links to spring-ai-agent-utils docs (non-migrated)

Zero hits for migrated projects.

## Note

The roadmap expected "zero hits" overall, but that's overly strict — ACP, A2A, and agent-tools legitimately link to the community site for their non-migrated documentation.
