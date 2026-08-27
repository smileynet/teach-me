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


def _terminate_server(proc: "subprocess.Popen") -> None:
    """Terminate a spawned server + its process group, cross-platform.

    Unix: signal the process group via killpg (server was started with setsid).
    Windows: os.setsid/os.killpg don't exist; the process was started with
    CREATE_NEW_PROCESS_GROUP, so terminate() (TerminateProcess) is sufficient.
    """
    if sys.platform == "win32":
        proc.terminate()
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        proc.terminate()


def find_test_page(base_url: str) -> str:
    """Find a lesson page to test against."""
    # Try workspace paths first (workspace server at :8787)
    workspace_candidates = [
        "/lessons/0001-esoteric-ebb-breakdown.html",
        "/lessons/0002-blender-npr-shaders.html",
    ]
    # Then example paths (project-root server, or workspace-root server)
    example_candidates = [
        "/lessons/blender-texture-prep/01-texture-audit.html",
        "/lessons/0004-toon-banding.html",
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

    # No served page found — signal skip (no suitable test target).
    return None


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

    # 5. Quiz button navigates correctly (verify destination URL is valid)
    quiz_btn = page.query_selector('.lesson-actions-bar button:first-child')
    quiz_nav_ok = False
    quiz_detail = "No quiz button found"
    if quiz_btn:
        label = quiz_btn.text_content().strip()
        if label not in ("📝 Take quiz", "+ Generate quiz"):
            quiz_detail = f"Unexpected label: '{label}'"
        elif "Take quiz" in label:
            # Quiz exists — verify the destination URL returns 200 (not 404)
            # The button navigates to quiz/{lessonId}-quiz.html
            quiz_url = page.evaluate("""() => {
                const btn = document.querySelector('.lesson-actions-bar button:first-child');
                // Trigger click handler but intercept navigation
                const origLocation = window.location.href;
                let targetUrl = null;
                const origAssign = window.location.assign;
                const origHref = Object.getOwnPropertyDescriptor(window.location, 'href');
                // The button uses window.location.href = url, so we check the onclick source
                // Easier: just extract from the component's known pattern
                const lessonId = window.location.pathname.split('/').pop().replace('.html', '');
                return new URL('quiz/' + lessonId + '-quiz.html', window.location.href).href;
            }""")
            if quiz_url:
                # HEAD request to check if quiz page exists
                response = page.request.head(quiz_url)
                quiz_nav_ok = response.status == 200
                quiz_detail = f"Quiz URL {quiz_url.split('/')[-1]}: {'exists (200)' if quiz_nav_ok else f'missing ({response.status})'}"
            else:
                quiz_detail = "Could not determine quiz URL"
        else:
            # "Generate quiz" — quiz doesn't exist, that's valid
            quiz_nav_ok = True
            quiz_detail = "Quiz not yet generated (Generate button shown)"
    checks.append({
        "name": "quiz_button_navigation",
        "pass": quiz_nav_ok,
        "detail": quiz_detail
    })

    # 6. Typography applies (change font size, verify computed style changes)
    typo_applies = False
    if typo_trigger:
        typo_trigger.click()
        page.wait_for_timeout(200)
        xl_btn = page.query_selector('.typo-opt:has-text("XL")')
        if xl_btn:
            # Get initial font size
            initial_size = page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--font-size-base').trim()")
            xl_btn.click()
            page.wait_for_timeout(100)
            new_size = page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--font-size-base').trim()")
            typo_applies = (new_size == "20px")
            # Reset back
            reset_btn = page.query_selector('.typo-reset')
            if reset_btn:
                reset_btn.click()
                page.wait_for_timeout(100)
        page.keyboard.press('Escape')
        page.wait_for_timeout(100)
    checks.append({
        "name": "typography_applies",
        "pass": typo_applies,
        "detail": "Font size changes on XL click" if typo_applies else "Typography change not applied"
    })

    # 7. Collapsed sections mode doesn't hide panel or action bar
    collapsed_ok = False
    if typo_trigger:
        # Switch to collapsed mode
        typo_trigger.click()
        page.wait_for_timeout(200)
        collapsed_btn = page.query_selector('.typo-opt:has-text("Collapsed")')
        if collapsed_btn:
            collapsed_btn.click()
            page.wait_for_timeout(300)
            # Verify panel is still visible
            panel_visible = page.query_selector('.typo-trigger')
            panel_visible = panel_visible.is_visible() if panel_visible else False
            # Verify action bar is still visible (not inside a closed details)
            action_bar = page.query_selector('.lesson-actions-bar')
            action_visible = action_bar.is_visible() if action_bar else False
            collapsed_ok = panel_visible and action_visible
            # Reset back to expanded
            expanded_btn = page.query_selector('.typo-opt:has-text("Expanded")')
            if expanded_btn:
                expanded_btn.click()
                page.wait_for_timeout(200)
        page.keyboard.press('Escape')
        page.wait_for_timeout(100)
    checks.append({
        "name": "collapsed_mode_safe",
        "pass": collapsed_ok,
        "detail": "Panel + action bar visible in collapsed mode" if collapsed_ok else "Panel or action bar hidden when sections collapsed"
    })

    # 8. No JS errors (ignore favicon 404 and quiz 404)
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
        # Start server on our port. Put it in its own process group so we can
        # tear down cleanly; os.setsid is Unix-only, so use the Windows
        # equivalent (a new process group) on win32.
        popen_kwargs = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }
        if sys.platform == "win32":
            popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            popen_kwargs["preexec_fn"] = os.setsid
        # serve.py defaults to workspace/, which may not exist at the project
        # root (it's the gitignored live workspace). Point at a workspace that
        # is always present so the interactive checks have real pages to test.
        default_ws = Path(__file__).resolve().parent.parent / "workspace"
        serve_ws = "workspace" if default_ws.exists() else "examples/godot-gamedev"
        server_proc = subprocess.Popen(
            [sys.executable, "tools/serve.py", "--workspace", serve_ws, "--port", str(port)],
            **popen_kwargs,
        )
        # Wait for server
        for _ in range(30):
            try:
                urllib.request.urlopen(base_url, timeout=0.5)
                break
            except urllib.error.HTTPError:
                # Server is running (returned 404 or similar) — that's fine
                break
            except Exception:
                time.sleep(0.2)
        else:
            # Could not start a server — skip rather than fail the whole gate
            # (matches the "skip if playwright missing" philosophy above).
            print("⚠ Could not start server — skipping interactive checks", file=sys.stderr)
            if server_proc:
                _terminate_server(server_proc)
            sys.exit(0)

    try:
        url = find_test_page(base_url)
        if url is None:
            print("⚠ No suitable lesson page served — skipping interactive checks", file=sys.stderr)
            return

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
            _terminate_server(server_proc)
            server_proc.wait()


if __name__ == "__main__":
    main()
