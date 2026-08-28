---
id: "217"
title: "Lesson: What Makes a Texture Toon-Unfriendly? (0015)"
type: feature
status: done
priority: high
blocked_by: []
parent: "216"
tags: [mktoon, blender]
---

# Lesson: What Makes a Texture Toon-Unfriendly? (0015)

## What to build

A lightweight orientation lesson (~12 min read) that teaches learners to analyze PBR texture sets and identify what fights toon shading. No Blender work yet — this is the "understand the problem before fixing it" lesson.

Structural analog: lesson 0003 (spatial-shader-anatomy) — orientation for a new track, conceptual-first, produces no code files, bridges to hands-on lessons.

### Win statement

> After this lesson, you can look at any PBR texture set and predict which channels will fight toon shading, decide what to keep/discard/repurpose, and explain WHY quantization amplifies texture noise.

### Lesson arc

**Opening visual (A/B pair, no preamble):**
- Left: `mktoon_flat_color.png` — clean 4-band toon, flat orange
- Right: `mktoon_before_pbr.png` — same shader, raw PBR textures, "broken" look

Caption: *"Same shader, same settings, same mesh. The only difference is the texture."*

---

**Section 1: Quantization Amplifies Noise** (key concept)

The root mechanism in one paragraph. Then a hand-written inline SVG showing:
- Input: smooth gradient (continuous NdotL)
- Operation: step function (floor-divide quantization)
- Output with clean input: crisp bands
- Output with noisy input: speckle

This is the ONE concept the lesson teaches. Everything else is application.

---

**Section 2: The Three Enemies** (channel isolation approach)

Progressive reveal — toggle one texture channel at a time on the barrel, showing the effect of each:

| Step | What you toggle on | What changes visually |
|------|-------------------|----------------------|
| Start | Flat color only | Clean bands (reference) |
| +albedo | `use_albedo_texture = true` | Bands buried in wood grain, labels, rust. "Busy" look. |
| +normal | `use_normal_map = true` | Shadow speckle appears at band edges. Chattering. |
| Both | albedo + normal | "Realistic barrel with broken lighting" — neither style works |

Each step gets a screenshot (captured via Godot MCP) and 2-3 sentence explanation.

**Decision callout** after presenting all three states:
> **When to keep vs discard the normal map:**
> - Keep + simplify: if the mesh has broad forms you want the shader to shade (e.g., folds in cloth)
> - Discard entirely: if the mesh silhouette already communicates the form (e.g., barrel rings)
> - Default: disable it first, add it back only if the result looks too "flat"

---

**Section 3: Channel Triage** (the actionable decision)

Hand-written inline SVG: fan-out diagram showing ARM texture → 3 channels → decision per channel:

```
ARM (packed texture)
├─ R: AO ──────→ REPURPOSE → threshold_map (per-pixel shadow bias)
├─ G: Roughness → DISCARD   → specular_disabled, no effect
└─ B: Metallic ─→ DISCARD   → specular_disabled, no effect

Diffuse ────────→ KEEP + SIMPLIFY → posterize, palette snap (lessons 0016-17)
Normal ─────────→ DECIDE → keep for form, flatten for clean bands
```

**New concept callout** for "threshold_map": *Brief inline definition — a per-pixel bias on where the shadow boundary falls. Darker = earlier shadow. The AO channel already encodes this spatial relationship.*

---

