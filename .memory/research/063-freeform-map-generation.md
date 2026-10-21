# Research 063 — Free-form topic generation from the map page

**Status:** complete · **Date:** 2026-10-21 · **Ticket:** 063

Can a user type "I want to learn about X" on the map page and get a new domain
MAP.md generated on the spot — in two modes (related → links to current domain;
greenfield → standalone)? **Yes, the generation half is proven.** The *wiring*
half (UI, created-file capture, navigation) is net-new and does not exist today.

## Coverage of the deliverable

| Question | Answer | Evidence | Confidence |
|----------|--------|----------|------------|
| Q1 Prompt construction | ✅ Answered | 5/5 live kiro-cli generations validated | Verified (live) |
| Q2 Filename convention | ✅ Answered | Code: generate_map_page.py / generate_index_page.py | Verified (code) |
| Q3 Parent linking | ✅ Answered | Live related-mode generation + map_parser | Verified (live) |
| Q4 Navigation after gen | ✅ Answered | Code trace: serve.py `done` event | Verified (code) — premise corrected |
| Q5 Input validation | ✅ Answered | Code: serve.py SAFE_PROMPT_RE | Verified (code) |
| Q6 UI placement | ⚠️ Recommendation | Code: generate_map_page.py (no screenshot) | Inferred |

Not screenshot-verified: Q6 UI mockups and the full browser click-through are
left to the follow-on *feature* tickets, which carry Playwright e2e criteria. A
research ticket can't screenshot UI that isn't built yet; what IS verifiable —
that the prompt reliably yields a renderable map — is verified live.

---

## ⚠️ Correction to the ticket's premise

The ticket states (Q4): *"Auto-redirect works (we have `_genCreatedFile`)."*
**This is false.** `_genCreatedFile` appears nowhere in the codebase — only in
the ticket text (grep across repo excluding `.tickets/` → 0 matches). Today:

- The map page's "Generate" buttons (`generate_map_page.py:594-636`,
  `offerGenerate`/`offerGenerateQuiz`/`offerZoomIn`) only show a **copy-pasteable
  shell command** in a modal. They do **not** call the server.
- `tools/serve.py` CAN spawn kiro-cli and stream SSE, but its `done` event
  carries **only `{"exit_code": N}`** (`serve.py:265`). Nothing captures which
  file was created; nothing redirects the browser.

So Q4 is not "which file do we navigate to" — it is "created-file capture and
navigation must be built." Treated as net-new below.

---

## 🚨 Critical finding — the checkpoint stall (blocks everything)

Running `kiro-cli chat --no-interactive` the way `serve.py` does
(`serve.py:159-181`) **hangs forever** on first run in this environment:

```
Checkpoint operation failed: Vim: Warning: Output is not to a terminal
Vim: Warning: Input is not from a terminal
```
(`.scratch/063-maptest/dns-resolution.log`, first attempt → `EXIT=124` timeout, no file)

Root cause: `chat.enableCheckpoint = true` (global default) + `EDITOR=vim`.
kiro-cli's checkpoint feature shells out to git/vim, which blocks with no TTY.

Worse, **`serve.py` silently drops the one diagnostic line** — `_read_output`
filters any line containing `"Checkpoint operation failed"` (`serve.py:202-203`).
In production this stall would look like a dead generation with no error.

**Fix (verified):** `kiro-cli settings chat.enableCheckpoint false` → the same
prompt completed in ~90-150s and wrote a valid file. The server must disable
checkpointing for its spawned process. Options, preferred first:
1. Pass a per-invocation setting if kiro-cli adds a flag (none exists at 2.16.0 —
   `chat --help` has no checkpoint flag).
2. Spawn with an env that neutralizes the editor, e.g.
   `env={... "EDITOR": "true", "VISUAL": "true", "GIT_EDITOR": "true"}` so the
   checkpoint's editor call returns instantly. (Needs validation — see Spike 090.)
3. Set `chat.enableCheckpoint false` in the server's HOME profile. Global and
   blunt; acceptable only for a dedicated generation host.

> Setting was flipped to `false` to run these tests and **restored to `true`**
> afterward (verified). Do not assume it is off.

---

## Q1 — Prompt construction (VERIFIED, 5/5)

A single prompt that **embeds the MAP.md format skeleton verbatim + explicit
hard rules** reliably produces spec-conformant, parser-valid maps. Test harness:
`.scratch/063-maptest/gen.sh` (greenfield) and `gen-related.sh` (related).

