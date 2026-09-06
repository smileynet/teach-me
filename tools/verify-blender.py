#!/usr/bin/env python3
"""verify-blender.py — opt-in Tier-2 gate: run the bpy artifacts' `--check` validators.

The Blender lesson track ships diffable bpy node-setup scripts (posterize, palette-snap,
control-maps). Each has a `--check` that builds its node group in real Blender and asserts
the sockets/wiring. The Tier-1 MATH oracles run in `mise run verify`; this gate covers the
Blender NODE GRAPH, which no headless-Python check can. It is intentionally NOT in core
`verify` (keeps that fast + Blender-free) — run it before closing Blender-track tickets.

Mirrors tools/ink-gd-run.py: BLENDER comes from the environment
(mise [env] BLENDER = { default = "blender" }; override to a full path in mise.local.toml).
If Blender is absent, SKIP (exit 0) — absence is not failure.

Reliability (Blender tracker T82494): `blender -b --python X.py` swallows a Python
exception and STILL EXITS 0. So we (a) pass `--python-exit-code 1` (an unhandled exception
then makes Blender exit 1) AND (b) require the artifact's success sentinel line in stdout.
Neither alone is sufficient — a dropped sys.exit or an early return could pass the other.

Exit codes: 0 = all checks passed OR skipped (Blender absent); 1 = a check failed;
2 = setup error.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Windows consoles default to cp1252; force UTF-8 so ✓/✗ glyphs don't crash (see #237).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# cwd for the checks = repo root: control_maps.py opens the ARM texture by a path
# relative to the repo root ("test-scene/assets/polyhaven/..."), so the checks must
# run from there. The other two artifacts touch no external files (cwd-agnostic).
CHECK_CWD = PROJECT_ROOT

# (artifact path relative to CHECK_CWD, success sentinel substring in stdout)
ARTIFACTS = [
    ("library/godot-gamedev/reference/code/albedo-posterize/posterize_rgb.py", "posterize_rgb: node group OK"),
    ("library/godot-gamedev/reference/code/palette-snap/palette_snap.py", "palette_snap: both groups OK"),
    ("library/godot-gamedev/reference/code/toon-control-maps/control_maps.py", "control_maps: OK"),
    ("library/godot-gamedev/reference/code/bake-and-export/bake_export.py", "bake_export: OK"),
    ("library/gltf-format/reference/code/authoring-and-blender-export/export_cube.py", "EXPORT_CUBE_OK"),
]


def resolve_blender() -> str | None:
    blender = os.environ.get("BLENDER", "blender")
    # Accept either an existing absolute path or a PATH-resolvable command.
    if Path(blender).exists():
        return blender
    return shutil.which(blender)


def run_check(blender: str, rel_path: str, sentinel: str) -> tuple[bool, str]:
    """Run one artifact's --check. Pass only if exit==0 AND the sentinel printed."""
    proc = subprocess.run(
        [blender, "-b", "--python-exit-code", "1", "--python", rel_path, "--", "--check"],
        cwd=str(CHECK_CWD),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    ok = proc.returncode == 0 and sentinel in (proc.stdout or "")
    if ok:
        return True, f"  ✓ {rel_path}"
    # Surface the most useful failure detail: sentinel-missing vs non-zero exit.
    if proc.returncode != 0:
        reason = f"exit {proc.returncode}"
    else:
        reason = "success sentinel not printed (silent early exit / swallowed error)"
    tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-3:]
    return False, f"  ✗ {rel_path} — {reason}\n" + "\n".join(f"      {t}" for t in tail)


def main() -> int:
    blender = resolve_blender()
    if blender is None:
        print("SKIP: Blender not found (set BLENDER in mise.local.toml or PATH).")
        return 0

    if not CHECK_CWD.is_dir():
        print(f"ERROR: {CHECK_CWD} not found", file=sys.stderr)
        return 2

    print(f"verify-blender: {blender}")
    failures = 0
    for rel_path, sentinel in ARTIFACTS:
        passed, msg = run_check(blender, rel_path, sentinel)
        print(msg)
        if not passed:
            failures += 1

    if failures:
        print(f"\n✗ {failures}/{len(ARTIFACTS)} bpy --check(s) FAILED", file=sys.stderr)
        return 1
    print(f"\nverify-blender: all {len(ARTIFACTS)} node-group checks pass")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - top-level guard for exit code 2
        print(f"verify-blender ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
