#!/usr/bin/env python3
"""Malformed-MAP blast-radius contract for serve.py (#373).

`_map_for_domain` parses EVERY map in the context per request. Before #373, one
malformed MAP.md raised inside that loop and 500'd `/api/map/{domain}` (reads AND
progress writes) for every domain, healthy ones included. This exercises the real
server against a tmp workspace holding one good map + one broken map and asserts:

1. The healthy domain's GET returns 200 with data.
2. The broken map's own domain returns a 422 naming the broken file (not a 500).
3. Progress writes for a healthy persisted-ULID topic succeed and round-trip.
4. A progress write for an ephemeral-id topic is rejected loudly with the
   migrate_map_ids remediation (never a silently-nonpersisting write).

Also unit-checks the `Topic.ephemeral_id` flag the write guard depends on.

Self-serves on an ephemeral port (like test-library-status-api.py). NOT in core
`verify` — a server-spawning check, exposed as `mise run test:map-isolation`.
Exit 0 = all assertions pass.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
PROJECT_ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from lib import ulid  # noqa: E402

GOOD_DOMAIN = "good-domain"
_ALPHA_ID = None  # filled per-run with a fresh valid ULID


def _good_map() -> str:
    return f"""---
domain: {GOOD_DOMAIN}
description: "Healthy fixture domain"
generated: 2026-09-18
depth: 0
parent: null
leads_to: []
---

# Good Domain

## Topics

### alpha

- **title:** Alpha
- **why:** Persisted-ULID topic that must accept progress writes
- **scope:** lightweight
- **id:** {_ALPHA_ID}
- **prereqs:** []

### beta

- **title:** Beta
- **why:** No id line — parse mints an ephemeral ULID every run
- **scope:** lightweight
- **prereqs:** []
"""


BROKEN_MAP = "this file has no frontmatter at all\n"


def _request(method: str, url: str, body: dict | None = None) -> tuple[int, dict | str]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            payload = response.read().decode("utf-8")
            return response.status, payload
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8")


def _detail(payload: str) -> str:
    try:
        return json.loads(payload).get("detail", "")
    except json.JSONDecodeError:
        return payload


def _check(label: str, condition: bool, evidence: str) -> bool:
    mark = "✓" if condition else "✗"
    print(f"  {mark} {label}")
    if not condition:
        print(f"      evidence: {evidence[:400]}")
    return condition


def _unit_checks() -> bool:
    print("map_parser unit checks (ephemeral_id flag):")
    from map_parser import load_map

    with tempfile.TemporaryDirectory() as tmp:
        maps = Path(tmp) / "maps"
        maps.mkdir()
        (maps / "good.MAP.md").write_text(_good_map(), encoding="utf-8")
        dm = load_map(maps / "good.MAP.md")
        alpha = dm.topic_by_slug("alpha")
        beta = dm.topic_by_slug("beta")
        ok = True
        ok &= _check("persisted-ULID topic: ephemeral_id is False", alpha is not None and alpha.ephemeral_id is False, str(alpha))
        ok &= _check("missing-id topic: ephemeral_id is True", beta is not None and beta.ephemeral_id is True, str(beta))
        (maps / "broken.MAP.md").write_text(BROKEN_MAP, encoding="utf-8")
        try:
            load_map(maps / "broken.MAP.md")
            ok &= _check("malformed map raises ValueError", False, "no exception raised")
        except ValueError:
            ok &= _check("malformed map raises ValueError", True, "")
    return ok


def _server_checks() -> bool:
    print("serve.py routing isolation (real server, one good + one broken MAP):")
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp)
        maps = ws / "maps"
        maps.mkdir()
        (maps / "good.MAP.md").write_text(_good_map(), encoding="utf-8")
        (maps / "broken.MAP.md").write_text(BROKEN_MAP, encoding="utf-8")

        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]

        server = subprocess.Popen(
            [sys.executable, str(TOOLS / "serve.py"), "--workspace", str(ws), "--port", str(port)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(PROJECT_ROOT),
        )
        try:
            base = f"http://127.0.0.1:{port}"
            deadline = time.monotonic() + 15
            ready = False
            while time.monotonic() < deadline:
                try:
                    with urllib.request.urlopen(f"{base}/api/maps", timeout=2):
                        ready = True
                        break
                except (urllib.error.URLError, OSError):
                    time.sleep(0.2)
            if not _check("server became ready", ready, "never answered /api/maps within 15s"):
                return False

            ok = True

            status, payload = _request("GET", f"{base}/api/map/{GOOD_DOMAIN}")
            ok &= _check(f"healthy domain GET → 200 (got {status})", status == 200 and GOOD_DOMAIN in payload, payload[:200])

            status, payload = _request("GET", f"{base}/api/map/broken")
            detail = _detail(payload)
            ok &= _check(f"broken domain GET → 422 naming the file (got {status})",
                         status == 422 and "broken.MAP.md" in detail, detail)

            status, payload = _request("POST", f"{base}/api/map/{GOOD_DOMAIN}/alpha/status",
                                       {"status": "complete"})
            ok &= _check(f"persisted-ULID write → 200 (got {status})", status == 200, payload[:200])

            status, payload = _request("GET", f"{base}/api/map/{GOOD_DOMAIN}/alpha/status")
            ok &= _check("written status round-trips", '"complete"' in payload, payload[:200])

            status, payload = _request("POST", f"{base}/api/map/{GOOD_DOMAIN}/beta/status",
                                       {"status": "in-progress"})
            detail = _detail(payload)
            ok &= _check(f"ephemeral-id write → 400 with migrate hint (got {status})",
                         status == 400 and "migrate_map_ids" in detail, detail)

            return ok
        finally:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()


def main() -> int:
    global _ALPHA_ID
    _ALPHA_ID = ulid.new()
    ok = _unit_checks()
    ok &= _server_checks()
    print("\nresult:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
