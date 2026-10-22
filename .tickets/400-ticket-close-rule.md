---
id: "400"
title: "Review migration finding: AGENTS.md told agents to hand-edit tickets to done"
status: backlog
blocked_by: []
validation_criteria:
  - "Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence"
  - "A real `tkt close` run in this repo succeeds (or the bug is reproduced and AGENTS.md updated)"
tags: ["adoption", "migration-finding"]
---

# Review migration finding: AGENTS.md told agents to hand-edit tickets to done

## Finding

> **Migration finding: review first.** Filed by grey-matter `adopt-project` during adoption
> (2026-10-22) from an outside audit, not by this project's owner.
> Reporter: adopt-project audit. Confirmation status: **unconfirmed**.
> Before changing anything, reproduce each point against the current repo and record it as
> confirmed, rejected (with why), or re-scoped. If every point is rejected, close the ticket with
> the evidence. Proposed remedies are suggestions; the owner decides the fix.

The pre-adoption AGENTS.md said to edit `status: done` by hand because "`tkt close` has a config
validation bug". During the audit `tkt close 089 --check-all --resolution probe --dry-run`
succeeded on tkt 0.3.1, and upstream commits 749f524 / eebded8 ("chore(tickets): close 359/360")
are `tkt close` output. The adoption replaced the rule with `tkt close` (the tkt block says reach
done only via `tkt close`) and kept the `## Resolution` requirement
(`close.require_resolution = true`). Confirm the bug is gone; if it isn't, record the repro here.
Evidence: J3 in the [adoption findings](../docs/agents/research/adoption-2026-10-22/findings.md) and the [cut log](../docs/agents/research/adoption-2026-10-22/agents-md-cut-log.md).

Source: grey-matter adopt-project, 2026-10-22.

## Acceptance criteria

- [ ] Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence
- [ ] A real `tkt close` run in this repo succeeds (or the bug is reproduced and AGENTS.md updated)
