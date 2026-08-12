#!/usr/bin/env python3
"""
Rebuild a map page's HTML to use the simplified template.

Reads the existing map page, extracts the SVG and topic data from the
topic-card sections, then rewrites the page with:
- Status-colored clickable graph nodes
- Detail panel (no topic cards)
- Dynamic lesson detection
- Auto-reload on generation
- Actionable "Where This Leads" buttons

Usage:
    python tools/rebuild-map-page.py lessons/godot-gamedev-map.html
"""

import re
import sys
from pathlib import Path

def extract_svg(html: str) -> str:
    """Extract the SVG block from the HTML."""
    m = re.search(r'(<svg\b.*?</svg>)', html, re.DOTALL)
    return m.group(1) if m else ''

def rewrite_svg_nodes(svg: str) -> str:
    """Make SVG nodes clickable with status colors (all gray = not-started initially).
    
    Replaces xlink:href="#topic-..." anchors with onclick="selectTopic('...')"
    and adds data-slug attributes, removes the scope text line.
    """
    # Add class="map-graph" to the SVG element
    svg = re.sub(r'<svg\b', '<svg class="map-graph"', svg, count=1)
    
    # Add data-slug to each node group
    def add_data_slug(m):
        node_id = m.group(1)
        # Convert graphviz ID to our slug format
        slug = node_id.replace('&#45;', '-')
        return f'<g id="node_{slug}" class="node" data-slug="{slug}"><title>{node_id}</title>'
    
    svg = re.sub(
        r'<g id="[^"]*" class="node">\s*<title>([^<]+)</title>',
        add_data_slug, svg
    )
    
    # Replace href="#topic-..." with onclick
    svg = re.sub(
        r'<a xlink:href="#topic-([^"]*)"[^>]*>',
        lambda m: f'<a href="javascript:void(0)" onclick="selectTopic(\'{m.group(1)}\')">',
        svg
    )
    
    # Set all node fills to gray (not-started) and stroke-width
    svg = re.sub(
        r'fill="#f3f4f6" stroke="#6b7280"',
        'fill="#e2e8f0" stroke="#64748b" stroke-width="2"',
        svg
    )
    # Blue nodes (in-progress) stay
    svg = re.sub(
        r'fill="#dbeafe" stroke="#2563eb"',
        'fill="#dbeafe" stroke="#2563eb" stroke-width="2"',
        svg
    )
    
    # Remove the scope line (second text element in each node: "◐ substantial", "● deep", etc)
    svg = re.sub(
        r'<text[^>]*>[○◐●]\s*(lightweight|substantial|deep)</text>\n?',
        '', svg
    )
    
    # Soften edge colors
    svg = svg.replace('stroke="#6b7280"', 'stroke="#94a3b8"')
    svg = svg.replace('fill="#6b7280"', 'fill="#94a3b8"')
    
    # Re-fix node strokes (we just replaced them too)
    svg = re.sub(
        r'(fill="#e2e8f0") stroke="#94a3b8"',
        r'\1 stroke="#64748b"',
        svg
    )
    
    return svg

def extract_topics(html: str) -> list[dict]:
    """Extract topic data from topic-card divs."""
    topics = []
    pattern = re.compile(
        r'<div class="topic-card" id="topic-([^"]+)">\s*'
        r'<h3>([^<]+?)(?:\s*<span[^>]*>[^<]*</span>)?\s*</h3>\s*'
        r'<p class="topic-why">([^<]+)</p>\s*'
        r'<p class="topic-scope">Scope:\s*(\w+)\s*·\s*Prereqs:\s*([^<]+)</p>',
        re.DOTALL
    )
    for m in pattern.finditer(html):
        slug, title, why, scope, prereqs = m.groups()
        title = title.strip()
        prereqs = prereqs.strip()
        # Check if there's a lesson link
        lesson_match = re.search(
            rf'id="topic-{re.escape(slug)}".*?href="([^"]+\.html)".*?</div>',
            html, re.DOTALL
        )
        lesson_file = None
        status = 'not-started'
        if lesson_match:
            href = lesson_match.group(1)
            if not href.startswith('#') and not href.endswith('-map.html'):
                lesson_file = href
                status = 'in-progress'
        
        topics.append({
            'slug': slug,
            'title': title,
            'why': why,
            'scope': scope,
            'prereqs': prereqs,
            'status': status,
            'lesson_file': lesson_file,
        })
    return topics

