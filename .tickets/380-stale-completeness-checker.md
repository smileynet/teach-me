---
id: "380"
title: "Fix stale check-topic-completeness.py: false-negatives on page-shell + Preact-quiz lessons"
status: open
blocked_by: []
tags: ["tooling"]
---

# Fix stale `check-topic-completeness.py`: false-negatives on current lessons

`tools/check-topic-completeness.py` reports three checks as FAILING on lessons that
are actually correct, because it greps for markup the current architecture replaced:

1. **`has_lesson_actions`** — greps for a literal `lesson-actions.js` script tag; the
   current page shell injects actions via `page-shell.js` + a `lesson-actions-config`
   block, so the literal filename is never present.
2. **`has_theme_toggle`** — greps for a literal `theme-toggle.js`; same story
   (consolidated into `page-shell.js`).
3. **quiz card count / types (`0 questions`, `0 types`)** — greps for `class="card"` /
   `class="card-type"` markup; the current quiz generator renders questions client-side
   from a `page-data` JSON island driving a Preact component, so the old card markup is
   never emitted.

Confirmed **pre-existing and systemic**: the shipped, known-good `gltf-format` and
`godot-asset-pipeline` lessons fail these three checks identically. The checker predates
the page-shell consolidation and the Preact-quiz island. It is NOT part of the CI gate
(`mise run verify`), so it doesn't block, but it produces misleading output that erodes
trust in the tool and forces every lesson build to hand-wave three "failures."

## What to build

Update the three stale checks to recognize the current architecture:
- `has_lesson_actions` → detect `page-shell.js` + a `lesson-actions-config` block (or
  whatever the shell uses to declare actions)
- `has_theme_toggle` → detect the theme toggle as delivered by `page-shell.js` /
  `typography-prefs.js`
- quiz features → parse the `page-data` JSON island (count questions and distinct
  `type` values) instead of grepping for `class="card"` markup

## Acceptance criteria

- [ ] `check-topic-completeness.py` reports the three checks as PASSING on the shipped
      `gltf-format` lessons (currently false-negative), verified before/after
- [ ] Reports PASS on the new `generative-media-pipelines/01-the-universal-serving-pipeline`
      lesson (9 questions, 6 types via the Preact island)
- [ ] Does NOT regress on any genuinely-incomplete topic (still reports real gaps)
- [ ] `mise run verify` passes

## Design source

- `tools/check-topic-completeness.py` (the three grep-based checks; quiz check ~`check_quiz_features`)
- `tools/lib/page_template.py` (`page-shell.js` shell / action + theme injection — source of truth)
- `tools/generate-quiz-page.py` (the `page-data` island the quiz check should parse)
- A shipped good lesson to calibrate against: `library/gltf-format/lessons/01-*.html`
- #371 Resolution section (the false-negative record)
