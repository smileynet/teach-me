/**
 * page-shell.js — THE single entry point for all lesson/reference/quiz page behavior.
 *
 * Initialization order (explicit, not racing):
 *   1. Preferences already loaded (signals populated from localStorage via import)
 *   2. Layout restructuring (must happen before glossary attaches to .term elements)
 *   3. Glossary (annotates terms, attaches hover/click/tray listeners)
 *   4. LessonActions (bottom bar — creates mount point)
 *   5. TypographyPanel (fixed position panel — creates mount point)
 *
 * Adding a new component:
 *   1. Export a mount/init function from the component
 *   2. Import it here
 *   3. Call it in the correct position in init()
 *   Zero HTML file changes required.
 */

import { prefs } from './preferences.js';
import { applyLayout } from './components/LayoutMode.js';
import { initGlossary, initInlineQuizzes } from './components/GlossaryQuiz.js';
import { mountLessonActions } from './components/LessonActions.js';
import { mountTypographyPanel } from './components/TypographyPanel.js';

function init() {
  // 1. Layout: restructure DOM into collapsible sections (reads prefs signal)
  applyLayout(prefs.value.sectionsCollapsed);

  // 2. Glossary: attach tooltips/tray to .term and [data-term] elements
  initGlossary();
  initInlineQuizzes();

  // 3. LessonActions: bottom navigation bar
  mountLessonActions();

  // 4. TypographyPanel: reading preferences panel
  mountTypographyPanel();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
