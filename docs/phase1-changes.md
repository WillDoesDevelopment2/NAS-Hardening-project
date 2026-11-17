# Phase 1 Change Steps

> **Status:** Draft v0.11 · Last updated: 6th November 2026
> **Author:** William Drummond
> **Related:** [phase1-checklist.md](phase1-checklist.md) (sections 4 to 8) · [04-design-decisions.md](04-design-decisions.md) (D-03 to D-10, D-12, D-13, D-14) · [02-threat-analysis.md](02-threat-analysis.md) (section 7) · [05-verification.md](05-verification.md) (section 4.2 tests, section 7 log)
> **Note:** Drafted with AI assistance on 2nd November 2026, for OMV 8 on Debian 13 (the versions seen in V-03). Nothing here has been run. Menu names in the OMV interface can differ slightly between versions, so check each label before changing it. Placeholders such as `<NAS-IP>` stay as placeholders in this file. Every change is logged in document 05, section 7 (Phase 1 log), with the time in UK time.

---

## 1. Before starting

- Phase 1 checklist, section 1 complete, including the new SD card image
- Keep one SSH session open as your current account for the whole of section 2. Test every change from a **second** session. Do not close the first session until the second one works
- Check that a recovery path works: the direct Ethernet link to the laptop, or a keyboard and screen on the NAS
- **Make SSH, account and group changes in the OMV interface, not by editing files.** OMV rewrites `/etc/ssh/sshd_config` and the group lists from its own database whenever settings are applied, so hand edits are lost or cause conflicts. Changes outside OMV's control (fail2ban, systemd-resolved, rpcbind, Bluetooth) are made on the command line

## 2. Accounts and SSH (checklist section 4)

### 2.1 Administration account (SR-03)

Done on 4th November 2026. The steps below are what was done: the account made at installation became the administration account, and a new account was made for daily use. This replaces the first draft, which created a new administration account.

1. On the laptop, create a key for the administration account:
   ```
   ssh-keygen -t ed25519 -f ~/.ssh/nas_admin_ed25519 -C nas-admin
   ```
   Give it a passphrase, and keep the passphrase in the password manager.
2. In OMV, **Users > Users**, edit the installation account (`<ADMIN-USER>`): groups `_ssh` and `sudo`, shell `/bin/bash`.
3. Under **Public keys**, add the public key on one line. OMV refuses a key that ends with a line break, so copy it with `tr -d '\n' < ~/.ssh/nas_admin_ed25519.pub` and paste that. Save and apply.
4. From a second terminal on the laptop:
   ```
   ssh -i ~/.ssh/nas_admin_ed25519 -o IdentitiesOnly=yes <ADMIN-USER>@<NAS-IP>
   sudo -v && sudo -l
   ```
   Key login works, and `sudo -l` shows `(ALL : ALL) ALL`. **Stop here if either fails.**

The OMV web interface has its own built-in administrator, `admin`, which is not shown in the user list. It only gets into the web interface and has no shell (V-13).

### 2.2 Daily account (SR-03)

1. In OMV, **Users > Users > Create**: `<DAILY-USER>`, a strong unique password, default group `users` only (no `sudo`, no `_ssh`), shell `/usr/sbin/nologin`. It is for file shares (section 8). Save and apply.
2. Check from the administration session:
   ```
   getent group sudo _ssh
   ```
   `sudo` lists only `<ADMIN-USER>`. `_ssh` lists `<ADMIN-USER>` and the Claude Code account.

### 2.3 SSH settings (SR-04, SR-05)

1. In OMV, **Services > SSH**: untick **Permit root login**, untick **Password authentication**, leave **Public key authentication** ticked. Save and apply.
2. From a new terminal, check that key login still works for `<ADMIN-USER>`, and that password login is refused:
   ```
   ssh -o PubkeyAuthentication=no -o PreferredAuthentications=password <ADMIN-USER>@<NAS-IP>
   ```
   Expected: `Permission denied (publickey)`.
3. Check the running configuration:
   ```
   sudo sshd -T | grep -E '^(permitrootlogin|passwordauthentication|kbdinteractiveauthentication|pubkeyauthentication) '
   ```
   Expected: `permitrootlogin no`, `passwordauthentication no`, `kbdinteractiveauthentication no`, `pubkeyauthentication yes`.

The Claude Code key (D-02) is in the account's own `authorized_keys` file, so it keeps working. Claude Code can then run V-09 and V-12.

### 2.4 Failed login limit with fail2ban (SR-06, D-07)

