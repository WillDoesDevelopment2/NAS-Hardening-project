# Phase 3 Plan

> **Status:** Draft v0.04 · Last updated: 13th November 2026
> **Author:** William Drummond
> **Related:** [01-scope-and-assets.md](01-scope-and-assets.md) (objective O-4, assets A-02 and A-04, roles in section 6.4, success criteria in section 13, open questions in section 14) · [02-threat-analysis.md](02-threat-analysis.md) (T-05, T-08, T-09, T-10, T-15, T-20) · [03-security-requirements.md](03-security-requirements.md) · [04-design-decisions.md](04-design-decisions.md) (D-02, D-06, D-09, D-16) · [05-verification.md](05-verification.md) (V-25, section 8)
> **Note:** Drafted with AI assistance on 12th November 2026, as proposals for the owner. The owner chose BorgBackup and answered section 2 on 12th November 2026, and accepted the decisions, requirements, tests and completion criterion the same day. No change to the NAS for Phase 3 until section 5 of this plan is complete. Placeholders such as `<BACKUP-USER>`, `<REPO-PATH>` and `<LAPTOP-TS-IP>` stay as placeholders in this file.

---

## 1. Goal

Back up the laptop to the NAS automatically, encrypted on the laptop before anything leaves it, in a way the laptop itself cannot delete or overwrite, and prove that a restore works (document 01, objective O-4 and section 13). The tool is BorgBackup over SSH, through Tailscale.

Outputs: a backup set-up, a written restore procedure, and a key storage procedure (T-15).

Why Borg over SSH (owner, 12th November 2026): the backups are encrypted on the laptop, the SSH key can be locked to append-only Borg for one repository, and it uses the existing SSH service, so no new port is opened on the NAS (V-01 and V-04 stay as they are).

## 2. Questions for the owner

Answer these before the decisions in section 3 are recorded. Each has a suggestion to start from. Answered by the owner on 12th November 2026.

### 2.1 What is backed up

1. **Which folders?** Suggestion: the home folder, run as your own user. System settings in `/etc` would need a second job run as root, so leave them out unless you want them.
   - **Owner answer, 12th November 2026:** the home folder (files and app and desktop settings) and system settings in `/etc`, plus a list of installed packages so the laptop can be rebuilt. One job run as root by a system timer, so it can read `/etc`
2. **What is left out?** Suggestion: caches (`~/.cache`), the bin, downloads you can fetch again, virtual machine images, and the SD card images in `~/NAS-Evidence/`. Those images are large and hold the NAS's keys, and a copy of them on the NAS does not help if the NAS is lost.
   - **Owner answer, 12th November 2026:** the SD card images are left out, and the owner plans to delete them from the laptop to save space. Caches and the bin left out as suggested. `~/Downloads` is left out. Keys are backed up but passwords are not, as the password manager keeps them. Included: SSH keys (`~/.ssh`), GPG keys (`~/.gnupg`) and the laptop's SSH host keys (`/etc/ssh`). Left out: passwords: saved browser logins (Firefox `logins.json` and `key4.db`, Chromium `Login Data`), the desktop keyring (`~/.local/share/keyrings`), Wi-Fi passwords (`/etc/NetworkManager/system-connections`), password hashes (`/etc/shadow`, `/etc/gshadow` and their backups), and access tokens stored by command-line tools (for example `~/.git-credentials`, `~/.config/gh/hosts.yml`, `~/.claude/.credentials.json`, `~/.netrc`). Also left out: the laptop's WireGuard keys and tunnel file (`/etc/wireguard`), as D-20 keeps no recovery copy of WireGuard private keys, and the backup job's own passphrase file and SSH key in `/root`. The list is in D-22, checked by V-44
3. **How much data is there?** The SSD is 1 TB and also holds your personal files. A rough figure sets how many archives fit and how long the first backup takes over Wi-Fi.
   - **Owner answer, 12th November 2026:** measured by Claude Code on 12th November 2026: the home folder is about 188 GB without caches, the bin and `~/NAS-Evidence/`, of which `~/Downloads` is about 86 GB. The bin holds about 32 GB. `/etc` is about 23 MB. Borg compresses and removes duplicates, so the repository will be smaller
