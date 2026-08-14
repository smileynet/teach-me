// preferences-prefs.js — BLOCKING script for <head>. Prevents FOUC.
// Reads unified prefs from localStorage, applies CSS vars + theme before paint.
// Also handles legacy key migration (teach-me-typography, teach-me-theme).
// Keep tiny (< 500 bytes minified). No imports, no modules.
(function() {
  try {
    var KEY = 'teach-me-prefs-v1';
    var p = JSON.parse(localStorage.getItem(KEY));

    // Legacy migration (runs once)
    if (!p) {
      var lt = localStorage.getItem('teach-me-typography');
      var lth = localStorage.getItem('teach-me-theme');
      if (lt || lth) {
        var old = lt ? JSON.parse(lt) : {};
        p = { _v: 1, theme: lth || 'auto', fontSize: old.fontSize || '16px',
              fontFamily: old.fontFamily ? (old.fontFamily.indexOf('OpenDyslexic') > -1 ? 'dyslexic' : old.fontFamily.indexOf('system-ui') > -1 ? 'sans' : 'serif') : 'serif',
              lineHeight: old.lineHeight || '1.7', maxWidth: old.maxWidth || '740px',
              sectionsCollapsed: old.layout === 'sections' };
        localStorage.setItem(KEY, JSON.stringify(p));
        localStorage.removeItem('teach-me-typography');
        localStorage.removeItem('teach-me-theme');
      }
    }
    if (!p) return;

    var s = document.documentElement.style;
    var families = { serif: "'Palatino Linotype', Palatino, 'Book Antiqua', Georgia, serif",
                     sans: "system-ui, -apple-system, 'Segoe UI', sans-serif",
                     dyslexic: "'OpenDyslexic', sans-serif" };

    if (p.fontSize) s.setProperty('--font-size-base', p.fontSize);
    if (p.fontFamily && families[p.fontFamily]) s.setProperty('--font-family-body', families[p.fontFamily]);
    if (p.lineHeight) s.setProperty('--line-height-body', p.lineHeight);
    if (p.maxWidth) s.setProperty('--max-width-content', p.maxWidth);

    // Resolve theme
    var theme = p.theme;
    if (theme === 'auto') theme = window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    if (theme) document.documentElement.setAttribute('data-theme', theme);
  } catch(e) {}
})();
