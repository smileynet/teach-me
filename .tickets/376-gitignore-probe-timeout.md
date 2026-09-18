---
id: "376"
title: "Add a timeout to the git check-ignore probe in generate_index_page"
status: done
blocked_by: []
priority: low
type: fix
tags: ["tools", "infra", "risk-review"]
validation_criteria:
  - "A hung git process cannot hang index generation"
---

# Add a timeout to the git check-ignore probe in generate_index_page

## Intent

The generation-time git subprocess must fail open on a hang, not block indefinitely.

## Context (found 2026-09-18 risk review of the 2026-09-16/17 window)

`fb5dfd7` (#369) added `committed_maps_only()` to `tools/generate_index_page.py:~50`, which runs

```python
r = subprocess.run(["git", "check-ignore", "-z", "--stdin"],
                   input=..., capture_output=True, cwd=PROJECT_ROOT)
```

with no `timeout=`. The encoding handling around it is deliberately correct (bytes mode, `-z`,
UTF-8 decode with replace for the Windows cp1252 locale), and OSError already fails open — but
a hung git (locked index, credential prompt in a weird state, network filesystem) would hang
the generator with no bound. Generation-time only, low traffic — hence low priority.

## What to build

Add a modest `timeout=` (a few seconds — check-ignore is local and fast) and fail open on
`subprocess.TimeoutExpired`, matching the existing OSError fail-open posture.

## Acceptance criteria

- [x] `committed_maps_only` passes `timeout=` to the subprocess and treats `TimeoutExpired` as fail-open (paths unchanged), consistent with the OSError path — `timeout=_GIT_PROBE_TIMEOUT_S` (5s) on the `subprocess.run`, `except (OSError, subprocess.TimeoutExpired): return paths`
- [x] A short comment documents the fail-open trio: OSError / timeout / non-zero exit → unchanged list

## Resolution (2026-09-18)

`tools/generate_index_page.py` `committed_maps_only`: added `_GIT_PROBE_TIMEOUT_S = 5`
(check-ignore is a local sub-second probe) to the `subprocess.run` call, and widened the
fail-open catch to `(OSError, subprocess.TimeoutExpired)` with a comment naming all three
fail-open modes (git missing, git hung, git erroring via empty stdout). Verified: real-path
behavior unchanged (committed map kept, and `git check-ignore` still flags gitignored roots
through the bytes/`-z` protocol); an injected `TimeoutExpired` returns the input list
unchanged instead of raising or hanging. Ticket #376.

## References

- Commit `fb5dfd7` (#369); `tools/generate_index_page.py` `committed_maps_only`
