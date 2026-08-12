# Page Scaffolds

Templates the agent reads before generating a new page. Each scaffold is both a **copyable skeleton** and a **feature checklist** — HTML comments document what's required, optional, and why.

## Available Scaffolds

| Scaffold | Generates | When to use |
|----------|-----------|-------------|
| `lesson.html` | `lessons/NNNN-slug.html` | Every new lesson |
| `reference.html` | `reference/NNNN-slug.html` | Companion to each lesson |
| `quiz.html` | `lessons/quiz/NNNN-slug-quiz.html` | Per-topic quiz page |
| `quick-check.html` | `lessons/review/quick-check.html` | SR review page with due cards |

## How to Use (agent instructions)

1. **Read the scaffold** before generating a page of that type
2. **Copy the structure** — don't invent new HTML structure for the same page type
3. **Replace placeholders** (`{{TITLE}}`, `{{TOPIC}}`, etc.) with content
4. **Check every `REQUIRED` comment** — those features must be present in the final page
5. **Include `RECOMMENDED` features** unless there's a specific reason to omit
6. **Omit `OPTIONAL` features** if they don't apply to this specific page

## Asset Path Depth

Count directories from the file to the workspace root (where the `assets` symlink lives):

| File location | Depth | Asset prefix |
|---------------|-------|--------------|
| `lessons/*.html` | 1 | `../assets/` |
| `reference/*.html` | 1 | `../assets/` |
| `lessons/quiz/*.html` | 2 | `../../assets/` |
| `lessons/review/*.html` | 2 | `../../assets/` |

**Note:** Example workspaces (`examples/X/`) have their own `assets` symlink pointing to `../../assets`, so the depth is relative to the workspace root, not the project root.

## Universal Contract (ALL pages)

Every page MUST have:
- `lang="en"` on `<html>`
- Viewport meta tag
- Link to `style.css` (correct depth)
- `theme-toggle.js` before `</body>`
- CSS variables for all colors — never hardcoded hex

## Feature Expectations by Page Type

### Lesson Page
- **Structure:** h1 title, lesson-meta, key-concept intro, h2 sections, next-steps footer
- **Diagrams:** At least one inline SVG for the core concept (accessible: role, title, aria-labelledby)
- **Citations:** Every factual claim links to a source
- **Glossary:** JSON block + glossary.js for domain terms
- **Actions:** lesson-actions.js with data attributes (quiz link, mark-complete, back-to-map)
- **Self-check:** One conceptual exercise with hint + criteria-based answer (not recall)

### Reference Page
- **Structure:** h1 title, lesson-meta link to companion lesson, tables for facts, decision aids
- **Content model:** Scannable lookup — tables, lists, short answers. NOT prose.
- **No glossary needed** (the lesson handles term introduction)
- **No diagrams required** (keep it text-scannable), but optional if they aid lookup

### Quiz Page
- **Structure:** nav bar (← lesson, progress count, ← map), cards, done section
- **Question types:** Mix of explain, apply, predict, quick-check (at least 3 types per quiz)
- **Interaction:** Reveal button → shows answer + rating buttons. No correct/incorrect judgment.
- **Self-rating:** 3-level confidence (Not at all / Roughly / Confidently)
- **Metadata:** Each card shows section + tags
- **Navigation:** Done section links back to lesson AND map

### Quick-Check (SR Review)
- **Structure:** Topic heading, due count, card stack, rating buttons
- **Cards:** Due cards only (filtered by schedule)
- **Rating:** Maps to SR quality (1/3/5)

## Adding a New Page Type

1. Create `assets/scaffolds/<type>.html`
2. Include all universal contract elements
3. Annotate with `<!-- REQUIRED: ... -->` and `<!-- OPTIONAL: ... -->` comments
4. Add to this table
5. Update `tools/lint-html.py` if the new type has structural requirements
