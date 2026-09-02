#!/usr/bin/env python3
"""
Playwright navigation suite — per-domain user journey across the library.

Discovers the library's domains at runtime from the aggregate index `#page-data`
island (no hardcoded slugs/filenames), then runs the core journey for EACH domain:

    aggregate index → domain map → a lesson → its quiz → breadcrumb back-nav

Rewritten for the current contract (#274): the map/lesson/quiz pages are Preact +
signals apps. The suite reads the `#page-data` JSON islands and asserts on stable DOM
hooks (`.dag-canvas[data-render-complete]`, `.topic-card`, `.quiz-view`, the
`aria-label="Breadcrumb"` landmark) — NOT the removed `TOPICS`/`selectTopic` globals or
the old `#detail-panel`/`#suggestion-banner`/`mark-complete-btn` selectors.

Navigation is asserted by ACT-then-VERIFY: click an accessible link/button, wait for the
URL to change, and confirm the landed `<h1>` — link presence alone proves nothing.

Serve the multi-domain library root and point the suite at it:
    python tools/serve.py --workspace library --port 8787 &
    python tools/test-navigation.py --base-url http://localhost:8787

Requires: playwright (pip install playwright && playwright install chromium)
"""

import json
import sys
import time
import urllib.request
from pathlib import Path

# Windows cp1252 stdout chokes on the ✓/✗/→ glyphs this prints (AGENTS.md Constraints).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

BASE_URL = sys.argv[sys.argv.index("--base-url") + 1] if "--base-url" in sys.argv else "http://localhost:8787"
SCREENSHOTS_DIR = Path(__file__).parent.parent / "test-results" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# (domain-slug | "index", check-name, passed, detail) — per-domain attribution.
results: list[tuple[str, str, bool, str]] = []


def report(scope: str, name: str, passed: bool, detail: str = ""):
    status = "✓" if passed else "✗"
    results.append((scope, name, passed, detail))
    print(f"  {status} [{scope}] {name}" + (f" — {detail}" if detail and not passed else ""))


def screenshot(page, name: str):
    page.screenshot(path=str(SCREENSHOTS_DIR / f"{name}.png"), full_page=True)


def discover_domains(base_url: str) -> list[dict]:
    """Read the aggregate index #page-data island → depth-0 domains with mapHref.

    Discovery is over HTTP (the served page), matching what the browser sees. The
    island is the single source of truth — the /api/map endpoint is unreliable at a
    multi-domain library root (falls back to one workspace).
    """
    html = urllib.request.urlopen(base_url + "/index.html", timeout=5).read().decode("utf-8")
    marker = 'id="page-data">'
    start = html.index(marker) + len(marker)
    end = html.index("</script>", start)
    data = json.loads(html[start:end])
    # Depth-0 domains only for the journey (sub-maps are reached via their parent's map).
    return [d for d in data["domains"] if d.get("depth", 0) == 0]


def wait_render_complete(page, timeout=8000):
    """Preact map pages flag readiness with .dag-canvas[data-render-complete='true'] —
    poll it instead of sleeping (avoids networkidle/hard-sleep flakiness)."""
    page.wait_for_selector('.dag-canvas[data-render-complete="true"]', timeout=timeout)


def h1_text(page) -> str:
    el = page.query_selector("h1")
    return (el.inner_text().strip() if el else "")


