// IndentedTreeView — the PRIMARY navigation view of the domain forest (#276).
//
// A WAI-ARIA tree (role=tree/treeitem/group): parent/child is the DOM nesting, which IS
// the accessible artifact (no separate a11y fallback). Roots are depth-0 domains; depth-1
// sub-maps nest under their parent; `leads_to` shows inline as "→ also leads to X". Islands
// (domains no structural edge touches) render as a second flat tree.
//
// Keyboard model (W3C ARIA APG Tree View): ROVING TABINDEX — exactly one treeitem is
// tabindex=0, the rest -1; arrows move real DOM focus and rewrite tabindex. Never mixed with
// aria-activedescendant. Handlers: Down/Up = next/prev VISIBLE item; Right = expand (or focus
// first child if already open); Left = collapse (or focus parent); Home/End = first/last
// visible; Enter = activate (follow the link); type-ahead = jump to next item whose title
// starts with the typed character(s). aria-expanded lives on PARENT items only; toggling it
// keeps focus on the node.
import { h } from 'preact';
import { useRef, useState, useCallback, useMemo } from 'preact/hooks';
import htm from 'htm';

const html = htm.bind(h);

function Ring({ complete, total }) {
  const pct = total > 0 ? complete / total : 0;
  const r = 9, c = 2 * Math.PI * r, off = c * (1 - pct);
  const color = pct >= 1 ? 'var(--success)' : pct > 0 ? 'var(--accent)' : 'var(--text-muted)';
  return html`<span class="dc-ring" aria-hidden="true"><svg width="22" height="22" viewBox="0 0 22 22">
    <circle cx="11" cy="11" r=${r} fill="none" stroke="var(--border)" stroke-width="2.5" />
    <circle cx="11" cy="11" r=${r} fill="none" stroke=${color} stroke-width="2.5" stroke-dasharray=${c} stroke-dashoffset=${off} transform="rotate(-90 11 11)" stroke-linecap="round" /></svg></span>`;
}

// Flatten the forest into the VISIBLE, ordered list of nodes (respecting collapse state).
// Used for roving-focus arrow navigation + type-ahead. Each entry: {slug, level, hasKids}.
function flattenVisible(roots, childrenOf, collapsed) {
  const out = [];
  const walk = (slug, level) => {
    const kids = childrenOf[slug] || [];
    out.push({ slug, level, hasKids: kids.length > 0 });
    if (kids.length > 0 && !collapsed[slug]) kids.forEach(k => walk(k, level + 1));
  };
  roots.forEach(r => walk(r, 1));
  return out;
}

function TreeItem({ domain, childrenOf, byslug, leadsFrom, level, posinset, setsize,
                    collapsed, focusSlug, onToggle, onFocusSlug, itemRef }) {
  const kids = (childrenOf[domain.slug] || []).map(s => byslug[s]).filter(Boolean);
  const hasKids = kids.length > 0;
  const isOpen = hasKids && !collapsed[domain.slug];
  const remaining = domain.total - domain.complete;
  const stat = remaining > 0
    ? `${remaining} to explore${domain.inProgress ? ` · ${domain.inProgress} in progress` : ''}`
    : '✓ done';
  const leads = leadsFrom[domain.slug];
  const isFocus = focusSlug === domain.slug;

  return html`<li role="treeitem"
      class="ti"
      aria-level=${level}
      aria-posinset=${posinset}
      aria-setsize=${setsize}
      aria-expanded=${hasKids ? String(isOpen) : undefined}>
    <a class=${'ti-row' + (domain.depth > 0 ? ' is-child' : '')}
       href=${domain.mapHref}
       data-domain=${domain.slug}
       tabindex=${isFocus ? 0 : -1}
       ref=${isFocus ? itemRef : undefined}
       onFocus=${() => onFocusSlug(domain.slug)}>
      ${hasKids && html`<button type="button" class="ti-twisty" tabindex="-1" aria-hidden="true"
          onClick=${(e) => { e.preventDefault(); e.stopPropagation(); onToggle(domain.slug); }}>${isOpen ? '▾' : '▸'}</button>`}
      <${Ring} complete=${domain.complete} total=${domain.total} />
      <span class="ti-title">${domain.title}</span>
      ${domain.depth > 0 && html`<span class="dc-sub-badge">sub-map</span>`}
      <span class="ti-stat">${stat}</span>
      ${leads && leads.length > 0 && html`<span class="ti-leads">→ also leads to ${leads.join(', ')}</span>`}
    </a>
    ${isOpen && html`<ul role="group" class="ti-group">
      ${kids.map((k, i) => html`<${TreeItem} domain=${k} childrenOf=${childrenOf} byslug=${byslug}
        leadsFrom=${leadsFrom} level=${level + 1} posinset=${i + 1} setsize=${kids.length}
        collapsed=${collapsed} focusSlug=${focusSlug} onToggle=${onToggle}
        onFocusSlug=${onFocusSlug} itemRef=${itemRef} key=${k.slug} />`)}
    </ul>`}
  </li>`;
}

