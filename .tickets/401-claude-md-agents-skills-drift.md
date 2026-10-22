---
id: "401"
title: "Review migration finding: CLAUDE.md and .agents/skills drifted from the shipped workflow"
status: backlog
blocked_by: []
validation_criteria:
  - "Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence"
  - "CLAUDE.md role decided and its commands/paths match the current tools"
  - "`.agents/skills` coverage and `default.json` resources decided"
tags: ["adoption", "migration-finding"]
---

# Review migration finding: CLAUDE.md and .agents/skills drifted from the shipped workflow

## Finding

> **Migration finding: review first.** Filed by grey-matter `adopt-project` during adoption
> (2026-10-22) from an outside audit, not by this project's owner.
> Reporter: adopt-project audit. Confirmation status: **unconfirmed**.
> Before changing anything, reproduce each point against the current repo and record it as
> confirmed, rejected (with why), or re-scoped. If every point is rejected, close the ticket with
> the evidence. Proposed remedies are suggestions; the owner decides the fix.

CLAUDE.md is a 44-line consumer-facing copy, not a pointer, and has drifted: it cites
`tools/init-workspace.sh` (ADR 0011 made init pure Python: `tools/init_workspace.py`), root
`workspace/MISSION.md` and NOTES.md (the teach skill now uses `.user/learner-profile.md`), and says
skills are "in .agents/skills/", which symlinks only 9 of 13 (missing asset-conversion,
godot-validation, lesson-validation, serve-workspace). `.kiro/agents/default.json` loads root
`MISSION.md`, `RESOURCES.md`, `NOTES.md`, none of which exist at the root. Decide: CLAUDE.md as a
pointer to AGENTS.md vs a maintained consumer copy; symlink coverage; NOTES.md vs learner profile.
Evidence: J4 in the [adoption findings](../docs/agents/research/adoption-2026-10-22/findings.md).

Source: grey-matter adopt-project, 2026-10-22.

## Acceptance criteria

- [ ] Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence
- [ ] CLAUDE.md role decided and its commands/paths match the current tools
- [ ] `.agents/skills` coverage and `default.json` resources decided
