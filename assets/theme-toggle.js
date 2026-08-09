/* Theme toggle — dark (default) / light */
(function () {
  'use strict';
  var saved = localStorage.getItem('teach-me-theme');
  if (saved) document.documentElement.setAttribute('data-theme', saved);

  var btn = document.createElement('button');
  btn.className = 'theme-toggle';
  btn.setAttribute('aria-label', 'Toggle light/dark mode');
  btn.textContent = saved === 'light' ? '☀️' : '🌙';
  document.body.appendChild(btn);

  btn.addEventListener('click', function () {
    var current = document.documentElement.getAttribute('data-theme');
    var next = current === 'light' ? null : 'light';
    if (next) {
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('teach-me-theme', next);
      btn.textContent = '☀️';
    } else {
      document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('teach-me-theme', 'dark');
      btn.textContent = '🌙';
    }
  });
})();
