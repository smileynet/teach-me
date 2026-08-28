---
id: "251"
title: "inkgd version provenance + deepen harness (pin bug signature, verify render, review prose)"
type: bug
status: in_progress
priority: high
blocked_by: []
tags: ["ink", "validation", "tooling"]
---

# inkgd version provenance + deepen harness

Two threads, same surface (the ink GDScript validation). Filed after #236 shipped.

## Version status (checked 2026-08-28, GitHub API)
- **inklecate: 1.2.1 = current latest release.** Pinned in mise.lock. NO action.
- **inkgd: vendored 0.6.0 = an UNRELEASED `godot4`-branch build** (latest tagged release is
  0.5.0; main targets Godot 3). Deliberate — no official Godot-4 inkgd release exists. But we
  have NO record of which `godot4` commit our snapshot came from, so "is it current?" is
  currently unanswerable.

## Version hygiene
1. **Record inkgd snapshot provenance** — capture the `godot4` source commit SHA + date
   (ADDONS.md or .memory note or plugin.cfg comment) so the baseline is known and diffable.
2. **Diff our 0.6.0 vs `godot4` HEAD** — specifically `ink_player.gd`
   continue_story_maximally()/current_text. The L05 bug's root cause was InkPlayer returning
   only the last line; check whether upstream fixed it. VALIDATION not a change — just know the
   delta. If upstream fixed it, revisit the L05 "maximal-last-line gotcha" framing.
3. **Do NOT blind-upgrade inkgd** — unreleased branch; an upgrade needs full harness +
   golden-transcript re-validation. Stay on validated 0.6.0 unless (2) shows a relevant fix;
   document the decision (ADR).

## Harness depth (validation debt on #236, admitted in self-audit)
4. **Pin the bug's signature** — L05 harness asserts the ENDING substring ("carved stairway"),
   NOT the opening narration the bug dropped. Add `assert "You stand at the mouth" in
   text_label.text` so a regression of THIS exact bug fails, not just any END-miss.
5. **Verify rendered output** — dump text_label.text (or screenshot) to confirm the single-step
   `+= line + "\n"` loop doesn't double blank lines (research-flagged gotcha, never eyeballed).
6. **Review rewritten prose** — dispatch a fresh reviewer for L05 (walkthrough, continue-maximally
   glossary, gotcha note, SVG labels) + L06 pivot. check-lesson only confirms structure, not that
   the reworded explanations are correct/clear.

## Findings (2026-08-28 — research + review subagents; see .scratch/subagent-raw/251-findings.md)

- **Provenance resolved by review.** Vendored `ink_player.gd` is **byte-identical** to the
  `.references/inkgd` `godot4` HEAD — SHA-256 `f8a79d3f…f96ac` on both, and
  `git diff --stat godot4 -- addons/inkgd/ink_player.gd` is empty.
  - Snapshot commit: **`fea9098ee18d6cdbe9a5e25f8f0296bcdf0fd96a`** (godot4 HEAD,
    "Re-enable inkgd plugin", 2024-01-28). `ink_player.gd` itself last changed at
    `88441d6` (2024-01-25); two later godot4 commits don't touch it.
  - Upstream repo: `https://github.com/ephread/inkgd.git`, branch `godot4`.
- **AC2 diff verdict: NO DELTA.** Upstream did NOT fix the maximal-continue last-line behavior —
  our snapshot equals branch HEAD. The bug is in the InkPlayer WRAPPER (`ink_player.gd:415-430`,
  line 424 `text = self.current_text` = last line only), NOT the underlying
  `Story.continue_story_maximally()` (`runtime/ink_story.gd:482` concatenates correctly). So it's
  upstream-inherited, not a vendoring artifact; the L05 gotcha framing stands.
- **AC3 decision: STAY on `fea9098`** — nothing to upgrade to (snapshot == HEAD). Recorded in ADR 0013.
- **Recording mechanism (best practice, Firefox moz.yaml pattern):** pin the FULL 40-char SHA (not
  the branch name) in a committed sidecar manifest next to the vendored code; add an inkgd entry to
  REFERENCES.md. Drift check: `git ls-remote https://github.com/ephread/inkgd.git refs/heads/godot4`.
