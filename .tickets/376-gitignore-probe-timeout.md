---
id: "376"
title: "Add a timeout to the git check-ignore probe in generate_index_page"
status: open
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

- [ ] `committed_maps_only` passes `timeout=` to the subprocess and treats `TimeoutExpired` as fail-open (paths unchanged), consistent with the OSError path
- [ ] A short comment documents the fail-open trio: OSError / timeout / non-zero exit → unchanged list

## References

- Commit `fb5dfd7` (#369); `tools/generate_index_page.py` `committed_maps_only`
