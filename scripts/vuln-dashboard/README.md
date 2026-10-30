# NAS vulnerability dashboard

> **Status:** Draft, not installed. Design decision D-03 in [`docs/04-design-decisions.md`](../../docs/04-design-decisions.md) is still open. Nothing here runs until that decision is accepted, after Phase 0.

Every 12 hours, the laptop reads the list of software installed on the NAS, looks each package up in public vulnerability data, and writes a local page showing what is affected, how serious it is, whether a fix exists and what changed since the last run.

## What it checks

| Item | How | Coverage |
|---|---|---|
| Debian packages (including OpenSSH, nginx, Samba, sudo) | [OSV](https://osv.dev) lookup of each installed source package and version. OSV carries the Debian security tracker data | Good for packages from Debian |
| Pending updates | `apt list --upgradable` on the NAS (uses the existing package lists, does not run `apt update`) | Everything apt knows about |
| openmediavault, Raspberry Pi kernel and firmware packages | Listed as manual checks. They come from other repositories that the Debian data does not cover | Manual |
| Raspberry Pi bootloader | `rpi-eeprom-update` status, if available | Pi 5 bootloader only |
| SSD firmware, case | Reminder only. No public feed exists | Manual |

Severity is the CVSS 3 base score where the record has one. Many Debian entries have no score or are low priority, so the page shows "fix available" and "no fix yet" separately.

## What it does not do

- It changes nothing on the NAS. It runs one read-only command over SSH, which `--print-remote-command` shows
- It does not show that the NAS is secure. It only shows publicly known issues in the software it can see
- Its output is never published. The page lists unfixed vulnerabilities and exact versions, so it stays in `~/NAS-Evidence/vuln-dashboard` (raw evidence location, outside this repository). The script refuses an output folder inside a git repository

## What it sends where

- **To the NAS:** one SSH connection, with `BatchMode` (never asks for a password)
- **To OSV (Google-run, public API):** package names and versions only. No hostnames, addresses or usernames

## Setup (after D-03 is accepted)

1. **SSH access (D-03, option 3).** A dedicated key, created on the laptop. The private key never leaves the laptop and is never shared, including with Claude Code.
   - On the laptop, create the key. It has no passphrase, so it can run unattended. The restrictions below are what limit it:
     ```
     ssh-keygen -t ed25519 -N "" -f ~/.ssh/nas_monitor_ed25519 -C nas-vuln-dashboard
     ```
   - On the NAS, add the public key (`~/.ssh/nas_monitor_ed25519.pub`) to the `authorized_keys` of the account chosen in D-03 (`<MONITOR-USER>`), locked to the one command. Print the command with:
     ```
     python3 -I scripts/vuln-dashboard/vuln_dashboard.py --print-remote-command
     ```
     The line then looks like this (placeholders):
     ```
     restrict,from="<LAPTOP-IP>",command="<output of --print-remote-command>" ssh-ed25519 <KEY> nas-vuln-dashboard
     ```
     `restrict` turns off forwarding, terminals and agent access. With `command=`, the key can run nothing else, whatever command is asked for. Log the change in document 05
   - On the laptop, add a host alias to `~/.ssh/config`:
     ```
     Host nas-monitor
         HostName <NAS-IP>
         User <MONITOR-USER>
         IdentityFile ~/.ssh/nas_monitor_ed25519
         IdentitiesOnly yes
     ```

2. **Test one run by hand:**
   ```
   python3 -I scripts/vuln-dashboard/vuln_dashboard.py --host <NAS-HOST-ALIAS>
   ```
   Then open `~/NAS-Evidence/vuln-dashboard/index.html` in a browser.

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
| `index.html` | The dashboard |
| `last-state.json` | Results of the last run, used to show what is new or gone |
| `osv-cache.json` | Vulnerability records already fetched, so each run downloads only new ones |
| `history.csv` | Date, number with a fix, number without, number of pending updates, one line per run |

## Testing without the NAS

`--input <file>` reads previously collected output instead of connecting. The script was tested this way on 30th October 2026 with made-up package versions only.
