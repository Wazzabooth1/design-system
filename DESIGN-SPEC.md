# Booth Homelab design spec

The shared look and feel for Warren's self-hosted apps. Every new app follows this. Existing apps move to it when they're next given UI work.

> **For Claude:** read this file before building or changing any UI in one of Warren's apps. Use the files in this repo rather than re-creating them, and never edit an app's copy under `ds/`. Change the repo and run `ds-sync.sh` instead. Section 13 is the checklist.

## 1. Principles

1. **Quiet chrome, loud data.** Neutrals do the structure. Colour is only for meaning: the accent says "this app / this is active", status colours say OK, in progress, look at this, broken.
2. **Dark first, light equal.** Dark is the default. Light follows the device unless the user picks one, and every screen is checked in both.
3. **One way to do each thing.** One button per role, one badge per status, one empty state. No page-specific one-offs.
4. **Phone width is a real target.** Everything works at 375px with no sideways scroll. The sidebar becomes a bottom nav under 760px.
5. **Use the whole screen.** `.content` fills the width beside the sidebar on any monitor — no centred or left-parked column. Lists, grids and side panels stretch; only add `.content-narrow` for text-heavy pages like settings forms.
6. **Calm motion.** 150ms fades. Nothing bounces. Live data updates in place.
7. **Plain words.** UK English, sentence case, say what happened ("Tower has less than 100 GB free"), not "Error 507".

## 2. What's in the repo

| Path | What it is |
|---|---|
| `css/tokens.css` | Colours, type, spacing, radii, chart colours, the self-hosted Inter font. Category, theme and mode switching. |
| `css/components.css` | Base styles, the app shell, every component, the app switcher, wall/TV mode and control tiles. |
| `js/ds.js` | Theme (`dsTheme`), mode (`dsMode`), toasts (`dsToast`), icons (`dsIcon`), the app switcher. No dependencies. |
| `js/chart-palette.js` | `dsChart()`: chart colours read live from the tokens, for any charting library. |
| `glyphs/icons.svg` | All glyphs as one sprite. |
| `fonts/` | Inter (variable weight). Apps never load Google Fonts. |
| `apps.json` | Every homelab app: name, URL, category, glyph. Feeds the app switcher, the links page and the icon generator. |
| `brand/<app>/` | Each app's home screen icons and web app manifest (made by `tools/make-icons.py`). |
| `templates/` | `starter.html` (a new app's first page, everything wired up) and `CLAUDE.md` (drop into a new app's repo). |
| `preview.html` | Every component on one page, with category, theme and mode switches. |
| `tools/ds-sync.sh` | Installs into an app, syncs it, and runs nightly. |
| `tools/switchboard/` | The patch that adds the Design system page to Switchboard. |

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

### Side panel (live activity)

