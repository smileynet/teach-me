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
assets/scaffolds/   — page templates for the teach skill
.tickets/           — local ticket tracking
examples/           — test fixtures and example workspaces (MAP.md samples, topic examples)
```

The `workspace/` directory is the single live workspace per machine. All topics go here — maps, lessons, quizzes, reference docs, learning records. It's gitignored (user-local state). Auto-created on first `mise run serve` if missing.

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
| Generate map page | `python3 tools/generate_map_page.py MAP.md --workspace X --output Y` | Preact DAG map from MAP.md |
| Generate index | `python3 tools/generate_index_page.py --scan-dir X --output Y` | Preact All Lessons dashboard |
| Generate resources | `python3 tools/generate_resources_page.py --workspace X --output Y` | Themed resources page from RESOURCES.md |
| Generate quiz page | `python3 tools/generate-quiz-page.py --workspace X --lesson-id Y --title T --lesson-file F --map-page M` | Preact quiz page from JSONL questions |
| Init workspace | `tools/init-workspace.sh [--default]` | Scaffold workspace; --default for generic first-launch content |
| Serve workspace | `mise run serve -- [--workspace PATH]` | Start server (default: workspace/). Auto-creates workspace on first run |
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
| Topic quiz page | `python tools/generate-quiz-page.py --lesson-id ID --title T --lesson-file F --map-page M` | Generate standalone quiz page for a topic (all questions, not just due) |
| Export to Anki | `mise run sr:export-anki -- [topic] [--output path]` | Export cards to .apkg |
| Generate map page | `mise run map:generate -- <MAP.md> [--output path]` | Interactive map HTML from MAP.md |
| Regenerate all maps | `mise run maps:regenerate` | Rebuild all map pages (workspace + examples) |
| Generate index | `mise run index:generate -- [--scan-dir path]` | All Lessons dashboard from MAP.md files |

## Workflow

| Situation | Action |
|-----------|--------|
| **New user arrives** | Detect no populated workspace → introduce ("I'm a teaching workspace"), ask what they want to learn, scaffold their workspace, begin research |
| Someone asks "what is this?" | Orient: research-backed lessons + quizzes + spaced repetition. Offer to start with any topic. |
| User names a topic to learn | Run `generate-topic` pipeline (research → lesson → post-process → verify) |
| User wants to customize | Ask about pace (detailed vs direct), visuals (diagrams vs text), then save to NOTES.md |
| User says "quiz me" or "test me" | Socratic dialog — learner explains, agent probes understanding |
| Writing a lesson | Teach skill produces lesson + reference doc + SR questions + glossary JSON |
| After a lesson | Run jargon skill to annotate domain terms |
| After UI changes | `mise run visual-qa` to verify components still work |
| Before progression | quiz-me for Socratic dialog (learner explains, agent probes) |
| Reviewing retention | `mise run sr:review` (all topics) or `mise run sr:review -- topic-slug` |
| Leaving a ticket | Ticket is DONE (all AC checked) or OPEN with an update note. No partial closes. No moving on with unchecked boxes. |
| Closing a ticket | `tkt close <id> --check-all --evidence "..." --resolution "..."`. Requires: (1) a `## Validation` section with `- [x]` checked items, (2) all acceptance criteria checked, (3) evidence string. `--force` may be disabled by project config. If close fails, add the Validation section first, then retry. |
| Creating tickets | Use `tkt new slug --title "..."` then edit the created file. Don't create a separate file manually — causes duplicate ID validation errors. |
| Validating work | Validate from the user's perspective (Playwright click-through, curl the endpoint, load the page). Prefer linters, syntax checkers, and templates over formal test suites. Only write maintained tests for libraries with multiple consumers (e.g., map_parser.py). |
| Session start | `mise run sr` to check if cards are due before new material |
| After writing questions | `mise run sr:check` as quality gate |
| Checking knowledge health | `mise run sr:analytics` for decay alerts and load forecast |
| Card is leeching | Suspend via `mise run sr:lifecycle -- suspend ID`, rewrite the prompt |
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
| Don't omit page-shell.js | Every lesson includes `<script type="module" src="../assets/page-shell.js"></script>` — single entry point for nav, glossary, typography, layout |
| Don't ship silent buttons | Interactive buttons must have visible hover state + click feedback (animation, color change, or navigation) |
| Don't give partial URLs | When a server is running, always provide full clickable URLs (http://host:port/path) |
| Don't context-switch to content during infrastructure | Finish the migration/ticket in progress before generating lessons or teaching |
| Don't create per-topic workspaces | One workspace/ per machine holds all topics. Use examples/ only for demo fixtures |

## Environment

- Codex sandbox (bwrap) fails: `bwrap: loopback: Failed RTM_NEWADDR`. Use `codex exec --dangerously-bypass-approvals-and-sandbox`.
- Playwright MCP requires headless mode (no X server).
- Bedrock image limit: >20 images in conversation history triggers 2000px max. Resize to ≤768px; dispatch fresh subagents for image analysis in long sessions.

## Skill Format (kiro-cli)

Skills live in `.kiro/skills/<name>/SKILL.md`. Frontmatter:
```yaml
name: skill-name
description: "What it does. Trigger: trigger phrases."
metadata:
  type: process|protocol|reference
  invocation: user-only|both
  practice: null
```
Skills auto-loaded via `skill://.kiro/skills/**/SKILL.md`.

## Design Posture (ADR 0001)

The teach skill's posture is **knowledgeable colleague at a whiteboard** — not course instructor. Informal, mission-driven, direct. Tone: assumes intelligence, doesn't over-explain motivation, gets to mechanics quickly.

## When Blocked

1. Check `.memory/` for prior decisions and context
2. Check `.references/` for patterns in reference repos
3. If domain term is ambiguous — ask, then record in CONTEXT.md
4. If architecture choice needed — write ADR with options, propose to user

## Test Fixture

The root-level teaching workspace (MISSION.md, RESOURCES.md, lessons/, reference/, learning-records/) is the **Iceberg on AWS** example — a real teaching session used as a test fixture. See `examples/README.md` for what to test feature changes against.

The live `workspace/` directory is gitignored and user-local. It holds all active learning topics for this machine.
