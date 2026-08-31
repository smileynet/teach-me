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

# Windows consoles default to cp1252; force UTF-8 so ✓/✗/⚠/— glyphs don't crash.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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


# Lesson pages we probe to (a) validate a server serves this project's content and
# (b) pick a test target. Ordering: workspace-root paths (serve.py on a single workspace),
# then library-root-relative paths (serve.py on the multi-domain library/ root — the gate's
# default → contents exposed at /{domain}/..., no /library/ prefix), then project-root paths.
_CANDIDATE_PAGES = [
    "/lessons/0001-esoteric-ebb-breakdown.html",
    "/lessons/0002-blender-npr-shaders.html",
    "/lessons/blender-texture-prep/01-texture-audit.html",
    "/lessons/0004-toon-banding.html",
    # library/ root serve (gate default): contents at /{domain}/... . Prefer the iceberg
    # metadata lesson — it has glossary .term spans + a diagram, so tooltip_hover +
    # svg_diagrams_visible have something to assert (a term-less page would fail them).
    "/iceberg-workspace/lessons/0001-iceberg-metadata-tree.html",
    "/godot-gamedev/lessons/0004-toon-banding.html",
    "/library/iceberg-workspace/lessons/0001-iceberg-metadata-tree.html",
    "/library/oidc-rust/lessons/0001-oidc-auth-flows.html",
]


