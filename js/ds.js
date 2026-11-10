/* Booth Homelab Design System: small runtime helpers (no dependencies).
   - Theme: <html data-theme> follows the device by default; dsTheme.toggle() flips and remembers it.
   - Toasts: dsToast('Saved', 'ok') -> ok | info | warn | bad
   Put <script src="/ds/js/ds.js"></script> in <head> so the theme applies before first paint. */
(function () {
  var KEY = 'ds-theme';
  var root = document.documentElement;
  var ICONS = window.DS_ICONS || '/ds/glyphs/icons.svg';

  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function store(v) { try { v ? localStorage.setItem(KEY, v) : localStorage.removeItem(KEY); } catch (e) {} }
  function current() {
    return root.getAttribute('data-theme') ||
      (window.matchMedia && matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
  }

  var saved = stored();
  if (saved === 'light' || saved === 'dark') root.setAttribute('data-theme', saved);

  window.dsTheme = {
    get: current,
    set: function (t) { root.setAttribute('data-theme', t); store(t); },
    toggle: function () { this.set(current() === 'dark' ? 'light' : 'dark'); return current(); },
    reset: function () { root.removeAttribute('data-theme'); store(null); }
  };

  var GLYPH = { ok: 'check-circle', info: 'info', warn: 'alert', bad: 'x-circle' };
  window.dsIcon = function (name, cls) {
    return '<svg class="icon ' + (cls || '') + '" aria-hidden="true"><use href="' + ICONS + '#' + name + '"/></svg>';
  };
  window.dsToast = function (msg, kind, ms) {
    kind = kind || 'info';
    var box = document.querySelector('.toasts');
    if (!box) { box = document.createElement('div'); box.className = 'toasts'; box.setAttribute('aria-live', 'polite'); document.body.appendChild(box); }
    var t = document.createElement('div');
    t.className = 'toast ' + kind;
    t.innerHTML = dsIcon(GLYPH[kind] || 'info') + '<div></div>';
    t.lastChild.textContent = msg;
    box.appendChild(t);
    setTimeout(function () { t.style.transition = 'opacity 150ms'; t.style.opacity = '0'; setTimeout(function () { t.remove(); }, 160); }, ms || 3500);
  };
})();
