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

## Acceptance criteria
- [ ] inkgd `godot4` snapshot commit SHA + date recorded somewhere durable
- [ ] our ink_player.gd continue/current_text logic diffed vs godot4 HEAD; delta documented (bug fixed upstream? y/n)
- [ ] inkgd upgrade decision documented (stay vs upgrade + rationale)
- [ ] harness L05 asserts the opening-narration line present (bug-signature regression guard)
- [ ] rendered L05 text confirmed correct (no newline doubling) — evidence captured
- [ ] L05/L06 rewritten prose reviewed for correctness by a fresh pass
- [ ] `mise run ink:validate-gd` still green after any harness change
