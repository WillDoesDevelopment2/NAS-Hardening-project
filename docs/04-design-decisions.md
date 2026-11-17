# 04 – Design Decisions

> **Status:** Draft v0.37 · Last updated: 17th November 2026
> **Author:** William Drummond
> **Related:** [01-scope-and-assets.md](01-scope-and-assets.md) · [02-threat-analysis.md](02-threat-analysis.md) · [03-security-requirements.md](03-security-requirements.md) · [05-verification.md](05-verification.md)
> **Note:** Add one record per meaningful decision, written as it is made, not afterwards. Replace anything in **[TODO]** or square brackets. Record meaningful changes in the revision log at the end.

---

## 1. Purpose

This document records why each design choice was made: what the options were, what was chosen, what was given up, and which threat or requirement the decision serves. It lets a reader follow the reasoning behind the configuration, not just the configuration itself.

A decision belongs here if someone could reasonably have chosen differently (for example Tailscale or WireGuard, HTTPS or HTTP for admin access, whether to encrypt the SSD). Routine steps belong in the verification log.

## 2. Method note

Decisions follow the loop used across this project: threat, requirement, control, test, result. Where useful, decisions refer to ISO/IEC 27002:2022 control themes as a reference. The loop is comparable to the TARA activity in ISO/SAE 21434, which is an automotive standard, so the comparison is an analogy and not a method I follow. This is not a compliance claim.

## 3. Decision index

| ID | Decision | Status | Phase | Related threats |
|---|---|---|---|---|
| D-01 | Baseline definition for Phase 0 | Accepted | 0 | All |
| D-02 | Temporary SSH access for Claude Code | Accepted | 0, 1 | T-01, T-04, T-12 |
| D-03 | Vulnerability monitoring dashboard | Accepted | 1 | T-02, T-06, T-14 |
| D-04 | Admin interface access and HTTPS | Accepted | 1 | T-01, T-13 |
| D-05 | File sharing protocol | Accepted | 1 | T-12, T-13 |
| D-06 | Encryption at rest | Accepted | 1 | T-11 |
| D-07 | Limiting failed SSH logins | Accepted | 1 | T-04 |
| D-08 | Update routine | Accepted | 1 | T-02, T-14 |
| D-09 | SSD health warnings | Accepted | 1 | T-10, T-18 |
| D-10 | NAS network connection and radios | Accepted | 1 | T-07, T-13, T-18 |
| D-11 | Network isolation | Accepted | 1 | T-07 |
| D-12 | Power protection | Accepted | 1 | T-18 |
| D-13 | Network services not in the inventory | Accepted | 1 | T-02, T-13 |
| D-16 | WireGuard alongside Tailscale | Accepted | 2 | T-08, T-16, T-17 |
| D-17 | Where WireGuard runs and how it is installed | Accepted | 2 | T-06, T-17 |
| D-18 | What WireGuard peers can reach | Accepted | 2 | T-07, T-13 |
| D-19 | Port forward and changes of public address | Accepted | 2 | T-03, T-19 |
| D-20 | WireGuard key management | Accepted | 2 | T-08, T-17 |
| D-21 | Backup tool and transport | Accepted | 3 | T-05, T-08, T-09, T-10 |
| D-22 | What the laptop backs up | Accepted | 3 | T-08, T-09, T-15 |
| D-23 | Backup account, repository and key limits | Accepted | 3 | T-05, T-08, T-12 |
| D-24 | Backup encryption and key storage | Accepted | 3 | T-08, T-15 |
| D-25 | Backup schedule, retention and pruning | Accepted | 3 | T-05, T-09, T-15 |
| D-26 | Missed-backup warning | Accepted | 3 | T-20 |
| D-27 | Off-site copy of the backups | Accepted | 3 | T-10, T-11 |
| D-28 | SD card image taken remotely | Accepted | 3 | T-14, T-18 |
| D-29 | What the phone backs up | Accepted | 3 | T-08, T-09, T-10 |
| D-30 | Phone backup tool, account and key limits | Accepted | 3 | T-05, T-08, T-12 |
| D-31 | Phone backup schedule, encryption, deleted files and restores | Accepted | 3 | T-05, T-09, T-10, T-20 |
| D-32 | Commands on the phone from the laptop's Claude Code session | Accepted | 3 | T-07, T-08, T-13, T-16 |

Status values: **Proposed**, **Accepted**, **Superseded by D-xx**, **Rejected**.

## 4. Decision record format

Copy this block for each decision.

```
### D-xx – Short title

- **Date:** [date]
- **Status:** Proposed / Accepted / Superseded by D-xx
- **Related:** Threat IDs, requirement IDs, test IDs
- **Context:** What problem or question prompted this decision, and what constraints apply
- **Options considered:**
  1. Option A – advantages and disadvantages
  2. Option B – advantages and disadvantages
- **Decision:** What I chose
- **Reasoning:** Why, in terms of the threats, the design principles in document 01 and the constraints
- **Trade-offs and residual risk:** What this decision gives up or leaves open
- **Evidence:** The test or measurement that supports or checks this decision (link to 05-verification.md)
- **Review trigger:** What would make me revisit it
```

## 5. Decisions

### D-01 – Baseline definition for Phase 0

- **Date:** 27th October 2026
- **Status:** Accepted
- **Related:** All threats. Phase 0 tests in 05-verification.md
- **Context:** Phase 0 measures the system before any hardening. Later "before and after" claims only make sense if the baseline is defined precisely.
- **Options considered:**
  1. **The system exactly as it stands now.** Honest about the real starting point, but may include earlier experiments and changes that are not documented
  2. **A fresh default OMV install on a wiped SD card and SSD.** Reproducible and clean, but not the system I was actually running
  3. **The system as it stands now, with known earlier changes listed before testing.** Same starting point as option 1, but each change I remember making since installation is written down first, so findings can be traced to either a default or my own change. The list may still be incomplete
- **Decision:** Option 3. The baseline is the system as it stands before Phase 0, captured in the SD card image, with the known earlier changes listed below
- **Reasoning:** The project question concerns the system I actually run, so option 2 would measure a system that does not exist. Option 3 keeps the real starting point and makes the known history explicit, which supports principle 5 (verify, do not assume). The SD card image taken before Phase 0 lets the baseline be restored and repeated
- **Trade-offs and residual risk:** Results are not directly comparable with a default OMV install, and undocumented earlier changes may still affect results. Where a finding cannot be traced to a default or a listed change, record it as of unknown origin
- **Known earlier changes:**
  1. Raspberry Pi OS Lite (64-bit) written with Raspberry Pi Imager, with SSH enabled and Wi-Fi configured in the Imager settings
  2. OMV 8 installed with the install script's `-n` option, which skips OMV's network setup so the existing network configuration is kept
  3. One user account only, used for both administration and daily use
  4. Direct Ethernet connection set up between the laptop and the NAS. Kept for troubleshooting only and not normally connected. The NAS uses Wi-Fi for the home LAN
  5. No router changes. No fixed IP address
  6. ~~Case control software installed~~ Corrected on 29th October 2026: the case control software is not installed (owner confirmed during Phase 0, matching V-01 and V-04)
  7. SSH used for administration, with password login
  8. No updates installed since setup
- **Evidence:** Phase 0 results in 05-verification.md. SD card image taken 28th October 2026, 08:17 UK time, SHA-256 `090dcc27c844456240e0279f80bf0bb753c488bd6cf53fd605fb20f9ab3f741d`. The hash recorded during imaging, the hash of the decompressed image and the hash of the card itself all matched
- **Review trigger:** The baseline is repeated, or the hardware changes

### D-02 – Temporary SSH access for Claude Code

- **Date:** 28th October 2026
- **Status:** Accepted (owner, 2nd November 2026). Drafted with AI assistance
- **Related:** T-01, T-04, T-12. V-09, V-12. FND-03, FND-05
- **Context:** Claude Code runs on my laptop on the home LAN. Until Tailscale is set up, I want it to be able to run checks on the NAS that I approve from my phone when I am not at the laptop
- **Options considered:**
  1. **Claude Code uses my own account.** Nothing to set up, but it would have my sudo rights, and its actions could not be told apart from mine
  2. **A separate account for Claude Code with an SSH key.** No sudo rights, actions can be attributed, and the key works only from the laptop's address. More to set up, and an extra account and key to remove later
  3. **No direct access.** I run the commands and pass on sanitised output. Adds nothing to the NAS, but is slower and needs me at the laptop
