#!/usr/bin/env python3
"""Initialize a fresh learning workspace (pure-Python port of init-workspace.sh).

Creates the required directory structure, seeds MISSION/RESOURCES, and drops a
placeholder lessons/index.html. Safe to run multiple times — won't overwrite
existing files.

Importable (serve.py calls init_workspace() in-process on first launch) or
runnable as a script:

    python tools/init_workspace.py                          # workspace/ at project root
    python tools/init_workspace.py --path library/my-topic # custom location
    python tools/init_workspace.py --default                # generic first-launch content

Cross-platform notes (ticket #245):
- No bash / python3-name / POSIX-symlink dependency.
- On Windows the workspace-local assets symlink is skipped: serve.py mounts
  /assets from PROJECT_ROOT, so the symlink is only needed for
  `python -m http.server` debugging on POSIX.
- Output is ASCII-safe (Windows cp1252 stdout can't encode ✓/✗).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "assets" / "workspace-template"

_DEFAULT_MISSION = """\
# Learning Workspace

This is your personal learning workspace. Topics you explore will generate
lessons, maps, quizzes, and reference docs here.

To get started, tell your AI assistant what you'd like to learn.
"""

_DEFAULT_RESOURCES = """\
# Resources

Verified sources for topics in this workspace. Populated automatically as you explore new domains.
"""

_INDEX_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lessons - {name}</title>
  <link rel="stylesheet" href="../assets/style.css">
</head>
<body>
  <main class="lesson-container">
    <h1>{name}</h1>
    <p>No lessons yet. Generate a topic map to get started.</p>
    <p><em>Run the teach skill or <code>mise run map:generate</code> to create your first map.</em></p>
  </main>
  <script src="../assets/lesson-actions.js" data-domain="{name}"></script>
</body>
</html>
"""

_SUBDIRS = (
    "lessons/quiz",
    "reference",
    ".user/learning-records/questions",
    "maps",
)


def init_workspace(
    workspace: Path | None = None,
    *,
    default: bool = False,
) -> dict:
    """Scaffold a learning workspace. Idempotent.

    Args:
        workspace: target directory. Relative paths are resolved against
            PROJECT_ROOT. Defaults to ``PROJECT_ROOT/workspace``.
        default: seed generic topic-agnostic MISSION/RESOURCES instead of
            copying from the workspace template.

    Returns:
        {"status": "created"|"exists", "workspace": str, "created": [paths],
         "warnings": [str]}
    """
    if workspace is None:
        ws = PROJECT_ROOT / "workspace"
    else:
        ws = workspace if workspace.is_absolute() else PROJECT_ROOT / workspace

    warnings: list[str] = []

    # Idempotency guard — matches serve.py's standardized workspace/lessons check.
    if (ws / "lessons").is_dir():
        lessons = len(list((ws / "lessons").glob("*.html")))
        maps = len(list((ws / "maps").glob("*.MAP.md"))) if (ws / "maps").is_dir() else 0
        return {
            "status": "exists",
            "workspace": str(ws),
            "created": [],
            "warnings": warnings,
            "lesson_files": lessons,
            "map_files": maps,
        }

    created: list[str] = []

    for sub in _SUBDIRS:
        (ws / sub).mkdir(parents=True, exist_ok=True)

    # Seed MISSION.md / RESOURCES.md (only if absent).
    if default:
        _write_if_absent(ws / "MISSION.md", _DEFAULT_MISSION, created)
        _write_if_absent(ws / "RESOURCES.md", _DEFAULT_RESOURCES, created)
    else:
        for name in ("MISSION.md", "RESOURCES.md"):
            dest = ws / name
            if not dest.exists():
                src = TEMPLATE_DIR / name
                if src.exists():
                    dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
                    created.append(str(dest))
                else:
                    warnings.append(f"template missing: {src}")

    # Assets symlink — POSIX only. serve.py mounts /assets from PROJECT_ROOT,
    # so this is only needed for `python -m http.server` debugging on POSIX.
    # On Windows a git/POSIX symlink becomes a broken text stub, so skip it.
    assets_link = ws / "assets"
    if not assets_link.exists() and not assets_link.is_symlink():
        if os.name == "posix":
            rel = os.path.relpath(PROJECT_ROOT / "assets", ws)
            try:
                assets_link.symlink_to(rel)
                created.append(str(assets_link))
            except OSError as e:
                warnings.append(f"could not create assets symlink: {e}")
        else:
            warnings.append(
                "skipped workspace/assets symlink on Windows "
                "(serve.py mounts /assets from project root)"
            )

    # Placeholder index so the workspace is immediately browsable.
    index = ws / "lessons" / "index.html"
    if not index.exists():
        index.write_text(_INDEX_TEMPLATE.format(name=ws.name), encoding="utf-8")
        created.append(str(index))

    return {
        "status": "created",
        "workspace": str(ws),
        "created": created,
        "warnings": warnings,
    }


def _write_if_absent(path: Path, content: str, created: list[str]) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")
        created.append(str(path))


def _parse_argv(argv: list[str]) -> tuple[Path | None, bool]:
    workspace: Path | None = None
    default = False
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--path" and i + 1 < len(argv):
            workspace = Path(argv[i + 1])
            i += 2
        elif arg == "--default":
            default = True
            i += 1
        else:
            print(f"Unknown argument: {arg}")
            print("Usage: init_workspace.py [--path <workspace-dir>] [--default]")
            sys.exit(1)
    return workspace, default


def main(argv: list[str] | None = None) -> int:
    workspace, default = _parse_argv(argv if argv is not None else sys.argv[1:])
    result = init_workspace(workspace, default=default)
    ws = result["workspace"]

    if result["status"] == "exists":
        print(f"Workspace already exists at: {ws}")
        print(f"  lessons/: {result['lesson_files']} lesson files")
        print(f"  maps/:    {result['map_files']} map files")
    else:
        print(f"Workspace ready at: {ws}")
        for w in result["warnings"]:
            print(f"  note: {w}")
        print("")
        print("Next steps:")
        print("  1. Edit MISSION.md with your learning goal")
        print("  2. Run: mise run serve")
        print("  3. Generate your first topic map")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
