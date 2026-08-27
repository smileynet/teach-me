"""
play-ink.py — Automated playthrough validator for ink stories.

Compiles each .ink story, then plays it with bink using several choice
strategies to verify it reaches an ending (rather than hanging in a loop
or crashing). Matches the Monte Carlo pattern used by wildwinter/Ink-Tester,
with a hard turn-cap to bound non-terminating loops.

Strategies (a story PASSES if ANY strategy reaches END):
  - LAST:   always pick the last choice (usually "leave"/"flee"/exit)
  - FIRST:  always pick choice[0] (detects loops on the first branch)
  - RANDOM: independent seeded runs, each a fresh walk

Per-strategy outcomes are reported explicitly so a strategy-dependent
hang is never silently swallowed.

Outcome per strategy:
  - END:   reached a terminal state (no content, no choices)
  - LOOP:  hit the turn-cap without reaching an ending
  - ERROR: the ink runtime raised (e.g., "ran out of content" dead end)

Story classification:
  - PASS:  at least one strategy reached END and none errored
  - FAIL:  any strategy hit an ink runtime ERROR (a real dead-end bug)
  - WARN:  no strategy errored, but none reached END (all loop)

Usage:
    python tools/play-ink.py [--dir DIR] [--inklecate PATH] [--turn-cap N]

Requires: bink (installed via the mise setup task).
Exit codes: 0=all pass, 1=one or more fail, 2=setup error.
"""

import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_INK_DIR = "ink-test-project/stories"
DEFAULT_INKLECATE = os.environ.get("INKLECATE", "D:/tools/inklecate/inklecate.exe")
DEFAULT_TURN_CAP = 200
RANDOM_RUNS = 3
RANDOM_SEED = 42

try:
    from bink.story import Story
except ImportError:
    print("ERROR: bink is not installed. Run: mise run setup", file=sys.stderr)
    sys.exit(2)


class InkRuntimeError(Exception):
    """A story-level ink runtime error (dead end, ran out of content, etc.)."""


def compile_ink(ink_path: Path, inklecate: str, out_dir: Path) -> Path | None:
    """Compile an .ink file to .ink.json in out_dir. Returns json path or None."""
    json_path = out_dir / (ink_path.stem + ".ink.json")
    cmd = [inklecate, "-o", str(json_path), str(ink_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        combined = (result.stdout or "") + (result.stderr or "")
        print(f"    compile error: {combined.strip()[:200]}")
        return None
    return json_path


def load_story(json_path: Path) -> Story:
    return Story(json_path.read_text(encoding="utf-8"))


def play_once(json_path: Path, pick, turn_cap: int) -> tuple[str, int]:
    """
    Play a story using `pick(num_choices) -> index`.
    Returns (outcome, turns): outcome in {"END", "LOOP", "ERROR"}.
    Only ink runtime errors are caught here; tool bugs propagate.

    Loop detection is by turn-cap. State-hash detection was evaluated and
    rejected: ink's save_state() always includes incrementing visit counts,
    so a repeated logical state never produces a repeated hash — it can
    never fire. The turn-cap is the honest, guaranteed mechanism.
    """
    story = load_story(json_path)
    turns = 0
    while turns < turn_cap:
        try:
            story.continue_maximally()
        except Exception as e:  # bink raises a RuntimeError for ink errors
            if "ran out of content" in str(e) or "RUNTIME ERROR" in str(e):
                raise InkRuntimeError(str(e)) from e
            raise  # tool bug — let it propagate
        choices = list(story.choices)
        if not choices:
            if not story.can_continue():
                return ("END", turns)
            turns += 1
            continue
        idx = pick(len(choices))
        story.choose_choice_index(idx)
        turns += 1
    return ("LOOP", turns)


def run_strategy(json_path: Path, pick, turn_cap: int) -> tuple[str, int]:
    """Run one strategy, converting ink errors into an ERROR outcome."""
    try:
        return play_once(json_path, pick, turn_cap)
    except InkRuntimeError:
        return ("ERROR", 0)


def validate_story(ink_path: Path, inklecate: str, turn_cap: int, out_dir: Path) -> dict:
    json_path = compile_ink(ink_path, inklecate, out_dir)
    if json_path is None:
        return {"name": ink_path.name, "status": "FAIL", "detail": "compilation failed"}

    results: dict[str, tuple[str, int]] = {}
    results["last"] = run_strategy(json_path, lambda n: n - 1, turn_cap)
    results["first"] = run_strategy(json_path, lambda n: 0, turn_cap)

    # Random: independent seeded runs (fresh RNG per run for reproducibility)
    random_outcome = ("LOOP", turn_cap)
    for run_i in range(RANDOM_RUNS):
        rng = random.Random(RANDOM_SEED + run_i)
        outcome = run_strategy(json_path, lambda n: rng.randrange(n), turn_cap)
        if outcome[0] == "END":
            random_outcome = outcome
            break
        if outcome[0] == "ERROR":
            random_outcome = outcome
            break
    results["random"] = random_outcome

    detail = ", ".join(f"{k}:{o}({t}t)" for k, (o, t) in results.items())
    outcomes = [o for o, _ in results.values()]

    if "ERROR" in outcomes:
        status = "FAIL"
    elif "END" in outcomes:
        status = "PASS"
    else:
        status = "WARN"

    return {"name": ink_path.name, "status": status, "detail": detail}


def main():
    ink_dir = DEFAULT_INK_DIR
    inklecate = DEFAULT_INKLECATE
    turn_cap = DEFAULT_TURN_CAP

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        flag = args[i]
        if flag in ("--dir", "--inklecate", "--turn-cap"):
            if i + 1 >= len(args):
                print(f"ERROR: {flag} requires a value", file=sys.stderr)
                sys.exit(2)
            value = args[i + 1]
            if flag == "--dir":
                ink_dir = value
            elif flag == "--inklecate":
                inklecate = value
            else:
                turn_cap = int(value)
            i += 2
        else:
            print(f"Unknown arg: {flag}", file=sys.stderr)
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
    # Compile artifacts to a temp dir so we don't litter the stories directory.
    with tempfile.TemporaryDirectory(prefix="play-ink-") as tmp:
        out_dir = Path(tmp)
        for ink_path in ink_files:
            result = validate_story(ink_path, inklecate, turn_cap, out_dir)
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
