---
id: "131"
title: "Replace CI/CD with pre-commit hooks until architecture stabilizes"
status: in_progress
blocked_by: []
priority: high
---

# Replace CI/CD with pre-commit hooks until architecture stabilizes

## Context

Architecture is still in flux (page shell, template contract, upcoming interactive quiz components). CI/CD adds friction during rapid structural changes — builds break on intermediate states, Pages deploys trigger on every push regardless of readiness. Move verification to pre-commit hooks so checks run locally before code leaves the machine. Re-add CI/CD once the component architecture settles.

## What to build

1. **Disable GitHub Actions** — remove or disable `.github/workflows/pages.yml` (and any other workflows)
2. **Create pre-commit hook** — `.githooks/pre-commit` that runs:
   - `mise run verify` (link check + lint + SVG vars + pytest + Playwright interactive)
   - Exit non-zero on failure (blocks the commit)
3. **Configure git to use project hooks** — add `core.hooksPath = .githooks` to project git config (or document the one-time setup command)
4. **Add bypass escape hatch** — document `git commit --no-verify` for WIP commits
5. **Keep GitHub Pages config** — don't delete the workflow file, just disable it (rename to `.yml.disabled` or set `on: workflow_dispatch` only) so re-enabling is trivial

## Acceptance criteria

- [ ] No CI/CD runs on push to main
- [ ] Pre-commit hook runs `mise run verify` and blocks on failure
- [ ] Hook is committed to the repo (`.githooks/pre-commit`)
- [ ] `mise run setup` or README documents enabling the hook (`git config core.hooksPath .githooks`)
- [ ] GitHub Pages remains deployable via manual trigger (workflow_dispatch)

## Validation

- [ ] Push to main does NOT trigger a workflow run
- [ ] `git commit` with a broken link fails at the hook stage
- [ ] `git commit --no-verify` bypasses the hook (escape hatch works)
