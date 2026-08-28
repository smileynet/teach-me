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

    # Import so synced scripts + scenes register. Godot's `--import` is unreliable
    # about exit codes — it can return 0 even when a GDScript fails to parse. So
    # gate on the log content, not the return code: any "SCRIPT ERROR"/"Parse Error"
    # is a setup failure. (The harmless inkgd first-import SVG-icon warning uses a
    # different message — "plugin could not be initialized" — and is not matched.)
    imp = subprocess.run(
        [godot, "--headless", "--editor", "--import", "--quit", "--path", "."],
        cwd=PROJECT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    imp_out = (imp.stdout or "") + (imp.stderr or "")
    parse_errors = [l for l in imp_out.splitlines()
                    if "SCRIPT ERROR" in l or "Parse Error" in l]
    if parse_errors:
        print("ERROR: Godot import failed with script/parse errors:", file=sys.stderr)
        for line in parse_errors:
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

    # A GDScript parse error in a lesson player surfaces at scene-instantiation
    # time during the harness run (Godot's --import can return 0 despite it), as
    # "SCRIPT ERROR"/"Failed to load script". Treat that as a setup failure even
    # if the harness's own exit code didn't capture it.
    if "SCRIPT ERROR" in out or "Failed to load script" in out or "Parse Error" in out:
        print("ERROR: a lesson player failed to load (parse/script error).", file=sys.stderr)
        return 2

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
