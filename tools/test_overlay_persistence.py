"""Concurrency and recovery contract for the private status overlay."""

from __future__ import annotations

import json
import multiprocessing
import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from lib import ulid
from lib.overlay import Overlay, OverlayRecoveryError


def _write_records(root: str, records: list[tuple[str, str]]) -> None:
    overlay = Overlay(root)
    for node_id, status in records:
        overlay.set(node_id, status)


@pytest.mark.parametrize("run", range(3))
def test_thread_contention_preserves_every_record(tmp_path, run):
    records = [(ulid.new(), "complete") for _ in range(100)]
    threads = [threading.Thread(target=_write_records, args=(str(tmp_path), [record])) for record in records]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert Overlay(tmp_path).status_map() == dict(records)


def test_process_contention_preserves_every_record(tmp_path):
    records = [(ulid.new(), "in-progress") for _ in range(100)]
    groups = [records[index:index + 25] for index in range(0, len(records), 25)]
    processes = [multiprocessing.Process(target=_write_records, args=(str(tmp_path), group)) for group in groups]
    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=15)
        assert process.exitcode == 0
    assert Overlay(tmp_path).status_map() == dict(records)


def test_readers_never_observe_a_partial_document_during_writes(tmp_path):
    records = [(ulid.new(), "complete") for _ in range(100)]
    overlay = Overlay(tmp_path)
    stop = threading.Event()
    errors: list[Exception] = []

    def reader():
        while not stop.is_set():
            try:
                overlay.load()
            except OverlayRecoveryError as error:
                errors.append(error)

    reader_thread = threading.Thread(target=reader)
    reader_thread.start()
    _write_records(str(tmp_path), records)
    stop.set()
    reader_thread.join()
    assert errors == []
    assert overlay.status_map() == dict(records)


def test_corrupt_overlay_surfaces_a_recovery_diagnostic(tmp_path):
    overlay = Overlay(tmp_path)
    overlay.path.parent.mkdir(parents=True)
    overlay.path.write_text('{"schema": 1, "overlay":', encoding="utf-8")

    with pytest.raises(OverlayRecoveryError, match="Malformed local overlay"):
        overlay.load()


def test_semantically_invalid_overlay_surfaces_a_recovery_diagnostic(tmp_path):
    overlay = Overlay(tmp_path)
    overlay.path.parent.mkdir(parents=True)
    overlay.path.write_text(json.dumps({"schema": 1, "overlay": {ulid.new(): "complete"}}), encoding="utf-8")

    with pytest.raises(OverlayRecoveryError, match="Malformed local overlay record"):
        overlay.status_map()


def test_failed_replace_keeps_last_complete_document(monkeypatch, tmp_path):
    overlay = Overlay(tmp_path)
    node_id = ulid.new()
    overlay.set(node_id, "in-progress")
    original = overlay.path.read_text(encoding="utf-8")

    def fail_replace(source, destination):
        raise PermissionError("sharing violation")

    monkeypatch.setattr("lib.overlay.os.replace", fail_replace)
    monkeypatch.setattr("lib.overlay._LOCK_TIMEOUT_SECONDS", 0)
    with pytest.raises(OverlayRecoveryError, match="Could not replace"):
        overlay.set(ulid.new(), "complete")
    assert overlay.path.read_text(encoding="utf-8") == original
