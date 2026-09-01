#!/usr/bin/env python3
"""control-maps-drift.py — Pillow drift-check for the #220 toon control maps.

COMPLEMENTARY to control-maps-oracle.py (the stdlib sidecar oracle), not a replacement.
The sidecar oracle trusts values measured at bake time; this check re-measures the
COMMITTED PNGs on disk and asserts they still match the sidecar — catching a
hand-edited or re-exported map that the sidecar (only regenerated on re-bake) would miss.

Division of labour (they cannot substitute for each other):
  sidecar oracle  -> colorspace INTENT (Non-Color), AO correlation — knowable only in
                     Blender at bake time; a PNG carries no reliable Non-Color flag.
  this drift-check -> actual shipped BYTES: dimensions, channel mode, and opposite-edge
                     match (tileability) recomputed from the PNG, compared to the sidecar.

Pillow is a first-class project dep (mise.toml setup + doctor). This check still guards
the import so a fresh checkout before `mise run setup` skips instead of hard-failing —
mirroring verify-interactive.py's playwright guard.

Exit codes: 0 = PNGs match sidecar (or skipped: Pillow absent / maps not baked yet),
            1 = a committed PNG drifted from the sidecar, 2 = error.
"""
from __future__ import annotations

# Windows consoles default to cp1252; force UTF-8 so ✓/→/emoji glyphs don't crash (#265).
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(_sys.stderr, "reconfigure"):
    _sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("⚠ Pillow not installed — skipping control-map drift check", file=sys.stderr)
    sys.exit(0)  # first-class dep, but don't block a pre-setup checkout

MAPDIR = Path("library/godot-gamedev/reference/code/toon-control-maps")
SIDECAR = MAPDIR / "control-maps-sidecar.json"
FILES = {"noise": MAPDIR / "toon_noise.png", "threshold": MAPDIR / "toon_threshold.png"}

DIM_OK = 0          # dimensions must match exactly
EDGE_DRIFT_TOL = 0.03  # recomputed edge-diff may differ from sidecar by at most this


def _edge_max_diff(im: "Image.Image") -> float:
    """Max opposite-edge difference on the red channel, normalized 0..1.

    Convert to RGB first (palette mode P returns indices, not colors, and drops the
    palette under raw pixel access). Pillow is (x, y); we index accordingly.
    """
    im = im.convert("RGB")
    w, h = im.size
    px = im.load()
    left_right = max(abs(px[0, y][0] - px[w - 1, y][0]) for y in range(h))
    top_bottom = max(abs(px[x, 0][0] - px[x, h - 1][0]) for x in range(w))
    return max(left_right, top_bottom) / 255.0


def main() -> int:
    if not SIDECAR.exists() or not all(f.exists() for f in FILES.values()):
        print("⚠ control maps not baked yet — skipping drift check "
              "(run control_maps.py --bake)", file=sys.stderr)
        return 0

    sidecar = json.loads(SIDECAR.read_text())["maps"]
    errors: list[str] = []

    for name, path in FILES.items():
        rec = sidecar.get(name)
        if rec is None:
            errors.append(f"{name}: no sidecar entry to compare against")
            continue
        with Image.open(path) as im:
            w, h = im.size
            if (w, h) != (rec["w"], rec["h"]):
                errors.append(f"{name}: on-disk {w}x{h} != sidecar {rec['w']}x{rec['h']} (drift)")
            measured = _edge_max_diff(im)
            recorded = rec["edge_max_diff"]
            if abs(measured - recorded) > EDGE_DRIFT_TOL:
                errors.append(f"{name}: edge_max_diff on disk {measured:.4f} != sidecar "
                              f"{recorded:.4f} (drift > {EDGE_DRIFT_TOL})")
            print(f"  {name:9s}: {w}x{h}  edge_max_diff disk={measured:.4f} sidecar={recorded:.4f}")

    if errors:
        print("\n✗ control-map drift detected:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("\ncontrol-maps-drift: committed PNGs match the sidecar (dims + edge-match)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"control-maps-drift ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
