import { h, render } from 'preact';
import { useState } from 'preact/hooks';
import htm from 'htm';

const html = htm.bind(h);

function LessonActions({ lessonId, domain, mapPage, topicTitle }) {
  const [status, setStatus] = useState('idle');

  const resolvedMapPage = mapPage || (domain ? `${domain}-map.html` : null);

  function handleMarkComplete() {
    setStatus('completing');
    // POST to mark-complete API if available, otherwise just visual feedback
    fetch(`/api/map/${domain}/complete/${lessonId}`, { method: 'POST' })
      .then(() => setStatus('complete'))
      .catch(() => setStatus('complete')); // optimistic
  }

  return html`
    <div class="lesson-actions-bar">
      ${resolvedMapPage && html`
        <a href=${resolvedMapPage} class="btn">← Back to map</a>
      `}
      <button class="btn" onClick=${() => {
        const quizUrl = 'quiz/' + lessonId + '-quiz.html';
        window.location.href = quizUrl;
      }}>+ Generate quiz</button>
      ${status === 'idle' && html`
        <button class="btn primary" onClick=${handleMarkComplete}>✓ Mark complete</button>
      `}
      ${status === 'complete' && html`
        <span class="btn done">✓ Complete</span>
      `}
    </div>
  `;
}

// Auto-mount: find the script tag or mount point and render
function mount() {
  // Look for a mount div first
  let target = document.getElementById('lesson-actions');

  // If no mount div, create one at the end of body
  if (!target) {
    target = document.createElement('div');
    target.id = 'lesson-actions';
    document.body.appendChild(target);
  }

  // Get data from the script tag that loaded us, or from the mount div's data attrs
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

// Mount when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', mount);
} else {
  mount();
}

export { LessonActions };
