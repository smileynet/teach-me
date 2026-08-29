#!/usr/bin/env python3
"""Map-edge connectivity gate (#261 — hardens #257).

Two-tier oracle, identity-first (research 2026-08-29): pixels/bbox alone can't tell the
correct node pair from a plausible-wrong pair, so we assert against the DATA MODEL.

For every committed map (and one synthetic `related` map):
  Tier 1 (exact): the set of rendered edges (path[data-source][data-target][data-type])
    equals the expected set from load_map(MAP.md).edges — same ids, same types, same count.
  Tier 2 (geometry): each rendered edge's two endpoints land within the bounding boxes of
    its data-source / data-target cards (data-topic-id) — no detached/misrouted endpoints.
  Plus: 0 console errors, and `related` edges render dashed + no arrowhead.

Serves each workspace via serve.py (mounts /assets from project root — plain http.server
404s on the map's ../assets depth-prefix). Structured JSON to stdout; exit 0 pass / 1 fail
/ 2 error.

Usage:
    python tools/check-map-edges.py            # all committed maps + synthetic related
    python tools/check-map-edges.py --json      # JSON only
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import map_parser as mp  # noqa: E402

PORT = 8791
TOL = 12  # px tolerance for Tier-2 endpoint-in-card containment

# In-page JS: read rendered edges (data-*) + card bounding boxes, map SVG user space to
# viewport via getScreenCTM, return everything the Python oracle needs.
_PROBE = r"""() => {
  const cards = {};
  document.querySelectorAll('.topic-card[data-topic-id]').forEach(c => {
    const r = c.getBoundingClientRect();
    cards[c.getAttribute('data-topic-id')] = {x:r.x, y:r.y, w:r.width, h:r.height};
  });
  const edges = [];
  document.querySelectorAll('.edge-layer path[data-source]').forEach(p => {
    const L = p.getTotalLength();
    const a = p.getPointAtLength(0), z = p.getPointAtLength(L);
    const m = p.getScreenCTM();
    const toClient = (pt) => ({x: pt.x*m.a + pt.y*m.c + m.e, y: pt.x*m.b + pt.y*m.d + m.f});
    const A = toClient(a), Z = toClient(z);
    edges.push({
      source: p.getAttribute('data-source'),
      target: p.getAttribute('data-target'),
      type: p.getAttribute('data-type'),
      dashed: (p.getAttribute('stroke-dasharray') || 'none') !== 'none',
      arrow: (p.getAttribute('marker-end') || 'none') !== 'none',
      x1: A.x, y1: A.y, x2: Z.x, y2: Z.y,
    });
  });
  return {cards, edges};
}"""


def _expected_edges(map_path: Path) -> list[dict]:
    dm = mp.load_map(map_path)
    # Only edges whose endpoints are in THIS map render (cross-map dangling refs don't).
    ids = {t.id for t in dm.topics}
    return [
        {"source": e.source_id, "target": e.target_id, "type": e.type}
        for e in dm.edges
        if e.source_id in ids and e.target_id in ids
    ]


def _check_one(page, url: str, expected: list[dict]) -> dict:
    errors: list[str] = []
    console_errors: list[str] = []
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: console_errors.append(str(e)))
    page.goto(url, wait_until="domcontentloaded")
    # Wait for MapView to finish dagre layout (no arbitrary sleeps).
    try:
        page.wait_for_function("() => document.querySelector('.dag-canvas[data-render-complete]')", timeout=10000)
    except Exception:
        return {"url": url, "status": "fail", "errors": ["render-complete flag never set"],
                "expected": len(expected), "rendered": 0}

    probe = page.evaluate(_PROBE)
    cards, rendered = probe["cards"], probe["edges"]

    # Tier 1 — exact identity match (source, target, type), including count.
    exp_set = {(e["source"], e["target"], e["type"]) for e in expected}
    ren_set = {(e["source"], e["target"], e["type"]) for e in rendered}
    missing = exp_set - ren_set
    extra = ren_set - exp_set
    if missing:
        errors.append(f"missing edges (expected, not rendered): {sorted(missing)[:3]}")
    if extra:
        errors.append(f"extra edges (rendered, not expected): {sorted(extra)[:3]}")
    if len(rendered) != len(expected):
        errors.append(f"edge count mismatch: rendered {len(rendered)} vs expected {len(expected)}")

    # Tier 2 — endpoints land within the CORRECT source/target cards.
    def in_card(x, y, cid):
        c = cards.get(cid)
        if not c:
            return False
        return (c["x"] - TOL <= x <= c["x"] + c["w"] + TOL and
                c["y"] - TOL <= y <= c["y"] + c["h"] + TOL)

    detached = 0
    for e in rendered:
        # endpoint nearest source should be in source card; nearest target in target card.
        src_ok = in_card(e["x1"], e["y1"], e["source"]) or in_card(e["x2"], e["y2"], e["source"])
        tgt_ok = in_card(e["x1"], e["y1"], e["target"]) or in_card(e["x2"], e["y2"], e["target"])
        if not (src_ok and tgt_ok):
            detached += 1
    if detached:
        errors.append(f"{detached} edge(s) with an endpoint not on its source/target card")

    # Styling: related dashed + no arrow; prereq/leads_to solid + arrow.
    for e in rendered:
        if e["type"] == "related" and (not e["dashed"] or e["arrow"]):
            errors.append(f"related edge {e['source']}->{e['target']} not dashed/no-arrow")
        if e["type"] in ("prereq", "leads_to") and e["dashed"]:
            errors.append(f"{e['type']} edge {e['source']}->{e['target']} should be solid")

    if console_errors:
        errors.append(f"console errors: {console_errors[:2]}")

    return {"url": url, "status": "pass" if not errors else "fail",
            "expected": len(expected), "rendered": len(rendered), "detached": detached,
            "errors": errors}


def _committed_maps() -> list[tuple[Path, Path, str]]:
    """(map_md_path, workspace, url_path) for each committed example map."""
    out = []
    for html in sorted(ROOT.glob("examples/*/lessons/*-map.html")):
        workspace = html.parent.parent          # examples/{domain}
        domain = html.stem[:-4]                  # strip '-map'
        mapmd = next(workspace.glob(f"maps/{domain}.MAP.md"), None)
        if mapmd:
            out.append((mapmd, workspace, f"lessons/{html.name}"))
    return out


def _serve(workspace: Path):
    return subprocess.Popen(
        [sys.executable, "tools/serve.py", "--workspace", str(workspace), "--port", str(PORT)],
        cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _synthetic_related() -> tuple[Path, Path, str]:
    """Build a temp workspace with a map that has ONE soft_prereq → related edge."""
    from lib import ulid
    ws = Path(tempfile.mkdtemp(prefix="synthmap-"))
    (ws / "maps").mkdir()
    (ws / "lessons").mkdir()
    aid, bid = ulid.new(), ulid.new()
    (ws / "maps" / "synth.MAP.md").write_text(
        "---\ndomain: synth\ndescription: \"s\"\ndepth: 0\nparent: null\n---\n\n# Synth\n\n"
        "## Orientation\n\nx.\n\n## Topics\n\n"
        f"### alpha\n- **id:** {aid}\n- **title:** Alpha\n- **prereqs:** []\n- **status:** not-started\n\n"
        f"### beta\n- **id:** {bid}\n- **title:** Beta\n- **prereqs:** []\n- **soft_prereqs:** [alpha]\n- **status:** not-started\n",
        encoding="utf-8")
    # Generate the map page into ws/lessons via the generator.
    import generate_map_page as gmp
    gmp.set_workspace(ws)
    data = gmp.parse_map_md(ws / "maps" / "synth.MAP.md")
    out = ws / "lessons" / "synth-map.html"
    out.write_text(gmp.generate_preact_map_page(data, out, None), encoding="utf-8")
    return (ws / "maps" / "synth.MAP.md", ws, "lessons/synth-map.html")


def main() -> int:
    from playwright.sync_api import sync_playwright

    targets = _committed_maps()
    synth = _synthetic_related()
    targets.append(synth)

    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for mapmd, workspace, url_path in targets:
            expected = _expected_edges(mapmd)
            srv = _serve(workspace)
            time.sleep(2.0)
            try:
                ctx = browser.new_context(viewport={"width": 1400, "height": 1200})
                page = ctx.new_page()
                r = _check_one(page, f"http://127.0.0.1:{PORT}/{url_path}", expected)
                r["map"] = mapmd.name
                results.append(r)
                ctx.close()
            finally:
                srv.terminate()
                srv.wait()
        browser.close()

    failed = [r for r in results if r["status"] != "pass"]
    report = {"status": "pass" if not failed else "fail",
              "maps": len(results), "failed": len(failed), "results": results}
    print(json.dumps(report, indent=2))
    for r in results:
        flag = "OK " if r["status"] == "pass" else "FAIL"
        print(f"  [{flag}] {r['map']}: expected={r['expected']} rendered={r['rendered']} "
              f"detached={r.get('detached','?')}" + (f" -- {r['errors']}" if r["errors"] else ""))
    return 0 if not failed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        print(json.dumps({"status": "error", "errors": [str(e)]}))
        raise SystemExit(2)