**Section 4: The Empty Slots** (what you'll author in this track)

Table of mk_toon_lite texture uniforms with status + forward reference to the lesson that fills each. This is motivational — shows the learner what's coming.

Code snippet (fragment, not downloadable): the uniform declarations from mk_toon_lite.gdshader with annotations. Uses `data-mode="fragment"` — illustration only, not extractable.

---

**Section 5: Industry Context** (FYI callout, placed AFTER committing to our approach)

> **Alternative:** AAA toon games (Guilty Gear, Genshin Impact) author all textures for NPR from scratch — hand-painted ILM maps with per-pixel specular/shadow control. This track teaches the indie middle ground: start with free PBR assets, simplify them to work with toon shading while preserving dynamic lighting.

---

**Exercise: Check Your Understanding**

Near-transfer with misconception probing:

> A colleague converted their PBR castle wall asset for a toon shader by assigning the albedo texture and disabling the normal map. "The normal map was causing shadow speckle, so I removed it," they say. But the toon bands still look noisy and the flat areas aren't flat.
>
> Why? What is the actual remaining source of visual noise, and what would you recommend they do about it?

**Why this works:** Tests the core concept (quantization amplifies noise from ANY continuous source, not just normals). The misconception is "normal maps are the only problem." The correct answer identifies high-frequency albedo detail as the remaining noise source and recommends simplification.

---

**What's Next:**

"Now you know what's wrong. Next lesson: fix it. You'll build a Blender node group that posterizes any albedo texture into discrete color bands that harmonize with your toon shader's band count."

---

### Diagrams needed (2 hand-written inline SVGs)

1. **Quantization noise diagram** — continuous signal + step function = amplified noise (conceptual, horizontal flow, ~5 elements)
2. **Channel triage diagram** — fan-out from ARM/Diffuse/Normal → keep/discard/repurpose (flow type, ~8 elements)

Both use `assets/svg-patterns.md` accessibility patterns + CSS color variables.

### Screenshots (4, captured via Godot MCP)

1. Flat color only — `mktoon_flat_color.png` ✅ captured
2. Albedo only (normal off) — `mktoon_albedo_only.png` ✅ captured
3. Normal only (albedo off) — `mktoon_normal_only.png` ✅ captured
4. Both — `mktoon_before_pbr.png` ✅ captured

All in `test-scene/.scratch/screenshots/` (gitignored). Copy to `examples/godot-gamedev/assets/img/` for lesson embedding (committed with `git add -f` since lessons/ is gitignored).

### No code files section

This lesson references existing shaders but produces no new files. Code snippets use `data-mode="fragment"` (illustration only, skip extraction). No `reference/code/` directory needed.

## Validation strategy

Layered — each tool proves what the others can't.

### Layer 1: Screenshot content (image analysis, BEFORE embedding)

Verify each screenshot shows the claimed state. One attribute per question, pre-resize ≤1568px, fresh session per image.

| Screenshot | Question | Expected |
|-----------|----------|----------|
| flat_color | "Are discrete lighting bands visible? How many?" | Yes, ~4 |
| albedo_only | "Fine surface detail/text, or flat color?" | Detailed |
| normal_only | "Shadow edges smooth curves or jagged?" | Jagged |
| before_pbr | "Clean cartoon art or realistic model with odd lighting?" | Realistic/broken |

Multi-validator consensus on the 2 pedagogically-critical claims (band clarity, jagged edges). Catches the wrong-state-capture failure mode.

### Layer 2: Diagram readability (image analysis, AFTER authoring SVGs)

Render lesson, screenshot each SVG region, verify:
- Quantization diagram: "signal passing through a step function?"
- Triage diagram: "three branches labeled keep/discard/repurpose?"
- Color-independence: "can you tell branches apart WITHOUT color?" (WCAG)

### Layer 3: Lesson page (Playwright via browser agent)

Load `http://localhost:8787/lessons/blender-texture-prep/01-texture-audit.html`, verify:
- `.key-concept` present
- 4 `<img>` load (naturalWidth > 0, no broken paths)
- 2 inline `<svg>` with `role="img"` + `<title>`
- Exercise `<details>` expands on click
- Full-page screenshot in light + dark theme

### Layer 4: Contract check (mise run verify)

Links + lint + SVG var check (no hardcoded hex). Catches contract violations.

### Godot MCP: NOT needed for #217

All runtime-dependent states already captured as screenshots. The one remaining claim ("roughness has no effect") is provable from code (no roughness uniform exists) — no runtime check needed. Skip Godot re-invocation.

### Pipeline order

```
1. Image analysis on 4 screenshots (parallel)  → catches wrong-state capture
2. Author HTML + 2 SVGs
3. Serve + Playwright (structure, img load, theme) → catches broken page
4. Image analysis on rendered diagrams → catches unreadable SVG
5. mise run verify → catches contract violations
```

## Validation findings (2026-08-26)

**Layer 1 caught a real issue.** Independent image analysis of `mktoon_flat_color.png` reported "no discrete cel-shading bands, ~2 broad brightness zones blending gradually" — NOT the crisp 4-band toon the lesson premise assumed.

Root cause (scene shader params):
- `light_bands_scale = 0.5` — only 50% band contribution, rest is smooth
- `wrapped_lighting = 1.0` + `wrapped_lighting_scale = 0.35` — softens terminator
- `gooch_ramp_intensity = 0.5` — adds smooth gradient over the bands

These are production-realistic MKToon settings, but they wash out the discrete banding that the "quantization amplifies noise" lesson needs to show clearly.

**Resolution:** Capture an additional "strong toon" reference (`light_bands_scale=1.0`, `gooch_ramp_intensity=0.0`, `wrapped_lighting=0.0`) so the opening A/B contrast is unambiguous. The lesson uses the strong-band version to teach the principle, then can note that production settings soften it. This is why Layer 1 runs BEFORE authoring — validated the premise before writing to it.

### Second finding: over-corrected + agent self-report unreliable

The "strong toon" attempt (`wrapped_lighting=0.0`, `light_bands_scale=1.0`) OVER-corrected — independent image analysis of `mktoon_strong_flat.png` reported "single flat uniform orange, one brightness level." Removing wrapped_lighting collapsed nearly the entire visible face into ONE band (the lighting angle + cylinder geometry compresses the terminator into a thin strip off the visible face).

**Critical process lesson:** the `godot_editor` agent's visual self-report claimed "crisp stepped gradient clearly visible" — but the actual pixels (confirmed by independent headless image analysis AND direct inspection) show flat orange. **Do NOT trust the capturing agent's visual description.** Always validate captures with an independent read. This is exactly the "silent success" failure mode from subagent-reliability steering.

**Correct next step (NOT more blind parameter guessing):** The banding visibility is a lighting/camera + parameter tuning problem best solved interactively in the live editor with real-time feedback, not via blind fire-and-capture. Options:
1. Tune interactively: rotate the light so the terminator crosses the visible face, keep moderate wrapped_lighting (~0.2), band_scale ~0.8, gooch off. Iterate with live view.
2. OR: accept the original production-realistic settings and reframe the lesson around "even subtle toon intent is destroyed by PBR noise" (weaker but honest).
3. OR: use a sphere/simpler mesh for the reference where banding reads cleanly regardless of angle.

Recommend option 1 (interactive tune) — pause automated capture, tune the material live in the editor, then re-capture once the reference reads correctly. Blind parameter guessing has failed twice.

### ROOT CAUSE FOUND (diagnostic, 2026-08-26)

Ran a diagnostic that read back actual state + sampled pixels. Findings:
- Light `rotation_degrees` read `(-47, -29, 0)` — the ORIGINAL scene value, NOT my iter1 `(-35,-55,0)` or iter2 `(-20,-85,0)` edits.
- `use_albedo_texture` read `true` despite my `set_shader_parameter(..., false)`.
- Sampled pixels were dark red (PBR texture), not flat orange.

**Root cause:** `project_run` launches a FRESH instance from the saved `.tscn` each time. Runtime `game_eval` mutations (`rotation_degrees`, `set_shader_parameter`) either don't persist across the run or don't land on the actually-rendered material_override. That's why iter1 and iter2 were pixel-identical — neither edit took effect. All my "tuning" was a no-op; I was looking at the same unchanged render each time.

**Correct approach:** Edit the `.tscn` file DIRECTLY (persistent, version-controlled) for light rotation + shader params, then `project_run` picks up the saved state. Runtime game_eval is only reliable for READING (diagnostics/sampling), not for persistent visual tuning. This matches the godot-validation skill's editor_screenshot note — MCP mutations are fragile.

**Process win:** Independent pixel sampling (not agent self-report, not visual guess) revealed the mutations were no-ops. Three "failed" iterations were actually ONE unchanged state captured three times.

### Disk-edit path confirmed working; band-angle tuning still open (2026-08-26)

After switching to direct `.tscn` edits (persistent), the flat orange color renders correctly (pixels confirmed `(1.0, 0.72, 0.28)`) — proving disk edits work where runtime mutation didn't. Light transform edited to a side-raking angle.

BUT: the visible front face of the cylinder still renders as one uniform band. Geometry analysis: camera views along -Z; the visible front face normals point toward +Z (camera). For a toon terminator to cross that face, the light needs a strong horizontal (±X) travel component so NdotL varies left-to-right across the visible surface. Current light still has too much Z-component (lighting the front evenly).

**Honest status:** I can reliably (a) edit the scene on disk, (b) capture, (c) validate via independent pixel sampling + image read. What remains is finding the light basis that rakes the terminator across the front face. Hand-computing Transform3D basis matrices for a precise light angle is error-prone; this is the one step genuinely better done with live editor manipulation (drag the light gizmo, watch the viewport).

**Recommendation:** Either (1) human drags the light in the editor to a raking angle while watching live, then I capture; or (2) I compute the light basis from a target forward-vector using look_at math and write it to disk. Option 2 is tractable — will try next: set light forward ≈ (0.9, -0.3, 0.1) via a computed basis.

### DEFINITIVE ROOT CAUSE + resolution (2026-08-26)

Two separate MCP failure modes, both now understood:

1. **Runtime `game_eval` mutations are ephemeral/unreliable** — `set_shader_parameter` and `rotation_degrees` set on a running instance don't reliably affect the render (or get reset on the fresh `project_run` instance). Confirmed by pixel diagnostic showing original values after "setting" new ones. → Use for READING only.

2. **MCP `save_scene` is DESTRUCTIVE on hand-authored scenes** — when the agent saved the scene, it STRIPPED all inline SubResources (the ShaderMaterial, outline pass), all shader/texture ext_resources, and the material_override. The saved file reverted the barrel to its default glTF PBR material. `git diff` showed the entire toon material block deleted. → NEVER use MCP save_scene on hand-authored .tscn files with inline resources.

**Resolution applied:**
- `git restore` recovered the known-good scene (textures + mk_toon_lite wired).
- Applied ONLY the validated raking light transform via direct disk `strReplace` (rotation -15,75,0 = the angle whose pixel row showed distinct band steps 0.29→0.15→0.01→0.47→0.60).
- Validated: headless `--check-only` import clean.

**The validated light angle** produces a terminator that rakes across the visible front face — this is the correct lighting for showing toon bands. The `light_bands_scale` etc. remain at committed values (0.5 + wrapped + gooch = production-realistic subtle bands).

**Reliable workflow going forward (for capturing lesson screenshots):**
1. Edit `.tscn` params + light DIRECTLY on disk (persistent, git-tracked, non-destructive)
2. `project_run` picks up saved state
3. `game_eval` ONLY to capture viewport + sample pixels (read-only)
4. Validate every capture with independent image analysis / direct read (agent self-reports proven unreliable — claimed "crisp bands" on flat orange)
5. NEVER call MCP save_scene on the hand-authored scene

**Remaining choice for the lesson:** with the raking light now correct, decide band strength via disk edits (try light_bands_scale=0.85, wrapped=0.15, gooch=0.0 for stronger bands) OR keep production-subtle. Capture flat + PBR pairs from the corrected scene. This is now a tractable disk-edit + capture + validate loop.








## Research refinement (2026-08-27) — subagent findings

Two research tracks (crisp-cel-bands, orientation-pedagogy) + two internal reviews (corpus cross-check, lesson-pattern extraction) ran. Raw: `.scratch/subagent-research/*.md`, `.scratch/subagent-review/*.md`.

### Crisp-band capture — RESOLVED (lighting, not params; keep the barrel)

The flat-reference washout is **geometry meeting math**, not a soft-param bug. A front-lit cylinder has `N·L ≈ 1` across the entire visible face, so all band thresholds crowd into thin crescents at the silhouette → one flat tone. Fix, in leverage order:
1. **¾ side light** (~30–45° off-axis, slightly above) so the terminator crosses the visible face and `N·L` sweeps 1→0 → bands read as clean vertical stripes following the curve.
2. **Fewer bands (2–3, not more)** — each band owns a wider region. Cranking band count up makes washout worse.
3. **Half-Lambert / moderate wrapped_lighting** (`0.5·N·L+0.5`) so the shadow side carries bands instead of collapsing to flat black.

**Keep the barrel — do NOT switch to a sphere.** A sphere's omnidirectional normals guarantee a clean sweep from any angle, which *hides* the exact front-face washout real assets (barrels, pillars, limbs, cans) hit. The barrel is the honest test mesh. Capture plan: on a throwaway `mktoon_test_strong.tscn` copy (protected `mktoon_test.tscn` stays untouched), set ¾ light + `light_bands=3` + `light_bands_scale≈0.9` + `gooch=0`, keep moderate wrapped lighting for the shadow side. Independent-validate band count (~3) before authoring. Source: `.scratch/subagent-research/crisp-cel-bands.md` (13 cited sources, L4–L6).

### Orientation-pedagogy — confirms the diagnose-first arc

Show the broken result FIRST as a contrasting case, then teach why (Schwartz "inventing vs telling"; Loibl & Rummel). The payoff is the explicit broken-vs-correct COMPARISON step. Name the deep-structure cause, not the surface symptom. Close with the near-transfer misconception-probe (already in spec). Source: `.scratch/subagent-research/orientation-pedagogy.md`.

### Corpus cross-check — spec CONSISTENT; six contract gaps to close

Diagram plan (2 hand-written SVGs), exercise design, and all shader claims ("roughness no-effect", "AO→threshold_map", "quantization amplifies noise") VERIFIED against source — no content contradictions. Gaps to fix during authoring:
1. **`key_concept` is a template PARAM**, not a body section → pass `key_concept="PBR encodes continuous properties; toon shaders discretize. Continuous detail + discrete shading = amplified noise."`
2. **Enumerate `glossary_data`** — define threshold_map, quantization, ARM (spec names terms, lists no defs).
3. **SR cards: contract requires 4–8 open-answer + 2–3 interactive** with full criteria/eli5/source/level metadata + ≥3 archetypes (spec's "4 cards" undercounts).
4. **Pass `depth=2`** (`lessons/{domain-slug}/NN-slug.html`) so asset prefixes resolve.
5. **Lesson number:** file is `01-texture-audit`, title says "0015" → use `lesson_number=15` in `.lesson-meta`.
6. **Regenerate quiz + map + index** pages (pipeline completeness).
No standalone CLI — `page_template.render_lesson_page(...)` is a library; run via `.venv\Scripts\python.exe` with `PYTHONIOENCODING=utf-8`, write-then-read body. Sources: `.scratch/subagent-review/corpus-crosscheck.md`, `lesson-patterns.md`.

## Acceptance criteria

- [x] Lesson file: `examples/godot-gamedev/lessons/blender-texture-prep/01-texture-audit.html`
- [x] `render_lesson_page` called with `key_concept=`, `glossary_data={...}`, `depth=2`, `lesson_number=15`
- [x] Glossary terms defined: threshold_map, quantization, ARM (+ any others introduced)
- [x] Quiz page + map + index regenerated after lesson lands
- [x] A/B opening visual (flat vs PBR, side by side or sequential)
- [x] Progressive channel isolation (4 screenshots: flat → +albedo → +normal → both)
- [x] "Quantization amplifies noise" SVG diagram
- [x] Channel triage SVG diagram (ARM fan-out + diffuse/normal decisions)
- [x] Decision callout: when to keep vs discard normal map
- [x] Exercise tests the Win (misconception probing: "just disable normals" isn't enough)
- [x] SR questions generated (4–8 open-answer + 2–3 interactive, ≥3 archetypes, full criteria/eli5/source/level metadata) in blender-texture-prep.jsonl
- [x] Jargon annotation pass: body first-use of glossary terms (quantization, threshold-map, ARM) wrapped in `data-term` spans via `jargon-annotate.py` (explicit file path — subfolder; dry-run first for ARM substring safety)
- [x] `check-lesson.py` passes (expect PASS G2/Q6/Q9/Q10/Q12, SKIP G3/CF/Q14)
- [x] No `data-file` code blocks (no downloadable files needed)
- [x] Page generated via `page_template.py` with correct structure
- [x] Layer 1: 4 screenshots validated via image analysis (correct state each)
- [x] Layer 2: 2 SVG diagrams validated via image analysis (readable, color-independent)
- [x] Layer 3: Playwright confirms page structure + img load + both themes
- [x] Layer 4: lint-html (0 errors) + check-svg-vars (no hex) + map_parser tests (37/37) pass. NOTE: `mise run verify` itself fails on Windows (bash `/dev/null` + bare `python` env quirk); verify-links reports pre-existing symlink-as-text false positives (same ../../assets/*.css|js flagged on all sibling lessons) — live HTTP 200 confirms all assets + 4 images serve correctly.

## Research context

**From toon-texture-problems research (8 specific artifacts):**

| # | Artifact | Cause | Visual description |
|---|----------|-------|-------------------|
| 1 | Shadow speckle/chattering | Normal map micro-detail pushes pixels across threshold | Salt-and-pepper noise at shadow boundaries |
| 2 | Visual noise / "busy" look | High-frequency albedo detail overwhelms flat bands | "Neither stylized nor realistic — just broken" (McKenney, Velan Studios) |
| 3 | Broken specular | Roughness variation → scattered highlights | "Wet/oily" appearance instead of clean cartoon lobe |
| 4 | TAA flickering | Hard step edges + temporal jitter = oscillation | Buzzing/shimmering on shadow edges per-frame |
| 5 | Dirty flat regions | AO noise quantized into what should be uniform areas | Speckly dark patches in shadow bands |
| 6 | Lumpy shadow edges | Mesh topology → lumpy normal interpolation | Shadow follows edge loops instead of clean shapes |
| 7 | Lumen/GI noise | Inherent GI noise visible in hard-banded output | Visible speckle in band interiors |
| 8 | Rim artifacts | Flat surfaces have poor NdotV variation | Rim light appears/disappears abruptly |

Key quote (Erik McKenney, Velan Studios 2019): "Be they hand-painted textures, high-poly sculpted height maps, or fully-procedural materials, too many small details detract from the stylized look. They create a noise frequency that is too high, and they distract from the key shapes of the model."

Key quote (Hyper3D docs): "Noisy normals shatter clean tone bands into speckle. Micro-detail belongs in realistic assets — for cel work, smooth surfaces and let the silhouette talk."

**From mk_toon_lite shader analysis:**
- All 9 texture samplers guarded by `use_*` booleans (default `false`)
- `render_mode specular_disabled` — roughness/metallic completely irrelevant
- Noise/threshold maps centered at 0.5 (bias operation, not multiplicative)
- Pattern-overlay maps (hatching/sketch/drawn) are multiplicative (1.0 = identity)
- The shader is designed for progressive opt-in: toggle features one at a time

**From mktoon-scene-analysis:**
- `mktoon_test.tscn` uses flat color only (`use_albedo_texture = false`)
- Barrel_01 textures exist and are properly imported (diff, nor_gl, arm)
- ARM texture R channel = AO (extractable as threshold_map)
- Outline shader loaded but not wired (dangling ext_resource)
- Lesson should reference the SPECIFIC UIDs for texture assignment

**From godot-texture-import research:**
- `source_color` hint REQUIRED on albedo in Forward+ (without it: washed out)
- mk_toon_lite already has `source_color` on albedo_texture ✓
- Normal map uniform lacks `hint_normal` — document this as potential issue
- Poly Haven `_nor_gl_` normals are OpenGL-format (Y+) — no inversion needed in Godot

## Resolution (2026-08-28)

Authored blender-texture-prep track-opener: quantization-amplifies-noise concept, progressive channel-isolation A/B, misconception-probe exercise, depth-3 quiz. Crisp-band capture resolved (gooch=band ramp + raking light). All 4 validation layers pass.
