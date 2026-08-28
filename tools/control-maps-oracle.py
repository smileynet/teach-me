#!/usr/bin/env python3
"""control-maps-oracle.py — validate the toon control maps taught in lesson #220 (0018).

The Tier-1 gate for the noise + threshold maps. It reads the sidecar JSON that
`control_maps.py` writes at bake time (measured from img.pixels INSIDE Blender, where
per-pixel access and colorspace intent are both known) and asserts the contracts the
mk_toon_lite shader depends on. Stdlib-only (like posterize/palette-snap oracles) — it
validates the properties the maps must have, which is what actually breaks the lesson.

It is complementary to `control-maps-drift.py` (Pillow), which re-measures the COMMITTED
PNGs against this sidecar to catch a hand-edited/re-exported file. Neither can do the
other's job: PNG carries no reliable Non-Color flag, so only the sidecar (measured in
Blender) can assert colorspace intent; only the drift-check reads the actual shipped bytes.

Contracts asserted:
  noise:      256x256, Non-Color, tileable (edge_max_diff below tolerance — the 4D-noise
              trick makes opposite edges match; a small residual from texel-center phase
              offset is expected, so tolerance is < 0.15, not == 0).
  threshold:  Non-Color, derived from AO (ao_corr high — the map must actually track the
              ARM red channel it came from), full 0..1 range.

Exit codes: 0 = all contracts hold, 1 = a contract failed, 2 = error (missing/bad sidecar).
Structured JSON summary on --json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SIDECAR = Path("examples/godot-gamedev/reference/code/toon-control-maps/control-maps-sidecar.json")

# Contract thresholds (documented in the lesson):
NOISE_RES = 256
NOISE_EDGE_TOL = 0.15      # tileable: opposite-edge max diff must be under this
THRESHOLD_MIN_AO_CORR = 0.90  # threshold map must track the ARM AO it was derived from


def check(sidecar_path: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    if not sidecar_path.exists():
        raise FileNotFoundError(f"sidecar not found: {sidecar_path} (run control_maps.py --bake)")
    data = json.loads(sidecar_path.read_text())
    maps = data.get("maps", {})

    # ---- noise ----
    noise = maps.get("noise")
    if noise is None:
        errors.append("sidecar missing 'noise' map")
    else:
        if (noise["w"], noise["h"]) != (NOISE_RES, NOISE_RES):
            errors.append(f"noise: {noise['w']}x{noise['h']} != {NOISE_RES}x{NOISE_RES}")
        if noise["colorspace"] != "Non-Color":
            errors.append(f"noise: colorspace {noise['colorspace']} != Non-Color")
        if noise["edge_max_diff"] > NOISE_EDGE_TOL:
            errors.append(f"noise: edge_max_diff {noise['edge_max_diff']} > {NOISE_EDGE_TOL} "
                          f"(not tileable — 4D circle map broken or UV not 0..1)")
        if not (noise["r_min"] < 0.5 < noise["r_max"]):
            errors.append(f"noise: range [{noise['r_min']},{noise['r_max']}] not centered around 0.5")

    # ---- threshold ----
    thr = maps.get("threshold")
    if thr is None:
        errors.append("sidecar missing 'threshold' map")
    else:
        if thr["colorspace"] != "Non-Color":
            errors.append(f"threshold: colorspace {thr['colorspace']} != Non-Color")
        ao = thr.get("ao_corr")
        if ao is None:
            errors.append("threshold: missing ao_corr (not derived from AO?)")
        elif ao < THRESHOLD_MIN_AO_CORR:
            errors.append(f"threshold: ao_corr {ao} < {THRESHOLD_MIN_AO_CORR} "
                          f"(map does not track the ARM AO channel)")

    return data, errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate lesson #220 control-map contracts")
    ap.add_argument("--json", action="store_true", help="emit JSON summary")
    ap.add_argument("--sidecar", default=str(SIDECAR), help="path to control-maps-sidecar.json")
    args = ap.parse_args()

    data, errors = check(Path(args.sidecar))
    status = "pass" if not errors else "fail"

    if args.json:
        print(json.dumps({"status": status, "metrics": data.get("maps", {}), "errors": errors}, indent=2))
    else:
        for name, m in data.get("maps", {}).items():
            line = f"  {name:9s}: {m['w']}x{m['h']} {m['colorspace']} edge_max_diff={m['edge_max_diff']}"
            if "ao_corr" in m:
                line += f" ao_corr={m['ao_corr']}"
            print(line)
        if errors:
            print("\nFAIL:")
            for e in errors:
                print(f"  - {e}")
        else:
            print("\ncontrol-maps-oracle: all contracts hold (noise tileable+Non-Color, threshold tracks AO)")

    return 0 if status == "pass" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - top-level guard for CI exit code 2
        print(f"control-maps-oracle ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
