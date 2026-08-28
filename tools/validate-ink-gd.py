"""
tools/validate-ink-gd.py — Run the headless inkgd-runtime validation harness.

Validates that the lesson story_player.gd files actually run inside Godot's
inkgd runtime (the gate that bink's ink:play / ink:transcripts cannot cover —
those test story logic; this tests the Godot integration code).

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

PROJECT = "ink-test-project"
HARNESS_SCENE = "res://scenes/validate_runtime.tscn"


def find_godot() -> str | None:
    # Explicit override wins.
    env = os.environ.get("GODOT")
    if env and Path(env).exists():
        return env
    # PATH lookup (covers the mise shim).
    for name in ("godot", "godot4", "Godot"):
        found = shutil.which(name)
        if found:
            return found
    return None


def main() -> int:
    godot = find_godot()
    if godot is None:
        print("SKIP: Godot not found (set GODOT env var or put godot on PATH).")
        return 0

    project_dir = Path(PROJECT)
    if not project_dir.is_dir():
        print(f"ERROR: {PROJECT} not found", file=sys.stderr)
        return 2

    # Import first so new/changed scripts and scenes are registered. The inkgd
    # first-import SVG-icon warning is harmless (resolves on a second import).
    subprocess.run(
        [godot, "--headless", "--editor", "--import", "--quit", "--path", "."],
        cwd=project_dir, capture_output=True, text=True,
    )

    result = subprocess.run(
        [godot, "--headless", HARNESS_SCENE, "--path", "."],
        cwd=project_dir, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )

    # Surface the harness's own [Lxx] / PASS / FAIL lines; drop the RID-leak
    # shutdown noise the dummy headless renderer prints.
    for line in ((result.stdout or "") + (result.stderr or "")).splitlines():
        if any(k in line for k in ("[L0", "Confirmed", "ERROR:", "PASS", "FAIL")) \
           and "RID allocations" not in line:
            print(line)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
