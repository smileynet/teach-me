---
id: "236"
title: "Runtime-validate shipped lesson 05/06 story_player.gd (back-fill)"
type: bug
status: open
priority: high
blocked_by: ["235"]
tags: ["ink", "validation"]
---

# Runtime-validate shipped lesson 05/06 story_player.gd (back-fill)

## Why

#211 and #212 were closed with `story_player.gd` validated only by API matching,
not by running it in Godot. This back-fills the real runtime validation using the
harness from #235, and fixes any defect it surfaces. These are DOWNLOADABLE files
learners run, so a runtime bug is a genuine defect.

## Scope

Two files:
- `examples/ink-godot/reference/code/godot-ink-integration/story_player.gd` (L05)
- `examples/ink-godot/reference/code/tags-as-commands/story_player.gd` (L06)

## What to do

1. Run both through the #235 harness (Layer 1 import + Layer 2 headless playthrough).
2. **Specifically confirm the assumptions I did NOT runtime-check:**
   - `String.split(":", false, 1)` maxsplit behaviour in GDScript 4 (L06 tag parse).
   - `var value = parts[1].strip_edges() if parts.size() > 1 else ""` ternary (L06).
   - `current_choices[i].text` resolves on the inkgd GDScript runtime (both).
   - `loaded` signal fires after `call_deferred("_create_story")` (both).
   - L06 single-step `while can_continue: continue_story()` yields per-line
     `current_tags` (the whole reason L06 changed the loop) — assert a mid-story
     line's tag is seen, not just the last line's.
3. If a defect is found: fix the file, re-run the reference `.ink` golden transcript
   (unchanged story ⇒ transcript should still match), re-run check-lesson, and
   ensure the lesson HTML's `data-mode="complete"` block stays byte-identical to the
   fixed downloadable (the contract).
4. Update #211/#212 resolution notes with the runtime-validation evidence (or a
   short correction if a bug was shipped).

## Acceptance criteria

- [ ] L05 story_player.gd: headless import parses + playthrough reaches END, text accumulates
- [ ] L06 story_player.gd: headless import parses + playthrough reaches END, speaker label set, `# hidden` line suppressed, mid-story tag observed
- [ ] The 4 assumption checks above each confirmed or fixed
- [ ] Any fix mirrored into the lesson HTML complete-block (contract preserved) + golden transcript re-verified
- [ ] #211 and #212 resolution notes updated with real runtime evidence


## FINDING (2026-08-27, via #235 harness) — L05 has a real runtime bug

The #235 harness caught it: **lesson 05 `story_player.gd` reads `_ink_player.current_text`
after `continue_story_maximally()`, but inkgd's `current_text` returns only the LAST line
of a multi-line passage — not the full concatenated text.**

Evidence (headless diagnostic, inkgd 4.7.1):
- Story 05's `start` knot emits "You stand at the mouth of a cave..." then `-> entrance`
  emits the lit/unlit line, all in one maximal continue.
- The player's label showed ONLY "The passage ahead is pitch black." — the `start`
  narration was dropped.
- Confirmed at the addon level: `continue_story_maximally()` (ink_player.gd:415) loops the
  underlying `Continue()`, and `current_text` (ink_player.gd:189) returns
  `_story.current_text` = only the most recent single Continue()'s output.

Why the golden transcript looked fine: `play-ink.py` captures the RETURN VALUE of each
continue (full text), not the `current_text` property — so bink-level output was correct
while the Godot player silently dropped lines.

**Fix options (decide during #236):**
1. Use the RETURN VALUE of `continue_story_maximally()` (it returns the full text) instead
   of reading the `current_text` property. Minimal change, keeps maximal continue.
2. Switch L05 to the single-step `while can_continue: continue_story()` loop (what L06
   already does) and accumulate each line. More consistent across lessons.

Recommend option 2 for consistency (L06 already steps line-by-line), OR option 1 for a
minimal L05-only fix. Either way: fix the reference file, mirror into the lesson HTML
complete-block, re-verify golden transcript (unchanged story), re-run the #235 harness to
green. NOTE: the spike (spike_story.gd) has the same pattern — worth fixing too or noting.

L06 PASSED all harness checks (speaker set, # hidden suppressed, reached ending) — its
single-step loop is correct. This asymmetry is itself evidence option 2 is right.
