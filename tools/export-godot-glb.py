#!/usr/bin/env python3
"""export-godot-glb.py — export a Godot-ready .glb/.gltf from a .blend (or fbx/obj/gltf).

The forward DCC→engine path: open the source in Blender, export glTF with Godot-correct
options, then run the Tier-1 structural oracle (gltf-format-oracle.py) on the result — because
"it exported" ≠ "it's correct" (a 100x-scaled / sideways / textureless model can still be
spec-valid). Authoring aid — NOT in core `verify`.

Host-side driver (venv): resolves Blender, invokes tools/blender/_bpy_convert.py to emit the
glTF, confirms the artifact exists, then imports gltf-format-oracle to assert structural
contracts (node/mesh/material/skin/anim counts, lights/cameras excluded).

Usage:
    mise run export-godot-glb -- <input.blend|.fbx|.obj|.gltf> \\
        [--out reference/code/SLUG/NAME.glb] [--separate] [--apply] [--force]

  --separate : emit .gltf + .bin + textures (the "files travel together" case) instead of .glb
  --apply    : bake modifiers (static props). NOTE bakes DROP shape keys — omit for morph assets.

Reliability: require exit==0 AND the worker SENTINEL AND the artifact exists AND the oracle
passes. SKIPs (exit 0) if Blender is absent.

Exit codes: 0 = exported + oracle-clean OR skipped (Blender absent); 1 = export failed /
artifact missing / oracle failed; 2 = setup error.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKER = PROJECT_ROOT / "tools" / "blender" / "_bpy_convert.py"
ORACLE = PROJECT_ROOT / "tools" / "gltf-format-oracle.py"
SENTINEL = "BPY_CONVERT_OK"


def resolve_blender() -> str | None:
    blender = os.environ.get("BLENDER", "blender")
    if Path(blender).exists():
        return blender
    return shutil.which(blender)


def _load_oracle():
    """Import gltf-format-oracle.py (hyphenated filename → importlib, not plain import)."""
    spec = importlib.util.spec_from_file_location("gltf_format_oracle", ORACLE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_oracle(glb: Path) -> tuple[bool, str]:
    oracle = _load_oracle()
    metrics, errors = oracle.check_asset(glb, require_material=False)
    if errors:
        return False, "oracle: " + "; ".join(errors)
    c = metrics.get("counts", {})
    summary = (f"v{metrics.get('asset_version','?')} "
               f"{c.get('nodes','?')}n/{c.get('meshes','?')}m/"
               f"{c.get('materials','?')}mat/{c.get('skins','?')}skin/{c.get('animations','?')}anim")
    return True, f"oracle OK ({summary})"


def main() -> int:
    ap = argparse.ArgumentParser(description="Export a Godot-ready .glb/.gltf from a .blend.")
    ap.add_argument("input", help="source (.blend/.fbx/.obj/.gltf)")
    ap.add_argument("--out", help="output .glb (or .gltf with --separate); default: <input stem>.glb")
    ap.add_argument("--separate", action="store_true", help="emit .gltf+bin+textures instead of .glb")
    ap.add_argument("--apply", action="store_true", help="bake modifiers (DROPS shape keys)")
    ap.add_argument("--force", action="store_true", help="overwrite existing output")
    args = ap.parse_args()

    src = Path(args.input).resolve()
    if not src.is_file():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 2
    if src.suffix.lower() not in {".blend", ".fbx", ".obj", ".gltf", ".glb"}:
        print(f"ERROR: unsupported input {src.suffix}", file=sys.stderr)
        return 2

    ext = ".gltf" if args.separate else ".glb"
    out = Path(args.out).resolve() if args.out else src.with_suffix(ext)
    if out.exists() and not args.force:
        print(f"SKIP: {out} exists (use --force to overwrite)")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)

    blender = resolve_blender()
    if blender is None:
        print("SKIP: Blender not found (set BLENDER in mise.local.toml or PATH).")
        return 0

    cmd = [blender, "-b", "--factory-startup", "--python-exit-code", "1",
           "--python", str(WORKER), "--", "--emit", "glb", "--in", str(src), "--out", str(out)]
    if args.separate:
        cmd.append("--separate")
    if args.apply:
        cmd.append("--apply")
    proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")

    if not (proc.returncode == 0 and SENTINEL in (proc.stdout or "") and out.is_file()):
        reason = (f"exit {proc.returncode}" if proc.returncode != 0
                  else "sentinel missing" if SENTINEL not in (proc.stdout or "")
                  else "output not written")
        print(f"✗ export-godot-glb failed ({reason})", file=sys.stderr)
        for line in (proc.stderr or proc.stdout or "").strip().splitlines()[-5:]:
            print(f"    {line}", file=sys.stderr)
        return 1

    # Tier-1: structural oracle on the emitted glTF ("exported" ≠ "correct").
    passed, msg = run_oracle(out)
    rel = out.relative_to(PROJECT_ROOT) if out.is_relative_to(PROJECT_ROOT) else out
    if passed:
        print(f"✓ export-godot-glb: {src.name} → {rel} — {msg}")
        return 0
    print(f"✗ export-godot-glb: {rel} exported but {msg}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - top-level guard → exit 2
        print(f"export-godot-glb ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
