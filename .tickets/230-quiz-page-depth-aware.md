---
id: "230"
title: "generate-quiz-page.py: depth-aware paths for per-domain subfolder quizzes"
status: done
priority: low
blocked_by: []
tags: [infra, quiz]
---

# generate-quiz-page.py: depth-aware paths for per-domain subfolder quizzes

## Problem

`tools/generate-quiz-page.py` hardcodes `depth=2` (`render_quiz_page(..., depth=2)` at `:66`) and builds depth-2 relative back-links. With the per-domain subfolder convention (`lessons/{domain-slug}/NN-slug.html`), the quiz belongs at `lessons/{domain-slug}/quiz/NN-slug-quiz.html` — **depth 3**. At that location the generated links are wrong:

- `../../assets/style.css` → resolves to `lessons/assets/` (needs `../../../assets/`)
- back-to-lesson `../{domain}/NN-slug.html` → doubles the domain segment (needs `../NN-slug.html`)

Discovered during #217/#229: the lesson→quiz link IS correct (page-shell derives `quiz/{id}-quiz.html` relative to the lesson — `LessonActions.js:24`), so navigation TO the quiz works. Only the quiz page's OWN outbound links (assets, back-to-lesson) are off.

## What to build

- Add a `--depth` arg (or infer from `--output` path) to `generate-quiz-page.py`.
- Compute back-to-lesson and back-to-map links relative to the quiz's actual location, not a fixed depth-2 assumption.
- Regenerate the #217 quiz (`examples/godot-gamedev/lessons/blender-texture-prep/quiz/01-texture-audit-quiz.html`) and confirm its assets + back-links resolve via a live server.

## Acceptance criteria

- [x] Quiz generated into a per-domain subfolder has correct asset + back-link prefixes (verified via live server 200s)
- [x] Flat `lessons/quiz/` quizzes (existing examples) still generate correctly (no regression)
- [x] #217 quiz relinked correctly

## Resolution

Made `render_quiz_page` (`tools/lib/page_template.py`) depth-aware and `generate-quiz-page.py` depth-inferring.

**Root cause:** `render_quiz_page` hardcoded depth-2 assumptions — module import `'../../assets/components/QuizView.js'`, `index_url='../index.html'`, `map_url='../{slug}-map.html'`; and `generate_page` passed the full `lesson_file` path (with subfolder) as `lesson_id`.

**Fix:**
- `render_quiz_page`: `up_to_lessons = "../"*(depth-1)` for index/map; `assets_prefix = "../"*depth` for the module import; `lesson_url = "../{lesson_id}.html"` always (the quiz is always one dir below its lesson).
- `generate-quiz-page.py`: added `_infer_depth(output, workspace)` = path-parts-minus-filename, a `--depth` override, threaded `depth` through `generate_page`, and `lesson_id` now uses the basename (`rsplit("/")[-1]`).

**Evidence:**
- Regenerated #217 quiz → depth 3 inferred. Links: `../../../assets/style.css` + QuizView, `../01-texture-audit.html`, `../../index.html`, `../../blender-texture-prep-map.html`.
- Served `examples/godot-gamedev` and curled all 6 targets (style.css, QuizView.js, lesson, index, map, quiz-self) → **all 200**.
- Regression: regenerated a flat depth-2 quiz → identical to pre-fix links (`../../assets`, `../lesson`, `../index`, `../map`). No regression.
- `mise run verify` → EXIT 0, 8/8 interactive checks, clean console.
