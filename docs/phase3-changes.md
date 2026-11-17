# Phase 3 Change Steps

> **Status:** Draft v0.5 · Last updated: 15th November 2026
> **Author:** William Drummond
> **Related:** [phase3-plan.md](phase3-plan.md) · [04-design-decisions.md](04-design-decisions.md) (D-02, D-06, D-21 to D-28) · [03-security-requirements.md](03-security-requirements.md) (SR-24 to SR-30) · [05-verification.md](05-verification.md) (section 4.4, Phase 3 log)
> **Note:** Drafted with AI assistance on 12th November 2026, for OMV 8 on Debian 13 and a laptop on Linux Mint 22.2. Nothing here has been run. Each change needs the owner's approval for that change, and is logged in document 05, section 7, with the time in UK time. Placeholders such as `<BACKUP-USER>`, `<SSD-MOUNT>`, `<REPO-PATH>` and `<LAPTOP-TS-IP>` stay as placeholders in this file. Real values, the passphrase and keys stay out of the repository.

---

## 1. Before starting

- [x] Phase 3 plan, section 5, done except the SD card image (12th November 2026)
- [ ] Keep one SSH session open as `<ADMIN-USER>` while changing accounts and keys, and test from a second one
- [ ] The SSD is unlocked (D-06)
- [x] Section 2 (SD card image) done before any other section (13th November 2026, by the owner with section 2.3)

Order: 2 (image), 3 (Borg on both sides), 4 (backup account and repository folder), 5 (restricted key), 6 (create the repository and export the key), 7 (backup script and timer), 8 (missed-backup warning on the NAS), 9 (pruning routine), 10 (tests).

## 2. SD card image, taken remotely (D-28, D-02)

### 2.1 Sudo rule so Claude Code can read the SD card (D-02 change)

A change to Claude Code's access, made by the owner on the NAS. Claude Code does not change its own access.

**What it allows:** the Claude Code account can run one more command as root, with fixed options:
```
/usr/bin/dd if=/dev/mmcblk0 bs=4M status=none
```
With no `of=`, `dd` can only read the card and write it to its own output, which goes back over SSH. sudo matches the whole command line, so `dd` with any other option (another device, `of=`, `seek=`) is refused.

**What it means:** this is much wider than the rest of the rule. Reading the whole card gives Claude Code a copy of everything on it, including password hashes in `/etc/shadow`, the SSH host keys, the NAS's WireGuard private key, the Tailscale node key and OMV's configuration. Data on the SSD is not included, as it is a separate device and encrypted (D-06). The image lands only on the laptop, in `~/NAS-Evidence/`, which is already outside the repository and outside the Borg backup (D-22).

Steps, as `<ADMIN-USER>`:
1. Check the SD card's device name and size, and the path of `dd`:
   ```
   lsblk -d -o NAME,SIZE,TYPE,TRAN,MODEL
   command -v dd
   ```
   The SD card is normally `mmcblk0`, and `dd` is `/usr/bin/dd`. If either differs, stop and correct the rule below first.
