# AGENTS.md — teach-me

Test bed for learning-oriented agent skills. Refined here, then ported to crew-research for global deployment.

## Workspace Layout

```
workspace/          — THE user's live learning workspace (gitignored, auto-created on first serve)
.kiro/skills/       — agent skills (teach, quiz-me, wait-what, jargon, visual-qa, theme, etc.)
.kiro/steering/     — visual-teaching guidelines
.memory/            — persistent knowledge (CONTEXT.md glossary, ADRs, research findings)
.scratch/           — ephemeral (gitignored) — only visual-qa output regenerated on run
.references/        — cloned reference repos (gitignored, rehydrate via mise run rehydrate)
tools/              — project scripts (draw-diagram, visual-qa, theme-preview, render-diagrams, sr-*)
tools/lib/          — Python helpers (preact_page.py for generating Preact HTML shells)
palettes/           — color palette definitions (JSON)
assets/             — shared: style.css, CSS variables, SVG patterns
assets/vendor/      — vendored Preact + Signals + HTM + dagre (self-hosted, no CDN)
assets/components/  — Preact components (MapView, TopicCard, QuizView, etc.)
assets/services/    — signal services (generation.js SSE stream)
assets/scaffolds/   — content-pattern examples (boilerplate is in tools/lib/page_template.py)
.tickets/           — local ticket tracking
library/           — public topic library (shipped, growing; served by default on a fresh clone — ADR 0012). Committed lessons/maps/reference per domain.
```

`workspace/` is the single live workspace per machine — all topics (maps, lessons, quizzes, reference docs, learning records) go here. Gitignored (user-local); auto-created on first `mise run serve`. Lessons are organized by domain: `lessons/{domain-slug}/NN-slug.html`, per-domain numbering from 01; quizzes and maps parallel this (`lessons/{domain-slug}/quiz/`, `lessons/{domain-slug}/{domain}-map.html`).

## Skills

| Skill | Trigger | What it does |
|-------|---------|-------------|
| teach | `/teach`, "teach me", "next lesson" | Multi-session learning with stateful workspace |
| generate-topic | `/generate-topic`, "generate lesson", "complete topic" | Full pipeline: research → lesson → post-process → verify (parallel subagents) |
| quiz-me | `/quiz-me`, "test me" | Socratic dialog — learner explains, agent probes |
| wait-what | `/wait-what`, "I don't understand" | Re-explain when comprehension fails |
| jargon | `/jargon`, "annotate terms" | Post-authoring: annotate domain jargon with tooltips |
| visual-qa | "visual qa", "check the ui" | Exercise components, capture screenshots, report |
| theme | "theme", "colors", "palette" | Preview, validate, and apply color palettes |
| draw-diagram | "draw diagram", "generate SVG" | Generate inline SVG teaching diagrams |
| browse-and-verify | "validate link", "check this URL" | Dispatch browser agent for URL validation |

## Commands

