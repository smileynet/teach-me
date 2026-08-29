#!/usr/bin/env python3
"""serve-bg.py — Launch serve.py as a NON-BLOCKING background task (LAN-ready).

Fills the gap left by the blocking `serve`/`serve:lan` tasks and the Unix-only
`serve:restart` (its `lsof` line is dead on Windows). Spawns serve.py detached,
polls until it answers HTTP, prints the Local + LAN URLs, records the PID, and
returns — the server keeps running after this process exits.

Pattern reused from verify-interactive.py (detached Popen + readiness poll +
cross-platform teardown) and the Windows steering (never Start-Process
-RedirectStandard*; use creationflags — this is the Popen analogue).

Usage:
    python tools/serve-bg.py [--workspace PATH] [--lan] [--port N]   # start
    python tools/serve-bg.py --force [...]                           # stop existing, start fresh
    python tools/serve-bg.py --stop                                  # stop by PID file
    python tools/serve-bg.py --status                                # is it up?

SINGLE INSTANCE: only one background server runs at a time. A start is refused if one
is already tracked (any port) — use --stop, or --force to replace it — and refused if
the target port is held by another (untracked) process, so it never clobbers a
foreground `serve`/`serve:dev`.

`--lan` binds 0.0.0.0 so the server is reachable on the LAN at the machine's
192.168.x.x address (printed on start). Exit 0 = server ready; 1 = failed to bind.
"""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PID_FILE = PROJECT_ROOT / ".scratch" / "serve-bg.pid"
LOG_FILE = PROJECT_ROOT / ".scratch" / "serve-bg.log"
DEFAULT_PORT = 8787


def _lan_ip() -> str:
    """Primary LAN IPv4 via the UDP-connect trick (no packets sent). Loopback on failure."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def _read_pid() -> int | None:
    try:
        return int(PID_FILE.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _pid_alive(pid: int) -> bool:
    if sys.platform == "win32":
        out = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True, text=True,
        ).stdout
        return str(pid) in out
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _port_owner_pid(port: int) -> int | None:
    """PID of the process LISTENING on `port`, or None. Cross-platform."""
    if sys.platform == "win32":
        out = subprocess.run(
            ["netstat", "-ano", "-p", "TCP"], capture_output=True, text=True
        ).stdout
        for line in out.splitlines():
            parts = line.split()
            # proto  local  remote  STATE  pid
            if len(parts) >= 5 and parts[3] == "LISTENING" and parts[1].endswith(f":{port}"):
                try:
                    return int(parts[4])
                except ValueError:
                    continue
        return None
    # Unix: lsof if present, else ss
    for cmd in (["lsof", "-ti", f"TCP:{port}", "-sTCP:LISTEN"],
                ["ss", "-ltnp", f"sport = :{port}"]):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
        except FileNotFoundError:
            continue
        if not out:
            continue
        if cmd[0] == "lsof":
            try:
                return int(out.splitlines()[0])
            except (ValueError, IndexError):
                pass
        else:  # ss: parse pid=NNN
            import re
            m = re.search(r"pid=(\d+)", out)
            if m:
                return int(m.group(1))
    return None


def _is_our_server_running() -> int | None:
    """PID of the background server WE started (from the PID file), if still alive."""
    pid = _read_pid()
    return pid if (pid and _pid_alive(pid)) else None


def _wait_ready(url: str, timeout: float = 15.0, interval: float = 0.25) -> bool:
    """Poll url until it answers HTTP. A 4xx/5xx counts as 'up' (server bound).

    Distinguishes 'connection refused / not up yet' (retry) from an actual HTTP
    response (ready). Bounded by a wall-clock deadline so a dead server fails fast.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(url, timeout=2.0)
            return True
        except urllib.error.HTTPError:
            return True  # server answered (e.g. 404 at /) — it's up
        except (urllib.error.URLError, ConnectionError, OSError):
            time.sleep(interval)
    return False


