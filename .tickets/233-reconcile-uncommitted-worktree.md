---
id: "233"
title: "Reconcile pre-existing uncommitted working-tree changes"
type: chore
status: done
priority: high
blocked_by: []
tags: ["hygiene"]
---

# Reconcile pre-existing uncommitted working-tree changes

At the start of the #228 session the working tree already carried a large set of
uncommitted changes from prior sessions (mktoon track + verify-pipeline rework +
Godot re-import artifacts). They were left untouched by #228 and need triaging —
committing what's intentional, gitignoring what's byproduct, reverting what's
stray.

## Groups (as of 2026-08-27)

### A. verify-pipeline rework (prior session, NOT #228)
- `mise.toml` verify task converted from a triple-quoted shell block to a
  `uv run python ...` array; added `tools/smoke-draw-diagram.py` (untracked).
- `tools/verify-interactive.py` (+60 lines), `tools/verify-links.py` (+26 lines).
- Related to the flaky 404 in #232. Decide: commit as one "verify pipeline
  hardening" change, or split. Confirm #232's flake predates or came from this.

### B. mktoon / blender-texture-prep track (prior + #217 session)
- `.tickets/217`, `.tickets/225` (deleted — superseded by #227), `.tickets/229`,
  `.tickets/230`, `.kiro/skills/godot-validation/SKILL.md`.
- `examples/godot-gamedev/lessons/index.html`, `maps/blender-texture-prep.MAP.md`,
  `learning-records/questions/blender-texture-prep.jsonl` (untracked).
- `test-scene/` — many new `.tscn` (mktoon_strong_*, mktoon_test_strong),
  `materials/`, `set_next_pass.gd`, and a large batch of `.gdshader.uid` files.
  Decide which are real deliverables vs scratch. Note the handoff's rule:
  NEVER commit MCP-saved mktoon_test.tscn.

### C. ink-test-project Godot artifacts (byproduct)
- `.godot/`, `addons/`, `*.uid`, and compiled `*.ink.json` / `*.import` files.
- `01_flow_and_knots.ink.json` + `hello.ink.json` show as MODIFIED; the other
  story `.ink.json` are UNTRACKED. These are inklecate/Godot compile byproducts.
- **Likely should be gitignored** — `tools/play-ink.py` and `validate-ink.py`
  now compile to temp dirs, so committed `.ink.json` next to sources are stale
  byproducts. Add `ink-test-project/.godot/`, `*.uid`, and story `*.ink.json` /
  `*.import` to `.gitignore` unless Godot needs the committed `.import` files.

## What to do

1. Triage each group: commit / gitignore / revert.
2. For group C: decide the .gitignore policy for compiled ink + Godot metadata
   (check whether inkgd needs committed `.ink.json`/`.import` to import at runtime).
3. Keep #228's own files (tools/lib/ink_compile.py, transcript fixtures,
   .kiro/steering/ink-authoring.md, the ink tooling edits) as their own commit —
   already logically separate.

## Triage findings (2026-08-27, corrected by research + `git ls-files` audit)

Evidence: `.scratch/subagent-review/gitignore-state.md`, `session-scope.md`;
`.scratch/subagent-research/{godot-gitignore,addons-vendoring}.md`.

**Correction to the original group-C guidance:** do NOT blanket-gitignore `*.uid` or
`addons/`.
- **`*.uid` MUST be committed** (Godot 4.4 official guidance — omitting them causes
  "invalid UID" warnings + swapped references). `test-scene` already tracks **127 .uid**.
- **addons should be vendored (committed)**, not ignored — prevailing Godot convention
  and required for a clone-and-run test fixture. `test-scene` vendors 251 addon files;
  `ink-test-project` tracks **0** (the real gap).
- Only safe ignores: **`__pycache__/`** (uncovered everywhere), **`ink-test-project/.godot/`**
  (cache; test-scene already ignores its own), and the **stale `*.ink.json`** next to
  sources (both play-ink and validate-ink recompile from `.ink`; committed copies are
  never read — 2 tracked: `01`, `hello` → need `git rm --cached`).

