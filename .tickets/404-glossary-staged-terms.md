---
id: "404"
title: "Review migration finding: staged glossary terms and contradicted entries"
status: backlog
blocked_by: []
validation_criteria:
  - "Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence"
  - "Each staged term confirmed (written to GLOSSARY.md), corrected, or rejected"
  - "Stale/contradicted entries rewritten or confirmed"
tags: ["adoption", "migration-finding"]
---

# Review migration finding: staged glossary terms and contradicted entries

## Finding

> **Migration finding: review first.** Filed by grey-matter `adopt-project` during adoption
> (2026-10-22) from an outside audit, not by this project's owner.
> Reporter: adopt-project audit. Confirmation status: **unconfirmed**.
> Before changing anything, reproduce each point against the current repo and record it as
> confirmed, rejected (with why), or re-scoped. If every point is rejected, close the ticket with
> the evidence. Proposed remedies are suggestions; the owner decides the fix.

The adoption migrated the 23 glossary terms as-is. Three entries are stale or contradicted by the
code (verdict table in the [adoption findings](../docs/agents/research/adoption-2026-10-22/findings.md)): **teach-me** (crew-research), **Teaching workspace**
("per-topic directory" vs one live `workspace/` plus the private `.user/` overlay), **Scaffold**
(vs `tools/lib/page_template.py`). Five inferred terms are staged, not written: Library, Learner
profile, Topic / Domain / Track, Reference project, Oracle
([staged terms](../docs/agents/research/adoption-2026-10-22/glossary-staged.md)). Evidence: J7.

Source: grey-matter adopt-project, 2026-10-22.

## Acceptance criteria

- [ ] Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence
- [ ] Each staged term confirmed (written to GLOSSARY.md), corrected, or rejected
- [ ] Stale/contradicted entries rewritten or confirmed
