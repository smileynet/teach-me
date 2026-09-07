#!/usr/bin/env python3
"""make-blend.py — derive an editable .blend from a mesh asset (glb/gltf/fbx/obj).

Props ship as glb/fbx only; this produces the editable .blend source so the DCC→glTF path
is genuinely end-to-end (the learner can open + inspect + re-export). Authoring aid — NOT in
core `verify`.

Host-side driver (venv, no bpy): resolves Blender, invokes tools/blender/_bpy_convert.py
inside `blender -b`, then confirms the output artifact exists. All bpy lives in the worker.

Usage:
    mise run make-blend -- <input.glb|.gltf|.fbx|.obj> [--out reference/blender/NAME.blend] [--force]

Reliability: `blender -b --python X` exits 0 even after a swallowed exception (T82494), so we
require exit==0 AND the worker's SENTINEL line AND the output file to exist. SKIPs (exit 0) if
Blender is absent — set BLENDER in mise.local.toml or PATH.

Exit codes: 0 = converted OR skipped (Blender absent); 1 = conversion failed / artifact missing;
2 = setup error (bad args, input missing).
"""
from __future__ import annotations

import argparse
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
SENTINEL = "BPY_CONVERT_OK"


def resolve_blender() -> str | None:
    blender = os.environ.get("BLENDER", "blender")
    if Path(blender).exists():
        return blender
    return shutil.which(blender)


def main() -> int:
    ap = argparse.ArgumentParser(description="Derive an editable .blend from glb/gltf/fbx/obj.")
    ap.add_argument("input", help="source mesh file (.glb/.gltf/.fbx/.obj)")
    ap.add_argument("--out", help="output .blend path (default: <input stem>.blend beside input)")
    ap.add_argument("--force", action="store_true", help="overwrite an existing .blend")
    args = ap.parse_args()

    src = Path(args.input).resolve()
    if not src.is_file():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 2
    if src.suffix.lower() not in {".glb", ".gltf", ".fbx", ".obj"}:
        print(f"ERROR: unsupported input {src.suffix} (want .glb/.gltf/.fbx/.obj)", file=sys.stderr)
        return 2

    out = Path(args.out).resolve() if args.out else src.with_suffix(".blend")
    if out.exists() and not args.force:
        print(f"SKIP: {out} exists (use --force to overwrite)")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)

    blender = resolve_blender()
    if blender is None:
        print("SKIP: Blender not found (set BLENDER in mise.local.toml or PATH).")
        return 0

    proc = subprocess.run(
        [blender, "-b", "--factory-startup", "--python-exit-code", "1",
         "--python", str(WORKER), "--", "--emit", "blend", "--in", str(src), "--out", str(out)],
        cwd=str(PROJECT_ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    ok = proc.returncode == 0 and SENTINEL in (proc.stdout or "") and out.is_file()
    if ok:
        print(f"✓ make-blend: {src.name} → {out.relative_to(PROJECT_ROOT) if out.is_relative_to(PROJECT_ROOT) else out}")
        return 0
    reason = (f"exit {proc.returncode}" if proc.returncode != 0
              else "sentinel missing" if SENTINEL not in (proc.stdout or "")
              else "output file not written")
    print(f"✗ make-blend failed ({reason})", file=sys.stderr)
    for line in (proc.stderr or proc.stdout or "").strip().splitlines()[-5:]:
        print(f"    {line}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - top-level guard → exit 2
        print(f"make-blend ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