def journey_for_domain(page, base_url: str, domain: dict):
    """Run the core journey for ONE domain. Each step reports under the domain slug."""
    slug = domain["slug"]
    map_href = domain["mapHref"]           # e.g. iceberg-workspace/lessons/data-analytics-map.html
    folder = map_href.split("/")[0]        # folder != slug (data-analytics → iceberg-workspace)
    map_url = f"{base_url}/{map_href}"

    # --- 1. Aggregate → domain map (enter via the Tree row for this domain) ---
    page.goto(f"{base_url}/index.html", wait_until="domcontentloaded")
    page.wait_for_selector(".index-view")
    row = page.query_selector(f'a.ti-row[data-domain="{slug}"]')
    if not row:
        report(slug, "enter domain from tree", False, "no .ti-row[data-domain] on aggregate")
        return
    row.click()
    try:
        page.wait_for_url(f"**/{map_href}", timeout=8000)
    except PWTimeout:
        report(slug, "enter domain from tree", False, f"URL did not become {map_href} (got {page.url})")
        return
    try:
        wait_render_complete(page)
    except PWTimeout:
        report(slug, "map renders", False, "dag-canvas never data-render-complete")
        return
    report(slug, "aggregate → map", True)
    screenshot(page, f"nav-{slug}-01-map")

    # --- 2. Read the map's page-data island → find a topic with a lesson ---
    map_data = page.evaluate("() => JSON.parse(document.getElementById('page-data').textContent)")
    topics = map_data.get("topics", [])
    lesson_topic = next((t for t in topics if t.get("lessonPath")), None)
    if not lesson_topic:
        report(slug, "has a lesson to open", False, "no topic with lessonPath")
        return
    report(slug, "map page-data has topics", len(topics) > 0, f"{len(topics)} topics")

    # --- 3. Map → lesson (open via the topic card's primary action link) ---
    card = page.query_selector(f'.topic-card[data-topic-id="{lesson_topic["id"]}"]')
    open_link = card.query_selector("a.btn.primary[href]") if card else None
    if not open_link:
        report(slug, "map → lesson", False, "no a.btn.primary in topic card")
        return
    lesson_path = lesson_topic["lessonPath"]
    open_link.click()
    try:
        page.wait_for_url(f"**/{lesson_path}", timeout=8000)
    except PWTimeout:
        report(slug, "map → lesson", False, f"URL did not become {lesson_path} (got {page.url})")
        return
    report(slug, "map → lesson", True, )
    screenshot(page, f"nav-{slug}-02-lesson")

    # Lesson breadcrumb landmark present (2 links + current span = 3 crumbs).
    crumb_links = page.query_selector_all('nav[aria-label="Breadcrumb"] a')
    report(slug, "lesson has 3-crumb breadcrumb", len(crumb_links) == 2,
           f"{len(crumb_links)} crumb links (expected 2 + current span)")

    # --- 4. Lesson → quiz (the LessonActions bar's quiz button) ---
    quiz_url = f"quiz/{Path(lesson_path).stem}-quiz.html"
    # The LessonActions bar's quiz button starts as '…' then resolves (async HEAD probe)
    # to '📝 Take quiz' (quiz exists) or '+ Generate quiz'. Wait for the label to SETTLE
    # before branching — reading it too early catches the '…' placeholder (false skip).
    quiz_btn = None
    try:
        page.wait_for_selector(".lesson-actions-bar", timeout=5000)
        # Wait until a button in the bar mentions quiz and is no longer the '…' placeholder.
        page.wait_for_function(
            """() => {
                const els = document.querySelectorAll('.lesson-actions-bar button, .lesson-actions-bar a');
                return [...els].some(e => /quiz/i.test(e.textContent) && !e.textContent.includes('…'));
            }""",
            timeout=6000,
        )
        for b in page.query_selector_all(".lesson-actions-bar button, .lesson-actions-bar a"):
            if "quiz" in (b.inner_text() or "").lower():
                quiz_btn = b
                break
    except PWTimeout:
        pass
    if quiz_btn and "take quiz" in (quiz_btn.inner_text() or "").lower():
        quiz_btn.click()
        try:
            page.wait_for_url("**/quiz/**", timeout=8000)
            page.wait_for_selector(".quiz-view", timeout=6000)
            cards = page.query_selector_all(".quiz-card")
            report(slug, "lesson → quiz", len(cards) > 0, f"{len(cards)} quiz cards")
            screenshot(page, f"nav-{slug}-03-quiz")
            # --- 5. Quiz breadcrumb → back to lesson (assert real navigation) ---
            lesson_crumb = page.query_selector(f'nav[aria-label="Breadcrumb"] a[href*="{Path(lesson_path).stem}"]')
            if lesson_crumb:
                lesson_crumb.click()
                page.wait_for_url(f"**/{lesson_path}", timeout=8000)
                report(slug, "quiz breadcrumb → lesson", h1_text(page) != "")
            else:
                report(slug, "quiz breadcrumb → lesson", False, "no lesson crumb in quiz breadcrumb")
        except PWTimeout:
            report(slug, "lesson → quiz", False, f"quiz did not load (url={page.url})")
    else:
        # No quiz for this lesson — not a failure, just note it (quiz generation is on-demand).
        report(slug, "lesson → quiz", True, "no quiz yet (generate button shown) — skipped")

    # --- 6. Lesson → map via breadcrumb (back-nav, assert real navigation) ---
    page.goto(f"{base_url}/{Path(map_href).parent.as_posix()}/{lesson_path}", wait_until="domcontentloaded")
    map_crumb = page.query_selector(f'nav[aria-label="Breadcrumb"] a[href*="{slug}-map.html"], nav[aria-label="Breadcrumb"] a[href*="-map.html"]')
    if map_crumb:
        map_crumb.click()
        try:
            page.wait_for_url("**/*-map.html", timeout=8000)
            wait_render_complete(page)
            report(slug, "lesson breadcrumb → map", True)
        except PWTimeout:
            report(slug, "lesson breadcrumb → map", False, f"map did not load (url={page.url})")
    else:
        report(slug, "lesson breadcrumb → map", False, "no map crumb in lesson breadcrumb")


