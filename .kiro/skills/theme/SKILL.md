---
name: theme
description: "Preview, validate, and apply color palettes. Use when changing colors, testing dark/light mode, or evaluating a new palette. Trigger: theme, colors, palette, dark mode, contrast, color scheme."
metadata:
  type: process
  invocation: both
  practice: null
---

# Theme

Preview, validate, and apply color palettes to the lesson UI.

## Workflow

### 1. Preview a palette

```bash
python tools/theme-preview.py --palette palettes/purple-night.json
```

Generates `.scratch/theme-preview.html` showing all UI elements with the palette applied, plus a contrast validation table. Open it in a browser or screenshot for analysis.

### 2. Validate contrast

The tool prints a contrast report to stdout:
```
✓ text on bg: 14.2:1 (AAA) — need 7.0:1
✓ text-muted on elevated: 5.1:1 (AA) — need 4.5:1
✗ text-faint on surface: 2.8:1 (FAIL) — need 4.5:1
```

Fix any failures before applying. Common fixes:
- Lighten the text token
- Darken the background token
- Use a less-saturated accent

### 3. Compare palettes

Generate previews for multiple palettes and compare:
```bash
python tools/theme-preview.py --palette palettes/purple-night.json --output .scratch/preview-purple.html
python tools/theme-preview.py --palette palettes/zinc-dark.json --output .scratch/preview-zinc.html
```

### 4. Get CSS snippet

```bash
python tools/theme-preview.py --palette palettes/purple-night.json --css
```

Prints the `:root { --bg: ...; }` block ready to paste into `style.css`.

### 5. Apply

Copy the CSS variables into `assets/style.css` `:root` block. Then verify:
```bash
mise run visual-qa
```

## Palette Format

Palettes live in `palettes/*.json`:

```json
{
  "name": "Purple Night",
  "mode": "dark",
  "tokens": {
    "bg": "#13111C",
    "bg-elevated": "#1C1A2E",
    "bg-surface": "#252340",
    "text": "#CDD6F4",
    "text-muted": "#9399B2",
    "text-faint": "#6C7086",
    "accent": "#CBA6F7",
    "link": "#89B4FA",
    "border": "#313244",
    "code-bg": "#1E1E2E",
    "success": "#A6E3A1",
    "warning": "#F9E2AF",
    "error": "#F38BA8",
    "callout-bg": "#1E293B",
    "key-concept-bg": "#2D1F0E"
  }
}
```

## Contrast Rules

| Pair | Minimum | Why |
|------|---------|-----|
| text on bg | 7:1 (AAA) | Extended reading — body text must be crisp |
| text on elevated | 7:1 | Tray panel body text |
| text-muted on bg | 4.5:1 (AA) | Secondary text still readable |
| text-muted on elevated | 4.5:1 | Common failure — always test this |
| text-muted on surface | 4.5:1 | Tooltips, popovers — the #1 failure point |
| link on bg | 4.5:1 | Interactive elements distinguishable |
| accent on bg | 4.5:1 | Headings readable |

## Design Principles (dark mode)

- Backgrounds: single hue family (purple ~250°), differentiated by lightness only (7%→20%)
- Text: off-white with slight blue/lavender tint — never pure #fff (causes halation)
- Accents: desaturated pastels (200-400 weight tones from light mode)
- Semantic colors: success/warning/error at reduced saturation
- Elevation = lighter (not shadowed) — dark mode inverts the depth model
- Body font weight: 500 (medium) in dark mode to counter irradiation thinning