export function IndentedTreeView({ domains, edges, islands }) {
  const byslug = useMemo(() => Object.fromEntries(domains.map(d => [d.slug, d])), [domains]);
  const childrenOf = useMemo(() => {
    const m = {};
    (edges || []).filter(e => e.type === 'parent').forEach(e => (m[e.source] ||= []).push(e.target));
    return m;
  }, [edges]);
  const leadsFrom = useMemo(() => {
    const m = {};
    (edges || []).filter(e => e.type === 'leads_to')
      .forEach(e => (m[e.source] ||= []).push(byslug[e.target]?.title || e.target));
    return m;
  }, [edges, byslug]);

  const islandSet = useMemo(() => new Set(islands || []), [islands]);
  const roots = useMemo(
    () => domains.filter(d => d.depth === 0 && !islandSet.has(d.slug)).map(d => d.slug),
    [domains, islandSet]);
  const islandRoots = useMemo(
    () => [...islandSet].filter(s => byslug[s]).map(s => s),
    [islandSet, byslug]);

  const [collapsed, setCollapsed] = useState({});
  // Roving focus: the one treeitem that carries tabindex=0. Defaults to the first root.
  const allRoots = [...roots, ...islandRoots];
  const [focusSlug, setFocusSlug] = useState(allRoots[0]);
  const itemRef = useRef(null);
  const typeahead = useRef({ str: '', at: 0 });

  const visible = useMemo(
    () => flattenVisible(allRoots, childrenOf, collapsed),
    [allRoots, childrenOf, collapsed]);

  const moveFocus = useCallback((slug) => {
    setFocusSlug(slug);
    // Focus the DOM node on the next tick (after the ref points at the new item).
    requestAnimationFrame(() => itemRef.current && itemRef.current.focus());
  }, []);

  const onToggle = useCallback((slug) => {
    setCollapsed(c => ({ ...c, [slug]: !c[slug] }));
  }, []);

  const onKeyDown = useCallback((e) => {
    const idx = visible.findIndex(v => v.slug === focusSlug);
    if (idx < 0) return;
    const cur = visible[idx];
    const kids = childrenOf[cur.slug] || [];
    const isOpen = kids.length > 0 && !collapsed[cur.slug];

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (idx < visible.length - 1) moveFocus(visible[idx + 1].slug);
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (idx > 0) moveFocus(visible[idx - 1].slug);
        break;
      case 'ArrowRight':
        e.preventDefault();
        if (kids.length > 0) {
          if (!isOpen) onToggle(cur.slug);          // closed → open (focus stays)
          else moveFocus(kids[0]);                   // open → first child
        }
        break;
      case 'ArrowLeft':
        e.preventDefault();
        if (isOpen) onToggle(cur.slug);              // open → close (focus stays)
        else if (cur.level > 1) {                    // child → parent
          const parent = visible.slice(0, idx).reverse().find(v => v.level === cur.level - 1);
          if (parent) moveFocus(parent.slug);
        }
        break;
      case 'Home':
        e.preventDefault();
        moveFocus(visible[0].slug);
        break;
      case 'End':
        e.preventDefault();
        moveFocus(visible[visible.length - 1].slug);
        break;
      default:
        // Type-ahead: printable single char → next visible item whose title starts with it.
        if (e.key.length === 1 && !e.metaKey && !e.ctrlKey && !e.altKey) {
          const now = Date.now();
          const ta = typeahead.current;
          ta.str = now - ta.at > 600 ? e.key : ta.str + e.key;
          ta.at = now;
          const needle = ta.str.toLowerCase();
          const order = [...visible.slice(idx + 1), ...visible.slice(0, idx + 1)];
          const hit = order.find(v => (byslug[v.slug]?.title || '').toLowerCase().startsWith(needle));
          if (hit) moveFocus(hit.slug);
        }
    }
  }, [visible, focusSlug, childrenOf, collapsed, byslug, moveFocus, onToggle]);

  const renderTree = (rootSlugs, label) => html`<ul role="tree" aria-label=${label} class="ti-root" onKeyDown=${onKeyDown}>
    ${rootSlugs.map((s, i) => html`<${TreeItem} domain=${byslug[s]} childrenOf=${childrenOf}
      byslug=${byslug} leadsFrom=${leadsFrom} level=${1} posinset=${i + 1} setsize=${rootSlugs.length}
      collapsed=${collapsed} focusSlug=${focusSlug} onToggle=${onToggle}
      onFocusSlug=${setFocusSlug} itemRef=${itemRef} key=${s} />`)}
  </ul>`;

  return html`<div class="indented-tree">
    ${renderTree(roots, 'Domain map')}
    ${islandRoots.length > 0 && html`
      <h2 class="sc-section-title">Standalone domains</h2>
      ${renderTree(islandRoots, 'Standalone domains')}`}
  </div>`;
}