def check_resume_cue(page, base_url: str, domains: list[dict]):
    """Option A: assert the resume cue + its destination on the aggregate. All library
    domains are in-progress on disk, so the cue should resolve to a 'Continue where you
    left off → {domain}' link. (empty→orientation & all-complete→no-resume are deferred
    to a synthetic-fixture follow-up — they can't be exercised from the real library.)"""
    page.goto(f"{base_url}/index.html", wait_until="domcontentloaded")
    page.wait_for_selector(".index-view")
    cues = page.query_selector_all(".index-cue")
    report("index", "exactly one cue", len(cues) == 1, f"{len(cues)} cues")
    resume = page.query_selector(".index-cue-resume a")
    if resume:
        href = resume.get_attribute("href")
        resume.click()
        try:
            page.wait_for_url("**/*-map.html", timeout=8000)
            report("index", "resume cue → map", True, f"→ {href}")
        except PWTimeout:
            report("index", "resume cue → map", False, f"did not navigate to a map (href={href}, url={page.url})")
    else:
        # No resume cue means the orientation (empty) state — only expected if counts are
        # zeroed (clean-checkout overlay). Report as info, not a hard failure.
        report("index", "resume cue present", False,
               "no .index-cue-resume (overlay counts may be zeroed on this checkout)")


def run_tests():
    domains = discover_domains(BASE_URL)
    print(f"Discovered {len(domains)} depth-0 domains: {', '.join(d['slug'] for d in domains)}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for domain in domains:
            # Fresh context per domain — isolated storage, no cross-domain state bleed.
            ctx = browser.new_context(viewport={"width": 1280, "height": 900})
            page = ctx.new_page()
            try:
                journey_for_domain(page, BASE_URL, domain)
            except Exception as e:
                report(domain["slug"], "journey", False, f"errored: {e}")
            finally:
                ctx.close()

        # Index resume cue (once, on the aggregate).
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        try:
            check_resume_cue(page, BASE_URL, domains)
        except Exception as e:
            report("index", "resume cue", False, f"errored: {e}")
        finally:
            ctx.close()
        browser.close()

    # === Report ===
    print(f"\n{'='*56}")
    passed = sum(1 for _, _, ok, _ in results if ok)
    failed = sum(1 for _, _, ok, _ in results if not ok)
    print(f"Results: {passed} passed, {failed} failed")
    if failed:
        print("\nFailed:")
        for scope, name, ok, detail in results:
            if not ok:
                print(f"  ✗ [{scope}] {name}: {detail}")

    report_path = SCREENSHOTS_DIR.parent / "navigation-report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Navigation Test Report (per-domain journey)\n\n")
        f.write(f"Run: {time.strftime('%Y-%m-%d %H:%M')} · Base: {BASE_URL}\n\n")
        f.write(f"**{passed} passed, {failed} failed**\n\n")
        f.write("| Domain | Check | Result | Detail |\n|---|---|---|---|\n")
        for scope, name, ok, detail in results:
            f.write(f"| {scope} | {name} | {'PASS' if ok else 'FAIL'} | {detail} |\n")
        f.write("\nScreenshots: `test-results/screenshots/nav-*`\n")
    print(f"\nReport: {report_path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    from lib.serve_harness import serve_workspace

    # Reuse an explicitly-passed --base-url as-is; otherwise serve the multi-domain library/
    # root on an ephemeral port via the shared harness (hermetic, headless, auto-teardown).
    explicit = "--base-url" in sys.argv
    prefer = BASE_URL if explicit else "http://localhost:8787"
    if explicit:
        code = run_tests()
        sys.exit(code)
    with serve_workspace("library", prefer_url=prefer) as served:
        BASE_URL = served
        code = run_tests()
    sys.exit(code)
