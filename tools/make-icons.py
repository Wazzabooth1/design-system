#!/usr/bin/env python3
"""Make home screen icons and a web app manifest for each app in apps.json.

    python3 tools/make-icons.py            # every app
    python3 tools/make-icons.py bookhound  # just one

Writes brand/<app>/: icon.svg, maskable.svg, and (if rsvg-convert is installed)
apple-touch-icon.png (180), icon-192.png, icon-512.png, maskable-512.png, favicon-32.png,
plus manifest.webmanifest. The icon is the app's glyph on its category colour, so apps in a
category look like a set and the glyph tells them apart.
"""
import json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATS = {  # accent, glyph colour (same pairs as tokens.css)
    "media": ("#f5b82e", "#111317"), "network": ("#3b82f6", "#ffffff"), "home": ("#22c55e", "#0b1a10"),
    "monitoring": ("#a855f7", "#ffffff"), "dev": ("#ec4899", "#ffffff"), "tools": ("#14b8a6", "#071a18"),
}
BG = "#14161a"

sprite = open(os.path.join(HERE, "glyphs", "icons.svg")).read()
glyphs = dict(re.findall(r'<symbol id="([^"]+)" viewBox="0 0 24 24">(.*?)</symbol>', sprite, re.S))
data = json.load(open(os.path.join(HERE, "apps.json")))
only = set(sys.argv[1:])
rsvg = shutil.which("rsvg-convert")


def svg(app, maskable):
    bg, fg = CATS.get(app["category"], CATS["tools"])
    body = glyphs.get(app.get("icon") or "grid", glyphs["grid"])
    scale = 11 if maskable else 13           # glyph size: maskable keeps inside the 80% safe zone
    off = 256 - 12 * scale
    shape = ('<rect width="512" height="512" fill="%s"/>' % bg if maskable else
             '<rect width="512" height="512" rx="116" fill="%s"/>' % bg)
    sheen = ('<rect width="512" height="512" %s fill="url(#s)"/>' % ('' if maskable else 'rx="116"'))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs><linearGradient id="s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".16"/><stop offset="1" stop-color="#000" stop-opacity=".12"/></linearGradient></defs>
  {shape}{sheen}
  <g transform="translate({off} {off}) scale({scale})" fill="none" stroke="{fg}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{body}</g>
</svg>
'''


made = 0
for app in data["apps"]:
    if only and app["id"] not in only:
        continue
    out = os.path.join(HERE, "brand", app["id"])
    os.makedirs(out, exist_ok=True)
    for name, mask in (("icon.svg", False), ("maskable.svg", True)):
        open(os.path.join(out, name), "w").write(svg(app, mask))
    icons = [{"src": "icon.svg", "sizes": "any", "type": "image/svg+xml"}]
    if rsvg:
        for src, dst, size in (("icon.svg", "apple-touch-icon.png", 180), ("icon.svg", "icon-192.png", 192),
                               ("icon.svg", "icon-512.png", 512), ("maskable.svg", "maskable-512.png", 512),
                               ("icon.svg", "favicon-32.png", 32)):
            subprocess.run([rsvg, "-w", str(size), "-h", str(size), "-o", os.path.join(out, dst), os.path.join(out, src)], check=True)
        icons += [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]
    manifest = {
        "name": app["name"], "short_name": app["name"][:12], "start_url": "/", "scope": "/",
        "display": "standalone", "background_color": BG, "theme_color": BG, "icons": icons,
    }
    json.dump(manifest, open(os.path.join(out, "manifest.webmanifest"), "w"), indent=2)
    made += 1

print(f"made icons for {made} app(s){'' if rsvg else ' (SVG only: install librsvg2-bin for PNGs)'}")
