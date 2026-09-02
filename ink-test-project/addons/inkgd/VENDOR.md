# Vendored dependency: inkgd

This addon is a **vendored snapshot** of an unreleased upstream branch. There is no
official Godot-4 inkgd release (latest tag is 0.5.0; `main` targets Godot 3), so the
snapshot commit SHA below **is** the version — `plugin.cfg` `version=0.6.0` is the
upstream maintainer's string, not a release we can pin against.

| Field | Value |
|-------|-------|
| Upstream repo | https://github.com/ephread/inkgd.git |
| Branch tracked | `godot4` |
| Pinned commit | `fea9098ee18d6cdbe9a5e25f8f0296bcdf0fd96a` |
| Commit date | 2024-01-28 |
| Commit subject | Re-enable inkgd plugin |
| Fetched / vendored | 2026-08-24 |
| License | MIT (see `LICENSE`) |
| Local patches | `.gitignore` removed (see below); otherwise byte-identical to branch HEAD (SHA-256 of `ink_player.gd` matches) |

## Local deviation from upstream (do not reintroduce on re-vendor)

Upstream ships `addons/inkgd/.gitignore` containing `*.import`, which hides the two editor
icon sidecars (`editor/icons/compile.svg.import`, `ink_player.svg.import`). This project
**removed** that file so the repo-root `.gitignore` owns all ignore policy (ignore `.godot/`
only), and the icon `.import` sidecars are committed like every other `.import` — matching
the `test-scene` precedent (449 tracked, zero addon-level `.gitignore`, all `.import`
committed). Committing the `.import` avoids per-machine UID/reimport churn on fresh clone.
When re-vendoring a newer `godot4` commit, delete the incoming `.gitignore` again. (#234)

`ink_player.gd` itself last changed upstream at `88441d6` (2024-01-25); the two later
`godot4` commits do not touch it.

## Known behavior (do not "fix" locally)

`InkPlayer.continue_story_maximally()` (`ink_player.gd:415-430`) returns only the **last**
line of a multi-line passage — line 424 assigns `text = self.current_text`, which holds the
current (last) line, discarding the concatenated text. The underlying
`Story.continue_story_maximally()` (`runtime/ink_story.gd:482`) concatenates correctly; the
wrapper throws it away. This is the root of the #236 lesson-05 bug. It is **upstream behavior
at branch HEAD**, not a vendoring artifact — shipped lessons use a single-step
`while can_continue: continue_story()` accumulate loop instead. See ADR 0013 and ticket #251.

## Checking for upstream drift

```
git ls-remote https://github.com/ephread/inkgd.git refs/heads/godot4
```

If the printed SHA differs from the pinned commit above, upstream has advanced. An upgrade is
NOT automatic: it requires re-running the full harness (`mise run ink:validate-gd`) and
re-validating golden transcripts (see ADR 0013's stay-vs-upgrade rationale).
