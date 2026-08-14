import { h, render } from 'preact';
import { signal } from '@preact/signals';
import htm from 'htm';

const html = htm.bind(h);

/**
 * GlossaryQuiz — tooltip on hover/focus + click tray for domain terms,
 * plus inline quiz cards.
 *
 * Exports:
 *   initGlossary()      — attach tooltips, tray, and accessibility attrs to term elements
 *   initInlineQuizzes() — mount inline quiz cards into .inline-quiz containers
 *
 * Called by page-shell.js AFTER layout restructuring (so DOM is stable).
 */

// --- Glossary data helper ---

function getGlossaryData() {
  const el = document.getElementById('glossary-data');
  if (!el) return {};
  try { return JSON.parse(el.textContent); } catch { return {}; }
}

// --- Hover tooltip (quick peek) ---

let tip = null;

function dismissTip() {
  if (tip) { tip.remove(); tip = null; }
}

function showTip(term) {
  dismissTip();
  const glossary = getGlossaryData();
  const key = term.getAttribute('data-term');
  const def = term.getAttribute('data-def') || (key && glossary[key]) || null;
  if (!def) return;

  tip = document.createElement('span');
  tip.className = 'glossary-tooltip';
  tip.setAttribute('role', 'tooltip');
  tip.textContent = def.length > 120 ? def.substring(0, 117) + '…' : def;
  term.appendChild(tip);

  const r = tip.getBoundingClientRect();
  if (r.left < 4) { tip.style.left = '0'; tip.style.transform = 'none'; }
  else if (r.right > window.innerWidth - 4) {
    tip.style.left = 'auto'; tip.style.right = '0'; tip.style.transform = 'none';
  }
}

// --- Slide-out tray ---

let tray = null;
let overlay = null;

function escHtml(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function escAttr(s) { return s.replace(/"/g, '&quot;'); }

function buildTray() {
  if (tray) return;
  overlay = document.createElement('div');
  overlay.className = 'glossary-overlay';
  document.body.appendChild(overlay);

  tray = document.createElement('aside');
  tray.className = 'glossary-tray';
  tray.setAttribute('role', 'complementary');
  tray.setAttribute('aria-label', 'Glossary');
  tray.innerHTML =
    '<div class="glossary-tray-header">' +
      '<button class="glossary-tray-back" aria-label="All terms" style="display:none">← All terms</button>' +
      '<h3 class="glossary-tray-title">Glossary</h3>' +
      '<button class="glossary-tray-close" aria-label="Close glossary">×</button>' +
    '</div>' +
    '<div class="glossary-tray-body"></div>';
  document.body.appendChild(tray);

  tray.querySelector('.glossary-tray-close').addEventListener('click', closeTray);
  tray.querySelector('.glossary-tray-back').addEventListener('click', showList);
  overlay.addEventListener('click', closeTray);
}

function openTray() {
  buildTray();
  tray.classList.add('open');
  overlay.classList.add('active');
}

function closeTray() {
  if (!tray) return;
  tray.classList.remove('open');
  overlay.classList.remove('active');
}

function showTerm(key) {
  const glossary = getGlossaryData();
  const def = glossary[key];
  if (!def) return;
  openTray();
  const body = tray.querySelector('.glossary-tray-body');
  const title = tray.querySelector('.glossary-tray-title');
  const back = tray.querySelector('.glossary-tray-back');
  title.textContent = key.replace(/-/g, ' ');
  back.style.display = '';
  body.innerHTML =
    '<div class="glossary-tray-term-name">' + escHtml(key.replace(/-/g, ' ')) + '</div>' +
    '<div class="glossary-tray-term-def">' + escHtml(def) + '</div>';
}

function showList() {
  const glossary = getGlossaryData();
  const keys = Object.keys(glossary).sort();
  if (!keys.length) return;
  openTray();
  const body = tray.querySelector('.glossary-tray-body');
  const title = tray.querySelector('.glossary-tray-title');
  const back = tray.querySelector('.glossary-tray-back');
  title.textContent = 'Glossary';
  back.style.display = 'none';
  let listHtml = '<ul class="glossary-tray-list">';
  keys.forEach(k => {
    listHtml += '<li data-key="' + escAttr(k) + '">' + escHtml(k.replace(/-/g, ' ')) + '</li>';
  });
  listHtml += '</ul>';
  body.innerHTML = listHtml;
  body.querySelectorAll('li').forEach(li => {
    li.addEventListener('click', () => showTerm(li.getAttribute('data-key')));
  });
}

// --- Public: initGlossary ---

export function initGlossary() {
  const glossary = getGlossaryData();
  if (!Object.keys(glossary).length && !document.querySelector('.term, [data-term]')) return;

  // Attach accessibility attributes from glossary-data JSON
  document.querySelectorAll('[data-term]').forEach(el => {
    const term = el.getAttribute('data-term');
    const def = glossary[term];
    if (!def) return;
    el.classList.add('glossary-term');
    if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '0');
    el.setAttribute('aria-label', `${term.replace(/-/g, ' ')}: ${def}`);
  });

  // Attach hover/click/keyboard listeners to all term elements
  document.querySelectorAll('.term, [data-term]').forEach(term => {
    if (!term.hasAttribute('tabindex')) term.setAttribute('tabindex', '0');

    term.addEventListener('mouseenter', () => showTip(term));
    term.addEventListener('mouseleave', dismissTip);
    term.addEventListener('click', (e) => {
      e.preventDefault();
      dismissTip();
      const key = term.getAttribute('data-term');
      if (key) {
        showTerm(key);
      } else if (term.getAttribute('data-def')) {
        openTray();
        const body = tray.querySelector('.glossary-tray-body');
        const title = tray.querySelector('.glossary-tray-title');
        const back = tray.querySelector('.glossary-tray-back');
        title.textContent = term.textContent;
        back.style.display = '';
        back.onclick = showList;
        body.innerHTML =
          '<div class="glossary-tray-term-name">' + escHtml(term.textContent) + '</div>' +
          '<div class="glossary-tray-term-def">' + escHtml(term.getAttribute('data-def')) + '</div>';
      }
    });
    term.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        term.click();
      }
    });
  });

  // Global Escape to close tray
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeTray();
  });
}

// --- Public: initInlineQuizzes ---

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