**Session split (sharp boundaries — reconcile within, not across):**
- **mktoon/#217 session (this session's slice — DONE here):** `examples/godot-gamedev/`
  content, `.tickets/217`, `.tickets/225` deletion, `godot-validation/SKILL.md`,
  `test-scene/` mktoon scratch. Disposition: commit #217 deliverables; revert MCP-churn
  (`shader_test.tscn`, `project.godot`, `*.png.import`); gitignore/remove strong-scene
  capture rigs.
- **ink session (#212/#228 — split to a NEW ticket, not done here):** all
  `ink-test-project/` addon vendoring, `.godot/`, stale `.ink.json` untracking,
  `06_tags_as_commands*`, `ink-godot.MAP.md`. This is the ink session's tree; #233
  should not cross into it.
- **cross-cutting (done here):** add `__pycache__/` to root `.gitignore`.

**#232 relationship confirmed:** the verify rework did NOT introduce the "flake" — the
404 was a deterministic quiz-path mismatch, fixed in #230 (closed). Not a race.

## Acceptance criteria

- [x] Every modified/untracked file triaged (committed, gitignored, or reverted) — see split above
- [x] .gitignore policy decided: `__pycache__/` + `ink-test-project/.godot/` + stale `.ink.json` ignore; `.uid`/addons COMMIT (Godot 4.4)
- [x] `git status` is clean or contains only deliberately-tracked work (mktoon slice done here; ink slice → #234, now DONE)
- [x] #232 relationship confirmed (deterministic quiz-path bug, not the verify rework; fixed by #230)
- [x] mktoon/#217 slice reconciled (this session)
- [x] ink-session reconciliation tracked in its own ticket

## Resolution (2026-09-02)

Mktoon slice reconciled and committed (`869ba70`): reverted the 3 `test-scene/*.png.import`
detect_3d reimport-churn files (no tracked refs — transient MCP editor churn) and committed
`test-scene/validate_claims.gd.uid` (legit sidecar for tracked `validate_claims.gd`). The
ink-test-project slice was split to #234 and completed in the same session (`a431fce`).
`git status` now shows only the intentionally-untracked `addons/godot_ai/` (MCP tooling) +
scratch. `mise run verify` EXIT 0 (20 interactive checks, 5 transcripts match); `ink:validate`
9/9 ok.

## Update (2026-09-02) — mktoon slice: confirmed disposition, ready to close

Fresh tree review + research (`.scratch/reconcile-233/`) resolved the two open ACs:

**The 3 `test-scene/*.png.import` changes = editor churn → REVERT** (confirms the
original triage). Diff is a Godot auto-reimport: `detect_3d/compress_to 1→0` +
`compress/mode 0→2` (lossless→S3TC VRAM) + `mipmaps/generate false→true`. `detect_3d=1→0`
is the tell — Godot flipped these when a texture was pulled into a 3D material by a
transient MCP-opened scene. NO tracked `.tscn`/`.tres`/material references treeA,
truck_alien, or wall_lines (`git grep` = 0 hits), so this is not a committed deliverable.
Action: `git checkout -- test-scene/assets/kenney-retro-urban/Textures/{treeA,truck_alien,wall_lines}.png.import`.

**`test-scene/validate_claims.gd.uid` (untracked):** commit if `validate_claims.gd` is
tracked (Godot 4.4 requires the `.uid`); else remove with the stray script.

**Remaining AC "ink reconciliation tracked in own ticket"** is already satisfied — #234
exists (and was corrected 2026-09-02: `.ink.json` must be COMMITTED, reversing its item 3).

**#233 closes** once the 3 `.png.import` reverts + `validate_claims.gd.uid` disposition
land; the ink tree is #234's scope, not this ticket's.
