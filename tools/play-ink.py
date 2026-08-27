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
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.ink_compile import DEFAULT_INKLECATE, compile_file, inklecate_available, detect_nondeterminism

DEFAULT_INK_DIR = "ink-test-project/stories"
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
    success, issues, result_path = compile_file(
        ink_path, inklecate, output_json=json_path, count_visits=False
    )
    if not success:
        detail = "; ".join(i["message"] for i in issues) or "compile failed"
        print(f"    compile error: {detail[:200]}")
        return None
    return result_path


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


# --- Golden-transcript mode (#228 Part B) --------------------------------
#
# Drives a story through a FIXED choice sequence and records the emitted
# text. Committed .transcript fixtures let `mise run verify` replay+diff to
# catch WRONG-OUTPUT bugs (self-loop read counts, non-sticky choices) that
# compile cleanly and reach END — the class structural validation misses.
#
# Fixture format (diffable, human-reviewable):
#   line 1: "# choices: 0,1,2"  (the choice-index sequence driven)
#   line 2: "# story: NN_name.ink"
#   blank line, then the transcript: emitted text blocks separated by the
#   chosen-choice marker ">>> [choice text]".
#
# Determinism note: bink's Story exposes no RNG seed, so a story using
# `{shuffle}`/`RANDOM()` would flap. The 4 reference stories use none
# (confirmed by the #228 bug audit). If a shuffle story is added, exclude
# its shuffle lines from the diff or gate behind a testVar.

TRANSCRIPT_MARKER = ">>> "


def play_capture(json_path: Path, choice_seq: list[int], turn_cap: int) -> str:
    """
    Play a story through a fixed choice-index sequence, capturing output.
    Returns the transcript body (text blocks + chosen-choice markers).
    Raises InkRuntimeError on a dead end. Raises ValueError if the sequence
    runs out before the story ends or an index is out of range.
    """
    story = load_story(json_path)
    seq = iter(choice_seq)
    lines: list[str] = []
    turns = 0
    while turns < turn_cap:
        try:
            text = story.continue_maximally()
        except Exception as e:
            if "ran out of content" in str(e) or "RUNTIME ERROR" in str(e):
                raise InkRuntimeError(str(e)) from e
            raise
        if text and text.strip():
            lines.append(text.rstrip("\n"))
        choices = [str(c) for c in story.choices]
        if not choices:
            if not story.can_continue():
                return "\n".join(lines) + "\n"
            turns += 1
            continue
        try:
            idx = next(seq)
        except StopIteration:
            raise ValueError(
                f"choice sequence exhausted with {len(choices)} choice(s) still "
                f"pending (story did not reach END)"
            )
        if idx < 0 or idx >= len(choices):
            raise ValueError(
                f"choice index {idx} out of range (story offered {len(choices)})"
            )
        lines.append(f"{TRANSCRIPT_MARKER}{choices[idx]}")
        story.choose_choice_index(idx)
        turns += 1
    raise ValueError(f"turn cap {turn_cap} hit before story reached END")


def render_transcript(story_name: str, choice_seq: list[int], body: str) -> str:
    """Assemble the full fixture text (header + body)."""
    header = f"# choices: {','.join(str(i) for i in choice_seq)}\n# story: {story_name}\n\n"
    return header + body


def parse_transcript(fixture_text: str) -> tuple[list[int], str]:
    """Parse a .transcript fixture into (choice_seq, expected_body)."""
    lines = fixture_text.splitlines()
    choice_seq: list[int] = []
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith("# choices:"):
            raw = line.split(":", 1)[1].strip()
            choice_seq = [int(x) for x in raw.split(",")] if raw else []
        if line.strip() == "" and any(l.startswith("#") for l in lines[:i]):
            body_start = i + 1
            break
    body = "\n".join(lines[body_start:])
    if not body.endswith("\n"):
        body += "\n"
    return choice_seq, body


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


def _capture_mode(story_path: Path, choice_seq: list[int], inklecate: str, turn_cap: int) -> int:
    """Capture a transcript for one story and print it to stdout."""
    nd = detect_nondeterminism(story_path)
    if nd:
        print(
            f"ERROR: {story_path.name} contains nondeterministic constructs "
            f"({', '.join(nd)}). bink has no RNG seed API, so its transcript "
            f"would flap between runs. Golden-transcript capture is refused for "
            f"this story. (Reachability is still covered by `play-ink.py` play mode.)",
            file=sys.stderr,
        )
        return 1
    with tempfile.TemporaryDirectory(prefix="ink-capture-") as tmp:
        json_path = compile_ink(story_path, inklecate, Path(tmp))
        if json_path is None:
            print(f"ERROR: could not compile {story_path.name}", file=sys.stderr)
            return 1
        try:
            body = play_capture(json_path, choice_seq, turn_cap)
        except (InkRuntimeError, ValueError) as e:
            print(f"ERROR capturing {story_path.name}: {e}", file=sys.stderr)
            return 1
    sys.stdout.write(render_transcript(story_path.name, choice_seq, body))
    return 0


