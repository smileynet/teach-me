/**
 * LayoutMode.js — Restructures lesson content into collapsible sections.
 *
 * Sections are ALWAYS collapsible (headings become <details>/<summary>).
 * The user preference controls whether they start expanded or collapsed:
 *   "flow"     — all sections start expanded (default)
 *   "sections" — all sections start collapsed
 *
 * Uses native <details>/<summary> for accessibility:
 *   - Keyboard: Enter/Space to toggle
 *   - Screen readers: expanded/collapsed state announced
 *   - Ctrl+F: works in collapsed sections (hidden="until-found")
 *
 * Reads/writes the "layout" key in the teach-me-typography localStorage object.
 * Listens for a custom "layout-change" event dispatched by TypographyPanel.
 */

const STORAGE_KEY = 'teach-me-typography';

/**
 * Get content elements between headings, grouped by h2.
 */
function getSections() {
  const allH2s = Array.from(document.querySelectorAll('h2'));
  if (allH2s.length === 0) return [];

  const sections = [];
  for (const h2 of allH2s) {
    const section = { heading: h2, content: [] };
    let sibling = h2.nextElementSibling;
    while (sibling && sibling.tagName !== 'H2') {
      section.content.push(sibling);
      sibling = sibling.nextElementSibling;
    }
    sections.push(section);
  }
  return sections;
}

let applied = false;

function applySections(startCollapsed) {
  if (applied) {
    // Already restructured — just toggle open/closed state
    document.querySelectorAll('details.lesson-section').forEach(d => {
      d.open = !startCollapsed;
    });
    document.body.setAttribute('data-layout', 'sections');
    return;
  }

  const sections = getSections();
  if (sections.length === 0) return;

  for (const { heading, content } of sections) {
    const details = document.createElement('details');
    details.className = 'lesson-section';
    details.open = !startCollapsed;

    const summary = document.createElement('summary');
    summary.className = 'section-heading';
    summary.innerHTML = heading.innerHTML;
    summary.setAttribute('role', 'heading');
    summary.setAttribute('aria-level', '2');

    details.appendChild(summary);

    for (const el of content) {
      details.appendChild(el);
    }

    heading.replaceWith(details);
  }

  document.body.setAttribute('data-layout', 'sections');
  applied = true;
}

function applyLayout(mode) {
  const startCollapsed = (mode === 'sections');
  applySections(startCollapsed);
}

function getLayout() {
  try {
    const prefs = JSON.parse(localStorage.getItem(STORAGE_KEY));
    return prefs?.layout || 'flow';
  } catch { return 'flow'; }
}

// Listen for layout changes from the typography panel
window.addEventListener('layout-change', (e) => {
  applyLayout(e.detail.layout);
});

// Apply on load
function init() {
  const layout = getLayout();
  applySections(layout === 'sections');
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

export { applyLayout, getLayout };
