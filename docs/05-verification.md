# 05 – Verification

> **Status:** Draft v0.17 · Last updated: 31st October 2026
> **Author:** William Drummond
> **Related:** [01-scope-and-assets.md](01-scope-and-assets.md) (service inventory, phases, success criteria) · [02-threat-analysis.md](02-threat-analysis.md) (threat IDs) · [04-design-decisions.md](04-design-decisions.md) (D-01 baseline definition) · [traceability/requirements-matrix.csv](../traceability/requirements-matrix.csv)
> **Note:** The test list in section 4 is a suggested starting point. Add, remove or change tests to fit the real setup, and write each **expected result before running the test**. Replace anything in **[TODO]** or square brackets. Record meaningful changes in the revision log at the end.

---

## 1. Purpose

This document records how I check that things are as I believe them to be. It does two jobs:

1. **Baseline (Phase 0).** Measure the current system before any change, so later improvements can be shown with before-and-after evidence.
2. **Verification (Phase 1 onwards).** Show that each stage is complete and that each control works, in particular that access controls allow what they should and refuse what they should not.

Verification here means collecting evidence that specific controls held up against specific tests. It does not prove the system is secure.

## 2. Conventions

### 2.1 Identifiers

| Item | Format | Example |
|---|---|---|
| Test | V-xx | V-01 |
| Finding | FND-xx | FND-03 |
| Threat | T-xx (document 02) | T-03 |
| Requirement | SR-xx (document 03) | SR-07 |

### 2.2 Evidence storage

- Sanitised evidence goes in `evidence/phase0/` (and `evidence/phase1/` and so on), one file per test, named `V-xx_short-description.ext`
- Raw, unsanitised output stays outside the repository and is never committed
- Each evidence file starts with a header: test ID, date, command or tool and version, where it was run from
- SD card image taken before Phase 0: 28th October 2026, 08:17 UK time, SHA-256 `090dcc27c844456240e0279f80bf0bb753c488bd6cf53fd605fb20f9ab3f741d` (three checks matched: hash recorded during imaging, decompressed image, card)

### 2.3 Authorisation

All testing is performed against my own equipment on my own network.

### 2.4 Sanitisation checklist (before every commit)

- [ ] No real IP addresses, hostnames, usernames or MAC addresses (use documentation placeholders such as `192.0.2.x` and `nas.example`)
- [ ] No keys, tokens or passwords
- [ ] No chosen port numbers (for example the WireGuard port). Placeholders only
- [ ] Exact patch-level versions reduced to major versions, or published only after the related findings are fixed
- [ ] Screenshots reviewed for hidden details (title bars, notifications, tabs)
- [ ] Raw output kept outside the repository

## 3. Before starting Phase 0

- [x] Image of the SD card taken, date and hash recorded (section 2.2)
- [x] Baseline definition decided and recorded as D-01 in document 04
- [x] Expected results written for every test in section 4
- [x] `evidence/phase0/` created and raw output location outside the repository chosen
- [x] Router access confirmed
- [x] Second LAN device and an outside network (for example mobile data) available for scanning
- [x] No sensitive data on the NAS during the baseline

## 4. Phase 0 test plan

Phase 0 is observation only. If something serious is found, record it first, then fix it and log the change with a timestamp.

`<NAS-IP>` is a placeholder. Use the real address only in the private raw output.

"Pass or fail" records whether the control held, not whether the expected result was predicted correctly. A test whose expected result is a finding is recorded as Fail when the finding is confirmed.

