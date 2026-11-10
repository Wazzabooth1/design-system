# UI rules for this app

This app uses the **Booth homelab design system** (github.com/Wazzabooth1/design-system).

- Before building or changing any screen, read `DESIGN-SPEC.md` in that repo and follow its checklist.
- The system lives in this app's `ds/` folder (inside the static dir). **Never edit anything under `ds/`.** Change the design-system repo and run `ds-sync --all` instead. It also updates itself every evening at 19:43.
- Set `<html data-category="…" data-app="…">` and load the files in the order shown in `templates/starter.html`.
- App-specific CSS goes in the app's own stylesheet, after the system's, and uses tokens (`var(--surface)`, `var(--s4)`) not raw colours or pixel values.
- Status is shown with badges, banners and toasts, never coloured text on its own.
- Charts take their colours from `dsChart()` (`ds/js/chart-palette.js`) in fixed series order.
- Need a new component or icon? Add it to the design-system repo so every app gets it, then sync.

Register the app once (sync now and nightly):

```bash
curl -fsSL https://raw.githubusercontent.com/Wazzabooth1/design-system/main/tools/ds-sync.sh \
  | bash -s -- --install <static dir> <category> <app-id>
```

Categories: `media`, `network`, `home`, `monitoring`, `dev`, `tools`. Add the app to `apps.json` in the repo so it appears in the app switcher and gets its icons.
