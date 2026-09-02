#!/usr/bin/env python3
"""test-cue-matrix.py (#282) — state-matrix test for the index orientation/resume cue.

The #271 IndexCue has distinct states the REAL library can't all produce (all 5 domains are
in-progress, so only `resume` is exercisable — that's covered by test-navigation.py). This
suite builds THROWAWAY single-domain fixtures — one per state — and asserts each cue in
ISOLATION:

    empty        (0 topics complete)          → orientation cue   (.index-cue-start)
    partial      (1 topic in-progress)        → resume cue        (.index-cue-resume a → map)
    all-complete (every topic complete)       → done cue          (.index-cue-done)   [#282]

Isolation matters: IndexCue uses Array.find, so N domains in ONE page yield ONE cue driven by
the first matching domain — states would interfere. Each state is therefore its OWN
single-domain fixture dir (domainCount==1, no edges → the generator's IndexView path, whose
IndexCue is identical to UnifiedView's). State is authored via a committed-style
demo-status.json (read by demo_status_map_for_map, #279), NOT .user/status-overlay.json.

Fixtures are built under .scratch/cue-fixture/ (gitignored) and torn down after.
Run: python tools/test-cue-matrix.py   (self-serves each fixture via serve_harness)
"""
from __future__ import annotations

import sys
from pathlib import Path

# Windows cp1252 stdout chokes on ✓/✗/→ (#265).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import shutil
import subprocess

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tools/ on path for lib imports
from lib import ulid  # noqa: E402
from lib.serve_harness import serve_workspace  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_ROOT = PROJECT_ROOT / ".scratch" / "cue-fixture"

# Each state: (dir-name, domain slug, how many of 3 topics complete, how many in-progress).
STATES = [
    ("empty", "cue-empty", 0, 0),
    ("partial", "cue-partial", 0, 1),
    ("allcomplete", "cue-done", 3, 0),
]


def _write_fixture(state_dir: str, slug: str, n_complete: int, n_in_progress: int) -> Path:
    """Build a single-domain fixture: {FIXTURE_ROOT}/{state}/{slug}/maps/{slug}.MAP.md +
    a matching demo-status.json. Returns the scan dir ({FIXTURE_ROOT}/{state})."""
    scan = FIXTURE_ROOT / state_dir
    ws = scan / slug
    maps = ws / "maps"
    maps.mkdir(parents=True, exist_ok=True)

    # 3 topics with explicit valid ULIDs (load_map mints ephemeral ids if absent — those
    # wouldn't match demo-status.json and counts would silently stay 0).
    ids = [ulid.new() for _ in range(3)]
    topic_blocks = "\n".join(
        f"### topic-{i}\n- **id:** {tid}\n- **title:** Topic {i}\n"
        f"- **why:** why {i}\n- **scope:** substantial\n- **prereqs:** []\n"
        for i, tid in enumerate(ids)
    )
    map_md = (
        f"---\ndomain: {slug}\ndepth: 0\nparent: null\n"
        f"description: Cue fixture {slug}\n---\n\n"
        f"# {slug.replace('-', ' ').title()}\n\n"
        f"## Orientation\n\nSynthetic cue-matrix fixture.\n\n"
        f"## Topics\n\n{topic_blocks}\n"
    )
    (maps / f"{slug}.MAP.md").write_text(map_md, encoding="utf-8")

    # demo-status.json: mark the first n_complete complete, next n_in_progress in-progress.
    overlay = {}
    for tid in ids[:n_complete]:
        overlay[tid] = {"status": "complete", "updated_at": "2026-01-01T00:00:00Z"}
    for tid in ids[n_complete:n_complete + n_in_progress]:
        overlay[tid] = {"status": "in-progress", "updated_at": "2026-01-01T00:00:00Z"}
    (ws / "demo-status.json").write_text(
        json.dumps({"schema": 1, "overlay": overlay}, indent=2) + "\n", encoding="utf-8")

    # Generate the aggregate for this single-domain fixture (→ IndexView path).
    out = scan / "index.html"
    r = subprocess.run(
        [sys.executable, "tools/generate_index_page.py", "--scan-dir", str(scan), "--output", str(out)],
        cwd=str(PROJECT_ROOT), capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"generate failed for {slug}:\n{r.stderr}")
    return scan


def _assert_state(page, base_url: str, state: str, results: list):
    def rec(name, ok, detail=""):
        results.append((state, name, ok, detail))
        print(f"  {'✓' if ok else '✗'} [{state}] {name}" + (f" — {detail}" if detail and not ok else ""))

    page.goto(base_url + "/index.html", wait_until="domcontentloaded")
    page.wait_for_selector(".index-view", timeout=8000)
    page.wait_for_timeout(300)
    cues = page.query_selector_all(".index-cue")
    rec("exactly one cue", len(cues) == 1, f"{len(cues)} cues")

    has_resume = page.query_selector(".index-cue-resume") is not None
    has_start = page.query_selector(".index-cue-start") is not None
    has_done = page.query_selector(".index-cue-done") is not None

    if state == "empty":
        rec("empty → orientation cue", has_start and not has_resume and not has_done,
            f"resume={has_resume} start={has_start} done={has_done}")
    elif state == "partial":
        resume = page.query_selector(".index-cue-resume a")
        href = resume.get_attribute("href") if resume else None
        # Assert the resume cue navigates to a map.
        nav_ok = False
        if resume:
            resume.click()
            try:
                page.wait_for_url("**/*-map.html", timeout=8000)
                nav_ok = True
            except Exception:
                nav_ok = False
        rec("partial → resume cue + map destination",
            has_resume and not has_done and nav_ok, f"href={href} nav_ok={nav_ok}")
    elif state == "allcomplete":
        rec("all-complete → done cue (not orientation)",
            has_done and not has_resume and not has_start,
            f"resume={has_resume} start={has_start} done={has_done}")


def main() -> int:
    results: list[tuple[str, str, bool, str]] = []
    if FIXTURE_ROOT.exists():
        shutil.rmtree(FIXTURE_ROOT, ignore_errors=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for state_dir, slug, n_c, n_ip in STATES:
                scan = _write_fixture(state_dir, slug, n_c, n_ip)
                # Serve THIS fixture dir (single-domain → IndexView). Fresh context per state.
                ws_rel = str(scan.relative_to(PROJECT_ROOT)).replace("\\", "/")
                with serve_workspace(ws_rel) as base_url:
                    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
                    page = ctx.new_page()
                    try:
                        _assert_state(page, base_url, state_dir, results)
                    except Exception as e:
                        results.append((state_dir, "assert", False, f"errored: {e}"))
                    finally:
                        ctx.close()
            browser.close()
    finally:
        shutil.rmtree(FIXTURE_ROOT, ignore_errors=True)

    passed = sum(1 for _, _, ok, _ in results if ok)
    failed = sum(1 for _, _, ok, _ in results if not ok)
    print(f"\nResults: {passed} passed, {failed} failed")
    if failed:
        for st, name, ok, detail in results:
            if not ok:
                print(f"  ✗ [{st}] {name}: {detail}", file=sys.stderr)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
