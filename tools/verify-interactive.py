#!/usr/bin/env python3
"""verify-interactive.py — Fast Playwright smoke tests for interactive components.

Runs as part of `mise run verify`. Tests one representative lesson page for:
- Tooltip hover (glossary.js loaded + functional)
- Action bar renders (LessonActions.js mounted)
- Typography panel (TypographyPanel.js mounted + responsive)
- SVG diagrams visible (non-zero dimensions)
- No JS errors on page load

Designed to complete in < 10s. Auto-starts a server if needed.

Exit codes:
  0 = all checks pass
  1 = one or more checks failed
  2 = crash / setup error
"""

import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("⚠ playwright not installed — skipping interactive checks", file=sys.stderr)
    sys.exit(0)  # Don't block verify if playwright isn't available


def find_test_page(base_url: str) -> str:
    """Find a lesson page to test against."""
    # Try workspace paths first (workspace server at :8787)
    workspace_candidates = [
        "/lessons/0001-esoteric-ebb-breakdown.html",
        "/lessons/0002-blender-npr-shaders.html",
    ]
    # Then example paths (project-root server)
    example_candidates = [
        "/examples/iceberg-workspace/lessons/0001-iceberg-metadata-tree.html",
        "/examples/oidc-rust/lessons/0001-oidc-auth-flows.html",
    ]

    for path in workspace_candidates + example_candidates:
        try:
            urllib.request.urlopen(base_url + path, timeout=1)
            return base_url + path
        except urllib.error.HTTPError:
            continue
        except Exception:
            continue

    # Fallback: first workspace candidate regardless
    return base_url + workspace_candidates[0]


def run_checks(page, url: str) -> list[dict]:
    """Run all interactive checks, return list of {name, pass, detail}."""
    checks = []
    console_errors = []

    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    page.goto(url, wait_until="networkidle")

    # 1. SVG diagrams visible
    svgs = page.query_selector_all('svg[role="img"]')
    svg_visible = all(
        svg.bounding_box() and svg.bounding_box()["width"] > 0
        for svg in svgs
    ) if svgs else True
    checks.append({
        "name": "svg_diagrams_visible",
        "pass": svg_visible and len(svgs) > 0,
        "detail": f"{len(svgs)} SVGs, all with non-zero dimensions" if svg_visible else "SVG has zero dimensions"
    })

    # 2. Tooltip hover
    term = page.query_selector('.term')
    tooltip_works = False
    if term:
        term.hover()
        page.wait_for_timeout(300)
        tooltip = page.query_selector('.glossary-tooltip')
        tooltip_works = tooltip is not None
        # Move away
        page.mouse.move(0, 0)
        page.wait_for_timeout(100)
    checks.append({
        "name": "tooltip_hover",
        "pass": tooltip_works,
        "detail": "Tooltip appears on .term hover" if tooltip_works else "No tooltip on hover (glossary.js missing?)"
    })

    # 3. Action bar renders
    action_bar = page.query_selector('.lesson-actions-bar')
    has_buttons = False
    if action_bar:
        buttons = action_bar.query_selector_all('button, a')
        has_buttons = len(buttons) > 0
    checks.append({
        "name": "action_bar_renders",
        "pass": has_buttons,
        "detail": f"Action bar with {len(buttons) if action_bar else 0} buttons" if has_buttons else "No action bar or empty"
    })

    # 4. Typography panel
    typo_trigger = page.query_selector('.typo-trigger')
    typo_works = False
    if typo_trigger:
        typo_trigger.click()
        page.wait_for_timeout(200)
        panel = page.query_selector('.typo-panel')
        typo_works = panel is not None
        # Close it
        page.keyboard.press('Escape')
        page.wait_for_timeout(100)
    checks.append({
        "name": "typography_panel",
        "pass": typo_works,
        "detail": "Aa button opens panel" if typo_works else "Typography panel not found"
    })

    # 5. No JS errors (ignore favicon 404 and quiz 404)
    real_errors = [e for e in console_errors if "favicon" not in e.lower() and "quiz" not in e.lower()]
    checks.append({
        "name": "no_js_errors",
        "pass": len(real_errors) == 0,
        "detail": f"Clean console" if not real_errors else f"JS errors: {real_errors[:3]}"
    })

    return checks


def main():
    port = 9123  # Non-standard port to avoid conflicts with serve/serve:lan
    base_url = f"http://localhost:{port}"
    server_proc = None

    # Check if any server is already running (try common ports)
    for try_url in [f"http://localhost:{port}", "http://localhost:8787", "http://localhost:8080"]:
        try:
            resp = urllib.request.urlopen(try_url, timeout=1)
            base_url = try_url
            break
        except urllib.error.HTTPError:
            # Server is running but returned an error (e.g., 404) — still usable
            base_url = try_url
            break
        except Exception:
            continue
    else:
        # Start server on our port
        server_proc = subprocess.Popen(
            [sys.executable, "tools/serve.py", "--port", str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid,
        )
        # Wait for server
        for _ in range(30):
            try:
                urllib.request.urlopen(base_url, timeout=0.5)
                break
            except Exception:
                time.sleep(0.2)
        else:
            print("ERROR: Could not start server", file=sys.stderr)
            if server_proc:
                os.killpg(os.getpgid(server_proc.pid), signal.SIGTERM)
            sys.exit(2)

    try:
        url = find_test_page(base_url)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(color_scheme="dark")
            page = context.new_page()

            checks = run_checks(page, url)

            browser.close()

        # Report
        all_pass = all(c["pass"] for c in checks)
        for c in checks:
            icon = "✓" if c["pass"] else "✗"
            print(f"  {icon} {c['name']}: {c['detail']}")

        if all_pass:
            print(f"\n✓ Interactive checks pass ({len(checks)} checks)")
        else:
            failed = [c for c in checks if not c["pass"]]
            print(f"\n✗ {len(failed)} interactive check(s) FAILED")
            sys.exit(1)

    finally:
        if server_proc:
            os.killpg(os.getpgid(server_proc.pid), signal.SIGTERM)
            server_proc.wait()


if __name__ == "__main__":
    main()
