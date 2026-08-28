#!/usr/bin/env python3
"""palette-snap-oracle.py — validate the palette-snap math taught in lesson #219 (0017).

Lesson 0017 (Palette Snapping) teaches mapping a posterized luminance to a fixed
artist palette via a 1D lookup table (Method B, the "CLUT"). Two math claims must
hold for the lesson — and the Blender node group built from it — to be correct:

  CLAIM 1 — luminance -> palette index (the quantize step):
      idx = clamp(floor(lum * N), 0, N-1)
    A luminance in [0,1] selects one of N palette slots. This is the same floor()
    quantization posterization uses (lesson 0016), reused as an index instead of a
    grey level.

  CLAIM 2 — index -> texel center (the Closest-interpolation lookup):
    An N-wide x 1-tall palette strip sampled with Closest interpolation returns the
    swatch whose texel CONTAINS the sample U. Sampling at the texel CENTER
        u = (idx + 0.5) / N
    lands squarely inside slot `idx` with maximum margin to both texel borders
    (border at idx/N and (idx+1)/N). This is why the lesson samples at the center,
    not the edge: edge sampling (u = idx/N) sits ON the border and is one float
    epsilon away from selecting the WRONG neighbouring swatch (the off-by-one the
    ticket flagged to resolve empirically — the oracle proves the center form is
    the safe one across a dense sweep).

  CLAIM 3 — round-trip: every luminance maps to EXACTLY ONE palette color, every
    palette color is reachable, and the boundaries fall at k/N for k in 1..N-1.

The palette here is the lesson's canonical 6-color warm-toon set (Barrel_01 wood
tones). The oracle is Blender-free — it validates the MATH the learner is taught and
that the node group must implement, which is the thing that actually breaks a lesson.
Tier-2 (blender --check) and Tier-3 (emit-bake) validate the node wiring separately.

Exit codes: 0 = all checks pass, 1 = a claim failed, 2 = error.
Structured JSON summary on --json.
"""
from __future__ import annotations

import argparse
import json
import math
import sys

# Canonical 6-color warm-toon palette (sRGB 0..1), darkest -> lightest.
# Value rises monotonically; hue shifts cool (shadow) -> warm (highlight);
# saturation peaks in the midtones. Order = palette-strip pixel order (slot 0..5).
PALETTE = [
    (0.101, 0.078, 0.145),  # 0 deep cool shadow (violet-black)
    (0.239, 0.157, 0.216),  # 1 shadow (muted plum)
    (0.451, 0.247, 0.235),  # 2 mid-shadow (warm brown)
    (0.647, 0.400, 0.271),  # 3 midtone (wood)
    (0.831, 0.596, 0.361),  # 4 light (warm tan)
    (0.965, 0.831, 0.569),  # 5 highlight (cream)
]
N = len(PALETTE)

# Dense sweep of the [0,1] luminance range (1001 samples covers endpoints + interior).
SWEEP = [i / 1000.0 for i in range(1001)]


def lum_to_index(lum: float, n: int = N) -> int:
    """CLAIM 1: idx = clamp(floor(lum * N), 0, N-1)."""
    return max(0, min(n - 1, math.floor(lum * n)))


def texel_center(idx: int, n: int = N) -> float:
    """CLAIM 2: the U coordinate at the center of palette slot `idx`."""
    return (idx + 0.5) / n


def closest_texel(u: float, n: int = N) -> int:
    """Which slot Closest-interpolation returns for sample U on an N-wide strip.

    Closest picks the texel whose center is nearest U; equivalently floor(u*N)
    clamped, since texel `k` spans [k/N, (k+1)/N). Models Blender's
    ShaderNodeTexImage interpolation='Closest' on a 1-D strip.
    """
    return max(0, min(n - 1, math.floor(u * n)))


def snap(lum: float, n: int = N):
    """Full pipeline: luminance -> index -> texel center -> sampled swatch."""
    idx = lum_to_index(lum, n)
    u = texel_center(idx, n)
    sampled = closest_texel(u, n)
    return idx, u, sampled


