#!/usr/bin/env python3
"""vuln_dashboard.py – check the NAS's installed software against public vulnerability data

Usage:  python3 -I scripts/vuln-dashboard/vuln_dashboard.py --host <ssh-host-alias> [--out DIR]
        python3 -I scripts/vuln-dashboard/vuln_dashboard.py --input <collected.txt> [--out DIR]
        python3 -I scripts/vuln-dashboard/vuln_dashboard.py --print-remote-command

Design: docs/04-design-decisions.md, D-03 (proposed, not yet accepted).

- Runs on the laptop. Reads the NAS over SSH with ONE read-only command (see REMOTE_CMD), so the
  key can be locked to that command with command="..." in authorized_keys. Uses BatchMode, so it
  never asks for a password
- Looks up each installed Debian source package in OSV (https://osv.dev), which carries the
  Debian security tracker data (DSA, DLA and DEBIAN-CVE records)
- Writes a static page, index.html, plus the state needed to show what changed since the last run.
  No web server: open the file in a browser
- Output is RAW: it lists unfixed vulnerabilities and exact versions. It stays outside the
  repository (default ~/NAS-Evidence/vuln-dashboard) and is never committed
- Changes nothing on the NAS. Sends package names and versions (not hostnames or addresses) to OSV

Limits: only publicly known issues; packages from non-Debian repositories (openmediavault, the
Raspberry Pi kernel and firmware) and Debian packages rebuilt by Raspberry Pi are not covered by
the Debian data and are listed for manual checks; many Debian entries are low priority. It does not show that the NAS is secure.
"""

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

UK = ZoneInfo("Europe/London")
OSV = "https://api.osv.dev/v1"
# CISA Known Exploited Vulnerabilities catalogue: CVEs that attackers are known to be using. Plain download, sends nothing about the NAS
KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
DEFAULT_OUT = Path.home() / "NAS-Evidence" / "vuln-dashboard"

# One command, read-only. Section markers let one SSH call return everything
REMOTE_CMD = (
    "cat /etc/os-release; echo '@@KERNEL@@'; uname -r; "
    "echo '@@DPKG@@'; dpkg-query -W -f='${db:Status-Abbrev}\\t${source:Package}\\t${source:Version}\\t${Package}\\t${Version}\\n'; "
    "echo '@@APT@@'; apt list --upgradable 2>/dev/null; "
    "echo '@@EEPROM@@'; (command -v rpi-eeprom-update >/dev/null && rpi-eeprom-update 2>&1) || echo 'rpi-eeprom-update not available'"
)

# Packages the Debian data does not cover: shown as manual checks
MANUAL_PREFIXES = ("openmediavault", "raspi-", "raspberrypi-", "rpi-", "linux-image-rpi", "linux-image-6")
# Source packages rebuilt by Raspberry Pi carry "rpt" or "rpi" in the version (for example 1:6.18.50-1+rpt1).
# Debian's records describe Debian's own builds, so these are listed as manual checks, not looked up
RPI_BUILD = re.compile(r"[+~](rpt|rpi)\d")


def collect(host):
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", host, REMOTE_CMD],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0 and "@@DPKG@@" not in r.stdout:
        sys.exit(f"SSH collection failed (exit {r.returncode}): {r.stderr.strip()[:300]}")
    return r.stdout


def parse(text):
    sections, name = {"OS": []}, "OS"
    for line in text.splitlines():
        if line.startswith("@@") and line.endswith("@@"):
            name = line.strip("@")
            sections[name] = []
        else:
            sections[name].append(line)

    os_release = dict(l.split("=", 1) for l in sections["OS"] if "=" in l)
    os_release = {k: v.strip('"') for k, v in os_release.items()}

    sources, binaries, bin2src = {}, {}, {}
    for line in sections.get("DPKG", []):
        parts = line.split("\t")
        if len(parts) != 5 or not parts[0].startswith("ii"):
            continue
        _, src, src_ver, pkg, ver = parts
        sources.setdefault(src, src_ver)
        binaries[pkg] = ver
        bin2src[pkg] = src

    # Pending updates, by binary package and by the source package it comes from
    pending, pending_src = {}, {}
    for line in sections.get("APT", []):
        if "/" in line and "[upgradable from:" in line:
            pkg = line.split("/", 1)[0]
            new = line.split()[1] if len(line.split()) > 1 else "?"
            pending[pkg] = new
            pending_src.setdefault(bin2src.get(pkg, pkg), new)

    return {
        "os": os_release,
        "kernel": " ".join(sections.get("KERNEL", [])).strip(),
        "sources": sources,
        "binaries": binaries,
        "pending": pending,
        "pending_src": pending_src,
        "eeprom": "\n".join(sections.get("EEPROM", [])).strip(),
    }


