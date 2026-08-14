/**
 * LayoutMode.js — Restructures lesson content into collapsible sections.
 *
 * Modes:
 *   "flow"     — no transformation (default, current behavior)
 *   "sections" — each h2 + its content wrapped in <details> elements
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
 * Returns array of { heading: Element, content: Element[] }
 */
function getSections() {
  const body = document.body;
  const sections = [];
  let current = null;

  // Walk direct children and top-level elements looking for h2 boundaries
  // We only restructure the main lesson content (skip lesson-meta, key-concept at top, scripts at bottom)
  const allH2s = Array.from(document.querySelectorAll('h2'));
  if (allH2s.length === 0) return sections;

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

let originalDOM = null;

function applySections() {
  if (document.body.getAttribute('data-layout') === 'sections') return; // already applied

  const sections = getSections();
  if (sections.length === 0) return;

  // Save original DOM state for revert
  originalDOM = document.body.innerHTML;

  for (const { heading, content } of sections) {
    const details = document.createElement('details');
    details.className = 'lesson-section';
    details.open = true;

    const summary = document.createElement('summary');
    summary.className = 'section-heading';
    summary.innerHTML = heading.innerHTML;
    summary.setAttribute('role', 'heading');
    summary.setAttribute('aria-level', '2');

    details.appendChild(summary);

    // Move content into details
    for (const el of content) {
      details.appendChild(el);
    }

    // Replace the h2 with the details element
    heading.replaceWith(details);
  }

  document.body.setAttribute('data-layout', 'sections');
}

function applyFlow() {
  if (document.body.getAttribute('data-layout') !== 'sections') return;

  if (originalDOM) {
    // Restore original DOM
    document.body.innerHTML = originalDOM;
    originalDOM = null;

    // Re-run component mounts (glossary, lesson actions, typography panel)
    // Dispatch event so other components know to re-mount
    document.body.removeAttribute('data-layout');
    window.dispatchEvent(new CustomEvent('layout-restored'));

    // Re-import components to trigger their auto-mount logic
    import('./GlossaryQuiz.js');
    import('./LessonActions.js');
    import('./TypographyPanel.js');
    // Re-run glossary.js
    const glossaryScript = document.createElement('script');
    glossaryScript.src = '../assets/glossary.js';
    document.body.appendChild(glossaryScript);
  } else {
    document.body.removeAttribute('data-layout');
  }
}

function applyLayout(mode) {
  if (mode === 'sections') {
    applySections();
  } else {
    applyFlow();
  }
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

// Apply on load (after DOM ready)
function init() {
  const layout = getLayout();
  if (layout === 'sections') {
    applySections();
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

export { applyLayout, getLayout };
