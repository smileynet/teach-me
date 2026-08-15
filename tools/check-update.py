#!/usr/bin/env python3
"""check-update.py — Check if a newer release of teach-me is available.

Compares the local version (from CHANGELOG.md or git tags) against the
latest GitHub release. Prints update instructions if newer version exists.

Usage:
    python tools/check-update.py
    mise run update:check
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPO = "smileynet/teach-me"
RELEASES_URL = f"https://api.github.com/repos/{REPO}/releases/latest"


def get_local_version() -> str | None:
    """Get local version from git tags or CHANGELOG.md."""
    # Try git tag first
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        if result.returncode == 0:
            return result.stdout.strip().lstrip("v")
    except FileNotFoundError:
        pass

    # Fallback: parse CHANGELOG.md
    changelog = PROJECT_ROOT / "CHANGELOG.md"
    if changelog.exists():
        match = re.search(r'## \[(\d+\.\d+\.\d+)\]', changelog.read_text())
        if match:
            return match.group(1)

    return None


def get_latest_release() -> tuple[str, str] | None:
    """Fetch latest release from GitHub. Returns (version, url) or None."""
    try:
        req = urllib.request.Request(RELEASES_URL, headers={"User-Agent": "teach-me-update-check"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            tag = data.get("tag_name", "").lstrip("v")
            url = data.get("html_url", f"https://github.com/{REPO}/releases")
            return tag, url
    except Exception:
        return None


def compare_versions(local: str, remote: str) -> int:
    """Compare semver strings. Returns -1 (local older), 0 (same), 1 (local newer)."""
    def parts(v):
        return [int(x) for x in v.split(".")[:3]]
    l, r = parts(local), parts(remote)
    if l < r:
        return -1
    elif l > r:
        return 1
    return 0


def main():
    local = get_local_version()
    if not local:
        print("Could not determine local version.")
        sys.exit(1)

    latest = get_latest_release()
    if not latest:
        print(f"Current version: {local}")
        print("Could not reach GitHub to check for updates (offline?).")
        sys.exit(0)

    remote_version, release_url = latest
    cmp = compare_versions(local, remote_version)

    if cmp == 0:
        print(f"✓ Up to date (v{local})")
    elif cmp < 0:
        print(f"Update available: v{local} → v{remote_version}")
        print(f"  {release_url}")
        print(f"\n  git pull origin main && mise run setup")
    else:
        print(f"✓ Ahead of latest release (local: v{local}, latest: v{remote_version})")

    sys.exit(0)


if __name__ == "__main__":
    main()
