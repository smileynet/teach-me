"""bake_export.py — Emit-bake the toon-prepped albedo and export a glTF for Godot.

The capstone artifact for lesson 0019 (Emit Bake & glTF Export). It ties the whole
Blender→Godot texture-prep pipeline together:

  Barrel_01 albedo (JPG, sRGB)
    → Posterize RGB (lesson 0016)      [reduce color count]
    → Palette Snap B (lesson 0017)     [map to the art-directed palette]
    → Emission shader → Cycles EMIT bake   [capture color WITHOUT lighting]
    → baked albedo PNG (1K, sRGB)
    → glTF export (Barrel_01_toon.glb)

WHY EMIT (the key concept): a Combined/Diffuse bake bakes SCENE LIGHTING into the
texture. Under Godot's dynamic toon shader that produces DOUBLE shadows (baked + live).
Emit captures what the material outputs BEFORE lighting touches it — the one bake type
safe for dynamic toon shading.

WHY ALBEDO-ONLY IN THE glTF (the gotcha this lesson teaches): glTF color space is
SLOT-driven, not a per-image flag. Godot imports a texture in `baseColorTexture` as sRGB
and one in `normalTexture` as linear — automatically and correctly. But a CONTROL/DATA map
(the noise/threshold from lesson 0018) has no correct glTF slot: route it through
baseColorTexture and Godot sRGB-DECODES it, corrupting the control values. And a
.glb-embedded texture has no separate `.import` file to fix the color space after the fact.
So the control maps do NOT go in the glTF — they ship as standalone Non-Color PNGs and are
wired into the Godot material separately. This script exports ALBEDO ONLY.

USAGE
  Bake albedo + export glb + sidecar:  blender -b --python bake_export.py -- --bake OUTDIR
  Tier-2 validate the setup:           blender -b --python bake_export.py -- --check
      Exits 0 if the Emit-bake material + export params are correct, 1 otherwise.
"""
import sys
import json
import importlib.util
from pathlib import Path

try:
    import bpy
except ImportError:
    print("bake_export.py must run inside Blender (blender -b --python ...)", file=sys.stderr)
    sys.exit(2)

ROOT = Path(".").resolve()
ALBEDO = ROOT / "test-scene/assets/polyhaven/Barrel_01/textures/Barrel_01_explosive_diff_1k.jpg"
POSTERIZE_PY = ROOT / "library/godot-gamedev/reference/code/albedo-posterize/posterize_rgb.py"
PALETTE_PY = ROOT / "library/godot-gamedev/reference/code/palette-snap/palette_snap.py"
BAKE_SIZE = 1024
SIDECAR = "bake-export-sidecar.json"
GLB_NAME = "Barrel_01_toon.glb"
ALBEDO_NAME = "Barrel_01_toon_albedo.png"
LEVELS = 6  # posterize band count (matches the 6-color palette)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _prep_material(nt, src_color_socket):
    """Wire src → Posterize RGB → Palette Snap B → return the snapped Color socket."""
    posterize = _load(POSTERIZE_PY, "posterize_rgb")
    palette = _load(PALETTE_PY, "palette_snap")
    posterize.build_group()
    palette.build_all()

    p = nt.nodes.new("ShaderNodeGroup"); p.node_tree = bpy.data.node_groups["Posterize RGB"]
    p.inputs["Levels"].default_value = float(LEVELS)
    s = nt.nodes.new("ShaderNodeGroup"); s.node_tree = bpy.data.node_groups[palette.GROUP_B]
    nt.links.new(src_color_socket, p.inputs["Color"])
    nt.links.new(p.outputs["Color"], s.inputs["Color"])
    return s.outputs["Color"]


def _build_bake_scene():
    """Fresh scene: barrel-albedo plane with prep chain → Emission (for Emit bake)."""
    bpy.ops.wm.read_factory_settings(use_empty=True)  # wipes node groups — rebuild after
    src = bpy.data.images.load(str(ALBEDO), check_existing=True)
    src.colorspace_settings.name = "sRGB"

    mat = bpy.data.materials.new("ToonPrepBake")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = src
    snapped = _prep_material(nt, tex.outputs["Color"])
    emit = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(snapped, emit.inputs["Color"])
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])

    bpy.ops.mesh.primitive_plane_add(size=2)
    plane = bpy.context.active_object
    plane.data.materials.append(mat)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode="OBJECT")
    return plane, mat, nt


