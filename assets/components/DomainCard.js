import { h } from 'preact';
import htm from 'htm';

const html = htm.bind(h);

// A progress ring: circumference-based stroke-dashoffset for the completed fraction.
// Color pairs with the numeric label (color-not-alone).
function Ring({ complete, total }) {
  const pct = total > 0 ? complete / total : 0;
  const r = 14, c = 2 * Math.PI * r;
  const off = c * (1 - pct);
  const color = pct >= 1 ? 'var(--success)' : pct > 0 ? 'var(--accent)' : 'var(--text-muted)';
  return html`
    <span class="dc-ring" aria-label="${complete} of ${total} complete">
      <svg width="34" height="34" viewBox="0 0 34 34">
        <circle cx="17" cy="17" r=${r} fill="none" stroke="var(--border)" stroke-width="3" />
        <circle cx="17" cy="17" r=${r} fill="none" stroke=${color} stroke-width="3"
          stroke-dasharray=${c} stroke-dashoffset=${off}
          transform="rotate(-90 17 17)" stroke-linecap="round" />
        <text x="17" y="21" text-anchor="middle" font-size="10" fill="var(--text-muted)">${complete}/${total}</text>
      </svg>
    </span>
  `;
}

export function DomainCard({ domain, position }) {
  const isChild = domain.depth > 0;
  const cls = 'domain-card' + (isChild ? ' is-child' : '');
  return html`
    <a class=${cls} href=${domain.mapHref}
       data-domain=${domain.slug}
       style="left:${position.x}px; top:${position.y}px">
      <h3>
        ${domain.title}
        ${isChild && html`<span class="dc-sub-badge">sub-map</span>`}
        ${(domain.private || domain.hasPrivate) && html`<span class="dc-private-badge" title="Local-only — not committed">private</span>`}
      </h3>
      <div class="dc-meta">
        <${Ring} complete=${domain.complete} total=${domain.total} />
        ${' '}${domain.total} topics${domain.inProgress ? `, ${domain.inProgress} in progress` : ''}
      </div>
    </a>
  `;
}
