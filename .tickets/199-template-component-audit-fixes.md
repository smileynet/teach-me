---
id: "199"
title: "Address validated findings from template & component system audit"
status: open
blocked_by: []
tags: [platform]
---

# Address validated findings from template & component system audit

## Re-scope (2026-09-17, #335 — findings re-verified against source)

The sections below are the ORIGINAL audit. Since it ran, several findings were fixed or
proved invalid. The surviving scope is exactly this list:

1. **Port `tools/quick-check.py` onto `page_template._base_page`; delete
   `tools/lib/preact_page.py`** — confirmed: `preact_page.py:79-89` emits no blocking
   `typography-prefs.js` (FOUC; confirmed baked into
   `library/iceberg-workspace/lessons/review/quick-check.html`), and `preact_page.py:84`
   does not escape `<title>`.
2. **Dead "Explore subtopics" button** — confirmed at `assets/components/TopicCard.js:53`
   (no handler; the adjacent quiz button is now a wired GeneratePrompt). Wire it or
   remove it.
3. **Missing CSS, corrected precision:** only `.assess-buttons` (`QuizView.js:86`) and
   rating-specific rules are genuinely unstyled (rating buttons do carry styled `.btn`
   base classes). `.gen-progress` is a DEAD class — nothing emits it since GeneratePrompt
   replaced the old generation flow — so drop it rather than style it. `.leads-to-btn`
   IS styled inline on map pages (`generate_map_page.py:293-299`).
4. **Strip hardcoded import maps from scaffolds** — confirmed still outstanding:
   `assets/scaffolds/lesson.html:13-26` and `reference.html:9` duplicate
   `assets/import-map.json`.
5. **Delete `assets/components/ProgressiveReveal.js`** — still present (2026-09-17) and
   referenced by nothing else.
6. **ink-test-project artifact hygiene** — still undecided: `addons/` untracked (inkgd
   vendored in `a431fce` + a newer `addons/godot_ai/`), `script_templates/` deletions
   sitting uncommitted, `.godot/`/`*.uid` policy. Decide gitignore-vs-commit for each.

Fixed or invalid since the audit (do NOT redo): XSS claim invalid (no `innerHTML`
interpolation of topic data remains in Map/GraphView — measurement renders escaped
Preact output); GenButton interval leak gone (component superseded by GeneratePrompt);
LessonActions POST-failure UI shipped; "Generate quiz" dead button fixed (wired to
GeneratePrompt); GenerationModal/GenerationStream deleted; §2 depth-model items were
handled by #273 (re-verify only if breadcrumbs regress). QuizView has one `next()`
(:102) plus `interactiveNext` (:130) — re-audit for dead code when executing item 1.

## What to build

A full audit of the lesson template system (`tools/lib/`, `assets/scaffolds/`) and the
Preact component system (`assets/components/`) produced findings across five areas.
The primary agent should first **verify each finding** (the audit was delegated; line
numbers may have drifted), then address the validated ones in the priority order below.
Invalid findings should be noted here and skipped.

### 1. Consolidate template shell: delete `preact_page.py`

- `tools/lib/preact_page.py` duplicates the entire shell from `page_template.py`
  (import-map loader is a line-for-line copy of `page_template._import_map`, already
  drifted in indentation).
- Its output **omits page-shell.js and typography-prefs.js** — violates AGENTS.md
  ("Don't omit page-shell.js") and causes FOUC on quick-check pages.
- It does not HTML-escape `<title>` (`preact_page.py:84` vs escaped
  `page_template.py:124`).
- **Fix:** port `tools/quick-check.py` onto `page_template._base_page`, delete
  `preact_page.py`.

### 2. Fix the depth model in `page_template.py`

- `render_lesson_page` accepts `depth` but its breadcrumbs ignore it (correct only at
  depth 1, `page_template.py:162-167`); `render_reference_page` does use `../` prefixes.
- AGENTS.md mandates `lessons/{domain-slug}/NN-slug.html` (depth 2) but
  `render_lesson_page` assumes lessons sit flat next to `index.html`.