2. Edit the rule file with `visudo`, which checks it before saving:
   ```
   sudo visudo -f /etc/sudoers.d/claude-readonly
   ```
   Add `/usr/bin/dd if=/dev/mmcblk0 bs=4M status=none` to the end of the `NAS_TESTS` list. The line before it needs a `, \` at the end.
3. Check the file:
   ```
   sudo visudo -c -f /etc/sudoers.d/claude-readonly
   ```
4. Claude Code then checks the rule with `sudo -n -l`, with the owner's approval, and logs it.

Rollback: remove the line with `sudo visudo -f /etc/sudoers.d/claude-readonly`. The rule is removed with the rest of D-02 at the review on 5th January 2027 at the latest.

### 2.2 Taking the image (Claude Code, when approved)

Choose a quiet time: no OMV changes or file copies while the image is taken.

On the laptop:
```
mkdir -p ~/NAS-Evidence/phase3
img=~/NAS-Evidence/phase3/nas-sd-$(TZ=Europe/London date +%F).img.gz
ssh nas-claude "bash -o pipefail -c 'sync && sudo -n /usr/bin/dd if=/dev/mmcblk0 bs=4M status=none | gzip -1'" > "$img"
echo "exit $?"
```
The image is compressed on the NAS, so only the compressed copy crosses the network, and nothing is written to the NAS. `pipefail` makes the exit code non-zero if `dd` fails as well as `gzip`.

Then check it:
```
gzip -t "$img" && echo "gzip OK"
gunzip -c "$img" | wc -c
sha256sum "$img" | tee "$img.sha256"
```
- The exit code is `0` and `gzip -t` passes. gzip's own check value catches a copy cut short or damaged on the way
- The uncompressed size equals the card's size in bytes (`lsblk -b -d -o SIZE /dev/mmcblk0` on the NAS)
- Record the date, UK time, size and SHA-256 hash in document 05, section 7

The card is copied while the system runs, so a restore boots like after a power cut (D-28). Restoring still needs physical access to write the card.

Keep the newest image. Older images can be deleted once the new one passes its checks.

### 2.3 Taking the image without Claude Code

The same image, taken by the owner with `<ADMIN-USER>`. `sudo` asks for a password, which cannot share one SSH connection with the image, so the image is written to the SSD first and then copied to the laptop. Needs the SSD unlocked (D-06).

1. Find `<SSD-MOUNT>`: `findmnt -t btrfs -o TARGET,SOURCE,SIZE`. It is the `/srv/dev-disk-by-uuid-...` line whose source is `/dev/mapper/...`. Nothing under `/srv` means the SSD is still locked
2. On the NAS, as `<ADMIN-USER>`, check the card is `mmcblk0`, then take the image:
   ```
   lsblk -d -o NAME,SIZE,TYPE,TRAN
   sudo install -d -m 700 -o <ADMIN-USER> <SSD-MOUNT>/sd-images
   sync
   sudo dd if=/dev/mmcblk0 bs=4M status=progress | gzip -1 > <SSD-MOUNT>/sd-images/nas-sd-$(date +%F).img.gz
   ```
   The folder is readable only by `<ADMIN-USER>` and is not an OMV shared folder, so it is not reachable over SMB
3. Check it on the NAS:
   ```
   cd <SSD-MOUNT>/sd-images
   gzip -t nas-sd-<DATE>.img.gz && echo "gzip OK"
   gunzip -c nas-sd-<DATE>.img.gz | wc -c
   lsblk -b -d -o SIZE /dev/mmcblk0
   sha256sum nas-sd-<DATE>.img.gz
   ```
   The two sizes must be the same
4. Copy it to the laptop and check the hash matches the one from the NAS:
   ```
   mkdir -p ~/NAS-Evidence/phase3
   scp -i ~/.ssh/nas_admin_ed25519 -o IdentitiesOnly=yes '<ADMIN-USER>@nas:<SSD-MOUNT>/sd-images/nas-sd-<DATE>.img.gz' ~/NAS-Evidence/phase3/
   sha256sum ~/NAS-Evidence/phase3/nas-sd-<DATE>.img.gz
   ```
5. Keep the newest image on the SSD as well, if wanted: it survives an SD card failure (T-18), though writing it to a new card still needs physical access. Delete older images in both places once the new one passes its checks
6. Record the date, UK time, size and SHA-256 hash in document 05, section 7

## 3. Borg on both sides (D-21)

On the NAS, as `<ADMIN-USER>`. `borgbackup` is a Debian package: it adds no service and no listening port.
```
sudo apt-get update
sudo apt-get install borgbackup
borg --version
```
On the laptop:
```
sudo apt-get install borgbackup
borg --version
```
Both must be Borg 1.x, 1.2 or later. Record both versions in the log.

Rollback: `sudo apt-get remove borgbackup` on either side.

## 4. Backup account and repository folder on the NAS (D-23)

### 4.1 Account

Accounts are made in the OMV interface, not with `useradd`, as OMV keeps its own user database (phase1-changes.md, section 1).

1. **Users > Users > Create**: `<BACKUP-USER>`, shell `/bin/sh`, groups `users` and `_ssh`, no `sudo`. Give it a long random password that is not stored anywhere: password login is off for SSH (SR-05), and the account is not used for SMB. Save and apply
2. Check from the administration session:
   ```
   getent group sudo _ssh
   id <BACKUP-USER>
   ```
   `sudo` still lists only `<ADMIN-USER>`. `_ssh` lists `<ADMIN-USER>`, the Claude Code account, `<MONITOR-USER>` and `<BACKUP-USER>`

The shell must be a real shell, not `nologin`, because SSH runs the forced command through it. The forced command in section 5 means the shell can run nothing else.

### 4.2 Repository folder

The folder is on the SSD but is **not** an OMV shared folder, so it cannot be shared over SMB (T-05):
```
sudo install -d -m 700 -o <BACKUP-USER> -g users <SSD-MOUNT>/borg
sudo install -d -m 700 -o <BACKUP-USER> -g users <SSD-MOUNT>/borg/laptop
sudo ls -ld <SSD-MOUNT>/borg <SSD-MOUNT>/borg/laptop
```
`<SSD-MOUNT>` is the SSD file system's mount point, under `/srv/dev-disk-by-uuid-...`. `<REPO-PATH>` in the rest of this file is `<SSD-MOUNT>/borg/laptop`. Both folders must show `drwx------ <BACKUP-USER> users`.

While the SSD is locked, the mount point is an empty folder on the SD card, owned by root, so `<REPO-PATH>` does not exist and Borg stops (V-42).

Rollback: delete the folders and the account in OMV.

## 5. The laptop's restricted key (D-23)

The backup job runs as root on the laptop (D-22), so the key belongs to root.

On the laptop:
```
sudo install -d -m 700 /root/.ssh
sudo ssh-keygen -t ed25519 -N '' -C laptop-backup -f /root/.ssh/nas_backup_ed25519
sudo cat /root/.ssh/nas_backup_ed25519.pub
tailscale ip -4
```
The key has no passphrase, so the timer can use it. The limits below are what protect it.

On the NAS, as `<ADMIN-USER>`, create the backup account's `authorized_keys` with one line. OMV's own key field is not used, as the line needs options (as for `<MONITOR-USER>`). The line is long, so do not paste the key by hand or type it in nano: a wrapped line or a cut-off key makes SSH ignore it (seen on 13th November 2026). Send the public key from the laptop as a file instead:
```
sudo cat /root/.ssh/nas_backup_ed25519.pub | ssh -i ~/.ssh/nas_admin_ed25519 -o IdentitiesOnly=yes <ADMIN-USER>@nas 'cat > /tmp/laptop-backup.pub'
```
Then on the NAS, in one terminal:
```
ssh-keygen -lf /tmp/laptop-backup.pub
sudo install -d -m 700 -o <BACKUP-USER> -g users /home/<BACKUP-USER>/.ssh
sudo install -m 600 -o <BACKUP-USER> -g users /dev/null /home/<BACKUP-USER>/.ssh/authorized_keys
KEY=$(cat /tmp/laptop-backup.pub)
IP='<LAPTOP-TS-IP>'
REPO='<REPO-PATH>'
sudo ls -ld "$REPO"
printf 'restrict,from="%s",command="borg serve --append-only --restrict-to-repository %s" %s\n' "$IP" "$REPO" "$KEY" | sudo tee /home/<BACKUP-USER>/.ssh/authorized_keys >/dev/null
rm /tmp/laptop-backup.pub
```
The first `ssh-keygen` must print the key's fingerprint, and `ls` must show the repository folder from section 4.2. The result is one line:
```
restrict,from="<LAPTOP-TS-IP>",command="borg serve --append-only --restrict-to-repository <REPO-PATH>" ssh-ed25519 <PUBLIC-KEY> laptop-backup
```
Check it: `sudo wc -l` on the file gives `1`, and `sudo ssh-keygen -lf` on the file gives the same fingerprint as `sudo ssh-keygen -lf /root/.ssh/nas_backup_ed25519.pub` on the laptop.

On the laptop, add an SSH entry for root, so the script does not depend on your own SSH settings:
```
sudo tee -a /root/.ssh/config >/dev/null <<'CONF'
Host nas-backup
    HostName nas
    User <BACKUP-USER>
    IdentityFile /root/.ssh/nas_backup_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 10
