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

function DomainCard({ domain, mission }) {
  const mapUrl = domain.mapHref || `${domain.domain}-map.html`;
  const remaining = domain.total - domain.complete;
  const inProgress = domain.inProgress || 0;

  // Honest stat line: remaining-to-explore + in-progress (previously dead data).
  let stat;
  if (remaining <= 0) {
    stat = '✓ Complete';
  } else {
    stat = `${remaining} to explore`;
    if (inProgress > 0) stat += ` · ${inProgress} in progress`;
  }

  return html`
    <a href=${mapUrl} class="domain-card">
      <div class="domain-card-header">
        <${ProgressRing} complete=${domain.complete} total=${domain.total} />
        <h2>${domain.title}</h2>
      </div>
      <p class="domain-desc">${domain.description}</p>
      <span class="domain-stat">${stat}</span>
      ${mission && mission.why && html`
        <details class="mission-fold">
          <summary>Mission</summary>
          <p class="mission-why">${mission.why}</p>
          ${mission.criteria && mission.criteria.length > 0 && html`
            <ul class="mission-criteria">
              ${mission.criteria.map(c => html`<li>${c}</li>`)}
            </ul>
          `}
        </details>
      `}
    </a>
  `;
}

// One orientation cue, computed from the data already in the island. Exactly one
// state renders: resume (returning user) XOR first-time orientation (empty). Never
// both (one primary action per screen). #271.
function IndexCue({ domains }) {
  // Resume target: first domain with in-progress topics, else the first
  // partially-complete domain. Counts are baked at generation time; on the
  // public library they're 0, so this falls through to the orientation line.
  const resume = domains.find(d => (d.inProgress || 0) > 0)
    || domains.find(d => (d.complete || 0) > 0 && d.complete < d.total);

  if (resume) {
    const mapUrl = resume.mapHref || `${resume.domain}-map.html`;
    return html`
      <p class="index-cue index-cue-resume">
        <a href=${mapUrl}>Continue where you left off → ${resume.title}</a>
      </p>
    `;
  }

  return html`
    <p class="index-cue index-cue-start">
      New here? Pick a domain below to start — each one opens a map of topics.
    </p>
  `;
}

export function IndexView({ domains, stats, mission }) {
  return html`
    <div class="index-view">
      <h1>📚 All Lessons</h1>
      <p class="index-meta">
        ${stats.domainCount} domain${stats.domainCount !== 1 ? 's' : ''} · ${stats.topicCount} topics · ${stats.completeCount} complete
        ${mission && mission.why ? ' · ' : ''}${mission && mission.why ? html`<a href="resources.html" class="resources-link">Sources</a>` : ''}
      </p>

      <${IndexCue} domains=${domains} />

      <div class="domain-grid">
        ${domains.map(d => html`<${DomainCard} domain=${d} mission=${mission} key=${d.domain} />`)}
      </div>
    </div>
  `;
}