- **Decision:** Option 2
- **Reasoning:** Separate accounts with the least privilege they need (document 01, section 6.4). The key is limited with `from=` to the laptop's address, with agent, port and X11 forwarding disabled. Every session is approved by me in advance, limited to the commands I approve, read-only unless I approve a specific change, and logged in document 05, section 7
- **Trade-offs and residual risk:** Adds an account and a key to the system during Phase 0, after the baseline collection run. The account can read files that all users can read. SSH password login is still enabled for other accounts (FND-03). If the laptop is compromised, the key gives a foothold on the NAS
- **Evidence:** Access test on 29th October 2026, 10:55 UK time (document 05, section 7): key login worked, groups `users` and `_ssh` only, no sudo rights
- **Sudo rule (drafted with AI assistance, accepted and added by the owner on 2nd November 2026, tested by Claude Code, see document 05, section 7):** lets the Claude Code account run only the read-only test commands below as root, with fixed options, so it can run V-04, V-05, V-06, V-09 and V-12 without my account. Each path is checked on the NAS with `command -v` before the rule is added, and the file is checked with `sudo visudo -c -f <FILE>`. Adding it is a change to the NAS, logged in document 05, section 7. It is removed together with the key

  ```
  # /etc/sudoers.d/claude-readonly
  Cmnd_Alias NAS_TESTS = /usr/bin/ss -tulpn, \
                        /usr/sbin/sshd -T, \
                        /usr/sbin/smartctl -a /dev/nvme0, \
                        /usr/sbin/lynis audit system, \
                        /usr/bin/cat /var/log/lynis-report.dat, \
                        /usr/bin/cat /etc/sudoers, \
                        /usr/bin/ls -l /etc/sudoers.d
  <CLAUDE-USER> ALL=(root) NOPASSWD: NAS_TESTS
  ```

  Trade-off: these commands run as root, so a flaw in one of these tools could give the account more than read access. The account still cannot run anything else as root, and sudo logs every use. Files in `/etc/sudoers.d` are listed but not read, so I read any that exist
- **Review trigger:** The end of the Phase 1 final checks, or 5th January 2027, whichever comes first. The key is then removed and the removal logged. Changed on 2nd November 2026 (owner): the key was to be removed once Tailscale was in place, but it is kept until the final checks so that Claude Code can help run them
- **Change, 6th November 2026 (owner, drafted with AI assistance):** the key's `from=` limit moves from the laptop's LAN address to the laptop's Tailscale IPv4 address, and Claude Code connects to the NAS by its Tailscale name. Reasons: a LAN address can be taken by any device on the home Wi-Fi, while a Tailscale address belongs to one approved device and its WireGuard key (D-14); the Tailscale access rules already limit port 22 on the NAS to my devices (phase1-changes.md, section 5.3); and the checks can then run when the laptop is away from home. Trade-off: the key works wherever the laptop is online, not only at home. Every session still needs my approval with the test IDs, the sudo rule is unchanged, and the key is still removed at the review trigger. The LAN address is removed, not kept alongside. I make the change on the NAS; Claude Code does not change its own access. Logged in document 05, section 7. Made and tested on 6th November 2026
- **Change, 9th November 2026 (owner, drafted with AI assistance):** the key is not removed at the end of the Phase 1 final checks. It is kept for Phase 2, with the same limits: Tailscale address only, the same sudo rule, sessions approved by the owner in advance and logged. The 5th January 2027 review date still applies. If Tailscale is removed in Phase 2, the `from=` limit needs a new change record (phase2-plan.md, question 2.6.1)
- **Change, 12th November 2026 (owner request, drafted with AI assistance):** the sudo rule gains one command, `/usr/bin/dd if=/dev/mmcblk0 bs=4M status=none`, so Claude Code can take the SD card image over SSH (D-28). sudo matches the whole command line, so `dd` cannot be given another device or an output file, and the image is written only to the laptop. Trade-off: this lets the account read the whole SD card, including password hashes, SSH host keys, the NAS's WireGuard private key, the Tailscale node key and OMV's configuration, which is far more than the read-only test commands. The SSD is not included (D-06). The image is kept only in `~/NAS-Evidence/` on the laptop, outside the repository and the Borg backup. Added by the owner on the NAS following phase3-changes.md, section 2.1, and logged in document 05, section 7. Removed with the rest of the rule at the 5th January 2027 review at the latest

### D-03 – Vulnerability monitoring dashboard

- **Date:** 30th October 2026
- **Status:** Accepted (owner, 2nd November 2026). Drafted with AI assistance. Creating the account and key is a change to the NAS, so it happens after Phase 0, or is logged as a deviation
- **Related:** T-02, T-06, T-14. V-03, V-10. FND-06. SR-14 (document 03, draft)
- **Context:** I want a local dashboard that checks the software on the NAS for known vulnerabilities every 12 hours, so I do not depend on remembering to look. Phase 0 showed a pending openmediavault update (FND-06) and that unattended upgrades are enabled but have installed nothing. Installing anything is a change, so this belongs to Phase 1 or later
- **Options considered:**
  1. **Run on the NAS.** A timer runs `debsecan` and `apt list --upgradable` and writes a page. Most accurate, needs no remote access. Adds a package and a timer to the NAS, and serving the page would add a service to protect (T-13)
  2. **Run on the laptop, using the temporary Claude Code key (D-02).** Nothing to set up. But D-02 and my working rules allow that key only for sessions I approve one by one, with the commands listed, so an unattended job every 12 hours would break that rule. The NAS logs would show the Claude Code account logging in when Claude Code is not working. The key is removed when Tailscale is in place or on 5th January 2027, so the dashboard would then stop
  3. **Run on the laptop, using a dedicated monitoring key.** A separate key in `authorized_keys`, limited with `restrict`, `from=` (laptop only) and `command=` to the one read-only command, so it cannot open a shell or forward anything. Adds nothing to the NAS except one key line. Needs a change on the NAS after Phase 0, which is logged. Only runs while the laptop is on
- **Decision:** Option 3 (owner, 30th October 2026, by messaging app). My first preference was option 2. Claude Code pointed out the conflict with D-02 and my working rules, and I chose a dedicated key instead. The key is held by a separate account with no sudo rights (owner, 2nd November 2026), so the logs show the dashboard as itself and it does not end with D-02
- **Reasoning:** The dashboard only needs to read the installed software and versions, so a key limited to that one read-only command is enough, and it can run unattended without using the Claude Code access
- **Trade-offs and residual risk:** For options 2 and 3, package names and versions are sent to OSV (a public API run by Google). No hostnames, addresses or usernames are sent. The dashboard output lists unfixed vulnerabilities and exact versions, so it stays in the raw evidence location and is never published. Packages from openmediavault and Raspberry Pi repositories are not covered by the Debian data and stay as manual checks. This includes Debian packages that Raspberry Pi rebuilds, among them the kernel, glibc and OpenSSL (added 5th November 2026), so these important packages depend on checking Raspberry Pi's release notes and on the weekly update routine. Records are also checked against CISA's Known Exploited Vulnerabilities catalogue, a plain download that sends nothing about the NAS, and a desktop notification on the laptop reports changes (added 5th November 2026). The dashboard shows only publicly known issues
- **Evidence:** Draft script `scripts/vuln-dashboard/`, tested on 30th October 2026 with made-up package data only. Set up on 5th November 2026 (document 05, section 7), first run the same day, V-18 in progress
- **Change after Tailscale (5th November 2026, owner):** the key is limited with `from=` to the laptop's Tailscale address instead of its LAN address, and the laptop connects to the NAS by its Tailscale name. The dashboard then works away from home, and the laptop's Tailscale address does not change when its LAN address does. The Tailscale access rules already allow the laptop to reach the NAS on port 22
- **Review trigger:** Tailscale is in place (the access path may change), D-02 ends, or the dashboard misses an update that V-10 finds

### D-04 – Admin interface access and HTTPS