4. **The phone:** document 01 includes it in Phase 3, but Borg has no Android app, so the phone needs a different tool. Suggestion: laptop first, then the phone as a second part of Phase 3 with its own questions, or in a later phase.
   - **Owner answer, 12th November 2026:** accepted: laptop first. The phone is deferred, with its own questions later

### 2.2 Where the backups live on the NAS

1. **Repository location:** a folder on the encrypted SSD (D-06), owned by the backup account. Suggestion: **not** shared over SMB, so nothing that mounts a share can reach the backups (T-05).
   - **Owner answer, 12th November 2026:** accepted
2. **Backup account:** a dedicated `<BACKUP-USER>` (document 01, section 6.4: "Backup client – computer"), with no password, SSH key login only, no sudo rights, and membership of `_ssh` so that SSH allows it (`AllowGroups root _ssh`, V-09).
   - **Owner answer, 12th November 2026:** accepted
3. **Limits on the laptop's key**, in the backup account's `authorized_keys`, the same pattern as Claude Code's key (D-02):
   ```
   restrict,from="<LAPTOP-TS-IP>",command="borg serve --append-only --restrict-to-repository <REPO-PATH>" ssh-ed25519 <PUBLIC-KEY> laptop-backup
   ```
   `restrict` turns off forwarding and terminals. `from=` allows only the laptop's Tailscale address, so backups run over Tailscale, at home as well as away. `command=` means the key can only run Borg, append-only, in that one repository. Do you accept the Tailscale address only, or also the LAN address?
   - **Owner answer, 12th November 2026:** accepted: the Tailscale address only. As the job runs as root (2.1.1), the private key is in root's SSH folder on the laptop
4. **Borg on the NAS:** the `borgbackup` package from Debian. It is a Debian package, not a third-party plugin, so suggestion: no SR-15 review, but record the version. The laptop and the NAS must both run Borg 1.x (Borg 2 cannot read 1.x repositories). Check that both versions are 1.2 or later.
   - **Owner answer, 12th November 2026:** accepted. Noted on 12th November 2026: the laptop runs Linux Mint 22.2, whose package is Borg 1.2.x, and Debian 13 has Borg 1.4.x. Both are 1.x, so they work together. Versions recorded when installed
5. **SSD locked after a reboot (D-06):** backups fail until you unlock it. Suggestion: accept this, and let the missed-backup warning (2.5) catch a long gap. A test checks that nothing is written to the SD card while the SSD is locked (V-42).
   - **Owner answer, 12th November 2026:** accepted

### 2.3 Encryption and keys (T-15)

1. **Encryption mode:**
   - `repokey-blake2`: the key is stored in the repository, protected by your passphrase. To restore you need only the passphrase (and the NAS)
   - `keyfile-blake2`: the key stays on the laptop. The NAS holds nothing usable even if the passphrase leaks, but losing the laptop loses the key unless you keep a copy

   Suggestion: `repokey-blake2` with a long random passphrase, plus an exported copy of the key (`borg key export --paper`), so a restore does not depend on the NAS's copy of the key.
   - **Owner answer, 12th November 2026:** `repokey-blake2`, with a paper and Proton Pass export of the key
2. **Where the passphrase and key copy are kept:** T-15 asks for two separate places. Suggestion: the passphrase and key export in Proton Pass, and a paper copy of both kept at home, away from the NAS.
   - **Owner answer, 12th November 2026:** accepted
3. **How the scheduled job gets the passphrase:** from the desktop keyring (`secret-tool`), or from a file readable only by your user. Either way, someone who controls your laptop account can read it. That is the T-08 case, which append-only (2.2.3) is there to limit. Which one?
   - **Owner answer, 12th November 2026:** follows from 2.1.1: from a file readable only by root on the laptop (mode 600), not the desktop keyring

### 2.4 Schedule, retention and pruning

1. **How often?** Suggestion: daily, from a systemd timer on the laptop with `Persistent=true`, so a backup missed while the laptop was off runs when it is next on and online.
   - **Owner answer, 12th November 2026:** accepted: daily, from a system timer with `Persistent=true`
2. **How long are old backups kept?** Suggestion: 7 daily, 4 weekly and 6 monthly.
   - **Owner answer, 12th November 2026:** accepted
