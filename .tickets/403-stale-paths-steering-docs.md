---
id: "403"
title: "Review migration finding: stale paths in steering, mise task text, and scaffold docs"
status: backlog
blocked_by: []
validation_criteria:
  - "Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence"
  - "Each stale path or description fixed or confirmed intentional"
tags: ["adoption", "migration-finding"]
---

# Review migration finding: stale paths in steering, mise task text, and scaffold docs

## Finding

> **Migration finding: review first.** Filed by grey-matter `adopt-project` during adoption
> (2026-10-22) from an outside audit, not by this project's owner.
> Reporter: adopt-project audit. Confirmation status: **unconfirmed**.
> Before changing anything, reproduce each point against the current repo and record it as
> confirmed, rejected (with why), or re-scoped. If every point is rejected, close the ticket with
> the evidence. Proposed remedies are suggestions; the owner decides the fix.

Stale paths and descriptions the adoption did not touch (steering edits were out of scope):
`.kiro/steering/visual-teaching.md:130` cites `.kiro/skills/writing-style` (does not exist);
AGENTS.md (Commands row "Generate map / index") and `mise.toml` `map:global` describe a generated
forest map, but `tools/generate_global_map.py` only writes the `global-map.html` redirect stub
(#276); `assets/scaffolds/README.md:3` calls the scaffolds templates the teach skill reads, while
AGENTS.md says boilerplate lives in `tools/lib/page_template.py`. Evidence: J6 in the [adoption findings](../docs/agents/research/adoption-2026-10-22/findings.md).

Source: grey-matter adopt-project, 2026-10-22.

## Acceptance criteria

- [ ] Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence
- [ ] Each stale path or description fixed or confirmed intentional
