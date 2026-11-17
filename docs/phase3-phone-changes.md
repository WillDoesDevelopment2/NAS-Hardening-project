# Phase 3 Part 2 Change Steps: Phone Backups

> **Status:** Draft v0.31 · Last updated: 17th November 2026
> **Author:** William Drummond
> **Related:** [phase3-phone-plan.md](phase3-phone-plan.md) · [04-design-decisions.md](04-design-decisions.md) (D-06, D-14, D-15, D-16, D-26, D-29 to D-31) · [03-security-requirements.md](03-security-requirements.md) (SR-31 to SR-34) · [05-verification.md](05-verification.md) (section 4.5, Phase 3 log) · [phase3-changes.md](phase3-changes.md) (the laptop's steps, same pattern)
> **Note:** Drafted with AI assistance on 15th November 2026, for OMV 8 on Debian 13, an Android 16 phone with Termux from F-Droid, and the laptop on Linux Mint 22.2. Nothing here has been run. Each change needs the owner's approval for that change, and is logged in document 05, section 7, with the time in UK time. Placeholders stay as placeholders in this file: `<PHONE-USER>` (the phone's account), `<DEVICE>` (the phone's folder name, for example `phone`), `<SSD-MOUNT>`, `<NAS-TS-IP>` and `<PHONE-TS-IP>` (Tailscale addresses).

---

## 1. Before starting

- [x] Phone plan, section 5: decisions, requirements and tests accepted (15th November 2026)
- [x] Root check on the phone (plan, 2.5.1), answer recorded: not rooted (15th November 2026)
- [x] Google's backup turned off on the phone (Settings, Google, Backup) (owner, 16th November 2026)
- [x] Tailscale on the phone connected and approved (D-14). Its address is `<PHONE-TS-IP>`: `tailscale status` on the laptop lists it
- [x] The SSD is unlocked (D-06)
- [ ] Keep one SSH session open as `<ADMIN-USER>` while changing accounts and keys, and test from a second one

Order: 2 (checks on the NAS), 3 (snapshot volume and folders), 4 (account), 5 (Termux), 6 (keys), 7 (sync script), 8 (schedule), 9 (snapshots timer), 10 (WhatsApp and the app list), 11 (tests).

## 2. Checks on the NAS (read-only)

```
apt-cache policy rsync btrfs-progs
command -v rrsync btrfs
rrsync -h 2>&1 | head -20
findmnt -no FSTYPE,SOURCE <SSD-MOUNT>
```
Expected: `rsync` and `btrfs-progs` installed, `rrsync` at `/usr/bin/rrsync`, and `btrfs` on the SSD. Note which of `-wo`, `-no-del` and `-no-overwrite` the help lists. If `-no-overwrite` is missing, the photos key in section 6.3 drops it, and the sync script's `--ignore-existing` (section 7) and the snapshots (section 9) cover overwrites instead. If `rsync` is not installed, stop: installing it is a separate approved change (a Debian package, no service, like Borg in phase3-changes.md section 3).

## 3. Snapshot volume and device folders (D-30, D-31)

`devices` is made as a Btrfs subvolume, so it can be snapshotted on its own. Snapshots go in a root-only folder beside it. Neither is an OMV shared folder, so neither is reachable over SMB.
```
sudo btrfs subvolume create <SSD-MOUNT>/devices
sudo chmod 755 <SSD-MOUNT>/devices
sudo install -d -m 700 -o root -g root <SSD-MOUNT>/snapshots
sudo install -d -m 700 -o root -g root <SSD-MOUNT>/snapshots/devices
sudo btrfs subvolume show <SSD-MOUNT>/devices | head -3
```
The device folders are made after the account (section 4.2).

While the SSD is locked, `<SSD-MOUNT>` is an empty folder on the SD card, so the device folders do not exist and `rrsync` refuses the copy. Nothing is written to the SD card.

Rollback: `sudo btrfs subvolume delete <SSD-MOUNT>/devices` (once empty of snapshots), and remove the folders.

## 4. The phone's account (D-30)

### 4.1 Account

In the OMV interface, as for the laptop (phase3-changes.md, section 4.1): **Users > Users > Create**: `<PHONE-USER>`, shell `/bin/sh`, groups `users` and `_ssh`, no `sudo`, a long random password that is not stored anywhere. Save and apply. Check:
```
getent group sudo _ssh
id <PHONE-USER>
```
The shell must be a real shell, as SSH runs the forced `rrsync` command through it.

### 4.2 Device folders

```
sudo install -d -m 700 -o <PHONE-USER> -g users <SSD-MOUNT>/devices/<DEVICE>
sudo install -d -m 700 -o <PHONE-USER> -g users <SSD-MOUNT>/devices/<DEVICE>/photos
sudo install -d -m 700 -o <PHONE-USER> -g users <SSD-MOUNT>/devices/<DEVICE>/files
sudo ls -ld <SSD-MOUNT>/devices/<DEVICE> <SSD-MOUNT>/devices/<DEVICE>/*
```
All three must show `drwx------ <PHONE-USER> users`. `<DEVICE-PATH>` below is `<SSD-MOUNT>/devices/<DEVICE>`.

Rollback: delete the folders, then the account in OMV.

## 5. Termux on the phone (D-30)

1. Install **Termux** and **Termux:API** from F-Droid. Both must come from F-Droid, as they are signed with the same key. The Google Play versions do not work with the F-Droid ones
2. Settings, Apps, Termux, Battery: **Unrestricted**. The same for Termux:API. Otherwise Android may stop the daily job
3. In Termux:
   ```
   pkg update && pkg upgrade
   pkg install openssh rsync termux-api
   termux-setup-storage
   ```
   Allow access when Android asks. On Android 16 this is "All files access", needed to read `Android/media` for WhatsApp. `~/storage/shared` then points to the phone's shared storage
4. Root check (plan 2.5.1): type `su`. `No su program found` means no root

## 6. Keys (D-30)

### 6.1 Make the keys, in Termux

```
ssh-keygen -t ed25519 -N "" -C phone-photos -f ~/.ssh/nas-photos
ssh-keygen -t ed25519 -N "" -C phone-files  -f ~/.ssh/nas-files
```
No passphrase, as the job runs unattended. The private keys stay in Termux's own storage, which other apps cannot read.

`~/.ssh/config` in Termux (`nano ~/.ssh/config`; `pkg install nano` if needed):
```
Host nas-photos
    HostName <NAS-TS-IP>
    User <PHONE-USER>
    IdentityFile ~/.ssh/nas-photos
    IdentitiesOnly yes
    ServerAliveInterval 30
Host nas-files
    HostName <NAS-TS-IP>
    User <PHONE-USER>
    IdentityFile ~/.ssh/nas-files
    IdentitiesOnly yes
    ServerAliveInterval 30
```
The address is used instead of the name `nas`, because Termux does not use Tailscale's DNS. `<NAS-TS-IP>` is the address `tailscale status` shows for the NAS.

### 6.2 Send the public keys to the NAS

The two `.pub` files go from the phone to the laptop with Tailscale's file sharing (Taildrop), then to the NAS as files, so nothing is retyped or wrapped (the problem met in phase3-changes.md section 5):

1. In Termux: `cp ~/.ssh/nas-photos.pub ~/.ssh/nas-files.pub ~/storage/shared/Download/`
2. In the phone's Files app, select both, Share, **Tailscale**, the laptop
3. On the laptop: `tailscale file get ~/Downloads/` (with `sudo` if it asks for permission) then `scp ~/Downloads/nas-photos.pub ~/Downloads/nas-files.pub nas:/tmp/` (as `<ADMIN-USER>`)
4. Delete the copies from the phone's `Download` folder and the laptop's `Downloads`. They are public keys, so this is tidiness, not secrecy

### 6.3 The key lines, on the NAS

As `<ADMIN-USER>`, using the `rrsync` options section 2 confirmed:
```
sudo install -d -m 700 -o <PHONE-USER> -g users /home/<PHONE-USER>/.ssh
{
  printf 'restrict,from="<PHONE-TS-IP>",command="/usr/bin/rrsync -wo -no-del -no-overwrite <DEVICE-PATH>/photos" %s\n' "$(cat /tmp/nas-photos.pub)"
  printf 'restrict,from="<PHONE-TS-IP>",command="/usr/bin/rrsync -wo -no-del <DEVICE-PATH>/files" %s\n' "$(cat /tmp/nas-files.pub)"
} | sudo tee -a /home/<PHONE-USER>/.ssh/authorized_keys >/dev/null
sudo chown <PHONE-USER>:users /home/<PHONE-USER>/.ssh/authorized_keys
sudo chmod 600 /home/<PHONE-USER>/.ssh/authorized_keys
sudo ssh-keygen -lf /home/<PHONE-USER>/.ssh/authorized_keys
rm /tmp/nas-photos.pub /tmp/nas-files.pub
```
`ssh-keygen -lf` must list two keys, `phone-photos` and `phone-files`. If the home folder does not exist, OMV makes it when the account is saved with a home folder; check with `ls -ld /home/<PHONE-USER>`.

### 6.4 First connection and host key, in Termux

Check the NAS's host key fingerprint first, from the administration session: `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`. Then in Termux:
```
rsync --version >/dev/null && echo test > ~/rsync-test.txt
rsync -t ~/rsync-test.txt nas-files:
```
Termux asks to trust the host key. Accept only if the fingerprint matches the one from the NAS. The file should appear as `<DEVICE-PATH>/files/rsync-test.txt`. Then `rm ~/rsync-test.txt` in Termux, and remove the test file on the NAS.

Rollback: delete the two lines from `authorized_keys`, and the keys in Termux.

## 7. Sync script, in Termux (D-29, D-31)

`~/bin/nas-backup` (`mkdir -p ~/bin`, then `nano ~/bin/nas-backup`):
```
#!/data/data/com.termux/files/usr/bin/sh
# Daily phone backup to the NAS (D-29 to D-31). Run by termux-job-scheduler on Wi-Fi and charging.
set -uf   # -f: no wildcard expansion, so the exclude patterns reach rsync unchanged
S=/storage/emulated/0
log=$HOME/nas-backup.log
ex="--exclude=.thumbnails/ --exclude=.trashed-* --exclude=.pending-*"
echo "== $(date '+%F %T')" >> "$log"

# Photos: new files only, never overwritten (D-30)
rsync -rt --ignore-existing $ex "$S/DCIM" "$S/Pictures" nas-photos: >> "$log" 2>&1 \
  || { echo "photos failed" >> "$log"; exit 1; }

# Files: everything else in shared storage, without the photo folders and Android
rsync -rt $ex --exclude=/DCIM/ --exclude=/Pictures/ --exclude=/Android/ \
  "$S/" nas-files:shared/ >> "$log" 2>&1 || echo "files failed" >> "$log"

# WhatsApp's local backup and received media (D-29)
w="$S/Android/media/com.whatsapp/WhatsApp"
[ -d "$w" ] && { rsync -rt $ex "$w/" nas-files:whatsapp/ >> "$log" 2>&1 || echo "whatsapp failed" >> "$log"; }

# List of installed apps, for reinstalling (D-29). Falls back to the laptop if Android blocks it
mkdir -p "$HOME/apps"
if pm list packages -3 --show-versioncode 2>/dev/null | sort > "$HOME/apps/app-list.txt" && [ -s "$HOME/apps/app-list.txt" ]; then
  rsync -t "$HOME/apps/app-list.txt" nas-files:apps/ >> "$log" 2>&1
else
  echo "app list blocked, use the laptop (section 10.2)" >> "$log"
fi
echo "done $(date '+%T')" >> "$log"
```
Then:
```
chmod 700 ~/bin/nas-backup
~/bin/nas-backup; tail -20 ~/nas-backup.log
```
The first run copies everything and can take a long time over Tailscale, so run it on home Wi-Fi with the phone charging. There is no `--delete` anywhere, and the keys would refuse it anyway.

## 8. Schedule, in Termux (D-31)

```
termux-job-scheduler --job-id 1 --script ~/bin/nas-backup \
  --period-ms 86400000 --network unmetered --charging true --persisted true
termux-job-scheduler --pending
```
`--network unmetered` means Wi-Fi only, `--charging true` while charging only, and `--persisted true` keeps the job after a restart. Android runs it once a day when both are true, not at a fixed time. `--pending` lists the job.

Rollback: `termux-job-scheduler --cancel --job-id 1`.

## 9. Daily snapshots, on the NAS (D-31, SR-33)

`/usr/local/sbin/devices-snapshot`, owned by root, mode 755:
```
#!/bin/sh
# Daily read-only snapshot of the device backups, kept 14 days (D-31)
set -eu
m=<SSD-MOUNT>
src=$m/devices
dst=$m/snapshots/devices
mountpoint -q "$m" || { echo "SSD not mounted, no snapshot"; exit 1; }
today=$(date +%F)
[ -e "$dst/$today" ] || btrfs subvolume snapshot -r "$src" "$dst/$today"
ls -1d "$dst"/20??-??-?? | head -n -14 | while read -r s; do btrfs subvolume delete "$s"; done
```
`/etc/systemd/system/devices-snapshot.service`:
```
[Unit]
Description=Snapshot of the device backups (D-31)

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/devices-snapshot
```
`/etc/systemd/system/devices-snapshot.timer`:
```
[Unit]
Description=Daily snapshot of the device backups

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```
```
sudo systemctl daemon-reload
sudo systemctl start devices-snapshot.service
sudo systemctl enable --now devices-snapshot.timer
sudo btrfs subvolume list -s <SSD-MOUNT> | tail -3
systemctl list-timers devices-snapshot.timer --no-pager
```
The snapshot list shows today's date. If the SSD is locked, the service fails with "SSD not mounted", which the missed-backup check will report.

To recover a file: `sudo cp -a <SSD-MOUNT>/snapshots/devices/<DATE>/<DEVICE>/files/<PATH> /tmp/` and copy it back as in section 10.3.

Rollback: `sudo systemctl disable --now devices-snapshot.timer`, delete the unit files and the script. Snapshots are removed with `btrfs subvolume delete`.

## 10. WhatsApp, the app list and restores (D-29, D-31)

### 10.1 WhatsApp

1. WhatsApp, Settings, Chats, Chat backup: turn on **End-to-end encrypted backup**, choose **64-digit encryption key**, and save the key in Proton Pass
2. With no Google account linked, set "Back up to Google Account" to **Never**. WhatsApp still writes its local backup every night at about 2 am
3. Check in Termux, the next day: `ls -l ~/storage/shared/Android/media/com.whatsapp/WhatsApp/Databases/ | tail -3`. A `msgstore.db.crypt15` file with today's date confirms it (V-50)

### 10.2 App list and settings from the laptop, if needed

Only if the log says "app list blocked", and for the settings values now and then. On the phone, turn on USB debugging for a few minutes (Settings, System, Developer options), plug into the laptop and accept the prompt. On the laptop (`sudo apt install adb` once, a separate approved change on the laptop):
```
d=~/phone-records; mkdir -p "$d"
adb shell pm list packages -3 --show-versioncode | sort > "$d/app-list.txt"
for n in system secure global; do adb shell settings list $n > "$d/settings-$n.txt"; done
adb kill-server
```
`~/phone-records` is in the laptop's home folder, so the next laptop backup carries it to the NAS, encrypted. Turn USB debugging off again afterwards.

### 10.3 Restores

As the phone's keys are write only, restores go from the NAS through the laptop: copy from `<DEVICE-PATH>` (or a snapshot) to the laptop as `<ADMIN-USER>` with `scp`, then to the phone over USB. WhatsApp on a new phone: copy `msgstore.db.crypt15` into the same `Databases` folder before opening WhatsApp, then restore with the 64-digit key.

## 11. Tests

Document 05, section 4.5: V-45 to V-50, then the repeats of V-01, V-04, V-09 and V-12 (Claude Code, when approved).

## 12. Commands from the laptop (D-32)

An SSH server in Termux, started only when a session needs it, so the laptop's Claude Code session can run approved commands on the phone.

1. On the laptop: a key used only for the phone, `~/.ssh/phone-claude` (`ed25519`), and an SSH entry `phone-claude` with `HostName <PHONE-TS-IP>`, `Port 8022`, that key, `IdentitiesOnly yes` and `BatchMode yes`
2. On the phone, once: a set-up script that writes `$PREFIX/etc/ssh/sshd_config` (keeping `sshd_config.orig`):
   ```
   Port 8022
   ListenAddress <PHONE-TS-IP>
   PubkeyAuthentication yes
   PasswordAuthentication no
   KbdInteractiveAuthentication no
   AllowAgentForwarding no
   AllowTcpForwarding no
   X11Forwarding no
   PermitTunnel no
   PrintMotd no
   ```
   and adds `from="<LAPTOP-TS-IP>",no-agent-forwarding,no-port-forwarding,no-X11-forwarding <LAPTOP-PHONE-KEY>` to Termux's `~/.ssh/authorized_keys`, then runs `sshd -t` and prints the phone's host key fingerprint
3. Tailscale policy, a grant next to the NAS rule (D-14 change):
   ```
   {"src": ["<LAPTOP-TS-IP>"], "dst": ["<PHONE-TS-IP>"], "ip": ["tcp:8022"]}
   ```
4. First connection: compare the host key fingerprint with the one the phone printed before trusting it
5. Each use: in Termux, `termux-wake-lock` then `sshd`. Afterwards `pkill -x sshd` then `termux-wake-unlock`, and check from the laptop that 8022 no longer answers
6. After changing `sshd_config`, restart `sshd`: a running `sshd` keeps its old settings (found by V-51). `ssh -v` with key login turned off should list only `publickey`

Rollback: `pkill -x sshd`, remove the key line from Termux's `authorized_keys`, copy `sshd_config.orig` back, remove the grant, and delete the laptop key and SSH entry.

## 13. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.1 | 15th November 2026 | Steps drafted: NAS checks, snapshot volume and folders, the phone's account, Termux, the two `rrsync` keys sent with Taildrop, the sync script, the schedule, daily snapshots, WhatsApp's encrypted local backup, the app list and restores. Not yet reviewed (drafted with AI assistance) | Phone plan accepted |
| 0.2 | 16th November 2026 | Section 1: root check, Google's backup off, Tailscale and SSD ticked. Sections 2 to 9 done, logged in document 05, section 7 | Phone steps carried out |
| 0.3 | 17th November 2026 | Section 12 added: the on-demand SSH server for commands from the laptop (D-32), with the restart lesson from V-51. Revision log moved to section 13 (drafted with AI assistance) | D-32 accepted |
| 0.31 | 17th November 2026 | Phone make and model removed before publishing, Android version kept | Owner decision |