Anything that keeps updating while you use the rest of the app (a downloads queue, what's playing on the wall panel, a running job) lives in the **side panel**, not in the page: right-hand side, 360px, sticky under the top bar with its own scroll. Media finder's Downloads panel is the reference.

```html
<div class="main">
  <header class="topbar">…</header>
  <div class="workspace">
    <main class="content">…</main>
    <aside class="side-panel" aria-label="Downloads">
      <div class="side-panel-head"><h2><svg class="icon">…</svg>Downloads</h2></div>
      <div><div class="side-group-title">Now <span>2</span></div>…</div>
    </aside>
  </div>
  <nav class="bottom-nav">…</nav>
</div>
```

- Shown from 1200px wide. Narrower, the panel hides and the same content moves to its own page (a bottom-nav item) or the top of the main page, wrapped in `.narrow-only` so it never appears twice.
- One side panel per app. Group its contents with `.side-group-title`; controls for what's in it (pause, stop, cancel) sit right there with it.
- The page's main job never goes in the side panel. It's for watching and nudging things that are already happening.
- Hidden in wall and TV mode; `.narrow-only` copies show instead.

## 6. Components

Side panel (`.workspace` + `.side-panel`, see section 5), card (`.card`, `.card.tight`, `.card.link`), stat tile (`.stat`), buttons (`.btn`, `.btn-primary`, `.btn-ghost`, `.btn-danger`, `.btn-sm`, `.btn-icon`), badges (`.badge.ok|info|warn|bad|accent`), forms (`.field`, `.input`, `.select`, `.textarea`, `.search`, `.switch`), tabs (`.tabs` + `.tab[aria-selected]`), table (`.table-wrap` + `.table`), progress, banner, empty state, media tiles (`.media-grid` + `.media-tile` + `.media-art`, add `.square` for albums and audiobooks), list rows, toasts, skeletons. See `preview.html` for markup.

Only one `.btn-primary` per view: the main thing the page is for.

## 7. Icons

```html
<svg class="icon"><use href="/ds/glyphs/icons.svg#search"/></svg>
```

Stroke icons on a 24px grid, `currentColor`. Sizes: `.icon.sm` 14px, default 18px, `.icon.lg` 22px. Add new glyphs to the sprite in this repo, never inline in an app.

## 8. App switcher

Put `<div data-ds-switcher></div>` in the top bar and `data-app="<app id>"` on `<html>`. It reads `apps.json` (synced into `ds/`) and shows every app grouped by category, with the current one highlighted. When an app is built, add it to `apps.json` and run `python3 tools/make-icons.py <app id>`. The links page (http://192.168.1.138, LXC 138) is built from the same file, so the app shows up there too after the nightly sync (or run `ds-sync --all` on LXC 138 to see it straight away). Remove an app from `apps.json` when it's retired.

## 9. Wall and TV mode

`<html data-mode="wall">` for touch panels (iPad frame, magic mirror) and `data-mode="tv"` for across-the-room screens (the LG TV dashboard). Or open any app with `?mode=wall` / `?mode=tv` (remembered on that device; `?mode=normal` clears it). Modes scale the whole type and spacing scale, hide the sidebar and bottom nav, grow buttons to 56px and give TV a heavy focus ring for the remote. Use `.tile-grid` + `button.tile[aria-pressed]` for big square controls (lights, scenes, appliances).

## 10. Charts

Use `dsChart().series` in fixed order: series 1 is always the same entity, and a filter that hides one never repaints the rest. Six series at most; the rest fold into "Other" or small multiples. Never two y-axes. Text on charts uses `--text`/`--muted`, never a series colour. In light mode three of the colours sit under 3:1 on white, so charts always carry direct labels or a table view. Status colours are for status, not series.

## 11. Icons and installing to a phone

`tools/make-icons.py` draws each app's glyph on its category colour (the same family look as the links page) and writes PNGs plus a manifest. `templates/starter.html` has the head tags that make an app open full screen from the home screen.

## 12. Using it in an app

Register once. This syncs now, adds the app to `/etc/ds-sync.d/` and installs a nightly job (19:43) that pulls changes:

```bash
curl -fsSL https://raw.githubusercontent.com/Wazzabooth1/design-system/main/tools/ds-sync.sh \
  | bash -s -- --install /opt/<app>/static <category> <app id>
```

Then start from `templates/starter.html` and copy `templates/CLAUDE.md` into the app. App-specific CSS goes in the app's own stylesheet, after the system's, and uses tokens (`var(--surface)`, `var(--s4)`) rather than raw values. Switchboard's **Design system** page lists every registered app, shows which are behind the repo, and updates them on demand.

## 13. Checklist before shipping a screen

- [ ] Registered with `ds-sync --install`, and listed in `apps.json` (which also puts it on the links page)
- [ ] `data-category` and `data-app` set on `<html>`; app switcher in the top bar
- [ ] Looks right in dark **and** light
- [ ] Works at 375px with no sideways scroll; bottom nav shows on phones
- [ ] Still usable with `?mode=wall` if it'll ever be on a panel
- [ ] Only tokens, no hard-coded colours, spacing or fonts
- [ ] One primary button per view
- [ ] Status shown with badges, not coloured text
- [ ] Live activity (queues, now playing) is in the side panel, with a `.narrow-only` fallback under 1200px
- [ ] Empty, loading and error states all exist
- [ ] Words are UK English, sentence case, and say what happened
