---
id: "236"
title: "Runtime-validate shipped lesson 05/06 story_player.gd (back-fill)"
type: bug
status: done
priority: high
blocked_by: ["235", "238"]
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

- [x] L05 story_player.gd: headless import parses + playthrough reaches END, text accumulates
- [x] L06 story_player.gd: headless import parses + playthrough reaches END, speaker label set, `# hidden` line suppressed, mid-story tag observed
- [x] The 4 assumption checks above each confirmed or fixed
- [x] Any fix mirrored into the lesson HTML complete-block (contract preserved) + golden transcript re-verified
- [x] #211 and #212 resolution notes updated with real runtime evidence


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


## Decision (2026-08-28) — fix via Option 1 (use the return value), NOT the loop switch

L05's fix: keep `continue_story_maximally()` but read its RETURN VALUE (which is the
full concatenated text) instead of the `current_text` property (last line only).

Rationale: the bug is reading the wrong thing (property vs return value), not the
choice of continue method. Option 1 is the minimal, honest fix AND preserves the
teaching progression — lesson 05 stays "maximal continue is the simple default,"
and lesson 06's pivot ("now switch to single-step BECAUSE tags need per-line
granularity") keeps its punch. Switching L05 to single-step (Option 2) would
retroactively spoil lesson 06's central beat.

Concretely in `_advance_story`:
```
var text = _ink_player.continue_story_maximally()   # RETURN value = full text
if text.strip_edges() != "":
    _text_label.text += text
```
(drop the separate `current_text` read).

Also fix `spike_story.gd` (same latent bug; it's a spike, note not a lesson deliverable).

Blocked-by #238 (harden the harness first) so the fix is validated by a trustworthy
harness, not the thin one.


## CORRECTION (2026-08-28) — Option 1 is WRONG; the fix is Option 2 (single-step loop)

Research (`.scratch/research/inkgd-text-idiom.md`, verified against inkgd 0.6.0 source)
OVERTURNS the earlier Option-1 decision. The scope review had ASSUMED
`InkPlayer.continue_story_maximally()` returns the full concatenated text. The source
proves otherwise:

- inkle C# `Story` + inkgd raw `InkStory`: return value = full concat, `current_text` = last line. (premise true here)
- **inkgd `InkPlayer` wrapper (what EVERY lesson uses via InkPlayerFactory.create()): `continue_story_maximally()` DISCARDS the story's concatenated return and does `text = self.current_text` → BOTH the return value AND the property give only the LAST line.**

→ Reading the return value (Option 1) does NOT fix the bug. There is no way to get full
passage text from one maximal call through the InkPlayer API. **The only correct fix is
the manual single-step accumulate loop** — exactly what Lesson 06 already does:
```gdscript
func _advance_story():
    while _ink_player.can_continue:
        var text = _ink_player.continue_story()   # one line; return == property here
        if text != "":
            _text_label.text += text + "\n"
    if _ink_player.has_choices:
        _show_choices()
    elif not _ink_player.can_continue:
        _on_ended()
```

### Pedagogical rethink (the Option-2 objection was based on the false premise)
"Option 2 spoils L06's pivot" assumed maximal-continue WORKS for display in L05. It
doesn't. Corrected arc — actually cleaner:
- L05 teaches the single-step accumulate loop as the correct display baseline + the
  maximal-continue-last-line GOTCHA (the real bug, now a teachable point).
- L06's pivot reframes from "switch to single-step for tags" → "you already step
  line-by-line; now read each line's tags in that same loop." Lighter, better progression.
- ig-06-002 already teaches "maximal collapses per-line data to last line" (for tags) —
  corrected L05 aligns both lessons on one truth.

### Revised change set (canonical fix confirmed by dialogue-display research: accumulate the loop)
1. _advance_story → single-step accumulate loop in: reference .gd (SoT), HTML complete-block
   (4-SPACE indent), spike_story.gd (TABS). 4th site lesson05_player.gd auto-regenerates via ink-gd-sync.py.
2. Rewrite L05 prose: walkthrough "fills current_text", glossary continue-maximally
   "accumulating into current_text" clause, the "New concept" note, SVG "read current_text"
   label (line 115) → reframe around single-step loop + maximal-last-line gotcha.
3. Reframe L06 pivot sentence (mechanism unchanged; only the "why now").
4. Update SR ig-05-003 (step "read current_text and display it" → read each line in the loop).
5. Exercise UNCHANGED (teaches async timing, still correct). Golden transcript UNCHANGED (story untouched).
6. #211 resolution note: shipped-bug-then-fixed correction.

### Re-validation
`mise run ink:validate-gd` → L05 GREEN (payoff); `ink:transcripts` unchanged; check-lesson
0005 contract holds; ink:validate/ink:play sanity. Newline gotcha: single-step `+= line + "\n"`
may double blank lines vs maximal — verify visible output in the harness.

## Resolution (2026-08-28)

L05 _advance_story switched to single-step 'while can_continue: continue_story()' accumulate loop across reference .gd + HTML complete-block + spike; L05 prose/glossary/SVG reframed around the loop + maximal-last-line gotcha; L06 pivot reframed to reuse L05's loop; SR ig-05-003 updated; #211 resolution corrected. Harness (which caught the bug) now green.
