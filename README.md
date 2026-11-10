# Booth Homelab Design System

The shared look and feel for Warren's self-hosted apps, so they all look like one family. Every new app pulls this repo; existing apps move to it when they're next given UI work. Modelled on Marc's Design Uniformity spec (Encore).

- **Spec:** [DESIGN-SPEC.md](DESIGN-SPEC.md) — principles, categories, components, checklist
- **Preview:** open `preview.html` — every component, with category and theme switches
- **New app:** start from `templates/starter.html`, copy in `templates/CLAUDE.md`, add it to `apps.json`, then register it:

  ```bash
  curl -fsSL https://raw.githubusercontent.com/Wazzabooth1/design-system/main/tools/ds-sync.sh \
    | bash -s -- --install /opt/<app>/static <category> <app-id>
  ```

  That syncs now and every evening at 19:43. Switchboard's **Design system** page shows who's behind.
- **Icons:** `python3 tools/make-icons.py <app-id>` after adding an app to `apps.json`

## Category accents (match the links page)

| Category | Accent | Example apps |
|---|---|---|
| `media` | `#F5B82E` amber | Media finder, BookHound, TubeYard |
| `network` | `#3B82F6` blue | Switchboard, WarrDash |
| `home` | `#22C55E` green | Home Assistant panels |
| `monitoring` | `#A855F7` purple | servermonitor |
| `dev` | `#EC4899` pink | n8n tools |
| `tools` | `#14B8A6` teal | Wine Tracker, shopping list |

Base neutrals (dark first): `--bg #14161a` · `--surface #1e2127` · `--border #2b2f37` · `--text #e6e6e6` · `--muted #9aa0a8`