def _replay_mode(story_dir: Path, inklecate: str, turn_cap: int) -> int:
    """Replay all committed .transcript fixtures and diff against fresh runs."""
    transcript_dir = story_dir / "transcripts"
    fixtures = sorted(transcript_dir.glob("*.transcript")) if transcript_dir.is_dir() else []
    if not fixtures:
        print(f"No .transcript fixtures in {transcript_dir}/ — nothing to replay.")
        return 0

    print(f"Replaying {len(fixtures)} transcript fixture(s)\n")
    fail_count = 0
    with tempfile.TemporaryDirectory(prefix="ink-replay-") as tmp:
        out_dir = Path(tmp)
        for fixture in fixtures:
            choice_seq, expected = parse_transcript(fixture.read_text(encoding="utf-8"))
            story_path = story_dir / fixture.stem  # e.g. 02_choices_and_weave
            story_path = story_path.with_suffix(".ink")
            if not story_path.exists():
                print(f"  [XX] {fixture.name}: source story {story_path.name} missing")
                fail_count += 1
                continue
            nd = detect_nondeterminism(story_path)
            if nd:
                print(f"  [--] {fixture.name}: SKIP (nondeterministic: {', '.join(nd)})")
                continue
            json_path = compile_ink(story_path, inklecate, out_dir)
            if json_path is None:
                print(f"  [XX] {fixture.name}: compile failed")
                fail_count += 1
                continue
            try:
                actual = play_capture(json_path, choice_seq, turn_cap)
            except (InkRuntimeError, ValueError) as e:
                print(f"  [XX] {fixture.name}: replay error: {e}")
                fail_count += 1
                continue
            if actual == expected:
                print(f"  [ok] {fixture.name}")
            else:
                print(f"  [XX] {fixture.name}: transcript mismatch")
                _print_diff(expected, actual)
                fail_count += 1

    print(f"\nResults: {len(fixtures)} fixture(s), {len(fixtures) - fail_count} match, {fail_count} mismatch")
    if fail_count:
        print("FAILED (transcript mismatch — review the diff; do NOT blindly re-capture)")
        return 1
    print("PASSED")
    return 0


def _print_diff(expected: str, actual: str) -> None:
    import difflib
    diff = difflib.unified_diff(
        expected.splitlines(), actual.splitlines(),
        fromfile="expected", tofile="actual", lineterm="",
    )
    for line in diff:
        print(f"       {line}")


def main():
    ink_dir = DEFAULT_INK_DIR
    inklecate = DEFAULT_INKLECATE
    turn_cap = DEFAULT_TURN_CAP
    mode = "play"          # play | capture | replay
    capture_story = None
    capture_choices: list[int] = []

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        flag = args[i]
        if flag in ("--dir", "--inklecate", "--turn-cap", "--story", "--choices"):
            if i + 1 >= len(args):
                print(f"ERROR: {flag} requires a value", file=sys.stderr)
                sys.exit(2)
            value = args[i + 1]
            if flag == "--dir":
                ink_dir = value
            elif flag == "--inklecate":
                inklecate = value
            elif flag == "--turn-cap":
                turn_cap = int(value)
            elif flag == "--story":
                capture_story = value
                mode = "capture"
            elif flag == "--choices":
                capture_choices = [int(x) for x in value.split(",")] if value else []
            i += 2
        elif flag == "--replay-transcripts":
            mode = "replay"
            i += 1
        else:
            print(f"Unknown arg: {flag}", file=sys.stderr)
            sys.exit(2)

    # inklecate skip-guard: in verify contexts the binary may be absent.
    # Skip gracefully (exit 0) rather than hard-failing the whole pipeline.
    if not inklecate_available(inklecate):
        print(f"SKIP: inklecate not found at {inklecate} (set INKLECATE env var).")
        sys.exit(0)

    story_dir = Path(ink_dir)
    if not story_dir.is_dir():
        print(f"ERROR: story dir not found: {ink_dir}", file=sys.stderr)
        sys.exit(2)

    if mode == "capture":
        story_path = story_dir / capture_story if not Path(capture_story).exists() else Path(capture_story)
        if not story_path.exists():
            print(f"ERROR: story not found: {capture_story}", file=sys.stderr)
            sys.exit(2)
        sys.exit(_capture_mode(story_path, capture_choices, inklecate, turn_cap))

    if mode == "replay":
        sys.exit(_replay_mode(story_dir, inklecate, turn_cap))

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
