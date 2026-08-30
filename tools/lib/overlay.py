"""Per-user status overlay — a thin, gitignored map of {ULID node id → status}.

The committed content graph (MAP.md, #257) is shared and versioned; per-user progress
is NOT. This module is that per-user store: a single sparse JSON file under `.user/`
(gitignored), keyed by the immutable ULID node id. Absent key = not-started.

This is the FLOOR interface #258 calls and #255 fills out (quiz/SR relocation, prereq
indicator). Locked surface — keep signatures stable so #255 drops in without touching
call sites:

    load()             -> {"schema": 1, "overlay": {node_id: {status, updated_at}}}
    get(node_id)       -> {"status", "updated_at"} | None     (None on absent)
    set(node_id, s)    -> None                                (stamps updated_at)
    reset()            -> None                                (delete the file)

Design constraints (ADR-0014 §B, #255 "Out of scope"):
  - Keys are ULID node ids, NOT slugs (serve resolves slug→id upstream).
  - Sparse: absent key = not-started; `get` returns None on absent (never materialize
    a record on read — keeps the file sparse and `git status` clean).
  - Pure stdlib JSON. No event log, no sync, no serve write-API beyond simple status
    read/write (that apparatus is #259, backlog).

Instantiate `Overlay(root)` with the workspace/content root; the store lives at
`{root}/.user/status-overlay.json`. Module-level `load/get/set/reset` operate on a
default overlay resolved workspace-first (mirrors tools/questions.py).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

try:
    from tools.lib import ulid
except ModuleNotFoundError:  # tools/ on sys.path directly, or run as a script
    try:
        from lib import ulid  # type: ignore[no-redef]
    except ModuleNotFoundError:
        import sys as _sys

        _sys.path.insert(0, str(Path(__file__).resolve().parent))
        import ulid  # type: ignore[no-redef]

SCHEMA = 1
VALID_STATUSES = ("not-started", "in-progress", "complete")
_OVERLAY_FILENAME = "status-overlay.json"


def _now_iso() -> str:
    """UTC timestamp, second precision, Z-suffixed (e.g. 2026-08-29T14:00:00Z)."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class Overlay:
    """A per-user status overlay backed by a single sparse JSON file under `.user/`."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.path = self.root / ".user" / _OVERLAY_FILENAME

    def load(self) -> dict:
        """Return the full overlay document. Missing/corrupt file → empty sparse doc."""
        if not self.path.exists():
            return {"schema": SCHEMA, "overlay": {}}
        try:
            doc = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"schema": SCHEMA, "overlay": {}}
        if not isinstance(doc, dict) or not isinstance(doc.get("overlay"), dict):
            return {"schema": SCHEMA, "overlay": {}}
        return doc

    def get(self, node_id: str) -> dict | None:
        """Return {status, updated_at} for a node, or None if absent (not-started)."""
        return self.load()["overlay"].get(node_id)

    def set(self, node_id: str, status: str) -> None:
        """Set a node's status (stamps updated_at). Writes only the gitignored overlay."""
        if not ulid.is_valid(node_id):
            raise ValueError(f"overlay key must be a ULID node id, got {node_id!r}")
        if status not in VALID_STATUSES:
            raise ValueError(f"invalid status {status!r}, must be one of {VALID_STATUSES}")
        doc = self.load()
        doc["schema"] = SCHEMA
        doc["overlay"][node_id] = {"status": status, "updated_at": _now_iso()}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    def reset(self) -> None:
        """Delete the overlay file (resets all progress). No-op if absent."""
        self.path.unlink(missing_ok=True)

    def status_map(self) -> dict[str, str]:
        """Convenience join surface: {node_id → status} for keys present in the overlay."""
        return {nid: rec.get("status", "not-started") for nid, rec in self.load()["overlay"].items()}


# ---------------------------------------------------------------------------
# Default module-level overlay (workspace-first resolution, mirrors questions.py)
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # tools/lib/ -> project root
_WORKSPACE = _PROJECT_ROOT / "workspace"
_DEFAULT_ROOT = _WORKSPACE if _WORKSPACE.exists() else _PROJECT_ROOT

_default = Overlay(_DEFAULT_ROOT)


def load() -> dict:
    return _default.load()


def get(node_id: str) -> dict | None:
    return _default.get(node_id)


def set(node_id: str, status: str) -> None:  # noqa: A001 - locked interface name
    _default.set(node_id, status)


def reset() -> None:
    _default.reset()


def status_map_for_map(map_path) -> dict[str, str]:
    """{node_id → status} for the workspace that owns a `*.MAP.md` path.

    Shared by generate_index_page + generate_global_map (#155): a MAP.md lives at
    `{workspace}/maps/...`, so the overlay root is the maps dir's parent. Absent
    overlay (fresh clone) → empty map → all topics not-started.
    """
    p = Path(map_path)
    workspace = p.parent.parent if p.parent.name == "maps" else p.parent
    return Overlay(workspace).status_map()


if __name__ == "__main__":
    # Self-test in a temp dir: sparse defaults, round-trip, validation, reset.
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        ov = Overlay(d)
        assert ov.load() == {"schema": 1, "overlay": {}}, "fresh = empty sparse"
        nid = ulid.new()
        assert ov.get(nid) is None, "absent key = None (not-started)"
        ov.set(nid, "complete")
        rec = ov.get(nid)
        assert rec and rec["status"] == "complete" and rec["updated_at"].endswith("Z"), rec
        assert ov.status_map() == {nid: "complete"}, ov.status_map()
        # Validation rejections.
        for bad_key in ["not-a-ulid", "", "8" + "0" * 25]:
            try:
                ov.set(bad_key, "complete")
                raise AssertionError(f"expected reject for key {bad_key!r}")
            except ValueError:
                pass
        try:
            ov.set(nid, "bogus")
            raise AssertionError("expected reject for bad status")
        except ValueError:
            pass
        ov.reset()
        assert ov.get(nid) is None and not ov.path.exists(), "reset clears file"
    print("tools/lib/overlay.py self-test OK")
