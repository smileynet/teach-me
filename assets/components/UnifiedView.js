// UnifiedView — the unified aggregate landing page (#276): one #page-data island, two
// views (Tree | Map) over one domain graph, a persisted toggle.
//
// Header (mission meta + the #271 orientation/resume cue + the toggle) sits ABOVE both
// views. Each view gets only {domains, edges, islands}. Both views are RENDERED and swapped
// with CSS display:none (NOT conditional unmount) so each keeps its scroll/hover/focus state
// across toggles. The active view comes from prefs.mapView, read REACTIVELY via the signal.
//
// View selection on load (resolved by the page bootstrap, not here): ?view=map ?? stored
// pref ?? 'tree'. The toggle writes prefs (auto-persists) + history.replaceState(?view=).
import { h } from 'preact';
import htm from 'htm';
import { prefs, set as setPref } from '../preferences.js';
import { IndentedTreeView } from './IndentedTreeView.js';
import { IteratedMapView } from './IteratedMapView.js';

const html = htm.bind(h);

// One orientation cue, computed from the island data. Resume (returning) XOR first-time
// orientation (empty). Kept byte-compatible with IndexView's #271 cue so verify's
// index_cue_present assertion (exactly one .index-cue) still holds.
function IndexCue({ domains }) {
  const resume = domains.find(d => (d.inProgress || 0) > 0)
    || domains.find(d => (d.complete || 0) > 0 && d.complete < d.total);
  if (resume) {
    const mapUrl = resume.mapHref || `${resume.domain}-map.html`;
    return html`<p class="index-cue index-cue-resume">
      <a href=${mapUrl}>Continue where you left off → ${resume.title}</a>
    </p>`;
  }
  // All-complete (#282): distinct affirming cue — never fall through to first-time
  // orientation (false status → distrust). Reached only after resume failed.
  const allComplete = domains.length > 0
    && domains.every(d => (d.total || 0) > 0 && (d.complete || 0) >= d.total);
  if (allComplete) {
    return html`<p class="index-cue index-cue-done">
      You've completed every topic here. Explore a new domain or revisit one to go deeper.
    </p>`;
  }
  return html`<p class="index-cue index-cue-start">
    New here? Pick a domain below to start — each one opens a map of topics.
  </p>`;
}

function ViewToggle({ view, onChange }) {
  return html`<div class="view-toggle" role="tablist" aria-label="View mode">
    <button type="button" role="tab" class=${'vt-btn' + (view === 'tree' ? ' is-active' : '')}
      aria-selected=${view === 'tree' ? 'true' : 'false'} onClick=${() => onChange('tree')}>Tree</button>
    <button type="button" role="tab" class=${'vt-btn' + (view === 'map' ? ' is-active' : '')}
      aria-selected=${view === 'map' ? 'true' : 'false'} onClick=${() => onChange('map')}>Map</button>
  </div>`;
}

// Demo takeover control (#279). Shown ONLY when the page is displaying the demo progress
// floor (no user overlay yet, not owning). Clicking sets hasOwnProgress and reloads so the
// bootstrap re-resolves with an empty user overlay — demo counts clear to the user's own
// (initially empty) progress. Labeled unmistakably so demo data is never mistaken for real.
function DemoBanner() {
  const startMine = () => {
    setPref('hasOwnProgress', true);   // UI state (ADR 0016) — not a learner-state store
    try { window.location.reload(); } catch {}
  };
  return html`<p class="index-demo-note">
    Showing sample progress so you can explore.
    ${' '}<button type="button" class="index-demo-start" onClick=${startMine}>Start my own progress</button>
  </p>`;
}

export function UnifiedView({ domains, edges, islands, stats, mission, showingDemo }) {
  const view = prefs.value.mapView === 'map' ? 'map' : 'tree';

  const onChange = (next) => {
    if (next === view) return;
    setPref('mapView', next);               // auto-persists to teach-me-prefs-v1
    try {
      const url = new URL(window.location.href);
      if (next === 'map') url.searchParams.set('view', 'map');
      else url.searchParams.delete('view');
      window.history.replaceState(null, '', url);  // replace, not push (no back-button spam)
    } catch {}
  };

  const treeDomains = domains;  // tree filters roots itself (depth===0 && !island)

  return html`<div class="index-view unified-view">
    <h1>📚 All Lessons</h1>
    <p class="index-meta">
      ${stats.domainCount} domain${stats.domainCount !== 1 ? 's' : ''} · ${stats.topicCount} topics · ${stats.completeCount} complete
    </p>

    <${IndexCue} domains=${domains} />
    ${showingDemo ? html`<${DemoBanner} />` : ''}
    <${ViewToggle} view=${view} onChange=${onChange} />

    <div class="view-pane" style=${view === 'tree' ? '' : 'display:none'}>
      <${IndentedTreeView} domains=${treeDomains} edges=${edges} islands=${islands} />
    </div>
    <div class="view-pane" style=${view === 'map' ? '' : 'display:none'}>
      <${IteratedMapView} domains=${domains} edges=${edges} islands=${islands} />
    </div>
  </div>`;
}
