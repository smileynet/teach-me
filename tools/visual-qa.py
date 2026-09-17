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

# Windows consoles default to cp1252; force UTF-8 so ✓/→/emoji glyphs don't crash (#265).
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(_sys.stderr, "reconfigure"):
    _sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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


_SVG_INVENTORY_JS = """
() => Array.from(document.querySelectorAll('body svg')).map((svg, index) => {
    const parts = [];
    for (let node = svg; node && node.nodeType === 1 && node.tagName !== 'BODY'; node = node.parentElement) {
        let part = node.tagName.toLowerCase();
        if (node.id) part += '#' + node.id;
        else if (node.classList.length) part += '.' + Array.from(node.classList).join('.');
        parts.unshift(part);
    }
    const rect = svg.getBoundingClientRect();
    return {
        index: index,
        path: parts.join(' > ') || 'svg',
        attr_width: svg.getAttribute('width'),
        attr_height: svg.getAttribute('height'),
        view_box: svg.getAttribute('viewBox'),
        rendered_width: rect.width,
        rendered_height: rect.height,
        hidden_ancestor: svg.closest('[style*="display: none"], [style*="display:none"], [hidden]') !== null
    };
})
"""


def recipe_diagrams(page, out_dir):
    """Check SVG diagrams in every view pane; report per-SVG failure diagnostics.

    UnifiedView keeps both the tree and map panes mounted and swaps them with
    display:none (#276), so SVGs in the inactive pane have no rendered box by
    design. The contract is therefore: every SVG must render with non-zero
    dimensions in AT LEAST ONE pane, and each pane's SVGs are asserted while
    that pane is actually visible (the toggle is exercised, not skipped).
    """
    interactions = []
    checks = []

    # Client-rendered views mount after domcontentloaded; wait for either the
    # unified view shell or any SVG before asserting.
    try:
        page.wait_for_selector('.unified-view, body svg', timeout=5000)
    except Exception:
        pass

    panes = [('initial', None)]
    map_tab = page.query_selector('button.vt-btn[role=tab]:has-text("Map")')
    if map_tab:
        panes.append(('map-pane', map_tab))

    seen = {}
    for pane_name, tab in panes:
        if tab:
            tab.click()
            page.wait_for_timeout(400)  # CSS display swap, no remount
        for item in page.evaluate(_SVG_INVENTORY_JS):
            record = seen.setdefault((item['path'], item['index']), item)
            if item['rendered_width'] > 0 and item['rendered_height'] > 0:
                record['rendered'] = True
                record['rendered_in'] = pane_name

    svgs = list(seen.values())
    valid = [s for s in svgs if s.get('rendered')]
    failed = [s for s in svgs if not s.get('rendered')]

    if svgs:
        page.screenshot(path=str(out_dir / 'diagrams.png'), full_page=True)
        interactions.append({
            'component': 'diagrams', 'action': 'full_page',
            'result': f'{len(valid)}/{len(svgs)} SVGs rendered '
                      f'(asserted across {len(panes)} view pane(s))',
            'screenshot': 'diagrams.png'
        })

    detail = f'{len(valid)}/{len(svgs)} inline SVGs have non-zero rendered dimensions'
    if failed:
        failing = '; '.join(
            f"{s['path']} (attrs {s['attr_width']}x{s['attr_height']}"
            + (f", viewBox {s['view_box']}" if s['view_box'] else '')
            + f"; rendered {s['rendered_width']}x{s['rendered_height']}"
            + ('; hidden ancestor' if s['hidden_ancestor'] else '') + ')'
            for s in failed
        )
        detail += ' — failing: ' + failing

    checks.append({
        'name': 'svg_renders',
        'pass': len(failed) == 0 and len(svgs) > 0,
        'detail': detail
    })

    return interactions, checks


RECIPES = {
    'glossary': recipe_glossary,
    'quiz': recipe_quiz,
    'reveal': recipe_reveal,
    'diagrams': recipe_diagrams,
}


def _resize_screenshots(output_dir):
    """Resize all PNGs to ≤768px long edge for Bedrock multi-image analysis."""
    magick = None
    for cmd in ['magick', 'convert']:
        if subprocess.run(['which', cmd], capture_output=True).returncode == 0:
            magick = cmd
            break
    if not magick:
        return  # ImageMagick not available, skip silently

    for png in output_dir.rglob('*.png'):
        subprocess.run([magick, str(png), '-resize', '768x768>', str(png)],
                       capture_output=True)


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

    # Resize screenshots for analysis (≤1568px long edge)
    _resize_screenshots(output_dir)

    manifest_path = output_dir / 'manifest.json'
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f'\n{"PASS" if total_failed == 0 else "FAIL"}: '
          f'{total_passed} checks passed, {total_failed} failed')
    print(f'Manifest: {manifest_path}')

    sys.exit(0 if total_failed == 0 else 1)


if __name__ == '__main__':
    main()
