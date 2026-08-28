"""
tools/ink-gd-run.py — Run the headless inkgd-runtime validation harness.

Assumes the shipped reference files are already synced (ink-gd-sync.py) and the
stories are compiled (ink:validate). This script does only the irreducible work
mise can't: locate Godot, guard the import, run the harness, filter Godot's noisy
output, and map the exit code.

GODOT comes from the environment (mise [env] GODOT = { default = "godot" }); may be
a bare command name (resolved on PATH) or an absolute path (mise.local.toml).

Exit codes: 0 = pass or skipped (Godot absent), 1 = a runtime check failed,
2 = setup error (import failed with script/parse errors).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path("ink-test-project")
HARNESS_SCENE = "res://scenes/validate_runtime.tscn"


def resolve_godot() -> str | None:
    godot = os.environ.get("GODOT", "godot")
    # Accept either an existing absolute path or a PATH-resolvable command.
    if Path(godot).exists():
        return godot
    return shutil.which(godot)


def main() -> int:
    godot = resolve_godot()
    if godot is None:
        print("SKIP: Godot not found (set GODOT in mise.local.toml or PATH).")
        return 0

    if not PROJECT.is_dir():
        print(f"ERROR: {PROJECT} not found", file=sys.stderr)
        return 2

    # Import so synced scripts + scenes register. Run it TWICE: on a cold
    # .godot/ cache (fresh checkout) the first editor import emits benign
    # load-order noise — "SCRIPT ERROR: Parse Error: Could not preload ... icon.svg"
    # and "ERROR: Failed loading resource ...ctex" (Godot #68615/#89879, inkgd's
    # icon-bearing plugins). These clear once the cache is warm, so the SECOND
    # pass (and the harness run below) are clean. There is no guard on the import
    # output: a broken LESSON player is only load()ed at scene-instantiation, so
    # its parse error never appears here — it surfaces in the harness run, where
    # the anchored guard below catches it.
    for _ in range(2):
        subprocess.run(
            [godot, "--headless", "--editor", "--import", "--quit", "--path", "."],
            cwd=PROJECT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    result = subprocess.run(
        [godot, "--headless", HARNESS_SCENE, "--path", "."],
        cwd=PROJECT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )

    out = (result.stdout or "") + (result.stderr or "")
    for line in out.splitlines():
        if any(k in line for k in ("[L0", "Confirmed", "ERROR:", "PASS", "FAIL", "[sound]")) \
           and "RID allocations" not in line:
            print(line)

    # A GDScript parse error in a lesson player surfaces at scene-instantiation
    # during the harness run (Godot's exit code doesn't reflect it). Anchor on
    # Godot's line-LEADING error prefix — not a free substring — so arbitrary
    # story text interpolated into the harness's own "[Lxx] ERROR: ... got: ..."
    # messages can never misclassify a normal check-failure (exit 1) as a
    # setup/parse failure (exit 2).
    if any(line.startswith(("SCRIPT ERROR", "ERROR: Failed to load script"))
           for line in out.splitlines()):
        print("ERROR: a lesson player failed to load (parse/script error).", file=sys.stderr)
        return 2

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
