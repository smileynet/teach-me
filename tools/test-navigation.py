#!/usr/bin/env python3
"""
Playwright navigation + interaction validation suite.

Tests the full user journey across all page types:
- Index → Map → Lesson → Quiz → back navigation
- Generation flow (mock)
- Mark complete + reopen
- Suggestion banner

Captures screenshots at each step for visual review.

Usage:
    python tools/test-navigation.py [--base-url http://localhost:8787]

Requires: playwright (pip install playwright && playwright install chromium)
"""

import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

BASE_URL = sys.argv[sys.argv.index("--base-url") + 1] if "--base-url" in sys.argv else "http://localhost:8787"
SCREENSHOTS_DIR = Path(__file__).parent.parent / "test-results" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

results = []


def report(name: str, passed: bool, detail: str = ""):
    status = "✓" if passed else "✗"
    results.append((name, passed, detail))
    print(f"  {status} {name}" + (f" — {detail}" if detail and not passed else ""))


def screenshot(page, name: str):
    path = SCREENSHOTS_DIR / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    return path


def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        # === 1. Index → Map ===
        page.goto(f"{BASE_URL}/lessons/index.html", wait_until="networkidle")
        screenshot(page, "01-index")
        has_cards = page.locator(".domain-card").count() > 0
        report("1. Index loads with domain cards", has_cards)

        # Click the data-analytics domain card (known-good)
        analytics_card = page.locator('a[href*="modern-data-analytics"]')
        if analytics_card.count() > 0:
            analytics_card.first.click()
        else:
            page.locator(".domain-card").first.click()
        page.wait_for_load_state("networkidle")
        time.sleep(3)  # wait for async detection
        screenshot(page, "02-map-page")
        is_map = "-map.html" in page.url
        report("2. Index → Map navigation", is_map)

        # === 2. Map: suggestion banner ===
        banner = page.locator("#suggestion-banner")
        banner_visible = banner.is_visible() if banner.count() > 0 else False
        report("3. Suggestion banner visible", banner_visible)
        screenshot(page, "03-suggestion-banner")

        # === 3. Map → Lesson (click green/blue node) ===
        # Use JS to find a node with a lesson and click it
        nav_result = page.evaluate("""() => {
            for (const [slug, topic] of Object.entries(TOPICS)) {
                if (topic.lesson_file) {
                    selectTopic(slug);
                    return {slug, lesson_file: topic.lesson_file};
                }
            }
            return null;
        }""")

        if nav_result:
            # selectTopic navigates directly for topics with lessons
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            screenshot(page, "04-lesson-page")
            on_lesson = "/lessons/" in page.url and "-map" not in page.url and "quiz" not in page.url
            report("4. Map → Lesson (green/blue node click)", on_lesson, page.url)
        else:
            report("4. Map → Lesson (green/blue node click)", False, "No topics with lessons found")

        # === 4. Lesson → Quiz ===
        if "/lessons/" in page.url and "-map" not in page.url:
            time.sleep(2)  # wait for lesson-actions.js
            quiz_btn = page.locator("text=Take the quiz")
            if quiz_btn.count() > 0:
                quiz_btn.first.click()
                page.wait_for_load_state("networkidle")
                screenshot(page, "05-quiz-page")
                on_quiz = "quiz" in page.url
                report("5. Lesson → Quiz navigation", on_quiz, page.url)

                # === 5. Quiz: has cards and nav ===
                cards = page.locator(".card").count()
                has_back_lesson = page.locator("text=Back to lesson").count() > 0
                has_back_map = page.locator("text=Back to map").count() > 0
                report("6. Quiz has question cards", cards > 0, f"{cards} cards")
                report("7. Quiz has ← Back to lesson", has_back_lesson)
                report("8. Quiz has ← Back to map", has_back_map)

                # === 6. Quiz → Lesson (back) ===
                page.locator("text=Back to lesson").first.click()
                page.wait_for_load_state("networkidle")
                back_to_lesson = "-quiz" not in page.url and "/lessons/" in page.url
                report("9. Quiz → Back to lesson", back_to_lesson, page.url)
                screenshot(page, "06-back-to-lesson")
            else:
                report("5. Lesson → Quiz navigation", False, "No 'Take the quiz' button found")
                for i in range(6, 10):
                    report(f"{i}. (skipped — no quiz)", False, "depends on test 5")

        # === 7. Lesson → Map (back) ===
        time.sleep(3)
        back_map = page.locator(".lesson-action-bar a:has-text('Back to map')")
        if back_map.count() == 0:
            back_map = page.locator("a:has-text('Back to map')")
        if back_map.count() > 0:
            back_map.first.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            on_map = "-map.html" in page.url
            report("10. Lesson → Back to map", on_map, page.url)
            screenshot(page, "07-back-to-map")
        else:
            report("10. Lesson → Back to map", False, "No 'Back to map' link found")

        # === 8. Map → Index ===
        all_lessons = page.locator("text=All Lessons")
        if all_lessons.count() > 0:
            all_lessons.first.click()
            page.wait_for_load_state("networkidle")
            on_index = "index.html" in page.url
            report("11. Map → All Lessons (index)", on_index, page.url)
            screenshot(page, "08-back-to-index")
        else:
            report("11. Map → All Lessons (index)", False, "No 'All Lessons' link")

        # === 9. Map: gray node → detail panel ===
        page.goto(f"{BASE_URL}/lessons/modern-data-analytics-stacks-map.html", wait_until="networkidle")
        time.sleep(3)
        # Use JS to find and click a not-started topic
        gray_clicked = page.evaluate("""() => {
            for (const [slug, topic] of Object.entries(TOPICS)) {
                if (topic.status === 'not-started' && !topic.lesson_file) {
                    selectTopic(slug);
                    return slug;
                }
            }
            return null;
        }""")
        if gray_clicked:
            time.sleep(1)
            detail_visible = page.locator("#detail-panel.visible").count() > 0
            has_generate = page.locator("text=Generate this topic").count() > 0
            report("12. Gray node → detail panel with Generate", detail_visible and has_generate)
            screenshot(page, "09-detail-panel")
        else:
            report("12. Gray node → detail panel", False, "No gray nodes found")

        # === 10. Mark complete flow ===
        # Go to a lesson that's not yet complete
        page.goto(f"{BASE_URL}/lessons/0001-iceberg-metadata-tree.html", wait_until="networkidle")
        time.sleep(3)
        mark_btn = page.locator("#mark-complete-btn")
        if mark_btn.count() > 0:
            mark_btn.click()
            time.sleep(3)
            # Should navigate to map
            on_map_after = "-map.html" in page.url
            report("13. Mark complete → navigates to map", on_map_after, page.url)
            screenshot(page, "10-after-mark-complete")
        else:
            # Already complete — verify "Completed" + "Reopen" are shown
            completed_text = page.locator("text=Completed").count() > 0
            reopen_btn = page.locator("text=Reopen").count() > 0
            report("13. Mark complete (already done — Completed + Reopen visible)", completed_text and reopen_btn)
            screenshot(page, "10-already-complete")

        # === 11. Verify green node on map ===
        page.goto(f"{BASE_URL}/lessons/modern-data-analytics-stacks-map.html", wait_until="networkidle")
        time.sleep(3)
        storage_fill = page.locator('[data-slug="storage-and-table-formats"] path').get_attribute("fill")
        is_green_or_blue = storage_fill in ("#dcfce7", "#dbeafe")
        report("14. Map shows correct node color after state change", is_green_or_blue, f"fill={storage_fill}")
        screenshot(page, "11-final-map-state")

        browser.close()

    # === Report ===
    print(f"\n{'='*50}")
    passed = sum(1 for _, p, _ in results if p)
    failed = sum(1 for _, p, _ in results if not p)
    print(f"Results: {passed} passed, {failed} failed")

    if failed:
        print("\nFailed tests:")
        for name, p, detail in results:
            if not p:
                print(f"  ✗ {name}: {detail}")

    # Write report
    report_path = SCREENSHOTS_DIR.parent / "navigation-report.md"
    with open(report_path, "w") as f:
        f.write("# Navigation Test Report\n\n")
        f.write(f"Run: {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Base URL: {BASE_URL}\n\n")
        f.write(f"**{passed} passed, {failed} failed**\n\n")
        f.write("| # | Test | Result | Detail |\n")
        f.write("|---|------|--------|--------|\n")
        for name, p, detail in results:
            f.write(f"| {'✓' if p else '✗'} | {name} | {'PASS' if p else 'FAIL'} | {detail} |\n")
        f.write(f"\n\nScreenshots in: `test-results/screenshots/`\n")
    print(f"\nReport: {report_path}")
    print(f"Screenshots: {SCREENSHOTS_DIR}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_tests())
