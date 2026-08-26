---
id: "090"
title: "mise command to check for updated release"
type: feature
status: done
priority: low
blocked_by: []
tags: [platform]
---

# mise command to check for updated release

## What to build

A `mise run update-check` command that checks whether a newer tagged release exists on the remote (GitHub) and reports it to the user.

## Motivation

Users running local clones should be nudged when a new version is available — especially since the project is evolving rapidly and new features/fixes land frequently.

## Acceptance Criteria

- [ ] `mise run update-check` compares local version (from git tag or CHANGELOG) against latest GitHub release
- [ ] Reports: current version, latest available, and whether an update is available
- [ ] If update available, prints the command to pull (`git pull` or specific instructions)
- [ ] If already current, prints "Up to date" and exits 0
- [ ] Works offline gracefully (timeout → "couldn't check, try later")
- [ ] Does NOT auto-update — informational only

## Implementation Notes

- Use `gh api repos/{owner}/{repo}/releases/latest` or `git ls-remote --tags origin` to check
- Compare against `git describe --tags --abbrev=0` for current version
- Consider running automatically on `mise run serve` with a 24h cooldown (cache last check timestamp in `.scratch/last-update-check`)
