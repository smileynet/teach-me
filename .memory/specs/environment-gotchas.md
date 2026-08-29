# Environment Gotchas (deep / track-specific)

Operational surprises scoped to specific tracks or tools. The broadly-relevant, always-on
environment facts stay in `AGENTS.md` → Environment; these deeper ones live here to keep AGENTS.md
under budget. Linked from AGENTS.md.

## Windows / Python tooling

- **Background servers on Windows:** use `Start-Process -WindowStyle Hidden` (never `-NoNewWindow` with
  redirects — it blocks). Verify with `Get-NetTCPConnection -LocalPort PORT -State Listen`. Never read
  stdout synchronously from a server process.
- **example lessons are tracked:** `examples/*/lessons/` are committed test fixtures. Only the live
  top-level `workspace/` is gitignored (anchored `/workspace/`) — no `git add -f` needed for example lessons.
- **Unicode stdout on Windows cp1252:** Python tools that print non-ASCII (`✓`, `✗`) fail on
  Windows cp1252. Every new `tools/*.py` printing non-ASCII MUST reconfigure stdout+stderr to UTF-8
  at module top: `if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")`
  (same for stderr). Six tools + verify-blender.py hit this (#237). Not a shared helper (single-use) —
  inline the guard.
- **maps:regenerate uses bash for-loop syntax** (fails on Windows). Use manual Python calls per-MAP:
  `.venv\Scripts\python.exe tools/generate_map_page.py {MAP} --workspace {ws} --output {out}` then
  `tools/generate_index_page.py --scan-dir {ws} --output {ws}/lessons/index.html` (both carry the
  UTF-8 stdout guard — no `PYTHONIOENCODING` needed).
- **Mutate-then-restore tests** (break a file → run a check → restore it) must put the RESTORE in its
  OWN shell call, never chained behind the run. A blocked/cancelled Godot/build/test run leaves the
  file broken and strands it (observed twice: a parse error left in `validate_runtime.gd` after a
  cancelled `--import` chain). Pattern: (1) back up + break, (2) run, (3) restore — three separate calls.

## Blender track

- **`mise run verify:blender` resolves Blender via `[env] BLENDER`** (default `"blender"`) — the mise
  `blender` shim is broken on Windows; point it at the full exe in gitignored `mise.local.toml`, e.g.
  `BLENDER = "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"`. Blender's `-b --python`
  swallows exceptions and exits 0, so `verify-blender.py` passes `--python-exit-code 1` AND checks each
  artifact's success sentinel (never trusts the exit code alone). The Godot A/B visual capture for the
  mktoon lessons is MANUAL (needs a GPU/window — headless can't render 3D); not part of any automated gate.
- **Blender bpy `img.save()` SILENTLY fails** (no error, no file) when `img.filepath_raw` is a RELATIVE
  path in headless mode. Always `Path(outdir).resolve()` to an absolute path before assigning
  `filepath_raw`, and set `img.file_format` explicitly. Hit by every bake script (#219/#220/#221).

## Ink / Godot track

- **inkgd (godot4 branch) cold-cache noise:** first headless import shows an SVG icon error ("plugin
  could not be initialized") — harmless, resolves on editor relaunch or second import. `ink:validate-gd`
  double-imports to warm the cache so this benign noise
  (`SCRIPT ERROR: Parse Error: Could not preload ... icon.svg`) never trips its error guard.
- **inklecate vs Godot as mise deps:** inklecate is a `[tools]` dep (`github:inkle/ink`, pinned in
  `mise.lock`) — on PATH after `mise install`. Godot is NOT a `[tools]` dep (heavy; only
  `ink:validate-gd` needs it): it resolves via PATH from `[env] GODOT = { default = "godot" }`. If your
  Godot isn't on PATH, point at it in gitignored `mise.local.toml`: `[env]\nGODOT = "C:/path/to/godot.exe"`.
- **Golden `.transcript` fixtures must be written UTF-8 from Python**
  (`open(path, "w", encoding="utf-8", newline="\n")`), NEVER via PowerShell `>` redirection —
  redirection re-encodes to cp1252 (an em-dash becomes byte `0x97`), and `play-ink.py` reads fixtures
  as UTF-8 and crashes on replay. Capture with a small Python wrapper that runs play-ink and writes
  stdout as UTF-8.
