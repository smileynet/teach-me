---
name: lesson-validation
description: "Validate a lesson against all quality guidelines — code block metadata, narrative framing, downloadable files, SVG theming, accessibility, glossary coverage. Dispatchable as a subagent for independent review. Trigger: validate lesson, check lesson, lesson compliance, review lesson quality."
metadata:
  type: process
  invocation: both
  practice: null
---

# Lesson Validation

Run a comprehensive compliance check on one or more lesson pages against all teach-me quality guidelines. Designed to be dispatched as a subagent for independent review — no context from the generation session needed.

## When to use

- After generating a lesson (Phase 4 verify in generate-topic)
- Before marking a topic complete
- Periodic audits of existing lessons
- When reviewing adopted/imported lessons (like proto lessons from other projects)
- When guidance changes and existing lessons need re-validation

## Input

- A lesson HTML file path (or `--all` for every lesson in a workspace)
- The workspace path (for locating reference/code directories, MAP.md, glossary)

## Checks (ordered by severity)

### Gate checks (MUST pass — blocks completion)

| # | Check | What to verify | How |
|---|-------|---------------|-----|
| G1 | **Page renders** | HTTP 200, no failed resource loads (CSS, JS) | Playwright: load page, check `requestfailed` events |
| G2 | **Template compliance** | Has DOCTYPE, style.css link, page-shell.js, breadcrumb nav, import map | Parse HTML for required elements |
| G3 | **Code files exist** | Every `<pre data-file="X">` has a corresponding `reference/code/{slug}/X` | Scan data-file attrs, check filesystem |
| G4 | **SVG uses CSS vars** | No hardcoded hex in inline SVGs | `tools/check-svg-vars.py` or regex scan for `#[0-9a-f]{3,6}` inside `<svg>` |
| G5 | **Links valid** | Internal links resolve, external links return 2xx | `mise run verify` or manual link check |

### Quality checks (SHOULD pass — report but don't block)

| # | Check | What to verify | How |
|---|-------|---------------|-----|
| Q1 | **Narrative framing** | No `<pre>` immediately after an `<h2>`/`<h3>` with no prose between | Scan DOM: if a code block's previous sibling is a heading, flag it |
| Q2 | **Code block metadata** | `<pre>` blocks that look like named files have `data-file` attr | Heuristic: contains `shader_type`, `extends`, `import`, or `fn main` → should have data-file |
| Q3 | **Diff blocks marked** | Blocks with `<span style="color:var(--error)">` or `var(--success)` have `data-mode="diff"` | Scan for colored spans inside `<pre>` without data-mode |
| Q4 | **Fragment blocks marked** | One-liner code blocks or blocks without file headers have `data-mode="fragment"` | Heuristic: <3 lines + no file-type header → likely fragment |
| Q5 | **Glossary coverage** | Domain terms in the lesson text are in the glossary-data island | Compare technical terms against glossary JSON |
| Q6 | **Key concept block** | Lesson has `.key-concept` div | DOM check |
| Q7 | **Exercise tests core concept** | Exercise exists with hint+answer AND tests the lesson's Win statement (not a peripheral gotcha) | Check for details/summary + compare exercise topic to lesson Win/key-concept |
| Q8 | **Read more links** | New concepts introduced have links to official docs | Scan `.note` blocks with "New concept" for presence of `<a href>` |
| Q9 | **Accessibility** | SVGs have `role="img"` + `<title>`, images have alt text | DOM scan |
| Q10 | **Dark/light rendering** | Page renders correctly in both themes | Playwright: toggle theme, check body BG + text color are distinct |

### Expansion checks (INFORMATIONAL — suggest improvements)

| # | Check | What to verify |
|---|-------|---------------|
| E1 | **Subtopic detection** | Glossary terms not covered by MAP topics → suggest expansion opportunities |
| E2 | **Cross-reference opportunities** | Concepts mentioned that have existing lessons → suggest links |
| E3 | **SR question coverage** | Does the lesson have corresponding questions in the JSONL? |

## Output format

```
=== Lesson Validation: {filename} ===

GATE CHECKS:
  [PASS] G1 Page renders (200, 0 failed resources)
  [PASS] G2 Template compliance (all required elements present)
  [FAIL] G3 Code files: missing reference/code/toon-banding/toon_smoothstep.gdshader
  [PASS] G4 SVG vars (0 hardcoded hex)
  [PASS] G5 Links valid (12/12)

QUALITY CHECKS:
  [PASS] Q1 Narrative framing (no bare code blocks after headings)
  [WARN] Q2 Code block metadata: 1 block without data-file (line 288)
  [PASS] Q3 Diff blocks marked
  ...

EXPANSION:
  [INFO] E1 "GradientTexture1D" not in MAP — consider expansion topic

RESULT: 4/5 gates pass, 1 FAIL (G3). NOT READY for completion.
```

## Dispatch pattern

This skill is designed to be called as a subagent:

```
Dispatch: lesson-validation
  Role: kiro_default
  Prompt: "Validate the lesson at {path}. Workspace is at {workspace}. 
           Read the lesson HTML, run all gate and quality checks, report results.
           Read D:/code/teach-me/.kiro/skills/lesson-validation/SKILL.md for the full checklist."
```

The subagent reads the lesson file, runs checks via tool calls (file reads, Playwright if available, grep patterns), and reports structured results. No generation context needed — it works from the artifact alone.

## Does NOT

- Fix issues (report only — the caller decides what to address)
- Require Playwright (degrades gracefully: skips G1/Q10 if no browser available)
- Block on quality checks (only gate checks block completion)
- Need to know how the lesson was generated (works on any HTML file)
- Replace `check-topic-completeness.py` (that checks artifact existence; this checks quality)

## Integration with generate-topic

In Phase 4 (Verify), dispatch this skill as one of the parallel subagents:

```
| Agent | Role | Gate |
|-------|------|------|
| lesson-validation | Validate all checks | Gate checks MUST pass |
| Link + lint check | `mise run verify` | MUST pass |
| Structural compliance | `check-topic-completeness.py` | MUST pass |
```

This replaces the ad-hoc "visual check" subagent with a structured, repeatable validation.