3. **Who prunes?** With append-only, the laptop cannot really remove anything. A prune from the laptop only marks archives as deleted, and the data stays until a compact is run without append-only. So old archives are removed from the NAS side, by you, in an admin session, with the passphrase typed in, not stored on the NAS. Before compacting, check that no archive was deleted unexpectedly, because compacting makes any deletion permanent. Suggestion: monthly, with `borg check` at the same time.
   - **Owner answer, 12th November 2026:** accepted: monthly from the NAS side, with `borg check`
4. **Client tool:**
   - plain `borg` in a short script with a systemd timer: the least software, and the easiest to show as evidence
   - borgmatic: a configuration file instead of a script, with retention, checks and failure hooks built in, but one more package
   - Vorta: a desktop app, easy to use, but harder to record and test

   Suggestion: plain `borg` with a script and timer, or borgmatic if you would rather edit a configuration file than a script.
   - **Owner answer, 12th November 2026:** plain `borg` with a script and a systemd timer

### 2.5 Knowing when backups stop (T-20)

1. **How is a missed or failed backup noticed?** Suggestion: a check on the NAS, on a timer, that sends an email through OMV's notifications (D-09) when the repository has had no new data for longer than the limit. It runs on the NAS, so it still works if the laptop is lost or its timer silently stops. It looks only at file times, so it needs no passphrase.
   - **Owner answer, 12th November 2026:** accepted
2. **What limit?** Suggestion: 48 hours. Longer trips without the laptop will give false alarms, which is acceptable.
   - **Owner answer, 12th November 2026:** accepted: 48 hours
3. **On the laptop as well?** A desktop notification when a backup run fails (systemd `OnFailure=`). Optional.
   - **Owner answer, 12th November 2026:** accepted as optional

### 2.6 Restore and checks

1. **Restore test:** restore a sample folder from the newest archive and from an older one into a temporary folder, and compare them with the originals. How often? Suggestion: at the end of Phase 3, then every 3 months.
   - **Owner answer, 12th November 2026:** accepted
2. **Restore without the laptop:** the case you are protecting against. On another device or a live USB: join Tailscale, add a new SSH key for the backup account (by you, on the NAS), and restore using only the passphrase and key copy from 2.3.2. Suggestion: test this once in Phase 3.
   - **Owner answer, 12th November 2026:** accepted
3. **`borg check`:** monthly. `--verify-data` reads every chunk and is slow on the Pi, so suggestion: every 3 months.
   - **Owner answer, 12th November 2026:** accepted

### 2.7 Off-site copy

1. Document 01, section 14 asks whether there is an offline or off-site copy. The NAS is one place: a fire, a theft or a failed SSD (T-10, T-11) takes the backups with it. Options:
   - none for now, recorded as an accepted risk
   - an external USB drive, copied to from time to time and kept somewhere else
   - an encrypted Borg copy at a hosted service. Borg encrypts before upload, but it brings back a third party, against objective O-1

   Suggestion: accept the risk in Phase 3 and revisit at the 5th January 2027 review, unless you already have a drive for it.
   - **Owner answer, 12th November 2026:** accepted: no off-site copy in Phase 3, recorded as an accepted risk and revisited at the 5th January 2027 review

### 2.8 Effect on earlier set-up

1. **SD card image (before any Phase 3 change):** the NAS can no longer be reached physically, so the image is taken while it runs. Options: the `openmediavault-backup` plugin (from omv-extras, so it needs an SR-15 review first) writing to the SSD, or `dd` over SSH, which gives an image like after a power cut. Either way, the image holds the NAS's WireGuard and Tailscale keys (D-17). Which one?
   - **Owner answer, 12th November 2026:** `dd` over SSH, run by the owner, as `dd` is not in Claude Code's sudo rule (D-02). The image is written to the SSD, hashed, copied to the laptop over Tailscale and hashed again. It is not put in the Borg backup, as it holds the NAS's keys (D-17)
   - **Change, 12th November 2026 (owner):** Claude Code takes the image, with one `dd` command added to its sudo rule (D-02 change). The image is sent straight to the laptop, not written to the SSD first (D-28)
2. **Tailscale access rules:** they already allow the laptop to reach port 22 on the NAS (phase1-changes.md, section 5.3). Suggestion: no change.
   - **Owner answer, 12th November 2026:** accepted