def check() -> tuple[list[dict], list[str]]:
    results: list[dict] = []
    errors: list[str] = []

    # --- CLAIM 1 + 2 + 3: dense sweep round-trip ---
    reached: set[int] = set()
    for lum in SWEEP:
        idx, u, sampled = snap(lum)
        # Center-sampled U must round-trip to the SAME slot (no off-by-one).
        if sampled != idx:
            errors.append(
                f"lum={lum:.3f}: index {idx} -> u={u:.4f} -> Closest returned {sampled} (off-by-one!)"
            )
        if not (0 <= idx < N):
            errors.append(f"lum={lum:.3f}: index {idx} out of range 0..{N-1}")
        reached.add(idx)

    # Every palette slot must be reachable by some luminance (no dead swatches).
    if reached != set(range(N)):
        missing = sorted(set(range(N)) - reached)
        errors.append(f"unreachable palette slots {missing} (some luminance never selects them)")

    # --- Boundaries land at k/N for k in 1..N-1 (where the selected index flips) ---
    boundaries = []
    prev_idx = lum_to_index(0.0)
    for lum in SWEEP:
        idx = lum_to_index(lum)
        if idx != prev_idx:
            boundaries.append(round(lum, 3))
            prev_idx = idx
    expected_boundaries = [round(k / N, 3) for k in range(1, N)]
    # Allow one sweep-step (0.001) of tolerance since boundaries are sampled.
    for exp in expected_boundaries:
        if not any(abs(b - exp) <= 0.0011 for b in boundaries):
            errors.append(f"expected index boundary near {exp} (k/N) not found in {boundaries}")

    # --- Edge-sampling counter-example: sampling just below a texel border ---
    # Prove WHY the lesson samples the center. Floating-point luminance can land a
    # hair below a slot's left border (idx/N - epsilon); Closest then returns the
    # PREVIOUS slot. Center sampling ((idx+0.5)/N) has a full half-texel of margin
    # to either border, so no epsilon jitter can flip it. This documents the gotcha
    # the ticket flagged (the (index+0.5)/N vs index/N choice).
    eps = 1e-6
    edge_off_by_one = 0
    for idx in range(1, N):
        u_edge = idx / N - eps  # a hair below slot idx's left border
        if closest_texel(u_edge) != idx:
            edge_off_by_one += 1  # returned idx-1 — the wrong swatch
    center_off_by_one = 0
    for idx in range(N):
        if closest_texel(texel_center(idx)) != idx:
            center_off_by_one += 1
    if center_off_by_one != 0:
        errors.append(f"center sampling produced {center_off_by_one} off-by-one (should be 0)")
    if edge_off_by_one == 0:
        errors.append("edge-sampling counter-example failed to demonstrate the border risk")

    # --- Worked example table the lesson cites ---
    worked = []
    for lum in (0.0, 0.2, 0.5, 0.8, 1.0):
        idx, u, sampled = snap(lum)
        worked.append({"lum": lum, "index": idx, "u": round(u, 4),
                       "swatch": [round(c, 3) for c in PALETTE[sampled]]})

    results.append({
        "palette_size": N,
        "boundaries": boundaries,
        "expected_boundaries": expected_boundaries,
        "slots_reached": len(reached),
        "edge_sampling_off_by_one": edge_off_by_one,   # >0 = why we sample the center
        "center_sampling_off_by_one": center_off_by_one,  # must be 0
        "worked_examples": worked,
    })
    return results, errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate lesson #219 palette-snap math")
    ap.add_argument("--json", action="store_true", help="emit JSON summary")
    args = ap.parse_args()

    results, errors = check()
    status = "pass" if not errors else "fail"

    if args.json:
        print(json.dumps({"status": status, "metrics": results, "errors": errors}, indent=2))
    else:
        m = results[0]
        print(f"  palette: {m['palette_size']} swatches, all reachable: "
              f"{m['slots_reached'] == m['palette_size']}")
        print(f"  index boundaries at k/N: {m['boundaries']}")
        print(f"  center-sampling off-by-one: {m['center_sampling_off_by_one']} "
              f"(edge-sampling would be {m['edge_sampling_off_by_one']} — why we sample the center)")
        print("  worked examples (lum -> slot):")
        for w in m["worked_examples"]:
            print(f"    lum={w['lum']:.1f} -> slot {w['index']} u={w['u']:.4f} -> {w['swatch']}")
        if errors:
            print("\nFAIL:")
            for e in errors:
                print(f"  - {e}")
        else:
            print("\npalette-snap-oracle: all claims hold (lum->index, center-sample->swatch, boundaries at k/N)")

    return 0 if status == "pass" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - top-level guard for CI exit code 2
        print(f"palette-snap-oracle ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
