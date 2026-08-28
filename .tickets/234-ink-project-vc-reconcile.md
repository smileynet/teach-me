---
id: "234"
title: "Reconcile ink-test-project version control: vendor addons, untrack stale compiled ink, gitignore .godot"
status: backlog
priority: medium
blocked_by: []
tags: ["ink"]
---

# Reconcile ink-test-project version control

Split from #233 — the ink-test-project portion of the uncommitted-worktree reconciliation. This is the ink session's tree (#212/#228), tracked separately from the mktoon/#217 slice that #233 handled directly.

## Context

`ink-test-project/` currently tracks **0 addon files** while `test-scene/` vendors **251** — an inconsistency. inkgd/gut/godot_ai plugins sit untracked, and Godot cache + stale compiled ink pollute `git status` (~500 entries). Research (`.scratch/subagent-research/{godot-gitignore,addons-vendoring}.md`) settled the policy; this ticket applies it.

## What to build

1. **Vendor the addons** (commit) so the ink-test-project opens clone-and-run:
   - `git add -f ink-test-project/addons/inkgd ink-test-project/addons/gut ink-test-project/addons/godot_ai` (matches test-scene's vendoring).
   - Pin the inkgd godot4-branch commit hash in REFERENCES.md (no official release; repo moved makeartandgames→ephread).
   - Commit the addons' `.uid` sidecars with them (Godot 4.4 requires committing `*.uid`).
2. **Gitignore Godot cache:** add `ink-test-project/.godot/` (test-scene already ignores its own).
3. **Untrack + gitignore stale compiled ink:** `git rm --cached ink-test-project/stories/*.ink.json` (2 tracked: `01_flow_and_knots`, `hello`) and ignore `ink-test-project/stories/*.ink.json` — both play-ink.py and validate-ink.py recompile from `.ink` to temp/next-to-source, so committed `.ink.json` are never read (evidence: `ink_compile.py`, `play-ink.py:251,275`).
4. **Decide `.import` policy:** Godot regenerates on import; headless ink tooling (inklecate+bink) doesn't need them. If addons are committed, their `.import` sidecars should be too (Godot 4.4 commits per-asset `.import`). Confirm interaction with inkgd's own `.gitignore` (`*.import`).
5. **Commit #212 Lesson 06 deliverables** (`06_tags_as_commands.ink`, transcript, `reference/code/tags-as-commands/`, `ink-godot.MAP.md`) — the ink session's in-progress content, not byproducts.

## Acceptance criteria

- [ ] ink-test-project addons vendored + committed (parity with test-scene) OR a documented rehydrate entry added
- [ ] `ink-test-project/.godot/` gitignored
- [ ] Stale `stories/*.ink.json` untracked (`git rm --cached`) + gitignored
- [ ] `.import` policy applied consistently with the addon-commit decision
- [ ] #212 Lesson 06 deliverables committed
- [ ] `git status` for `ink-test-project/` is clean or only deliberate

## Note

`__pycache__/` was added to root `.gitignore` under #233 (cross-cutting). `.uid` files are committed per Godot 4.4 guidance — do NOT gitignore them.
