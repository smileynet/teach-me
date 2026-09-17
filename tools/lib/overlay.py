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
import os
import tempfile
import threading
import time
from contextlib import contextmanager
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
_LOCK_TIMEOUT_SECONDS = 10
_THREAD_LOCKS: dict[Path, threading.Lock] = {}
_THREAD_LOCKS_GUARD = threading.Lock()


class OverlayRecoveryError(RuntimeError):
    """The local overlay needs repair; its last known state was not discarded."""


def _now_iso() -> str:
    """UTC timestamp, second precision, Z-suffixed (e.g. 2026-08-29T14:00:00Z)."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class Overlay:
    """A per-user status overlay backed by a single sparse JSON file under `.user/`."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.path = self.root / ".user" / _OVERLAY_FILENAME
        self.lock_path = self.path.with_suffix(".lock")

    @contextmanager
    def _write_lock(self):
        """Serialize writers with retained OS locks; a crash cannot leave a stale lock."""
        with _THREAD_LOCKS_GUARD:
            thread_lock = _THREAD_LOCKS.setdefault(self.lock_path, threading.Lock())
        deadline = time.monotonic() + _LOCK_TIMEOUT_SECONDS
        if not thread_lock.acquire(timeout=_LOCK_TIMEOUT_SECONDS):
            raise OverlayRecoveryError(f"Timed out waiting for local overlay lock: {self.lock_path}")
        try:
            with self.lock_path.open("a+b") as lock:
                if lock.tell() == 0:
                    lock.write(b"0")
                    lock.flush()
                while True:
                    try:
                        if os.name == "nt":
                            import msvcrt

                            lock.seek(0)
                            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                        else:
                            import fcntl

                            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except OSError:
                        if time.monotonic() >= deadline:
                            raise OverlayRecoveryError(f"Timed out waiting for local overlay lock: {self.lock_path}")
                        time.sleep(0.01)
                try:
                    yield
                finally:
                    if os.name == "nt":
                        msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
                    else:
                        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        finally:
            thread_lock.release()

    def _atomic_write(self, doc: dict) -> None:
        """Replace the JSON document from a same-directory temporary file.

        `os.replace` is atomic on one filesystem. On Windows it can briefly fail while
        another process has the destination open, so retry that transient sharing error
        while retaining the old complete document.
        """
        descriptor, temporary = tempfile.mkstemp(prefix=f".{self.path.name}.", suffix=".tmp", dir=self.path.parent)
        temporary_path = Path(temporary)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as output:
                json.dump(doc, output, indent=2)
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())
            deadline = time.monotonic() + _LOCK_TIMEOUT_SECONDS
            while True:
                try:
                    os.replace(temporary_path, self.path)
                    break
                except PermissionError as error:
                    if time.monotonic() >= deadline:
                        raise OverlayRecoveryError(f"Could not replace local overlay: {self.path}") from error
                    time.sleep(0.01)
        finally:
            temporary_path.unlink(missing_ok=True)

    def load(self) -> dict:
        """Return the full overlay document, or a diagnostic for corrupt local state."""
        if not self.path.exists():
            return {"schema": SCHEMA, "overlay": {}}
        deadline = time.monotonic() + _LOCK_TIMEOUT_SECONDS
        try:
            while True:
                try:
                    text = self.path.read_text(encoding="utf-8")
                    break
                except FileNotFoundError:
                    return {"schema": SCHEMA, "overlay": {}}
                except PermissionError:
                    if time.monotonic() >= deadline:
                        raise
                    time.sleep(0.01)
            doc = json.loads(text)
        except json.JSONDecodeError as error:
            raise OverlayRecoveryError(f"Malformed local overlay at {self.path}: {error}") from error
        except OSError as error:
            raise OverlayRecoveryError(f"Could not read local overlay at {self.path}: {error}") from error
        if not isinstance(doc, dict) or not isinstance(doc.get("overlay"), dict):
            raise OverlayRecoveryError(f"Malformed local overlay at {self.path}: missing overlay object")
        if doc.get("schema") != SCHEMA:
            raise OverlayRecoveryError(f"Unsupported local overlay schema at {self.path}: {doc.get('schema')!r}")
        for node_id, record in doc["overlay"].items():
            if not ulid.is_valid(node_id) or not isinstance(record, dict):
                raise OverlayRecoveryError(f"Malformed local overlay record at {self.path}: {node_id!r}")
            if record.get("status") not in VALID_STATUSES or not isinstance(record.get("updated_at"), str):
                raise OverlayRecoveryError(f"Malformed local overlay record at {self.path}: {node_id!r}")
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
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._write_lock():
            doc = self.load()
            doc["schema"] = SCHEMA
            doc["overlay"][node_id] = {"status": status, "updated_at": _now_iso()}
            self._atomic_write(doc)

    def reset(self) -> None:
        """Delete the overlay file (resets all progress). No-op if absent."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._write_lock():
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


_DEMO_FILENAME = "demo-status.json"


def demo_status_map_for_map(map_path) -> dict[str, str]:
    """{node_id → status} from the COMMITTED demo fixture for a workspace (#279, Approach B).

    The demo/showcase progress that ships with the library lives in a committed
    `{workspace}/demo-status.json` — NOT under `.user/`. This decouples the shipped demo
    seed from the private per-user overlay (`.user/status-overlay.json`, which is
    gitignored again post-#279). The generator bakes counts + the inlined `demoOverlay`
    from THIS; the client reads the real user overlay live and overrides it. Absent fixture
    (a workspace with no demo) → empty map → zero baked counts, honestly.

    Same on-disk schema as the overlay (`{schema, overlay:{id:{status,...}}}`) so the
    fixture is just a committed overlay document; reuses Overlay's tolerant loader.
    """
    p = Path(map_path)
    workspace = p.parent.parent if p.parent.name == "maps" else p.parent
    fixture = workspace / _DEMO_FILENAME
    if not fixture.exists():
        return {}
    try:
        doc = json.loads(fixture.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    overlay = doc.get("overlay") if isinstance(doc, dict) else None
    if not isinstance(overlay, dict):
        return {}
    return {nid: rec.get("status", "not-started") for nid, rec in overlay.items()
            if isinstance(rec, dict)}


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

        # Demo fixture resolver (#279): reads committed {workspace}/demo-status.json, NOT
        # .user/. Absent fixture → empty map (honest zeros); present → flat {id: status}.
        maps_dir = Path(d) / "maps"
        maps_dir.mkdir(parents=True, exist_ok=True)
        fake_map = maps_dir / "x.MAP.md"
        fake_map.write_text("# x", encoding="utf-8")
        assert demo_status_map_for_map(fake_map) == {}, "absent demo fixture = empty"
        did = ulid.new()
        (Path(d) / _DEMO_FILENAME).write_text(
            json.dumps({"schema": 1, "overlay": {did: {"status": "complete", "updated_at": "z"}}}),
            encoding="utf-8")
        assert demo_status_map_for_map(fake_map) == {did: "complete"}, demo_status_map_for_map(fake_map)
    print("tools/lib/overlay.py self-test OK")
