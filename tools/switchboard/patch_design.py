"""Add the Design page to Switchboard -> v2.13.0
Shows every app that uses the Booth design system (found by scanning running LXCs for ds-sync),
which version each is on against the repo, and Update buttons."""
import shutil
from pathlib import Path

B = Path("/opt/proxbridge")
app, ui = B / "app.py", B / "static/index.html"
shutil.copy(app, B / "app.py.bak-2.12.0")
shutil.copy(ui, B / "static/index.html.bak-2.12.0")


def sub(s, old, new, count=1):
    n = s.count(old)
    assert n == count, f"expected {count} of {old[:60]!r}, found {n}"
    return s.replace(old, new)


BACKEND = r'''
# ---------------------------------------------------------------- design system (ds-sync)
DS_REPO = "https://github.com/Wazzabooth1/design-system.git"
DS_SCAN = ("command -v ds-sync >/dev/null 2>&1 && ds-sync --status || true")


async def ds_head() -> dict:
    p = await asyncio.create_subprocess_exec("git", "ls-remote", DS_REPO, "refs/heads/main",
                                             stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
    out, _ = await asyncio.wait_for(p.communicate(), 20)
    sha = (out.decode().split() or [""])[0]
    return {"sha": sha, "short": sha[:7]}


async def ds_scan() -> list[dict]:
    rows, jobs = [], []
    for sid in CFG["servers"]:
        res = await resources(sid)
        for g in res["guests"]:
            if g["type"] == "lxc" and g.get("status") == "running":
                jobs.append((sid, g))

    gate = asyncio.Semaphore(4)   # the SSH link to Proxmox can't take 27 channels at once

    async def one(sid, g):
        try:
            async with gate:
                r = await guest_run(g["vmid"], DS_SCAN, sid, 30, "design system check")
        except Exception:
            return []
        out = []
        for line in (r.get("output") or "").splitlines():
            parts = line.split("|")
            if len(parts) != 5:
                continue
            appid, dest, cat, ver, t = parts
            out.append({"server": sid, "vmid": g["vmid"], "guest": g.get("name"), "app": appid, "dir": dest,
                        "category": cat, "version": ver, "short": ver.split(" ")[0] if ver != "missing" else "",
                        "synced": int(t or 0)})
        return out

    for chunk in await asyncio.gather(*(one(s, g) for s, g in jobs)):
        rows.extend(chunk)
    return sorted(rows, key=lambda r: (r["category"], r["app"]))
'''

ROUTES = r'''
@app.get("/api/design")
async def design_get(req: Request):
    require(req)
    head, apps = await asyncio.gather(ds_head(), ds_scan())
    for a in apps:
        a["current"] = bool(head["short"]) and a["short"] == head["short"]
    return {"head": head, "apps": apps, "repo": DS_REPO.removesuffix(".git")}


@app.post("/api/design/{sid}/{vmid}/sync")
async def design_sync(sid: str, vmid: int, req: Request):
    require(req)
    r = await guest_run(vmid, "ds-sync --all", sid, 180, "design system update")
    log("ui", f"{sid}/{vmid}", "design system update", ok=r.get("exit_code") == 0, detail=(r.get("output") or "")[-400:])
    return {"ok": r.get("exit_code") == 0, "output": (r.get("output") or "")[-2000:]}


'''

UI = r'''
/* ======================= design system ======================= */
let DSG = null;
async function renderDesign(force) {
  const m = $('#page');
  if (!DSG || force) {
    m.innerHTML = pageHead('Design system', 'Checking which apps use it…') + '<div class="card"><div class="hint">Scanning running containers. This takes about 30 seconds…</div></div>';
    try { DSG = await api('/api/design'); } catch (e) { m.innerHTML = pageHead('Design system', '') + `<div class="card"><div class="hint">Couldn't check: ${esc(e.message)}</div></div>`; return; }
  }
  const d = DSG, behind = d.apps.filter(a => !a.current);
  const right = `<button class="btn" onclick="renderDesign(true)">${ic('refresh')} Check again</button>` +
    (behind.length ? ` <button class="btn primary" onclick="dsUpdateAll()">Update ${behind.length} behind</button>` : '');
  const rows = d.apps.map(a => `<tr>
      <td><b>${esc(a.app)}</b><div class="hint">${esc(a.dir)}</div></td>
      <td>${esc(a.guest)} <span class="hint">${a.vmid}</span></td>
      <td>${esc(a.category)}</td>
      <td><code>${esc(a.short || 'missing')}</code><div class="hint">${esc(a.version.split(' ').slice(2).join(' '))}</div></td>
      <td>${a.synced ? ago(a.synced) + ' ago' : '—'}</td>
      <td><span class="pill ${a.current ? 'ok' : 'warn'}">${a.current ? 'Up to date' : 'Behind'}</span></td>
      <td style="text-align:right"><button class="btn sm" id="dsu-${a.server}-${a.vmid}" onclick="dsUpdate('${a.server}',${a.vmid})">Update</button></td>
    </tr>`).join('');
  m.innerHTML = pageHead('Design system',
      `Latest: <code>${esc(d.head.short || 'unknown')}</code> · <a href="${esc(d.repo)}" target="_blank" rel="noopener" style="color:var(--dim)">GitHub</a> · apps sync themselves nightly at 19:43`, right) +
    (d.apps.length ? `<div class="card" style="overflow-x:auto"><table><thead><tr><th>App</th><th>Container</th><th>Category</th><th>Version</th><th>Synced</th><th>Status</th><th></th></tr></thead><tbody>${rows}</tbody></table></div>`
      : `<div class="card"><b>No apps use it yet</b><div class="hint" style="margin-top:6px">New apps register with <code>ds-sync --install &lt;static dir&gt; &lt;category&gt; &lt;app-id&gt;</code> and show up here.</div></div>`);
}
async function dsUpdate(sid, vmid) {
  const b = $(`#dsu-${sid}-${vmid}`); if (b) { b.disabled = true; b.textContent = 'Updating…'; }
  try { const r = await api(`/api/design/${sid}/${vmid}/sync`, {method: 'POST'}); toast(r.ok ? 'Updated' : 'Update failed: see Activity'); }
  catch (e) { toast('Update failed: ' + e.message); }
  renderDesign(true);
}
async function dsUpdateAll() {
  const seen = new Set();
  for (const a of DSG.apps.filter(a => !a.current)) {
    const k = a.server + ':' + a.vmid; if (seen.has(k)) continue; seen.add(k);
    try { await api(`/api/design/${a.server}/${a.vmid}/sync`, {method: 'POST'}); } catch (e) {}
  }
  toast('Updated'); renderDesign(true);
}
'''

a = app.read_text()
assert "ds_scan" not in a, "already patched"
a = sub(a, 'VERSION = "2.12.0"', 'VERSION = "2.13.0"')
a = sub(a, '@app.get("/api/connectors")\n', BACKEND + '\n@app.get("/api/connectors")\n')
a = sub(a, '@app.get("/healthz")\n', ROUTES + '@app.get("/healthz")\n')
app.write_text(a)

h = ui.read_text()
h = sub(h, "crew: renderCrew,\n", "crew: renderCrew, design: renderDesign,\n")
h = sub(h, "    ${link('activity', 'Activity', 'activity')}\n",
        "    ${link('design', 'Design system', 'grid')}\n    ${link('activity', 'Activity', 'activity')}\n")
h = sub(h, "api('/api/info').then(start)", UI + "api('/api/info').then(start)")
ui.write_text(h)
print("patched to 2.13.0")