CONF
sudo chmod 600 /root/.ssh/config
```
Root has never connected to the NAS, so copy the host key your own account already trusts, instead of accepting it blindly:
```
ssh-keygen -F nas
ssh-keygen -F nas | grep -v '^#' | sudo tee -a /root/.ssh/known_hosts >/dev/null
sudo chmod 600 /root/.ssh/known_hosts
```
The repository address used from here on is `ssh://nas-backup` followed directly by `<REPO-PATH>`, which starts with `/srv`, so there is one slash after `nas-backup`. Borg compares it with `--restrict-to-repository` character for character. Test it:
```
sudo borg info ssh://nas-backup<REPO-PATH>
```
Before section 6 this must fail with `is not a valid repository` or `does not exist`. That shows the key, `from=` and the forced command work. `Repository path not allowed` means the address does not match the path in the key's line exactly. `Could not resolve hostname nas-backup` means the command was run without `sudo`, or on the NAS instead of the laptop.

Rollback: delete the line on the NAS, and the key and config entry on the laptop.

## 6. Creating the repository and exporting the key (D-24)

### 6.1 Passphrase

Create a long random passphrase in Proton Pass (at least 6 words or 30 random characters), saved as an item for the Borg repository. On the laptop, store it for the timer in a root-only file:
```
sudo install -m 600 /dev/null /root/.config-borg-passphrase
sudo nano /root/.config-borg-passphrase
```
Paste the passphrase on one line and save.

