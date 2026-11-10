# Booth Homelab Design System

The shared look and feel for Warren's self-hosted apps, so they all look like one family. Every new app pulls this repo; existing apps move to it when they're next given UI work. Modelled on Marc's Design Uniformity spec (Encore).

- **Spec:** [DESIGN-SPEC.md](DESIGN-SPEC.md) — principles, categories, components, checklist
- **Preview:** open `preview.html` — every component, with category and theme switches
- **Use it in an app:** `tools/ds-sync.sh /opt/<app>/static <category>`

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