Command (exactly serve.py's shape):
`kiro-cli chat --no-interactive --trust-tools=read,write,glob,shell,code,grep "<prompt>"`

| Topic phrase | slug | topics | depth/parent | validate() |
|---|---|---|---|---|
| "how DNS resolution works end to end" | dns-resolution | 8 | 0 / null | 0 errors |
| "the fundamentals of how a CPU cache works" | cpu-caching | 8 | 0 / null | 0 errors |
| "getting started with Kubernetes for application developers" | kubernetes-for-app-devs | 8 | 0 / null | 0 errors |
| "sourdough bread baking" (short/ambiguous) | sourdough-baking | 8 | 0 / null | 0 errors |
| "shader programming in Godot" (RELATED) | shader-programming | 7 | 1 / godot-gamedev | 0 errors |

5/5 passed `map_parser.validate()` with 0 errors, all within the 5-9 topic rule,
all DAG-valid, all with correct frontmatter. One sample rendered end-to-end
through `generate_map_page.py` → 27KB working HTML with topic anchors + generate
buttons + "Where This Leads" section.

**Prompt rules that mattered** (dropping any of these is the likely regression
source if quality drops later):
- Embed the literal format skeleton (frontmatter + one example topic block).
- State the hard constraints as an explicit list: 5-9 topics; every prereq slug
  must match a topic in THIS file; prereqs form a DAG; first topic `prereqs: []`;
  slugs lowercase-hyphenated; scope ∈ {lightweight,substantial,deep}; status
  always `not-started`.
- "Write ONLY the file (use the write tool). Do not create any other files. No
  prose outside the file." — prevents it from also generating lessons/quizzes.
- Pin `domain:`, `generated:` (today's date), `depth:`, `parent:` in the skeleton
  so the model fills content, not structure.

**Prompt size caveat:** the working prompt is ~1.2-1.3K chars — it **exceeds the
server's `MAX_PROMPT_LEN=500`** and contains characters `SAFE_PROMPT_RE` rejects
(`#`, `[`, `]`, `{`, `}`, `*`, newlines). This is fine *by design*: the user only
types the topic phrase (short, validated); the server **injects the format
scaffold around it**. The scaffold is a trusted server-side constant, never user
input, so it bypasses the regex legitimately. See Q5.

**Latency:** ~90-150s per map (observed, single generation, checkpoint off).
Well within the existing SSE heartbeat/stream design; no new timeout needed.

Sample output: `.scratch/063-maptest/maps/dns-resolution.MAP.md` (reproduced in
the appendix is unnecessary — the file is in scratch for this session).

## Q2 — Filename convention (VERIFIED from code)

Two files per generated domain, matching existing conventions exactly:
- **Source:** `{workspace}/maps/{domain}.MAP.md` (e.g.
  `examples/iceberg-workspace/maps/data-analytics.MAP.md`). Sub-maps use the flat
  `{topic-slug}.MAP.md` form (`map_parser.resolve_map_filename`).
- **HTML:** `{workspace}/lessons/{domain}-map.html` where `{domain}` comes from
  **frontmatter, not the filename** (`generate_map_page.py:697`,
  `generate_index_page.py:141`). The index links map↔html via this `{domain}`
  convention.

Recommendation: generate BOTH. The MAP.md is the source of truth (future zoom,
status updates, re-render); the HTML is what the user navigates to. The server
runs `generate_map_page.py` after the MAP.md is written.

## Q3 — Parent linking (VERIFIED, live)

For related mode, the prompt needs only: the **parent domain slug** and its
**human title** (+ optional one-line orientation). Full parent MAP.md is NOT
required — the related-mode test passed with just slug + title, producing
`parent: godot-gamedev`, `depth: 1`, 7 valid topics. Keep the injected parent
context minimal (slug + title + orientation sentence) to keep the prompt small
and reliable.

Auto-adding the child to the parent's `leads_to`: do this **server-side after
generation**, not via the prompt — it's a deterministic edit to a different file
and should not depend on model behavior. `map_parser` has no `leads_to` mutator
yet (only `update_status`); one must be added (Feature 092). Note the godot map
already lists `shader-programming` in `leads_to`, so the add must be idempotent
(skip if already present).

Greenfield mode: `parent: null`, `depth: 0`, and **do NOT** touch any other map's
`leads_to` (per ticket). The confirmation warning is pure UI.

## Q4 — Navigation after generation (VERIFIED from code; premise corrected)

`_genCreatedFile` does not exist (see correction above). What's needed:
1. The generation produces a **known domain slug** — the server already knows it
   because IT constructs the prompt (it chose the slug), so it can compute the
   target `lessons/{domain}-map.html` **without parsing kiro-cli output**. This is
   the robust path: don't scrape stdout for filenames; the server owns the slug.
2. After `done` (exit_code 0), server runs `generate_map_page.py` for that slug,
   then the client redirects to `lessons/{domain}-map.html`. The SSE `done` event
   should be extended to carry the redirect target, e.g.
   `{"exit_code":0,"redirect":"lessons/dns-resolution-map.html"}`.
3. On non-zero exit or validation failure, do NOT redirect; surface the error.

This makes slug derivation a server responsibility (slugify the user's topic,
dedupe against existing maps) rather than trusting model output — strictly more
reliable.

## Q5 — Input validation (VERIFIED from code)

`SAFE_PROMPT_RE = ^[\w\s&:,.'/()\-–—]+$`, `MAX_PROMPT_LEN=500` (`serve.py:141-142`).
- **Keep it for the user's topic field** — it is exactly the command-injection
  guard needed before the phrase is interpolated into the prompt. All 5 test
  phrases pass it ("how DNS resolution works end to end" etc.).
- **Do not run it against the full scaffolded prompt** — the scaffold is a
  server-side trusted constant containing `#[]{}` etc. Validate the *user input*,
  then build the prompt. (The current code validates `req.prompt` which today IS
  the full prompt — that's why the scaffold must move server-side.)
- Recommend a dedicated endpoint `POST /api/generate-map {topic, mode, parent}`
  rather than overloading `/api/generate`, so the 500-char/regex check applies to
  `topic` only and the server composes the scaffold. Also slugify + length-check
  the derived slug.

## Q6 — UI placement (RECOMMENDATION, not screenshot-verified)

Options considered (`generate_map_page.py` HTML structure, lines 218-640):
- **Sticky footer bar** (recommended): always reachable regardless of scroll;
  doesn't compete with the graph. A single text input + "Generate" button +
  "Unrelated topic?" checkbox. Fits the existing modal pattern for progress.
- Inside "Where This Leads" (`:283-304`): thematically apt ("explore further")
  but that section is static today and may be absent on leaf maps.
- Below the graph: simple, but pushed off-screen on tall topic lists.

Flow: type topic → (if "Unrelated" checked) confirm warning → POST to
`/api/generate-map` → reuse the existing SSE progress modal
(`tools/sse-test.html:99-128` is the reference client loop) → on `done` with
redirect, navigate. Greenfield checkbox gates the standalone-vs-linked behavior
and the confirmation dialog.

---

## Proposed follow-on tickets (filed separately)

- **090 — Spike: harden kiro-cli generation subprocess (checkpoint stall).**
  Validate the `EDITOR=true`/`GIT_EDITOR=true` env fix vs. `chat.enableCheckpoint
  false`; stop serve.py from swallowing the checkpoint error line; confirm a clean
  generation in a fresh worktree. **BLOCKS 091/092.**
- **091 — Feature: free-form map generation endpoint + UI.** `POST /api/generate-map`
  (server-side scaffold, slug derivation, SAFE_PROMPT_RE on topic only), sticky
  footer UI with related/greenfield toggle + confirmation, SSE progress, redirect
  on done.
- **092 — Feature: parent-linking on related generation.** Server sets
  `parent`/`depth` via the prompt, adds child to parent's `leads_to` idempotently
  (new `map_parser.add_leads_to`), regenerates the parent map HTML.

Each ticket's e2e validation is written in the ticket itself (Playwright
click-through / curl the endpoint / parser-validate the output).

## Reproduce

```
kiro-cli settings chat.enableCheckpoint false   # REQUIRED or it hangs
bash .scratch/063-maptest/gen.sh "<topic>" "<slug>"
bash .scratch/063-maptest/gen-related.sh "<topic>" "<slug>" "<parent-domain>" "<parent-title>"
python3 -c "import sys;sys.path.insert(0,'tools');from map_parser import load_map,validate;m=load_map('<file>');print(validate(m) or 'PASS')"
kiro-cli settings chat.enableCheckpoint true    # restore
```
