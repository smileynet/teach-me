#!/usr/bin/env python3
"""serve_harness.py — shared cross-platform serve.py bootstrap for the Playwright test tools.

Both test-navigation.py and test-cue-matrix.py need the same ~40 lines of fiddly logic:
own an ephemeral port, start serve.py on a workspace in its own process group, poll until
it answers, and tear it down cleanly on any platform. Factored here so the two suites share
ONE implementation (they differ only in which workspace they serve).

Usage:
    from lib.serve_harness import serve_workspace
    with serve_workspace("library") as base_url:
        ... run Playwright against base_url ...
    # server is terminated on exit (normal or exception)

If a server is already reachable at `prefer_url` (e.g. a dev server on 8787), it's reused
and NOT torn down — mirrors Playwright's reuseExistingServer.
"""
from __future__ import annotations

import contextlib
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _reachable(url: str) -> bool:
    try:
        with urllib.request.urlopen(url + "/index.html", timeout=2) as r:
            return getattr(r, "status", r.getcode()) == 200
    except Exception:
        return False


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextlib.contextmanager
def serve_workspace(workspace: str, prefer_url: str | None = None):
    """Serve `workspace` via serve.py on an ephemeral port; yield the base URL.

    If `prefer_url` is already serving this project (HTTP 200 on /index.html), reuse it
    (no spawn, no teardown). Otherwise spawn serve.py, wait for readiness, and terminate
    it on exit. Raises RuntimeError if the spawned server never becomes reachable.
    """
    if prefer_url and _reachable(prefer_url):
        yield prefer_url
        return

    port = _free_port()
    base_url = f"http://localhost:{port}"
    kw: dict = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if sys.platform == "win32":
        kw["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kw["preexec_fn"] = os.setsid  # own process group so we can kill children too
    proc = subprocess.Popen(
        [sys.executable, "tools/serve.py", "--workspace", workspace, "--port", str(port)],
        cwd=str(PROJECT_ROOT), **kw,
    )
    try:
        for _ in range(30):
            if _reachable(base_url):
                break
            time.sleep(0.3)
        else:
            raise RuntimeError(f"serve.py did not become reachable at {base_url} (workspace={workspace})")
        yield base_url
    finally:
        if sys.platform == "win32":
            proc.terminate()
        else:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                proc.terminate()
