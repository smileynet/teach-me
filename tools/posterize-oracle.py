#!/usr/bin/env python3
"""posterize-oracle.py — validate the posterize math taught in lesson #218.

Lesson 0016 (Albedo Posterization) teaches two quantization formulas:

  1. TRUNCATE (what posterize_albedo.gdshader:13 does):
         floor(x * N) / N
     Mirrors the shader exactly. Produces N distinct levels but the top level
     tops out at (N-1)/N — pure white is never reached (bands are dark-biased).

  2. CANONICAL (the taught improvement — round-to-nearest, endpoint-inclusive):
         floor(x * (N-1) + 0.5) / (N-1)
     Produces exactly N distinct levels with BLACK (0.0) and WHITE (1.0) as
     clean anchor bands, centered (unbiased).

This oracle asserts both formulas behave as the lesson claims across a dense
input sweep for N in {4, 8, 16}. It is the Tier-1 validation gate for #218 and
needs no Blender — it validates the math the learner is taught, which is the
thing that actually matters for the lesson's correctness.

Exit codes: 0 = all checks pass, 1 = a claim failed, 2 = error.
Structured JSON summary on --json.
"""
from __future__ import annotations

import argparse
import json
import math
import sys

LEVELS = (4, 8, 16)
# Dense sweep of the [0,1] input range (1001 samples covers endpoints + interior).
SWEEP = [i / 1000.0 for i in range(1001)]


def truncate(x: float, n: int) -> float:
    """floor(x*N)/N — the shader's form. Clamp handles the x==1.0 edge."""
    return math.floor(min(x, 0.999999) * n) / n


def canonical(x: float, n: int) -> float:
    """floor(x*(N-1)+0.5)/(N-1) — round-to-nearest, endpoint-inclusive."""
    return math.floor(x * (n - 1) + 0.5) / (n - 1)


def distinct_levels(fn, n: int) -> list[float]:
    return sorted({round(fn(x, n), 6) for x in SWEEP})


def check() -> tuple[list[dict], list[str]]:
    results: list[dict] = []
    errors: list[str] = []

    for n in LEVELS:
        # --- TRUNCATE: exactly N levels; top level is (N-1)/N; min is 0.0 ---
        t_levels = distinct_levels(truncate, n)
        if len(t_levels) != n:
            errors.append(f"truncate N={n}: expected {n} distinct levels, got {len(t_levels)}")
        if t_levels and abs(t_levels[0] - 0.0) > 1e-6:
            errors.append(f"truncate N={n}: min level {t_levels[0]} != 0.0")
        expected_top = (n - 1) / n
        if t_levels and abs(t_levels[-1] - expected_top) > 1e-6:
            errors.append(f"truncate N={n}: top level {t_levels[-1]} != (N-1)/N={expected_top} (should NOT reach 1.0)")
        results.append({"formula": "truncate", "N": n, "levels": len(t_levels),
                        "min": t_levels[0], "max": t_levels[-1]})

        # --- CANONICAL: exactly N levels; anchored at 0.0 AND 1.0; centered ---
        c_levels = distinct_levels(canonical, n)
        if len(c_levels) != n:
            errors.append(f"canonical N={n}: expected {n} distinct levels, got {len(c_levels)}")
        if c_levels and abs(c_levels[0] - 0.0) > 1e-6:
            errors.append(f"canonical N={n}: min level {c_levels[0]} != 0.0 (black anchor)")
        if c_levels and abs(c_levels[-1] - 1.0) > 1e-6:
            errors.append(f"canonical N={n}: max level {c_levels[-1]} != 1.0 (white anchor)")
        # Even spacing at 1/(N-1)
        expected = [round(k / (n - 1), 6) for k in range(n)]
        if c_levels != expected:
            errors.append(f"canonical N={n}: levels {c_levels} != evenly-spaced {expected}")
        results.append({"formula": "canonical", "N": n, "levels": len(c_levels),
                        "min": c_levels[0], "max": c_levels[-1]})

    # --- Worked N=4 example the lesson cites: {0, 0.333, 0.667, 1.0} ---
    n4 = distinct_levels(canonical, 4)
    n4_expected = [0.0, round(1 / 3, 6), round(2 / 3, 6), 1.0]
    if n4 != n4_expected:
        errors.append(f"canonical N=4: {n4} != cited example {n4_expected}")

    return results, errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate lesson #218 posterize math")
    ap.add_argument("--json", action="store_true", help="emit JSON summary")
    args = ap.parse_args()

    results, errors = check()
    status = "pass" if not errors else "fail"

    if args.json:
        print(json.dumps({"status": status, "metrics": results, "errors": errors}, indent=2))
    else:
        for r in results:
            print(f"  {r['formula']:9s} N={r['N']:2d}: {r['levels']} levels "
                  f"[{r['min']:.4f} .. {r['max']:.4f}]")
        if errors:
            print("\nFAIL:")
            for e in errors:
                print(f"  - {e}")
        else:
            print("\nposterize-oracle: all claims hold (truncate + canonical, N=4/8/16)")

    return 0 if status == "pass" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - top-level guard for CI exit code 2
        print(f"posterize-oracle ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
