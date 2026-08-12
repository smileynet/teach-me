---
id: "072"
title: "Feature: publishing prep — LICENSE, CHANGELOG, CONTRIBUTING, CI"
status: open
priority: high
blocked_by: ["079", "080", "081"]
type: feature
---

# Feature: publishing preparation

## What to add

### Files
- `LICENSE` — MIT
- `CHANGELOG.md` — Keep a Changelog 2.0 format, starting with 0.1.0
- `CONTRIBUTING.md` — lightweight (how to run locally, where things live, how to submit issues)
- `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1

### Version
- Tag `v0.1.0` after cleanup (ticket 071) is done
- Add version to mise.toml or a VERSION file

### GitHub config
- `.github/ISSUE_TEMPLATE/bug_report.yml` — bug template
- `.github/ISSUE_TEMPLATE/feature_request.yml` — feature template
- `.github/workflows/verify.yml` — CI running `mise run verify` on push/PR

### Pre-publish audit
- No hardcoded paths (grep for /home/sam)
- No personal data in committed files
- Fresh clone works: `mise install && mise run setup && mise run verify`
- Repository topics set (learning, ai, education, cli, etc.)

## Acceptance criteria

- [ ] LICENSE file exists (MIT)
- [ ] CHANGELOG.md exists with v0.1.0 entry
- [ ] CONTRIBUTING.md explains setup and contribution process
- [ ] CI workflow runs on push and passes
- [ ] No personal paths or data in committed files
- [ ] Fresh clone → setup → verify passes

## Validation

- **E2E:** Clone to /tmp, run full setup + verify pipeline
- **Audit:** `grep -r "/home/sam" . --include="*.py" --include="*.md"` returns zero hits (excluding .git)
