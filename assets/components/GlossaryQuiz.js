import { h, render } from 'preact';
import { signal } from '@preact/signals';
import htm from 'htm';

const html = htm.bind(h);

/**
 * GlossaryTerm — tooltip on hover/focus for domain terms.
 * 
 * Auto-mounts: finds all elements with data-term attribute and attaches tooltips.
 * Reads definitions from #glossary-data JSON block in the page.
 */

export function initGlossary() {
  const dataEl = document.getElementById('glossary-data');
  if (!dataEl) return;

  let glossary;
  try {
    glossary = JSON.parse(dataEl.textContent);
  } catch (e) {
    return;
  }

  // Add accessibility attributes to term elements.
  // Tooltip hover/click behavior is handled by glossary.js (non-module script).
  document.querySelectorAll('[data-term]').forEach(el => {
    const term = el.getAttribute('data-term');
    const def = glossary[term];
    if (!def) return;

    el.classList.add('glossary-term');
    if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '0');
    el.setAttribute('aria-label', `${term.replace(/-/g, ' ')}: ${def}`);
  });
}

/**
 * InlineQuiz — simple multiple-choice or explain question embedded in a lesson.
 * 
 * Mount into a container with quiz data:
 *   <div class="inline-quiz" data-prompt="..." data-answer="..."></div>
 */

export function initInlineQuizzes() {
  document.querySelectorAll('.inline-quiz').forEach(el => {
    const prompt = el.getAttribute('data-prompt');
    const answer = el.getAttribute('data-answer');
    if (!prompt) return;

    const revealed = signal(false);

    function Quiz() {
      return html`
        <div class="inline-quiz-card">
          <p class="inline-quiz-prompt">${prompt}</p>
          ${!revealed.value && html`
            <button class="btn" onClick=${() => { revealed.value = true; }}>Check Answer</button>
          `}
          ${revealed.value && html`
            <div class="inline-quiz-answer">
              <p>${answer}</p>
            </div>
          `}
        </div>
      `;
    }

    render(html`<${Quiz} />`, el);
  });
}

// Auto-init when loaded as module
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => { initGlossary(); initInlineQuizzes(); });
} else {
  initGlossary();
  initInlineQuizzes();
}