| Task | Command | What it does |
|------|---------|-------------|
| Install deps | `mise run setup` | drawsvg + graphviz + playwright + rich via uv |
| Generate diagram | `mise run draw -- --type flow --data '{...}'` (builtin) or `--type graph --backend graphviz` (auto-layout) | SVG to stdout |
| Render .mmd/.d2 | `mise run render-diagrams` | Batch render to assets/generated/ |
| Check topic complete | `python3 tools/check-topic-completeness.py --workspace X --all` | Reports missing artifacts per topic (lesson, ref, quiz, jargon, SR) |
| Compile lesson code blocks | `python tools/check-lesson-code.py` | Compiles downloadable `data-file` blocks (skips `fragment`): `.ink`→inklecate, `.py`→py_compile (both in `verify`); `.gd`/`.gdshader`→SKIP (Godot compile-check is opt-in, needs a project). Diff blocks reconstructed to post-diff state; blocks grouped by `data-file` + assembled before compile |
| Annotate jargon | `python3 tools/jargon-annotate.py --workspace X` | Mechanical term annotation from glossary-data JSON (idempotent) |
| Migrate SVG colors | `python3 tools/check-svg-vars.py --workspace X` | Flags hardcoded hex in lesson SVGs |
| Init workspace | `python tools/init_workspace.py [--default] [--path DIR]` | Scaffold workspace; --default for generic first-launch content (pure Python — no bash) |
| Mint MAP topic ULIDs | `python tools/migrate_map_ids.py --apply <mapfile>` | Fill MISSING `- **id:**` lines in a MAP.md with ULIDs (idempotent). Only fills missing — a `TBD`/invalid stub is flagged "manual review", NOT overwritten; omit the id line so the tool mints it. Run before committing a hand-written MAP (parser mints ephemeral ids otherwise → churn) |
| Serve workspace | `mise run serve -- [--workspace PATH]` | Start server (default workspace/, auto-created). Add `:lan` for 0.0.0.0:8787; `:restart` to kill+restart |
| Validate ink stories | `mise run ink:validate` (add `:strict` to treat warnings as errors) | Compile all .ink via inklecate, report errors/warnings |
| Validate ink GDScript | `mise run ink:validate-gd` | Headless Godot: run shipped lesson story_player.gd in the real inkgd runtime (needs Godot; skips if absent). `ink:validate` does NOT need Godot. |
| Validate Blender artifacts | `mise run verify:blender` | Real Blender: run the bpy artifacts' `--check` node-group validators (Tier-2 for the Blender lesson track). Skips if Blender absent. NOT in core `verify` — run before closing Blender-track tickets. |
| tkt (direct) | `D:\code\tkt\target\release\tkt.exe` | Bypass mise shim recursion for ticket management |
| SR review | `mise run sr` (due + health); `sr:review [-- topic]`, `sr:check` (leeches/format), `sr:analytics` (retention), `sr:lifecycle -- suspend ID` | Spaced-repetition review + maintenance |
| SR export | `mise run sr:quick-check -- [topic] [--all]` (review HTML); `sr:export-anki -- [topic] [--output path]` (.apkg) | Generate review pages / export cards |
| Visual QA | `mise run visual-qa` | Exercise all components, report pass/fail |
| Theme preview | `mise run theme-preview -- --palette palettes/purple-night.json` | Preview + contrast validation |
| Health check | `mise run doctor` | Verify tools, venv, references |
| Smoke test | `mise run verify` | Links + lint + SVG var check |
| Clone references | `mise run rehydrate` | Clone repos from REFERENCES.md — runs `tools/rehydrate.py` (cross-platform: parses `^git clone` lines, skips existing dirs, clones the rest). Every `.references/` repo MUST have a `git clone … .references/<dir>` line in REFERENCES.md or it won't rehydrate. |
| Open lesson | `mise run open-lesson` | Open latest lesson in browser |
| Generate map / index | `mise run map:generate -- <MAP.md>` (one); `maps:regenerate` (all); `index:generate -- [--scan-dir path]` (dashboard); `map:global -- [--scan-dir path]` (forest map — all domains as nodes, parent/child + leads_to edges) | Map/index/forest HTML from MAP.md files |
| Validate map forest | `python tools/check-maps-forest.py` (in `verify`) | Forest-scope prereq check — cross-map prereqs (sibling sub-maps) resolve against the union, not per-map (#155/#260) |
| Ingest source | `python tools/ingest_source.py <file-or-url> --workspace W --domain D --title T` | Full pipeline: chunk → classify → MAP → enrich prereqs. Find matching chunks with `match_section.py source-chunks/domain.json "query"` |

## Workflow

| Situation | Action |
|-----------|--------|
| **New user arrives** | Detect no populated workspace → introduce ("I'm a teaching workspace"), ask what they want to learn, scaffold their workspace, begin research |
| Someone asks "what is this?" | Orient: research-backed lessons + quizzes + spaced repetition. Offer to start with any topic. |
| User names a topic to learn | Run `generate-topic` pipeline (research → lesson → post-process → verify) |
| Starting a new lesson track | Scaffold reference project first (ADR 0010): test-scene, ink project, or equivalent. Each lesson produces a runnable artifact in the project. Validate via the project's toolchain before closing lessons. |
| Cloning a repo into `.references/` | Immediately add a `git clone … .references/<dir>` line to REFERENCES.md (grouped by track, with a one-line "what it shows") — otherwise `mise run rehydrate` can't reconstruct it and the clone is lost on a fresh checkout. Prune the entry if you delete the clone. |
| User wants to customize | Ask about pace (detailed vs direct), visuals (diagrams vs text), then save to NOTES.md |
| User says "quiz me" or "test me" | Socratic dialog — learner explains, agent probes understanding |
| Writing a lesson | Teach skill produces lesson + reference doc + SR questions + glossary JSON |
| After a lesson | Run jargon skill to annotate domain terms |
| After UI changes | `mise run visual-qa` to verify components still work |
| Leaving a ticket | Ticket is DONE (all AC checked) or OPEN with an update note. No partial closes. No moving on with unchecked boxes. |
| Closing a ticket | Edit frontmatter `status: done` directly — `tkt close` has a config validation bug that rejects valid tickets. Check all AC boxes in the same commit. Every close carries a `## Resolution` section (what shipped + how verified) — enforced going forward by `close.require_resolution=true` in `.tickets/config.toml`. |
| Historical ticket-resolution debt | `tkt validate` flags ~116 pre-convention done tickets `[missing/tbd-resolution]` — these are an ACCEPTED BASELINE (#285), non-blocking, not to be bulk-backfilled (git-log/body-mining is low-value churn per the baseline+ratchet best practice). Forward-only enforcement gates NEW closes; the baseline count may only decrease (add a Resolution opportunistically when you touch an old ticket). Fix `[stub-body]`/`[unchecked-acs-on-done]` honestly, never by faking a box. |
| Creating tickets | Use `tkt new slug --title "..."` then edit the created file. Don't create a separate file manually — causes duplicate ID validation errors. `tkt new` auto-commits AND pushes the stub; your populated-body edit is a separate follow-up commit. |
| Proposing non-trivial work (new ticket, design, or code change) | Dispatch research subagents (best practices/prior art) AND review subagents (existing code/docs/config) FIRST, then propose from findings — the established default here (requested verbatim across #233/#286). Extends the global research-dispatch mandate with the review-pairing. Skip for trivial/mechanical changes (over-trigger risk is real). When presenting a change for sign-off, show the actual DIFF, not just described effects or output samples. |
| Validating work | Validate from the user's perspective (Playwright click-through, curl the endpoint, load the page). Prefer linters, syntax checkers, and templates over formal test suites. Only write maintained tests for libraries with multiple consumers (e.g., map_parser.py). |
| Session start | `mise run sr` to check if cards are due before new material |
| New domain term | Add to `.memory/CONTEXT.md` immediately |
| Significant decision | Write ADR in `.memory/adr/NNNN-slug.md` |
| Changing colors | Use theme skill (preview → validate contrast → apply) |
| Complex diagram needed | Use `--backend graphviz` for cycles, state machines, 9+ nodes |

## Constraints

| Don't | Do instead |
|-------|-----------|
| Don't accumulate scratch files | Promote to `.memory/` or delete after use |
| Don't put implementation details in CONTEXT.md | Use ADRs for decisions with rationale |
| Don't commit .scratch/ or .references/ | Both are gitignored |
| Don't load Playwright MCP in default agent | Dispatch to `browser` specialist |
| Don't assume subagent tool trust inherits | Each specialist needs its own `allowedTools` |
| Don't teach from parametric memory | Cite sources in every lesson |
| Don't invent specific numbers | Cite or frame as general |
| Don't ask recall questions in gates | Ask "explain to [person] why..." |
| Don't give partial URLs, or default to 127.0.0.1 for humans | When a server is running, always provide full clickable URLs (http://host:port/path). For a human to VIEW, launch `--lan` and give the LAN address (http://192.168.x.x:PORT) as the primary link — 127.0.0.1 is only for agent-internal checks |
| Don't context-switch to content during infrastructure | Finish the migration/ticket in progress before generating lessons or teaching |
| Don't create per-topic workspaces | One workspace/ per machine holds all topics. Use library/ only for demo fixtures |
| Don't script creative work | Judgment work (question writing, term selection, level assignment) is a skill instruction, not a `tools/` script |
| Don't over-engineer user-facing features | Show information simply. One line of attribution beats routing + classification + progressive disclosure |
| Don't start new feature chains with open tickets in the current chain | Finish through the parent ticket before proposing new work |
| Don't put lessons in flat lessons/ root | Use `lessons/{domain-slug}/NN-slug.html` — per-domain subfolders numbered from 01 |

Lesson-authoring rules (page-shell.js, narrative framing around code blocks, downloadable `data-file` artifacts, no silent buttons, honest visual validation) live in `.kiro/steering/visual-teaching.md`.

## Environment

Deep track-specific gotchas (Blender bake internals, inkgd cache noise, transcript UTF-8, Windows Python quirks, Godot shader coordinate/lighting traps, glTF color-space, GitHub-Pages CI/deploy) live in `.memory/specs/environment-gotchas.md`. Always-on facts:

- Codex sandbox (bwrap) fails: `bwrap: loopback: Failed RTM_NEWADDR`. Use `codex exec --dangerously-bypass-approvals-and-sandbox`.
- Playwright MCP requires headless mode (no X server).
- Bedrock image limit: >20 images in conversation history triggers 2000px max. Resize to ≤768px; dispatch fresh subagents for image analysis in long sessions.
- Mise shim recursion: `mise run` may fail with "recursive shim invocation detected". Workaround: invoke `.venv\Scripts\python.exe` directly instead of `python` or `mise run`.
- PowerShell mangles complex inline shell-arg strings — inline JSON (`curl -d '{...}'`), `->`, backslashes, and long `git commit -m`/`tkt close --resolution` bodies get corrupted or misparsed. Use a file instead: `--data "@body.json"` for curl; `git commit -F msg.txt`; write long ticket resolutions to a temp file. Confirmed 3x (curl status POST, commit `->` arrows, tkt close).
- serve.py serves ONE workspace at a time. To view a different domain, restart: `mise run serve -- --workspace library/{domain}`. Git symlinks on Windows are text files — serve.py mounts `/assets` from project root automatically (no junctions). Serving a multi-domain root (`library/`, the fresh-clone default) works: serve.py normalizes any-depth `**/assets` + nested `index.html` back-links to the shared root (ADR-0015 unifying root, #198) — contents are exposed at `/{domain}/...` (NO `/library/` prefix; `/index.html` = the aggregate). Pages stay document-relative (`../assets`) — never root-relative `/assets` (breaks anchors/SVG under GitHub project-page `<base>`).
- All Preact packages must resolve to ONE instance or signals silently stop triggering re-renders. Vendored locally in `assets/vendor/` (import map resolves it); on a CDN (esm.sh) add `?external=preact`.
- FOUC prevention: a synchronous `<script>` in `<head>` (currently `typography-prefs.js`) reads prefs from localStorage and applies CSS custom properties BEFORE CSS paints. Must stay blocking/in-head — deferring it reintroduces the flash.
- Regenerating a committed library page (`index:generate`, `map:global`) re-bakes progress counts from `.user/status-overlay.json`. #278 committed a demo overlay under `library/**/.user/` (un-gitignored, kept at deploy), so regen is now IDEMPOTENT — counts re-bake to the committed values (ink 3/8, iceberg 2/7, godot 2/8), not 0. Still verify a regen diff before committing; a future move to load-time overlay reads is tracked in #279.
- New-domain scaffold sequence (validated #309): `python tools/init_workspace.py --path library/{domain}` (makes dirs, NOT the MAP) → hand-write `maps/{domain}.MAP.md` → **`python tools/migrate_map_ids.py --apply <mapfile>` to mint ULIDs**. Gotcha: `migrate_map_ids` only fills MISSING `- **id:**` lines — a present-but-invalid placeholder (e.g. `TBD`) is flagged "manual review" and NOT overwritten. Omit the id line entirely (don't stub it) so the tool mints it.
- `tools/check-lesson.py` path resolution: run as `--workspace library/{domain} --lesson lessons/NN-slug.html` (lesson path **workspace-relative**). Passing an absolute/repo-relative `--lesson` errors "lesson not found"; passing `--lesson` without `--workspace` mis-resolves the G3 "reference/code files present" check (false FAIL). The `reference/code/{slug}/` dir must be named the lesson slug **with the `NN-` prefix stripped** (`02-authoring-...html` → `reference/code/authoring-.../`) — check-lesson does `re.sub(r"^\d+-", "", stem)`.
- glTF/GLB lesson artifacts validate via `tools/gltf-format-oracle.py` (in `verify`); `check-lesson-code.py` does NOT validate `.gltf`/`.json` (only `.py`/`.ink`; `.gd`/`.gdshader` SKIP). A material-bearing `.glb` (cube + `pbrMetallicRoughness` + embedded PNG) is generatable with Python stdlib alone (`struct`+`json`+`zlib`, PNG via `zlib.crc32` — no Blender/Pillow); use `--require-material` to gate channel presence. Blender-produced artifacts ship a **bpy `.py` script** (zero committed `.blend` — repo precedent), wired opt-in into `tools/verify-blender.py` with a success sentinel + `--python-exit-code 1`.

## Skill Format (kiro-cli)

Skills live in `.kiro/skills/<name>/SKILL.md`, auto-loaded via `skill://.kiro/skills/**/SKILL.md`. For frontmatter and authoring conventions, see the global `skill-authoring` skill. Judge a skill by effectiveness — activation accuracy, workflow up front (detail in `references/`), non-redundancy, one-level references, dispatched-skills-stay-monolithic — NOT a line count (the agentskills.io spec has no hard size limit; <500 lines is a soft guardrail).

## Design Posture (ADR 0001)

The teach skill's posture is **knowledgeable colleague at a whiteboard** — not course instructor. Informal, mission-driven, direct. Tone: assumes intelligence, doesn't over-explain motivation, gets to mechanics quickly.

## When Blocked

1. Check `.memory/` for prior decisions and context
2. Check `.references/` for patterns in reference repos
3. If domain term is ambiguous — ask, then record in CONTEXT.md
4. If architecture choice needed — write ADR with options, propose to user

## Test Fixture

The root-level teaching workspace (MISSION.md, RESOURCES.md, lessons/, reference/, learning-records/) is the **Iceberg on AWS** example — a real teaching session used as a test fixture. See `library/README.md` for what to test feature changes against.
