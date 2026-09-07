---
name: asset-conversion
description: "Convert 3D assets between formats to produce lesson artifacts — derive an editable .blend from glb/fbx/obj, and export a Godot-ready .glb/.gltf from a .blend, with a structural oracle check. Use when preparing 3D assets for the godot-asset-pipeline (or any Godot/glTF) lesson track. Trigger: convert asset, make blend, export glb, .blend from fbx, glb for godot, prepare 3d asset, derive blend, asset pipeline artifact."
metadata:
  type: reference
  invocation: both
  practice: null
---

# Asset Conversion

Two headless-Blender tools produce the downloadable 3D artifacts a lesson needs. Both **SKIP
gracefully (exit 0) when Blender is absent** — so they're safe to call anywhere, but only DO work
on a machine with Blender configured.

## When to use

- A lesson names a `.glb`/`.gltf`/`.blend`/`.fbx` the learner should download, and you need to
  produce or convert it.
- You have a Kenney/CC0 source (often `.fbx` or `.glb`) and need the editable `.blend` **and** a
  Godot-ready `.glb`.
- Do NOT convert what already exists in the right form — most Kenney props already ship a `.glb`;
  use it directly. Convert only to (a) derive a missing `.blend`, (b) turn an FBX-only asset into
  `.glb`, or (c) emit the same asset in multiple formats for a format-comparison lesson.

## The two tools

### Derive an editable `.blend` (glb/gltf/fbx/obj → `.blend`)
```
mise run make-blend -- <input.glb|.gltf|.fbx|.obj> [--out reference/blender/NAME.blend] [--force]
```
Imports the source into an empty scene, applies transforms (fixes FBX-cm 100× + axis bugs), saves a
compressed `.blend`. Default output is `<input>.blend` beside the input.

### Export a Godot-ready glTF (`.blend`/fbx/obj/gltf → `.glb`/`.gltf`)
```
mise run export-godot-glb -- <input.blend> [--out reference/code/SLUG/NAME.glb] [--separate] [--apply] [--force]
```
Exports with Godot-correct options (`export_yup` — glTF/Godot 4 are both +Y-up, so no import
rotation; lights/cameras excluded; materials from Principled BSDF), then runs the **Tier-1
structural oracle** (`gltf-format-oracle.py`) on the result and fails if it doesn't pass.
- `--separate` — emit `.gltf` + `.bin` + textures (the "files travel together" case) instead of `.glb`.
- `--apply` — bake modifiers (static props only). **Omit for rigged/morph assets — baking DROPS
  shape keys.**

## Typical flow (produce a lesson artifact)

```
# 1. derive the editable source (committed for end-to-end downloadability)
mise run make-blend -- <kenney-source>.fbx --out library/godot-asset-pipeline/reference/blender/chair.blend
# 2. export the Godot-ready glb into the lesson's code dir
mise run export-godot-glb -- library/godot-asset-pipeline/reference/blender/chair.blend \
    --out library/godot-asset-pipeline/reference/code/first-import-happy-path/chair.glb
```

## Non-negotiables

- **License + credits.** Every vendored third-party asset MUST get a row in the track's ASSETS
  manifest AND its kit's `License.txt` copied alongside the committed files. The lesson page carries
  a **credits footer** (`render_lesson_page(..., credits=[("3D assets by Kenney (kenney.nl) — CC0 1.0",
  "https://kenney.nl")])`) and the README `## Credits` section lists the author. `check-lesson`'s CR
  gate WARNs if a lesson has downloadable `.glb`/`.blend`/`.fbx` but no credits footer.
- **Commit assets as plain git blobs — NOT Git LFS.** They're small; GitHub Pages does not serve LFS
  content (it would ship pointer stubs → broken downloads). `.blend` sources are committed too.
- **"Exported" ≠ "correct."** `export-godot-glb` runs the oracle for you; still eyeball the summary
  (`v2.0 Nn/Nm/…`) — a 0-mesh or unexpected-skin count means the source was wrong.
- **Setup:** these need `BLENDER` resolvable — set it in the gitignored `mise.local.toml`
  (`[env] BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"`). Absent → the tools SKIP.

## Verifying an already-committed glb (no Blender needed)

The Tier-1 oracle is standalone and Blender-free — run it directly to check any `.glb`/`.gltf`:
```
uv run python tools/gltf-format-oracle.py <path.glb>
```
For the runtime truth (node tree in real Godot), that's the opt-in `asset:validate-gd` Tier-2 gate,
not these tools.