fail2ban is a Debian package. SR-15 check: it runs as root, reads the system log and adds firewall rules, and does not listen on the network.

1. Install it:
   ```
   sudo apt update
   sudo apt install fail2ban python3-systemd
   command -v nft
   ```
2. Create `/etc/fail2ban/jail.d/sshd-local.conf`:
   ```
   [sshd]
   enabled  = true
   backend  = systemd
   mode     = aggressive
   maxretry = 5
   findtime = 10m
   bantime  = 1h
   ```
   If `command -v nft` printed a path, also add `banaction = nftables-multiport`. `mode = aggressive` also counts the failures from key-only logins, which the normal mode can miss once password login is off.
3. Restart and check:
   ```
   sudo systemctl restart fail2ban
   sudo systemctl is-enabled fail2ban
   sudo fail2ban-client status sshd
   ```
   Expected: `enabled`, and the `sshd` jail listed with 0 banned.
4. Run V-16 from a second LAN device (not the laptop). To unblock early: `sudo fail2ban-client set sshd unbanip <DEVICE-IP>`.

### 2.5 Default password check (SR-01)

Run V-13 again in the OMV interface.

## 3. Services and admin interface (checklist section 6)

### 3.1 rpcbind off (D-13)

NFS is off in OMV (D-05), so nothing needs rpcbind.
```
sudo systemctl disable --now rpcbind.service rpcbind.socket
sudo systemctl mask rpcbind.service rpcbind.socket
```
If applying settings in OMV later gives an error that mentions rpcbind, unmask it and log the problem.

### 3.2 LLMNR off (D-13)

LLMNR comes from systemd-resolved. Create `/etc/systemd/resolved.conf.d/no-llmnr.conf`:
```
[Resolve]
LLMNR=no
```
Then `sudo systemctl restart systemd-resolved`. The global setting overrides any per-connection setting in NetworkManager. OMV already turns off mDNS in systemd-resolved with its own file in the same folder, as Avahi handles mDNS.

### 3.3 mDNS off (D-13)

mDNS comes from Avahi, which OMV manages. OMV stops and restarts Avahi itself whenever related settings are applied, so stopping it with `systemctl` alone would not last. OMV's own switch is the `OMV_ZEROCONF_ENABLED` setting (checked in OMV's Avahi rules on 4th November 2026):
```
echo 'OMV_ZEROCONF_ENABLED="no"' | sudo tee -a /etc/default/openmediavault
sudo omv-salt stage run prepare
sudo omv-salt deploy run avahi
systemctl is-active avahi-daemon.service avahi-daemon.socket
```
Expected: `inactive` twice. Turn it back on by changing the setting to `yes` and running the last two `omv-salt` commands, if Apple devices cannot find the NAS and that matters (D-13).

### 3.4 Bluetooth off, and Ethernet or Wi-Fi (D-10)

1. Bluetooth:
   ```
   sudo systemctl disable --now bluetooth.service
   sudo systemctl disable --now hciuart.service 2>/dev/null
   ```
   Then add `dtoverlay=disable-bt` on its own line at the end of `/boot/firmware/config.txt`. It takes effect at the next reboot.
2. If a cable reaches the router: connect it, check it gets an address with `ip -br addr`, and connect over SSH to the new address **before** turning off Wi-Fi. Then add `dtoverlay=disable-wifi` to `/boot/firmware/config.txt` and reboot. The NAS address changes, so update `<NAS-IP>` in the laptop's SSH configuration and in the sanitise map. The Claude Code key limits the laptop's address, not the NAS's, so it still works.
3. If no cable reaches: leave Wi-Fi on. Bluetooth off is enough.

### 3.5 HTTPS for the admin interface (SR-02, D-04)

1. In OMV, **System > Certificates > SSL > Create**: a self-signed certificate, common name the NAS's name.
2. **System > Workbench**: enable SSL/TLS with that certificate on port 443, and tick **Force SSL/TLS** so port 80 only redirects. Save and apply. Reload the page on `https://<NAS-IP>`.
3. Record the certificate fingerprint once, from the laptop:
   ```
   openssl s_client -connect <NAS-IP>:443 </dev/null 2>/dev/null | openssl x509 -noout -fingerprint -sha256
   ```
   Compare it with the certificate details in OMV. Accept the browser warning only if they match. Keep the fingerprint in the raw evidence, not in the repository.
4. The NAS's interfaces are the LAN, Tailscale and the direct troubleshooting link, and the router blocks inbound connections (V-08), so this meets the access limit in SR-02. A host firewall that also blocks other sources is **optional**, as the router already does this.

