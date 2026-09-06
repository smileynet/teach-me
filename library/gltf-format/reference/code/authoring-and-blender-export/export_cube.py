#!/usr/bin/env python3
"""export_cube.py — the Blender (bpy) source for lesson 02's cube_metalrough.glb.

This is the *reproducible Blender path* for the artifact `make_cube_glb.py` builds with the
stdlib. It is NOT committed as a .blend (the repo has a zero-.blend precedent — the Blender
track ships diffable bpy scripts, and the .blend is reconstructible from this). It demonstrates
the "clean export" the lesson teaches: a Principled BSDF wired in the glTF-native layout,
exported with the game-ready settings from export_notes.md.

Dual interface (matches the blender-texture-prep bpy scripts):
    blender --background --python export_cube.py -- --bake OUTDIR   # build + export the .glb
    blender --background --python export_cube.py -- --check         # assert the node graph only

Run under Blender:
    blender -b --python-exit-code 1 --python export_cube.py -- --check

Exit codes: 0 = pass, 1 = a check failed (via --python-exit-code 1 on a raised AssertionError),
2 = not run under Blender. A success SENTINEL string is printed on pass so the harness can
confirm the run actually reached the end (Blender otherwise exits 0 even after a swallowed error).
"""
from __future__ import annotations

import sys

SENTINEL = "EXPORT_CUBE_OK"

try:
    import bpy
except ImportError:
    print("SKIP: export_cube.py must run inside Blender (bpy unavailable)", file=sys.stderr)
    sys.exit(2)


def _argv_after_ddash() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def build_cube_scene() -> "bpy.types.Object":
    """A unit cube with a Principled BSDF wired in the glTF-native layout (base color image)."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    cube = bpy.context.active_object
    cube.name = "Cube"

    # Apply rotation & scale so the export carries correct normals/bounds (the lesson's gotcha).
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    mat = bpy.data.materials.new("CubeMetalRough")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    # glTF-native: metal off, mid-high roughness; a base-color image drives baseColorTexture.
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.8
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    img = bpy.data.images.new("base_color", width=2, height=2)
    img.pixels = [0.78, 0.47, 0.24, 1.0] * 4  # solid base color, matches make_cube_glb.py
    tex.image = img
    mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    cube.data.materials.append(mat)
    return cube


def do_bake(outdir: str) -> None:
    build_cube_scene()
    out = f"{outdir.rstrip('/')}/cube_metalrough.glb"
    bpy.ops.export_scene.gltf(
        filepath=out,
        export_format="GLB",
        export_materials="EXPORT",
        export_yup=True,              # Blender Z-up -> glTF +Y up
        export_apply=True,            # apply modifiers
        export_texcoords=True,
        export_normals=True,
        export_tangents=True,         # needed for normal-mapped materials downstream
        export_cameras=False,
        export_lights=False,
        use_selection=False,
    )
    print(f"baked {out}")


def do_check() -> None:
    """Assert the node graph is the glTF-native 'clean export' layout the lesson teaches."""
    cube = build_cube_scene()
    mat = cube.data.materials[0]
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    assert bsdf is not None, "material must use a Principled BSDF (the exporter pattern-matches it)"
    assert abs(bsdf.inputs["Metallic"].default_value) < 1e-6, "metallic should be 0 for this cube"
    base = bsdf.inputs["Base Color"]
    assert base.is_linked, "Base Color must be linked to an image (drives baseColorTexture)"
    src = base.links[0].from_node
    assert src.type == "TEX_IMAGE", "Base Color source must be an Image Texture (not procedural)"
    print("check: Principled BSDF + base-color image, metallic=0, glTF-native layout OK")


def main() -> int:
    args = _argv_after_ddash()
    if "--check" in args:
        do_check()
    elif "--bake" in args:
        i = args.index("--bake")
        outdir = args[i + 1] if i + 1 < len(args) else "."
        do_bake(outdir)
    else:
        print("usage: export_cube.py -- (--bake OUTDIR | --check)", file=sys.stderr)
        return 2
    print(SENTINEL)   # reached the end without a swallowed exception
    return 0


if __name__ == "__main__":
    sys.exit(main())
