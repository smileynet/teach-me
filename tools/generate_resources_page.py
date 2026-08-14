#!/usr/bin/env python3
"""Generate a themed resources page from RESOURCES.md.

Parses the markdown table format and produces a Preact page with
source cards showing title, URL, trust rating, and coverage description.

Usage:
    python tools/generate_resources_page.py --workspace workspace --output workspace/resources.html
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def parse_resources_md(path: Path) -> dict:
    """Parse RESOURCES.md into structured sections with source entries."""
    content = path.read_text(encoding="utf-8")

    # Extract title (first # heading)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Resources"

    sections = []
    # Split by ## headings
    parts = re.split(r'^##\s+(.+)$', content, flags=re.MULTILINE)

    # parts[0] is before first ##, then alternating (heading, body)
    for i in range(1, len(parts), 2):
        section_name = parts[i].strip()
        section_body = parts[i + 1] if i + 1 < len(parts) else ""

        sources = []
        # Parse markdown table rows: | [Title](URL) | Covers | Trust |
        for row in re.finditer(
            r'\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*([^|]+)\|\s*([^|]+)\|',
            section_body
        ):
            source_title = row.group(1).strip()
            url = row.group(2).strip()
            covers = row.group(3).strip()
            trust = row.group(4).strip()
            sources.append({
                "title": source_title,
                "url": url,
                "covers": covers,
                "trust": trust,
            })

        # Extract any note paragraphs (non-table text that's not a header)
        note_lines = []
        for line in section_body.splitlines():
            line = line.strip()
            if line and not line.startswith('|') and not line.startswith('Source') and not line.startswith('---'):
                if '**Key' in line or '**Note' in line or line.startswith('**'):
                    note_lines.append(re.sub(r'\*\*([^*]+)\*\*', r'\1', line))

        note = ' '.join(note_lines) if note_lines else None

        if sources:
            sections.append({
                "name": section_name,
                "sources": sources,
                "note": note,
            })

    return {"title": title, "sections": sections}


def generate_page(resources_data: dict, domain: str = "", domain_slug: str = "") -> str:
    """Generate the Preact resources page."""
    sys.path.insert(0, str(PROJECT_ROOT / "tools"))
    from lib.page_template import render_resources_page

    data = resources_data

    module_script = """
    import { h, render } from 'preact';
    import htm from 'htm';
    import { ResourcesView } from '../assets/components/ResourcesView.js';

    const html = htm.bind(h);
    const data = JSON.parse(document.getElementById('page-data').textContent);

    render(
      html`<${ResourcesView} sections=${data.sections} title=${data.title} />`,
      document.getElementById('app')
    );
"""

    css_extra = """
    body { max-width: 900px; margin: 0 auto; padding: 2rem; }
    .resources-view h1 { font-size: 1.5rem; margin-bottom: 0.3rem; }
    .resources-meta { color: var(--text-muted); font-size: 0.85rem; margin-bottom: 2rem; }
    .source-section { margin-bottom: 2rem; }
    .source-section h2 { font-size: 1.1rem; margin-bottom: 0.75rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }
    .section-note { font-size: 0.83rem; color: var(--text-muted); margin-bottom: 0.75rem; line-height: 1.5; }
    .source-grid { display: flex; flex-direction: column; gap: 0.5rem; }
    .source-card {
      display: block; padding: 0.75rem 1rem; background: var(--bg-elevated);
      border: 1px solid var(--border); border-radius: 8px; text-decoration: none;
      color: var(--text); transition: border-color 0.15s;
    }
    .source-card:hover { border-color: var(--accent); }
    .source-header { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem; }
    .source-title { font-weight: 500; font-size: 0.9rem; color: var(--link); }
    .source-covers { font-size: 0.8rem; color: var(--text-muted); margin: 0; line-height: 1.4; }
    .trust-badge { font-size: 0.75rem; white-space: nowrap; }
    .trust-3 { color: var(--success); }
    .trust-2 { color: var(--warning); }
    .trust-1 { color: var(--text-muted); }
    .trust-note { font-size: 0.7rem; color: var(--text-faint); margin-left: 0.3rem; }
"""

    # Use title from RESOURCES.md as domain name if domain not provided
    effective_domain = domain or data.get("title", "Resources")
    effective_slug = domain_slug

    return render_resources_page(
        title=data.get("title", "Resources"),
        domain=effective_domain,
        domain_slug=effective_slug,
        body_content='<div id="app"></div>',
        data=data,
        module_script=module_script,
        css_extra=css_extra,
        depth=1,
    )


def main():
    args = sys.argv[1:]

    workspace = PROJECT_ROOT / "workspace"
    if "--workspace" in args:
        idx = args.index("--workspace")
        if idx + 1 < len(args):
            workspace = Path(args[idx + 1])
            if not workspace.is_absolute():
                workspace = PROJECT_ROOT / workspace

    domain = ""
    if "--domain" in args:
        idx = args.index("--domain")
        if idx + 1 < len(args):
            domain = args[idx + 1]

    domain_slug = ""
    if "--domain-slug" in args:
        idx = args.index("--domain-slug")
        if idx + 1 < len(args):
            domain_slug = args[idx + 1]

    resources_path = workspace / "RESOURCES.md"
    if not resources_path.exists():
        print(f"RESOURCES.md not found at {resources_path}")
        sys.exit(1)

    output = workspace / "resources.html"
    if "--output" in args:
        idx = args.index("--output")
        if idx + 1 < len(args):
            output = Path(args[idx + 1])
            if not output.is_absolute():
                output = PROJECT_ROOT / output

    resources_data = parse_resources_md(resources_path)
    html = generate_page(resources_data, domain=domain, domain_slug=domain_slug)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")

    total = sum(len(s["sources"]) for s in resources_data["sections"])
    print(f"✓ Generated {output.name} ({total} sources in {len(resources_data['sections'])} sections)")


if __name__ == "__main__":
    main()