### 3.6 After section 3

Claude Code re-runs V-01, V-03 and V-04, you run V-02 and V-21, then Claude Code drafts the update to the service inventory in document 01, section 6.3.

## 4. Updates and monitoring (checklist section 7)

### 4.1 Pending updates (FND-06)

The Phase 1 SD card image counts as the image before a major upgrade (D-08), if nothing else has changed since it was taken.
```
sudo omv-upgrade
```
Reboot if a new kernel was installed. Then Claude Code runs V-10.

### 4.2 Automatic security updates (SR-10, D-08)

Check the current settings:
```
cat /etc/apt/apt.conf.d/20auto-upgrades
grep -rn 'Origins-Pattern\|Unattended-Upgrade' /etc/apt/apt.conf.d/
systemctl list-timers --no-pager 'apt-daily*'
sudo unattended-upgrade --dry-run --debug 2>&1 | tail -30
```
OMV keeps these settings in its own files (`95openmediavault-unattended-upgrade` and others), not in `50unattended-upgrades`, and the last file to set a value wins. Expected: `Update-Package-Lists "1"` and `Unattended-Upgrade "1"` in effect, allowed origins limited to `Debian-Security` (also shown in `/var/log/unattended-upgrades/unattended-upgrades.log`), both timers listed, and the dry run reports allowed origins without errors. Updates from the openmediavault and Raspberry Pi repositories are not included, as D-08 intends.

### 4.3 Update routine (SR-10, D-08)

Every 7 days, so nothing waits more than 14:

1. `sudo apt update && apt list --upgradable`
2. If openmediavault or the kernel has a new major version, take an SD card image first
3. `sudo omv-upgrade`, then reboot if a new kernel was installed
4. Check that the OMV interface, SSH and shares work
5. Log the date and what was updated in document 05, section 7

### 4.4 SSD health warnings (SR-13, D-09)

1. Create an app password or a dedicated email account for the NAS to send from.
2. In OMV, **System > Notification > Settings**: SMTP server, port, encryption, sender, login and recipient. Save, apply, then **Send a test email** (V-17).
3. **System > Notification > Notifications**: tick S.M.A.R.T. and the other events you want.
4. **Storage > S.M.A.R.T. > Settings**: enable monitoring, and set the temperature limits a little below the SSD's own warning temperature (`Warning Comp. Temperature Threshold` in V-06). **Devices**: enable monitoring for the SSD.

### 4.5 Vulnerability monitoring account (SR-14, D-03)

1. In OMV, create `<MONITOR-USER>`: shell `/bin/bash`, groups `users` and `_ssh`, no sudo, a long random password that is not stored anywhere. Click **Apply**, then check with `getent group _ssh`.
2. Follow `scripts/vuln-dashboard/README.md`, step 1, to add the restricted key to that account. The key is limited to the laptop's Tailscale address (D-03).
3. Enable the timer on the laptop as the README describes. V-18 checks two runs.

### 4.6 Safe shutdown routine (T-18, D-12)

1. Check nobody is copying files to the NAS
2. Shut down from the OMV interface (**Power > Shutdown**) or with `sudo shutdown -h now`
3. Wait until the green activity light has stopped for 10 seconds, then remove power
4. After power returns: check the OMV interface loads, unlock the SSD (once it is encrypted, D-06), and check the shares
5. After an unexpected power cut: also check the system log for file system errors (`sudo journalctl -b -p err`) and SMART (`sudo smartctl -a /dev/nvme0`)

V-27 tests this routine.

## 5. Tailscale (checklist section 5)

Done on 4th and 5th November 2026, and tested (V-19, V-20, V-22, V-26). Checked against the Tailscale documentation on 4th November 2026 (document 02, section 7.5). Device approval is used, not Tailnet Lock (D-14).

### 5.1 Account and identity provider (SR-19)

A tailnet cannot be created with a passkey: Tailscale only allows passkey users who are invited into an existing tailnet. So:

1. Identity provider for the tailnet owner: GitHub (owner, 4th November 2026). The options were Apple, Google, GitHub and Microsoft. Use an account protected by a passkey or an authenticator app. Both can be kept in Proton Pass. A separate account just for this, made with a Proton email alias, keeps it apart from anything else. Record which provider and which second factor in V-19, not the account name
2. Sign up at tailscale.com with that provider. Give the tailnet no personal names
3. **Settings > Device management**: turn on **Device approval** (D-14). Leave key expiry at 180 days
4. Invite a backup admin who signs in with a passkey: **Users > Invite users**, role **Admin**. Open the invite in a private browser window, choose **Sign in with a passkey**, a neutral username, and save the passkey in Proton Pass. This is the way back in if the identity provider ever blocks the main login. The backup admin gets no access to the NAS in the access rules (5.3), and it is used for V-22
5. Do not turn on Tailscale SSH, Funnel, exit nodes or subnet routing (D-14, document 02, section 7.3)