- `render_quiz_page` hardcodes depth-2 assumptions (`page_template.py:257, 286`).
- Also remove the dead `lesson_id` param in `render_lesson_page`.
- **Fix:** unify on depth-relative URLs everywhere; document the depth convention once.

### 3. Component bug fixes

- **XSS**: `MapView.computeLayout` interpolates topic titles into `innerHTML` for
  offscreen measurement (`MapView.js:26-32`). Everything else renders via htm (escaped);
  this path isn't. Escape or build via DOM APIs.
- **Dead buttons**: TopicCard "Generate quiz" / "Explore subtopics" have no onClick
  (`TopicCard.js:32-33`) — AGENTS.md silent-button violation.
- **Silent failure**: LessonActions `.catch` reports the optimistic status on failed
  POST (`LessonActions.js:52-53`) — user believes completion was saved. Add error UI.
- **Interval leak**: GenButton polls a signal with `setInterval`, never cleared on
  unmount (`GenButton.js:19-33`). Replace with a signal effect. Dead
  `GenerationStream` import there too.
- **Missing CSS**: `.rating-*`, `.assess-buttons`, `.gen-progress`, `.leads-to-btn`
  have zero rules in style.css/quiz.css — ReviewView rating buttons render unstyled,
  violating the hover/click-feedback constraint.
- **QuizView "show all" mode**: no summary shown, stale scores pollute the next run
  (`QuizView.js:133, 156`).

### 4. Delete dead code

- `GenerationModal` in `GenerationStream.js:47-75` (unreferenced; also has a
  side-effect-in-render bug if revived).
- `assets/components/ProgressiveReveal.js` (superseded by vanilla
  `assets/progressive-reveal.js`).
- Duplicate `next()` in `QuizView.js:109-112` (shadowed by `interactiveNext`).

### 5. Scaffolds

- Strip hardcoded import maps from `assets/scaffolds/lesson.html` and
  `reference.html` (duplicates `assets/import-map.json`; three-place edit trap).
  Reduce to content patterns per AGENTS.md.
- `reference.html` lacks glossary.css and breadcrumbs vs template output.
- Add the code-block + `data-file` content pattern to `lesson.html` (AGENTS.md
  constraint currently unrepresented in scaffolds).

### 6. Housekeeping (gitignore / commit hygiene)

- `ink-test-project/addons/` (the inkgd addon), `.godot/`, and `*.uid` files are
  untracked — decide gitignore vs commit for each.
- Committed example pages predate `data-theme="dark"` (e.g.
  `examples/godot-gamedev/lessons/0001-nodes-and-scenes.html`) — regenerate via
  `mise run maps:regenerate`-style tooling after template fixes land.

Deferred (not in scope here, file follow-ups if desired): QuizView/ReviewView clone
consolidation, TypographyPanel OptionGroup extraction, GlossaryQuiz tray
componentization, a11y nits (`javascript:history.back()` links, `aria-pressed`,
tray focus management), module-scope signal state.

## Acceptance criteria

- [ ] Every finding above is either verified-and-fixed or marked invalid with a note
- [ ] `preact_page.py` deleted; `quick-check.py` uses `page_template` (page-shell.js +
      typography-prefs.js present in generated quick-check HTML, title escaped)
- [ ] Breadcrumbs and asset URLs render correctly for depth-2 lessons
      (`lessons/{domain-slug}/NN-slug.html`) — verified by generating a test page
- [ ] MapView measurement no longer uses unescaped `innerHTML` with topic data
- [ ] TopicCard buttons wired to real behavior or removed
- [ ] LessonActions surfaces POST failure (no silent fake success)
- [ ] GenButton uses a signal effect (no unbounded `setInterval`)
- [ ] `.rating-*`, `.assess-buttons`, `.gen-progress` classes have visible styling
      (hover + click feedback)
- [ ] Dead code removed: GenerationModal, ProgressiveReveal.js, duplicate `next()`,
      dead `lesson_id` param
- [ ] Scaffolds contain no duplicated import map; lesson scaffold shows the
      `data-file` code-block pattern
- [ ] Godot artifact hygiene decided (gitignore or committed) for addons/, .godot/, *.uid
- [ ] `mise run verify` passes; spot-check a generated page in the browser