- **AC6 prose: PASS.** Fresh reviewer traced every L05/L06 explanation to source — all literally
  accurate (wrapper returns last line; underlying Story concatenates; current_tags overwritten the
  same way); SVGs carry no maximal-continue implication. Two non-blocking cosmetic items only
  (L05 print-based single-line smoke tests precede the gotcha in reading order).
- **Env:** Godot 4.7.1 on PATH — harness (AC4/5/7) is runnable on this machine.
- **AC4 method:** add the opening-line assert, then MUTATION-VERIFY (revert player to maximal-continue
  → harness must go RED → restore → GREEN), using the 3-separate-calls mutate/run/restore pattern.

## AC5 finding (2026-08-28) — newline doubling IS present (real defect, not clean)

Render dump of L05 `text_label.text` (¶ = `\n`):
`You stand at the mouth of a cave...dark.¶¶A torch bracket juts...¶¶The passage ahead is pitch black.¶¶...`

Every line is separated by **two** newlines, with one `¶¶¶¶` (quad) at a passage boundary. Root cause:
inkgd's `continue_story()` returns `current_text`, which **already includes the line's trailing `\n`**
(ink's line representation). The shipped loop then appends **another** `+ "\n"`, so every line
double-spaces. Confirmed against `ink_player.gd:366-380` (continue_story returns current_text) and the
ink source (consecutive same-passage lines render double-spaced, which is wrong).

**Fix scope (needs decision — touches shipped teaching content):** the `_text_label.text += text + "\n"`
pattern appears in BOTH lessons' players + HTML + READMEs + harness copies + spike (11 occurrences via
grep). Correct fix: append `text` alone (ink already terminates the line). This is a content change to
lessons 05 AND 06, beyond "pin the bug signature." Golden transcripts unaffected (bink captures the
continue return value, not the Godot render). Options: (a) fix all now under #251, (b) split to a new
bug ticket. Pending user call.

## Acceptance criteria
- [x] inkgd `godot4` snapshot commit SHA + date recorded somewhere durable
- [x] our ink_player.gd continue/current_text logic diffed vs godot4 HEAD; delta documented (bug fixed upstream? y/n)
- [x] inkgd upgrade decision documented (stay vs upgrade + rationale)
- [x] harness L05 asserts the opening-narration line present (bug-signature regression guard)
- [x] rendered L05 text confirmed correct (no newline doubling) — evidence captured
- [x] L05/L06 rewritten prose reviewed for correctness by a fresh pass
- [x] `mise run ink:validate-gd` still green after any harness change

## Resolution (2026-08-28)

**Provenance:** vendored inkgd pinned to `fea9098` (godot4 HEAD, 2024-01-28) — verified
byte-identical to upstream (SHA-256 match, empty `git diff`). Recorded in a new
`ink-test-project/addons/inkgd/VENDOR.md` (moz.yaml-style manifest: repo/branch/SHA/date/license/
drift-check command) + a REFERENCES.md "Ink toolchain" entry. **Diff verdict: NO DELTA** — the
maximal-continue last-line drop is a WRAPPER bug (`ink_player.gd:424`), unchanged upstream, not a
vendoring artifact. **Upgrade decision: STAY** (snapshot == HEAD) — recorded in ADR 0013.

**Harness:** added an opening-narration bug-signature guard to `_validate_lesson05`
(`"You stand at the mouth" in text_label.text`). MUTATION-VERIFIED: reverting the player to
`continue_story_maximally()` turned the harness RED on exactly that assertion
(`got: The passage ahead is pitch black.`); restoring → GREEN.

**AC5 found + fixed a real defect (option a):** the render dump showed shipped players DOUBLE-SPACED
output — inkgd's `continue_story()` returns text already ending in `\n`, and the loop appended a
second. Fixed the `_text_label.text += text + "\n"` → `+= text` pattern in all 6 source-of-truth sites
(L05+L06 shipped players, both lesson HTML complete/fragment blocks, L06 README, spike_story.gd) + a
code comment documenting why. Re-dumped: single-spaced (one `¶` between same-passage lines vs the
prior `¶¶`). Golden transcripts unaffected (bink captures the continue return value, not the Godot
render).

**Prose (AC6):** fresh subagent review — all L05/L06 explanations traced to source, literally accurate;
SVGs clean. Two non-blocking cosmetic notes only.

Evidence: `mise run ink:validate-gd` PASS; `mise run verify` EXIT 0 (transcripts 4/4).