### 5.2 Check before installing (SR-15)

Drafted with AI assistance, accepted by the owner on 4th November 2026:

| Question | Answer |
|---|---|
| Where it comes from | Tailscale's own package source for Debian 13 (`pkgs.tailscale.com`), signed with Tailscale's key. Not from Debian |
| Privileges | The `tailscaled` service runs as root. It creates the `tailscale0` network interface and adds routing and firewall rules for it |
| Network exposure | Listens on UDP 41641 by default, on all interfaces, for WireGuard. Connects out to Tailscale's coordination, relay and logging servers |
| Data sent to Tailscale | Device details, public keys, and logs with connection events unless logging is turned off (5.4, step 2) |
| Updates | Not covered by the automatic Debian security updates (D-08). Updated with everything else in the weekly routine (section 4.3), as it is a normal package |
| Decision | Accepted (owner, 4th November 2026). Logging off on the NAS (5.4, step 2) |

### 5.3 Access rules (SR-19, T-08)

Before any device joins, replace the default policy in **Access controls** with:

```
{
  "tagOwners": {
    "tag:nas": ["autogroup:admin"]
  },
  "grants": [
    {
      "src": ["<OWNER-LOGIN>"],
      "dst": ["tag:nas"],
      "ip":  ["tcp:22", "tcp:443"]
    }
  ]
}
```

`<OWNER-LOGIN>` is the tailnet owner's login as shown on the **Users** page. This lets only your own devices reach the NAS, and only for SSH and the admin interface. Nothing else is allowed: devices cannot reach each other, and the backup admin cannot reach the NAS. SMB (TCP 445) is added in section 8 when the shares are made (D-05). Tagging the NAS turns off its key expiry, so a headless NAS does not drop off every 180 days. Client devices keep their 180-day expiry.

### 5.4 Install on the NAS

As the administration account:

1. Add the package source and install:
   ```
   sudo mkdir -p --mode=0755 /usr/share/keyrings
   curl -fsSL https://pkgs.tailscale.com/stable/debian/trixie.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
   curl -fsSL https://pkgs.tailscale.com/stable/debian/trixie.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list
   sudo apt-get update && sudo apt-get install tailscale
   ```
2. Logging: to stop the NAS sending logs to Tailscale, add `TS_NO_LOGS_NO_SUPPORT=true` to `/etc/default/tailscaled` and run `sudo systemctl restart tailscaled`. Tailscale may then not be able to help with support problems (document 02, section 7.2). Chosen: logging off (owner, 4th November 2026)
3. Join with a neutral name and the NAS tag:
   ```
   sudo tailscale up --hostname=nas --advertise-tags=tag:nas
   ```
   Open the link it prints, sign in as the tailnet owner, then approve the NAS in **Machines**
4. Check: `tailscale status` lists the NAS, and the admin console shows it tagged `tag:nas` with key expiry off

### 5.5 Client devices (T-08, SR-18)

1. Install Tailscale on the laptop and the phone, and sign in as the tailnet owner
2. Approve each one in **Machines**, after checking it is the device you expect. Give each a neutral name
3. Keep a list of approved devices in document 05 (V-19): device type and approval date, no names or addresses
4. On the laptop, check `ssh -i ~/.ssh/nas_admin_ed25519 -o IdentitiesOnly=yes <ADMIN-USER>@nas` and `https://nas` work over Tailscale (V-20). The Claude Code key only allows the laptop's LAN address (D-02), so Claude Code does not use Tailscale

### 5.6 Removing a device (T-08, SR-18)

1. In the admin console, **Machines**, open the device's menu and choose **Remove**. It loses access to the tailnet straight away
2. If the device was lost or stolen, also sign out of the identity provider on it, and change any passwords stored on it
3. If the admin console cannot be reached, cut all Tailscale access on the NAS: `sudo tailscale down`. LAN access still works
4. Log the removal in document 05, section 7

V-26 tests this: remove a device, check within 5 minutes that it cannot reach the NAS, then add it back and approve it again.

### 5.7 After section 5

