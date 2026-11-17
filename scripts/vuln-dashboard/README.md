# NAS vulnerability dashboard

> **Status:** Installed on 5th November 2026 (Phase 1 checklist, section 7). Design decision D-03 in [`docs/04-design-decisions.md`](../../docs/04-design-decisions.md), with the key held by a separate account with no sudo rights. Since Tailscale was set up, the laptop reaches the NAS over Tailscale, and the key is limited to the laptop's Tailscale address.

Every 12 hours, the laptop reads the list of software installed on the NAS, looks each package up in public vulnerability data, and writes a local page showing what is affected, how serious it is, whether a fix exists and what changed since the last run.

## What it checks

| Item | How | Coverage |
|---|---|---|
| Debian packages (including OpenSSH, nginx, Samba, sudo) | [OSV](https://osv.dev) lookup of each installed source package and version. OSV carries the Debian security tracker data | Good for packages from Debian |
| Pending updates | `apt list --upgradable` on the NAS (uses the existing package lists, does not run `apt update`) | Everything apt knows about |
| Actively exploited | Each record's CVEs are checked against CISA's [Known Exploited Vulnerabilities](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) catalogue (KEV), downloaded at most every 12 hours. Matches are listed first, with their own count | Only flaws CISA has confirmed are being used by attackers |
| openmediavault, Raspberry Pi kernel and firmware packages | Listed as manual checks. They come from other repositories that the Debian data does not cover | Manual |
| Debian packages rebuilt by Raspberry Pi (version contains `+rpt` or `+rpi`, for example the kernel, glibc and OpenSSL) | Listed as manual checks and not looked up, since Debian's records describe Debian's own builds. On 5th November 2026 this was 25 source packages, which had produced 415 of 899 records | Manual |
| Raspberry Pi bootloader | `rpi-eeprom-update` status, if available | Pi 5 bootloader only |
| SSD firmware, case | Reminder only. No public feed exists | Manual |

Severity is the CVSS 3 base score where the record has one. Many Debian entries have no score or are low priority, so the page shows "fix available" and "no fix yet" separately. Records with only a CVSS 4 vector are not scored by the script and are grouped as "CVSS 4".

## Filtering and fixed records

The page has a filter bar: tick boxes for each rating (Critical, High, Medium, Low, None, CVSS 4, Unrated, each with its count), "Only with a fix available", "Only actively exploited", "Only new since last run", and a search box for package, CVE or text. Within each table, rows are sorted with the highest score first. The filter choices are remembered in the browser on the laptop only, and the page works without them.

Fixed records drop off by themselves. Each run asks OSV about the versions installed at that moment, so once an update installs a version that is no longer affected, the record is listed once under "Gone since last run" and then not again. Nothing has to be removed by hand.

## What it does not do

- It changes nothing on the NAS. It runs one read-only command over SSH, which `--print-remote-command` shows
- It does not show that the NAS is secure. It only shows publicly known issues in the software it can see
- Its output is never published. The page lists unfixed vulnerabilities and exact versions, so it stays in `~/NAS-Evidence/vuln-dashboard` (raw evidence location, outside this repository). The script refuses an output folder inside a git repository

## What it sends where

- **To the NAS:** one SSH connection, with `BatchMode` (never asks for a password)
- **To OSV (Google-run, public API):** package names and versions only. No hostnames, addresses or usernames
- **From CISA (US government):** a plain download of the KEV catalogue. Nothing about the NAS is sent

## Notifications

After a run started with `--host` (the timer), a desktop pop-up appears on the laptop when something changed since the last run: a new KEV match (marked urgent), a fix newly available, new records, or new pending updates. It also appears if a run fails. The pop-up shows counts only, no package names. Nothing appears on the first run, or when nothing changed. Add `--no-notify` to run without pop-ups. Uses `notify-send`, and does nothing if it is not installed

## Setup

1. **SSH access (D-03, option 3).** A dedicated key, created on the laptop. The private key never leaves the laptop and is never shared, including with Claude Code.
   - On the laptop, create the key. It has no passphrase, so it can run unattended. The restrictions below are what limit it:
     ```
     ssh-keygen -t ed25519 -N "" -f ~/.ssh/nas_monitor_ed25519 -C nas-vuln-dashboard
     ```
   - In OMV, create `<MONITOR-USER>`: shell `/bin/bash` (the forced command needs a shell, so not `nologin`), groups `users` and `_ssh`, no `sudo`, a random password that is not kept. Apply the change in OMV, then check with `getent group _ssh`.
   - On the NAS, add the public key (`~/.ssh/nas_monitor_ed25519.pub`) to `~/.ssh/authorized_keys` of `<MONITOR-USER>` (folder mode 700, file mode 600, owned by that account), locked to the one command. OMV's own key field is not used, as the line needs options. Print the command with:
     ```
     python3 -I scripts/vuln-dashboard/vuln_dashboard.py --print-remote-command
     ```
     The line then looks like this (placeholders):
     ```
     restrict,from="<LAPTOP-TAILSCALE-IP>",command="<output of --print-remote-command>" ssh-ed25519 <KEY> nas-vuln-dashboard
     ```
     `<LAPTOP-TAILSCALE-IP>` is the output of `tailscale ip -4` on the laptop. `restrict` turns off forwarding, terminals and agent access. With `command=`, the key can run nothing else, whatever command is asked for. Log the change in document 05
   - On the laptop, add a host alias to `~/.ssh/config`:
     ```
     Host nas-monitor
         HostName nas
         User <MONITOR-USER>
         IdentityFile ~/.ssh/nas_monitor_ed25519
         IdentitiesOnly yes
         BatchMode yes
     ```

2. **Test one run by hand:**
   ```
   python3 -I scripts/vuln-dashboard/vuln_dashboard.py --host <NAS-HOST-ALIAS>
   ```
   Then open `~/NAS-Evidence/vuln-dashboard/index.html` in a browser. The first run fetches every vulnerability record and took about 7 minutes on 5th November 2026. Later runs use the cache.

3. **Schedule it every 12 hours** (systemd user timer, runs only while you are logged in to the laptop):
   ```
   mkdir -p ~/.config/systemd/user
   cp scripts/vuln-dashboard/nas-vuln-dashboard.{service,timer} ~/.config/systemd/user/
   # edit ~/.config/systemd/user/nas-vuln-dashboard.service: replace <REPO> and <NAS-HOST-ALIAS>
   systemctl --user daemon-reload
   systemctl --user enable --now nas-vuln-dashboard.timer
   systemctl --user list-timers nas-vuln-dashboard.timer
   ```
   If the laptop was off at a scheduled time, the check runs when it is next on.

## Files written (outside the repository)

| File | Content |
|---|---|
| `index.html` | The dashboard. All files are written readable by the owner only |
| `last-state.json` | Results of the last run, used to show what is new or gone |
| `osv-cache.json` | Vulnerability records already fetched, so each run downloads only new ones |
| `kev-cache.json` | The last CISA KEV catalogue downloaded, used if a download fails |
| `history.csv` | Date, number with a fix, number without, number of pending updates, number actively exploited (from 5th November 2026), one line per run |

## Testing without the NAS

`--input <file>` reads previously collected output instead of connecting. The script was tested this way on 30th October 2026 with made-up package versions only.