def _spawn(args: list[str]) -> subprocess.Popen:
    """Spawn serve.py detached, child stdout+stderr merged into the log file."""
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    log = open(LOG_FILE, "ab")
    popen_kwargs: dict = {
        "cwd": str(PROJECT_ROOT),
        "stdout": log,
        "stderr": subprocess.STDOUT,
        "stdin": subprocess.DEVNULL,
    }
    if sys.platform == "win32":
        # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP — survives the launching shell,
        # no inherited console (the Popen analogue of Start-Process fire-and-forget).
        popen_kwargs["creationflags"] = 0x00000008 | 0x00000200
        popen_kwargs["close_fds"] = True
    else:
        popen_kwargs["preexec_fn"] = os.setsid  # own process group for clean killpg
    return subprocess.Popen(
        [sys.executable, "tools/serve.py", *args], **popen_kwargs
    )


def _stop() -> int:
    pid = _read_pid()
    if pid is None:
        print("No PID file — nothing to stop (server may not be running).")
        return 0
    if not _pid_alive(pid):
        print(f"PID {pid} not running (stale PID file) — clearing.")
        PID_FILE.unlink(missing_ok=True)
        return 0
    if sys.platform == "win32":
        # /T kills the tree (uvicorn reload workers, if any); /F forces.
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                       capture_output=True, text=True)
    else:
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    PID_FILE.unlink(missing_ok=True)
    print(f"Stopped server (PID {pid}).")
    return 0


def _port_from_args(passthrough: list[str]) -> int:
    if "--port" in passthrough:
        i = passthrough.index("--port")
        if i + 1 < len(passthrough):
            try:
                return int(passthrough[i + 1])
            except ValueError:
                pass
    return DEFAULT_PORT


def main() -> int:
    argv = sys.argv[1:]

    if "--stop" in argv:
        return _stop()

    port = _port_from_args(argv)
    probe_url = f"http://127.0.0.1:{port}/"

    if "--status" in argv:
        pid = _read_pid()
        up = _wait_ready(probe_url, timeout=1.0)
        print(f"PID file: {pid or 'none'}; server on :{port} {'UP' if up else 'DOWN'}")
        return 0 if up else 1

    # --- Single-instance enforcement -------------------------------------
    # Only ONE background server at a time. If WE already have one running (from
    # the PID file, on ANY port), refuse — unless --force, which stops it first.
    force = "--force" in argv
    ours = _is_our_server_running()
    if ours is not None:
        if force:
            print(f"--force: stopping existing server (PID {ours}) before restart.")
            _stop()
        else:
            print(f"Server already running (PID {ours}). Only one at a time — "
                  f"use `--stop` (or `--force` to replace it).")
            return 0

    # Guard the target port against a DIFFERENT process (a foreground `serve`,
    # `serve:dev`, or a stray listener). Never clobber something we don't own.
    owner = _port_owner_pid(port)
    if owner is not None:
        print(f"✗ Port {port} is already in use by PID {owner} (not our tracked server).",
              file=sys.stderr)
        print(f"  Stop that process, or start on a different --port.", file=sys.stderr)
        return 1

    is_lan = "--lan" in argv
    proc = _spawn([a for a in argv if a != "--force"])
    PID_FILE.write_text(str(proc.pid), encoding="utf-8")

    if not _wait_ready(probe_url):
        print(f"✗ Server did not become ready on :{port} within timeout.", file=sys.stderr)
        print(f"  Check {LOG_FILE} for the cause.", file=sys.stderr)
        return 1

    local_url = f"http://127.0.0.1:{port}"
    print(f"✓ Server ready (PID {proc.pid}) — logs: {LOG_FILE.relative_to(PROJECT_ROOT)}")
    print(f"  Local: {local_url}")
    if is_lan:
        print(f"  LAN:   http://{_lan_ip()}:{port}   (reachable from other devices)")
        print("  note: first LAN launch may need a Windows Firewall inbound allow for this port.")
    print(f"  Stop:  python tools/serve-bg.py --stop")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
