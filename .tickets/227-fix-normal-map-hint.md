---
id: "227"
title: "Fix: mk_toon_lite normal_map uniform missing hint_normal"
type: fix
status: open
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

- [ ] `normal_map` uniform declares `hint_normal` in the reference shader
- [ ] All copies of mk_toon_lite.gdshader kept in sync (test-scene + examples/)
- [ ] Headless import clean after the change
- [ ] Visual check: normal-mapped barrel in mktoon_test renders correctly (no regression)

## Out of scope

- Other texture uniforms (albedo already has `source_color` ✓; control maps are non-color data, correctly hint-less)
- Lesson content changes (#222 snippet already correct)
