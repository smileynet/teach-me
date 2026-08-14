/**
 * LayoutMode.js — Restructures lesson content into collapsible sections.
 *
 * Sections are ALWAYS collapsible (headings become <details>/<summary>).
 * The user preference (sectionsCollapsed) controls whether they start
 * expanded or collapsed.
 *
 * Reads from preferences.js signal. Listens for 'layout-change' event
 * dispatched by TypographyPanel for immediate toggle.
 */

import { prefs } from '../preferences.js';

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

export function applyLayout(collapsed) {
  applySections(collapsed);
}

// Listen for layout changes from the typography panel
window.addEventListener('layout-change', (e) => {
  applySections(e.detail.collapsed);
});

// Apply on load
function init() {
  applySections(prefs.value.sectionsCollapsed);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