### 6.2 Create the repository

On the laptop:
```
sudo BORG_PASSCOMMAND='cat /root/.config-borg-passphrase' borg init --encryption=repokey-blake2 ssh://nas-backup<REPO-PATH>
```
`borg init` is allowed in append-only mode, and `--restrict-to-repository` allows only this path.

### 6.3 Export the key

```
sudo BORG_PASSCOMMAND='cat /root/.config-borg-passphrase' borg key export --paper ssh://nas-backup<REPO-PATH>
```
- Print or copy it by hand on paper, and keep it at home with a paper copy of the passphrase, away from the NAS
- Also save the export in the Proton Pass item with the passphrase
- Do not save it in a file on the laptop or in `~/NAS-Evidence/`

Rollback: before any backup, delete `<REPO-PATH>` on the NAS and start again.

## 7. Backup script and timer (D-22, D-25)

### 7.1 Exclusion list

`/etc/borg-laptop/exclude`, owned by root, mode 644. One pattern per line, in Borg's `sh:` style. `<HOME>` is your home folder (for example `/home/<USER>`):
```
# Large or can be fetched again
sh:<HOME>/Downloads
sh:<HOME>/.cache
sh:<HOME>/.local/share/Trash
sh:<HOME>/NAS-Evidence/**/*.img*
sh:<HOME>/VirtualBox VMs
sh:<HOME>/.zoom/data/cefcache
# Passwords (D-22, SR-30): the password manager keeps these
sh:<HOME>/.local/share/keyrings
sh:<HOME>/.mozilla/firefox/*/logins.json
sh:<HOME>/.mozilla/firefox/*/logins-backup.json
sh:<HOME>/.mozilla/firefox/*/key4.db
sh:<HOME>/.config/chromium/*/Login Data*
sh:<HOME>/.config/google-chrome/*/Login Data*
sh:<HOME>/.git-credentials
sh:<HOME>/.netrc
sh:<HOME>/.config/gh/hosts.yml
sh:<HOME>/.claude/.credentials.json
sh:<HOME>/.claude/channels/telegram/.env
sh:<HOME>/.thunderbird/*/logins.json
sh:<HOME>/.thunderbird/*/key4.db
sh:<HOME>/.var/app/com.obsproject.Studio/config/obs-studio/basic/profiles/*/service.json
sh:/etc/NetworkManager/system-connections
sh:/etc/shadow*
sh:/etc/gshadow*
# WireGuard keys (D-20) and the backup job's own secrets
sh:/etc/wireguard
```
The backup job's passphrase file and key are in `/root`, which is not backed up at all.

Checked on this laptop by Claude Code on 12th November 2026 (file names only, no contents read): Firefox (two profiles), Thunderbird, the desktop keyring, the GitHub CLI and Claude Code token files, the Telegram channel's `.env` file and OBS Studio (Flatpak), whose stream keys are in `service.json`. No Chromium-based browser and no `~/.gnupg`. Evolution keeps its passwords in the desktop keyring, which is already left out. Check again for new applications before the first backup.

### 7.2 Script

