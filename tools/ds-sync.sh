#!/usr/bin/env bash
# ds-sync.sh: pull the Booth design system into an app.
# Usage:  ds-sync.sh <app static dir> [category]
#   e.g.  ds-sync.sh /opt/bookhound/static media
# Copies css/, js/ and glyphs/ into <static dir>/ds/ and writes ds/VERSION.
# Re-run any time (or from cron) to pick up changes. Never edit files under ds/ in an app:
# change them in the design-system repo and sync instead.
set -euo pipefail

DEST="${1:?usage: ds-sync.sh <app static dir> [category]}"
CAT="${2:-}"
REPO="${DS_REPO:-https://github.com/Wazzabooth1/design-system.git}"
CACHE="${DS_CACHE:-/opt/.design-system}"

if [ -n "${DS_TOKEN:-}" ]; then
  REPO="${REPO/https:\/\//https://x-access-token:${DS_TOKEN}@}"
fi

if [ -d "$CACHE/.git" ]; then
  git -C "$CACHE" fetch -q --depth 1 origin main
  git -C "$CACHE" reset -q --hard origin/main
else
  git clone -q --depth 1 "$REPO" "$CACHE"
fi

mkdir -p "$DEST/ds"
for d in css js glyphs; do
  rm -rf "$DEST/ds/$d"
  cp -r "$CACHE/$d" "$DEST/ds/$d"
done
git -C "$CACHE" log -1 --format='%h %cs %s' > "$DEST/ds/VERSION"
[ -n "$CAT" ] && echo "$CAT" > "$DEST/ds/CATEGORY"

echo "design system $(cat "$DEST/ds/VERSION") -> $DEST/ds${CAT:+ (category: $CAT)}"
