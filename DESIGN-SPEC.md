# Booth Homelab design spec

The shared look and feel for Warren's self-hosted apps. Every new app follows this. Existing apps move to it when they're next given UI work.

> **For Claude:** read this file before building or changing any UI in one of Warren's apps. Use the files in this repo rather than re-creating them, and never edit an app's copy under `ds/`. Change the repo and run `ds-sync.sh` instead. Section 9 is the checklist.

## 1. Principles

1. **Quiet chrome, loud data.** Neutrals do the structure. Colour is only for meaning: the accent says "this app / this is active", status colours say OK, in progress, look at this, broken.
2. **Dark first, light equal.** Dark is the default. Light follows the device unless the user picks one, and every screen is checked in both.
3. **One way to do each thing.** One button per role, one badge per status, one empty state. No page-specific one-offs.
4. **Phone width is a real target.** Everything works at 375px with no sideways scroll. The sidebar becomes a bottom nav under 760px.
5. **Calm motion.** 150ms fades. Nothing bounces. Live data updates in place.
6. **Plain words.** UK English, sentence case, say what happened ("Tower has less than 100 GB free"), not "Error 507".

## 2. What's in the repo

| Path | What it is |
|---|---|
| `css/tokens.css` | Colours, type, spacing, radii, shadows. Category and theme switching. |
| `css/components.css` | Base styles, the app shell and every component. |
| `js/ds.js` | Theme switch (`dsTheme`), toasts (`dsToast`), icon helper (`dsIcon`). No dependencies. |
| `glyphs/icons.svg` | All glyphs as one sprite. |
| `preview.html` | Every component on one page, with category and theme switches. Open it to check a change. |
| `tools/ds-sync.sh` | Copies the system into an app's static folder. |

## 3. Categories

Set once per app on `<html data-category="…">`. The accent, buttons, focus rings, active nav and progress bars all follow it.

| Value | Accent | Apps |
|---|---|---|
| `media` | `#F5B82E` amber | Media finder, BookHound, TubeYard, Encore-style apps |
| `network` | `#3B82F6` blue | Switchboard, WarrDash |
| `home` | `#22C55E` green | Home Assistant panels, iPad frame |
| `monitoring` | `#A855F7` purple | servermonitor |
| `dev` | `#EC4899` pink | n8n and automation tools |
| `tools` | `#14B8A6` teal | Wine Tracker, shopping list, links |

The app icon and name tell apps apart within a category. The colours match the links page.

## 4. Status colours

`--ok` green, `--info` blue, `--warn` orange, `--bad` red. Use them through `.badge`, `.banner`, `.progress` and `.toast`. Never use a status colour for decoration, and never use the accent to mean a status.

## 5. Layout shell

```html
<div class="app">
  <aside class="sidebar">…brand, .nav-link items…</aside>
  <div class="main">
    <header class="topbar">…</header>
    <main class="content">…</main>
    <nav class="bottom-nav">…same 3–5 top items…</nav>
  </div>
</div>
```

Mark the current page with `aria-current="page"` on both the sidebar link and the bottom-nav link.

## 6. Components

Card (`.card`, `.card.tight`, `.card.link`), stat tile (`.stat`), buttons (`.btn`, `.btn-primary`, `.btn-ghost`, `.btn-danger`, `.btn-sm`, `.btn-icon`), badges (`.badge.ok|info|warn|bad|accent`), forms (`.field`, `.input`, `.select`, `.textarea`, `.search`, `.switch`), tabs (`.tabs` + `.tab[aria-selected]`), table (`.table-wrap` + `.table`), progress, banner, empty state, media tiles (`.media-grid` + `.media-tile` + `.media-art`, add `.square` for albums and audiobooks), list rows, toasts, skeletons. See `preview.html` for markup.

Only one `.btn-primary` per view: the main thing the page is for.

## 7. Icons

```html
<svg class="icon"><use href="/ds/glyphs/icons.svg#search"/></svg>
```

Stroke icons on a 24px grid, `currentColor`. Sizes: `.icon.sm` 14px, default 18px, `.icon.lg` 22px. Add new glyphs to the sprite in this repo, never inline in an app.

## 8. Using it in an app

```bash
ds-sync.sh /opt/<app>/static media
```

```html
<html lang="en-GB" data-category="media">
<head>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/static/ds/css/tokens.css">
  <link rel="stylesheet" href="/static/ds/css/components.css">
  <script>window.DS_ICONS = '/static/ds/glyphs/icons.svg';</script>
  <script src="/static/ds/js/ds.js"></script>
</head>
```

App-specific CSS goes in the app's own stylesheet, loaded after these, and uses the tokens (`var(--surface)`, `var(--s4)`) rather than raw values.

## 9. Checklist before shipping a screen

- [ ] `data-category` set on `<html>`
- [ ] Looks right in dark **and** light
- [ ] Works at 375px with no sideways scroll; bottom nav shows on phones
- [ ] Only tokens, no hard-coded colours or spacing
- [ ] One primary button per view
- [ ] Status shown with badges, not coloured text
- [ ] Empty, loading and error states all exist
- [ ] Words are UK English, sentence case, and say what happened
