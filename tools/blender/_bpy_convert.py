#!/usr/bin/env python3
"""_bpy_convert.py — the in-Blender (bpy) worker for the asset-conversion tools.

Runs INSIDE Blender (`blender -b --python _bpy_convert.py -- ...`). Two host drivers invoke
it — tools/make-blend.py (emit .blend) and tools/export-godot-glb.py (emit Godot-ready glTF).
This module contains all the bpy calls; the drivers own tool-resolution, subprocess, and the
Tier-1 oracle check (they run in the venv, without bpy).

Mirrors the export_cube.py / verify-blender.py conventions:
  - args after `--`; a success SENTINEL printed on completion (Blender exits 0 even after a
    swallowed exception — the driver requires this line, T82494);
  - AssertionError (not return) on a hard failure so `--python-exit-code 1` yields a non-zero exit;
  - exit 2 if not run under Blender.

Interfaces (after `--`):
  --emit blend  --in <src.fbx|.obj|.glb|.gltf>  --out <dst.blend>
  --emit glb    --in <src.blend|.fbx|.obj|.gltf> --out <dst.glb|.gltf> [--separate] [--apply]

Import operators verified present in Blender 5.2 (probed): import_scene.fbx, wm.obj_import,
import_scene.gltf. Manual refs: manual/files/import_export/{fbx,obj}.rst, manual/addons/scene_gltf2.rst.
"""
from __future__ import annotations

import sys

SENTINEL = "BPY_CONVERT_OK"

try:
    import bpy
except ImportError:
    print("SKIP: _bpy_convert.py must run inside Blender (bpy unavailable)", file=sys.stderr)
    sys.exit(2)


def _argv_after_ddash() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def _arg(args: list[str], name: str, default: str | None = None) -> str | None:
    return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else default


def _clean_scene() -> None:
    """Start from an EMPTY factory scene — no default Cube/Camera/Light in the output.

    read_factory_settings(use_empty=True) up front is more reliable than deleting after
    startup (objects can reappear in a --python run, T38676).
    """
    bpy.ops.wm.read_factory_settings(use_empty=True)


def _import(src: str) -> None:
    low = src.lower()
    if low.endswith(".fbx"):
        # Legacy Python importer: exposes global_scale + manual-orientation for axis/scale fixups.
        bpy.ops.import_scene.fbx(filepath=src)
    elif low.endswith(".obj"):
        bpy.ops.wm.obj_import(filepath=src)
    elif low.endswith((".glb", ".gltf")):
        bpy.ops.import_scene.gltf(filepath=src)
    elif low.endswith(".blend"):
        bpy.ops.wm.open_mainfile(filepath=src)
    else:
        raise AssertionError(f"unsupported source extension: {src}")


def _apply_transforms() -> None:
    """Apply rotation & scale on every mesh so exported bounds/normals are correct and the
    asset sits at metre scale (catches the FBX-cm 100x + axis bugs). In -b nothing is selected,
    so we must select + set active or transform_apply's poll fails."""
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def emit_blend(src: str, out: str) -> None:
    _clean_scene()
    _import(src)
    _apply_transforms()
    assert any(o.type == "MESH" for o in bpy.data.objects), "no mesh imported — nothing to save"
    bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
    print(f"emit blend: {out}")


def emit_glb(src: str, out: str, *, separate: bool, apply: bool) -> None:
    _clean_scene()
    _import(src)
    fmt = "GLTF_SEPARATE" if separate else "GLB"
    kwargs = dict(
        filepath=out,
        export_format=fmt,           # raw default is '' — MUST set explicitly
        export_yup=True,             # glTF +Y-up == Godot 4 → imports upright, no rotation
        export_materials="EXPORT",   # Principled BSDF → glTF PBR → Godot StandardMaterial3D
        export_cameras=False,        # gltf-format oracle asserts these are absent
        export_lights=False,
        export_apply=apply,          # True bakes modifiers but DROPS shape keys — off by default
        export_animations=True,
        export_skins=True,
        export_morph=True,
        use_selection=False,
    )
    if separate:
        # textures beside the .gltf (the "files travel together" teaching case)
        from pathlib import Path as _P
        kwargs["export_texture_dir"] = ""  # same dir as the .gltf
        _P(out).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(**kwargs)
    print(f"emit glb: {out} (format={fmt})")


def main() -> int:
    args = _argv_after_ddash()
    emit = _arg(args, "--emit")
    src = _arg(args, "--in")
    out = _arg(args, "--out")
    if not emit or not src or not out:
        print("usage: _bpy_convert.py -- --emit blend|glb --in SRC --out DST [--separate] [--apply]",
              file=sys.stderr)
        return 2
    if emit == "blend":
        emit_blend(src, out)
    elif emit == "glb":
        emit_glb(src, out, separate="--separate" in args, apply="--apply" in args)
    else:
        print(f"unknown --emit {emit!r} (want blend|glb)", file=sys.stderr)
        return 2
    print(SENTINEL)  # reached the end without a swallowed exception
    return 0


if __name__ == "__main__":
    sys.exit(main())