| Test ID | Threat | What it checks | Tool and command | Run from | Expected result | Actual result | Pass or fail | Evidence |
|---|---|---|---|---|---|---|---|---|
| V-01 | T-02, T-13 | Open TCP ports | `nmap -sS -p- <NAS-IP>` | Second LAN device | Only 22 and 80 open, plus 445 if SMB is enabled (file sharing is still to be decided, document 01, section 6.2). Any other open TCP port, including one opened by the case control software, is a finding | Run 29th October 2026, 13:17 UK time, from the laptop over Wi-Fi. Open: 22 (ssh), 80 (http), 111 (rpcbind) and 5355 (LLMNR). All other TCP ports closed. 111 and 5355 are outside the expected result (FND-04). No port for SMB or for case control software. Run as a connect scan (`-sT`) instead of `-sS`, see section 7 | **[TODO]** (owner) | `evidence/phase0/V-01_tcp-scan.txt` |
| V-02 | T-13 | Open UDP ports | `sudo nmap -sU --top-ports 100 <NAS-IP>` | Second LAN device | Every port reported `open` or `open\|filtered` is matched to a known service, or recorded as unexplained (for example mDNS on 5353 if a discovery service runs). Unexplained ports are findings | Run 29th October 2026, 13:43 UK time, from the laptop over Wi-Fi. Open: 111/UDP (rpcbind) and 5353/UDP (mDNS, reported as zeroconf). The other 98 ports closed, none `open\|filtered`. Both match known services from V-04, so no unexplained ports. LLMNR (5355/UDP) and the DHCPv6 client (546/UDP) are not in the top 100 UDP ports and were not covered by this scan | **[TODO]** (owner) | `evidence/phase0/V-02_udp-scan.txt` |
| V-03 | T-02 | Service versions | `nmap -sV <NAS-IP>` | Second LAN device | Each detected service matches an installed package (cross-check with V-04). No updates have been installed since setup (D-01), so versions behind current releases are expected. Any service with pending updates in V-10, or past end of support, is a finding. Exact versions stay in the private raw output until fixed | Network scan 29th October 2026, 13:17 UK time, from the laptop: SSH is OpenSSH 10.x (Debian build), HTTP is nginx with no version shown, rpcbind reports RPC versions 2 to 4. 5355 is outside the default port list and was not version-scanned (identified as LLMNR by V-01 and V-04). Installed versions from the collection script (28th October 2026, 12:45 UK time): openmediavault 8.x, openssh-server 10.x, samba 4.x, matching the SSH service. openmediavault, which serves the web interface behind nginx, has a pending update in V-10 (FND-06). Major versions only in the repository | **[TODO]** (owner) | `evidence/phase0/V-03_service-versions.txt`, `V-03_installed-versions.txt` |
| V-04 | T-13 | Listening sockets on the NAS | `ss -tulpn` | The NAS | Every listening socket maps to a row in document 01, section 6.3, including the case control software, which is installed (D-01). Record whether each service listens on all interfaces or on localhost only. The Ethernet port is not normally connected, so services are reached over Wi-Fi. Anything unexplained is a finding | Run 28th October 2026, 12:45 UK time. On all interfaces (IPv4 and IPv6): SSH on 22/TCP, the OMV web interface (nginx) on 80/TCP, rpcbind on 111/TCP and UDP, LLMNR (systemd-resolved) on 5355/TCP and UDP, and mDNS (Avahi) on 5353/UDP plus one random high UDP port. DHCPv6 client (NetworkManager) on 546/UDP, link-local address. Localhost only: DNS stub resolver (53) and chrony (323). SMB not running (smbd and nmbd inactive and disabled). Bluetooth service running. No service or listening socket for the case control software was seen. The owner confirmed on 29th October 2026 that it is not installed, so D-01 has been corrected. rpcbind, LLMNR, mDNS and the DHCPv6 client have no completed row in document 01, section 6.3 (FND-04) | **[TODO]** (owner) | `evidence/phase0/V-04_listening-sockets.txt`, `V-04_running-services.txt`, `V-04_smb-state.txt` |
| V-05 | T-02, T-13, T-14 | System audit | `sudo lynis audit system` | The NAS | Hardening index and every warning recorded. No target score at baseline | Run 28th October 2026, 12:45 UK time (Lynis 3.x, `lynis audit system --quick`). Hardening index 63, 269 tests performed, 1 warning (KRNL-5830, reboot of the system most likely needed, not yet investigated **[TODO]**) and 51 suggestions | **[TODO]** (owner) | Summary only. The sanitised output stays outside the repository, as it is long and contains exact versions |
| V-06 | T-10, T-18 | SSD health | `sudo smartctl -a /dev/nvme0` | The NAS | Critical warning 0, available spare above its threshold and no media or data integrity errors. Percentage used and power-on hours recorded, as the SSD is recycled (document 01, section 6.1) | Run 28th October 2026, 12:45 UK time. SMART overall health PASSED, critical warning 0x00, available spare 100% (threshold 10%), media and data integrity errors 0. Percentage used 0%, power-on hours 625. Also recorded: 179 unsafe shutdowns and 151,204 error log entries. Checked on 29th October 2026: the error log holds one entry type, "Invalid Field in Command" with no disk location, meaning commands the drive rejected, not media errors. The SSD was previously used in a laptop (14,580 power cycles), so the unsafe shutdown count cannot be attributed to the NAS. 179 is kept as the baseline for later comparison | **[TODO]** (owner) | `evidence/phase0/V-06_ssd-health.txt` |
| V-07 | T-03, T-19 | Router exposure | Router admin page | Router | No port forwards to the NAS, no DMZ host set and UPnP off | Checked by the owner in the router admin page, confirmed 30th October 2026. No port forwarding rules, no DMZ host, DDNS off. UPnP is on, with no mappings (FND-07). Not behind CGNAT. Also noted: the NAS has public IPv6 addresses from the router's prefix (`ip -6 addr show scope global`), so the router's IPv6 firewall setting matters for V-08 **[TODO]** | **[TODO]** (owner) | Owner observation, no screenshot |
| V-08 | T-03 | External exposure | Same Nmap scan as V-01, against the public IPv4 address and, if the outside network has IPv6, each public IPv6 address of the NAS. IPv6 added on 30th October 2026 (owner confirmed), because V-07 showed the NAS has public IPv6 addresses | Outside network (mobile data) | No NAS port reachable over IPv4 or IPv6. Record whether the connection is behind CGNAT, as this affects how the result can be read (V-07: not behind CGNAT). Record the router's IPv6 firewall setting | | | |
| V-09 | T-04 | SSH configuration | `sudo sshd -T` | The NAS | Values of `permitrootlogin`, `passwordauthentication`, `pubkeyauthentication` and any `allowusers` or `allowgroups` recorded. Password login is expected to be enabled, as it is used today (D-01). Root login or password login enabled is a finding | Run 28th October 2026, 12:45 UK time. `permitrootlogin yes`, `passwordauthentication yes`, `pubkeyauthentication yes`, `kbdinteractiveauthentication no`, `allowgroups root` and `_ssh`, no `allowusers`. Listens on 22/TCP on all interfaces. Root login and password login are enabled (FND-02, FND-03). Checked on 29th October 2026: the root password is locked (`passwd -S` shows `L`), so root cannot log in with a password, and `/root/.ssh/authorized_keys` exists. Reviewed on 30th October 2026: the file is empty (0 bytes, no keys), so root cannot currently log in with a key either | **[TODO]** (owner) | `evidence/phase0/V-09_sshd-config.txt` |
| V-10 | T-02, T-14 | Pending updates | `apt list --upgradable` | The NAS | Number of pending updates recorded, with security updates listed separately. Pending updates, including security updates, are expected as none have been installed since setup (D-01). Any pending security update is a finding | Run 28th October 2026, 12:45 UK time, after the owner ran `apt update`. 12 pending updates, none from a security suite. They include openmediavault (minor version) and Raspberry Pi packages. Unattended upgrades are enabled (`APT::Periodic::Unattended-Upgrade "1"`) and have run (3 log files), but the logs show no packages upgraded, which matches D-01 (checked 29th October 2026) | **[TODO]** (owner) | `evidence/phase0/V-10_pending-updates.txt`, `V-10_pending-security-updates.txt`, `V-10_package-list-age.txt` |
| V-11 | T-12 | Share permissions | OMV share and ACL review | OMV interface | Only intended accounts have access and there is no guest access. If no shares exist yet, record that | Checked by the owner in the OMV interface, reported 31st October 2026. No shares exist yet, so there are no share permissions or ACLs to review. SMB shows as enabled, minimum protocol SMB2, guest access not allowed. This differs from V-04 (28th October 2026: smbd and nmbd inactive and disabled) and V-01 (29th October 2026: port 445 closed). Not yet explained **[TODO]** | **[TODO]** (owner) | None, owner observation |
| V-12 | T-01, T-12 | Accounts | User and group list, sudo rights | The NAS | Only expected accounts have a login shell, and only the administrator account has sudo rights. One account is used for both administration and daily use (D-01), so this is expected to be a finding | Run 28th October 2026, 12:45 UK time. Accounts with a login shell: root and one user account (`<USER>`, uid 1000). `<USER>` is in the `sudo`, `adm` and `_ssh` groups. The OMV admin group contains only the built-in `admin` web account. One account is used for both administration and daily use, as expected (FND-05). The account for Claude Code was created after this run (section 7, D-02) | **[TODO]** (owner) | `evidence/phase0/V-12_login-accounts.txt`, `V-12_privileged-groups.txt`, `V-12_sudoers.txt` |
| V-13 | T-01 | Default credentials | Check whether the publicly documented default OMV admin password is still in use | OMV interface | The default is still in use (known before testing). Expected to be a finding: record it first, then change the password and log the change with a timestamp | Login with the publicly documented default OMV admin credentials succeeded (28th October 2026, 08:45 UK time). Password changed at 09:00 and the re-test was refused, see section 7 | Fail | None, owner observation |
| V-14 | T-11 | Encryption status | `lsblk -f` | The NAS | Whether the SSD is encrypted is recorded. An unencrypted SSD holding data is a finding | Run 28th October 2026, 12:45 UK time. No disk is encrypted. The root file system (ext4) is on the SD card. The SSD has no partitions or file system, so it holds no data yet. Any data stored on the NAS at baseline is on the unencrypted SD card. The owner decided on 31st October 2026 that this is a finding (FND-08) | **[TODO]** (owner) | `evidence/phase0/V-14_block-devices.txt` |
| V-15 | T-10 | Existing copies of data | Manual check | n/a | For each data type in document 01, section 7.1, whether another copy exists is recorded. Data held only on the NAS is a finding | Reported by the owner, 31st October 2026. Personal photos and documents (A-01), project and portfolio files (A-03), media and some identity documents: other copies exist, including in cloud storage and on other devices. Other identity documents, financial documents, phone backups and computer backups: no other copy. The SSD holds no data (V-14), no sensitive data is on the NAS (section 3), and document 01, section 7.1, does not place the data types without a copy on the NAS at baseline, so no finding is raised | **[TODO]** (owner) | None, owner observation |

