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
examples/           — test fixtures and example workspaces (MAP.md samples, topic examples)
```

The `workspace/` directory is the single live workspace per machine. All topics go here — maps, lessons, quizzes, reference docs, learning records. It's gitignored (user-local state). Auto-created on first `mise run serve` if missing.

Lessons are organized by domain: `lessons/{domain-slug}/NN-slug.html`. Each domain gets its own subfolder with per-domain numbering starting from 01. Quizzes and maps parallel this: `lessons/{domain-slug}/quiz/`, `lessons/{domain-slug}/{domain}-map.html`.

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
| Generate diagram | `mise run draw -- --type flow --data '{...}'` | SVG to stdout (builtin layout) |
| Generate complex diagram | `mise run draw -- --type graph --backend graphviz --data '{...}'` | Auto-layout via Graphviz |
| Render .mmd/.d2 | `mise run render-diagrams` | Batch render to assets/generated/ |
| Check topic complete | `python3 tools/check-topic-completeness.py --workspace X --all` | Reports missing artifacts per topic (lesson, ref, quiz, jargon, SR) |
| Annotate jargon | `python3 tools/jargon-annotate.py --workspace X` | Mechanical term annotation from glossary-data JSON (idempotent) |
| Migrate SVG colors | `python3 tools/check-svg-vars.py --workspace X` | Flags hardcoded hex in lesson SVGs |
| Init workspace | `python tools/init_workspace.py [--default] [--path DIR]` | Scaffold workspace; --default for generic first-launch content (pure Python — no bash) |
| Serve workspace | `mise run serve -- [--workspace PATH]` | Start server (default: workspace/). Auto-creates workspace on first run |
| Validate shaders | `godot --path test-scene --editor` | Open test-scene in Godot; apply shaders to meshes, visually confirm |
| Validate shaders (headless) | `godot --headless --editor --import --quit --path test-scene` | Catches compilation errors only (no visual check) |
| Validate ink stories | `mise run ink:validate` | Compile all .ink files via inklecate, report errors/warnings |
| Validate ink (strict) | `mise run ink:validate:strict` | Same but warnings = errors (for release gates) |
| tkt (direct) | `D:\code\tkt\target\release\tkt.exe` | Bypass mise shim recursion for ticket management |
| Serve on LAN | `mise run serve:lan -- [--workspace PATH]` | Same but on 0.0.0.0:8787 for network access |
| Serve restart | `mise run serve:restart` | Kill existing server and restart |
| SR status | `mise run sr` | What's due, health summary |
| SR review | `mise run sr:review` | Review all due (or `-- topic-slug` for one topic) |
| SR quality check | `mise run sr:check` | Leech detection, prompt format issues |
| SR analytics | `mise run sr:analytics` | Knowledge %, what's decaying, load forecast |
| SR lifecycle | `mise run sr:lifecycle -- suspend ID` | Suspend, retire, reset, sync-lessons |
| Visual QA | `mise run visual-qa` | Exercise all components, report pass/fail |
| Theme preview | `mise run theme-preview -- --palette palettes/purple-night.json` | Preview + contrast validation |
| Health check | `mise run doctor` | Verify tools, venv, references |
| Smoke test | `mise run verify` | Links + lint + SVG var check |
| Clone references | `mise run rehydrate` | Clone repos from REFERENCES.md |
| Open lesson | `mise run open-lesson` | Open latest lesson in browser |
| Quick-check page | `mise run sr:quick-check -- [topic] [--all]` | Generate quick-check review HTML from due SR cards |
| Export to Anki | `mise run sr:export-anki -- [topic] [--output path]` | Export cards to .apkg |
| Generate map page | `mise run map:generate -- <MAP.md> [--output path]` | Interactive map HTML from MAP.md |
| Regenerate all maps | `mise run maps:regenerate` | Rebuild all map pages (workspace + examples) |
| Generate index | `mise run index:generate -- [--scan-dir path]` | All Lessons dashboard from MAP.md files |
| Ingest source | `python tools/ingest_source.py <file-or-url> --workspace W --domain D --title T` | Full pipeline: chunk → classify → MAP → enrich prereqs |
| Match section | `python tools/match_section.py source-chunks/domain.json "query"` | Find chunks matching a section reference |

## Workflow

| Situation | Action |
|-----------|--------|
| **New user arrives** | Detect no populated workspace → introduce ("I'm a teaching workspace"), ask what they want to learn, scaffold their workspace, begin research |
| Someone asks "what is this?" | Orient: research-backed lessons + quizzes + spaced repetition. Offer to start with any topic. |
| User names a topic to learn | Run `generate-topic` pipeline (research → lesson → post-process → verify) |
| Starting a new lesson track | Scaffold reference project first (ADR 0010): test-scene, ink project, or equivalent. Each lesson produces a runnable artifact in the project. Validate via the project's toolchain before closing lessons. |
| User wants to customize | Ask about pace (detailed vs direct), visuals (diagrams vs text), then save to NOTES.md |
| User says "quiz me" or "test me" | Socratic dialog — learner explains, agent probes understanding |
| Writing a lesson | Teach skill produces lesson + reference doc + SR questions + glossary JSON |
| After a lesson | Run jargon skill to annotate domain terms |
| After UI changes | `mise run visual-qa` to verify components still work |
| Leaving a ticket | Ticket is DONE (all AC checked) or OPEN with an update note. No partial closes. No moving on with unchecked boxes. |
| Closing a ticket | Edit frontmatter `status: done` directly — `tkt close` has a config validation bug that rejects valid tickets. Check all AC boxes in the same commit. |
| Creating tickets | Use `tkt new slug --title "..."` then edit the created file. Don't create a separate file manually — causes duplicate ID validation errors. |
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
| Don't omit page-shell.js | Every lesson includes page-shell.js via the template's depth-relative path — single entry point for nav, glossary, typography, layout |
| Don't ship silent buttons | Interactive buttons must have visible hover state + click feedback (animation, color change, or navigation) |
| Don't trust visual validation on pixel-art assets | Color simplification shaders (Kuwahara, posterize) produce NO visible effect on low-res flat-color textures — use 1K+ PBR textures (Poly Haven CC0) for honest validation |
| Don't give partial URLs | When a server is running, always provide full clickable URLs (http://host:port/path) |
| Don't context-switch to content during infrastructure | Finish the migration/ticket in progress before generating lessons or teaching |
| Don't create per-topic workspaces | One workspace/ per machine holds all topics. Use examples/ only for demo fixtures |
| Don't script creative work | If it requires judgment (question writing, term selection, level assignment), it's a skill instruction — not a `tools/` script |
| Don't over-engineer user-facing features | Show information simply. One line of attribution beats a system of routing + classification + progressive disclosure |
| Don't start new feature chains with open tickets in the current chain | Finish through the parent ticket before proposing new work |
| Don't drop code blocks without narrative framing | Before: what's changing and why. Between sequential blocks: what limitation motivates the next. After: connect back to concept. |
| Don't put lessons in flat lessons/ root | Use `lessons/{domain-slug}/NN-slug.html` — per-domain subfolders with numbering starting from 01 |
| Don't name files in code blocks without providing them | Every `data-file` block must have a corresponding downloadable file at `reference/code/{lesson-slug}/` |

## Environment

- Codex sandbox (bwrap) fails: `bwrap: loopback: Failed RTM_NEWADDR`. Use `codex exec --dangerously-bypass-approvals-and-sandbox`.
- Playwright MCP requires headless mode (no X server).
- Bedrock image limit: >20 images in conversation history triggers 2000px max. Resize to ≤768px; dispatch fresh subagents for image analysis in long sessions.
- Git symlinks on Windows are text files (contain target path as text). For local serving, use `python tools/serve.py --workspace examples/godot-gamedev` — it mounts `/assets` from project root automatically (no junctions needed). Only use junctions for `python -m http.server` debugging.
- Python tools with Unicode stdout (✓, ✗) fail on Windows cp1252. Use `set PYTHONIOENCODING=utf-8` or avoid non-ASCII in print() output.
- Mise shim recursion: `mise run` may fail with "recursive shim invocation detected". Workaround: invoke `.venv\Scripts\python.exe` directly instead of `python` or `mise run`.
- serve.py serves ONE workspace at a time. To view a different domain, restart: `mise run serve -- --workspace examples/{domain}`. Cross-workspace index page links are broken until #198 is resolved.
- examples/*/lessons/ is gitignored. Use `git add -f` when committing generated lesson HTML files.
- tkt new creates `{id}-{slug}.md`. Write ticket content to THAT file — don't create a separate file or you get duplicates requiring manual cleanup.
- inkgd (godot4 branch): first headless import shows SVG icon error ("plugin could not be initialized") — harmless, resolves on editor relaunch or second import.
- maps:regenerate mise task uses bash for-loop syntax (fails on Windows). Use manual Python calls per-MAP: `.venv\Scripts\python.exe tools/generate_map_page.py {MAP} --workspace {ws} --output {out}`
- Background servers on Windows: use `Start-Process -WindowStyle Hidden` (never `-NoNewWindow` with redirects — it blocks). Verify with `Get-NetTCPConnection -LocalPort PORT -State Listen`. Never read stdout synchronously from a server process.

## Skill Format (kiro-cli)

Skills live in `.kiro/skills/<name>/SKILL.md`, auto-loaded via `skill://.kiro/skills/**/SKILL.md`. For frontmatter and authoring conventions, see the global `skill-authoring` skill.

## Design Posture (ADR 0001)

The teach skill's posture is **knowledgeable colleague at a whiteboard** — not course instructor. Informal, mission-driven, direct. Tone: assumes intelligence, doesn't over-explain motivation, gets to mechanics quickly.

## When Blocked

1. Check `.memory/` for prior decisions and context
2. Check `.references/` for patterns in reference repos
3. If domain term is ambiguous — ask, then record in CONTEXT.md
4. If architecture choice needed — write ADR with options, propose to user

## Test Fixture

The root-level teaching workspace (MISSION.md, RESOURCES.md, lessons/, reference/, learning-records/) is the **Iceberg on AWS** example — a real teaching session used as a test fixture. See `examples/README.md` for what to test feature changes against.
