/* Glossary component: hover tooltip (quick peek) + click tray (deep look) */
(function () {
  'use strict';
  var tip = null;
  var tray = null;
  var overlay = null;

  function glossary() {
    var el = document.getElementById('glossary-data');
    if (!el) return {};
    try { return JSON.parse(el.textContent); } catch (e) { return {}; }
  }

  function defFor(term) {
    return term.getAttribute('data-def') ||
      (term.getAttribute('data-term') && glossary()[term.getAttribute('data-term')]) || null;
  }

  // --- Hover tooltip (quick peek) ---
  function dismissTip() { if (tip) { tip.remove(); tip = null; } }

  function showTip(term) {
    dismissTip();
    var def = defFor(term);
    if (!def) return;
    tip = document.createElement('span');
    tip.className = 'glossary-tooltip';
    tip.setAttribute('role', 'tooltip');
    tip.textContent = def.length > 120 ? def.substring(0, 117) + '…' : def;
    term.appendChild(tip);
    var r = tip.getBoundingClientRect();
    if (r.left < 4) { tip.style.left = '0'; tip.style.transform = 'none'; }
    else if (r.right > window.innerWidth - 4) {
      tip.style.left = 'auto'; tip.style.right = '0'; tip.style.transform = 'none';
    }
  }

  // --- Slide-out tray ---
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
    var data = glossary();
    var def = data[key];
    if (!def) return;
    openTray();
    var body = tray.querySelector('.glossary-tray-body');
    var title = tray.querySelector('.glossary-tray-title');
    var back = tray.querySelector('.glossary-tray-back');
    title.textContent = key.replace(/-/g, ' ');
    back.style.display = '';
    body.innerHTML =
      '<div class="glossary-tray-term-name">' + key.replace(/-/g, ' ') + '</div>' +
      '<div class="glossary-tray-term-def">' + escHtml(def) + '</div>';
  }

  function showList() {
    var data = glossary();
    var keys = Object.keys(data).sort();
    if (!keys.length) return;
    openTray();
    var body = tray.querySelector('.glossary-tray-body');
    var title = tray.querySelector('.glossary-tray-title');
    var back = tray.querySelector('.glossary-tray-back');
    title.textContent = 'Glossary';
    back.style.display = 'none';
    var html = '<ul class="glossary-tray-list">';
    keys.forEach(function (k) {
      html += '<li data-key="' + escAttr(k) + '">' + escHtml(k.replace(/-/g, ' ')) + '</li>';
    });
    html += '</ul>';
    body.innerHTML = html;
    body.querySelectorAll('li').forEach(function (li) {
      li.addEventListener('click', function () { showTerm(li.getAttribute('data-key')); });
    });
  }

  function escHtml(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
  function escAttr(s) { return s.replace(/"/g, '&quot;'); }

  // --- Init ---
  function init() {
    document.querySelectorAll('.term').forEach(function (term) {
      term.setAttribute('tabindex', '0');
      term.addEventListener('mouseenter', function () { showTip(term); });
      term.addEventListener('mouseleave', dismissTip);
      term.addEventListener('click', function (e) {
        e.preventDefault();
        dismissTip();
        var key = term.getAttribute('data-term');
        if (key) showTerm(key);
        else if (term.getAttribute('data-def')) {
          // Inline def — show in tray too
          openTray();
          var body = tray.querySelector('.glossary-tray-body');
          var title = tray.querySelector('.glossary-tray-title');
          var back = tray.querySelector('.glossary-tray-back');
          title.textContent = term.textContent;
          back.style.display = '';
          back.onclick = showList;
          body.innerHTML =
            '<div class="glossary-tray-term-name">' + escHtml(term.textContent) + '</div>' +
            '<div class="glossary-tray-term-def">' + escHtml(term.getAttribute('data-def')) + '</div>';
        }
      });
      term.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          term.click();
        }
      });
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeTray();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