## 5. Phase 0 findings

One row per finding. Every finding links to a test, a threat and, once it exists, a requirement.

| ID | Test | Observation | Threat | Effect on rating | Resulting requirement | Status |
|---|---|---|---|---|---|---|
| FND-01 | V-13 | The publicly documented default OMV admin password was still in use. The password was changed and a re-test with the default credentials failed to log in | T-01 | None. The draft rating stays (owner decision) | **[TODO]** (document 03 not yet written) | Treated |
| FND-02 | V-09 | SSH permits root login (`permitrootlogin yes`). The root password is locked and `/root/.ssh/authorized_keys` is empty (reviewed 30th October 2026), so root has no working login method today. The setting still allows root login if a password or key is added later | T-04 | **[TODO]** (owner decision) | **[TODO]** (document 03 not yet written) | Open |
| FND-03 | V-09 | SSH password login is enabled (`passwordauthentication yes`). Expected, as password login is used today (D-01) | T-04 | **[TODO]** (owner decision) | **[TODO]** (document 03 not yet written) | Open |
| FND-04 | V-04 | Network-facing services that are not in the service inventory (document 01, section 6.3) listen on all interfaces: rpcbind (111/TCP and UDP), LLMNR (5355/TCP and UDP), mDNS (5353/UDP) and a DHCPv6 client (546/UDP, link-local) | T-13 | **[TODO]** (owner decision) | **[TODO]** (document 03 not yet written) | Open |
| FND-05 | V-12 | One account is used for both administration and daily use, and has sudo rights. Expected (D-01) | T-01, T-12 | **[TODO]** (owner decision) | **[TODO]** (document 03 not yet written) | Open |
| FND-06 | V-03, V-10 | openmediavault, which serves the web interface, has a pending update. No pending update is listed from a security suite | T-02, T-14 | **[TODO]** (owner decision) | **[TODO]** (document 03 not yet written) | Open |
| FND-07 | V-07 | UPnP is enabled on the router. No mappings are present, but any device on the LAN, including the NAS, could open a port to the internet without a visible port forwarding rule | T-03, T-19 | **[TODO]** (owner decision) | **[TODO]** (document 03 not yet written) | Open |
| FND-08 | V-14 | No disk is encrypted. The SD card holds the system and any data stored on the NAS, and can be removed and read on another computer. The SSD is also unencrypted, but holds no data yet | T-11 | **[TODO]** (owner decision) | **[TODO]** (document 03 not yet written) | Open |