def extract_leads_to(html: str) -> list[str]:
    """Extract leads-to items."""
    m = re.search(r'<div class="leads-to">.*?<ul>(.*?)</ul>', html, re.DOTALL)
    if not m:
        return []
    return re.findall(r'<li>([^<]+)</li>', m.group(1))

def extract_title(html: str) -> str:
    m = re.search(r'<title>Map:\s*(.+?)</title>', html)
    return m.group(1) if m else 'Untitled Map'

def extract_orientation(html: str) -> str:
    m = re.search(r'<p class="orientation">(.+?)</p>', html, re.DOTALL)
    return m.group(1).strip() if m else ''

def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def build_page(title: str, orientation: str, svg: str, topics: list[dict], leads_to: list[str]) -> str:
    """Build the full HTML page."""
    topics_js = ',\n'.join(
        f"  '{t['slug']}': {{\n"
        f"    title: '{t['title'].replace(chr(39), chr(92)+chr(39))}',\n"
        f"    why: '{t['why'].replace(chr(39), chr(92)+chr(39))}',\n"
        f"    scope: '{t['scope']}', prereqs: '{t['prereqs']}', status: '{t['status']}',\n"
        f"    lesson_file: {'\"' + t['lesson_file'] + '\"' if t['lesson_file'] else 'null'}\n"
        f"  }}"
        for t in topics
    )
    
    leads_buttons = '\n'.join(
        f'      <li><button class="btn btn-secondary" onclick="offerGenerate(\'{slugify(item)}\', \'{item}\')">{item}</button></li>'
        for item in leads_to
    )
    
    total = len(topics)
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Map: {title}</title>
  <link rel="stylesheet" href="../assets/style.css">
  <style>
    html {{ scroll-behavior: smooth; }}
    .map-container {{ max-width: 900px; margin: 0 auto; padding: 1rem; }}
    .lesson-nav {{
      padding: 0.5rem 0; margin-bottom: 0.5rem; border-bottom: 1px solid var(--border);
      font-size: 0.85rem; display: flex; justify-content: space-between; align-items: center;
    }}
    .lesson-nav a {{ color: var(--link); text-decoration: none; }}
    .lesson-nav a:hover {{ text-decoration: underline; }}
    .lesson-nav .nav-position {{ color: var(--text-muted); }}
    .orientation {{
      font-size: 1rem; color: var(--text-muted); line-height: 1.6;
      border-left: 4px solid var(--accent); padding-left: 1rem; margin: 1rem 0;
    }}
    .legend {{
      display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.8rem;
      color: var(--text-muted); margin: 0.75rem 0 1.5rem;
    }}
    .legend-item {{ display: flex; align-items: center; gap: 0.3rem; }}
    .legend-swatch {{ width: 14px; height: 14px; border-radius: 3px; border: 2px solid; }}
    .map-graph {{ max-width: 100%; height: auto; cursor: pointer; }}
    .map-graph .node a {{ cursor: pointer; }}
    .map-graph .node:hover polygon,
    .map-graph .node:hover path {{ filter: brightness(1.15); }}
    .detail-panel {{
      border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem;
      background: var(--bg-elevated); margin-top: 1.5rem; display: none;
      animation: fadeIn 0.2s ease;
    }}
    .detail-panel.visible {{ display: block; }}
    .detail-panel h3 {{ margin: 0 0 0.25rem; font-size: 1.1rem; }}
    .detail-panel .detail-why {{ color: var(--text-muted); font-size: 0.9rem; margin: 0.25rem 0 0.75rem; }}
    .detail-panel .detail-meta {{ font-size: 0.8rem; color: var(--text-faint, #888); margin-bottom: 0.75rem; }}
    .detail-panel .detail-actions {{ display: flex; gap: 0.75rem; flex-wrap: wrap; }}
    .detail-panel .btn,.leads-to .btn {{
      padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.85rem;
      cursor: pointer; border: 1px solid var(--border); text-decoration: none;
      display: inline-block; background: var(--bg-surface); color: var(--text);
    }}
    .detail-panel .btn-primary {{ background: var(--accent); color: var(--bg); border-color: var(--accent); }}
    .detail-panel .btn-secondary,.leads-to .btn {{ background: var(--bg-surface); color: var(--accent); border-color: var(--accent); }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-4px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    .leads-to {{
      margin-top: 2rem; padding: 1.25rem; border-radius: 8px;
      background: var(--bg-elevated); border: 1px solid var(--border);
    }}
    .leads-to ul {{ list-style: none; padding: 0; margin: 0.75rem 0 0; display: flex; flex-wrap: wrap; gap: 0.5rem; }}
    .leads-to li {{ margin: 0; }}
    .leads-to .btn {{ font-size: 0.8rem; padding: 0.4rem 0.75rem; }}
    .modal-overlay {{
      display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6);
      z-index: 100; align-items: center; justify-content: center;
    }}
    .modal-overlay.show {{ display: flex; }}
    .modal {{
      background: var(--bg-elevated); border: 1px solid var(--border);
      border-radius: 8px; padding: 1.5rem; max-width: 400px; width: 90%;
    }}
    .modal h3 {{ margin-top: 0; }}
    .modal-actions {{ display: flex; gap: 0.5rem; margin-top: 1rem; }}
    .modal-actions button {{
      padding: 0.4rem 1rem; border-radius: 4px; cursor: pointer;
      border: 1px solid var(--border); font-size: 0.85rem;
    }}
    .modal-actions .primary {{ background: var(--accent); color: var(--bg); border-color: var(--accent); }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  </style>
</head>
<body>

<div class="map-container">
  <nav class="lesson-nav">
    <a href="index.html">← All Lessons</a>
    <span class="nav-position">{total} topics</span>
  </nav>

  <h1>{title}</h1>
  <p class="orientation">{orientation}</p>

  <div class="legend">
    <span class="legend-item"><span class="legend-swatch" style="background:#dcfce7;border-color:#16a34a"></span> Complete</span>
    <span class="legend-item"><span class="legend-swatch" style="background:#dbeafe;border-color:#2563eb"></span> In progress</span>
    <span class="legend-item"><span class="legend-swatch" style="background:#e2e8f0;border-color:#64748b"></span> Not started</span>
  </div>

  {svg}

  <div class="detail-panel" id="detail-panel">
    <h3 id="detail-title"></h3>
    <p class="detail-why" id="detail-why"></p>
    <p class="detail-meta" id="detail-meta"></p>
    <div class="detail-actions" id="detail-actions"></div>
  </div>

  <div class="leads-to">
    <h3>🚀 Where This Leads</h3>
    <p>After this domain, these become accessible:</p>
    <ul>
{leads_buttons}
    </ul>
  </div>
</div>

<!-- Generation modal -->
<div class="modal-overlay" id="gen-modal">
  <div class="modal" style="max-width:400px;">
    <h3 id="gen-title">Generate topic</h3>
    <p id="gen-desc">This topic hasn\\'t been created yet.</p>
    <p id="gen-status" style="display:none; font-size:0.9rem; margin:1rem 0 0; padding:0.75rem; background:var(--code-bg,#f8fafc); border-radius:6px;">
      <span id="gen-spinner" style="display:inline-block; animation:spin 1s linear infinite;">⟳</span>
      <span id="gen-phase-text">Starting...</span>
    </p>
    <div class="modal-actions">
      <button class="primary" id="gen-run-btn" onclick="runGenerate()">▶ Generate</button>
      <button id="gen-cancel-btn" onclick="cancelGenerate()" style="display:none; background:#dc2626; color:white;">Cancel</button>
      <button onclick="closeModal()">Close</button>
    </div>
  </div>
</div>

<script>
const TOPICS = {{
{topics_js}
}};

// --- Detail panel ---
function selectTopic(slug) {{
  const t = TOPICS[slug];
  if (!t) return;
  document.getElementById('detail-title').textContent = t.title;
  document.getElementById('detail-why').textContent = t.why;
  document.getElementById('detail-meta').textContent = `Scope: ${{t.scope}} · Prereqs: ${{t.prereqs}}`;
  const actions = document.getElementById('detail-actions');
  actions.innerHTML = '';
  if (t.lesson_file) {{
    actions.innerHTML = `<a href="${{t.lesson_file}}" class="btn btn-primary">Open lesson →</a>` +
      `<button class="btn btn-secondary" onclick="offerGenerateQuiz('${{slug}}', '${{t.title.replace(/'/g,"\\\\'")}}')">Generate quiz</button>`;
  }} else {{
    actions.innerHTML = `<button class="btn btn-primary" onclick="offerGenerate('${{slug}}', '${{t.title.replace(/'/g,"\\\\'")}}')">▶ Generate this topic</button>` +
      `<button class="btn btn-secondary" onclick="offerGenerateQuiz('${{slug}}', '${{t.title.replace(/'/g,"\\\\'")}}')">Generate quiz</button>`;
  }}
  document.getElementById('detail-panel').classList.add('visible');
  document.getElementById('detail-panel').scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
  document.querySelectorAll('.map-graph .node').forEach(n => n.classList.remove('selected'));
  const node = document.querySelector(`.map-graph .node[data-slug="${{slug}}"]`);
  if (node) node.classList.add('selected');
}}

// --- Generation modal ---
let _genTaskId = null, _genES = null, _genType = 'topic', _genTitle = '', _genCreatedFile = null;

function offerGenerate(slug, title) {{
  _genTitle = title; _genType = 'topic';
  document.getElementById('gen-title').textContent = 'Generate: ' + title;
  resetModal(); document.getElementById('gen-modal').classList.add('show');
}}
function offerGenerateQuiz(slug, title) {{
  _genTitle = title; _genType = 'quiz';
  document.getElementById('gen-title').textContent = 'Generate Quiz: ' + title;
  resetModal(); document.getElementById('gen-modal').classList.add('show');
}}
function resetModal() {{
  document.getElementById('gen-status').style.display = 'none';
  document.getElementById('gen-spinner').style.display = 'inline-block';
  document.getElementById('gen-run-btn').style.display = '';
  document.getElementById('gen-cancel-btn').style.display = 'none';
  document.getElementById('gen-desc').textContent = "This topic hasn't been created yet.";
  _genCreatedFile = null;
}}
async function runGenerate() {{
  const prompt = _genType === 'topic' ? 'teach me about ' + _genTitle : 'generate quick-check questions for ' + _genTitle;
  document.getElementById('gen-run-btn').style.display = 'none';
  document.getElementById('gen-cancel-btn').style.display = '';
  document.getElementById('gen-status').style.display = '';
  document.getElementById('gen-desc').textContent = 'Generating — this takes 30–120 seconds.';
  setPhase('Starting...');
  try {{
    const res = await fetch('/api/generate', {{ method: 'POST', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify({{ prompt, mock: false }}) }});
    if (res.status !== 202) {{ finish('❌ Server error: ' + res.status, false); return; }}
    const data = await res.json(); _genTaskId = data.id;
    _genES = new EventSource(data.stream_url);
    _genES.addEventListener('phase', (e) => {{
      const labels = {{'tool:thinking':'Thinking...','tool:write':'Writing file...','tool:read':'Reading context...','tool:web_search':'Researching...','tool:subagent':'Researching (parallel)...','tool:glob':'Scanning files...','writing':'Writing lesson...','responding':'Finishing up...','complete':'Done','tool_done':null}};
      const label = labels[e.data];
      if (label) setPhase(label);
      else if (e.data.startsWith('creating:')) {{ const p=e.data.slice(9); if(p.includes('lessons/')&&p.endsWith('.html'))_genCreatedFile=p.split('lessons/').pop(); setPhase('Saving...'); }}
      else if (!labels.hasOwnProperty(e.data)) setPhase(e.data);
    }});
    _genES.addEventListener('done', (e) => {{ const r=JSON.parse(e.data); _genES.close(); _genES=null; r.exit_code===0?finish('✅ Done! Opening...',true):finish('⚠️ Exited: '+r.exit_code,false); }});
    _genES.onerror = () => finish('❌ Connection lost', false);
  }} catch(err) {{ finish('❌ '+err.message+' — is the server running?', false); }}
}}
function setPhase(t) {{ document.getElementById('gen-phase-text').textContent = t; }}
function finish(msg, success) {{
  document.getElementById('gen-desc').textContent = msg;
  document.getElementById('gen-cancel-btn').style.display = 'none';
  document.getElementById('gen-spinner').style.display = 'none';
  document.getElementById('gen-phase-text').textContent = success ? 'Complete' : 'Stopped';
  if (success) setTimeout(() => {{ if (_genCreatedFile) window.location.href=_genCreatedFile; else window.location.reload(); }}, 1500);
}}
async function cancelGenerate() {{
  if (_genTaskId) await fetch('/api/generate/'+_genTaskId+'/cancel',{{method:'POST'}});
  if (_genES) {{ _genES.close(); _genES=null; }} finish('🛑 Cancelled', false);
}}
function closeModal() {{ document.getElementById('gen-modal').classList.remove('show'); if(_genES){{_genES.close();_genES=null;}} }}
document.getElementById('gen-modal').addEventListener('click', function(e) {{ if(e.target===this) closeModal(); }});

// --- Detect existing lessons on load ---
(async function() {{
  let files = [];
  try {{ const r = await fetch('/api/lessons'); if(r.ok) files = await r.json(); }} catch(e) {{}}
  let found = 0;
  for (const [slug, topic] of Object.entries(TOPICS)) {{
    if (topic.lesson_file) {{ found++; continue; }}
    const match = files.find(f => slug.split('-').every(p => f.includes(p)) || f.includes(slug));
    if (match) {{
      topic.lesson_file = match; topic.status = 'in-progress'; found++;
      const node = document.querySelector(`.map-graph .node[data-slug="${{slug}}"] path`);
      if (node) {{ node.setAttribute('fill','#dbeafe'); node.setAttribute('stroke','#2563eb'); }}
    }}
  }}
  const nav = document.querySelector('.nav-position');
  if (nav) nav.textContent = `{total} topics · ${{found}} with lessons`;
}})();
</script>
<script src="../assets/theme-toggle.js"></script>
</body>
</html>'''


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/rebuild-map-page.py <map-page.html>")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    html = path.read_text()
    
    title = extract_title(html)
    orientation = extract_orientation(html)
    svg_raw = extract_svg(html)
    svg = rewrite_svg_nodes(svg_raw)
    topics = extract_topics(html)
    leads_to = extract_leads_to(html)
    
    if not topics:
        print(f"ERROR: No topics found in {path}")
        sys.exit(1)
    
    print(f"Rebuilding {path.name}: {title}")
    print(f"  Topics: {len(topics)}")
    print(f"  Leads to: {len(leads_to)} items")
    
    new_html = build_page(title, orientation, svg, topics, leads_to)
    path.write_text(new_html)
    print(f"  Written: {len(new_html)} bytes")


if __name__ == '__main__':
    main()
