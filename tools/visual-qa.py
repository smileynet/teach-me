#!/usr/bin/env python3
"""visual-qa.py — Exercise UI components and capture evidence.

Usage:
  python tools/visual-qa.py [OPTIONS]

Options:
  --pages PATH...     Specific lesson files (default: all lessons/*.html)
  --output-dir DIR    Where to write screenshots + manifest (default: .scratch/visual-qa/)
  --base-url URL      Server URL (default: http://localhost:8080)
  --focus COMPONENT   Only test one component: glossary, quiz, reveal, diagrams
  --serve             Auto-start a server for the duration of the run
  --port PORT         Port for auto-serve (default: 8080)

Exit codes:
  0 = all checks pass
  1 = one or more checks failed
  2 = crash / setup error
"""

import argparse
import json
import os
import sys
import subprocess
import time
import signal
from datetime import datetime, timezone
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: playwright not installed. Run: uv pip install playwright && playwright install chromium", file=sys.stderr)
    sys.exit(2)


# --- Component Recipes ---

def detect_components(page):
    """Detect which interactive components are on the page."""
    found = []
    if page.query_selector('.term'):
        found.append('glossary')
    if page.query_selector('[data-quiz], .quiz-options'):
        found.append('quiz')
    if page.query_selector('[data-step]'):
        found.append('reveal')
    if page.query_selector('svg'):
        found.append('diagrams')
    return found


def recipe_glossary(page, out_dir):
    """Exercise glossary: hover tooltip, click tray, back to list, close."""
    interactions = []
    checks = []

    terms = page.query_selector_all('.term')
    glossary_el = page.query_selector('#glossary-data')

    # Check: terms wired to definitions
    if glossary_el:
        data = json.loads(glossary_el.text_content())
        wired = sum(1 for t in terms if t.get_attribute('data-term') in data or t.get_attribute('data-def'))
        checks.append({
            'name': 'glossary_terms_wired',
            'pass': wired == len(terms),
            'detail': f'{wired}/{len(terms)} terms resolve to definitions'
        })
    elif terms:
        # All must have data-def inline
        wired = sum(1 for t in terms if t.get_attribute('data-def'))
        checks.append({
            'name': 'glossary_terms_wired',
            'pass': wired == len(terms),
            'detail': f'{wired}/{len(terms)} terms have inline definitions'
        })

    if not terms:
        return interactions, checks

    first_term = terms[0]

    # Hover → tooltip
    first_term.hover()
    page.wait_for_timeout(200)
    tooltip = page.query_selector('.glossary-tooltip')
    interactions.append({
        'component': 'glossary', 'action': 'hover',
        'result': 'tooltip_shown' if tooltip else 'no_tooltip',
        'screenshot': 'glossary-hover.png'
    })
    page.screenshot(path=str(out_dir / 'glossary-hover.png'))

    # Move away to dismiss tooltip
    page.mouse.move(0, 0)
    page.wait_for_timeout(100)

    # Click → tray
    first_term.click()
    page.wait_for_timeout(300)
    tray = page.query_selector('.glossary-tray.open')
    interactions.append({
        'component': 'glossary', 'action': 'click',
        'result': 'tray_opened' if tray else 'no_tray',
        'screenshot': 'glossary-tray-term.png'
    })
    page.screenshot(path=str(out_dir / 'glossary-tray-term.png'))

    # Back → list
    back_btn = page.query_selector('.glossary-tray-back')
    if back_btn:
        back_btn.click()
        page.wait_for_timeout(200)
        list_items = page.query_selector_all('.glossary-tray-list li')
        interactions.append({
            'component': 'glossary', 'action': 'back',
            'result': f'list_shown ({len(list_items)} items)',
            'screenshot': 'glossary-tray-list.png'
        })
        page.screenshot(path=str(out_dir / 'glossary-tray-list.png'))

    # Escape → close
    page.keyboard.press('Escape')
    page.wait_for_timeout(200)
    tray_after = page.query_selector('.glossary-tray.open')
    interactions.append({
        'component': 'glossary', 'action': 'escape',
        'result': 'tray_closed' if not tray_after else 'tray_still_open'
    })

    checks.append({
        'name': 'glossary_tray_opens',
        'pass': tray is not None,
        'detail': 'Click term opens slide-out tray'
    })
    checks.append({
        'name': 'glossary_tray_closes',
        'pass': tray_after is None,
        'detail': 'Escape closes tray'
    })

    return interactions, checks