Status values: **Open**, **Treated**, **Accepted**.

## 6. Rating changes from Phase 0

Where evidence changes a rating in document 02, record it here and in document 02's revision log.

| Threat | Draft rating | New rating | Reason | Test ID |
|---|---|---|---|---|
| | | | | |

## 7. Phase 0 log

Written as the work happens, not afterwards. A few lines per test is enough.

| Date | Test ID | Command or action | What happened | Deviation or note |
|---|---|---|---|---|
| 28th October 2026, 08:45 UK time | V-13 | Logged in to the OMV interface with the publicly documented default admin credentials | Login succeeded. Recorded as FND-01 | No evidence saved. Owner observation only |
| 28th October 2026, 09:00 UK time | V-13 | Changed the OMV admin password | The default password is no longer in use | Change made during Phase 0, as section 4 allows for serious findings |
| 28th October 2026, 09:03 UK time | V-13 | Re-test: tried to log in to the OMV interface with the default admin credentials | Login refused | No evidence saved. Owner observation only |
| 28th October 2026, 12:40 UK time (logged at this time, exact time not recorded) | V-04, V-05, V-06, V-09, V-10, V-12, V-14 | Ran `scripts/phase0-collect.sh` with `/` as the output folder | Collection ran as root and wrote its raw output into `/`. smartctl was installed. Lynis was not installed, so V-05 was recorded as skipped | Deviation: the script set the permissions of `/` to 700, so non-root users and services could no longer use the system. Caused by a defect in the script (it accepted an existing folder), now fixed |
| 28th October 2026, 12:40 UK time (logged at this time, exact time not recorded) | n/a | Recovery: NAS shut down, SD card mounted on the laptop, permissions of the root folder checked and restored, raw output moved off the NAS, NAS booted | Root folder showed 700 before the fix and was set back to 755. Access for the owner account restored | Change made during Phase 0 to undo the deviation. The output of this first run was deleted by the owner and not used. All script results come from the second run at 12:45 |
| 28th October 2026, 12:40 UK time (logged at this time, exact time not recorded) | V-05 | Installed Lynis | Lynis now installed | Change to the system made during Phase 0 so that V-05 can run. The owner ran `apt update` first, which also refreshed the package lists used by V-10 |
| 28th October 2026, 12:45 UK time (from the evidence file timestamps) | V-03, V-04, V-05, V-06, V-09, V-10, V-12, V-14 | Second run of `scripts/phase0-collect.sh`, fixed version, default output folder | All tests completed, including Lynis | Lynis wrote its log and report under `/var/log`. The owner recalled the run as 13:30. The evidence timestamps are used |
| 28th October 2026, time not recorded | V-03, V-04, V-05, V-06, V-09, V-10, V-12, V-14 | Raw output copied off the NAS to the raw evidence location on the laptop | Checked against `SHA256SUMS` on 29th October 2026 before sanitising: all 17 files matched | Deleted from the NAS afterwards (owner confirmed 29th October 2026, time not recorded) |
| 28th October 2026, 14:00 UK time | n/a | Created a separate NAS account for Claude Code: SSH group only, no sudo (D-02) | Account created | Change made during Phase 0, after the collection run, so it is not part of the V-12 baseline |
| Date and time not recorded | n/a | Installed an SSH public key for the Claude Code account, limited to the laptop's address with `from=`, with agent, port and X11 forwarding disabled | Key login refused at first because the `from=` address was wrong. Corrected, then key login worked | Change made during Phase 0 (D-02) |
| 29th October 2026, 10:55 UK time | n/a | Claude Code connected over SSH with the dedicated key, with the owner's approval, and ran read-only checks: `whoami`, `id`, a hostname check, `uptime` and `sudo -n true` | Logged in as the dedicated account, groups `users` and `_ssh` only, no sudo rights | No change made. `uptime` showed 2 users logged in. The owner confirmed on 31st October 2026 that both were their own sessions |
| 29th October 2026, 12:44 UK time | V-03, V-04, V-06, V-09, V-10, V-12, V-14 | Raw output sanitised on the laptop with `scripts/sanitise.py`. 13 files added to `evidence/phase0/`, with exact versions reduced to major versions | Sanitiser gaps found and fixed before publishing (Lynis log host IDs, SSD identifier, file system UUIDs) | No change to the NAS. V-05 output and the full V-09 output stay outside the repository |
| 29th October 2026, 13:17 UK time | V-01, V-03 | Claude Code ran `nmap -sT -p- <NAS-IP>` and then `nmap -sV <NAS-IP>` from the laptop, with the owner's approval. Raw output to the raw evidence location | Both completed in under 10 seconds each | Deviation: V-01 run as a connect scan (`-sT`) instead of `-sS`, which needs sudo. For finding open TCP ports the result is equivalent. A first run a few seconds earlier stamped its output in the laptop's time zone, so both scans were rerun with UK time and only the rerun is kept |
| 29th October 2026, 13:43 UK time | V-02 | Owner ran `sudo nmap -sU --top-ports 100 <NAS-IP>` from the laptop | Completed in about 104 seconds | An earlier run the same afternoon stamped its output in the laptop's time zone and was replaced by this rerun |
| 29th October 2026, time not recorded | V-04, V-06, V-09, V-10 | Owner ran read-only checks on the NAS: case control software, unattended upgrades configuration and logs, `passwd -S root`, the contents of `/root/.ssh/` and the SSD error log | Case control software not installed. Unattended upgrades enabled, no packages upgraded. Root password locked. `/root/.ssh/authorized_keys` exists. SSD error log holds command rejections only | No change made. Results recorded in section 4 |
| 30th October 2026, reported to Claude at 13:12 UK time | V-09 | Owner checked `/root/.ssh/authorized_keys` on the NAS: size, number of non-comment lines and key types, without printing any key data | 0 bytes, 0 lines, no keys | No change made. FND-02 and V-09 updated |
| 30th October 2026, confirmed to Claude at 14:59 UK time | V-07 | Owner checked the router admin page: port forwarding, DMZ, DDNS, UPnP and its mappings, and whether the connection is behind CGNAT. Owner also listed the NAS's global IPv6 addresses | No forwards, no DMZ, DDNS off, UPnP on with no mappings, not behind CGNAT. The NAS has public IPv6 addresses | No change made. FND-07 added |
| 31st October 2026, reported to Claude at about 09:30 UK time | V-07 | Owner decided not to take router screenshots | V-07 stays an owner observation | Deviation: the checklist asked for screenshots |
| 31st October 2026, reported to Claude at about 09:30 UK time | V-11 | Owner checked shares and SMB settings in the OMV interface | No shares. SMB shows as enabled, minimum protocol SMB2, guest access not allowed | No change reported. SMB differs from V-04 and V-01 and is not yet explained **[TODO]** |
| 31st October 2026, reported to Claude at about 09:30 UK time | V-14, V-15 | Owner recorded V-15 (corrected by the owner the same day), confirmed the SSD was wiped and reimaged before reuse (method not recorded), and decided the unencrypted SD card is a finding | FND-08 added | No change made |

