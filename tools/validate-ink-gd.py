"""
tools/validate-ink-gd.py — Run the headless inkgd-runtime validation harness.

Validates that the lesson story_player.gd files actually run inside Godot's
inkgd runtime (the gate that bink's ink:play / ink:transcripts cannot cover —
those test story logic; this tests the Godot integration code).

Single source of truth: the SHIPPED reference files. This script copies them
into ink-test-project fresh on each run (A4), so the harness can never validate
a stale copy that has drifted from what a learner downloads.

Skips gracefully (exit 0) when Godot is absent, mirroring how validate-ink.py
handles a missing inklecate — so `mise run verify` doesn't hard-fail on machines
without Godot.

Exit codes: 0 = pass or skipped, 1 = a runtime check failed, 2 = setup error.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path("ink-test-project")
HARNESS_SCENE = "res://scenes/validate_runtime.tscn"

# Shipped reference file -> where the harness project expects it.
# Single source of truth = the reference the learner downloads.
REFERENCE_FILES = {
    "examples/ink-godot/reference/code/godot-ink-integration/story_player.gd":
        "scenes/lesson05_player.gd",
    "examples/ink-godot/reference/code/tags-as-commands/story_player.gd":
        "scenes/lesson06_player.gd",
}
# Reference stories -> project stories (recompiled to .ink.json by the caller
# via ink:validate, but copy the source so it's the shipped one).
REFERENCE_STORIES = {
    "examples/ink-godot/reference/code/godot-ink-integration/05_first_godot_integration.ink":
        "stories/05_first_godot_integration.ink",
    "examples/ink-godot/reference/code/tags-as-commands/06_tags_as_commands.ink":
        "stories/06_tags_as_commands.ink",
}

INKLECATE = os.environ.get("INKLECATE", "D:/tools/inklecate/inklecate.exe")


def find_godot() -> str | None:
    env = os.environ.get("GODOT")
    if env and Path(env).exists():
        return env
    for name in ("godot", "godot4", "Godot"):
        found = shutil.which(name)
        if found:
            return found
    return None


def sync_reference_files() -> None:
    """Copy shipped reference players + stories into the harness project (A4)."""
    for src, dst in REFERENCE_FILES.items():
        shutil.copyfile(src, PROJECT / dst)
    for src, dst in REFERENCE_STORIES.items():
        shutil.copyfile(src, PROJECT / dst)


def compile_stories() -> bool:
    """Recompile the copied stories to .ink.json so the players load fresh output."""
    if not Path(INKLECATE).exists():
        return True  # ink:validate covers compile elsewhere; don't block here
    ok = True
    for dst in REFERENCE_STORIES.values():
        ink = PROJECT / dst
        out = ink.with_suffix(".ink.json")
        r = subprocess.run([INKLECATE, "-o", str(out), str(ink)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"ERROR: failed to compile {ink}", file=sys.stderr)
            ok = False
    return ok


def main() -> int:
    godot = find_godot()
    if godot is None:
        print("SKIP: Godot not found (set GODOT env var or put godot on PATH).")
        return 0

    if not PROJECT.is_dir():
        print(f"ERROR: {PROJECT} not found", file=sys.stderr)
        return 2

    # A4: validate exactly what ships.
    sync_reference_files()
    if not compile_stories():
        return 2

    # Import so new/changed scripts + scenes register. A3: a failed import is a
    # setup error, not a silent pass — check its return code.
    imp = subprocess.run(
        [godot, "--headless", "--editor", "--import", "--quit", "--path", "."],
        cwd=PROJECT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    # The inkgd first-import SVG-icon warning is harmless; a real import failure
    # shows a non-zero code AND script/parse errors. Guard on both to avoid the
    # known false exit-1 on clean first import (Godot < 4.3 behaviour).
    imp_out = (imp.stdout or "") + (imp.stderr or "")
    if imp.returncode != 0 and ("SCRIPT ERROR" in imp_out or "Parse Error" in imp_out):
        print("ERROR: Godot import failed with script/parse errors:", file=sys.stderr)
        for line in imp_out.splitlines():
            if "SCRIPT ERROR" in line or "Parse Error" in line:
                print("  " + line, file=sys.stderr)
        return 2

    result = subprocess.run(
        [godot, "--headless", HARNESS_SCENE, "--path", "."],
        cwd=PROJECT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )

    out = (result.stdout or "") + (result.stderr or "")
    for line in out.splitlines():
        if any(k in line for k in ("[L0", "Confirmed", "ERROR:", "PASS", "FAIL", "[sound]")) \
           and "RID allocations" not in line:
            print(line)

    # A3: the wrapper's exit code mirrors the harness scene's exit code.
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
