#!/usr/bin/env bash
# ds-sync: keep an app's copy of the Booth design system up to date.
#
#   ds-sync --install <static dir> <category> <app-id>   register an app, sync now, add the nightly job
#   ds-sync --all                                        sync every registered app (the nightly job runs this)
#   ds-sync --status                                     one line per app: app|dir|category|version|synced(epoch)
#   ds-sync <static dir> <category> [app-id]             one-off sync without registering
#
#   e.g.  curl -fsSL https://raw.githubusercontent.com/Wazzabooth1/design-system/main/tools/ds-sync.sh \
#           | bash -s -- --install /opt/bookhound/static media bookhound
#
# Copies css/, js/, glyphs/, fonts/, apps.json and the app's own icons (brand/<app-id>/) into
# <static dir>/ds/. Never edit files under ds/ in an app: change the design-system repo instead.
# The nightly job runs at 19:43 and logs to /var/log/ds-sync.log. Switchboard's Design page reads --status.
set -euo pipefail

REPO="${DS_REPO:-https://github.com/Wazzabooth1/design-system.git}"
CACHE="${DS_CACHE:-/opt/.design-system}"
CONF_DIR=/etc/ds-sync.d
BIN=/usr/local/bin/ds-sync

need_git() {
  command -v git >/dev/null && return
  if command -v apt-get >/dev/null; then DEBIAN_FRONTEND=noninteractive apt-get -qq update && apt-get -qq install -y git >/dev/null
  elif command -v apk >/dev/null; then apk add --quiet git
  else echo "ds-sync: git is needed and I can't install it here" >&2; exit 1; fi
}

fetch() {
  need_git
  if [ -d "$CACHE/.git" ]; then
    git -C "$CACHE" fetch -q --depth 1 origin main
    git -C "$CACHE" reset -q --hard origin/main
  else
    rm -rf "$CACHE"; git clone -q --depth 1 "$REPO" "$CACHE"
  fi
}

sync_one() {  # dest category app
  local dest="$1" cat="$2" app="${3:-}"
  mkdir -p "$dest/ds"
  for d in css js glyphs fonts; do rm -rf "$dest/ds/$d"; cp -r "$CACHE/$d" "$dest/ds/$d"; done
  cp "$CACHE/apps.json" "$dest/ds/apps.json"
  rm -rf "$dest/ds/brand"
  if [ -n "$app" ] && [ -d "$CACHE/brand/$app" ]; then cp -r "$CACHE/brand/$app" "$dest/ds/brand"; fi
  git -C "$CACHE" log -1 --format='%h %cs %s' > "$dest/ds/VERSION"
  echo "$cat" > "$dest/ds/CATEGORY"
  echo "$(date '+%F %T') ${app:-app} -> $dest/ds ($(cut -c1-7 "$dest/ds/VERSION"))"
}

case "${1:-}" in
  --install)
    dest="${2:?usage: ds-sync --install <static dir> <category> <app-id>}"; cat="${3:?category}"; app="${4:?app-id}"
    fetch
    install -m 755 "$CACHE/tools/ds-sync.sh" "$BIN"
    mkdir -p "$CONF_DIR"
    printf 'APP=%q\nDEST=%q\nCATEGORY=%q\n' "$app" "$dest" "$cat" > "$CONF_DIR/$app.conf"
    echo "43 19 * * * root $BIN --all >> /var/log/ds-sync.log 2>&1" > /etc/cron.d/ds-sync
    chmod 644 /etc/cron.d/ds-sync
    command -v cron >/dev/null || command -v crond >/dev/null || \
      { command -v apt-get >/dev/null && DEBIAN_FRONTEND=noninteractive apt-get -qq install -y cron >/dev/null && systemctl enable --now cron >/dev/null 2>&1 || true; }
    sync_one "$dest" "$cat" "$app"
    echo "registered $app: syncs nightly at 19:43"
    ;;
  --all)
    shopt -s nullglob; confs=("$CONF_DIR"/*.conf)
    [ ${#confs[@]} -eq 0 ] && { echo "no apps registered"; exit 0; }
    fetch
    for c in "${confs[@]}"; do ( . "$c"; sync_one "$DEST" "$CATEGORY" "$APP" ) || echo "$(date '+%F %T') failed: $c"; done
    ;;
  --status)
    shopt -s nullglob
    for c in "$CONF_DIR"/*.conf; do
      ( . "$c"; v=$(cat "$DEST/ds/VERSION" 2>/dev/null || echo "missing"); t=$(stat -c %Y "$DEST/ds/VERSION" 2>/dev/null || echo 0)
        printf '%s|%s|%s|%s|%s\n' "$APP" "$DEST" "$CATEGORY" "$v" "$t" )
    done
    ;;
  ""|-h|--help) sed -n '2,16p' "$0"; exit 0 ;;
  *)
    fetch; sync_one "$1" "${2:-tools}" "${3:-}" ;;
esac
