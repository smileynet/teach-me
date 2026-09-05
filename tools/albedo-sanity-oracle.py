#!/usr/bin/env python3
"""albedo-sanity-oracle.py — aesthetic-outcome gate for baked toon albedos (#302).

The posterize / palette-snap / bake-export oracles validate the MATH of the toon-prep
pipeline. None catches the failure that actually shipped in #222: a palette-snapped albedo
that drifted to muddy violet-gray (red barrel → mean RGB 93,81,107) and rendered near-black
under the toon shader. It was caught only by manually reading pixels, late.

This oracle asserts two MEASURABLE aesthetic properties of a baked albedo vs. its source:

  HUE PRESERVED    — the baked albedo's dominant hue is within `hue_tol_deg` of the source's
                     dominant hue. Catches the red→purple drift (a palette whose shadow end is
                     a different hue family than the asset).
  LUMINANCE SPREAD — the bake is NOT collapsed into the darkest band: at most `max_dark_frac`
                     of pixels may fall in the lowest of N luminance slots, and mean luminance
                     must be ≥ `min_mean_lum`. Catches the crush (Barrel_01 = 94% in slot 0).

Sidecar-driven (`albedo-sanity-sidecar.json`): a list of {baked, source, expected thresholds}.
Pillow-based (the bake pipeline already uses Pillow). Exit 0 = all pass, 1 = a check failed,
2 = error. Structured JSON on --json.
"""
from __future__ import annotations

import argparse
import colorsys
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("albedo-sanity-oracle needs Pillow (pip/uv add pillow)", file=sys.stderr)
    sys.exit(2)

SIDECAR = Path("library/godot-gamedev/reference/code/bake-and-export/albedo-sanity-sidecar.json")
N_SLOTS = 6                    # luminance bands, matching the 6-slot palette
DEFAULTS = {"hue_tol_deg": 40.0, "max_dark_frac": 0.85, "min_mean_lum": 0.12}


def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _luminance(r: float, g: float, b: float) -> float:
    return 0.2126 * _srgb_to_linear(r) + 0.7152 * _srgb_to_linear(g) + 0.0722 * _srgb_to_linear(b)


def _dominant_hue_deg(img: Image.Image) -> float:
    """Mean hue (degrees) over reasonably-saturated, non-dark pixels (circular mean)."""
    import math
    px = list(img.convert("RGB").getdata())
    sx = sy = 0.0
    n = 0
    for r, g, b in px:
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if v > 0.15 and s > 0.15:          # ignore near-black / near-gray (unstable hue)
            sx += math.cos(h * 2 * math.pi)
            sy += math.sin(h * 2 * math.pi)
            n += 1
    if n == 0:
        return -1.0
    return (math.degrees(math.atan2(sy, sx)) % 360.0)


def _dark_fraction_and_mean(img: Image.Image) -> tuple[float, float]:
    px = list(img.convert("RGB").getdata())
    n = len(px)
    dark = 0
    lum_sum = 0.0
    for r, g, b in px:
        lum = _luminance(r / 255, g / 255, b / 255)
        lum_sum += lum
        if int(min(lum, 0.999999) * N_SLOTS) == 0:     # lowest luminance slot
            dark += 1
    return dark / n, lum_sum / n


def _hue_delta(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def check_one(entry: dict, root: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    baked_p = root / entry["baked"]
    source_p = root / entry["source"]
    tol = {**DEFAULTS, **{k: entry[k] for k in DEFAULTS if k in entry}}

    if not baked_p.exists():
        return ({"baked": entry["baked"], "error": "baked missing"}, [f"{entry['baked']}: file missing"])
    if not source_p.exists():
        return ({"baked": entry["baked"], "error": "source missing"}, [f"{entry['source']}: source missing"])

    baked, source = Image.open(baked_p), Image.open(source_p)
    src_hue = _dominant_hue_deg(source)
    baked_hue = _dominant_hue_deg(baked)
    dark_frac, mean_lum = _dark_fraction_and_mean(baked)

    hue_delta = _hue_delta(baked_hue, src_hue) if (src_hue >= 0 and baked_hue >= 0) else 999.0
    if hue_delta > tol["hue_tol_deg"]:
        errors.append(f"{entry['baked']}: hue drift {hue_delta:.0f}° > {tol['hue_tol_deg']:.0f}° "
                      f"(baked {baked_hue:.0f}° vs source {src_hue:.0f}°) — palette lost the asset's hue")
    if dark_frac > tol["max_dark_frac"]:
        errors.append(f"{entry['baked']}: {dark_frac:.0%} of pixels in the darkest slot "
                      f"> {tol['max_dark_frac']:.0%} — luminance crushed (reads black under the shader)")
    if mean_lum < tol["min_mean_lum"]:
        errors.append(f"{entry['baked']}: mean luminance {mean_lum:.3f} < {tol['min_mean_lum']:.3f} — too dark")

    return ({"baked": entry["baked"], "src_hue": round(src_hue, 1), "baked_hue": round(baked_hue, 1),
             "hue_delta": round(hue_delta, 1), "dark_frac": round(dark_frac, 3),
             "mean_lum": round(mean_lum, 3)}, errors)


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate baked toon albedo hue/luminance sanity (#302)")
    ap.add_argument("--json", action="store_true", help="emit JSON summary")
    ap.add_argument("--sidecar", default=str(SIDECAR))
    args = ap.parse_args()

    sidecar_p = Path(args.sidecar)
    if not sidecar_p.is_absolute():
        sidecar_p = Path.cwd() / sidecar_p
    root = Path.cwd()
    if not sidecar_p.exists():
        print(f"albedo-sanity-oracle: sidecar not found: {sidecar_p}", file=sys.stderr)
        return 2

    entries = json.loads(sidecar_p.read_text()).get("albedos", [])
    all_metrics, all_errors = [], []
    for e in entries:
        m, errs = check_one(e, root)
        all_metrics.append(m)
        all_errors.extend(errs)

    status = "pass" if not all_errors else "fail"
    if args.json:
        print(json.dumps({"status": status, "metrics": all_metrics, "errors": all_errors}, indent=2))
    else:
        for m in all_metrics:
            if "error" in m:
                print(f"  {m['baked']}: {m['error']}")
            else:
                print(f"  {m['baked']}: hue {m['baked_hue']}° (src {m['src_hue']}°, Δ{m['hue_delta']}°), "
                      f"dark {m['dark_frac']:.0%}, mean-lum {m['mean_lum']}")
        if all_errors:
            print("\nFAIL:")
            for e in all_errors:
                print(f"  - {e}")
        else:
            print(f"\nalbedo-sanity-oracle: {len(all_metrics)} albedo(s) pass hue + luminance sanity")

    return 0 if status == "pass" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - top-level guard for CI exit code 2
        print(f"albedo-sanity-oracle ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
