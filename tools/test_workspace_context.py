"""Workspace boundaries must keep content and learner state together."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib.overlay import Overlay
from lib.workspace_context import WorkspaceContext
from generate_map_page import topic_has_lesson


def _workspace(root: Path, domain: str) -> Path:
    (root / "maps").mkdir(parents=True)
    (root / "lessons").mkdir()
    (root / "maps" / f"{domain}.MAP.md").write_text(f"---\ndomain: {domain}\n---\n", encoding="utf-8")
    return root


def test_contexts_keep_content_and_overlay_roots_separate():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        first = WorkspaceContext.from_root(_workspace(root / "first", "first"))
        second = WorkspaceContext.from_root(_workspace(root / "second", "second"))
        node_id = "01M1T33FPC4YTKKSXWH53N60PZ"
        (first.lessons_dir / "first-topic.html").write_text("", encoding="utf-8")

        Overlay(first.overlay_root).set(node_id, "complete")

        assert first.maps[0].parent.parent == first.root
        assert second.maps[0].parent.parent == second.root
        assert first.lessons_dir != second.lessons_dir
        assert first.questions_dir != second.questions_dir
        assert topic_has_lesson("first-topic", first) == "first-topic.html"
        assert topic_has_lesson("first-topic", second) is None
        assert Overlay(first.overlay_root).status_map() == {node_id: "complete"}
        assert Overlay(second.overlay_root).status_map() == {}


def test_explicit_workspace_without_maps_fails_clearly():
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [sys.executable, "tools/serve.py", "--workspace", tmp, "--port", "0"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Workspace has no MAP.md files" in result.stdout
