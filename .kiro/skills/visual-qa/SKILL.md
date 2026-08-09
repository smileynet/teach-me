---
name: visual-qa
description: "Run visual QA on lesson pages — exercise interactive components, capture screenshots, report findings. Use after UI changes or feature additions. Trigger: visual qa, check the ui, screenshot all pages, verify components, test the lessons visually, check glossary visuals."
metadata:
  type: process
  invocation: both
  practice: null
---

# Visual QA

Verify that UI components render and behave correctly by exercising them and analyzing the evidence.

## General Check

Run the automated tool to exercise all components across all pages:

```bash
mise run visual-qa
```

This produces `.scratch/visual-qa/manifest.json` + screenshots per page. If it exits 0, all behavioral checks pass (tooltips appear, trays open, quizzes give feedback, SVGs render). If it exits 1, something is broken — read the manifest for which checks failed.

The tool is a *behavioral* check. It answers "does this work?" not "does this look right?"

## Feature-Specific Visual Review

After building or modifying a specific feature, run the tool with `--focus` to scope screenshots, then analyze those screenshots against the feature's design intent.

```bash
python tools/visual-qa.py --serve --focus glossary
```

Then load the screenshots and analyze. The analysis prompt should be tailored to what the feature is supposed to look and feel like.

### Glossary

Capture: `.scratch/visual-qa/*/glossary-hover.png`, `glossary-tray-term.png`, `glossary-tray-list.png`

Analyze for:
- **Hover tooltip**: Dark background, white text, positioned above the term with arrow pointing down. Text is readable (not clipped, not overflowing). Does not obscure the content the learner is reading.
- **Term underlines**: Dotted, muted color, subtle — noticeable but not distracting. Should NOT look like a hyperlink (no solid underline, no blue color on the text itself).
- **Tray (term view)**: Slides from right, 320px wide, shows term name as heading + definition as body text. "← All terms" link visible. × close button in top-right.
- **Tray (list view)**: All defined terms listed, clickable, no visual clutter. Title says "Glossary". Back button hidden.
- **Overall**: Terms blend into the lesson flow. A reader who ignores them sees normal prose. A reader who notices them can get help without context-switching.

### Quiz

Capture: `.scratch/visual-qa/*/quiz-initial.png`, `quiz-answered.png`

Analyze for:
- **Initial state**: Questions bold, options in bordered cards. All options same visual weight — no clue which is correct. Radio buttons visible.
- **After answer**: Selected answer highlighted green (correct) or red (incorrect). Correct answer always highlighted green. Explanation appears below with blue left-border callout. Source links present if specified.
- **Overall**: Clean, not gamified. Looks like a thoughtful knowledge check, not a game show.

### Progressive Reveal

Capture: `.scratch/visual-qa/*/reveal-step-*.png`

Analyze for:
- **Step 1**: Only one element visible. Clear call-to-action (Next button). "Step 1 of N" indicator.
- **Step N**: Each step adds exactly one element to the diagram. Previous elements remain. Arrows/connections appear between steps.
- **Controls**: Prev/Next buttons centered, step counter between them. Prev disabled on step 1.
- **Overall**: Builds the mental model incrementally. No step shows more than 5-9 elements total. Colors follow vocabulary (blue=primary, amber=metadata, green=data).

### Diagrams (SVG)

Capture: `.scratch/visual-qa/*/diagrams.png` or `full-page.png`

Analyze for:
- **Renders at all**: Non-blank, visible shapes and text.
- **Color vocabulary**: Blue for primary/input, amber for processing/metadata, green for output/data, gray for infrastructure. Consistent within the page.
- **Labels**: ON the diagram (inside or immediately adjacent to shapes), not in a separate legend.
- **Scale**: Fits within the lesson column width without horizontal scroll. Text readable at normal zoom.
- **Overall**: Teaches something. If removing it wouldn't hurt understanding, it shouldn't be there (coherence principle).

## When to Run

| Situation | What to do |
|-----------|-----------|
| Changed `assets/*.js` or `assets/*.css` | `mise run visual-qa` (full behavioral check) |
| Just built a new component | `--focus <component>` + analyze screenshots against the section above |
| Ran jargon skill on a lesson | `--focus glossary` + quick check terms aren't overloading the page |
| Before closing a visual ticket | Full check + analyze relevant screenshots |
| Routine health check | `mise run visual-qa` — if green, move on |

## What This Does NOT Do

- No pixel-diff regression (content changes constantly)
- No Lighthouse / accessibility audit (that's ticket 013)
- No cross-browser testing (static HTML, Chromium-only is fine)
- No aesthetic judgment from the tool itself — that's the agent's job when reading screenshots

## Screenshot Hygiene

Each run **wipes the output directory first** — only the most current screenshots exist. Never accumulate multiple versions of the same feature state.

When capturing manual screenshots (via Playwright MCP during development):
- Save to `.scratch/screenshots/` with descriptive names (no timestamps)
- Before a new capture session, delete the previous session's screenshots
- One screenshot per state, not multiples of the same thing

### Sizing for Analysis

**The Bedrock constraint:** When a conversation has >20 images total (across all turns, accumulated in history), the per-image max drops from 8000px to 2000px. In long sessions with multiple screenshot rounds, you WILL hit this.

**Rules:**
1. Pre-resize all screenshots to **≤ 768px long edge** before analysis (safe under all limits, fast to process)
2. In long sessions (15+ images already sent), **dispatch a fresh subagent** for image analysis — it starts with zero image history
3. Never accumulate >15 images in a single session without dispatching

```bash
# Resize for analysis
for f in .scratch/visual-qa/**/*.png; do
  magick "$f" -resize '768x768>' "$f"
done
```

**Fresh subagent for image analysis (when session has accumulated images):**
```
Dispatch subagent: "Read these images and analyze against [criteria]:
  .scratch/visual-qa/0001-iceberg-metadata-tree/full-page.png
  .scratch/visual-qa/0001-iceberg-metadata-tree/glossary-tray-term.png
Write findings to .scratch/visual-qa-analysis.md"
```

**Analysis batching:** ≤ 3 images per analysis call. Label each with its role.

The principle: anyone reading `.scratch/visual-qa/` sees exactly the current state. No archaeology required.