def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def get(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def query_osv(ecosystem, sources):
    """Returns {source package: [vuln ids]} for the installed versions."""
    names = sorted(sources)
    found = {}
    print(f"Looking up {len(names)} source packages in OSV", file=sys.stderr)
    for i in range(0, len(names), 500):
        chunk = names[i:i + 500]
        queries = [{"package": {"ecosystem": ecosystem, "name": n}, "version": sources[n]} for n in chunk]
        res = post(f"{OSV}/querybatch", {"queries": queries})
        for n, q, result in zip(chunk, queries, res.get("results", [])):
            ids = [v["id"] for v in result.get("vulns", [])]
            token = result.get("next_page_token")
            while token:
                more = post(f"{OSV}/query", dict(q, page_token=token))
                ids += [v["id"] for v in more.get("vulns", [])]
                token = more.get("next_page_token")
            if ids:
                found[n] = sorted(set(ids))
    return found


def vuln_details(ids, cache_file):
    cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
    todo = [vid for vid in ids if vid not in cache]
    print(f"{len(ids)} records, {len(todo)} not yet cached", file=sys.stderr)
    for n, vid in enumerate(ids, 1):
        if n % 100 == 0:
            print(f"  {n}/{len(ids)}", file=sys.stderr)
        if vid not in cache:
            try:
                cache[vid] = get(f"{OSV}/vulns/{vid}")
            except urllib.error.URLError as e:
                cache[vid] = {"id": vid, "summary": f"(details not available: {e})"}
    cache_file.write_text(json.dumps(cache))
    return cache


def cvss3_base(vector):
    """Base score and rating from a CVSS 3.x vector, or None if it is not one."""
    if not vector.startswith("CVSS:3"):
        return None
    m = dict(part.split(":", 1) for part in vector.split("/")[1:] if ":" in part)
    try:
        changed = m["S"] == "C"
        av = {"N": .85, "A": .62, "L": .55, "P": .2}[m["AV"]]
        ac = {"L": .77, "H": .44}[m["AC"]]
        pr = {"N": .85, "L": .68 if changed else .62, "H": .5 if changed else .27}[m["PR"]]
        ui = {"N": .85, "R": .62}[m["UI"]]
        c, i, a = ({"H": .56, "L": .22, "N": 0}[m[k]] for k in ("C", "I", "A"))
    except KeyError:
        return None
    iss = 1 - (1 - c) * (1 - i) * (1 - a)
    impact = 7.52 * (iss - .029) - 3.25 * (iss - .02) ** 15 if changed else 6.42 * iss
    expl = 8.22 * av * ac * pr * ui
    if impact <= 0:
        score = 0.0
    else:
        raw = min((1.08 if changed else 1) * (impact + expl), 10)
        n = round(raw * 100000)
        score = n / 100000 if n % 10000 == 0 else (n // 10000 + 1) / 10
    rating = ("None" if score == 0 else "Low" if score < 4 else "Medium" if score < 7
              else "High" if score < 9 else "Critical")
    return score, rating


def load_kev(cache_file, max_age_hours=12):
    """Returns ({CVE: date added}, catalogue version), or (None, None) if no copy is available.
    Downloads at most every 12 hours. If the download fails, the last saved copy is used."""
    if not cache_file.exists() or time.time() - cache_file.stat().st_mtime > max_age_hours * 3600:
        try:
            data = get(KEV_URL)
            if not isinstance(data.get("vulnerabilities"), list):
                raise ValueError("unexpected format")
            cache_file.write_text(json.dumps(data))
        except (urllib.error.URLError, TimeoutError, ValueError) as err:
            print(f"KEV download failed, using the saved copy if there is one: {err}", file=sys.stderr)
    if not cache_file.exists():
        return None, None
    data = json.loads(cache_file.read_text())
    return ({v["cveID"]: v.get("dateAdded", "") for v in data["vulnerabilities"] if "cveID" in v},
            data.get("catalogVersion", "unknown"))


def notify(title, body, urgent=False):
    """Desktop pop-up on the laptop. Counts only, no package names. Does nothing if notify-send is missing."""
    if not shutil.which("notify-send"):
        return
    cmd = ["notify-send", "--app-name=NAS vulnerability check", "--urgency=" + ("critical" if urgent else "normal"), title, body]
    try:
        subprocess.run(cmd, capture_output=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        pass


def changes_since(previous, state):
    """What is worth a notification: new KEV matches, newly available fixes, new records, new pending updates.
    Nothing on the first run, when there is no previous run to compare with."""
    if not previous.get("rows"):
        return []
    old = {r["key"]: r for r in previous["rows"]}
    new_kev = [r for r in state["rows"] if r.get("kev") and not old.get(r["key"], {}).get("kev")]
    new_fix = [r for r in state["rows"] if r["fixed"] and not old.get(r["key"], {}).get("fixed")]
    new_rec = [r for r in state["rows"] if r["key"] not in old]
    new_pend = set(state["pending"]) - set(previous.get("pending", {}))
    out = []
    if new_kev:
        out.append(f"{len(new_kev)} actively exploited (CISA KEV)")
    if new_fix:
        out.append(f"{len(new_fix)} with a new fix available")
    if new_rec:
        out.append(f"{len(new_rec)} new records")
    if new_pend:
        out.append(f"{len(new_pend)} new pending updates")
    return out


def summarise(vid, record, pkg, ecosystem, kev=None):
    fixed = None
    for aff in record.get("affected", []):
        p = aff.get("package", {})
        if p.get("name") == pkg and p.get("ecosystem") == ecosystem:
            for rng in aff.get("ranges", []):
                for ev in rng.get("events", []):
                    if "fixed" in ev:
                        fixed = ev["fixed"]
    severity = "unrated"
    for sev in record.get("severity", []):
        base = cvss3_base(sev.get("score", ""))
        severity = f"{base[1]} ({base[0]:.1f})" if base else f"{sev.get('type', 'rated')}, see record"
        if base:
            break
    aliases = [a for a in record.get("aliases", []) + record.get("upstream", []) if a.startswith("CVE-")]
    text = record.get("summary") or (record.get("details") or "").split("\n")[0]
    exploited = sorted(c for c in set(aliases) if kev and c in kev)
    return {"id": vid, "cves": sorted(set(aliases))[:5], "fixed": fixed, "severity": severity, "summary": text[:200],
            "kev": exploited}


RATINGS = ["Critical", "High", "Medium", "Low", "None", "CVSS 4", "Unrated"]


def rating(row):
    """Rating group used by the filter. CVSS 4 vectors are not scored here, so they get their own group."""
    first = row["severity"].split(" ")[0]
    if first in RATINGS:
        return first
    return "CVSS 4" if row["severity"].startswith("CVSS_V4") else "Unrated"


def score(row):
    m = re.search(r"\((\d+(?:\.\d)?)\)", row["severity"])
    return float(m.group(1)) if m else -1.0


def render(state, previous, out_file):
    e = html.escape
    new_ids = {r["key"] for r in state["rows"]} - {r["key"] for r in previous.get("rows", [])}
    gone = [r for r in previous.get("rows", []) if r["key"] not in {x["key"] for x in state["rows"]}]
    with_fix = [r for r in state["rows"] if r["fixed"]]
    no_fix = [r for r in state["rows"] if not r["fixed"]]
    exploited = [r for r in state["rows"] if r.get("kev")]
    kev_note = (f"CISA KEV catalogue {e(state['kev_version'])}" if state.get("kev_version")
                else "CISA KEV catalogue not available this run")

    def table(rows):
        if not rows:
            return "<p class=muted>None.</p>"
        out = ["<table class=vt><tr><th>Package</th><th>Installed</th><th>Record</th><th>CVE</th><th>Fixed in</th>"
               "<th>Update pending</th><th>Severity</th><th>Summary</th></tr>"]
        for r in sorted(rows, key=lambda r: (not r.get("kev"), r["key"] not in new_ids, -score(r), r["package"], r["id"])):
            mark = " <span class=new>new</span>" if r["key"] in new_ids else ""
            if r.get("kev"):
                mark += f" <span class=new>exploited: {e(', '.join(r['kev']))}</span>"
            attrs = (f"data-sev='{e(rating(r))}' data-fix='{1 if r['fixed'] else 0}' "
                     f"data-kev='{1 if r.get('kev') else 0}' data-new='{1 if r['key'] in new_ids else 0}'")
            out.append(f"<tr class=vr {attrs}><td>{e(r['package'])}{mark}</td><td>{e(r['installed'])}</td>"
                       f"<td><a href='https://osv.dev/vulnerability/{e(r['id'])}'>{e(r['id'])}</a></td>"
                       f"<td>{e(', '.join(r['cves']))}</td><td>{e(r['fixed'] or '-')}</td>"
                       f"<td>{e(r['pending'] or '-')}</td><td>{e(r['severity'])}</td><td>{e(r['summary'])}</td></tr>")
        return "\n".join(out) + "</table><p class='muted fnone' hidden>No rows match the filter.</p>"

    pending = "".join(f"<li>{e(p)} → {e(v)}</li>" for p, v in sorted(state["pending"].items())) or "<li>None</li>"
    manual = "".join(f"<li>{e(p)} {e(v)}</li>" for p, v in sorted(state["manual"].items())) or "<li>None</li>"
    rpi = "".join(f"<li>{e(p)} {e(v)}</li>" for p, v in sorted(state.get("rpi_builds", {}).items())) or "<li>None</li>"
    resolved = "".join(f"<li>{e(r['package'])}: {e(r['id'])}</li>" for r in gone) or "<li>None</li>"
    counts = {g: sum(1 for r in state["rows"] if rating(r) == g) for g in RATINGS}
    sev_boxes = "".join(f"<label><input type=checkbox class=fsev value='{e(g)}' checked> {e(g)} ({counts[g]})</label>"
                        for g in RATINGS if counts[g])

    page = f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width, initial-scale=1"><title>NAS vulnerability check</title>
<style>
:root{{--bg:#fff;--fg:#1a1a1a;--muted:#666;--line:#ddd;--new:#b3261e;--card:#f6f6f6}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151515;--fg:#eee;--muted:#999;--line:#333;--new:#ff8a80;--card:#202020}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif;margin:0 auto;max-width:1200px;padding:16px}}
table{{border-collapse:collapse;width:100%;font-size:13px;display:block;overflow-x:auto}}
th,td{{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}}
.muted{{color:var(--muted)}} .new{{color:var(--new);font-weight:600}} a{{color:inherit}}
.cards{{display:flex;flex-wrap:wrap;gap:12px}} .card{{background:var(--card);border-radius:8px;padding:12px 16px;min-width:150px}}
.card b{{display:block;font-size:24px}} pre{{background:var(--card);padding:12px;overflow-x:auto}}
.filters{{background:var(--card);border-radius:8px;padding:12px 16px;margin:16px 0;display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center}}
.filters label{{white-space:nowrap}} .filters input[type=search]{{font:inherit;padding:4px 8px;min-width:200px;max-width:100%;
background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:4px}}
</style></head><body>
<h1>NAS vulnerability check</h1>
<p class=muted>Last run: {e(state['run'])} · Source: {e(state['source'])} · OS: {e(state['os_name'])} ·
Kernel: {e(state['kernel'])} · Data: OSV ({e(state['ecosystem'])}), {kev_note}. Raw output: do not publish.</p>
<div class=cards>
<div class=card><b>{len(exploited)}</b>actively exploited</div>
<div class=card><b>{len(with_fix)}</b>fix available</div>
<div class=card><b>{len(no_fix)}</b>no fix yet</div>
<div class=card><b>{len(new_ids)}</b>new since last run</div>
<div class=card><b>{len(state['pending'])}</b>updates pending</div>
</div>
<div class=filters role=group aria-label="Filter records">
<strong>Filter:</strong> {sev_boxes}
<label><input type=checkbox id=ffix> Only with a fix available</label>
<label><input type=checkbox id=fkev> Only actively exploited</label>
<label><input type=checkbox id=fnew> Only new since last run</label>
<input type=search id=fq placeholder="Search package, CVE or text" aria-label="Search records">
<span class=muted id=fcount></span>
</div>
<p class=muted>Fixed records drop off by themselves: each run asks OSV about the versions installed now, so a record
the installed version is no longer affected by is listed once under "Gone since last run" and then not again.
CVSS 4 ratings are not calculated here; open the record to see them.</p>
<h2>Actively exploited (CISA Known Exploited Vulnerabilities)</h2>
<p class=muted>Records whose CVE is in CISA's catalogue of flaws attackers are known to be using. Update or mitigate these first.</p>
{table(exploited)}
<h2>Fix available</h2>{table(with_fix)}
<h2>No fix available yet</h2>{table(no_fix)}
<h2>Pending updates (apt)</h2><ul>{pending}</ul>
<h2>Gone since last run</h2><ul>{resolved}</ul>
<h2>Manual checks (not covered by the Debian data)</h2>
<ul>{manual}
<li>Kernel {e(state['kernel'])}: check Raspberry Pi kernel release notes</li>
<li>SSD firmware: check the manufacturer's support page</li></ul>
<h3>Source packages rebuilt by Raspberry Pi (not looked up)</h3>
<p class=muted>Debian's vulnerability records describe Debian's builds, not these. Check the Raspberry Pi release notes.</p>
<ul>{rpi}</ul>
<h3>Raspberry Pi bootloader (rpi-eeprom-update)</h3><pre>{e(state['eeprom'] or 'No output')}</pre>
<p class=muted>Only publicly known issues are shown. This page does not show that the NAS is secure.</p>
<script>
(function () {{
  var KEY = "nas-dashboard-filters";
  var sev = Array.prototype.slice.call(document.querySelectorAll(".fsev"));
  var fix = document.getElementById("ffix"), kev = document.getElementById("fkev"),
      nw = document.getElementById("fnew"), q = document.getElementById("fq"),
      count = document.getElementById("fcount");
  var rows = Array.prototype.slice.call(document.querySelectorAll("tr.vr"));
  try {{
    var saved = JSON.parse(localStorage.getItem(KEY) || "null");
    if (saved) {{
      sev.forEach(function (b) {{ b.checked = saved.sev.indexOf(b.value) !== -1; }});
      fix.checked = !!saved.fix; kev.checked = !!saved.kev; nw.checked = !!saved.nw;
    }}
  }} catch (err) {{}}
  function apply() {{
    var on = sev.filter(function (b) {{ return b.checked; }}).map(function (b) {{ return b.value; }});
    var text = q.value.trim().toLowerCase(), shown = 0;
    rows.forEach(function (r) {{
      var ok = on.indexOf(r.dataset.sev) !== -1 && (!fix.checked || r.dataset.fix === "1") &&
               (!kev.checked || r.dataset.kev === "1") && (!nw.checked || r.dataset.new === "1") &&
               (!text || r.textContent.toLowerCase().indexOf(text) !== -1);
      r.hidden = !ok; if (ok) shown++;
    }});
    count.textContent = "Showing " + shown + " of " + rows.length + " rows";
    Array.prototype.forEach.call(document.querySelectorAll("table.vt"), function (t) {{
      var any = t.querySelector("tr.vr:not([hidden])") !== null;
      t.hidden = !any; t.nextElementSibling.hidden = any;
    }});
    try {{
      localStorage.setItem(KEY, JSON.stringify({{sev: on, fix: fix.checked, kev: kev.checked, nw: nw.checked}}));
    }} catch (err) {{}}
  }}
  sev.concat([fix, kev, nw]).forEach(function (el) {{ el.addEventListener("change", apply); }});
  q.addEventListener("input", apply);
  apply();
}})();
</script>
</body></html>"""
    tmp = out_file.with_suffix(".tmp")
    tmp.write_text(page)
    tmp.replace(out_file)


def in_git_repo(path):
    r = subprocess.run(["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
    return r.returncode == 0


def main():
    os.umask(0o077)  # files written hold unfixed vulnerabilities and exact versions: owner only
    ap = argparse.ArgumentParser(description="NAS vulnerability dashboard (runs on the laptop).")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--host", help="SSH host alias from ~/.ssh/config")
    src.add_argument("--input", type=Path, help="previously collected output, instead of SSH")
    src.add_argument("--print-remote-command", action="store_true", help="print the one command run on the NAS")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--no-notify", action="store_true", help="no desktop notification")
    a = ap.parse_args()

    if a.print_remote_command:
        print(REMOTE_CMD)
        return

    # Check before creating anything. An existing folder is used as it is: its permissions are
    # never changed, only reported, so a wrong --out cannot lock up a folder such as your home
    out = a.out.expanduser().resolve()
    existing = next(p for p in [out, *out.parents] if p.exists())
    if in_git_repo(existing):
        sys.exit("Refusing: the output folder is inside a git repository. The output is raw and must stay outside.")
    if out.exists():
        if out.stat().st_mode & 0o077:
            print(f"Warning: {out} can be read by other users. Consider: chmod 700 {out}", file=sys.stderr)
    else:
        out.mkdir(parents=True, mode=0o700)
    a.out = out
    global NOTIFY
    NOTIFY = bool(a.host) and not a.no_notify

    raw = collect(a.host) if a.host else a.input.read_text()
    data = parse(raw)
    if not data["sources"]:
        sys.exit("No installed packages found in the collected output.")
    version = data["os"].get("VERSION_ID", "")
    ecosystem = f"Debian:{version}" if version else "Debian"

    manual = {p: v for p, v in data["binaries"].items() if p.startswith(MANUAL_PREFIXES)}
    rpi_builds = {s: v for s, v in data["sources"].items() if RPI_BUILD.search(v)}
    debian_sources = {s: v for s, v in data["sources"].items() if s not in rpi_builds}
    found = query_osv(ecosystem, debian_sources)
    details = vuln_details(sorted({v for ids in found.values() for v in ids}), a.out / "osv-cache.json")
    kev, kev_version = load_kev(a.out / "kev-cache.json")

    # Map each source package to its installed binaries, to show pending updates against it
    rows = []
    for pkg, ids in found.items():
        for vid in ids:
            s = summarise(vid, details.get(vid, {}), pkg, ecosystem, kev)
            pend = data["pending_src"].get(pkg)
            rows.append(dict(s, key=f"{pkg}|{vid}", package=pkg, installed=data["sources"][pkg], pending=pend))

    state_file = a.out / "last-state.json"
    previous = json.loads(state_file.read_text()) if state_file.exists() else {}
    state = {
        "run": datetime.now(UK).strftime("%d %B %Y, %H:%M UK time"),
        "source": a.host or "file", "os_name": data["os"].get("PRETTY_NAME", "unknown"),
        "kernel": data["kernel"], "ecosystem": ecosystem, "rows": rows,
        "pending": data["pending"], "manual": manual, "rpi_builds": rpi_builds, "eeprom": data["eeprom"],
        "kev_version": kev_version,
    }
    render(state, previous, a.out / "index.html")
    state_file.write_text(json.dumps(state))
    with open(a.out / "history.csv", "a") as h:
        h.write(f"{datetime.now(UK).isoformat(timespec='minutes')},{sum(1 for r in rows if r['fixed'])},{sum(1 for r in rows if not r['fixed'])},{len(data['pending'])},{sum(1 for r in rows if r.get('kev'))}\n")
    changes = changes_since(previous, state)
    if NOTIFY and changes:
        notify("NAS vulnerability check", ", ".join(changes) + ". Open the dashboard for details.",
               urgent=any("exploited" in c for c in changes))
    print(f"Done: {len(rows)} records for {len(found)} packages. Open {a.out / 'index.html'}")


NOTIFY = False

if __name__ == "__main__":
    try:
        main()
    except SystemExit as err:
        if NOTIFY and err.code not in (0, None):
            notify("NAS vulnerability check failed", "The last run did not finish. See: journalctl --user -u nas-vuln-dashboard")
        raise
    except Exception:
        if NOTIFY:
            notify("NAS vulnerability check failed", "The last run did not finish. See: journalctl --user -u nas-vuln-dashboard")
        raise
