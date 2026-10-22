---
id: "398"
title: "Review migration finding: non-public material is published in the public repo and Pages site"
status: backlog
blocked_by: []
validation_criteria:
  - "Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence"
  - "Whether this material may be public decided by the owner, with any untrack/scrub done in the current tree"
  - "History purge decision recorded (done, or explicitly declined)"
tags: ["adoption", "migration-finding"]
---

# Review migration finding: non-public material is published in the public repo and Pages site

## Finding

> **Migration finding: review first.** Filed by grey-matter `adopt-project` during adoption
> (2026-10-22) from an outside audit, not by this project's owner.
> Reporter: adopt-project audit. Confirmation status: **unconfirmed**.
> Before changing anything, reproduce each point against the current repo and record it as
> confirmed, rejected (with why), or re-scoped. If every point is rejected, close the ticket with
> the evidence. Proposed remedies are suggestions; the owner decides the fix.

Research notes and shipped library pages (deployed to GitHub Pages) carried non-public material
(details intentionally not repeated here: this repo is public). The repo is public (GitHub API 200
unauthenticated). Suggested: scrub the current tree, then decide on a history purge (owner decision:
rewrite + force-push). Evidence: J1, H2 in the [adoption findings](../docs/agents/research/adoption-2026-10-22/findings.md).

**Status (2026-10-22):** current tree scrubbed by the privacy-scrub commit
(`chore(privacy): remove internal and customer content from the public tree`). History purge is
still an open owner decision.

Source: grey-matter adopt-project, 2026-10-22.

## Acceptance criteria

- [ ] Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence
- [ ] Whether this material may be public decided by the owner, with any untrack/scrub done in the current tree
- [ ] History purge decision recorded (done, or explicitly declined)
