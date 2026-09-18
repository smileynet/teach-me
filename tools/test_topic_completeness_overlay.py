"""Corrupt-overlay contract for check-topic-completeness (#374).

The #353 overlay contract made corrupt local state a recovery error instead of a silent
reset. serve.py surfaces it as 503; this pins the CLI side: `--all` must exit with a
distinct deliberate code and a readable diagnostic — never a traceback, and never a
silent "no complete topics" answer that would treat corrupt state as no progress.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).parent
PROJECT_ROOT = TOOLS.parent

_MINIMAL_MAP = """---
domain: overlay-recovery-fixture
description: "Fixture domain for the corrupt-overlay CLI contract"
generated: 2026-09-18
depth: 0
parent: null
leads_to: []
---

# Overlay Recovery Fixture

## Topics

### fixture-topic

- **title:** Fixture Topic
- **why:** Exists so the workspace has a map to parse
- **scope:** lightweight
- **prereqs:** []
"""


def _make_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "ws"
    (workspace / "maps").mkdir(parents=True)
    (workspace / "maps" / "fixture.MAP.md").write_text(_MINIMAL_MAP, encoding="utf-8")
    return workspace


def _run_checker(workspace: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TOOLS / "check-topic-completeness.py"),
         "--workspace", str(workspace), "--all"],
        capture_output=True, text=True, timeout=60,
    )


def test_corrupt_overlay_is_a_deliberate_state_error(tmp_path):
    workspace = _make_workspace(tmp_path)
    overlay = workspace / ".user" / "status-overlay.json"
    overlay.parent.mkdir(parents=True)
    overlay.write_text('{"schema": 1, "overlay":', encoding="utf-8")  # truncated JSON

    result = _run_checker(workspace)

    assert result.returncode == 3, (result.returncode, result.stdout, result.stderr)
    assert "needs repair" in result.stderr
    assert "status-overlay.json" in result.stderr
    assert "Traceback" not in result.stderr


def test_semantically_invalid_overlay_is_rejected_not_reset(tmp_path):
    workspace = _make_workspace(tmp_path)
    overlay = workspace / ".user" / "status-overlay.json"
    overlay.parent.mkdir(parents=True)
    overlay.write_text('{"schema": 1, "overlay": {"not-a-ulid": {"status": "complete"}}}',
                       encoding="utf-8")

    result = _run_checker(workspace)

    assert result.returncode == 3, (result.returncode, result.stdout, result.stderr)
    assert "needs repair" in result.stderr
    assert "Traceback" not in result.stderr


def test_healthy_workspace_still_reports_zero_complete(tmp_path):
    workspace = _make_workspace(tmp_path)

    result = _run_checker(workspace)

    # No overlay at all → legitimately no complete topics, exit 0 (regression guard:
    # the handler must not turn the ordinary empty case into an error).
    assert result.returncode == 0, (result.returncode, result.stdout, result.stderr)
    assert "No complete topics found" in result.stdout


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
