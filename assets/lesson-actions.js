/**
 * Lesson action bar — auto-injected at the bottom of every lesson page.
 * 
 * Renders: Back to map | Take quiz / Generate quiz | Reference doc
 * Detects quiz availability via /api/questions.
 * 
 * Usage: <script src="../assets/lesson-actions.js"></script>
 * 
 * Expects: data attributes on the script tag or auto-detects from page:
 *   data-lesson-id="0001-iceberg-metadata-tree"  (filename without .html)
 *   data-topic-title="Iceberg Metadata Tree"
 *   data-map-page="modern-data-analytics-stacks-map.html"
 */

(function() {
  'use strict';

  // --- Config from script tag or auto-detect ---
  const script = document.currentScript;
  const lessonId = script?.dataset.lessonId || detectLessonId();
  const topicTitle = script?.dataset.topicTitle || detectTitle();
  const mapPage = script?.dataset.mapPage || detectMapPage();

  function detectLessonId() {
    const path = window.location.pathname.split('/').pop();
    return path.replace('.html', '');
  }

  function detectTitle() {
    const h1 = document.querySelector('h1');
    return h1 ? h1.textContent.trim() : 'this topic';
  }

  function detectMapPage() {
    // Look for a back-link in the nav, or guess from lesson naming
    const backLink = document.querySelector('.lesson-nav a[href*="-map.html"]');
    if (backLink) return backLink.getAttribute('href');
    // Check for any map page link on the page
    const mapLink = document.querySelector('a[href$="-map.html"]');
    if (mapLink) return mapLink.getAttribute('href');
    return 'index.html';
  }

  // --- Render the action bar ---
  function render() {
    // Remove any existing "What's Next" prose section
    const oldNext = findNextStepsSection();

    const bar = document.createElement('div');
    bar.className = 'lesson-action-bar';
    bar.innerHTML = `
      <style>
        .lesson-action-bar {
          margin-top: 2rem; padding: 1.25rem; border-radius: 8px;
          background: var(--bg-elevated); border: 1px solid var(--border);
        }
        .lesson-action-bar h3 { margin: 0 0 0.75rem; font-size: 1rem; }
        .lesson-action-bar .actions {
          display: flex; flex-direction: column; gap: 0.6rem;
        }
        .lesson-action-bar .action-btn {
          display: inline-flex; align-items: center; gap: 0.5rem;
          padding: 0.6rem 1rem; border-radius: 6px; font-size: 0.9rem;
          width: fit-content; text-decoration: none; cursor: pointer;
          border: 1px solid var(--border); color: var(--text);
          background: none;
        }
        .lesson-action-bar .action-btn:hover { background: var(--bg-surface); }
        .lesson-action-bar .action-primary {
          border-color: var(--accent); color: var(--accent);
        }
      </style>
      <h3>What's next</h3>
      <div class="actions">
        <a href="${mapPage}" class="action-btn action-primary">← Back to map</a>
        <span id="lesson-quiz-action" class="action-btn" style="color:var(--text-muted)">Loading quiz status...</span>
      </div>
    `;

    // Insert before the glossary script or at end of body
    const glossaryScript = document.getElementById('glossary-data');
    if (glossaryScript) {
      glossaryScript.parentNode.insertBefore(bar, glossaryScript);
    } else if (oldNext) {
      oldNext.parentNode.insertBefore(bar, oldNext.nextSibling);
    } else {
      document.body.appendChild(bar);
    }

    // Remove old prose "What's Next" section if it exists
    if (oldNext) oldNext.remove();

    // Detect quiz status
    detectQuiz();
  }

  function findNextStepsSection() {
    // Find the "What's Next" div.next-steps
    const sections = document.querySelectorAll('.next-steps');
    for (const s of sections) {
      const h3 = s.querySelector('h3');
      if (h3 && /what.s next/i.test(h3.textContent)) return s;
    }
    return null;
  }

  async function detectQuiz() {
    const el = document.getElementById('lesson-quiz-action');
    if (!el) return;

    try {
      const res = await fetch('/api/questions');
      if (!res.ok) throw new Error('no server');
      const data = await res.json();

      // Find matching questions by lesson ID
      const count = data[lessonId] || 0;

      if (count > 0) {
        el.outerHTML = `<a href="javascript:void(0)" onclick="window._startQuiz()" class="action-btn action-primary">✓ Take the quiz (${count} questions)</a>`;
      } else {
        el.outerHTML = `<a href="javascript:void(0)" onclick="window._generateQuiz()" class="action-btn">+ Generate quiz</a>`;
      }
    } catch (e) {
      el.outerHTML = `<span class="action-btn" style="color:var(--text-muted)">Quiz requires server (mise run serve)</span>`;
    }
  }

  // --- Quiz actions (global so onclick can reach them) ---
  window._startQuiz = function() {
    // For now: run the quick-check generator which produces an HTML quiz page
    if (confirm(`Start a quick-check review for "${topicTitle}"?`)) {
      fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: `run quick-check review for ${topicTitle}`, mock: false }),
      }).then(r => r.json()).then(d => {
        const es = new EventSource(d.stream_url);
        es.addEventListener('done', (e) => {
          es.close();
          const result = JSON.parse(e.data);
          if (result.exit_code === 0) {
            alert('Quiz generated! Check the output.');
            location.reload();
          }
        });
      }).catch(() => alert('Server not running — use: mise run serve'));
    }
  };

  window._generateQuiz = function() {
    if (!confirm(`Generate quiz questions for "${topicTitle}"?`)) return;
    fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: `generate quick-check questions for ${topicTitle}`, mock: false }),
    }).then(r => r.json()).then(d => {
      const es = new EventSource(d.stream_url);
      es.addEventListener('done', () => { es.close(); location.reload(); });
    }).catch(() => alert('Server not running — use: mise run serve'));
  };

  // --- Init ---
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', render);
  } else {
    render();
  }
})();
