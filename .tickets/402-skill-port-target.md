---
id: "402"
title: "Review migration finding: skills still say they port to crew-research"
status: backlog
blocked_by: []
validation_criteria:
  - "Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence"
  - "Port target recorded in AGENTS.md and the GLOSSARY entry"
tags: ["adoption", "migration-finding"]
---

# Review migration finding: skills still say they port to crew-research

## Finding

> **Migration finding: review first.** Filed by grey-matter `adopt-project` during adoption
> (2026-10-22) from an outside audit, not by this project's owner.
> Reporter: adopt-project audit. Confirmation status: **unconfirmed**.
> Before changing anything, reproduce each point against the current repo and record it as
> confirmed, rejected (with why), or re-scoped. If every point is rejected, close the ticket with
> the evidence. Proposed remedies are suggestions; the owner decides the fix.

AGENTS.md (line 3, now reworded) and the GLOSSARY entry "teach-me" said skills are refined here
and "ported to crew-research for global deployment"; crew-research is retired. grey-matter ships
its own `teach` and `wait-what` (`grey-matter/skills/productivity/`); the same-named project
skills here shadow them in sessions in this repo, which is expected for a shipped product. Decide
the current port target and whether grey-matter's copies should track these. Evidence: J5 in the
[adoption findings](../docs/agents/research/adoption-2026-10-22/findings.md).

Source: grey-matter adopt-project, 2026-10-22.

## Acceptance criteria

- [ ] Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence
- [ ] Port target recorded in AGENTS.md and the GLOSSARY entry