`/usr/local/sbin/borg-laptop-backup`, owned by root, mode 700:
```
#!/bin/sh
# Daily laptop backup to the NAS (D-21, D-22, D-25). Runs as root from a systemd timer.
set -eu

# Skip on a metered connection, such as a phone hotspot (D-25).
# To back up anyway: sudo BORG_ALLOW_METERED=1 /usr/local/sbin/borg-laptop-backup
if [ "${BORG_ALLOW_METERED:-0}" != 1 ]; then
    case "$(busctl get-property org.freedesktop.NetworkManager /org/freedesktop/NetworkManager org.freedesktop.NetworkManager Metered 2>/dev/null || true)" in
        "u 1"|"u 3") echo "Metered connection: backup skipped"; exit 0 ;;
    esac
fi
export BORG_REPO='ssh://nas-backup<REPO-PATH>'
export BORG_PASSCOMMAND='cat /root/.config-borg-passphrase'
list=/var/backups/borg-laptop-packages.txt

# A list of installed packages, so the laptop can be rebuilt (D-22)
install -d -m 755 /var/backups
{ echo "# apt-mark showmanual"; apt-mark showmanual
  echo "# flatpak"; flatpak list --app --columns=application 2>/dev/null || true
} > "$list"

borg create --stats --compression zstd,3 --exclude-caches \
    --exclude-from /etc/borg-laptop/exclude \
    ::'{hostname}-{now:%Y-%m-%dT%H:%M}' \
    <HOME> /etc "$list"
```
- Set `BORG_REPO` by editing the installed script with `sudo nano` and checking it with `sudo grep BORG_REPO`. Filling it in from a shell variable failed twice on 13th November 2026, when the variable was empty in a new terminal, and Borg then looked for a folder called by the placeholder's name
- The metered check skips the run on a phone hotspot or any connection marked as metered in the network settings (NetworkManager values 1, metered, and 3, guessed metered). The next unmetered run catches up, and a long gap sets off the warning in section 8. A skipped run ends normally, with "Metered connection: backup skipped" in its log
- No prune here: the key is append-only, and pruning is done from the NAS (section 9)
- `zstd,3` is a light compression that the laptop does quickly
- Check the script for mistakes with `sudo sh -n /usr/local/sbin/borg-laptop-backup`

### 7.3 First backup, by hand

The first backup sends everything, about 100 GB, so run it while the laptop is plugged in at home:
```
sudo /usr/local/sbin/borg-laptop-backup
sudo BORG_PASSCOMMAND='cat /root/.config-borg-passphrase' borg list ssh://nas-backup<REPO-PATH>
```
One archive is listed. Run it again: the second run sends only what changed and should take minutes.

If the connection drops during the first backup (`client_loop: send disconnect: Broken pipe`, seen on 13th November 2026), run it again: everything up to the last checkpoint is kept. For the first run, more frequent checkpoints and visible progress help:
```
sudo sh -c 'sed "s/--stats/--stats --progress --checkpoint-interval 600/" /usr/local/sbin/borg-laptop-backup | sh'
```
Keep the laptop on home Wi-Fi, plugged in and awake. Check with `tailscale ping nas` that the connection goes to the home network address, not over mobile data.

### 7.4 Timer

`/etc/systemd/system/borg-laptop-backup.service`:
```
[Unit]
Description=Laptop backup to the NAS (Borg)
Wants=network-online.target
After=network-online.target tailscaled.service

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/borg-laptop-backup
Nice=10
IOSchedulingClass=idle
```
`/etc/systemd/system/borg-laptop-backup.timer`:
```
[Unit]
Description=Daily laptop backup to the NAS

[Timer]
OnCalendar=daily
RandomizedDelaySec=1h
Persistent=true

[Install]
WantedBy=timers.target
```
Then:
```
sudo systemctl daemon-reload
sudo systemctl enable --now borg-laptop-backup.timer
systemctl list-timers borg-laptop-backup.timer
```
`Persistent=true` runs a missed backup the next time the laptop is on. If the laptop is offline or off Tailscale, the run fails and the next day's run tries again. The NAS warning (section 8) catches a long gap.

Optional: a desktop notification on failure, with `OnFailure=` and a small unit that runs `notify-send`. Not needed for the tests.

Rollback: `sudo systemctl disable --now borg-laptop-backup.timer`, and delete the two unit files, the script and `/etc/borg-laptop`.

## 8. Missed-backup warning on the NAS (D-26, SR-28)

The check looks only at file times in the repository, so it needs no passphrase. It sends email through OMV's mail settings (D-09).

