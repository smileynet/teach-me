"""
play-ink.py — Automated playthrough validator for ink stories.

Compiles each .ink story, then plays it with bink using three choice
strategies to verify it reaches an ending (rather than hanging in a loop
or crashing). Matches the Monte Carlo pattern used by wildwinter/Ink-Tester.

Strategies (a story PASSES if ANY strategy reaches END):
  - LAST:   always pick the last choice (usually "leave"/"flee"/exit)
  - FIRST:  always pick choice[0], turn-capped (detects infinite loops)
  - RANDOM: random choices, 3 runs, turn-capped

Classification:
  - PASS: at least one strategy reached END (no content, no choices)
  - WARN: no strategy reached END but no error (likely an intentional
          loop with no auto-reachable exit under these strategies)
  - FAIL: an exception occurred during play, or compilation failed

Usage:
    python tools/play-ink.py [--dir DIR] [--inklecate PATH] [--turn-cap N]

Requires: bink (installed via the mise setup task).

Exit codes: 0=all pass, 1=one or more fail, 2=setup error.
"""

import os
import random
import subprocess
import sys
from pathlib import Path

DEFAULT_INK_DIR = "ink-test-project/stories"
DEFAULT_INKLECATE = os.environ.get("INKLECATE", "D:/tools/inklecate/inklecate.exe")
DEFAULT_TURN_CAP = 200
RANDOM_RUNS = 3

try:
    from bink.story import story_from_file
except ImportError:
    print("ERROR: bink is not installed. Run: mise run setup", file=sys.stderr)
    sys.exit(2)


def compile_ink(ink_path: Path, inklecate: str) -> Path | None:
    """Compile an .ink file to .ink.json. Returns the json path, or None on failure."""
    json_path = ink_path.with_suffix(".ink.json")
    cmd = [inklecate, "-o", str(json_path), str(ink_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        combined = (result.stdout or "") + (result.stderr or "")
        print(f"    compile error: {combined.strip()[:200]}")
        return None
    return json_path


def is_ended(story) -> bool:
    """A story has ended when it can't continue and offers no choices."""
    return not story.can_continue() and len(list(story.choices)) == 0


def play_once(json_path: Path, pick, turn_cap: int) -> tuple[str, int]:
    """
    Play a story to completion using the `pick` function to select choices.
    `pick(num_choices)` returns the index to choose.
    Returns (outcome, turns) where outcome is "END", "LOOP", or "ERROR".
    """
    story = story_from_file(str(json_path))
    turns = 0
    while turns < turn_cap:
        # Exhaust available content
        story.continue_maximally()
        choices = list(story.choices)
        if not choices:
            # No choices and can't continue → ended
            if not story.can_continue():
                return ("END", turns)
            # Can continue but produced no choices — loop guard
            turns += 1
            continue
        idx = pick(len(choices))
        story.choose_choice_index(idx)
        turns += 1
    return ("LOOP", turns)


def validate_story(ink_path: Path, inklecate: str, turn_cap: int) -> dict:
    """Compile and play a story through all strategies. Returns a result dict."""
    json_path = compile_ink(ink_path, inklecate)
    if json_path is None:
        return {"name": ink_path.name, "status": "FAIL", "detail": "compilation failed"}

    strategies = {
        "last": lambda n: n - 1,
        "first": lambda n: 0,
    }

    results = {}
    try:
        for label, pick in strategies.items():
            outcome, turns = play_once(json_path, pick, turn_cap)
            results[label] = (outcome, turns)

        # Random: multiple runs, record best outcome
        rng = random.Random(42)
        random_best = ("LOOP", turn_cap)
        for _ in range(RANDOM_RUNS):
            outcome, turns = play_once(json_path, lambda n: rng.randrange(n), turn_cap)
            if outcome == "END":
                random_best = (outcome, turns)
                break
        results["random"] = random_best
    except Exception as e:
        return {"name": ink_path.name, "status": "FAIL", "detail": f"runtime error: {e}"}

    reached_end = [label for label, (o, _) in results.items() if o == "END"]
    if reached_end:
        status = "PASS"
        detail = ", ".join(f"{label}:{results[label][0]}({results[label][1]}t)" for label in results)
    else:
        status = "WARN"
        detail = "no strategy reached END: " + ", ".join(
            f"{label}:{results[label][0]}" for label in results
        )

    return {"name": ink_path.name, "status": status, "detail": detail}


def main():
    ink_dir = DEFAULT_INK_DIR
    inklecate = DEFAULT_INKLECATE
    turn_cap = DEFAULT_TURN_CAP

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--dir":
            ink_dir = args[i + 1]; i += 2
        elif args[i] == "--inklecate":
            inklecate = args[i + 1]; i += 2
        elif args[i] == "--turn-cap":
            turn_cap = int(args[i + 1]); i += 2
        else:
            print(f"Unknown arg: {args[i]}", file=sys.stderr)
            sys.exit(2)

    if not Path(inklecate).exists():
        print(f"ERROR: inklecate not found at {inklecate}", file=sys.stderr)
        sys.exit(2)

    story_dir = Path(ink_dir)
    if not story_dir.is_dir():
        print(f"ERROR: story dir not found: {ink_dir}", file=sys.stderr)
        sys.exit(2)

    ink_files = sorted(story_dir.glob("*.ink"))
    if not ink_files:
        print(f"No .ink files found in {ink_dir}", file=sys.stderr)
        sys.exit(2)

    print(f"Playing {len(ink_files)} ink story/stories in {ink_dir}/")
    print(f"bink runtime, turn cap {turn_cap}\n")

    fail_count = 0
    warn_count = 0
    for ink_path in ink_files:
        result = validate_story(ink_path, inklecate, turn_cap)
        marker = {"PASS": "[ok]", "WARN": "[??]", "FAIL": "[XX]"}[result["status"]]
        print(f"  {marker} {result['name']}")
        print(f"       {result['detail']}")
        if result["status"] == "FAIL":
            fail_count += 1
        elif result["status"] == "WARN":
            warn_count += 1

    total = len(ink_files)
    passed = total - fail_count - warn_count
    print(f"\nResults: {total} stories, {passed} pass, {warn_count} warn, {fail_count} fail")
    if fail_count:
        print("FAILED (errors present)")
        sys.exit(1)
    print("PASSED")
    sys.exit(0)


if __name__ == "__main__":
    main()
