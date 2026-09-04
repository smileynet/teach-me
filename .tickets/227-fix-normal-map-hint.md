---
id: "227"
title: "Fix: mk_toon_lite normal_map uniform missing hint_normal"
type: fix
status: done
blocked_by: []
priority: medium
tags: [mktoon]
validation_criteria:
  - "normal_map uniform in mk_toon_lite.gdshader declares hint_normal"
  - "test-scene/shaders/reference/ and examples/godot-gamedev/reference/code/ copies match"
  - "mktoon_test scene renders normal-mapped barrel correctly (headless import clean + visual check)"
---

# Fix: mk_toon_lite normal_map uniform missing hint_normal

## Intent source

Discovered during #217 (texture-audit) research + scene wiring this session. The `godot-texture-import` research (`.memory/research/mktoon-texture-prep/godot-texture-import.md`) established that normal-map sampler uniforms REQUIRE `hint_normal` for correct RGTC reimport and blue-channel reconstruction. Verified the reference shader is missing it.

## What to build

Add the `hint_normal` texture hint to the `normal_map` uniform in `mk_toon_lite.gdshader`.

Current (line 18):
```glsl
uniform sampler2D normal_map;
```

Should be:
```glsl
uniform sampler2D normal_map : hint_normal;
```

Without the hint, Godot samples the normal texture as raw RGB instead of decoding it as a tangent-space normal map (RGTC compression, blue reconstruction). This can produce subtly wrong lighting on normal-mapped toon materials.

Note: lesson #222's code snippet already SHOWS the uniform with `hint_normal` — so the lesson currently teaches code that doesn't match the reference shader. This fix aligns them.

## Context

- **Reference shader:** `test-scene/shaders/reference/mk_toon_lite.gdshader` (line 18)
- **Second copy:** `examples/godot-gamedev/reference/code/` — check for a copy that also needs the fix (keep them in sync)
- **Affected scene:** `test-scene/scenes/mktoon_test.tscn` (uses normal_map with use_normal_map=true)
- **Research:** `.memory/research/mktoon-texture-prep/godot-texture-import.md` — hint reference table
- **Validation constraint:** MCP `save_scene` is destructive — edit shader file on disk, validate via headless import (see godot-validation skill)

## Acceptance criteria

- [x] `normal_map` uniform declares `hint_normal` in the reference shader
- [x] All copies of mk_toon_lite.gdshader kept in sync — glob confirms only ONE copy exists (`test-scene/shaders/reference/`); the ticket's claimed `examples/` copy does not exist (repo uses `library/`), so nothing to sync
- [x] Headless import clean after the change
- [x] Visual check: `mktoon_test` scene reloads during headless editor scan with no shader compile error (a broken shader errors on scene reopen). Note: no published lesson currently declares this uniform — #222 (unshipped) will carry `: hint_normal` when it ships, so the reference is now correct ahead of it

## Out of scope

- Other texture uniforms (albedo already has `source_color` ✓; control maps are non-color data, correctly hint-less)
- Lesson content changes (#222 snippet already correct)


## Resolution (2026-09-03)

One-line fix applied: `test-scene/shaders/reference/mk_toon_lite.gdshader` line 18
`uniform sampler2D normal_map;` → `uniform sampler2D normal_map : hint_normal;`.

Independent review (subagent) confirmed only ONE copy of the shader exists repo-wide —
the ticket's `examples/godot-gamedev/reference/code/` copy does not exist (repo migrated to
`library/`), so the "keep copies in sync" AC is satisfied trivially. The premise "the lesson
already teaches the correct form" was stale: no published lesson declares this uniform; the
only place is #222's body (unshipped). Editing the reference is still correct — it now
precedes #222, which already shows `: hint_normal`.

Validated via headless Godot 4.7.1 editor scan (`--headless --editor --quit-after`): full
filesystem scan + scene reopen (mktoon_test uses this shader) completed EXIT 0 with no shader
compile error. A broken uniform declaration errors on scene reload, so a clean reopen is the
practical no-regression signal here.
