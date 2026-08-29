"""
tools/ink-gd-sync.py — Copy shipped lesson reference files into the harness project.

The #235 harness validates the SHIPPED reference story_player.gd + .ink files, not
manually-synced copies. This script refreshes those copies from the single source of
truth (the reference the learner downloads) on each run, so the harness can never
validate stale code that has drifted (#238 A4).

Idempotent; no external tools needed. Exits 2 if a source file is missing.
"""

import shutil
import sys
from pathlib import Path

PROJECT = Path("ink-test-project")

# Shipped reference file -> harness location.
FILES = {
    "examples/ink-godot/reference/code/godot-ink-integration/story_player.gd":
        "scenes/lesson05_player.gd",
    "examples/ink-godot/reference/code/tags-as-commands/story_player.gd":
        "scenes/lesson06_player.gd",
    "examples/ink-godot/reference/code/godot-ink-integration/05_first_godot_integration.ink":
        "stories/05_first_godot_integration.ink",
    "examples/ink-godot/reference/code/tags-as-commands/06_tags_as_commands.ink":
        "stories/06_tags_as_commands.ink",
    "examples/ink-godot/reference/code/state-bridge/story_player.gd":
        "scenes/lesson07_player.gd",
    "examples/ink-godot/reference/code/state-bridge/07_state_bridge.ink":
        "stories/07_state_bridge.ink",
    "examples/ink-godot/reference/code/production-patterns/story_player.gd":
        "scenes/lesson08_player.gd",
    "examples/ink-godot/reference/code/production-patterns/08_production_patterns.ink":
        "stories/08_production_patterns.ink",
}


def main() -> int:
    for src, dst in FILES.items():
        src_path = Path(src)
        if not src_path.exists():
            print(f"ERROR: reference file missing: {src}", file=sys.stderr)
            return 2
        shutil.copyfile(src_path, PROJECT / dst)
    print(f"Synced {len(FILES)} reference file(s) into {PROJECT}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
