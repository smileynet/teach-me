---
created_at: 2026-08-26T21:15:00-07:00
base_commit: 9d70c86
handoff_key: mktoon-texture-prep
---

# Handoff

> Supersedes the `ink-godot-lessons` handoff (recoverable at git history; that workstream's tickets #208-214 remain open and untouched).

## Objective
Build the `blender-texture-prep` lesson track (#216 epic, lessons #217-222): teach converting photoreal PBR textures to toon-friendly assets for the mk_toon_lite shader. Next concrete step: author lesson #217 (texture-audit).

## Constraints
- **Godot MCP `save_scene` is DESTRUCTIVE** — strips inline SubResources/material_override from hand-authored .tscn. NEVER call it on mktoon_test.tscn. Edit .tscn on disk instead. (Full rules: `.kiro/skills/godot-validation/SKILL.md` → MCP Reliability.)
- **game_eval mutations are ephemeral** — use for READ-only (capture + pixel sample), not persisting param/light changes.
- **Agent visual self-reports are unreliable** — validate every capture with independent image read (`kiro-cli chat --no-interactive --trust-tools=read "<question> <path>"`) or your own read.
- test-scene project at `D:\code\teach-me\test-scene`; screenshots land in Godot `user://` then copy to `test-scene/.scratch/screenshots/` (gitignored).

## Prior Decisions
- #216 is an EPIC/tracking ticket — child lessons own concrete deliverables (node group→#218, ramp/noise/threshold→#220). Don't rebuild in #216.
- Strategy A+B (research-backed): keep dynamic lighting, simplify albedo (posterize+palette) + author control maps. Do NOT bake lighting.
- Lesson #217 = orientation (channel-isolation teaching, misconception-probe exercise, 2 SVGs, no code files). Full spec in ticket body.

## Current State
Work status lives in tickets (no PLAN.md). What's not in tickets:
- mktoon_test.tscn is wired (albedo+normal on, outline next_pass) with a VALIDATED raking light `Transform3D(0.259..., ..., 0, 3, 0)` (rotation -15,75,0) that puts a terminator across the barrel face.
- 4 progressive screenshots captured (flat/albedo-only/normal-only/both) + validated via independent image analysis. In `test-scene/.scratch/screenshots/` (mktoon_*.png).
- Research promoted to `.memory/research/mktoon-texture-prep/` (12 files; #216/#217 reference them).

## Next Steps
1. **Resolve band-strength decision** (see #217 validation findings): bands are production-subtle. Either tune stronger (light_bands_scale~0.85, wrapped~0.15, gooch=0 — via DISK edit, then capture+validate) OR reframe lesson around "subtle intent destroyed by noise". Needs the user's earlier call ("A" = tune) finished.
2. **Author lesson #217** — spec is complete in ticket. Needs: strong-band flat reference recaptured after step 1.
3. **#227** (medium, ready) — add `hint_normal` to mk_toon_lite normal_map uniform (1-line shader fix; keep both shader copies in sync).

## Fog
- Band-strength: blind param tuning FAILED (3 no-op iterations due to game_eval ephemerality — now understood). Correct path is disk-edit + capture + independent-validate loop. Not yet dialed to a crisp-band reference.
- Whether to keep the barrel as the hero asset or switch to a sphere (cleaner banding at any angle) if disk-edit tuning still can't get crisp bands across the cylinder face.

## Evidence
- Screenshots: `test-scene/.scratch/screenshots/mktoon_{flat_color,albedo_only,normal_only,before_pbr}.png` (visually confirmed + independent image analysis).
- Scene renders clean: headless `--check-only` import passed after light edit (commit fce58a2).
- tkt validate: pass (11 pre-existing warnings, none in mktoon track). Frontier: #216, #217, #227 ready.

## Recommended Updates
- [x] skill(godot-validation): MCP failure modes captured this session (commit 644edc7)
- [x] .tickets/227: hint_normal fix created this session
- [ ] Consider promoting the "disk-edit + capture + independent-validate" loop to a named procedure in godot-validation if #218-222 reuse it heavily
