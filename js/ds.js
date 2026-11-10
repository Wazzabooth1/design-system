/* Booth Homelab Design System: runtime helpers (no dependencies).
   Put <script src="/static/ds/js/ds.js"></script> in <head> so theme and mode apply before first paint.

   Config (optional, set before this script):
     window.DS_BASE  = '/static/ds'   where ds-sync put the system (default: worked out from this script's URL)
     window.DS_APPS  = [...]           app list override (default: fetched from DS_BASE/apps.json)

   Theme:    dsTheme.get() / .set('light'|'dark') / .toggle() / .reset()   (follows the device by default)
   Mode:     dsMode.get() / .set('tv'|'wall'|null)   also ?mode=tv or ?mode=wall in the URL (remembered)
   Toasts:   dsToast('Saved', 'ok' | 'info' | 'warn' | 'bad')
   Icons:    dsIcon('search', 'lg')  -> <svg> string
   Switcher: <div data-ds-switcher></div> in the top bar; mark this app with <html data-app="bookhound">. */
(function () {
  var root = document.documentElement;
  var me = document.currentScript && document.currentScript.src;
  var BASE = (window.DS_BASE || (me ? me.replace(/\/js\/ds\.js(\?.*)?$/, '') : '/static/ds')).replace(/\/$/, '');
  var ICONS = window.DS_ICONS !== undefined ? window.DS_ICONS : BASE + '/glyphs/icons.svg';

  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function put(k, v) { try { v ? localStorage.setItem(k, v) : localStorage.removeItem(k); } catch (e) {} }

  /* ---------- Theme ---------- */
  var savedTheme = get('ds-theme');
  if (savedTheme === 'light' || savedTheme === 'dark') root.setAttribute('data-theme', savedTheme);
  function currentTheme() {
    return root.getAttribute('data-theme') ||
      (window.matchMedia && matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
  }
  window.dsTheme = {
    get: currentTheme,
    set: function (t) { root.setAttribute('data-theme', t); put('ds-theme', t); },
    toggle: function () { this.set(currentTheme() === 'dark' ? 'light' : 'dark'); return currentTheme(); },
    reset: function () { root.removeAttribute('data-theme'); put('ds-theme', null); }
  };

  /* ---------- Mode: tv / wall (big type, big touch targets, no hover reliance) ---------- */
  var urlMode = null;
  try { urlMode = new URLSearchParams(location.search).get('mode'); } catch (e) {}
  if (urlMode === 'tv' || urlMode === 'wall') put('ds-mode', urlMode);
  if (urlMode === 'normal') put('ds-mode', null);
  var savedMode = get('ds-mode');
  if (!root.hasAttribute('data-mode') && (savedMode === 'tv' || savedMode === 'wall')) root.setAttribute('data-mode', savedMode);
  window.dsMode = {
    get: function () { return root.getAttribute('data-mode'); },
    set: function (m) { m ? root.setAttribute('data-mode', m) : root.removeAttribute('data-mode'); put('ds-mode', m); }
  };

  /* ---------- Icons ---------- */
  window.dsIcon = function (name, cls) {
    return '<svg class="icon ' + (cls || '') + '" aria-hidden="true"><use href="' + ICONS + '#' + name + '"/></svg>';
  };

  /* ---------- Toasts ---------- */
  var GLYPH = { ok: 'check-circle', info: 'info', warn: 'alert', bad: 'x-circle' };
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

  /* ---------- App switcher ---------- */
  function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : s; return d.innerHTML; }

  function renderSwitcher(host, data) {
    var here = root.getAttribute('data-app');
    var cats = data.categories || [];
    var apps = data.apps || [];
    var id = 'ds-switcher-' + Math.random().toString(36).slice(2, 7);
    var groups = cats.map(function (c) {
      var list = apps.filter(function (a) { return a.category === c.id; });
      if (!list.length) return '';
      return '<div class="switcher-group"><div class="switcher-cat" style="--c:var(--cat-' + c.id + ')">' + esc(c.name) + '</div>' +
        '<div class="switcher-apps">' + list.map(function (a) {
          return '<a class="switcher-app" href="' + esc(a.url) + '"' + (a.id === here ? ' aria-current="page"' : '') +
            ' style="--c:var(--cat-' + a.category + ')"><span class="switcher-glyph">' + dsIcon(a.icon || 'grid') + '</span>' +
            '<span>' + esc(a.name) + '</span></a>';
        }).join('') + '</div></div>';
    }).join('');
    host.classList.add('switcher');
    host.innerHTML =
      '<button class="btn btn-ghost btn-icon" type="button" aria-label="All apps" aria-expanded="false" aria-controls="' + id + '">' + dsIcon('grid') + '</button>' +
      '<div class="switcher-panel" id="' + id + '" hidden><div class="switcher-head"><strong>Apps</strong>' +
      '<button class="btn btn-ghost btn-sm btn-icon" type="button" aria-label="Close">' + dsIcon('x', 'sm') + '</button></div>' +
      '<div class="switcher-body">' + groups + '</div></div>';
    var btn = host.firstChild, panel = host.lastChild;
    function open(v) { panel.hidden = !v; btn.setAttribute('aria-expanded', v); }
    btn.addEventListener('click', function (e) { e.stopPropagation(); open(panel.hidden); });
    panel.querySelector('.switcher-head button').addEventListener('click', function () { open(false); btn.focus(); });
    document.addEventListener('click', function (e) { if (!host.contains(e.target)) open(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !panel.hidden) { open(false); btn.focus(); } });
  }

  function initSwitchers() {
    var hosts = document.querySelectorAll('[data-ds-switcher]');
    if (!hosts.length) return;
    var go = function (data) { hosts.forEach(function (h) { renderSwitcher(h, data); }); };
    if (window.DS_APPS) return go(Array.isArray(window.DS_APPS) ? { categories: [], apps: window.DS_APPS } : window.DS_APPS);
    fetch(BASE + '/apps.json', { cache: 'no-cache' }).then(function (r) { return r.json(); }).then(go)
      .catch(function () { hosts.forEach(function (h) { h.hidden = true; }); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initSwitchers);
  else initSwitchers();

  window.DS_BASE = BASE;
})();