Run V-19 (owner, in the browser), V-20, V-22 (from a device signed in as the backup admin) and V-26. Claude Code re-runs V-04 to check that only `tailscaled` is new.

## 6. Storage and shares (checklist section 8)

In progress: 6.3, 6.5, 6.6 and 6.7 done on 5th November 2026. 6.4 and the re-tests in 6.8 wait until the owner is at home. Do this before any data is stored on the NAS. Drafted with AI assistance on 5th November 2026. Menu names are from the plugin and OMV documentation and may differ slightly. Everything here can be done over Tailscale, but keep a recovery path for the reboot in 6.4 (section 1).

### 6.1 Choices to make first

| Choice | Options | Chosen (owner, 5th November 2026, D-15) |
|---|---|---|
| File system on the encrypted SSD | ext4: simple, OMV's usual choice. Btrfs: also supports snapshots of shared folders in OMV, which can undo deletions or ransomware damage (input for Phase 3) | Btrfs, as there is no data yet and changing later means moving everything |
| SMB encryption | Required: file contents are encrypted on the Wi-Fi, needs SMB 3 clients (all current systems). Off: only the login is protected | Required |
| Shares | Which folders, and which accounts need each one | One share for photos and other media, for `<DAILY-USER>` only, so photos can move off Google Drive. Others when a use appears |

### 6.2 Check before installing (SR-15)

| Question | Answer |
|---|---|
| What | `openmediavault-luksencryption`, the LUKS plugin for OMV 8 (version 8.1.x, October 2026) |
| Where it comes from | The omv-extras package source, already set up on the NAS (it appears in the V-10 package lists). Maintained by the OMV plugin developers on GitHub |
| What it installs | `cryptsetup`, `cryptsetup-bin`, `systemd-cryptsetup` and `busybox`, all from Debian |
| Privileges | Runs through OMV's own engine as root, as OMV does for all storage changes |
| Network exposure | None. It opens no port. Its optional automatic unlock with a Tang server or TPM2 would add a dependency, and is not used (D-06) |
| Decision | Accepted (owner, 5th November 2026) |

### 6.3 Encrypt the SSD (SR-12, D-06)

1. In OMV, **System > Plugins**: install `openmediavault-luksencryption`. A new **Storage > Encryption** page appears
2. Create a passphrase of at least 6 random words in Proton Pass, saved there. Without it the data cannot be read, and there is no recovery
3. **Storage > Encryption > Create**: device the SSD (`/dev/nvme0n1`), the default cipher, a neutral label, and the passphrase. Leave automatic unlock off. Apply
4. **Unlock** the new device with the passphrase
5. **Header backup:** use the page's header backup option and keep the file in Proton Drive or on the laptop outside the repository. If the start of the SSD is damaged, the header is needed together with the passphrase
6. **Storage > File Systems > Create**: the chosen file system (6.1) on the unlocked device (`/dev/mapper/...`). For Btrfs, choose the **Single** profile: the others need two or more devices, and DUP stores everything twice on the one SSD. Then **mount** it and Apply. Check it shows as mounted before going on

### 6.4 Test a reboot and unlock (SR-12, V-14)

1. Reboot from OMV or with `sudo reboot`
2. After the reboot, check **Storage > Encryption**: the device shows as locked, and the file system as missing or not mounted. Shares are unavailable
3. Unlock it with the passphrase, then check the file system mounts again (mount it in **Storage > File Systems** if it does not)
4. Log both steps. Claude Code then runs `lsblk -f` for V-14 when approved

While the SSD is locked, the start waits 90 seconds for the Btrfs file system and then carries on. monit reports the file system as not mounted until it is unlocked. Both are expected. Done on 6th November 2026 together with V-27.

### 6.5 SMB settings (SR-11, D-05)

**Services > SMB/CIFS > Settings**:
- **Enabled**, minimum protocol **SMB3**
- **Home directories** off
- Under extra options, if chosen in 6.1: `server smb encrypt = required`
- Leave NetBIOS and WINS off if the page shows them

### 6.6 Shares (SR-11)

1. **Storage > Shared Folders > Create**: a neutral name for the media share, the encrypted file system, default path. Apply
2. Select it, **Permissions**: `<DAILY-USER>` read and write. Every other account no access. Leave the "others" permission as no access
3. **Services > SMB/CIFS > Shares > Create**: that shared folder, **Public** set to **No** (no guest), browseable on. Apply. This is a separate step from creating the shared folder: without it, SMB runs but shares nothing
4. Test from the laptop or phone as `<DAILY-USER>`: the share opens with that account, and a connection without an account is refused

