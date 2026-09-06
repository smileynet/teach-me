import { h, render } from 'preact';
import { useState, useEffect } from 'preact/hooks';
import htm from 'htm';
import { GeneratePrompt } from './GeneratePrompt.js';

const html = htm.bind(h);

/**
 * LessonActions — bottom navigation bar with map link, quiz button, and mark-complete.
 *
 * Exports:
 *   mountLessonActions() — creates mount point and renders the component.
 *
 * Called by page-shell.js. Reads props from:
 *   1. A script tag with data-domain/data-lesson-id attributes
 *   2. A #lesson-actions div with data attributes
 *   3. Falls back to URL-derived lessonId and page h1
 */

function LessonActions({ lessonId, domain, mapPage, topicTitle }) {
  const [status, setStatus] = useState('loading');
  const [quizExists, setQuizExists] = useState(null);
  const [error, setError] = useState(null);

  const resolvedMapPage = mapPage || (domain ? `${domain}-map.html` : null);
  const quizUrl = 'quiz/' + lessonId + '-quiz.html';

  useEffect(() => {
    fetch(quizUrl, { method: 'HEAD' })
      .then(res => setQuizExists(res.ok))
      .catch(() => setQuizExists(false));
  }, [quizUrl]);

  // Check current completion status on mount
  useEffect(() => {
    if (!domain) { setStatus('idle'); return; }
    // Try full lessonId, then without number prefix (MAP.md uses slug without NNNN-)
    const slug = lessonId.replace(/^\d+-/, '');
    fetch(`/api/map/${domain}/${slug}/status`)
      .then(res => res.ok ? res.json() : null)
      .then(data => setStatus(data?.status === 'complete' ? 'complete' : 'idle'))
      .catch(() => setStatus('idle'));
  }, [domain, lessonId]);

  function handleToggleComplete() {
    const slug = lessonId.replace(/^\d+-/, '');
    const newStatus = status === 'complete' ? 'in-progress' : 'complete';
    const priorStatus = status;
    setError(null);
    setStatus('saving');
    fetch(`/api/map/${domain}/${slug}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    })
      .then(res => {
        if (!res.ok) throw new Error(`status ${res.status}`);
        setStatus(newStatus === 'complete' ? 'complete' : 'idle');
      })
      .catch(() => {
        // Never show a state the server didn't persist — revert + surface the error.
        setStatus(priorStatus);
        setError('Could not save — try again');
      });
  }

  const quizPrompt = `Generate the quiz page for the "${topicTitle}" lesson (lesson id ${lessonId}${domain ? ', domain ' + domain : ''}) in this teaching workspace. Run the generate-quiz-page tool / generate-topic quiz step so it lands at ${quizUrl}.`;

  return html`
    <div class="lesson-actions-bar">
      ${resolvedMapPage && html`
        <a href=${resolvedMapPage} class="btn">← Back to map</a>
      `}
      ${quizExists === null && html`<span class="btn">…</span>`}
      ${quizExists === true && html`
        <a href=${quizUrl} class="btn" aria-label=${'Take quiz: ' + topicTitle}>📝 Take quiz</a>
      `}
      ${quizExists === false && html`
        <${GeneratePrompt} buttonLabel="+ Generate quiz" groupLabel=${'How to generate the quiz for ' + topicTitle} prompt=${quizPrompt} />
      `}
      ${status === 'loading' && html`
        <span class="btn">…</span>
      `}
      ${status === 'idle' && html`
        <button class="btn primary" onClick=${handleToggleComplete}
                title=${error || 'Mark this lesson complete'}>✓ Mark complete</button>
      `}
      ${status === 'complete' && html`
        <button class="btn done" onClick=${handleToggleComplete}
                title=${error || 'Lesson complete — click to unmark'}>✓ Complete</button>
      `}
      ${status === 'saving' && html`
        <span class="btn">…</span>
      `}
      ${error && html`
        <span class="lesson-actions-error" role="status" aria-live="polite">${error}</span>
      `}
    </div>
  `;
}

export function mountLessonActions() {
  let target = document.getElementById('lesson-actions');
  if (!target) {
    target = document.createElement('div');
    target.id = 'lesson-actions';
    document.body.appendChild(target);
  }

  const script = document.querySelector('script[data-domain]');
  const source = script || target;

  const props = {
    lessonId: source.dataset.lessonId || window.location.pathname.split('/').pop().replace('.html', ''),
    domain: source.dataset.domain || null,
    mapPage: source.dataset.mapPage || null,
    topicTitle: source.dataset.topicTitle || document.querySelector('h1')?.textContent || '',
  };

  render(html`<${LessonActions} ...${props} />`, target);
}

export { LessonActions };