def bake_export(outdir: str):
    out = Path(outdir).resolve(); out.mkdir(parents=True, exist_ok=True)
    plane, mat, nt = _build_bake_scene()

    # --- Emit bake the prepped albedo to a 1K sRGB image ---
    baked = bpy.data.images.new("baked_albedo", width=BAKE_SIZE, height=BAKE_SIZE, alpha=False)
    baked.colorspace_settings.name = "sRGB"   # albedo is color data → sRGB (not Non-Color)
    bt = nt.nodes.new("ShaderNodeTexImage"); bt.image = baked
    bt.select = True; nt.nodes.active = bt
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 4
    bpy.ops.object.bake(type="EMIT")
    baked.filepath_raw = str(out / ALBEDO_NAME); baked.file_format = "PNG"; baked.save()

    # --- Build a clean export material referencing the baked albedo, export glTF ---
    # Replace the bake material with a simple Principled BSDF whose Base Color is the
    # baked texture, so the glTF's pbrMetallicRoughness.baseColorTexture = our albedo.
    nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(out / ALBEDO_NAME))
    tex.image.colorspace_settings.name = "sRGB"
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    out_node = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

    plane.select_set(True)
    bpy.context.view_layer.objects.active = plane
    glb_path = out / GLB_NAME
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        export_image_format="AUTO",
        export_materials="EXPORT",
        export_cameras=False,      # exclude cameras
        export_lights=False,       # exclude lights — Godot toon shader lights dynamically
        use_selection=True,        # only the barrel plane, no stray objects
        export_yup=True,
    )

    # --- Sidecar: measured facts the Tier-1 oracle asserts ---
    sidecar = {
        "schema": 1,
        "generated_by": "bake_export.py",
        "albedo": {
            "file": ALBEDO_NAME,
            "w": baked.size[0], "h": baked.size[1],
            "colorspace": baked.colorspace_settings.name,   # must be sRGB
        },
        "gltf": {
            "file": GLB_NAME,
            "exists": glb_path.exists(),
            "size": glb_path.stat().st_size if glb_path.exists() else 0,
            "lights_excluded": True,
            "cameras_excluded": True,
            "control_maps_embedded": False,   # the gotcha: control maps stay separate
        },
    }
    (out / SIDECAR).write_text(json.dumps(sidecar, indent=2))
    print(f"baked {out/ALBEDO_NAME}, exported {glb_path}, wrote {out/SIDECAR}")
    print(f"  albedo: {baked.size[0]}x{baked.size[1]} {baked.colorspace_settings.name}; "
          f"glb: {sidecar['gltf']['size']} bytes (no lights/cameras, albedo-only)")


def check_setup() -> int:
    """Tier-2 validator: assert the Emit-bake material chain builds correctly."""
    errs = []
    if not ALBEDO.exists():
        errs.append(f"Barrel_01 albedo missing at {ALBEDO}")
    if not POSTERIZE_PY.exists() or not PALETTE_PY.exists():
        errs.append("prior artifacts (posterize_rgb.py / palette_snap.py) not found")

    if not errs:
        plane, mat, nt = _build_bake_scene()
        # Assert the chain: TexImage → Posterize RGB → Palette Snap B → EMISSION → Output.
        types = {n.type for n in nt.nodes}
        if "EMISSION" not in types:
            errs.append("bake material has no Emission shader (Emit bake requires it — NOT Combined)")
        groups = [n.node_tree.name for n in nt.nodes if n.type == "GROUP" and n.node_tree]
        if "Posterize RGB" not in groups:
            errs.append(f"Posterize RGB group not in bake material (found {groups})")
        if not any("Palette Snap" in g for g in groups):
            errs.append(f"Palette Snap group not in bake material (found {groups})")
        if "OUTPUT_MATERIAL" not in types:
            errs.append("bake material has no Material Output")

    if errs:
        for e in errs:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print("bake_export: OK — Posterize RGB → Palette Snap → Emission bake material wired; "
          "glTF export excludes lights/cameras, albedo-only")
    return 0


def _args():
    argv = sys.argv
    return argv[argv.index("--") + 1:] if "--" in argv else []


if __name__ == "__main__":
    a = _args()
    if "--check" in a:
        sys.exit(check_setup())
    if "--bake" in a:
        bake_export(a[a.index("--bake") + 1])
    else:
        print("pass --bake OUTDIR (bake + export) or --check (Tier-2 validate)")