- **Date:** 2nd November 2026
- **Status:** Accepted (owner, 2nd November 2026, from suggestions drafted with AI assistance)
- **Related:** T-01, T-13. SR-02. V-01, V-04, V-20, V-21
- **Context:** The OMV web interface is served over plain HTTP on all interfaces (V-01, V-04)
- **Options considered:**
  1. **Plain HTTP, LAN only.** Nothing to set up, but passwords cross the home Wi-Fi unencrypted
  2. **HTTPS with OMV's self-signed certificate, LAN and Tailscale only.** Encrypted, little to set up. Browsers warn about the certificate, so the fingerprint is checked by hand once
  3. **HTTPS with a publicly trusted certificate** (own domain or Tailscale's certificate feature). No browser warning, but more to set up, and certificate transparency logs publish the machine name
- **Decision:** Option 2
- **Reasoning:** Limiting access to the LAN and Tailscale is the main control. HTTPS on top stops the admin password crossing the Wi-Fi in clear text, at little cost
- **Trade-offs and residual risk:** Browser warnings remain. A first connection could be intercepted if the fingerprint is not checked
- **Evidence:** Phase 1 re-tests, not yet run
- **Review trigger:** A trusted certificate becomes easy to get without publishing names, or remote access changes

### D-05 – File sharing protocol

- **Date:** 2nd November 2026
- **Status:** Accepted (owner, 2nd November 2026, from suggestions drafted with AI assistance)
- **Related:** T-12, T-13. SR-07, SR-11. V-02, V-04, V-11
- **Context:** Document 01, section 6.2 leaves the protocol open. SMB is enabled in OMV but not running, and rpcbind (used by NFS) listens on all interfaces (FND-04)
- **Options considered:**
  1. **SMB only, version 3 minimum.** Supported by phones and computers, and encryption is available
  2. **NFS.** Suited to Linux clients, weaker per-user access control without extra setup, and needs rpcbind
  3. **Both.** Most flexible, but two services to protect
- **Decision:** Option 1, with no guest access
- **Reasoning:** One protocol that every client supports, and dropping NFS lets rpcbind be turned off (D-13)
- **Trade-offs and residual risk:** Very old clients that only support SMB1 or SMB2 cannot connect
- **Evidence:** Phase 1 re-tests, not yet run
- **Review trigger:** A client needs NFS or an older SMB version

### D-06 – Encryption at rest

- **Date:** 2nd November 2026
- **Status:** Accepted (owner, 2nd November 2026, from suggestions drafted with AI assistance)
- **Related:** T-11. SR-12. FND-08. V-14
- **Context:** No disk is encrypted (FND-08). The NAS holds no data yet, so this is the easiest time to encrypt the SSD
- **Options considered:**
  1. **No encryption.** No effect on reboots, but a stolen SSD or SD card can be read
  2. **SSD encrypted (LUKS), key file on the SD card.** Unlocks itself after a reboot, but anyone who takes the whole device gets the key too
  3. **SSD encrypted (LUKS), unlocked by hand after each reboot.** Protects the data if the device is taken, but data is unavailable until I unlock it
  4. **SD card encrypted as well.** Also protects the system and its configuration, but complicated on a Raspberry Pi and needs a passphrase before the system starts
- **Decision:** Option 3. The SD card is not encrypted, as an accepted risk
- **Reasoning:** The data on the SSD is what matters most. A key file on the SD card would defeat the purpose. Encrypting the SD card adds a lot of complexity for less benefit
- **Trade-offs and residual risk:** After any reboot or power cut, shares and backups stop until I unlock the SSD. The SD card can still be read if removed, including OMV configuration, password hashes and SSH host keys, so secrets are kept on the SSD where possible. T-11 stays Medium until this is verified
- **Evidence:** Phase 1 re-tests, not yet run
- **Review trigger:** Unlocking by hand becomes impractical, or the SD card starts holding secrets that cannot be moved

### D-07 – Limiting failed SSH logins

- **Date:** 2nd November 2026
- **Status:** Accepted (owner, 2nd November 2026, from suggestions drafted with AI assistance)
- **Related:** T-04. SR-06. V-04, V-09
- **Context:** No service limits repeated SSH login attempts (V-04)
- **Options considered:**
  1. **No limit.** Key-only login (SR-05) already makes guessing impractical
  2. **OpenSSH settings only** (for example `MaxAuthTries`). Nothing to install, but no blocking across connections
  3. **fail2ban.** Blocks a source after repeated failures, at the cost of a package and a service
- **Decision:** Option 3: 5 failures within 10 minutes blocks the source for 1 hour
- **Reasoning:** A common default that slows any attempt without locking me out for long. It also limits noise in the logs
- **Trade-offs and residual risk:** One more package and service to keep updated. I could block myself for an hour, so I keep a second device or the direct Ethernet link for recovery
- **Evidence:** Phase 1 re-tests, not yet run
- **Review trigger:** Too many false blocks, or SSH is no longer reachable from anywhere but Tailscale

### D-08 – Update routine

- **Date:** 2nd November 2026
- **Status:** Accepted (owner, 2nd November 2026, from suggestions drafted with AI assistance)
- **Related:** T-02, T-14. SR-10. FND-06. V-10
- **Context:** Unattended upgrades are enabled but have installed nothing, and openmediavault has a pending update (FND-06)
- **Options considered:**
  1. **Manual updates only.** Full control, but depends on me remembering
  2. **Security updates automatic each day, others by hand within 14 days.** Security fixes arrive quickly, larger changes stay under my control
  3. **Everything automatic.** Least effort, but an openmediavault upgrade could break the system unattended
- **Decision:** Option 2, with an image of the SD card before any major upgrade
- **Reasoning:** Most of the risk is in security fixes, which are small and safe to install automatically. Larger updates are better done when I can check the result
- **Trade-offs and residual risk:** An automatic update can still occasionally break something. Updates from the openmediavault and Raspberry Pi repositories are checked by hand
- **Evidence:** Phase 1 re-tests, not yet run
- **Review trigger:** An automatic update causes a problem, or V-10 finds updates older than 14 days

### D-09 – SSD health warnings

- **Date:** 2nd November 2026
- **Status:** Accepted (owner, 2nd November 2026, from suggestions drafted with AI assistance)
- **Related:** T-10, T-18. SR-13. V-06
- **Context:** SSD health is only checked when I look (V-06)
- **Options considered:**
  1. **OMV's built-in email notifications.** Built in, but needs an email account to send from
  2. **A script that sends a messaging app alert.** Reaches my phone directly, but more to build and maintain
  3. **Checking by hand.** Nothing to set up, but easy to forget
- **Decision:** Option 1
- **Reasoning:** Built into OMV and covers SMART warnings as well as other system events
- **Trade-offs and residual risk:** Needs email account credentials stored on the NAS, so a dedicated account or app password is used. Warnings only help if I read them
- **Evidence:** Phase 1 alert test V-17. Postponed by the owner on 3rd November 2026 while the alert method is reviewed: OMV can only send through Proton with an SMTP token for an address on a custom domain, which would have to be bought. Options under review: a custom domain on Proton, or option 2. Deferred out of Phase 1 by the owner on 6th November 2026: SR-13 and V-17 stay open until the alert method is chosen, and SSD health is checked by hand until then
- **Review trigger:** Emails are missed, or the email account changes

### D-10 – NAS network connection and radios

- **Date:** 2nd November 2026
- **Status:** Accepted (owner, 2nd November 2026, from suggestions drafted with AI assistance)
- **Related:** T-07, T-13, T-18. SR-07
- **Context:** The NAS uses Wi-Fi. Bluetooth is running (V-04). The direct Ethernet link to the laptop is kept for troubleshooting (D-01)
- **Options considered:**
  1. **Ethernet to the router, Wi-Fi and Bluetooth off.** More reliable, fewer radios to protect, but needs a cable to the router
  2. **Wi-Fi, Bluetooth off.** No cable needed, but less reliable for large transfers
- **Decision:** Option 1 if a cable can reach the router, otherwise option 2. Bluetooth is turned off either way. Owner, 3rd November 2026: no cable can reach the router at present, so option 2 applies
- **Reasoning:** Fewer interfaces and radios means less to protect, and a wired link suits a NAS
- **Trade-offs and residual risk:** With Wi-Fi off, the NAS depends on the cable. The direct troubleshooting link stays available but is not normally connected
- **Evidence:** Phase 1 re-tests, not yet run
- **Review trigger:** The NAS moves, or a cable to the router is no longer possible

### D-11 – Network isolation

- **Date:** 2nd November 2026
- **Status:** Accepted (owner, 2nd November 2026, from suggestions drafted with AI assistance)
- **Related:** T-07
- **Context:** The NAS shares the home LAN with all other devices. Whether the router supports guest isolation or VLANs has not been checked
- **Options considered:**
  1. **Accept the risk.** No change, but any compromised device on the LAN can reach the NAS's LAN services
  2. **Guest network or VLAN for other devices**, if the router supports it. Limits which devices can reach the NAS
- **Decision:** Option 1, unless a router check (optional) shows guest isolation or VLAN support
- **Reasoning:** Restricting NAS services to the LAN and Tailscale (D-04, D-13) already reduces what other devices can reach
- **Trade-offs and residual risk:** A compromised device on the LAN can still attempt the remaining services. T-07 stays as rated
- **Evidence:** Router check by the owner, 3rd November 2026: no guest network in use, and no isolation or VLAN settings on the router. Option 1 stands
- **Review trigger:** A router that supports isolation, or a new device type on the LAN

### D-12 – Power protection

- **Date:** 2nd November 2026
- **Status:** Accepted (owner, 2nd November 2026, from suggestions drafted with AI assistance)
- **Related:** T-18
- **Context:** The NAS has no protection against power cuts. The SSD shows 179 unsafe shutdowns over its life, most likely from earlier use
- **Options considered:**
  1. **UPS.** Allows a clean shutdown, but outside the budget
  2. **No UPS, with a written safe shutdown routine and an image of the boot media.** No cost, but a power cut is still an unclean shutdown
- **Decision:** Option 2
- **Reasoning:** The budget rules out a UPS. A routine and an image limit the damage
- **Trade-offs and residual risk:** A power cut can still corrupt data being written. With D-06, the SSD also needs unlocking after power returns
- **Evidence:** Safe shutdown routine, Phase 1
- **Review trigger:** Budget changes, or unclean shutdowns cause a problem

### D-13 – Network services not in the inventory

- **Date:** 2nd November 2026
- **Status:** Accepted (owner, 2nd November 2026, from suggestions drafted with AI assistance)
- **Related:** T-02, T-13. SR-07. FND-04. V-01, V-02, V-04
- **Context:** rpcbind, LLMNR, mDNS and a DHCPv6 client listen on network interfaces without a row in the service inventory (FND-04)
- **Options considered:**
  1. **Turn all four off.** Smallest attack surface, but IPv6 set-up and name discovery may be affected
  2. **Keep only what is needed.** rpcbind off (only NFS needs it), LLMNR off (old Windows name lookup), mDNS off unless Apple devices need to find the NAS by name, DHCPv6 client kept (link-local only, helps IPv6 set-up)
- **Decision:** Option 2
- **Reasoning:** Each service is kept only if it has a use. The DHCPv6 client is low risk and supports IPv6 on the NAS
- **Trade-offs and residual risk:** Devices cannot discover the NAS by name, so it is reached by address or a fixed name. mDNS is turned back on if that proves impractical
- **Evidence:** Phase 1 re-tests, not yet run
- **Review trigger:** A client needs name discovery, or NFS is needed

### D-14 – Tailscale new device control

- **Date:** 4th November 2026
- **Status:** Accepted (owner, 4th November 2026, from suggestions drafted with AI assistance)
- **Related:** T-08, T-16. SR-18, SR-19. V-19, V-22, V-26. Document 02, section 7
- **Context:** Tailscale offers two ways to stop devices joining the tailnet without my say. They cannot both be used
- **Options considered:**
  1. **Device approval.** Each new device waits until I approve it in the admin console. Nothing extra to look after, available on all plans. Does not protect against the coordination service adding a device by itself
  2. **Tailnet Lock.** New devices must be signed by trusted keys on my own devices, so the coordination service cannot add devices by itself. Needs at least two signing devices, and disablement secrets that must be stored safely, as losing them can leave the tailnet unrecoverable
- **Decision:** Option 1. Tailscale SSH is not turned on: SSH stays as OpenSSH with keys (SR-05)
- **Reasoning:** Device approval meets SR-19 with little upkeep for a one-person system. The threat Tailnet Lock adds cover for, a compromised or malicious coordination service, is the main question for the Phase 2 comparison with self-hosted WireGuard
- **Trade-offs and residual risk:** I trust Tailscale's coordination service not to add devices itself (document 02, section 7.3). OMV and SSH logins still apply to any device on the tailnet
- **Evidence:** V-19, once Tailscale is set up
- **Review trigger:** The Phase 2 comparison, or a reported compromise of Tailscale's coordination service

### D-15 – Storage file system, SMB encryption and first share

- **Date:** 5th November 2026
- **Status:** Accepted (owner, 5th November 2026, from suggestions drafted with AI assistance)
- **Related:** T-05, T-07, T-11, T-12. SR-11, SR-12, SR-17. D-05, D-06. V-11, V-14
- **Context:** The SSD is about to be encrypted (D-06) and shared over SMB 3 (D-05), with no data on it yet. Photos and other media are to move off Google Drive
- **Options considered:**
  1. **ext4, SMB encryption off.** Simplest. File contents cross the Wi-Fi unencrypted
  2. **Btrfs, SMB encryption required.** Btrfs lets OMV take snapshots of shared folders, which can undo deletions or ransomware damage. Required encryption protects file contents on the Wi-Fi, and needs SMB 3 clients, which D-05 already requires
- **Decision:** Option 2. The first share is for photos and other media, for the daily account only
- **Reasoning:** Choosing the file system before any data is stored avoids moving everything later. Encrypting SMB traffic costs nothing extra once SMB 3 is required
- **Trade-offs and residual risk:** Btrfs needs some care (free space, scrubs) that ext4 does not. Very old clients cannot connect. While Phase 3 backups are not in place, the NAS must not become the only copy of the photos: the Google Drive copy is kept until an offsite copy exists. Choosing a photo application that runs on the NAS would add a service, and is a separate decision
- **Evidence:** Phase 1 section 8, not yet done
- **Review trigger:** Btrfs causes problems, a client cannot use SMB encryption, or a photo application is chosen

### D-16 – WireGuard alongside Tailscale

- **Date:** 9th November 2026
- **Status:** Accepted (owner, 9th November 2026, from the owner's answers in phase2-plan.md, section 2, drafted with AI assistance)
- **Related:** T-08, T-16, T-17. SR-02, SR-18, SR-19. D-02, D-14. Objective O-6 (document 01)
- **Context:** Phase 2 adds self-hosted WireGuard and compares it with Tailscale. Tailscale is the only remote access path today, and Claude Code's key is limited to the laptop's Tailscale address (D-02)
- **Options considered:**
  1. **Replace Tailscale straight away.** One way in, but no fallback while WireGuard is new, and no side-by-side comparison
  2. **Run both, decide later.** A fair comparison and a fallback, but two ways in while both run
- **Decision:** Option 2 (owner, 8th November 2026). Which one to keep is decided later in Phase 2, after the comparison tests
- **Reasoning:** Tailscale stays the way back in if the WireGuard tunnel fails while away from home (question 2.5.2). D-02 needs no change while Tailscale stays
- **Trade-offs and residual risk:** Two remote access paths to maintain, monitor and revoke separately. A device removed from one path keeps access through the other until it is removed there too
- **Evidence:** Phase 2 tests (phase2-plan.md, section 6), not yet run
- **Review trigger:** The comparison tests are done, or either path causes a problem
- **Change, 12th November 2026 (owner, drafted with AI assistance):** Tailscale is kept as the remote access path. WireGuard stays on the NAS for the laptop on the home network only: no router port forward, so it cannot be reached from the internet. The phone's peer block stays in `wg0.conf` for later, although the phone did not complete a handshake. Reasons: the tunnel and its firewall work for the laptop (document 05, section 4.3), Tailscale already gives remote access that works (V-20), and the owner prefers to move on to Phase 3 (backups). The comparison tests that need the port forward (V-07, V-28 to V-31, V-35, V-36) are not run, so the comparison for O-6 is limited to the set-up and LAN use. Trade-off: WireGuard adds a listening UDP port on the home network and a second set of keys to look after, for little use while Tailscale stays. Review trigger: remote access is needed without Tailscale, Tailscale causes a problem, or WireGuard is not used by the 5th January 2027 review
- **Change, 15th November 2026 (owner, drafted with AI assistance):** the NAS is no longer on the owner's home network and is reachable only over Tailscale. WireGuard, which was set up for the laptop on the LAN only, cannot be used, but its UDP port is still open on the NAS. Whether to stop and disable `wg-quick@wg0` is an open owner decision. LAN-based tests now run against the NAS's Tailscale address, or by inspection
- **Change, 15th November 2026 (owner decision, drafted with AI assistance):** WireGuard is turned off: `wg-quick@wg0` stopped and disabled on the NAS, which also removes its firewall table, and the laptop's tunnel and the phone's tunnel removed from use. The configuration files and keys stay on each device, root-only, so the tunnel can be turned back on with `systemctl enable --now wg-quick@wg0`. Phase 2's comparison of Tailscale and WireGuard (objective O-6) stands as written. Steps and checks in phase2-changes.md, section 10

### D-17 – Where WireGuard runs and how it is installed

- **Date:** 9th November 2026
- **Status:** Accepted (owner, 9th November 2026, from the owner's answers in phase2-plan.md, section 2, drafted with AI assistance)
- **Related:** T-06, T-17. SR-10, SR-15. D-06, D-16
- **Context:** WireGuard can run on the NAS or, if supported, on the router. On the NAS it can be set up by hand or through an OMV plugin
- **Options considered:**
  1. **On the NAS, by hand.** The kernel module and `wg-quick`, configured in `/etc/wireguard/`. No plugin, but OMV does not know about it
  2. **On the NAS, with an OMV plugin.** Managed in the OMV interface, but needs an SR-15 plugin review
  3. **On the router.** Keeps the tunnel off the NAS, if the ISP router supports WireGuard at all
- **Decision:** Option 1 (owner, 9th November 2026). The tunnel starts at boot through the `wg-quick` service. SMB is available only after the SSD is unlocked (D-06)
- **Reasoning:** No third-party plugin, and setting it up by hand teaches more. Tailscale uses its own interface and port, so the two do not clash
- **Trade-offs and residual risk:** The configuration lives outside OMV, so it has to be documented and is not shown in the OMV interface. An OMV network change could affect it. The NAS's private key is on the SD card, which is not encrypted (FND-08, D-06), so anyone with the card or an image of it has that key
- **Evidence:** Phase 2 tests V-34 and V-35 (phase2-plan.md, section 6), not yet run
- **Review trigger:** An OMV update breaks the tunnel, or a plugin becomes the better choice

### D-18 – What WireGuard peers can reach

- **Date:** 9th November 2026
- **Status:** Accepted (owner, 9th November 2026, from the owner's answers in phase2-plan.md, section 2, drafted with AI assistance)
- **Related:** T-07, T-13. SR-02, SR-07, proposed SR-21. D-11, D-16
- **Context:** WireGuard has no access rules of its own. `AllowedIPs` controls routing, not which ports a peer may use. Tailscale's access rules allow only 22, 443 and 445 to the NAS
- **Options considered:**
  1. **Only the NAS, on 22, 443 and 445**, enforced by a firewall on the NAS for the WireGuard interface
  2. **The whole home network**
- **Decision:** Option 1 (owner, 9th November 2026). Split tunnel on the clients, so only NAS traffic goes through it. IPv4 only, so no IPv6 pinhole is opened
- **Reasoning:** The same reach as Tailscale, so the comparison is fair, and the least access a peer needs. IPv6 would need a second exception to SR-09
- **Trade-offs and residual risk:** A host firewall becomes required for the WireGuard interface, where it was optional in Phase 1. A mistake in its rules could block access or allow more than intended, so it is tested (V-31)
- **Evidence:** Phase 2 tests V-30 and V-31, not yet run
- **Review trigger:** A peer needs another device on the home network, or IPv6 access is needed

### D-19 – Port forward and changes of public address

- **Date:** 9th November 2026
- **Status:** Accepted (owner, 9th November 2026, from the owner's answers in phase2-plan.md, section 2, drafted with AI assistance)
- **Related:** T-03, T-19. SR-08, SR-09 (both to change). D-16
- **Context:** Self-hosted WireGuard needs one UDP port forwarded from the router to the NAS. The home public IPv4 address changed between Phase 0 and 7th November 2026 (V-08), so clients need a way to find the new address
- **Options considered (address changes):**
  1. **Check by hand and update the clients.** Nothing new, but too slow, as the address changed within about a week
  2. **A DDNS provider.** Simple, but a new third party, against the aim of removing dependencies (phase2-plan.md, question 2.1.4)
  3. **A script on the NAS that tells the owner the new address.** No third party, more to maintain
- **Decision:** One UDP port forward from the router to the NAS, on a non-default high port, recorded only as `<WG-PORT>`. The router supports a UDP forward to one address (owner, 9th November 2026). Changes of public address are handled by option 3 (owner, 9th November 2026)
- **Reasoning:** The port forward is the minimum WireGuard needs. A non-default port cuts scan noise but is not a security control. WireGuard does not answer packets without a valid key, so the port looks closed to scanners
- **Trade-offs and residual risk:** SR-08 and SR-09 each gain one documented exception. Whether the forward stays after a router restart or firmware update is not yet known. How the script tells the owner the new address is not yet decided: the address is private, so it must not go through the Telegram channel or anywhere it is kept. Until the clients are updated with a new address, WireGuard is down and Tailscale is the way in
- **Evidence:** Phase 2 tests V-28 and V-36, not yet run
- **Review trigger:** The router loses the forward, the address changes too often for the script, or Tailscale is removed
- **Change, 12th November 2026 (owner):** not implemented. With Tailscale kept (D-16, 12th November 2026), no port forward is added and the address script (phase2-changes.md, section 7) is not installed. The router stays as verified in Phase 1: no port forwards, no DMZ host, UPnP off
- **Change, 9th November 2026 (owner, drafted with AI assistance):** the script checks the public address every 15 minutes. When it changes, it writes the new address to a file on the NAS that only the owner's account can read, and the owner fetches it over Tailscale. Nothing is pushed to a third party. Target: a peer reconnects within 30 minutes of a change, once the owner has updated the client (V-36). If Tailscale is removed (D-16), this needs a new way to reach the file

### D-20 – WireGuard key management

- **Date:** 9th November 2026
- **Status:** Accepted (owner, 9th November 2026, from the owner's answers in phase2-plan.md, section 2, drafted with AI assistance)
- **Related:** T-08, T-17. SR-18, proposed SR-22 and SR-23. D-14, D-16, D-17
- **Context:** WireGuard has no central console. Each peer is a key pair, and the NAS accepts only the public keys in its configuration
- **Decision (owner, 9th November 2026):**
  1. Key pairs are made on each device. Private keys never leave it, and no recovery copy is kept. A lost device's key is revoked and a new key made
  2. Each peer also has a preshared key
  3. Keys are rotated every 180 days, matching the Tailscale key expiry
  4. A peer is revoked by removing it from the NAS configuration and reloading, within 5 minutes (as SR-18)
  5. The peer list (device name, public key, tunnel address) is kept in Proton Pass, not in the repository
  6. Connections are checked by hand with `wg show` (last handshake) during Phase 2
  7. A peer exists only if the owner adds its public key. This is WireGuard's counterpart to device approval (D-14)
- **Reasoning:** Keys that never move cannot be copied in transit. Preshared keys cost little and add some protection against future quantum attacks
- **Trade-offs and residual risk:** Rotation and revocation are manual and easy to forget. Each peer has two secrets. Without a timer check, a peer that should not be connecting is seen only when `wg show` is run. The NAS's own private key is on the unencrypted SD card (D-17)
- **Evidence:** Phase 2 tests V-29, V-32, V-33 and V-34, not yet run
- **Review trigger:** A device is lost, a rotation is missed, or a key may have leaked
- **Change, 12th November 2026 (owner, drafted with AI assistance):** two peers are configured, the laptop (working on the home network) and the phone (added, no handshake yet, kept for later). Revocation (V-32) and rotation (V-33) are not tested, and the procedure in phase2-changes.md, section 8 is not yet written up on its own. The 180-day rotation starts from the date each peer was added. Residual risk: the phone's preshared key is in `wg0.conf` and in the phone app for a peer that is not in use

### D-21 – Backup tool and transport

- **Date:** 12th November 2026
- **Status:** Accepted (owner, 12th November 2026, from the owner's answers in phase3-plan.md, section 2, drafted with AI assistance)
- **Related:** T-05, T-08, T-09, T-10. Proposed SR-24, SR-25. D-02, D-16. Objective O-4 (document 01)
- **Context:** Phase 3 adds automated backups of the laptop to the NAS. Document 01 asks for encryption in transit, a backup account that can write only to its own location, and a restore from a version the client cannot overwrite
- **Options considered:**
  1. **BorgBackup over SSH.** Encrypted on the laptop, the SSH key can be limited to append-only Borg in one repository, and it uses the existing SSH service. Borg is needed on both sides
  2. **restic with rest-server in append-only mode.** Similar features, but rest-server is a new service and a new listening port on the NAS
  3. **restic over SFTP.** Simple, but the laptop's key can delete snapshots
  4. **rsync with snapshots on the NAS.** Easy to browse, but not encrypted on the laptop, and the snapshots need their own protection
- **Decision:** Option 1 (owner, 12th November 2026), through Tailscale
- **Reasoning:** Meets all three document 01 conditions without a new port, so the service inventory and V-01 and V-04 stay as they are. The key limits follow the same pattern as Claude Code's key (D-02)
- **Trade-offs and residual risk:** Borg 1.x append-only keeps deleted data until the administrator compacts, so the repository grows until pruned from the NAS side (D-25). The laptop (Linux Mint 22.2, Borg 1.2.x) and the NAS (Debian 13, Borg 1.4.x) must stay on Borg 1.x
- **Evidence:** Phase 3 tests V-25 and V-37 to V-44, not yet run
- **Review trigger:** Borg 1.x stops receiving fixes, or Tailscale is removed (D-16)

### D-22 – What the laptop backs up

- **Date:** 12th November 2026
- **Status:** Accepted (owner, 12th November 2026, from the owner's answers in phase3-plan.md, section 2, drafted with AI assistance)
- **Related:** T-08, T-09, T-15. Proposed SR-24, SR-30. D-20, D-21
- **Context:** The owner wants the laptop's files and device settings backed up, with passwords left to the password manager
- **Options considered:**
  1. **Home folder only, run as the owner's user.** Simpler, no root job, but system settings are not covered
  2. **Home folder, `/etc` and a list of installed packages, run as root.** Covers files, app and desktop settings and system settings, so the laptop can be rebuilt
- **Decision:** Option 2 (owner, 12th November 2026). Included: the home folder, `/etc`, and a list of installed packages written just before each run. Keys included: SSH keys (`~/.ssh`), GPG keys (`~/.gnupg`) and the laptop's SSH host keys (`/etc/ssh`). Left out: `~/Downloads`, caches, the bin, the SD card images in `~/NAS-Evidence/`, passwords: saved browser logins (Firefox `logins.json` and `key4.db`, Chromium `Login Data`), the desktop keyring (`~/.local/share/keyrings`), Wi-Fi passwords (`/etc/NetworkManager/system-connections`), password hashes (`/etc/shadow`, `/etc/gshadow` and their backups), and access tokens stored by command-line tools (for example `~/.git-credentials`, `~/.config/gh/hosts.yml`, `~/.claude/.credentials.json`, `~/.netrc`), and the laptop's WireGuard keys and tunnel file (`/etc/wireguard`), as D-20 keeps no recovery copy of WireGuard private keys, and the backup job's own passphrase file and SSH key in `/root`. The phone is deferred
- **Reasoning:** Passwords are already kept by the password manager, so a second copy adds exposure without adding recovery. Keys such as SSH and GPG keys have no other copy, so losing them would lock the owner out of other systems
- **Trade-offs and residual risk:** The exclusion list is by path, so a password stored somewhere new is backed up until the list is updated. V-44 checks the list against an archive. After a restore, Wi-Fi networks must be joined again and tokens signed in again. The SSH and GPG private keys are in the backup, protected by the repository encryption (D-24)
- **Evidence:** Phase 3 test V-44, not yet run
- **Review trigger:** A new application stores passwords or keys outside the listed paths, or the laptop is replaced
- **Change, 12th November 2026 (drafted with AI assistance):** a check of the laptop's applications (file names only) added three more places to leave out: Thunderbird's saved logins, the token file for the Telegram channel, and OBS Studio's stream keys. There is no `~/.gnupg` on the laptop, so no GPG keys are backed up today. The full list is in phase3-changes.md, section 7.1
- **Change, 15th November 2026 (owner, drafted with AI assistance):** the `~/VirtualBox VMs` folder is left out. It was 98 GB, most of the first full backup, and its disk and saved-state files change whenever a virtual machine runs, so each daily run would re-read tens of GB over the NAS's slow link. The virtual machines are not backed up. Data from them already sent stays in the first archive until it is pruned (D-25)
- **Change, 15th November 2026 (owner, drafted with AI assistance):** V-44 found 12 `Login Data` files in Zoom's embedded-browser cache bin, so `~/.zoom/data/cefcache` is left out (13 MB of cache). Correction: the laptop has no SSH server, so there are no SSH host keys in `/etc/ssh` to back up, in the same way as `~/.gnupg`

### D-23 – Backup account, repository and key limits

- **Date:** 12th November 2026
- **Status:** Accepted (owner, 12th November 2026, from the owner's answers in phase3-plan.md, section 2, drafted with AI assistance)
- **Related:** T-05, T-08, T-12. Proposed SR-25, SR-26. D-02, D-06, D-21. Document 01, section 6.4
- **Context:** The backup must not be deletable from the laptop, and the account it uses must reach nothing else
- **Options considered:**
  1. **Repository in an SMB share.** Easy to see, but anything that mounts the share can reach the backups (T-05)
  2. **Dedicated account, repository on the SSD not shared over SMB, key limited to append-only Borg**
- **Decision:** Option 2 (owner, 12th November 2026). A dedicated backup account with no password, SSH key login only, no sudo rights, and membership of `_ssh`. The repository is a folder on the encrypted SSD owned by that account and not shared over SMB. The laptop's key is limited in `authorized_keys` with `restrict`, `from=` (the laptop's Tailscale address only) and `command="borg serve --append-only --restrict-to-repository <REPO-PATH>"`. The private key is kept in root's SSH folder on the laptop, as the job runs as root (D-22)
- **Reasoning:** Each limit covers a different failure: `restrict` stops forwarding and terminals, `from=` stops use of a copied key from elsewhere, and `command=` stops anything other than append-only Borg in one place
- **Trade-offs and residual risk:** Backups only run while the laptop is on Tailscale. While the SSD is locked after a reboot (D-06), backups fail until it is unlocked (V-42). The account's name is the same as the Debian package name, so a reader of the published repository could guess it; accepted by the owner on 17th November 2026, as it can only log in with the restricted key from the laptop's Tailscale address
- **Evidence:** Phase 3 tests V-25, V-37 and V-42, not yet run
- **Review trigger:** Tailscale is removed, or the laptop is replaced

### D-24 – Backup encryption and key storage

- **Date:** 12th November 2026
- **Status:** Accepted (owner, 12th November 2026, from the owner's answers in phase3-plan.md, section 2, drafted with AI assistance)
- **Related:** T-08, T-15. Proposed SR-24, SR-27. D-21, D-23
- **Context:** Borg encrypts on the laptop. Losing the key or passphrase means losing the backups (T-15)
- **Options considered:**
  1. **`repokey-blake2`.** The key is stored in the repository, protected by the passphrase. A restore needs the passphrase and the repository
  2. **`keyfile-blake2`.** The key stays on the laptop, so the NAS holds nothing usable even if the passphrase leaks, but losing the laptop loses the key unless a copy is kept
- **Decision:** Option 1 (owner, 12th November 2026), with a long random passphrase. The passphrase and an export of the key (`borg key export --paper`) are kept in Proton Pass and on paper at home, away from the NAS. On the laptop, the scheduled job reads the passphrase from a file readable only by root (mode 600)
- **Reasoning:** A restore needs only the passphrase and the key copy, which do not depend on the laptop. Two places, as T-15 asks
- **Trade-offs and residual risk:** Anyone who controls root on the laptop can read the passphrase. Append-only (D-23) limits what they can do with it to adding data and marking archives deleted. The passphrase alone protects the repository if the NAS is taken, so it must be long and random
- **Evidence:** Phase 3 tests V-38 and V-41, not yet run
- **Review trigger:** The passphrase or the paper copy may have been seen, or the laptop is lost

### D-25 – Backup schedule, retention and pruning

- **Date:** 12th November 2026
- **Status:** Accepted (owner, 12th November 2026, from the owner's answers in phase3-plan.md, section 2, drafted with AI assistance)
- **Related:** T-05, T-09, T-15. Proposed SR-24, SR-25, SR-29. D-21, D-23
- **Context:** Append-only means the laptop cannot remove old archives, so pruning has to happen elsewhere
- **Options considered:**
  1. **borgmatic.** Configuration file with retention and checks built in, one more package
  2. **Plain `borg` with a script and a systemd timer.** Least software, easiest to read and record
  3. **Vorta.** Desktop app, harder to record and test
- **Decision:** Option 2 (owner, 12th November 2026). Daily, from a system timer with `Persistent=true`. Archives kept: 7 daily, 4 weekly and 6 monthly. Once a month, the administrator prunes and checks the repository from the NAS side, typing the passphrase, after checking that no archive was deleted unexpectedly, then compacts. `borg check --verify-data` every 3 months. Restore tests at the end of Phase 3 and every 3 months (SR-29)
- **Reasoning:** Keeps the pruning credentials off the laptop, so a compromised laptop cannot make deletions permanent
- **Trade-offs and residual risk:** Pruning and checks are manual and can be missed. The repository grows between prunes
- **Evidence:** Phase 3 tests V-25, V-39 and V-40, not yet run
- **Review trigger:** A monthly prune is missed, or the SSD fills up
- **Change, 13th November 2026 (owner, drafted with AI assistance):** the daily run is skipped when NetworkManager reports the connection as metered, such as the phone's hotspot, so backups do not use mobile data. It can be overridden for a manual run. Trade-off: no backups while the laptop is only on mobile data. A gap of more than 48 hours sets off the warning (D-26)

### D-26 – Missed-backup warning

- **Date:** 12th November 2026
- **Status:** Accepted (owner, 12th November 2026, from the owner's answers in phase3-plan.md, section 2, drafted with AI assistance)
- **Related:** T-20. Proposed SR-28. D-09, D-21
- **Context:** A backup that silently stops is found only when a restore is needed
- **Options considered:**
  1. **Desktop notification on the laptop only.** Does not work if the laptop's timer stops or the laptop is lost
  2. **A check on the NAS that emails the owner through OMV's notifications (D-09)**
- **Decision:** Option 2 (owner, 12th November 2026), with an optional laptop notification on failure. A timer on the NAS checks the age of the newest file in the repository, which needs no passphrase, and sends an email when it is older than 48 hours
- **Reasoning:** Works independently of the laptop, and reuses the email set up for SSD warnings
- **Trade-offs and residual risk:** False alarms when the laptop is off for more than 48 hours. Depends on OMV's email settings keeping working
- **Evidence:** Phase 3 test V-43, not yet run
- **Review trigger:** False alarms become frequent, or OMV's email stops working

### D-27 – Off-site copy of the backups

- **Date:** 12th November 2026
- **Status:** Accepted (owner, 12th November 2026, from the owner's answers in phase3-plan.md, section 2, drafted with AI assistance)
- **Related:** T-10, T-11. D-21. Document 01, section 14
- **Context:** The NAS is in one place, so a fire, theft or SSD failure would take the backups with it
- **Options considered:**
  1. **No off-site copy for now**, as an accepted risk
  2. **An external USB drive** copied to from time to time and kept elsewhere
  3. **An encrypted Borg copy at a hosted service**, which brings back a third party (objective O-1)
- **Decision:** Option 1 (owner, 12th November 2026)
- **Reasoning:** Phase 3 focuses on a working, tested backup first
- **Trade-offs and residual risk:** The laptop and the NAS together are the only copies. If both are lost at once, the data is lost
- **Evidence:** Not applicable
- **Review trigger:** The 5th January 2027 review, or a drive becomes available

### D-28 – SD card image taken remotely

- **Date:** 12th November 2026
- **Status:** Accepted (owner, 12th November 2026, from the owner's answers in phase3-plan.md, section 2, drafted with AI assistance)
- **Related:** T-14, T-18. D-06, D-17. phase3-plan.md, section 5
- **Context:** The NAS can no longer be reached physically, so the SD card cannot be removed and imaged. The most recent image is from 2nd November 2026, before the Phase 1 changes
- **Options considered:**
  1. **The `openmediavault-backup` plugin.** Made for running systems, but it comes from omv-extras and needs an SR-15 review
  2. **`dd` over SSH.** Nothing installed, but the card is copied while in use
- **Decision:** Option 2 (owner, 12th November 2026). Run by the owner, as `dd` is not in Claude Code's sudo rule (D-02). The image is written to the SSD first, its SHA-256 hash recorded, then copied to the laptop over Tailscale and the hash checked again
- **Reasoning:** No new software on the NAS, and it works without physical access
- **Trade-offs and residual risk:** The copy is taken while the system runs, so a restore boots like after a power cut: usually fine, not guaranteed. A restore still needs physical access to write the card. The image holds the NAS's WireGuard and Tailscale keys and SSH host keys (D-17), so it is kept where only the owner can reach it and is not put in the Borg backup
- **Evidence:** Image date and hash recorded in document 05, section 7
- **Review trigger:** A restore from an image fails, or physical access becomes possible again
- **Change, 12th November 2026 (owner request, drafted with AI assistance):** Claude Code takes the image, using the D-02 sudo rule change, when the owner approves it for a session. The image is compressed on the NAS and sent straight to the laptop over SSH through Tailscale, so nothing is written to the NAS. This replaces writing it to the SSD first. It is checked on the laptop with gzip's own check, the uncompressed size against the card's size, and a SHA-256 hash recorded in document 05, section 7 (phase3-changes.md, section 2)

### D-29 – What the phone backs up

- **Date:** 15th November 2026
- **Status:** Accepted (owner, 15th November 2026, from the owner's answers in phase3-phone-plan.md, section 2, drafted with AI assistance)
- **Related:** T-08, T-09, T-10. D-22, D-30, D-31. phase3-phone-plan.md, sections 1, 2.1, 2.5 and 2.6
- **Context:** The owner wants the phone's photos, files, apps, app data and settings backed up to the NAS, with nothing sent to Google or another cloud service. The phone runs stock Android 16, is not rooted, and GrapheneOS and LineageOS do not support it. Without root, Android lets no app read another app's data, `adb backup` skips the data of almost all current apps, and Shizuku has only `adb`'s rights
- **Options considered:**
  1. **Google's built-in backup** for app data and settings. Covers the most, but goes to the owner's Google account. Not acceptable to the owner
  2. **Root the phone** and use Neo Backup. Covers everything, but needs the bootloader unlocked (wipes the phone), weakens its protection if lost or stolen, and often stops banking apps
  3. **Shared storage and each app's own export, no cloud.** Photos, all shared-storage folders, and app exports written into a synced `Backups` folder. A list of installed apps for reinstalling. Data of apps with no export is not backed up
- **Decision:** Option 3 (owner, 15th November 2026). `photos`: `DCIM/Camera`, `Pictures/Screenshots` and other `Pictures` folders. `files`: every other shared-storage folder except `Android`, thumbnails and caches, plus WhatsApp's folder under `Android/media` (its nightly local backup and received media). WhatsApp's end-to-end encrypted backup is turned on, with its 64-digit key in the password manager. A list of installed apps (`pm list packages -3`) is saved by the daily job, or by the laptop over USB with `adb` if Android blocks it, with the phone's settings values (`settings list`) saved by the laptop now and then. No app install files. Google's backup is turned off. The phone is not rooted
- **Reasoning:** Keeps everything on hardware the owner controls. WhatsApp, the app that matters most, writes a restorable local backup. Rooting costs more security than it gains
- **Trade-offs and residual risk:** Accepted gap: data of apps without an export is lost if the phone is lost. Settings are saved as values, restored by hand or with `adb`, not automatically. Whether WhatsApp writes its local backup with no Google account linked is checked on the phone (V-50)
- **Evidence:** Phase 3 part 2 tests V-46, V-50, not yet run
- **Review trigger:** Moving to a phone that GrapheneOS or LineageOS supports (Seedvault then covers apps, app data and settings without root), or WhatsApp stops writing local backups

### D-30 – Phone backup tool, account and key limits

- **Date:** 15th November 2026
- **Status:** Accepted (owner, 15th November 2026, from the owner's answers in phase3-phone-plan.md, section 2, drafted with AI assistance)
- **Related:** T-05, T-08, T-12. D-14, D-16, D-23. phase3-phone-plan.md, section 2.2
- **Context:** The NAS is reachable only over Tailscale (D-16 change, 15th November 2026). The phone needs a way to copy files to it that adds no new service, and whose credentials cannot delete or read back what is stored
- **Options considered:**
  1. **Syncthing.** Easy, but a new service and two new ports on the NAS
  2. **An SFTP sync app** (FolderSync, Round Sync). No new service, but the SFTP server cannot refuse overwrites or reading back
  3. **Termux with `rsync` over SSH, limited by `rrsync`.** No new service, open source, and `rrsync` can make the key write-only, without deletes, and without overwrites
- **Decision:** Option 3 (owner, 15th November 2026). Termux and Termux:API from F-Droid, with `openssh` and `rsync`. `rsync` over SSH through the Tailscale app, to the existing SSH server, the NAS named by its Tailscale address in Termux's SSH settings. A dedicated `<PHONE-USER>` per device, made in OMV: no password, key login only, no sudo, in `_ssh`. Two keys made in Termux with no passphrase, one per folder, each limited in `authorized_keys` with `restrict`, `from=` (the phone's Tailscale address) and a forced `rrsync` command: `rrsync -wo -no-del -no-overwrite <DEVICE-PATH>/photos` and `rrsync -wo -no-del <DEVICE-PATH>/files`. Folders `<SSD-MOUNT>/devices/<DEVICE>/photos` and `.../files`, owned by that account, mode 700, not shared over SMB. The same pattern is repeated for future devices
- **Reasoning:** A stolen or compromised phone cannot read the backups back, delete them, or change existing photos, and nothing new listens on the NAS
- **Trade-offs and residual risk:** The `files` key can overwrite a document with the same name, covered by snapshots (D-31). The keys have no passphrase, so they are protected only by Termux's private storage and the phone's lock. The `rrsync` options are checked against the NAS's version with `rrsync -h` before the lines are written. Without a chroot, the account can read other files its permissions allow, checked by V-45
- **Evidence:** Phase 3 part 2 test V-45, not yet run
- **Review trigger:** The phone is lost or replaced (remove its keys and account), or `rrsync` changes its options

### D-31 – Phone backup schedule, encryption, deleted files and restores

- **Date:** 15th November 2026
- **Status:** Accepted (owner, 15th November 2026, from the owner's answers in phase3-phone-plan.md, section 2, drafted with AI assistance)
- **Related:** T-05, T-09, T-10, T-20. D-06, D-15, D-26. phase3-phone-plan.md, sections 2.3 and 2.4
- **Context:** The phone's copies need a schedule that avoids mobile data, a way to recover from overwrites, and a restore path that works with write-only keys
- **Decision (owner, 15th November 2026):**
  - **Schedule:** daily, with `termux-job-scheduler` set to Wi-Fi only and charging only. Termux is exempted from battery optimisation. The job exits without sending if the NAS cannot be reached
  - **Encryption:** no extra encryption on the phone. The SSD is encrypted (D-06). WhatsApp's and other apps' exports that hold secrets are encrypted by the apps themselves
  - **Deleted on the phone:** kept on the NAS, as the keys cannot delete. Old files are cleared by hand on the NAS
  - **Overwrites:** daily read-only Btrfs snapshots of `<SSD-MOUNT>/devices` on the NAS (the SSD is Btrfs, D-15), kept 14 days, from a new timer on the NAS
  - **Missed backups:** the missed-backup check (D-26) also checks the newest file in each device's folders and warns after 7 days without a new file
  - **Restores:** copied from the NAS by the administrator to the laptop, then to the phone over USB
- **Reasoning:** Photos stay viewable on the NAS and easy to restore. The snapshots cover the one write the keys allow
- **Trade-offs and residual risk:** Copies are readable by the NAS administrator while the SSD is unlocked. Snapshots use SSD space for 14 days. A phone that is rarely charged on Wi-Fi is backed up rarely, which the 7-day warning catches
- **Evidence:** Phase 3 part 2 tests V-46 to V-49, not yet run
- **Review trigger:** The SSD fills, or the phone's backup pattern changes

### D-32 – Commands on the phone from the laptop's Claude Code session

- **Date:** 16th November 2026
- **Status:** Accepted (owner, 16th November 2026, drafted with AI assistance)
- **Related:** T-07, T-08, T-13, T-16. D-02, D-14, D-30. Phase 3 part 2 tests V-45 to V-50
- **Context:** Typing commands in Termux on the phone is slow and error-prone, and sending scripts to it needed Taildrop, email or a firewall change on the laptop. The owner wants the Claude Code session on the laptop, which already works under this project's rules (D-02, CLAUDE.md), to run commands on the phone directly
- **Options considered:**
  1. **Claude Code installed in Termux (Node and npm).** Light, but Termux is not a standard Linux and Claude Code is not built for it, so parts break and updates are unsupported. Instructions would still be typed on the phone
  2. **A third-party install script or patched build from GitHub.** Easy, but unreviewed code would run with the Claude login and full access to Termux, the phone's NAS keys and shared storage
  3. **Ubuntu inside Termux (`proot-distro`) with the official Claude Code install.** Supported install, but 1 to 2 GB, slower, no Termux commands inside it, not a security boundary, and instructions still typed on the phone
  4. **Controlling the laptop session from the phone (Remote Control or claude.ai).** Nothing new on the phone, but it cannot run commands on the phone
  5. **An SSH server in Termux, used from the laptop's Claude Code session.** Termux's own `openssh` package. The laptop session runs commands with `ssh` and reads the output itself
  6. **Wireless ADB over Tailscale.** Runs as Android's `shell` user, not Termux, so no `rsync`, keys or Termux commands, and pairing resets often
- **Decision (owner, 16th November 2026):** Option 5, set up as follows:
  - **On demand only:** the owner starts `sshd` in Termux when a session needs it and stops it with `pkill sshd` afterwards. Nothing listens on the phone the rest of the time
  - **Listening address:** Termux's port 8022, bound to the phone's Tailscale address only (`ListenAddress`), so it is not reachable on the home Wi-Fi or mobile network, and does not start if Tailscale is off
  - **Login:** key only. Password and keyboard-interactive login off. Agent, TCP and X11 forwarding and tunnels off
  - **Key:** a new `ed25519` key on the laptop used only for the phone, in the phone's `authorized_keys` with `from=` (the laptop's Tailscale address) and `no-agent-forwarding,no-port-forwarding,no-X11-forwarding`. The phone's host key fingerprint is checked by the owner on first connection
  - **Network:** a Tailscale ACL rule allowing only the laptop to reach the phone on tcp 8022 (D-14 change)
  - **Use:** as D-02. Each session is approved by the owner in advance with its purpose. Read-only unless the owner approves a specific change. No change to the phone's NAS keys, the backup script or the schedule without a separate approval, logged in document 05, section 7. Raw output stays on the laptop under the evidence rules
- **Reasoning:** The smallest change that gives command execution on the phone. It adds no third-party code, keeps instructions, approvals and evidence handling in the one session that already follows the project's rules, and can be switched off with one command
- **Trade-offs and residual risk:** A new listening port on the phone while `sshd` runs. Anyone with the laptop's key and the laptop's Tailscale address gets a shell as the Termux user, which can read the phone's shared storage and use the two NAS keys; their limits (D-30) still apply, and Termux cannot read other apps' data. A compromised laptop therefore reaches the phone while `sshd` is running. Android may stop `sshd` in the background, which is acceptable for on-demand use. The phone is no longer only a client on the tailnet
- **Evidence:** New test V-51, not yet run: the laptop key works; password login is refused; the port is not reachable on the phone's Wi-Fi address or from another tailnet device; nothing listens after `pkill sshd`
- **Review trigger:** Not used for 3 months (remove the key and the ACL rule), the laptop is replaced or compromised, or the phone is lost or replaced


## 6. Candidate decisions to expect

These are not decisions yet. They are placeholders so that each one is recorded when it is made.

- Remote access: Tailscale first, then self-hosted WireGuard, and how they are compared (Phase 1 and 2). New device control for Tailscale decided: D-14
- ~~File sharing protocol and version (document 01, section 6.2 still says to be decided)~~ Decided: D-05
- ~~Admin interface: HTTP or HTTPS, and which networks may reach it~~ Decided: D-04
- ~~SSD encryption, and how it is unlocked after a reboot~~ Decided: D-06
- Backup tool for phone and computer, and how clients are prevented from deleting their own backups
- Photo application to replace Google Photos, and whether it runs on the NAS (a new service to review, T-13, SR-15)
- Monitoring and alerting approach (SSD warnings decided: D-09)
- ~~Network isolation: VLAN or guest network if the router supports it, otherwise accept the risk~~ Decided: D-11
- ~~Update routine, including unattended security updates~~ Decided: D-08
- Case vendor software: keep, restrict or remove
- ~~NAS network connection: Wi-Fi or Ethernet to the router, and which unused radios and interfaces are disabled (Bluetooth, Wi-Fi if Ethernet is chosen, the direct troubleshooting link to the laptop). Related: T-07, T-13, T-18 (Phase 1)~~ Decided: D-10
- Offsite copy: cloud provider and how it is chosen (for example certification to ISO/IEC 27001, 27017 and 27018, and where the data is stored), with encryption before upload and where that key is kept. Related: T-10, T-15 (Phase 3)
- Offsite copy protection: immutable or versioned storage (object lock or append-only access) and a separate access key per device with no delete rights, so a compromised client cannot delete backups. Related: T-05, T-09 (Phase 3)

## 7. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.1 | Not recorded | Template created | Structure agreed before Phase 0 |
| 0.2 | 27th October 2026 | D-01: added option 3, draft recommendation, reasoning and trade-offs (drafted with AI assistance, decision still open) | Preparation for Phase 0 |
| 0.3 | 27th October 2026 | Header: link to document 05 and remove template note (drafted with AI assistance) | Out-of-date header |
| 0.4 | 27th October 2026 | D-01 accepted: option 3, with the list of known earlier changes | Owner decision before Phase 0 |
| 0.5 | 27th October 2026 | D-01: install option, network connection and case software confirmed in the list of known earlier changes | Owner answers |
| 0.6 | 27th October 2026 | D-01: SSH login method confirmed as password | Owner answer |
| 0.7 | 27th October 2026 | D-01: no updates installed since setup. List of known earlier changes complete | Owner answer |
| 0.8 | 27th October 2026 | Revision log: date for 0.1 marked as not recorded | Owner confirmed the date was not recorded |
| 0.9 | 28th October 2026 | D-01: SD card image date and SHA-256 hash added to the evidence line | Image taken and verified |
| 0.10 | 29th October 2026 | D-02 drafted: temporary SSH access for Claude Code, status Proposed (drafted with AI assistance) | Record the access set up during Phase 0 |
| 0.11 | 29th October 2026 | D-01: item 6 corrected, the case control software is not installed (drafted with AI assistance) | Owner confirmed during Phase 0 |
| 0.12 | 30th October 2026 | D-03 drafted: vulnerability monitoring dashboard, three options, status Proposed. Header link to document 03 (drafted with AI assistance) | Owner request for 12-hourly vulnerability checks |
| 0.13 | 30th October 2026 | Section 6: candidate decisions added for the NAS network connection and the offsite copy (drafted with AI assistance) | Owner request |
| 0.14 | 2nd November 2026 | D-02 and D-03 accepted, D-02 key kept until the Phase 1 final checks, D-03 key on a separate account. D-04 to D-13 recorded. Section 6: decided items marked (drafted with AI assistance) | Owner decisions for Phase 1 |
| 0.15 | 2nd November 2026 | D-02: proposed sudo rule for the read-only test commands added, not yet accepted (drafted with AI assistance) | Owner wants Claude Code to run approved tests on the NAS |
| 0.16 | 2nd November 2026 | D-02: sudo rule accepted, added and tested | Owner added the rule |
| 0.17 | 3rd November 2026 | D-09: alert method postponed. D-10: option 2 applies, no cable reaches the router. D-11: router check done, no isolation available (drafted with AI assistance) | Owner checks and decisions |
| 0.18 | 4th November 2026 | D-14 recorded: device approval for Tailscale, Tailscale SSH not used (drafted with AI assistance) | Owner decision before the Tailscale set-up |
| 0.19 | 5th November 2026 | D-03: set up, access over Tailscale after the review trigger (drafted with AI assistance) | Owner decision |
| 0.20 | 5th November 2026 | D-03: Raspberry Pi rebuilds listed as manual checks, KEV check and notifications added (drafted with AI assistance) | Owner request after the first run |
| 0.21 | 5th November 2026 | D-15 recorded: Btrfs, SMB encryption required, first share for media. Section 6: photo application added as a candidate decision (drafted with AI assistance) | Owner decisions for checklist section 8 |
| 0.22 | 6th November 2026 | D-02: key limited to the laptop's Tailscale address instead of its LAN address (drafted with AI assistance) | Owner decision |
| 0.23 | 6th November 2026 | D-09: alert set-up deferred out of Phase 1 | Owner decision |
| 0.24 | 9th November 2026 | D-02: key kept after the Phase 1 final checks, for Phase 2 (drafted with AI assistance) | Owner decision |
| 0.25 | 9th November 2026 | D-16 to D-20 drafted as Proposed from the owner's Phase 2 answers (drafted with AI assistance) | Phase 2 plan, section 2 |
| 0.26 | 9th November 2026 | D-16 to D-20 accepted | Owner decision |
| 0.27 | 9th November 2026 | D-19: how the address script reports a new address, and the reconnection target (drafted with AI assistance) | Owner decision |
| 0.28 | 12th November 2026 | D-16: Tailscale kept, WireGuard on the home network for the laptop only. D-19: not implemented. D-20: peers and untested steps noted (drafted with AI assistance) | Owner decision, Phase 2 closed |
| 0.29 | 12th November 2026 | D-21 to D-28 drafted from the owner's Phase 3 answers and accepted by the owner (drafted with AI assistance) | phase3-plan.md, section 2, owner decision |
| 0.30 | 12th November 2026 | D-02: `dd` of the SD card added to the sudo rule. D-28: Claude Code takes the image, sent straight to the laptop (drafted with AI assistance) | Owner request |
| 0.31 | 12th November 2026 | D-22: three more paths left out after checking the laptop's applications (drafted with AI assistance) | Laptop check |
| 0.32 | 13th November 2026 | D-25: backups skipped on metered connections (drafted with AI assistance) | Owner decision |
| 0.33 | 15th November 2026 | D-22: the VirtualBox folder left out after the first full backup. Revision rows 0.31 and 0.32 moved to the end of the table (drafted with AI assistance) | Owner decision |
| 0.34 | 15th November 2026 | D-22: Zoom's cache left out after V-44, no laptop SSH host keys. D-16: the NAS is now reachable only over Tailscale (drafted with AI assistance) | Phase 3 tests, owner decision |
| 0.35 | 15th November 2026 | D-29 to D-31 recorded for the phone backups, accepted from the owner's answers in phase3-phone-plan.md. D-16: WireGuard to be turned off (drafted with AI assistance) | Owner decisions |
| 0.36 | 16th November 2026 | D-32 accepted: an on-demand SSH server in Termux so the laptop's Claude Code session can run commands on the phone (drafted with AI assistance) | Owner request |
| 0.37 | 17th November 2026 | D-23: guessable backup account name recorded as an accepted risk before publishing (drafted with AI assistance) | Owner decision |
