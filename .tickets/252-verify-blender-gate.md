---
id: "252"
title: "Opt-in verify:blender gate — run bpy --check artifacts (skip if Blender absent)"
status: open
blocked_by: []
priority: high
tags: ["mktoon", "blender"]
---

# Opt-in verify:blender gate — run bpy --check artifacts (skip if Blender absent)

## Why

The Blender lesson track (#218 posterize, #219 palette-snap, #220 control-maps) ships
diffable bpy artifacts that each have a `--check` Tier-2 validator (assert the node group
builds with correct sockets/wiring). Today those `--check`s are run ONCE by hand during
authoring — nothing re-runs them. A future edit to a bpy artifact (or a Blender version
bump) could silently break the node wiring and no gate would catch it. The Tier-1 math
oracles ARE in `mise run verify`, but they validate the math, not the Blender node graph.

Mirror the `ink:validate-gd` pattern: an opt-in task that runs the real-runtime checks and
**skips gracefully when the runtime is absent**, so core `verify` stays fast and Blender-free.

## What to build

A `mise run verify:blender` task that:
1. Detects Blender (full path per AGENTS.md — the mise `blender` shim is broken; resolve
   via an env var like `BLENDER` with a sensible default, overridable in mise.local.toml).
2. If Blender is absent → print a skip message, exit 0 (like ink:validate-gd skips without Godot).
3. If present → run each bpy artifact's `--check`:
   - `reference/code/albedo-posterize/posterize_rgb.py --check`
   - `reference/code/palette-snap/palette_snap.py --check`
   - `reference/code/toon-control-maps/control_maps.py --check`
   Aggregate exit codes; any non-zero → fail.
4. Do NOT add it to the core `verify` run list (keep verify Blender-free + fast). It's a
   separate opt-in gate, run before closing Blender-track tickets and in the pre-commit
   hook only if Blender is present.

Document the Godot A/B visual capture as explicitly manual (not CI-able — needs GPU/window),
with the re-capture recipe in the reference README, so the visual tier isn't mistaken for gated.

## Acceptance criteria

- [ ] `mise run verify:blender` runs all three bpy `--check`s when Blender is present, fails on any broken node group
- [ ] Skips cleanly (exit 0 + message) when Blender is absent — does not block a Blender-less machine
- [ ] Blender path resolves via env var with mise.local.toml override (not hardcoded)
- [ ] Core `mise run verify` is unchanged (still Blender-free, still fast)
- [ ] AGENTS.md Commands table documents `verify:blender` + notes Godot A/B is manual
- [ ] Verified: break a node group on purpose → verify:blender fails; restore → passes
