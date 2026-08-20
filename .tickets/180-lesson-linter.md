---
id: "180"
title: "Mechanical lesson linter — enforce conventions via script"
status: in_progress
priority: high
blocked_by: []
---

# Mechanical lesson linter — enforce conventions via script

## Context

The generate-topic pipeline has 18+ enforceable conventions that agents must remember and apply manually. Research (2026-08-20) classified each rule as MECHANICAL (scriptable), SEMI-MECHANICAL (detect but can't auto-fix), or CREATIVE (irreducibly AI). 8 high-value mechanical checks have no script coverage today.

The quality bottleneck isn't the creative writing — it's the compliance surrounding it. A single linter command that catches format/structural violations means the agent only needs to get the content right.

## What to build

`tools/check-lesson.py` — comprehensive lesson linter with check IDs matching the lesson-validation skill.

```bash
python tools/check-lesson.py --workspace examples/godot-gamedev --lesson lessons/0005-triplanar-mapping.html
python tools/check-lesson.py --workspace examples/godot-gamedev --all
```

### Checks to implement (priority order):

| ID | Check | Detection |
|----|-------|-----------|
| G2 | Template compliance | DOCTYPE, style.css, page-shell.js, breadcrumb nav, importmap present |
| G3 | Code files contract | Every `data-file` attr has a file at `reference/code/{slug}/` |
| Q1 | Narrative framing | No `<pre>` immediately after `</h2>` or `</h3>` without intervening `<p>` |
| Q3 | Diff blocks marked | `<pre>` with `var(--error)` or `var(--success)` spans has `data-mode="diff"` |
| Q6 | Key concept block | `.key-concept` div exists |
| Q9 | SVG accessibility | Every `<svg>` has `role="img"` + `<title>` child |
| Q11 | Nav chain | Previous lesson links forward to this one |
| CF | Code Files section | If `data-file` blocks exist, lesson has a "Code Files" `<h2>` with download links |

### Output format:

```
=== check-lesson: 0005-triplanar-mapping.html ===
PASS G2  Template compliance
PASS G3  Code files (1/1 data-file blocks have reference files)
FAIL Q1  Narrative: <pre> at line 45 follows heading with no prose between
WARN Q3  Diff block at line 88: colored spans without data-mode="diff"
PASS Q6  Key concept block present
PASS Q9  SVG accessibility (1/1 SVGs have role+title)
SKIP Q11 No prerequisite lesson found
PASS CF  Code Files section present with download links

Result: 6 pass, 1 fail, 1 warn, 1 skip
```

### Interface:

- Exit 0: all pass
- Exit 1: any FAIL
- Exit 2: script error
- `--json` flag: structured output for tooling
- `--checks G2,Q1,Q3` flag: run subset

## Acceptance criteria

- [ ] `tools/check-lesson.py` exists and runs on a single lesson file
- [ ] `--all` flag checks every lesson in the workspace
- [ ] G2 detects missing template elements
- [ ] G3 detects data-file blocks without corresponding reference files
- [ ] Q1 detects bare code blocks after headings
- [ ] Q3 detects unmarked diff blocks
- [ ] Q6 detects missing key-concept
- [ ] Q9 detects SVGs without accessibility attributes
- [ ] Q11 detects broken forward navigation chain
- [ ] CF detects missing Code Files section when data-file blocks exist
- [ ] Exit codes are correct (0/1/2)
- [ ] Runs on all 3 toon shader lessons with correct results