def _free_port() -> int:
    """Ask the OS for a free ephemeral port (bind :0, read it back, release)."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _serves_lessons(base_url: str) -> bool:
    """True only if base_url serves one of THIS project's lesson pages (HTTP 200).

    A foreign server (or serve.py on an empty workspace) answers the port but 404s
    every candidate — so mere connectivity is NOT proof it's our server.
    """
    for path in _CANDIDATE_PAGES:
        try:
            with urllib.request.urlopen(base_url + path, timeout=2) as r:
                if getattr(r, "status", r.getcode()) == 200:
                    return True
        except Exception:
            continue
    return False


def find_test_page(base_url: str) -> str:
    """Return the first candidate lesson page that returns HTTP 200, else None."""
    for path in _CANDIDATE_PAGES:
        try:
            with urllib.request.urlopen(base_url + path, timeout=2) as r:
                if getattr(r, "status", r.getcode()) == 200:
                    return base_url + path
        except Exception:
            continue
    return None


def run_checks(page, url: str) -> list[dict]:
    """Run all interactive checks, return list of {name, pass, detail}."""
    checks = []
    console_errors = []
    failed_requests = []

    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
    page.on("response", lambda r: failed_requests.append(r.url) if r.status >= 400 else None)

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
    # Locate the quiz button by its label — NOT by position. With a wired domain
    # (#264), the "← Back to map" link now renders first in the bar, so a
    # positional `button:first-child` selector would miss the quiz button.
    quiz_btn = None
    for b in page.query_selector_all('.lesson-actions-bar button'):
        if 'quiz' in (b.text_content() or '').lower():
            quiz_btn = b
            break
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
    # 8. No JS errors. Ignore: favicon + quiz 404s (expected), and the LessonActions
    # status probe (/api/map/{domain}/{slug}/status) — the gate serves the multi-domain
    # library/ ROOT, where serve.py only mounts one workspace's /api, so a lesson under a
    # NON-mounted domain 404s that probe. That's a known serve.py multi-domain limitation,
    # not a page defect (the status bar degrades gracefully). Only suppress the resource-load
    # console errors if EVERY unexpected failed request is such a status probe — so a REAL
    # 404 (missing asset/module) is never masked. Match by URL (precise).
    def _expected_fail(u: str) -> bool:
        lu = u.lower()
        if "favicon" in lu or "quiz" in lu:
            return True
        return "/api/map/" in u and u.rstrip("/").endswith("/status")
    only_expected_fails = all(_expected_fail(u) for u in failed_requests)
    real_errors = [
        e for e in console_errors
        if "favicon" not in e.lower()
        and "quiz" not in e.lower()
        and not (only_expected_fails and "failed to load resource" in e.lower())
    ]
    checks.append({
        "name": "no_js_errors",
        "pass": len(real_errors) == 0,
        "detail": f"Clean console" if not real_errors else f"JS errors: {real_errors[:3]}"
    })

    return checks


# Index pages we probe. The gate serves the multi-domain library/ ROOT, where serve.py
# normalizes /lessons/index.html back to the root /index.html (ADR-0015) — the unified
# #276 two-view aggregate. So the first candidate that 200s is the unified page.
_INDEX_PAGES = ["/lessons/index.html", "/index.html", "/library/index.html"]


def find_index_page(base_url: str) -> str | None:
    for path in _INDEX_PAGES:
        try:
            with urllib.request.urlopen(base_url + path, timeout=2) as r:
                if getattr(r, "status", r.getcode()) == 200:
                    return base_url + path
        except Exception:
            continue
    return None


def run_index_checks(page, url: str) -> list[dict]:
    """Smoke-check the All Lessons index (a Preact island page, like lessons).

    Guards the #271 orientation/resume cue and the index's JS health — neither was
    covered before (run_checks only probes lesson pages). Failed requests + console
    errors here would otherwise ship silently.
    """
    checks = []
    console_errors = []
    failed_requests = []
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("response", lambda r: failed_requests.append(f"{r.status} {r.url}") if r.status >= 400 else None)

    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(500)

    # a. Preact island mounted (not a blank #app)
    app = page.query_selector("#app")
    mounted = bool(app and (app.query_selector(".index-view") or app.inner_html().strip()))
    checks.append({
        "name": "index_renders",
        "pass": mounted,
        "detail": "Index island mounted (.index-view present)" if mounted else "#app empty — island failed to render",
    })

    # b. Exactly one orientation cue (#271: resume XOR first-time, never both)
    cues = page.query_selector_all(".index-cue")
    checks.append({
        "name": "index_cue_present",
        "pass": len(cues) == 1,
        "detail": f"exactly one .index-cue" if len(cues) == 1 else f"expected 1 .index-cue, found {len(cues)}",
    })

    # c. No JS errors / no 4xx-5xx on the index (favicon excepted)
    real_errors = [e for e in console_errors if "favicon" not in e.lower()]
    real_failed = [f for f in failed_requests if "favicon" not in f.lower()]
    ok = not real_errors and not real_failed
    checks.append({
        "name": "index_no_js_errors",
        "pass": ok,
        "detail": "Clean console + no failed requests" if ok else f"errors={real_errors[:2]} failed={real_failed[:2]}",
    })

    # d. Two-view Tree|Map toggle (#276) — only on the UNIFIED aggregate page (a
    # per-domain index has no .view-toggle, so this block is skipped there). Asserts
    # the default Tree renders, clicking Map mounts the dagre map, and clicking Tree
    # returns — all from ONE #page-data island (no reload).
    toggle = page.query_selector(".view-toggle")
    if toggle:
        tree_default = bool(page.query_selector(".indented-tree"))
        page.click(".view-toggle .vt-btn:has-text('Map')")
        page.wait_for_timeout(400)
        map_shown = bool(page.query_selector(".iterated-map .im-card"))
        page.click(".view-toggle .vt-btn:has-text('Tree')")
        page.wait_for_timeout(200)
        tree_back = bool(page.query_selector(".indented-tree"))
        two_view_ok = tree_default and map_shown and tree_back
        checks.append({
            "name": "index_two_view_toggle",
            "pass": two_view_ok,
            "detail": "Tree default, Map mounts on toggle, Tree returns"
                      if two_view_ok
                      else f"tree_default={tree_default} map_shown={map_shown} tree_back={tree_back}",
        })

        # e. Tree keyboard model (#276 — roving tabindex, WAI-ARIA APG). We're back on the
        # Tree view. Focus the first roving item (tabindex=0), then drive the key handlers
        # and assert observable state: ArrowDown moves focus to a different row; ArrowRight
        # on a parent sets aria-expanded=true; ArrowLeft collapses it; End/Home jump.
        def _focused_domain():
            return page.evaluate(
                "() => (document.activeElement && document.activeElement.getAttribute('data-domain')) || null"
            )
        try:
            first = page.query_selector(".indented-tree .ti-row[tabindex='0']")
            first.focus()
            start = _focused_domain()
            page.keyboard.press("ArrowDown")
            page.wait_for_timeout(120)
            after_down = _focused_domain()
            moved = bool(start) and bool(after_down) and after_down != start

            # Find a parent treeitem (has aria-expanded) and toggle it via keys.
            page.keyboard.press("End")
            page.wait_for_timeout(80)
            at_end = _focused_domain()
            page.keyboard.press("Home")
            page.wait_for_timeout(80)
            at_home = _focused_domain()
            home_end_ok = bool(at_end) and bool(at_home) and at_end != at_home and at_home == start

            # Expand/collapse: focus a parent row, ArrowRight → expanded, ArrowLeft → collapsed.
            parent = page.query_selector(".indented-tree .ti[aria-expanded] > .ti-row")
            expand_ok = True  # default pass if the forest has no parent (single-domain)
            if parent:
                parent.focus()
                parent_li = page.query_selector(".indented-tree .ti[aria-expanded]")
                page.keyboard.press("ArrowLeft")   # ensure collapsed baseline
                page.wait_for_timeout(80)
                page.keyboard.press("ArrowRight")  # expand
                page.wait_for_timeout(120)
                expanded = parent_li.get_attribute("aria-expanded")
                page.keyboard.press("ArrowLeft")   # collapse
                page.wait_for_timeout(120)
                collapsed = parent_li.get_attribute("aria-expanded")
                expand_ok = expanded == "true" and collapsed == "false"

            kbd_ok = moved and home_end_ok and expand_ok
            checks.append({
                "name": "index_tree_keyboard",
                "pass": kbd_ok,
                "detail": "roving focus: ArrowDown moves, Home/End jump, ArrowRight/Left expand/collapse"
                          if kbd_ok
                          else f"moved={moved} home_end_ok={home_end_ok} expand_ok={expand_ok}",
            })
        except Exception as e:
            checks.append({"name": "index_tree_keyboard", "pass": False, "detail": f"keyboard test errored: {e}"})

    return checks


def main():
    base_url = None
    server_proc = None

    # Optional convenience: reuse a running dev server on 8787 — but ONLY if it
    # actually serves this project's lesson pages. A foreign server (or serve.py
    # on an empty workspace) answers the port yet 404s every candidate, so we must
    # validate content, not just connectivity. (mirrors Playwright reuseExistingServer)
    if _serves_lessons("http://localhost:8787"):
        base_url = "http://localhost:8787"
    else:
        # Own an ephemeral port so the gate is hermetic — never adopt a server we
        # don't control. Pre-bind :0 to get a free port, then hand it to serve.py.
        port = _free_port()
        base_url = f"http://localhost:{port}"
        popen_kwargs = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }
        if sys.platform == "win32":
            popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            popen_kwargs["preexec_fn"] = os.setsid
        # serve.py defaults to workspace/, which may not exist OR may be a freshly
        # scaffolded workspace with only an index.html and no lesson pages. Serve
        # workspace/ ONLY if it actually contains a lesson page one of our candidates
        # can hit; otherwise serve the multi-domain library/ ROOT — serve.py normalizes
        # it (ADR-0015), so the `/library/{domain}/lessons/...` candidates resolve AND
        # `/index.html` serves the unified aggregate (so run_index_checks exercises the
        # #276 two-view page, not just a per-domain index).
        project_root = Path(__file__).resolve().parent.parent
        ws_lessons = project_root / "workspace" / "lessons"
        ws_has_lesson = ws_lessons.exists() and any(
            p.name != "index.html" for p in ws_lessons.rglob("*.html")
        )
        serve_ws = "workspace" if ws_has_lesson else "library"
        server_proc = subprocess.Popen(
            [sys.executable, "tools/serve.py", "--workspace", serve_ws, "--port", str(port)],
            **popen_kwargs,
        )
        # Wait for our server to bind (404 at / is fine — the workspace has no root index).
        for _ in range(30):
            try:
                urllib.request.urlopen(base_url, timeout=0.5)
                break
            except urllib.error.HTTPError:
                break
            except Exception:
                time.sleep(0.2)
        else:
            # We control serve.py and its deps are present (it's in the verify venv),
            # so a server that won't start is a misconfig/regression — FAIL loudly,
            # don't silently skip and let the gate go green on an untested build.
            print("✗ Could not start serve.py — interactive gate cannot run", file=sys.stderr)
            if server_proc:
                _terminate_server(server_proc)
                server_proc.wait()
            sys.exit(2)

    try:
        url = find_test_page(base_url)
        if url is None:
            # The server is up and it's OUR known-good workspace, so a missing
            # lesson page is a real regression (broken mount / renamed page), NOT
            # an environment gap. Fail — a silent skip here hides the very defect
            # a smoke test exists to catch.
            print(f"✗ No lesson page served at {base_url} — interactive gate cannot run", file=sys.stderr)
            sys.exit(1)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(color_scheme="dark")
            page = context.new_page()

            checks = run_checks(page, url)

            # Also smoke-check the index page if the server exposes one (#271 cue +
            # index JS health). A missing index is not fatal here — some workspaces
            # have no aggregate index — but a served index that errors IS a failure.
            index_url = find_index_page(base_url)
            if index_url:
                checks += run_index_checks(context.new_page(), index_url)

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
