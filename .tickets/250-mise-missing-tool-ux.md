---
id: "250"
title: "Surface missing pinned mise tools proactively instead of at cd-time"
status: backlog
blocked_by: []
priority: low
tags: ["platform"]
---

# Surface missing pinned mise tools proactively instead of at cd-time

## Why

On `cd teach-me`, mise emits `WARN missing: node@22.22.3` on every directory
entry until the pinned tool is installed. Root cause: `[tools] node = "22"` +
`[settings] lockfile = true` pins the exact patch (`22.22.3`) in `mise.lock`, but
the machine had only `22.22.2` installed. When the lockfile advances ahead of what
is installed (e.g. after a `git pull` that bumped the lock, or a fresh checkout),
the warning recurs on every `cd` with no guidance on the fix.

This is the lockfile working as designed — the "UX problem" is that the drift
surfaces as a repeated shell-entry warning rather than through a check the developer
runs deliberately. `mise run doctor` verifies python/node/uv *versions* but does NOT
detect a pinned-but-uninstalled tool, so the one task meant to catch environment
problems misses this class entirely.

Resolution for the immediate occurrence: `mise install` (already run — node@22.22.3
is now installed and the warning cleared). This ticket is the durable follow-up.

## What to do

1. **Add a missing-tool check to `[tasks.doctor]`** in `mise.toml`. After the
   version block, add a section that reports any pinned-but-uninstalled tool, e.g.:
   ```
   echo "=== Missing pinned tools ==="
   missing=$(mise ls --missing 2>/dev/null)
   if [ -n "$missing" ]; then
     echo "$missing"
     echo "→ run: mise install"
   else
     echo "✓ all pinned tools installed"
   fi
   ```
   (Verify `mise ls --missing` output shape against the installed mise version;
   fall back to parsing `mise ls` for `(missing)` if the flag is unavailable.)

2. **Document the reflex in AGENTS.md** (Environment section): after a `git pull`
   that changes `mise.lock` or `mise.toml`, run `mise install` before working —
   this clears any newly-pinned tool the machine lacks. One line.

3. **(Optional, discuss)** Decide the pinning policy for `node`. It is only used by
   optional diagram CLIs (`mmdc`, `d2`) which are not required for the core teaching
   pipeline. Options, in order of preference:
   - Keep exact pinning + doctor check (recommended — preserves reproducibility,
     just makes drift visible). No behavior change beyond items 1–2.
   - `mise use node@<installed>` to align the lock to a version already present
     (trades latest-patch for less reinstall churn).
   - Do NOT remove `lockfile = true` — the project pins deliberately for
     reproducibility; weakening it to silence one warning is the wrong trade.

## Acceptance criteria

- [ ] `mise run doctor` reports missing pinned tools (or "✓ all pinned tools installed")
      and names the `mise install` remedy
- [ ] `doctor` output verified against actual `mise ls --missing` behavior (not assumed)
- [ ] AGENTS.md Environment section notes the post-pull `mise install` reflex
- [ ] Pinning policy decision recorded (comment in mise.toml or a one-line note) —
      even if the decision is "keep as-is"
- [ ] No regression: `mise run doctor` still passes its existing checks