3. **Service inventory (document 01, section 6.3):** no new listener. Add a row for the backup account to the users and roles table in section 6.4.
   - **Owner answer, 12th November 2026:** accepted
4. **Claude Code (D-02):** Claude Code does not hold the backup key. Tests that use it (V-25, V-37) are run by you. Claude Code can run V-04 and V-12 when you approve them.
   - **Owner answer, 12th November 2026:** accepted

## 3. Decisions to record (document 04)

To be written once section 2 is answered. Proposed numbers follow the last decision, D-20.

| Proposed | Decision | Questions |
|---|---|---|
| D-21 | Backup tool and transport. Owner, 12th November 2026: BorgBackup over SSH, through Tailscale | 1, 2.2.4 |
| D-22 | What is backed up, and the phone | 2.1 |
| D-23 | Backup account, repository location and key limits (append-only) | 2.2 |
| D-24 | Encryption mode and where the passphrase and key are kept | 2.3 |
| D-25 | Schedule, retention, pruning and the client tool | 2.4, 2.6.3 |
| D-26 | Missed-backup warning | 2.5 |
| D-27 | Off-site copy, or the risk accepted | 2.7 |
| D-28 | How the SD card image is taken while the NAS runs | 2.8.1 |

D-21 to D-28 accepted in document 04 on 12th November 2026.

## 4. Requirements to propose (document 03)

Drafts only. The owner accepts, changes or rejects each one and sets its priority.

| Proposed ID | Requirement | Threats | Suggested priority |
|---|---|---|---|
| SR-24 | The laptop is backed up to the NAS automatically at least once a day while it is on and online, and the backup is encrypted on the laptop before it is sent | T-09, T-10 | Must |
| SR-25 | The laptop's backup credentials cannot delete or overwrite existing backups. Old backups are removed only from the NAS side, by the administrator | T-05, T-08 | Must |
| SR-26 | The backup account can reach only its own repository: no shell, no other files, no forwarding, and only from the laptop's Tailscale address | T-08, T-12 | Must |
| SR-27 | The repository passphrase and a copy of its key are kept in two separate places, and the restore procedure is written down | T-15 | Must |
| SR-28 | A failed backup, or no new backup for 48 hours, sends a warning to the administrator | T-20 | Should |
| SR-29 | A restore is tested at the end of Phase 3 and then every 3 months, including from an older archive and without the laptop | T-09, T-10, T-15 | Must |
| SR-30 | Passwords on the laptop are not included in its backups. The password manager is the place they are kept | T-08 | Should |

SR-24 to SR-30 accepted in document 03 on 12th November 2026.

## 5. Before any Phase 3 change

- [x] Phase 2 closed in document 05, section 8 (12th November 2026, with deviations)
- [x] Questions in section 2 answered (12th November 2026)
- [x] Decisions in section 3 recorded in document 04 (D-21 to D-28 accepted, 12th November 2026)
- [x] Requirements in section 4 accepted, with priorities (SR-24 to SR-30, 12th November 2026)
- [x] Phase 3 completion criterion written (document 05, section 8) and agreed (12th November 2026)
- [x] Phase 3 tests written, with expected results, before they are run (document 05, section 4.4, confirmed 12th November 2026)
- [x] SD card image taken with the method from 2.8.1, with date and SHA-256 hash recorded (13th November 2026, by the owner, phase3-changes.md, 2.3. Hash in document 05, section 7)

## 6. Draft test plan

V-25 is already in document 05, section 9. New test IDs start at V-37. Expected results to be confirmed by the owner before any test is run. Run-from entries follow D-02: Claude Code runs tests on the NAS only when the owner approves them by ID.

### 6.1 New tests