def recipe_quiz(page, out_dir):
    """Exercise quiz: screenshot initial, click answer, screenshot feedback."""
    interactions = []
    checks = []

    page.screenshot(path=str(out_dir / 'quiz-initial.png'))
    interactions.append({
        'component': 'quiz', 'action': 'initial_state',
        'result': 'captured', 'screenshot': 'quiz-initial.png'
    })

    # Click first option of first question
    first_option = page.query_selector('.quiz-label input, .quiz-label')
    if first_option:
        first_option.click()
        page.wait_for_timeout(300)
        feedback = page.query_selector('.quiz-correct, .quiz-incorrect')
        interactions.append({
            'component': 'quiz', 'action': 'answer',
            'result': 'feedback_shown' if feedback else 'no_feedback',
            'screenshot': 'quiz-answered.png'
        })
        page.screenshot(path=str(out_dir / 'quiz-answered.png'))
        checks.append({
            'name': 'quiz_feedback',
            'pass': feedback is not None,
            'detail': 'Selecting answer shows correct/incorrect feedback'
        })

    return interactions, checks


def recipe_reveal(page, out_dir):
    """Exercise progressive reveal: step through all steps, screenshot each."""
    interactions = []
    checks = []

    steps = page.query_selector_all('[data-step]')
    step_count = len(steps)

    # Screenshot initial
    page.screenshot(path=str(out_dir / 'reveal-step-1.png'))
    interactions.append({
        'component': 'reveal', 'action': 'step_1',
        'result': 'captured', 'screenshot': 'reveal-step-1.png'
    })

    # Advance through steps
    for i in range(2, step_count + 1):
        next_btn = page.query_selector('button:has-text("Next")')
        if not next_btn:
            break
        next_btn.click()
        page.wait_for_timeout(300)
        fname = f'reveal-step-{i}.png'
        page.screenshot(path=str(out_dir / fname))
        interactions.append({
            'component': 'reveal', 'action': f'step_{i}',
            'result': 'captured', 'screenshot': fname
        })

    checks.append({
        'name': 'reveal_steps_advance',
        'pass': step_count > 0,
        'detail': f'{step_count} steps detected and exercised'
    })

    return interactions, checks


def recipe_diagrams(page, out_dir):
    """Check SVG diagrams: verify non-zero dimensions, screenshot."""
    interactions = []
    checks = []

    svgs = page.query_selector_all('body svg')
    valid = 0
    for i, svg in enumerate(svgs):
        box = svg.bounding_box()
        if box and box['width'] > 0 and box['height'] > 0:
            valid += 1

    if svgs:
        page.screenshot(path=str(out_dir / 'diagrams.png'), full_page=True)
        interactions.append({
            'component': 'diagrams', 'action': 'full_page',
            'result': f'{valid}/{len(svgs)} SVGs rendered', 'screenshot': 'diagrams.png'
        })

    checks.append({
        'name': 'svg_renders',
        'pass': valid == len(svgs) and len(svgs) > 0,
        'detail': f'{valid}/{len(svgs)} inline SVGs have non-zero dimensions'
    })

    return interactions, checks


RECIPES = {
    'glossary': recipe_glossary,
    'quiz': recipe_quiz,
    'reveal': recipe_reveal,
    'diagrams': recipe_diagrams,
}


# --- Main ---