`/usr/local/sbin/borg-laptop-check`, owned by root, mode 755:
```
#!/bin/sh
# Warns when the laptop's Borg repository has had no new data for 48 hours (D-26)
set -eu
repo='<REPO-PATH>'
limit_min=$((48 * 60))
if [ ! -d "$repo/data" ]; then
    echo "Laptop backup check: repository not found (is the SSD unlocked?)" | mail -s "NAS: laptop backup check failed" root
    exit 0
fi
if [ -z "$(find "$repo/data" -type f -mmin -"$limit_min" -print -quit)" ]; then
    echo "No new laptop backup data in the last 48 hours." | mail -s "NAS: no laptop backup for 48 hours" root
fi
```
Mail to `root` goes to the address set in OMV's notification settings. Check that `mail` works first:
```
echo test | mail -s "NAS test" root
```
Run it every 6 hours with a systemd timer on the NAS (`borg-laptop-check.service` and `.timer`, `OnCalendar=*-*-* 00/6:00:00`), set up as in 7.4. The script runs as root, as the repository is readable only by `<BACKUP-USER>`.

Rollback: disable the timer and delete the units and the script.

## 9. Monthly pruning and checks, from the NAS (D-25)

Once a month, as `<ADMIN-USER>` on the NAS, running Borg as `<BACKUP-USER>` directly on the repository. This does not go through the restricted key, so append-only does not apply. The passphrase is typed in, not stored on the NAS.

Borg keeps a cache for the repository in the account's home folder, which is on the SD card. To keep it on the SSD instead, add `BORG_CACHE_DIR=<SSD-MOUNT>/borg/cache` before `borg` in each command below (for example `sudo -u <BACKUP-USER> env BORG_CACHE_DIR=<SSD-MOUNT>/borg/cache borg list <REPO-PATH>`).

1. List the archives and compare them with what you expect: one a day while the laptop was on, nothing missing that was there last month:
   ```
   sudo -u <BACKUP-USER> borg list <REPO-PATH>
   ```
2. If an archive is missing that should be there, **stop**. Do not prune or compact. Append-only kept the data: follow Borg's documentation on recovering from a deletion in an append-only repository, using the transaction list in `<REPO-PATH>/transactions`
3. Otherwise, prune and compact:
   ```
   sudo -u <BACKUP-USER> borg prune --list --keep-daily 7 --keep-weekly 4 --keep-monthly 6 <REPO-PATH>
   sudo -u <BACKUP-USER> borg compact <REPO-PATH>
   sudo -u <BACKUP-USER> borg check <REPO-PATH>
   ```
   Every 3 months, use `borg check --verify-data`. It reads every chunk and takes a long time on the Pi
4. Log the date, the number of archives, and the result of `borg check` in document 05, section 7

## 10. Tests

Run the tests in document 05, section 4.4, in this order:
- After section 5: V-37
- After section 7.3: V-38 and V-44
- After a few days of the timer: V-39
- Then V-25, V-40, V-42 and V-43
- At the end: V-41, and V-01, V-04, V-09 and V-12 (Claude Code, when approved)

Then write the restore procedure (from V-40 and V-41) and the key storage procedure (from section 6) in their own short document, and check document 05, section 8.

## 11. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.1 | 12th November 2026 | Steps drafted for the remote SD card image (with a D-02 change so Claude Code can take it), Borg, the backup account, the restricted key, the repository, the backup script and timer, the missed-backup warning and monthly pruning, not yet reviewed (drafted with AI assistance) | Owner request after the Phase 3 decisions were accepted |
| 0.2 | 12th November 2026 | Section 2.3: taking the image without Claude Code, written to the SSD first and then copied to the laptop | Owner question |
| 0.3 | 12th November 2026 | Section 7.1: Thunderbird logins, the Telegram channel token and OBS stream keys added to the exclusion list, after checking which applications are on the laptop | Laptop check |
| 0.4 | 13th November 2026 | Sections 5 to 7: what was learned while running them. The key's line is written from the `.pub` file sent from the laptop, not pasted. Root trusts the host key copied from the owner's `known_hosts`. The repository address has one slash after `nas-backup`. `BORG_REPO` is set by editing the installed script. SSH keep-alives in root's settings, and what to do if the first backup's connection drops. Section 7.2: the script skips metered connections | Problems met while running sections 5 to 7 |
| 0.5 | 15th November 2026 | Section 7.1: the VirtualBox folder and Zoom's cache added to the exclusion list, after the first full backup and V-44 (D-22) | Owner decision |