### 6.7 Tailscale access to SMB

Add `"tcp:445"` to the `ip` list of the grant in the Tailscale access rules (5.3), so shares work away from home. Nothing else changes.

### 6.8 After section 6

Claude Code re-runs V-04 (does SMB now listen, and does anything else start with it, such as `nmbd` or `wsdd2`) and V-14. The owner checks V-11 in OMV. Claude Code updates the SMB row of the service inventory in document 01, section 6.3.

Done on 6th November 2026: V-04 found smbd also on 139 and WS-Discovery started with SMB (FND-11). Fixed in 6.9.

### 6.9 Close FND-11 (SR-07)

1. **Services > SMB/CIFS > Settings**: add `smb ports = 445` in the main **Extra options** box, on a new line under `server smb encrypt = required`. Not the Extra options box under **Home directories**: home directories are off, so OMV never writes that box to Samba. Save, then Apply in the yellow banner. Check it reached Samba with `grep -i "smb ports" /etc/samba/smb.conf`
2. As the administration account, check the setting is not already there, then add it:
   ```
   grep WSDD /etc/default/openmediavault
   echo 'OMV_WSDD_ENABLED="0"' | sudo tee -a /etc/default/openmediavault
   ```
   OMV's Samba setup starts `wsdd-server` unless this is `0` (`srv/salt/omv/deploy/samba/default.sls` in the OMV source). There is no switch in the interface
3. Load it the way the OMV documentation gives for these settings, and check it reached OMV's settings before deploying. If the `grep` prints nothing, any Samba deploy, including Apply in the interface, starts `wsdd-server` again:
   ```
   sudo monit restart omv-engined
   sudo omv-salt stage run prepare
   sudo grep -i wsdd /srv/pillar/omv/default.sls
   ```
4. Deploy Samba, then stop the service, as OMV no longer starts it but does not stop it either:
   ```
   sudo omv-salt deploy run samba
   sudo systemctl disable --now wsdd-server
   ```
5. Check `smb://nas/media` still opens. No Windows device is used on this network today. If one is added, it will not list the NAS under Network, but can connect with `\\nas\media`
6. Claude Code re-runs V-04 when approved: smbd on 445 only, nothing on 3702 or 5357

Done on 6th November 2026, after two corrections: the first `smb ports` line went into the Home directories box, and the first Samba deploy ran before the setting reached OMV's settings, so it started `wsdd-server` again. V-04 then found smbd on 445 only and WS-Discovery stopped and disabled.

## 7. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.1 | 2nd November 2026 | Steps drafted for checklist sections 4, 6 and 7, not yet reviewed (drafted with AI assistance) | Owner request to prepare the Phase 1 changes |
| 0.2 | 4th November 2026 | Section 3: mDNS uses OMV's own Zeroconf setting, LLMNR file no longer repeats OMV's mDNS setting, after checking OMV's rules on the NAS (drafted with AI assistance) | Before section 6 changes |
| 0.3 | 4th November 2026 | Section 2: steps changed to what was done (installation account as administration account, new daily account, key without a line break). Section 5: Tailscale steps and SR-15 check added, checked against the Tailscale documentation (drafted with AI assistance) | Section 4 done, before the Tailscale set-up |
| 0.4 | 4th November 2026 | Section 5: GitHub as identity provider, SR-15 check accepted, logging off on the NAS | Owner decisions |
| 0.5 | 4th November 2026 | Section 5: progress noted | Steps 5.1, 5.3 and 5.4 done |
| 0.6 | 5th November 2026 | Section 5: marked done and tested | Section 5 complete |
| 0.7 | 5th November 2026 | Section 4.2: commands changed to find OMV's own unattended-upgrades files, `--no-pager` added | Checked on the NAS |
| 0.8 | 5th November 2026 | Section 4.5: shell, Apply step and Tailscale address added | Found during set-up |
| 0.9 | 5th November 2026 | Section 6: storage and share steps, choices and SR-15 check for the encryption plugin added (drafted with AI assistance) | Start of checklist section 8 |
| 0.10 | 6th November 2026 | Section 6.4: boot wait and monit messages noted, test done. Section 6.8 result. Section 6.9: steps to close FND-11 (drafted with AI assistance) | Re-tests after section 6 |
| 0.11 | 6th November 2026 | Section 6.9: which Extra options box to use, omv-engined restart and a check of OMV's settings before deploying, step reworded (no Windows device in use), result added | Found while closing FND-11 |
