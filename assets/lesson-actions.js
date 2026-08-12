/**
 * Lesson action bar — auto-injected at the bottom of every lesson page.
 * 
 * Renders: Back to map | Take quiz / Generate quiz | Mark as complete
 * Detects quiz availability via /api/questions.
 * Detects completion status via /api/map/{domain}.
 * 
 * Usage: <script src="../assets/lesson-actions.js"></script>
 * 
 * Data attributes (on the script tag):
 *   data-lesson-id="0001-iceberg-metadata-tree"  (filename without .html)
 *   data-topic-title="Iceberg Metadata Tree"
 *   data-map-page="modern-data-analytics-stacks-map.html"
 *   data-domain="data-analytics"       (for status API calls)
 *   data-topic-slug="storage-and-table-formats"  (topic slug in MAP.md)
 */

(function() {
  'use strict';

  const script = document.currentScript;
  const lessonId = script?.dataset.lessonId || detectLessonId();
  const topicTitle = script?.dataset.topicTitle || detectTitle();
  const mapPage = script?.dataset.mapPage || detectMapPage();
  const domain = script?.dataset.domain || null;
  const topicSlug = script?.dataset.topicSlug || null;

  function detectLessonId() {
    return window.location.pathname.split('/').pop().replace('.html', '');
  }

  function detectTitle() {
    const h1 = document.querySelector('h1');
    return h1 ? h1.textContent.trim() : 'this topic';
  }

  function detectMapPage() {
    const backLink = document.querySelector('.lesson-nav a[href*="-map.html"]');
    if (backLink) return backLink.getAttribute('href');
    const mapLink = document.querySelector('a[href$="-map.html"]');
    if (mapLink) return mapLink.getAttribute('href');
    return 'index.html';
  }

  // --- Render ---
  function render() {
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
        .lesson-action-bar .actions { display: flex; flex-direction: column; gap: 0.6rem; }
        .lesson-action-bar .action-btn {
          display: inline-flex; align-items: center; gap: 0.5rem;
          padding: 0.6rem 1rem; border-radius: 6px; font-size: 0.9rem;
          width: fit-content; text-decoration: none; cursor: pointer;
          border: 1px solid var(--border); color: var(--text); background: none;
        }
        .lesson-action-bar .action-btn:hover { background: var(--bg-surface); }
        .lesson-action-bar .action-primary { border-color: var(--accent); color: var(--accent); }
        .lesson-action-bar .action-success { border-color: #16a34a; color: #16a34a; }
        .lesson-action-bar .action-success:hover { background: color-mix(in srgb, #16a34a 10%, transparent); }
        .lesson-action-bar .action-success:active { transform: scale(0.96); }
        .lesson-action-bar .action-done { border-color: #16a34a; color: #16a34a; opacity: 0.7; cursor: default; }
        .lesson-action-bar .action-muted { border-color: var(--border); color: var(--text-muted); font-size: 0.8rem; }
        .lesson-action-bar .action-muted:hover { color: var(--text); }
      </style>
      <h3>What's next</h3>
      <div class="actions" id="lesson-actions-list">
        <a href="${mapPage}" class="action-btn action-primary">← Back to map</a>
        <span id="lesson-quiz-action" class="action-btn" style="color:var(--text-muted)">Loading...</span>
        <span id="lesson-complete-action"></span>
      </div>
    `;

    const glossaryScript = document.getElementById('glossary-data');
    if (glossaryScript) {
      glossaryScript.parentNode.insertBefore(bar, glossaryScript);
    } else if (oldNext) {
      oldNext.parentNode.insertBefore(bar, oldNext.nextSibling);
    } else {
      document.body.appendChild(bar);
    }

    if (oldNext) oldNext.remove();

    detectQuiz();
    detectCompletionStatus();
  }

  function findNextStepsSection() {
    const sections = document.querySelectorAll('.next-steps');
    for (const s of sections) {
      const h3 = s.querySelector('h3');
      if (h3 && /what.s next/i.test(h3.textContent)) return s;
    }
    return null;
  }

  // --- Quiz detection ---
  async function detectQuiz() {
    const el = document.getElementById('lesson-quiz-action');
    if (!el) return;

    try {
      const res = await fetch('/api/questions');
      if (!res.ok) throw new Error('no server');
      const data = await res.json();
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

  // --- Completion status detection ---
  async function detectCompletionStatus() {
    const el = document.getElementById('lesson-complete-action');
    if (!el) return;

    // Need domain and slug to call the status API
    let resolvedDomain = domain;
    let resolvedSlug = topicSlug;

    // If not provided via data attributes, try to auto-detect from /api/map
    if (!resolvedDomain || !resolvedSlug) {
      resolvedDomain = resolvedDomain || await autoDetectDomain();
      resolvedSlug = resolvedSlug || await autoDetectSlug(resolvedDomain);
    }

    if (!resolvedDomain || !resolvedSlug) {
      el.remove(); // Can't determine topic, don't show the button
      return;
    }

    // Check current status
    try {
      const res = await fetch(`/api/map/${resolvedDomain}`);
      if (!res.ok) throw new Error('no map');
      const mapData = await res.json();
      const topic = mapData.topics.find(t => t.slug === resolvedSlug);

      if (topic && topic.status === 'complete') {
        el.outerHTML = `<span class="action-btn action-done">✓ Completed</span> <button class="action-btn action-muted" onclick="window._reopenTopic()">↩ Reopen</button>`;
      } else {
        el.outerHTML = `<button class="action-btn action-success" id="mark-complete-btn" onclick="window._markComplete()">☐ Mark as complete</button>`;
      }
    } catch (e) {
      el.remove(); // Server not running or no map — hide button
    }

    // Store for the click handler
    window._completeDomain = resolvedDomain;
    window._completeSlug = resolvedSlug;
  }

  async function autoDetectDomain() {
    // Infer domain from the map page filename: "modern-data-analytics-stacks-map.html" → "data-analytics"
    // Or query /api/maps and find which domain contains our lesson
    try {
      const res = await fetch('/api/maps');
      if (!res.ok) return null;
      const maps = await res.json();
      // Try each map's API to find one containing our lesson
      for (const mapFile of maps) {
        const domainGuess = mapFile.replace('-map.html', '').replace('modern-', '').replace('web-application-', 'web-');
        // Try common domain slug patterns
        const candidates = [
          mapFile.replace('-map.html', ''),
          domainGuess,
          mapFile.replace('-map.html', '').split('-').slice(0, 2).join('-'),
        ];
        for (const c of candidates) {
          try {
            const r = await fetch(`/api/map/${c}`);
            if (r.ok) {
              const data = await r.json();
              const match = data.topics.find(t =>
                t.lesson_file === lessonId + '.html' ||
                lessonId.includes(t.slug) ||
                t.slug.split('-').every(p => lessonId.includes(p))
              );
              if (match) return c;
            }
          } catch(e) {}
        }
      }
    } catch(e) {}
    return null;
  }

  async function autoDetectSlug(dom) {
    if (!dom) return null;
    try {
      const res = await fetch(`/api/map/${dom}`);
      if (!res.ok) return null;
      const data = await res.json();
      const match = data.topics.find(t =>
        t.lesson_file === lessonId + '.html' ||
        lessonId.includes(t.slug) ||
        t.slug.split('-').every(p => lessonId.includes(p))
      );
      return match ? match.slug : null;
    } catch(e) { return null; }
  }

  // --- Global actions ---
  window._markComplete = async function() {
    const btn = document.getElementById('mark-complete-btn');
    if (!btn) return;
    btn.textContent = '✓ Done!';
    btn.style.background = '#16a34a';
    btn.style.color = '#fff';
    btn.style.borderColor = '#16a34a';
    btn.style.transform = 'scale(1.05)';
    btn.disabled = true;

    try {
      const res = await fetch(`/api/map/${window._completeDomain}/${window._completeSlug}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'complete' }),
      });
      if (res.ok) {
        setTimeout(() => { window.location.href = mapPage; }, 800);
      } else {
        btn.textContent = '☐ Mark as complete';
        btn.style.cssText = '';
        btn.disabled = false;
        alert('Failed to update status');
      }
    } catch(e) {
      btn.textContent = '☐ Mark as complete';
      btn.style.cssText = '';
      btn.disabled = false;
      alert('Server not running — use: mise run serve');
    }
  };

  window._reopenTopic = async function() {
    try {
      const res = await fetch(`/api/map/${window._completeDomain}/${window._completeSlug}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'in-progress' }),
      });
      if (res.ok) location.reload();
    } catch(e) {
      alert('Server not running — use: mise run serve');
    }
  };

  window._startQuiz = function() {
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
          if (result.exit_code === 0) { alert('Quiz generated!'); location.reload(); }
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
