# Page Scaffolds

Templates the agent reads before generating a new page. Copy the scaffold, replace `{{PLACEHOLDERS}}`, and fill with content.

## Available Scaffolds

| Scaffold | Generates | When to use |
|----------|-----------|-------------|
| `lesson.html` | `lessons/NNNN-slug.html` | Every new lesson |
| `reference.html` | `reference/NNNN-slug.html` | Companion to each lesson |
| `quick-check.html` | `lessons/review/quick-check.html` | SR review page with due cards |

## How to Use (agent instructions)

1. **Read the scaffold** before generating a page of that type
2. **Copy the structure** — don't invent new HTML structure for the same page type
3. **Replace placeholders** (`{{TITLE}}`, `{{TOPIC}}`, etc.) with content
4. **Keep the asset links** — `style.css`, `glossary.css`, `theme-toggle.js` in correct relative paths
5. **Use CSS variables** for any custom styling — never hardcoded hex colors
6. **Add content** between the structural markers

## Contract

All pages MUST:
- Link `../assets/style.css` (adjust relative path for depth)
- Include `../assets/theme-toggle.js` before `</body>`
- Use CSS variables for all colors (see `style.css` `:root` block)
- Include `lang="en"` on `<html>`
- Include viewport meta tag

Interactive pages additionally include:
- `../assets/glossary.css` + `glossary.js` (if using term tooltips)
- `../assets/progressive-reveal.js` (if using step-through diagrams)
- `../assets/quiz.js` (if using multiple-choice quizzes)

## Adding a New Page Type

When a new page type is needed (e.g., a progress dashboard, an index page):
1. Create a new scaffold here: `assets/scaffolds/<type>.html`
2. Include all required contract elements
3. Document it in this README
4. Use CSS variables for all custom styling
