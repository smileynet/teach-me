#!/usr/bin/env python3
"""theme-preview.py — Preview a palette against all UI elements + validate contrast.

Usage:
  python tools/theme-preview.py --palette palettes/purple-night.json
  python tools/theme-preview.py --palette palettes/purple-night.json --serve 8080
  python tools/theme-preview.py --palette palettes/purple-night.json --css

Exit codes:
  0 = all contrast checks pass (AA minimum)
  1 = one or more contrast failures
"""

# Windows consoles default to cp1252; force UTF-8 so ✓/→/emoji glyphs don't crash (#265).
import sys as _sys
if hasattr(_sys.stdout, "reconfigure"):
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(_sys.stderr, "reconfigure"):
    _sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import sys
import subprocess
from pathlib import Path


def hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def relative_luminance(rgb):
    """WCAG 2.1 relative luminance."""
    def linearize(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = [linearize(c) for c in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex1, hex2):
    """WCAG contrast ratio between two hex colors."""
    l1 = relative_luminance(hex_to_rgb(hex1))
    l2 = relative_luminance(hex_to_rgb(hex2))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def wcag_grade(ratio):
    if ratio >= 7.0:
        return 'AAA'
    elif ratio >= 4.5:
        return 'AA'
    elif ratio >= 3.0:
        return 'AA-large'
    return 'FAIL'


def validate_palette(tokens):
    """Run contrast checks and return results."""
    checks = [
        ('text on bg', 'text', 'bg', 7.0),
        ('text on elevated', 'text', 'bg-elevated', 7.0),
        ('text-muted on bg', 'text-muted', 'bg', 4.5),
        ('text-muted on elevated', 'text-muted', 'bg-elevated', 4.5),
        ('text-muted on surface', 'text-muted', 'bg-surface', 4.5),
        ('link on bg', 'link', 'bg', 4.5),
        ('link on elevated', 'link', 'bg-elevated', 4.5),
        ('accent on bg', 'accent', 'bg', 4.5),
        ('success on bg', 'success', 'bg', 4.5),
        ('warning on key-concept-bg', 'warning', 'key-concept-bg', 4.5),
        ('error on bg', 'error', 'bg', 4.5),
    ]

    results = []
    for label, fg_key, bg_key, threshold in checks:
        fg = tokens.get(fg_key, '#ffffff')
        bg = tokens.get(bg_key, '#000000')
        ratio = contrast_ratio(fg, bg)
        grade = wcag_grade(ratio)
        passed = ratio >= threshold
        results.append({
            'label': label,
            'fg': fg,
            'bg': bg,
            'ratio': round(ratio, 2),
            'grade': grade,
            'threshold': threshold,
            'pass': passed
        })
    return results


def generate_css_snippet(tokens):
    """Generate CSS :root block from tokens."""
    lines = [':root {']
    for key, value in tokens.items():
        lines.append(f'  --{key}: {value};')
    lines.append('}')
    return '\n'.join(lines)


def generate_preview_html(palette):
    """Generate a preview HTML page showing all UI elements."""
    name = palette['name']
    tokens = palette['tokens']
    checks = validate_palette(tokens)

    contrast_rows = ''
    for c in checks:
        status = '✓' if c['pass'] else '✗'
        color = tokens.get('success', '#a6e3a1') if c['pass'] else tokens.get('error', '#f38ba8')
        contrast_rows += f'''<tr>
          <td>{c["label"]}</td>
          <td><span style="color:{c["fg"]};background:{c["bg"]};padding:2px 6px;border-radius:3px">Sample</span></td>
          <td>{c["ratio"]}:1</td>
          <td>{c["grade"]}</td>
          <td style="color:{color}">{status}</td>
        </tr>\n'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Theme Preview: {name}</title>
  <style>
    :root {{
      {chr(10).join(f"      --{k}: {v};" for k, v in tokens.items())}
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Palatino Linotype', Palatino, Georgia, serif;
      background: var(--bg);
      color: var(--text);
      max-width: 740px;
      margin: 0 auto;
      padding: 2rem 1.5rem;
      line-height: 1.7;
    }}
    h1 {{ font-size: 2rem; margin-bottom: 0.5rem; font-weight: 700; color: var(--accent); }}
    h2 {{ font-size: 1.4rem; margin-top: 2.5rem; margin-bottom: 0.75rem; font-weight: 600; }}
    h3 {{ font-size: 1.1rem; margin-top: 1.5rem; margin-bottom: 0.5rem; font-weight: 600; }}
    p {{ margin-bottom: 1rem; }}
    a {{ color: var(--link); text-decoration: underline; }}
    .muted {{ color: var(--text-muted); }}
    .faint {{ color: var(--text-faint); }}
    code {{
      font-family: Menlo, Consolas, monospace;
      font-size: 0.85rem;
      background: var(--code-bg);
      padding: 0.15rem 0.35rem;
      border-radius: 3px;
    }}
    pre {{
      background: var(--code-bg);
      padding: 1rem;
      border-radius: 4px;
      overflow-x: auto;
      margin: 1.5rem 0;
      border-left: 3px solid var(--accent);
    }}
    pre code {{ background: none; padding: 0; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 1.5rem 0;
      font-size: 0.85rem;
    }}
    th, td {{ padding: 0.5rem 0.75rem; border: 1px solid var(--border); text-align: left; }}
    th {{ background: var(--code-bg); font-weight: 600; }}
    .key-concept {{
      background: var(--key-concept-bg);
      border-left: 4px solid var(--warning);
      padding: 0.75rem 1rem;
      margin: 1.5rem 0;
      border-radius: 0 4px 4px 0;
    }}
    .callout {{
      background: var(--callout-bg);
      border-left: 4px solid var(--link);
      padding: 0.75rem 1rem;
      margin: 1.5rem 0;
      border-radius: 0 4px 4px 0;
    }}
    .elevated {{
      background: var(--bg-elevated);
      padding: 1rem;
      border-radius: 6px;
      margin: 1.5rem 0;
    }}
    .surface {{
      background: var(--bg-surface);
      padding: 1rem;
      border-radius: 6px;
      margin: 1.5rem 0;
    }}
    details {{
      margin: 1rem 0;
      padding: 0.5rem 0.75rem;
      border-left: 3px solid var(--border);
    }}
    details[open] {{ background: var(--code-bg); }}
    details summary {{ cursor: pointer; color: var(--text-muted); font-size: 0.9rem; }}
    .term {{
      text-decoration: underline dotted var(--text-muted);
      text-underline-offset: 3px;
      cursor: help;
    }}
    .quiz-correct {{
      background: color-mix(in srgb, var(--success) 15%, var(--bg));
      border: 1.5px solid var(--success);
      padding: 0.6rem 0.8rem;
      border-radius: 6px;
      margin: 0.4rem 0;
    }}
    .quiz-incorrect {{
      background: color-mix(in srgb, var(--error) 15%, var(--bg));
      border: 1.5px solid var(--error);
      padding: 0.6rem 0.8rem;
      border-radius: 6px;
      margin: 0.4rem 0;
    }}
    .swatch {{
      display: inline-block;
      width: 24px;
      height: 24px;
      border-radius: 4px;
      vertical-align: middle;
      margin-right: 0.5rem;
      border: 1px solid var(--border);
    }}
    .color-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
      gap: 0.75rem;
      margin: 1rem 0;
    }}
    .color-chip {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.4rem 0.6rem;
      background: var(--bg-elevated);
      border-radius: 4px;
      font-size: 0.8rem;
      font-family: monospace;
    }}
  </style>
</head>
<body>

<h1>{name}</h1>
<p class="muted">Theme preview — all UI elements rendered with this palette</p>

<h2>Color Tokens</h2>
<div class="color-grid">
  {"".join(f'<div class="color-chip"><span class="swatch" style="background:{v}"></span>{k}: {v}</div>' for k, v in tokens.items())}
</div>

<h2>Typography Hierarchy</h2>
<h1 style="font-size:2rem">Heading 1 — Primary (accent color)</h1>
<h2>Heading 2 — Section</h2>
<h3>Heading 3 — Subsection</h3>
<p>Body text at full contrast. This is the primary reading experience — long-form content about technical topics like Apache Iceberg metadata trees.</p>
<p class="muted">Muted text — metadata, timestamps, secondary information.</p>
<p class="faint">Faint text — disabled states, line numbers. Never for readable content.</p>
<p><a href="#">This is a link</a> — interactive elements use the link color.</p>
<p>Inline <code>code spans</code> for technical terms and file paths like <code>s3://bucket/table/metadata/</code>.</p>

<h2>Code Block</h2>
<pre><code>def snapshot_isolation(table):
    """Every write creates a new snapshot."""
    manifest = table.current_manifest_list()
    files = manifest.resolve_data_files()
    return ConsistentView(files)</code></pre>

<h2>Callouts</h2>
<div class="key-concept">
  <strong>Key concept:</strong> Iceberg tracks exactly which files belong to a table at any point in time, using a metadata tree stored alongside the data.
</div>
<div class="callout">
  <strong>Note:</strong> The AWS Glue Data Catalog now exposes an Iceberg REST Catalog API, enabling cross-engine access without proprietary connectors.
</div>

<h2>Surfaces & Elevation</h2>
<div class="elevated">
  <strong>Elevated surface</strong> (bg-elevated) — used for tray panels, cards, dropdowns.
  <p class="muted">Muted text on elevated surface — verify this passes 4.5:1.</p>
</div>
<div class="surface">
  <strong>Surface</strong> (bg-surface) — used for tooltips, popovers, highest elevation.
  <p class="muted">Muted text on surface — the most common failure point.</p>
</div>

<h2>Table</h2>
<table>
  <tr><th>Layer</th><th>What it stores</th><th>Where it lives</th></tr>
  <tr><td><strong>Catalog</strong></td><td>Pointer to current metadata file</td><td>AWS Glue</td></tr>
  <tr><td><strong>Manifest list</strong></td><td>Which manifests belong to this snapshot</td><td>S3 metadata/</td></tr>
  <tr><td><strong>Data files</strong></td><td>Actual rows (Parquet)</td><td>S3 data/</td></tr>
</table>

<h2>Details / Collapsible</h2>
<details>
  <summary>How does pruning actually work?</summary>
  <p>Each manifest file records min/max values per column. The engine skips files whose ranges can't match the query predicate.</p>
</details>

<h2>Glossary Term</h2>
<p>Every write creates a new <span class="term">snapshot</span> — a frozen view of which files belong to the table.</p>

<h2>Quiz States</h2>
<div class="quiz-correct">✓ Correct: The catalog pointer updates atomically</div>
<div class="quiz-incorrect">✗ Incorrect: S3 has built-in transaction support</div>

<h2>Contrast Validation</h2>
<table>
  <tr><th>Check</th><th>Sample</th><th>Ratio</th><th>Grade</th><th>Pass</th></tr>
  {contrast_rows}
</table>

</body>
</html>'''
    return html


def main():
    parser = argparse.ArgumentParser(description='Preview and validate a color palette')
    parser.add_argument('--palette', required=True, help='Path to palette JSON')
    parser.add_argument('--serve', type=int, nargs='?', const=8080, help='Serve preview on port')
    parser.add_argument('--css', action='store_true', help='Print CSS :root snippet and exit')
    parser.add_argument('--output', default='.scratch/theme-preview.html', help='Output HTML path')
    args = parser.parse_args()

    palette_path = Path(args.palette)
    if not palette_path.exists():
        print(f'ERROR: palette not found: {palette_path}', file=sys.stderr)
        sys.exit(2)

    with open(palette_path) as f:
        palette = json.load(f)

    tokens = palette['tokens']

    if args.css:
        print(generate_css_snippet(tokens))
        sys.exit(0)

    # Validate
    checks = validate_palette(tokens)
    failures = [c for c in checks if not c['pass']]

    print(f'Palette: {palette["name"]}')
    print(f'Checks: {len(checks) - len(failures)}/{len(checks)} pass')
    for c in checks:
        status = '✓' if c['pass'] else '✗'
        print(f'  {status} {c["label"]}: {c["ratio"]}:1 ({c["grade"]}) — need {c["threshold"]}:1')

    if failures:
        print(f'\nFAIL: {len(failures)} contrast issue(s)')
    else:
        print(f'\nPASS: all contrasts meet AA minimum')

    # Generate preview
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html = generate_preview_html(palette)
    with open(output_path, 'w') as f:
        f.write(html)
    print(f'Preview: {output_path}')

    # Serve if requested
    if args.serve:
        print(f'Serving on http://localhost:{args.serve}/')
        subprocess.run([sys.executable, '-m', 'http.server', str(args.serve)],
                       cwd=str(output_path.parent))

    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