## 8. Stage completion checks (Phase 1 onwards)

Each stage is complete when its criteria are verified, with evidence.

| Stage | Completion criterion | Verified by | Evidence | Date | Done |
|---|---|---|---|---|---|
| Phase 0 | All tests in section 4 run, findings logged, ratings reviewed | Owner review of sections 4, 5 and 6 **[TODO]**. 14 of 15 tests run (V-08 to do) | `evidence/phase0/` | **[TODO]** | [ ] |
| Phase 1 | **[TODO: write when requirements exist]** | | | | [ ] |
| Phase 2 | | | | | [ ] |
| Phase 3 | Restore test passed, including a copy that clients cannot overwrite | | | | [ ] |
| Phase 4 | Success criteria in document 01, section 13 all met | | | | [ ] |

## 9. Access control tests (Phase 1 onwards)

These show that access is allowed where it should be and refused where it should not be. Both directions matter. **[TODO: complete once requirements exist.]**

| Test ID | Who or what | Target | Expected | Actual | Evidence |
|---|---|---|---|---|---|
| V-20 | Approved device on the VPN | OMV admin interface | Access allowed | | |
| V-21 | Approved device on the LAN | OMV admin interface | Per the access rule **[TODO]** | | |
| V-22 | Device that is not approved | NAS services | Refused | | |
| V-23 | Internet, outside network, no VPN | Any NAS port | Nothing reachable | | |
| V-24 | Standard user account | OMV admin interface and SSH | Refused | | |
| V-25 | Backup account | Delete or overwrite existing backups | Refused | | |
| V-26 | Device removed from the VPN | NAS services | Refused after revocation | | |

