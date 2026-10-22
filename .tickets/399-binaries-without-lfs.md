---
id: "399"
title: "Review migration finding: 87 binaries tracked without Git LFS"
status: backlog
blocked_by: []
validation_criteria:
  - "Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence"
  - "LFS decision recorded; if adopted, a Pages build serves real images (not pointer stubs)"
tags: ["adoption", "migration-finding"]
---

# Review migration finding: 87 binaries tracked without Git LFS

## Finding

> **Migration finding: review first.** Filed by grey-matter `adopt-project` during adoption
> (2026-10-22) from an outside audit, not by this project's owner.
> Reporter: adopt-project audit. Confirmation status: **unconfirmed**.
> Before changing anything, reproduce each point against the current repo and record it as
> confirmed, rejected (with why), or re-scoped. If every point is rejected, close the ticket with
> the evidence. Proposed remedies are suggestions; the owner decides the fix.

87 binaries are tracked without Git LFS (35 glb, 28 png, 15 jpg, 4 gltf, 3 bin, 1 woff2, 1
blend; largest ~1.2 MB under `test-scene/assets/quaternius-characters/`). `.gitignore` deliberately
commits `library/**/*.png` because GitHub Pages serves them, so an LFS move needs `lfs: true` on the
Pages checkout in `.github/workflows/pages.yml` or the site serves pointer stubs. Suggested: LFS for
the current tree only, plus a `git lfs install` gotcha; migrating history is a separate owner
decision. Evidence: J2, H1 in the [adoption findings](../docs/agents/research/adoption-2026-10-22/findings.md).

Source: grey-matter adopt-project, 2026-10-22.

## Acceptance criteria

- [ ] Reviewed before any change: each finding reproduced against the current repo and marked confirmed / rejected / re-scoped, with evidence
- [ ] LFS decision recorded; if adopted, a Pages build serves real images (not pointer stubs)
