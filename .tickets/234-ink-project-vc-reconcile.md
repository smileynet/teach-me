---
id: "234"
title: "Reconcile ink-test-project version control: vendor addons, untrack stale compiled ink, gitignore .godot"
status: open
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

## Update (2026-08-28)
- **Item 5 is DONE** — #212's commit already landed `06_tags_as_commands.ink`, its transcript,
  `reference/code/tags-as-commands/`, and the MAP. Remaining scope is items 1–4 (addon vendoring,
  .godot gitignore, stale .ink.json untrack, .import policy).
- **Provenance overlap with #251:** item 1's "pin the inkgd godot4-branch commit hash" is the same
  work as #251 item 1 (record inkgd snapshot provenance). Whichever runs first does it; the other
  references it. #251 also diffs our snapshot vs branch HEAD (out of scope here).
- New untracked compiled ink since this ticket was filed: `stories/{02,03,04,05,06}_*.ink.json`
  (harness/validate byproducts) — same untrack+gitignore treatment as item 3.
- `mise.lock` (new, committed by #244) pins inklecate; not a reconciliation concern.

## CORRECTION (2026-09-02) — item 3 policy REVERSED; `.ink.json` must be COMMITTED, not ignored

Research + code review (`.scratch/reconcile-233/`) overturned item 3's premise. The
claim "committed `.ink.json` are never read" is true ONLY for the headless bink tools
(`play-ink.py` / `validate-ink.py` recompile to temp). It is FALSE for the Godot path:

- Every lesson player does `load("res://stories/NN.ink.json")` at runtime — e.g.
  `lesson05_player.gd:27`, `lesson06_player.gd:32`, `lesson07_player.gd:32`,
  `lesson08_player.gd:36`, `spike_story.gd:18`. They load the COMPILED JSON directly,
  they do NOT recompile from `.ink`.
- `mise run ink:validate-gd` (real Godot headless) exercises exactly this load path.
- inkgd research [L4:established]: `InkPlayer` "takes a resource as its input"; runtime
  never executes raw `.ink`. A clone-and-run fixture with no committed `.ink.json` and no
  inklecate on the machine has no story to load.

**Reversed policy:**
- **Item 3 is CANCELLED.** Do NOT `git rm --cached` the `.ink.json`; do NOT gitignore
  `stories/*.ink.json`. Doing so would break the Godot lesson players.
- **New item 3′ (COMMIT the compiled JSON):** track the `.ink.json` the players load —
  the 12 currently-untracked ones (`02`–`08`, `exercise_02/03/04_answer`, `test_fallback`)
  and keep the 2 tracked (`01`, `hello`). These are runtime deps of the fixture.
- **07/08 `.ink` SOURCES also untracked** (`07_state_bridge.ink`, `08_production_patterns.ink`)
  — commit them alongside their `.ink.json`.

**Godot 4.4 VC guidance confirmed** (official docs, `research-godot-vc.md`) — reinforces
items 1, 2, 4: commit `.uid` (MUST — 4.4 blog), commit per-asset `.import`, vendor
`addons/` for clone-and-run; gitignore ONLY `.godot/`.

**`01`/`hello.ink.json` recompile drift:** both show as modified — the in-place
`ink-test-project/mise.toml` compile (`$INKLECATE -o stories/hello.ink.json ...`)
regenerated them with newer compiler flags (`#f`, auto `g-0` gather). Regenerate all
`.ink.json` canonically once, then commit, so the tree is deterministic.

**`project.godot` (modified):** commit the `[autoload] __InkRuntime` line (REQUIRED for
inkgd) + inkgd plugin enablement; REVERT the `_mcp_game_helper` autoload (MCP scratch,
handoff rule: never commit MCP-saved artifacts).

**Bump status backlog → open** — scope is now unblocked and fully specified.
