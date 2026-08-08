/* Glossary tooltip — inline definitions for lesson terms */
(function () {
  'use strict';
  let tip = null;

  function glossary() {
    const el = document.getElementById('glossary-data');
    if (!el) return {};
    try { return JSON.parse(el.textContent); } catch { return {}; }
  }

  function defFor(term) {
    return term.getAttribute('data-def') ||
      (term.getAttribute('data-term') && glossary()[term.getAttribute('data-term')]) || null;
  }

  function dismiss() { if (tip) { tip.remove(); tip = null; } }

  function show(term) {
    dismiss();
    const def = defFor(term);
    if (!def) return;
    tip = document.createElement('span');
    tip.className = 'glossary-tooltip';
    tip.setAttribute('role', 'tooltip');
    tip.textContent = def;
    const ref = term.getAttribute('data-ref');
    if (ref) {
      const a = document.createElement('a');
      a.href = ref;
      a.textContent = '\u{1F4D6} See glossary';
      tip.appendChild(a);
    }
    term.appendChild(tip);
    // Keep within viewport horizontally
    const r = tip.getBoundingClientRect();
    if (r.left < 4) { tip.style.left = '0'; tip.style.transform = 'none'; }
    else if (r.right > window.innerWidth - 4) {
      tip.style.left = 'auto'; tip.style.right = '0'; tip.style.transform = 'none';
    }
  }

  function init() {
    document.querySelectorAll('.term').forEach(function (term) {
      term.setAttribute('tabindex', '0');
      term.addEventListener('mouseenter', function () { show(term); });
      term.addEventListener('mouseleave', dismiss);
      term.addEventListener('click', function (e) {
        e.preventDefault();
        activeOn(term) ? dismiss() : show(term);
      });
      term.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); show(term); }
        if (e.key === 'Escape') dismiss();
      });
    });
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.term')) dismiss();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') dismiss();
    });
  }

  function activeOn(term) { return tip && tip.parentNode === term; }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
