---
id: "074"
title: "Validation: Playwright full navigation + visual analysis of all page types"
status: done
priority: high
blocked_by: ["073"]
type: feature
---

# Validation: Playwright full navigation + visual analysis

## What to build

A Playwright test script that exercises the complete user journey across all page types, validates every navigation link and action, and captures screenshots for visual review.

### Navigation tests (click-through)

1. **Index → Map:** Click a domain card → verify map page loads
2. **Map → Lesson (green/blue node):** Click a completed/in-progress node → verify lesson page loads
3. **Map → Generate (gray node):** Click ungenerated node → verify detail panel appears with Generate button
4. **Lesson → Quiz:** Click "Take the quiz" → verify quiz page loads with questions
5. **Quiz → Lesson:** Click "← Back to lesson" → verify returns to correct lesson
6. **Quiz → Map:** Click "← Back to map" → verify returns to domain map
7. **Lesson → Map:** Click "← Back to map" → verify returns to map with correct state
8. **Lesson → Mark complete:** Click mark complete → verify navigates to map → node is green
9. **Map → Index:** Click "← All Lessons" → verify returns to index
10. **Map leads-to:** Click a "From here" button → verify modal or navigation

### Action tests (interactive)

11. **Generation flow:** Click generate on gray node → verify modal → mock generation → verify redirect
12. **Cancel generation:** Start mock → click cancel → verify cancelled state
13. **Mark complete + reopen:** Mark complete → go back → verify green → reopen → verify not-started
14. **Suggestion banner:** Verify banner shows and clicking it opens appropriate action

### Visual capture (screenshots at each stage)

Capture a named screenshot at each step. After all tests pass, analyze screenshots for:
- Consistent styling (colors, spacing, fonts match across pages)
- Status indicators visible and correct (green/blue/gray nodes)
- Action buttons visible and properly styled
- No layout overflow or broken elements
- Dark mode consistency (if theme toggle engaged)

### Output

- `test-results/navigation-report.md` — pass/fail per test with screenshot paths
- `test-results/screenshots/` — named PNGs for each step
- Visual findings: any inconsistencies flagged with screenshot evidence

## Acceptance criteria

- [ ] All 14 navigation/action tests pass
- [ ] Screenshots captured at each major state
- [ ] Visual analysis reports no layout breaks or style inconsistencies
- [ ] Script is reusable: `python tools/test-navigation.py` runs the full suite
- [ ] Can run headless (CI-compatible)

## Validation

- This ticket IS the validation. Its output validates ticket 073.

## Resolution (2026-08-12)

**14/14 tests pass.** Script: `python tools/test-navigation.py`

### Visual findings (from screenshot analysis):
1. **Index progress rings hardcoded** — not reading from /api/map (known gap, deferred)
2. **No selected-node highlight** on graph when detail panel shows — cosmetic
3. **Action bar** could use stronger visual separator from lesson content — cosmetic

None blocking. Navigation flow is complete and correct.
Screenshots in `test-results/screenshots/`, report in `test-results/navigation-report.md`.
