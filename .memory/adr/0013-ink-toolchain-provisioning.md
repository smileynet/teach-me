# ADR 0013 — Ink toolchain provisioning via mise (inklecate pinned, Godot env-only, inkgd vendored)

Date: 2026-08-28
Status: accepted

## Context

The ink+Godot lesson track needs three tools at validation time: **inklecate** (the ink
compiler), **Godot** (runs the shipped `story_player.gd` via `mise run ink:validate-gd`), and
**inkgd** (the GDScript ink runtime addon, vendored in `ink-test-project/addons/`). Before this
decision, `inklecate` was hardcoded as `D:/tools/inklecate/inklecate.exe` in three committed
files — non-portable and invisible to contributors.

## Decision

1. **inklecate → mise `[tools]` `github:inkle/ink@1.2.1`, pinned in `mise.lock`.** It's a
   self-contained ~26 MB download (bundles .NET, no separate runtime), clean per-platform assets
   (win/linux/mac verified), and it's needed by the always-run `ink:validate`. On PATH after
   `mise install`. `[env] INKLECATE = { default = "inklecate" }` allows a local override.

2. **Godot → `[env]`-only (`GODOT = { default = "godot" }`), NOT a `[tools]` dep.** The Godot
   editor is ~100 MB+, only the *optional* `ink:validate-gd` gate needs it, and forcing every
   contributor to download it on `mise install` is disproportionate. Resolves via PATH; override
   in gitignored `mise.local.toml`. `ink:validate-gd` skips gracefully (exit 0) if Godot is absent.

3. **inkgd → stay on the vendored 0.6.0 `godot4`-branch snapshot; do NOT blind-upgrade.** There is
   no official Godot-4 inkgd release (latest tag is 0.5.0; `main` targets Godot 3). Upgrading the
   branch snapshot requires re-validating the whole harness + golden transcripts. Change only if
   #251's diff-vs-branch-HEAD shows a relevant fix (e.g. the InkPlayer last-line behavior), and
   record provenance (source commit SHA) when doing so.

## Consequences

- No committed absolute machine paths; `mise install` provisions inklecate reproducibly.
- Contributors without Godot can still run `ink:validate`/`ink:transcripts`; only the runtime
  gate skips. CI can run the compile/transcript gates without a Godot download.
- inkgd stability is our own responsibility (unreleased branch) — the harness is the safety net.

## Alternatives rejected

- **Godot as `[tools]` (aqua:godotengine/godot):** works (4.7.1 available) but the heavy download
  for an optional gate isn't worth it. Re-propose only if the Godot gate becomes mandatory in CI.
- **inklecate hardcoded path / `http:` backend:** rejected — `[tools]` github backend is portable
  and lock-pinned; the hardcoded path was the problem this ADR removes.

Supersedes the hardcoded-path approach (#244). Provenance/upgrade tracking: ticket #251.

## Update (2026-08-28, #251 — provenance recorded, diff resolved)

Decision 3 executed. Findings:

- **Snapshot commit pinned:** vendored inkgd == `godot4` HEAD `fea9098ee18d6cdbe9a5e25f8f0296bcdf0fd96a`
  (2024-01-28). Verified byte-identical (`ink_player.gd` SHA-256 matches the branch; `git diff --stat`
  empty). Provenance recorded in `ink-test-project/addons/inkgd/VENDOR.md` + REFERENCES.md.
- **Diff verdict (the InkPlayer last-line behavior):** NO DELTA. Our snapshot already equals branch
  HEAD, so upstream has NOT fixed the maximal-continue last-line drop. The bug lives in the InkPlayer
  wrapper (`ink_player.gd:424`), not the underlying `Story` method — upstream-inherited, not ours.
  The L05 "maximal-last-line gotcha" framing therefore stands (no revision needed).
- **Upgrade decision: STAY on `fea9098`.** There is nothing to upgrade to (snapshot == HEAD). Re-evaluate
  only when `git ls-remote … refs/heads/godot4` shows a newer SHA (drift check documented in VENDOR.md),
  and then only with a full harness + golden-transcript re-validation.


## Update (2026-08-28, #226 — bink reachability confirmed against inklecate)

`play-ink.py` uses **bink** (blade-ink-rs Python binding) to decide whether a story reaches END.
bink is NOT in the public ink-proof conformance harness (which tests inklecate/inkjs/godot-ink/inkcpp);
it self-verifies with in-repo tests only. This spike provides our LOCAL conformance evidence.

**Method:** drove `02_choices_and_weave.ink` (deterministic, branching) through BOTH runtimes with the
identical committed choice sequence `0,0,3,1,2,2,1` — bink via `play_capture()` (0-based), inklecate via
`inklecate -p` + `Popen.communicate()` with the +1 offset (1-based, no `-k`). Cross-check script:
`.scratch/226-crosscheck.py` (throwaway spike).

**Verdict: MATCH.** Both reach END (exit 0, terminal text present). A negative probe (truncated sequence
`0,0`) confirms the check discriminates — bink raises `ValueError: choice sequence exhausted with 4
choice(s) still pending`, correctly reporting non-termination. So bink's reachability verdict is
empirically sound for our use.

**Scope of the claim (honest):** this confirms bink agrees with inklecate on *reachability* for a
deterministic branching story — NOT full spec conformance. Reachability (terminates y/n) is the right
question because RANDOM/shuffle PRNG differs across C#/JS/Rust runtimes, so exact text can't match
cross-runtime anyway (which is why nondeterministic stories are excluded from golden transcripts).

**Windows note:** the #224 "inklecate -p doesn't accept piped stdin on Windows" concern did NOT
reproduce with inklecate 1.2.1 using the write-all-then-read `communicate()` pattern (all choices fed up
front, read to EOF). A per-prompt interactive read/write loop might still deadlock; `communicate()`
sidesteps it.

**Follow-up (backlog, not blocking):** broader confidence would come from a `rinklecate`-based ink-proof
driver for blade-ink-rs (bink ships `rinklecate`, mirroring the inklecate CLI, so a driver is feasible
but unpublished). File if bink conformance ever becomes load-bearing beyond reachability.
