---
id: "168"
title: "Tool: extract final-state code files from lessons for download"
status: open
blocked_by: []
---

# Tool: extract final-state code files from lessons for download

## Context

Lessons like "Toon Banding" name specific files (`toon_smoothstep.gdshader`, `toon_bands.gdshader`, `toon_ramp.gdshader`) and build them up across code blocks — sometimes starting from a base, showing diffs, then adding shadow color tinting. A reader following along must mentally merge all the blocks to reconstruct the final state.

We should extract the "end-of-lesson" version of each named file and provide them as downloadable reference files. This serves two purposes:
1. Learners can compare their work against the correct final state
2. Learners who skip ahead can grab the files and catch up

## What to build

### 1. `tools/extract-lesson-code.py` — code file extractor

A script that:
- Parses a lesson HTML file
- Identifies all named code files (detected from phrases like "Create a new file `filename.ext`", "Modify your `filename.ext`", or explicit `data-file="filename"` attributes on `<pre>` blocks)
- Tracks the evolution of each file across code blocks (applying diffs where marked)
- Outputs the final state of each file to `reference/{domain-slug}/code/{lesson-slug}/`

**Detection heuristics (ordered by reliability):**
1. `<pre data-file="toon_bands.gdshader">` — explicit attribute (preferred, add to generation convention)
2. Preceding paragraph contains "Create a new file `X`" or "Modify your `X`" — filename extraction via regex
3. `shader_type spatial;` as first line → infer `.gdshader` extension; `extends Node` → `.gd`; etc.

**Diff resolution:**
- If a code block uses diff markers (red/green spans from ticket #157), apply the diff to the previous version of that file
- If a code block is a full replacement (no diff markers), it becomes the new canonical state
- If a code block is a snippet (no `shader_type` or file header), append to a "fragments" list (not exported as standalone)

**Output format:**
```
reference/{domain-slug}/code/{lesson-slug}/
  toon_smoothstep.gdshader
  toon_bands.gdshader
  toon_ramp.gdshader
  README.md              — lists each file with a one-line description
```

### 2. `data-file` attribute convention

Update lesson generation to tag code blocks with the target filename:

```html
<pre data-file="toon_bands.gdshader"><code>shader_type spatial;
...
</code></pre>
```

This makes extraction deterministic instead of relying on heuristic paragraph scanning.

### 3. Mise task

```toml
[tasks."code:extract"]
run = "python tools/extract-lesson-code.py"
description = "Extract final-state code files from a lesson"

# Usage:
# mise run code:extract -- lessons/godot-toon-shaders/02-toon-banding.html
# mise run code:extract -- --workspace examples/godot-gamedev --all
```

### 4. Download link in lesson page

Add a "Download code files" link in the `.next-steps` section at the bottom of each lesson (or in the breadcrumb/nav area). Points to the `reference/{domain}/code/{lesson}/` directory.

The page-shell.js can detect whether the code directory exists (relative link check) and show/hide the download link dynamically — or the generate-topic pipeline always creates it.

### 5. Integration with generate-topic pipeline

Add as a Phase 3 post-process step:
1. After lesson generation, run `extract-lesson-code.py` on the new lesson
2. Output goes to `reference/{domain-slug}/code/{lesson-slug}/`
3. Verify: each extracted file is syntactically valid (for shaders: check `shader_type` is present; for GDScript: check `extends` is present)

## Design decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Final state only, or per-section snapshots? | **Final state only** (with bonus section noted) | Simpler output, covers 90% use case. Version history is in the lesson itself. |
| One file per code block, or merged? | **Merged by filename** | A file mentioned in 3 blocks (base → diff → addition) produces ONE output file in its final form |
| Where do files live? | `reference/{domain}/code/{lesson-slug}/` | Parallel to existing reference docs, clearly a companion to the lesson |
| What about "bonus" sections? | **Separate sub-directory** | `reference/{domain}/code/{lesson-slug}/bonus/` for optional extensions (like shadow color tinting that modifies any of the three approaches) |
| Include a README? | **Yes** | Lists each file with description and which lesson section produced it |

## Acceptance criteria

- [ ] `tools/extract-lesson-code.py` exists and extracts named files from a lesson HTML
- [ ] Handles both full code blocks and diff-style blocks
- [ ] Outputs to `reference/{domain}/code/{lesson-slug}/` with correct final-state content
- [ ] Generates a README.md listing each file with description
- [ ] `data-file` attribute convention documented in visual-teaching.md or AGENTS.md
- [ ] `mise run code:extract` works for single lessons and `--all`
- [ ] Extracted .gdshader files contain valid `shader_type` declarations
- [ ] Integrated into generate-topic Phase 3 (post-process)
