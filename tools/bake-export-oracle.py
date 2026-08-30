#!/usr/bin/env python3
"""bake-export-oracle.py — validate the bake+export contracts taught in lesson #221 (0019).

The Tier-1 gate for the capstone bake/export step. Reads the sidecar `bake_export.py` writes
and asserts the pipeline's correctness contracts — the same pitfalls the lesson warns about,
made machine-checkable. Stdlib-only (like the posterize/palette-snap/control-maps oracles).

Contracts:
  albedo:  the baked albedo is 1024x1024 and **sRGB** (color data — unlike the control maps
           which are Non-Color). A wrong colorspace here is the lesson's #1 pitfall.
  glTF:    exists and is non-trivial; excludes lights AND cameras (Godot's toon shader lights
           dynamically — a baked light would double-shadow); and does NOT embed the control
           maps (they route through an sRGB glTF slot and get corrupted — the lesson's core
           gotcha; they ship as separate Non-Color PNGs instead).

Exit codes: 0 = all contracts hold, 1 = a contract failed, 2 = error (missing/bad sidecar).
Structured JSON summary on --json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SIDECAR = Path("library/godot-gamedev/reference/code/bake-and-export/bake-export-sidecar.json")
ALBEDO_RES = 1024
MIN_GLB_BYTES = 1024   # a real GLB is far bigger; guard against an empty/failed export


def check(sidecar_path: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    if not sidecar_path.exists():
        raise FileNotFoundError(f"sidecar not found: {sidecar_path} (run bake_export.py --bake)")
    data = json.loads(sidecar_path.read_text())

    albedo = data.get("albedo", {})
    if (albedo.get("w"), albedo.get("h")) != (ALBEDO_RES, ALBEDO_RES):
        errors.append(f"albedo: {albedo.get('w')}x{albedo.get('h')} != {ALBEDO_RES}x{ALBEDO_RES}")
    if albedo.get("colorspace") != "sRGB":
        errors.append(f"albedo: colorspace {albedo.get('colorspace')} != sRGB "
                      f"(baked albedo is color data — a control map would be Non-Color)")

    gltf = data.get("gltf", {})
    if not gltf.get("exists"):
        errors.append("glTF: export file does not exist")
    if gltf.get("size", 0) < MIN_GLB_BYTES:
        errors.append(f"glTF: size {gltf.get('size')} < {MIN_GLB_BYTES} (empty/failed export?)")
    if not gltf.get("lights_excluded"):
        errors.append("glTF: lights NOT excluded (a baked light double-shadows under the toon shader)")
    if not gltf.get("cameras_excluded"):
        errors.append("glTF: cameras NOT excluded")
    if gltf.get("control_maps_embedded"):
        errors.append("glTF: control maps embedded — they'd be sRGB-decoded through the "
                      "baseColorTexture slot and corrupted; ship them as separate Non-Color PNGs")

    return data, errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate lesson #221 bake/export contracts")
    ap.add_argument("--json", action="store_true", help="emit JSON summary")
    ap.add_argument("--sidecar", default=str(SIDECAR))
    args = ap.parse_args()

    data, errors = check(Path(args.sidecar))
    status = "pass" if not errors else "fail"

    if args.json:
        print(json.dumps({"status": status, "metrics": data, "errors": errors}, indent=2))
    else:
        a, g = data.get("albedo", {}), data.get("gltf", {})
        print(f"  albedo: {a.get('w')}x{a.get('h')} {a.get('colorspace')}")
        print(f"  glTF:   {g.get('size')} bytes, lights_excluded={g.get('lights_excluded')}, "
              f"cameras_excluded={g.get('cameras_excluded')}, control_maps_embedded={g.get('control_maps_embedded')}")
        if errors:
            print("\nFAIL:")
            for e in errors:
                print(f"  - {e}")
        else:
            print("\nbake-export-oracle: all contracts hold (albedo sRGB 1K; glTF albedo-only, no lights/cameras)")

    return 0 if status == "pass" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - top-level guard for CI exit code 2
        print(f"bake-export-oracle ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
