# 05 – Verification

> **Status:** Draft v0.4 · Last updated: 27th October 2026
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
- Record the SHA-256 hash of the SD card image taken before Phase 0 **[TODO]**

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

- [ ] Image of the SD card taken, date and hash recorded
- [ ] Baseline definition decided and recorded as D-01 in document 04
- [x] Expected results written for every test in section 4
- [ ] `evidence/phase0/` created and raw output location outside the repository chosen
- [ ] Router access confirmed
- [ ] Second LAN device and an outside network (for example mobile data) available for scanning
- [ ] No sensitive data on the NAS during the baseline

## 4. Phase 0 test plan

Phase 0 is observation only. If something serious is found, record it first, then fix it and log the change with a timestamp.

`<NAS-IP>` is a placeholder. Use the real address only in the private raw output.

| Test ID | Threat | What it checks | Tool and command | Run from | Expected result | Actual result | Pass or fail | Evidence |
|---|---|---|---|---|---|---|---|---|
| V-01 | T-02, T-13 | Open TCP ports | `nmap -sS -p- <NAS-IP>` | Second LAN device | Only 22 and 80 open, plus 445 if SMB is enabled (file sharing is still to be decided, document 01, section 6.2). Any other open TCP port, including one opened by the case control software, is a finding | | | |
| V-02 | T-13 | Open UDP ports | `sudo nmap -sU --top-ports 100 <NAS-IP>` | Second LAN device | Every port reported `open` or `open\|filtered` is matched to a known service, or recorded as unexplained (for example mDNS on 5353 if a discovery service runs). Unexplained ports are findings | | | |
| V-03 | T-02 | Service versions | `nmap -sV <NAS-IP>` | Second LAN device | Each detected service matches an installed package (cross-check with V-04). No updates have been installed since setup (D-01), so versions behind current releases are expected. Any service with pending updates in V-10, or past end of support, is a finding. Exact versions stay in the private raw output until fixed | | | |
| V-04 | T-13 | Listening sockets on the NAS | `ss -tulpn` | The NAS | Every listening socket maps to a row in document 01, section 6.3, including the case control software, which is installed (D-01). Record whether each service listens on all interfaces or on localhost only. The Ethernet port is not normally connected, so services are reached over Wi-Fi. Anything unexplained is a finding | | | |
| V-05 | T-02, T-13, T-14 | System audit | `sudo lynis audit system` | The NAS | Hardening index and every warning recorded. No target score at baseline | | | |
| V-06 | T-10, T-18 | SSD health | `sudo smartctl -a /dev/nvme0` | The NAS | Critical warning 0, available spare above its threshold and no media or data integrity errors. Percentage used and power-on hours recorded, as the SSD is recycled (document 01, section 6.1) | | | |
| V-07 | T-03, T-19 | Router exposure | Router admin page | Router | No port forwards to the NAS, no DMZ host set and UPnP off | | | |
| V-08 | T-03 | External exposure | Same Nmap scan as V-01, against the public address | Outside network (mobile data) | No NAS port reachable. Record whether the connection is behind CGNAT, as this affects how the result can be read | | | |
| V-09 | T-04 | SSH configuration | `sudo sshd -T` | The NAS | Values of `permitrootlogin`, `passwordauthentication`, `pubkeyauthentication` and any `allowusers` or `allowgroups` recorded. Password login is expected to be enabled, as it is used today (D-01). Root login or password login enabled is a finding | | | |
| V-10 | T-02, T-14 | Pending updates | `apt list --upgradable` | The NAS | Number of pending updates recorded, with security updates listed separately. Pending updates, including security updates, are expected as none have been installed since setup (D-01). Any pending security update is a finding | | | |
| V-11 | T-12 | Share permissions | OMV share and ACL review | OMV interface | Only intended accounts have access and there is no guest access. If no shares exist yet, record that | | | |
| V-12 | T-01, T-12 | Accounts | User and group list, sudo rights | The NAS | Only expected accounts have a login shell, and only the administrator account has sudo rights. One account is used for both administration and daily use (D-01), so this is expected to be a finding | | | |
| V-13 | T-01 | Default credentials | Check whether the publicly documented default OMV admin password is still in use | OMV interface | The default is still in use (known before testing). Expected to be a finding: record it first, then change the password and log the change with a timestamp | | | |
| V-14 | T-11 | Encryption status | `lsblk -f` | The NAS | Whether the SSD is encrypted is recorded. An unencrypted SSD holding data is a finding | | | |
| V-15 | T-10 | Existing copies of data | Manual check | n/a | For each data type in document 01, section 7.1, whether another copy exists is recorded. Data held only on the NAS is a finding | | | |

## 5. Phase 0 findings

One row per finding. Every finding links to a test, a threat and, once it exists, a requirement.

| ID | Test | Observation | Threat | Effect on rating | Resulting requirement | Status |
|---|---|---|---|---|---|---|
| FND-01 | | | | | | Open |

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
| | | | | |

## 8. Stage completion checks (Phase 1 onwards)

Each stage is complete when its criteria are verified, with evidence.

| Stage | Completion criterion | Verified by | Evidence | Date | Done |
|---|---|---|---|---|---|
| Phase 0 | All tests in section 4 run, findings logged, ratings reviewed | | | | [ ] |
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
| 0.1 | [date] | Template created with suggested Phase 0 tests | Structure agreed before Phase 0 |
| 0.2 | 27th October 2026 | Section 4: draft expected results for V-01 to V-15 (drafted with AI assistance, not yet confirmed) | Expected results must be written before tests run |
| 0.3 | 27th October 2026 | Header: correct matrix path and remove template note (drafted with AI assistance) | Out-of-date header |
| 0.4 | 27th October 2026 | Section 4: draft expected results updated with the known earlier changes in D-01 and confirmed by the owner (drafted with AI assistance) | Match D-01 and confirm before testing |