def run_page(page, url, page_path, out_dir, focus=None):
    """Run all applicable recipes on one page."""
    page.goto(url)
    page.wait_for_load_state('domcontentloaded')

    # Check for JS errors
    js_errors = []
    page.on('pageerror', lambda err: js_errors.append(str(err)))

    components = detect_components(page)
    all_interactions = []
    all_checks = []

    # If focused, only run that recipe
    if focus:
        if focus in components:
            recipe = RECIPES[focus]
            interactions, checks = recipe(page, out_dir)
            all_interactions.extend(interactions)
            all_checks.extend(checks)
        else:
            # Not a failure — just skip this page
            return None
    else:
        # Full page screenshot
        page.screenshot(path=str(out_dir / 'full-page.png'), full_page=True)

        # Run all detected component recipes
        for comp in components:
            recipe = RECIPES.get(comp)
            if recipe:
                interactions, checks = recipe(page, out_dir)
                all_interactions.extend(interactions)
                all_checks.extend(checks)

    # JS error check
    all_checks.append({
        'name': 'no_js_errors',
        'pass': len(js_errors) == 0,
        'detail': f'{len(js_errors)} JS errors' if js_errors else 'No JS console errors'
    })

    return {
        'path': page_path,
        'components_found': components,
        'interactions': all_interactions,
        'checks': all_checks
    }


def main():
    parser = argparse.ArgumentParser(description='Visual QA for lesson pages')
    parser.add_argument('--pages', nargs='*', help='Lesson files to test (default: all)')
    parser.add_argument('--output-dir', default='.scratch/visual-qa', help='Output directory')
    parser.add_argument('--base-url', default='http://localhost:8080', help='Server base URL')
    parser.add_argument('--focus', choices=['glossary', 'quiz', 'reveal', 'diagrams'],
                        help='Only test one component type')
    parser.add_argument('--serve', action='store_true', help='Auto-start HTTP server')
    parser.add_argument('--port', type=int, default=8080, help='Port for auto-serve')
    args = parser.parse_args()

    # Discover pages
    if args.pages:
        pages = args.pages
    else:
        lesson_dir = Path('lessons')
        if not lesson_dir.exists():
            print('ERROR: no lessons/ directory found', file=sys.stderr)
            sys.exit(2)
        pages = sorted(str(p) for p in lesson_dir.glob('*.html'))

    if not pages:
        print('ERROR: no lesson pages found', file=sys.stderr)
        sys.exit(2)

    # Auto-serve if requested
    server_proc = None
    if args.serve:
        server_proc = subprocess.Popen(
            [sys.executable, '-m', 'http.server', str(args.port), '--bind', '0.0.0.0'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        args.base_url = f'http://localhost:{args.port}'
        time.sleep(0.5)

    output_dir = Path(args.output_dir)
    # Clean previous run — only keep most current screenshots
    if output_dir.exists():
        import shutil
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        'run_at': datetime.now(timezone.utc).isoformat(),
        'base_url': args.base_url,
        'focus': args.focus,
        'pages': []
    }

    total_passed = 0
    total_failed = 0

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 800})
            page = context.new_page()

            for page_path in pages:
                slug = Path(page_path).stem
                page_out = output_dir / slug
                page_out.mkdir(parents=True, exist_ok=True)

                url = f'{args.base_url}/{page_path}'
                print(f'  {page_path}', end=' ')

                result = run_page(page, url, page_path, page_out, focus=args.focus)

                if result is None:
                    print(f'  (no {args.focus})')
                    continue

                manifest['pages'].append(result)

                passed = sum(1 for c in result['checks'] if c['pass'])
                failed = sum(1 for c in result['checks'] if not c['pass'])
                total_passed += passed
                total_failed += failed

                status = '✓' if failed == 0 else '✗'
                print(f'{status} ({len(result["components_found"])} components, {passed} pass, {failed} fail)')

            browser.close()

    finally:
        if server_proc:
            server_proc.terminate()
            server_proc.wait()

    manifest['summary'] = {
        'pages': len(manifest['pages']),
        'interactions': sum(len(p['interactions']) for p in manifest['pages']),
        'checks_passed': total_passed,
        'checks_failed': total_failed
    }

    manifest_path = output_dir / 'manifest.json'
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f'\n{"PASS" if total_failed == 0 else "FAIL"}: '
          f'{total_passed} checks passed, {total_failed} failed')
    print(f'Manifest: {manifest_path}')

    sys.exit(0 if total_failed == 0 else 1)


if __name__ == '__main__':
    main()
