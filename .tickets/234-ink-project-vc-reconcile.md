---
id: "234"
title: "Reconcile ink-test-project version control: vendor addons, untrack stale compiled ink, gitignore .godot"
status: done
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

- [x] ink-test-project addons vendored + committed (inkgd, parity with test-scene; godot_ai excluded as MCP tooling; gut deleted as unused)
- [x] `ink-test-project/.godot/` gitignored
- [x] ~~Stale `stories/*.ink.json` untracked~~ → REVERSED: lesson `.ink.json` COMMITTED (Godot players `load()` them at runtime); orphan `test_fallback.*`/`exercise_0*_answer.*` gitignored instead
- [x] `.import` policy applied consistently with the addon-commit decision (all per-asset `.import` committed; addon `.gitignore` neutralized)
- [x] #212 Lesson 06 deliverables committed (already landed pre-ticket)
- [x] `git status` for `ink-test-project/` is clean or only deliberate (only untracked `addons/godot_ai/` remains, by design)

## Resolution (2026-09-02)

Committed `a431fce` (206 files, +17,479). Applied the corrected Godot-4.4 policy matching
test-scene precedent:
- Vendored `addons/inkgd` in full (ephread/inkgd godot4 @ fea9098, v0.6.0); removed the
  upstream addon-local `.gitignore` so root policy owns ignores + committed the 2 editor-icon
  `.import` sidecars. Deviation noted in VENDOR.md.
- Committed lesson stories (07/08 `.ink` sources + 02–08 `.ink.json` + all `.import`) — the
  Godot players `load("res://stories/NN.ink.json")` at runtime, so these are runtime deps,
  NOT stale byproducts (reversed the original item-3 premise after load-path review).
- Committed scene `.gd.uid` + `script_templates/`.
- `project.godot`: kept `__InkRuntime` autoload + inkgd plugin; dropped `_mcp_game_helper`
  autoload + `godot_ai` plugin entry.
- Excluded: `addons/godot_ai/` (MCP tooling, left untracked), `addons/gut/` (unused
  speculative install — deleted), orphan `test_fallback.*`/`exercise_0*_answer.*` (no tracked
  `.ink` source — gitignored).

Verified: `mise run ink:validate` 9/9 ok (incl. new 07/08); `mise run verify` EXIT 0 (20
interactive checks, 5 transcripts match). `git status` clean except the by-design untracked
`addons/godot_ai/`.

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

## ROUND-2 refinements (2026-09-02) — precedent alignment + new exclusions

Second review pass (`.scratch/reconcile-233/r2-*.md`) — test-scene precedent + commit
runbook + gitignore-conflict check. Four refinements:

**A. `addons/godot_ai/` is EXCLUDED (new — round 1 missed this).** It's the MCP
game-helper tooling, not a lesson dep. The `project.godot` `_mcp_game_helper` autoload
points at `res://addons/godot_ai/runtime/game_helper.gd`, and `godot_ai/plugin.cfg` is in
the enabled editor_plugins array. Vendor ONLY `inkgd` (+ decide `gut` separately). Do NOT
stage `addons/godot_ai/`.

**B. `project.godot` partial revert — drop TWO godot_ai references, not one:**
- KEEP: `[autoload] __InkRuntime`, `res://addons/inkgd/plugin.cfg` in enabled plugins,
  `[inkgd] register_templates=true`.
- DROP: `_mcp_game_helper` autoload line AND `res://addons/godot_ai/plugin.cfg` from the
  enabled array. Edit the WORKTREE to the desired end-state (a committed project.godot
  referencing an un-committed autoload path is broken on clone), then `git add` + verify
  `git diff --cached | Select-String "godot_ai|_mcp_game_helper"` returns nothing.

**C. CRITICAL divergence — `addons/inkgd/.gitignore` (`*.import`) vs test-scene.**
test-scene has ZERO addon-level `.gitignore` and commits all 79 `.import`. inkgd's
vendored `.gitignore` actively hides 2 real icon sidecars (`editor/icons/compile.svg.import`,
`ink_player.svg.import`) — a fresh-clone reimport-churn risk test-scene avoids. Options:
(1) neutralize/delete `addons/inkgd/.gitignore` so root policy owns ignores + force-add the
2 `.svg.import`; or (2) keep upstream's ignore, let the icons reimport locally (harmless,
but diverges from precedent). If (1): note the deviation in VENDOR.md so re-vendor doesn't
reintroduce it. Confirmed the addon `*.import` is scoped to `addons/inkgd/` only — it does
NOT block `stories/*.import` (those `git add` cleanly).

**D. DECISION items — RESOLVED by round-3 provenance check (2026-09-02):**

Round-3 (`.scratch/reconcile-233/r3-*.md`) traced provenance via git-history + load-path
grep. All four resolved:

- **`stories/test_fallback.*` → DROP** (unconditional). Never tracked (no git history on
  any branch), no `.ink` source exists anywhere, no player/harness/task references it. Pure
  spike scratch, no revival path.
- **`stories/exercise_0{2,3,4}_answer.ink.json` (+`.import`) → DROP.** Never tracked, NO
  tracked-or-untracked `.ink` source exists, not referenced by any lesson HTML or player.
  Committing = orphan artifacts nobody can regenerate or diff-review. Conditional revival:
  author the `exercise_0N_answer.ink` SOURCES first + wire into a player, THEN commit
  source+JSON+.import together. Until then, exclude.
- **`addons/gut/` → DROP** (delete, don't just exclude). GUT v9.1.1 was installed
  speculatively via editor AssetLib on 2026-08-24 (same batch as inkgd + godot_ai). It is
  DISABLED (not in project.godot enabled-plugins), never committed, zero test files extend
  `GutTest`, no mise/CI task invokes it, and test-scene does NOT vendor it. The real runtime
  gate (`ink:validate-gd`) uses the bespoke `validate_runtime.gd` harness, not GUT. Safe to
  `Remove-Item -Recurse -Force ink-test-project/addons/gut/`.
- **`script_templates/` → INCLUDE if intentional** (small project-local editor templates;
  low risk). Otherwise exclude.

**⚠️ CORRECTION to this ticket's own round-1 item 3′:** round 1 listed
`exercise_02/03/04_answer` and `test_fallback` among ".ink.json to COMMIT (runtime deps)."
That was WRONG — it assumed they were loaded fixtures without checking the load path. No
player `load()`s them (verified). Item 3′ COMMIT scope is ONLY the lesson stories `02`–`08`
(which players DO load) + `01`/`hello` (already tracked). The orphans are DROP, per D above.

**Suggested scoped `.gitignore`** (narrow — won't catch legit lesson `.ink.json`):
`ink-test-project/stories/test_fallback.*` + `ink-test-project/stories/exercise_0*_answer.*`

**test-scene precedent confirms** (449 tracked): commit sources + `.uid` (153) + per-asset
`.import` (79) + whole vendored addon; ignore only `.godot/` + build products. Full runbook:
`.scratch/reconcile-233/r2-commit-runbook.md`.