## 10. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.1 | Not recorded | Template created with suggested Phase 0 tests | Structure agreed before Phase 0 |
| 0.2 | 27th October 2026 | Section 4: draft expected results for V-01 to V-15 (drafted with AI assistance, not yet confirmed) | Expected results must be written before tests run |
| 0.3 | 27th October 2026 | Header: correct matrix path and remove template note (drafted with AI assistance) | Out-of-date header |
| 0.4 | 27th October 2026 | Section 4: draft expected results updated with the known earlier changes in D-01 and confirmed by the owner (drafted with AI assistance) | Match D-01 and confirm before testing |
| 0.5 | 27th October 2026 | Revision log: date for 0.1 marked as not recorded | Owner confirmed the date was not recorded |
| 0.6 | 28th October 2026 | Sections 2.2 and 3: SD card image date and hash recorded, D-01 ticked | Image taken and verified |
| 0.7 | 28th October 2026 | Section 3: evidence location and router access ticked | Owner confirmed |
| 0.8 | 28th October 2026 | Section 3: scanning devices, outside network and no sensitive data ticked. All prerequisites complete | Owner confirmed |
| 0.9 | 28th October 2026 | V-13 result recorded (Fail), password change and re-test logged, FND-01 added as Treated, meaning of the Pass or fail column stated in section 4 | First Phase 0 test run by the owner |
| 0.10 | 28th October 2026 | Header version corrected (0.9 was not shown). Section 7: collection script run, the root folder permission deviation and its recovery, and the Lynis install logged | Record the deviation and the changes made during Phase 0 |
| 0.11 | 29th October 2026 | Section 4: actual results for V-03 (partial), V-04, V-05, V-06, V-09, V-10, V-12 and V-14 recorded from the sanitised evidence, pass or fail left for the owner. Section 5: FND-02 to FND-05 added as Open. Section 7: second collection run, Claude Code account, key and access test, and sanitising logged. Two TODOs resolved (drafted with AI assistance) | Results of the script-collected Phase 0 tests |
| 0.12 | 29th October 2026 | Section 4: V-01, V-02 and V-03 results recorded, and owner checks added to V-04, V-06, V-09 and V-10. Section 5: FND-02 updated, FND-06 added. Section 7: scans and owner checks logged, deletion from the NAS confirmed (drafted with AI assistance) | Network scans and owner answers |
| 0.13 | 29th October 2026 | Section 8: Phase 0 progress noted (drafted with AI assistance) | Track completion |
| 0.14 | 30th October 2026 | Section 4 (V-09), section 5 (FND-02) and section 7: root `authorized_keys` review recorded (drafted with AI assistance) | Close open item |
| 0.15 | 30th October 2026 | Section 4: V-07 result recorded, IPv6 exposure noted for V-08. Section 5: FND-07 added. Sections 7 and 8 updated (drafted with AI assistance) | Owner results |
| 0.16 | 30th October 2026 | Section 4, V-08: IPv6 scan added, confirmed by the owner (drafted with AI assistance) | V-07 showed the NAS has public IPv6 addresses |
| 0.17 | 31st October 2026 | Section 4: V-11 and V-15 results recorded, V-14 decision recorded. Section 5: FND-08 added. Section 7: new rows added, logged-in users confirmed. Section 8 updated (drafted with AI assistance) | Owner results |
