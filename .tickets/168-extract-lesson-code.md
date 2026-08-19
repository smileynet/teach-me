---
id: "168"
title: "Tool: extract final-state code files from lessons for download"
status: open
blocked_by: []
parent: "173"
---

# Tool: extract final-state code files from lessons for download

## Context

Lessons like "Toon Banding" name specific files (`toon_smoothstep.gdshader`, `toon_bands.gdshader`, `toon_ramp.gdshader`) and build them up across code blocks — sometimes starting from a base, showing diffs, then adding shadow color tinting. A reader following along must mentally merge all the blocks to reconstruct the final state.

We should extract the "end-of-lesson" version of each named file and provide them as downloadable reference files. This serves two purposes:
1. Learners can compare their work against the correct final state
2. Learners who skip ahead can grab the files and catch up

## Research Findings

Prior art falls into three categories:
- **Literate programming tanglers** (mdweb, lmt, lima): named blocks → files at build time. Use `file=` metadata. Multiple blocks append to same target.
- **Documentation platforms** (Docusaurus, Quarto, mdBook): offer copy buttons and `title`/`filename` display metadata, but no download-as-file. Docusaurus has an open feature request (#8457) for this exact thing — unimplemented.
- **Sandbox-per-step** (React docs + StackBlitz): full project snapshots at each tutorial step. Heavy infrastructure, doesn't fit teach-me's local-first model.

**Gap teach-me fills:** No mainstream tool assembles multiple incremental HTML code blocks into a downloadable final-state file. The literate programming tanglers work on markdown source; we work on rendered HTML with diff-style spans.

**Key decisions from research:**
- Build-time extraction (at generation, not in browser) — simpler, works offline, no JS assembly logic
- BeautifulSoup + lxml for HTML parsing — best API for structured extraction with data attributes
- Custom diff applier (~50 lines) — our `var(--success)`/`var(--error)` span format is non-standard
- "Last complete block wins" model over append model — clearer semantics for lessons that show evolution

## What to build

### 1. `tools/extract-lesson-code.py` — code file extractor

**Parser approach:** BeautifulSoup with lxml backend.

```python
# Pseudocode for the extraction logic
for pre in soup.select('pre[data-file]'):
    filename = pre['data-file']
    code_el = pre.find('code')
    
    # Classify block type
    has_diff_spans = code_el.find('span', style=re.compile('--error|--success'))
    
    if has_diff_spans:
        # Extract diff: green lines are additions, red are removals, plain is context
        apply_diff(file_state[filename], parse_diff(code_el))
    else:
        # Complete replacement — this becomes the new canonical state
        file_state[filename] = code_el.get_text()
```

**Detection (priority order):**
1. `data-file="filename.ext"` attribute on `<pre>` — **preferred, deterministic**
2. Preceding paragraph matching `Create.*file.*\`([^`]+)\`` — regex fallback
3. First-line heuristic (`shader_type spatial;` → `.gdshader`)

**Diff resolution:** Custom ~50-line applier that:
- Iterates child elements of `<code>`
- Classifies each line by its parent span's `style` attribute (`--error` = remove, `--success` = add, no span = context)
- Applies additions/removals to the current file state using context lines as anchors
- Falls back to `difflib.SequenceMatcher` fuzzy matching if exact context doesn't match

**Output:**
```
reference/{domain-slug}/code/{lesson-slug}/
  toon_smoothstep.gdshader
  toon_bands.gdshader
  toon_ramp.gdshader
  README.md              — lists each file + which section produced it
```

### 2. `data-file` attribute convention

Tag `<pre>` blocks with target filename during lesson generation:

```html
<pre data-file="toon_bands.gdshader"><code>shader_type spatial;
...</code></pre>
```

For diff blocks (ticket #157 format):
```html
<pre data-file="toon_test.gdshader" data-mode="diff"><code>
 // context
<span style="color:var(--error)">-old line</span>
<span style="color:var(--success)">+new line</span>
</code></pre>
```

`data-mode` values:
- `complete` (default) — this block is the full file content
- `diff` — apply as a patch to the current state of this file
- `fragment` — a snippet for illustration, not a complete file (skip extraction)

### 3. Pipeline integration (end of Phase 2)

After lesson + reference + SR + quiz are written:
```
Phase 2, Step 2.5: Extract code files
  - Run extract-lesson-code.py on the new lesson
  - Output to reference/{domain-slug}/code/{lesson-slug}/
  - Validate: each extracted file has basic structure (shader_type for .gdshader, etc.)
```

Fast and deterministic — no subagent needed. Sequential at end of Phase 2, before Phase 3 post-processing.

### 4. Completeness check

Add to `check-topic-completeness.py`:
- Only applies if lesson has `<pre data-file=...>` blocks
- Verifies `code/{lesson-slug}/` directory exists with matching filenames
- Non-blocking for conceptual lessons without code

### 5. UI surfacing (three access paths)

**A. Lesson bottom bar** — extend `LessonActions.js` with conditional "Code files" button (HEAD request to check if code dir exists, same pattern as quiz button).

**B. Reference doc** — include "Code Files" section in reference page body with per-file download links.

**C. Per-block download** (optional, future) — `CodeBlockActions.js` component that adds copy+download to `<pre data-file>` blocks.

### 6. Mise task

```toml
[tasks."code:extract"]
run = "python tools/extract-lesson-code.py"
description = "Extract final-state code files from lesson(s)"

# Usage:
# mise run code:extract -- lessons/godot-toon-shaders/02-toon-banding.html
# mise run code:extract -- --workspace examples/godot-gamedev --all
```

## Design decisions

| Decision | Choice | Rationale | Prior art |
|----------|--------|-----------|-----------|
| Build-time vs client-side? | **Build-time** | Simpler, works offline, no JS assembly logic | Literate tanglers (mdweb, lmt) |
| Append vs replace model? | **Last complete block wins** (with diff apply for `data-mode="diff"`) | Lessons show evolution — final block is canonical | React docs (full snapshot per step) |
| Output format? | **Raw source files + README** | Not HTML. Files are directly usable. | mdBook companion code |
| Naming source? | **`data-file` attribute** (with heuristic fallback) | Deterministic > heuristic | Docusaurus `title=`, mdweb `file=` |
| Fragment handling? | **`data-mode="fragment"` skips extraction** | Not every code block is a complete file | Quarto `echo: false` |
| Directory structure? | **`reference/{domain}/code/{lesson-slug}/`** | Parallel to existing reference docs | Standard companion code pattern |
| Bonus/optional code? | **`bonus/` subdirectory** | Optional extensions don't confuse the main output | - |

## Acceptance criteria

- [ ] `tools/extract-lesson-code.py` exists and extracts named files from lesson HTML
- [ ] Handles both full code blocks (`data-mode="complete"`) and diff blocks (`data-mode="diff"`)
- [ ] Correctly strips `<span>` styling from diff blocks to produce clean source
- [ ] Outputs to `reference/{domain}/code/{lesson-slug}/` with correct final-state content
- [ ] Generates a README.md listing each file with description and source section
- [ ] `data-file` attribute convention documented in visual-teaching.md
- [ ] `mise run code:extract` works for single lessons and `--all`
- [ ] Extracted files are syntactically valid (basic structure checks)
- [ ] Integrated into generate-topic Phase 2, Step 2.5
- [ ] `check-topic-completeness.py` gates on code extraction when applicable
- [ ] LessonActions.js shows conditional "Code files" button
