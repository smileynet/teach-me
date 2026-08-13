import { h } from 'preact';
import htm from 'htm';

const html = htm.bind(h);

function TrustBadge({ rating }) {
  const stars = (rating.match(/★/g) || []).length;
  const note = rating.replace(/★+\s*/, '').replace(/[()]/g, '').trim();
  return html`
    <span class="trust-badge trust-${stars}">
      ${'★'.repeat(stars)}${'☆'.repeat(3 - stars)}
      ${note && html`<span class="trust-note">${note}</span>`}
    </span>
  `;
}

function SourceCard({ source }) {
  return html`
    <a href=${source.url} class="source-card" target="_blank" rel="noopener">
      <div class="source-header">
        <span class="source-title">${source.title}</span>
        <${TrustBadge} rating=${source.trust} />
      </div>
      <p class="source-covers">${source.covers}</p>
    </a>
  `;
}

function SourceSection({ section }) {
  return html`
    <div class="source-section">
      <h2>${section.name}</h2>
      ${section.note && html`<p class="section-note">${section.note}</p>`}
      <div class="source-grid">
        ${section.sources.map(s => html`<${SourceCard} source=${s} key=${s.url} />`)}
      </div>
    </div>
  `;
}

export function ResourcesView({ sections, title }) {
  const totalSources = sections.reduce((sum, s) => sum + s.sources.length, 0);
  return html`
    <div class="resources-view">
      <h1>${title || 'Resources'}</h1>
      <p class="resources-meta">${totalSources} verified sources across ${sections.length} categories</p>
      ${sections.map(s => html`<${SourceSection} section=${s} key=${s.name} />`)}
    </div>
  `;
}
