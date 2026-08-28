---
id: "242"
title: "check-lesson.py: enforce image-link existence + data-mode=complete byte-match"
status: backlog
blocked_by: []
priority: medium
tags: ["platform"]
---

# check-lesson.py: enforce image-link existence + data-mode=complete byte-match

## Why

During #219 an independent audit found two lesson-quality issues that `check-lesson.py`
does not catch, both invisible to the current checks:

1. **No image-link existence check.** A lesson can reference `<img src="...">` paths
   that 404 and check-lesson passes. (`verify-links.py` covers this project-wide, but
   check-lesson — the per-lesson gate — does not, so a single-lesson check gives false
   confidence.)
2. **No `data-mode="complete"` byte-match.** The steering contract says a `complete`
   block == the fully-assembled downloadable file. #219 shipped a simplified block
   mislabeled `complete`; check-lesson's CF check only verifies a download link exists,
   not that a `complete` block matches the file it names. (Fixed in #219 by relabeling
   to `fragment`, but the check should enforce the contract.)

## What to do

Add two checks to `tools/check-lesson.py`:
- **Image links:** for every `<img src>` in the lesson, resolve the path (accounting for
  the project-root `/assets` mount — `../../assets/...` → project-root `assets/...`) and
  assert the file exists. FAIL on a missing image.
- **complete-mode match:** for every `<pre data-file="X" data-mode="complete">`, load
  `reference/code/{slug}/X` and assert the block body matches the file (allow leading/
  trailing whitespace normalization). FAIL on mismatch, with a hint to use `fragment` if
  the in-page block is intentionally simplified.

Reuse `verify-links.py`'s path-resolution logic for the `/assets` mount rather than
reinventing it. Do not duplicate the whole link checker — just the img-existence slice.

## Acceptance criteria

- [ ] check-lesson FAILs when a lesson references a non-existent image (respecting the /assets mount)
- [ ] check-lesson FAILs when a `data-mode="complete"` block does not match its `data-file` on disk
- [ ] `fragment` blocks are exempt from the byte-match check
- [ ] Existing lessons (0016, 0017, godot-gamedev) still pass check-lesson after the new checks
- [ ] Hint message tells authors to use `fragment` for intentionally-simplified in-page blocks