| Test ID | Requirement | What it checks | Tool and command | Run from | Expected result |
|---|---|---|---|---|---|
| V-25 | SR-25 | Backup key cannot delete backups | With the laptop's backup key: `borg delete` on one archive, then `borg prune` with a very short retention. Then, on the NAS as the administrator, check the archives can be recovered | Laptop (owner), then the NAS (owner) | The laptop's commands appear to work, but every archive is still recoverable from the NAS side, as append-only keeps the data. Nothing is lost until the administrator compacts the repository |
| V-37 | SR-26 | Backup key limits | With the laptop's backup key: `ssh <BACKUP-USER>@nas` (no command), `ssh <BACKUP-USER>@nas ls`, `sftp`, a port forward, Borg pointed at another path, and a connection from the laptop's LAN address instead of its Tailscale address | Laptop (owner) | No shell and no command other than Borg. SFTP and the forward refused. Another path refused by `--restrict-to-repository`. The LAN address refused by `from=` |
| V-38 | SR-24 | Encrypted on the laptop | `borg info` on the laptop. On the NAS, search the repository files for a known text string from a backed-up file | Laptop (owner). The NAS (owner, as the repository is readable only by the backup account) | `borg info` shows `repokey-blake2` (or the mode chosen in 2.3.1). The text string is not found in the repository files |
| V-39 | SR-24 | Daily backup runs | `systemctl list-timers` on the laptop, and `borg list` after a few days, including after the laptop was off at the scheduled time | Laptop (owner) | The timer is listed. One archive for each day the laptop was on and online. A missed run happens the next time the laptop is on |
| V-40 | SR-29 | Restore from the newest and an older archive | `borg extract` of a sample folder from two archives into a temporary folder, then `diff -r` against the originals, or against what they held then | Laptop (owner) | Both restores complete. The newest matches the current files. The older one matches the files as they were at that date |
| V-41 | SR-27, SR-29 | Restore without the laptop | On another device or a live USB: join Tailscale, add a temporary SSH key for the backup account on the NAS, and restore a sample folder using only the passphrase and key copy from where they are kept | Another device (owner) | The restore works without anything from the laptop. The temporary key is removed afterwards, and the removal logged |
| V-42 | D-06, SR-24 | SSD locked | Reboot the NAS and run a backup before unlocking the SSD. Then check the SD card for anything written under the repository path | Laptop and the NAS (owner) | The backup fails with "repository does not exist" or similar. Nothing is written to the SD card. After the unlock, the next backup works |
| V-43 | SR-28 | Missed-backup warning | Stop the laptop's timer for longer than the limit in 2.5.2, or point a run at a wrong passphrase | The NAS's email notification (owner) | A warning email arrives within one check interval after the limit is passed. The warning clears after the next successful backup |
| V-44 | SR-30 | No passwords in the backup | `borg list` of the newest archive, searched for the excluded paths in D-22, and for `~/.ssh` and `~/.gnupg` | Laptop (owner, as root) | None of the excluded paths is in the archive. `~/.ssh` and `~/.gnupg` are |

### 6.2 Earlier tests to repeat, with new expected results

| Test ID | Change to the expected result |
|---|---|
| V-01, V-02 | Unchanged from Phase 2: no new port |
| V-04 | Unchanged from Phase 2: no new listener. Borg runs only inside SSH sessions |
| V-09 | Unchanged. `allowgroups root _ssh`, with the backup account in `_ssh` |
| V-12 | One new account, the backup account, with no sudo rights and no password login |

## 7. Draft completion criterion (document 05, section 8)

Phase 3 is complete when: the decisions in section 3 are recorded; the requirements in section 4 are verified by the tests in section 6, with evidence in `evidence/phase3/`; the restore procedure and key storage procedure are written; V-25, V-40 and V-41 pass; the phone is covered or deferred with a reason; the off-site copy is in place or the risk is accepted in document 04; and an SD card image of the Phase 3 system is recorded.

## 8. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.01 | 12th November 2026 | First draft: questions, decisions, requirements, test plan and completion criterion, with BorgBackup as the owner's chosen tool (drafted with AI assistance) | Owner request after Phase 2 closed |
| 0.02 | 12th November 2026 | Owner answers recorded: home folder and `/etc` from a root job, `repokey-blake2`, plain `borg` with a timer, all other suggestions accepted. Data size measured | Owner answers |
| 0.03 | 12th November 2026 | Owner answers: `~/Downloads` left out, keys backed up but not passwords, SD card image by `dd` over SSH. SR-30 and V-44 added. D-21 to D-28, SR-24 to SR-30, test plan and completion criterion drafted in documents 03, 04 and 05, and accepted by the owner. Section 5 ticked except the SD card image | Owner answers and decision |
| 0.04 | 13th November 2026 | Section 5: SD card image ticked. Every item is now done | SD card image taken |
