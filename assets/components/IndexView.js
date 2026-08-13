import { h } from 'preact';
import htm from 'htm';

const html = htm.bind(h);

function ProgressRing({ complete, total, size = 48 }) {
  const radius = (size - 6) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = total > 0 ? complete / total : 0;
  const offset = circumference * (1 - pct);

  return html`
    <svg width=${size} height=${size} viewBox="0 0 ${size} ${size}" class="progress-ring">
      <circle cx=${size / 2} cy=${size / 2} r=${radius}
        fill="none" stroke="var(--border)" stroke-width="3" />
      <circle cx=${size / 2} cy=${size / 2} r=${radius}
        fill="none" stroke="var(--success)" stroke-width="3"
        stroke-dasharray=${circumference} stroke-dashoffset=${offset}
        stroke-linecap="round" transform="rotate(-90 ${size / 2} ${size / 2})" />
      <text x=${size / 2} y=${size / 2 + 4} text-anchor="middle"
        fill="var(--text-muted)" font-size="11">${complete}/${total}</text>
    </svg>
  `;
}

function DomainCard({ domain }) {
  const mapUrl = `${domain.domain}-map.html`;
  const remaining = domain.total - domain.complete;

  return html`
    <a href=${mapUrl} class="domain-card">
      <div class="domain-card-header">
        <${ProgressRing} complete=${domain.complete} total=${domain.total} />
        <h2>${domain.title}</h2>
      </div>
      <p class="domain-desc">${domain.description}</p>
      <span class="domain-stat">${remaining > 0 ? remaining + ' to explore' : '✓ Complete'}</span>
    </a>
  `;
}

export function IndexView({ domains, stats, mission }) {
  return html`
    <div class="index-view">
      <h1>📚 All Lessons</h1>
      <p class="index-meta">${stats.domainCount} domain${stats.domainCount !== 1 ? 's' : ''} · ${stats.topicCount} topics · ${stats.completeCount} complete</p>
      
      ${mission && mission.why && html`
        <div class="mission-block">
          <p class="mission-why">${mission.why}</p>
          ${mission.criteria && mission.criteria.length > 0 && html`
            <ul class="mission-criteria">
              ${mission.criteria.map(c => html`<li>${c}</li>`)}
            </ul>
          `}
        </div>
      `}

      <div class="domain-grid">
        ${domains.map(d => html`<${DomainCard} domain=${d} key=${d.domain} />`)}
      </div>
    </div>
  `;
}
