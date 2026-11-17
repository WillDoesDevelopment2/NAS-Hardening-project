# 03 – Security Requirements

> **Status:** Draft v0.11 · Last updated: 15th November 2026
> **Author:** William Drummond
> **Related:** [01-scope-and-assets.md](01-scope-and-assets.md) · [02-threat-analysis.md](02-threat-analysis.md) (threats and treatment plan) · [04-design-decisions.md](04-design-decisions.md) · [05-verification.md](05-verification.md) (tests and Phase 0 findings) · [../traceability/requirements-matrix.csv](../traceability/requirements-matrix.csv)
> **Note:** This is an outline drafted with AI assistance from the treatment plan in document 02, section 8, and the Phase 0 findings in document 05, section 5. Every requirement is **Proposed** until I accept, change or reject it. Priorities, target values and decisions are mine and are left as **[TODO]**. Record what I accepted, changed or rejected in `docs/ai-usage.md`, and meaningful changes in the revision log at the end.

---

## 1. Purpose

This document turns each threat treatment into numbered requirements (SR-01 onwards) that can be tested. Each requirement traces back to a threat in document 02 and forward to a test in document 05, and the traceability matrix records the chain.

## 2. How requirements are written

- One testable statement per requirement, written as what must be true, not how to achieve it. How is a design decision in document 04
- Each requirement names the threats it treats, the Phase 0 finding that showed the gap (if any), the phase it belongs to and the test that verifies it
- A requirement without an existing test gets a new test in document 05 before the phase starts
- Status values: **Proposed**, **Accepted**, **Rejected** (with the reason), **Superseded by SR-xx**
- Priority: Must, Should or Could. Set by the owner on 2nd November 2026, from suggestions drafted with AI assistance

## 3. Requirements

| ID | Requirement | Threats | Phase 0 finding | Phase | Verified by | Priority | Status |
|---|---|---|---|---|---|---|---|
| SR-01 | No account on the NAS uses a default or publicly documented password | T-01 | FND-01 (treated) | 1 | V-13 | Must | Accepted |
| SR-02 | The OMV admin interface is reachable only from the LAN and the VPN, and is not served over plain HTTP (HTTPS is Should, see D-04) | T-01, T-13 | Baseline: HTTP on all interfaces (V-01, V-04) | 1 | V-01, V-04 | Must (access limit), Should (HTTPS) | Accepted |
| SR-03 | Administration uses a separate account from daily use, and only the administration account has sudo rights | T-01, T-12 | FND-05 | 1 | V-12 | Must | Accepted |
| SR-04 | SSH does not allow root login | T-04 | FND-02 | 1 | V-09 | Must | Accepted |
| SR-05 | SSH accepts key-based login only. Password login is disabled | T-04 | FND-03 | 1 | V-09 | Must | Accepted |
| SR-06 | Repeated failed SSH logins are blocked: 5 failures within 10 minutes blocks the source for 1 hour (D-07) | T-04 | Baseline: no fail2ban or similar service (V-04) | 1 | New test **[TODO]** | Should | Accepted |
| SR-07 | Only services listed in the service inventory (document 01, section 6.3) listen on network interfaces. Services that are not needed are disabled | T-13, T-02 | FND-04 | 1 | V-01, V-02, V-04 | Must | Accepted |
| SR-08 | The router has no port forwards except one UDP port to the NAS for WireGuard, no DMZ host, and UPnP disabled. Phase 1 wording, verified in Phase 1: no port forwards to the NAS at all. Changed for Phase 2 (owner, 9th November 2026), D-19 | T-03, T-19 | FND-07 | 1, 2 | V-07 | Must | Accepted |
| SR-09 | No NAS service is reachable from the internet over IPv4 or IPv6, except the WireGuard UDP port, which answers only peers with a known key. Phase 1 wording, verified in Phase 1: no exception. Changed for Phase 2 (owner, 9th November 2026), D-19 | T-03 | FND-09 | 1, 2 | V-08, V-28, V-29 | Must | Accepted |
| SR-10 | Security updates for Debian are installed automatically each day, and other Debian and openmediavault updates within 14 days of release, following a written update routine (D-08), with an image of the boot media taken before major upgrades | T-02, T-14 | FND-06 | 1 | V-10 | Must | Accepted |
| SR-11 | Each share is accessible only to the accounts that need it, and guest access is disabled | T-12 | Baseline: no shares, SMB enabled with guest access not allowed (V-11) | 1 | V-11 | Must | Accepted |
| SR-12 | Data on the SSD is encrypted at rest, with a recorded unlock approach. The SD card is not encrypted, as an accepted risk (D-06) | T-11 | FND-08 | 1 | V-14 | Should | Accepted |
| SR-13 | SSD health is monitored, and a warning reaches me by email from OMV's notifications (D-09) | T-10, T-18 | Baseline: SSD healthy, not yet in use (V-06, V-14) | 1 | V-06, new alert test **[TODO]** | Should | Accepted |
| SR-14 | Installed software is checked for known vulnerabilities at least every 12 hours, and the result is visible to me | T-02, T-06, T-14 | FND-06 | 1 | New test **[TODO]**. Design: D-03 | Should | Accepted |
| SR-15 | Third-party software is reviewed for its privileges and network exposure before it is installed | T-06 | Baseline: no case software installed | 1 | V-04 | Should | Accepted |
| SR-16 | Nothing that identifies the network, devices, accounts or keys is published in this repository | T-21 | None | All | Leak checks before every commit (document 05, section 2.4) | Must | Accepted |
| SR-17 | No NAS service accepts unauthenticated access from the LAN, and no password crosses the LAN in clear text (OMV over HTTPS, SSH, SMB 3). Isolating other LAN devices is not required, as an accepted risk (D-11) | T-07 | None | 1 | V-01, V-04, V-11, V-21 | Must | Accepted |
| SR-18 | Each client device that reaches the NAS is listed and approved, and a written revocation procedure removes a lost or compromised device's access within 5 minutes. Devices no longer used are removed | T-08 | None | 1 | V-22, V-26 | Should | Accepted |
| SR-19 | The Tailscale account is protected by multi-factor authentication or a passkey at the identity provider. New devices need my approval (device approval or Tailnet Lock, choice recorded in document 04). Access rules allow only approved devices to reach the NAS ports needed | T-16 | None | 1 | V-19, V-22 | Must | Accepted |
| SR-20 | A written safe shutdown routine exists and has been tested. SSD temperature is covered by the SMART warnings in SR-13, and the boot media image by SR-10. A UPS is not required, as an accepted risk (D-12) | T-18 | Baseline: 179 unsafe shutdowns recorded on the SSD, most likely from earlier use (V-06) | 1 | V-27, V-17 | Should | Accepted |
| SR-21 | A WireGuard peer can reach only the NAS services it needs (22, 443, 445), enforced by a firewall on the NAS | T-07, T-13 | None | 2 | V-30, V-31 | Must | Accepted (owner, 9th November 2026) |
| SR-22 | WireGuard keys follow a written procedure: made on the device, private keys never copied off it, a list of peers kept outside the repository, rotation at a set interval | T-17 | None | 2 | V-33, V-34 | Must | Accepted (owner, 9th November 2026) |
| SR-23 | A WireGuard peer can be revoked within 5 minutes, using the written procedure | T-08, T-17 | None | 2 | V-32 | Should | Accepted (owner, 9th November 2026) |
| SR-24 | The laptop is backed up to the NAS automatically at least once a day while it is on and online, and the backup is encrypted on the laptop before it is sent (D-21, D-24, D-25) | T-09, T-10 | None | 3 | V-38, V-39 | Must | Accepted (owner, 12th November 2026) |
| SR-25 | The laptop's backup credentials cannot delete or overwrite existing backups. Old backups are removed only from the NAS side, by the administrator (D-23, D-25) | T-05, T-08 | None | 3 | V-25 | Must | Accepted (owner, 12th November 2026) |
| SR-26 | The backup account can reach only its own repository: no shell, no other files, no forwarding, and only from the laptop's Tailscale address (D-23) | T-08, T-12 | None | 3 | V-37 | Must | Accepted (owner, 12th November 2026) |
| SR-27 | The repository passphrase and a copy of its key are kept in two separate places, and the restore procedure is written down (D-24) | T-15 | None | 3 | V-41 | Must | Accepted (owner, 12th November 2026) |
| SR-28 | A failed backup, or no new backup for 48 hours, sends a warning to the administrator (D-26) | T-20 | None | 3 | V-43 | Should | Accepted (owner, 12th November 2026) |
| SR-29 | A restore is tested at the end of Phase 3 and then every 3 months, including from an older archive and without the laptop (D-25) | T-09, T-10, T-15 | None | 3 | V-40, V-41 | Must | Accepted (owner, 12th November 2026) |
| SR-30 | Passwords on the laptop are not included in its backups. The password manager is the place they are kept (D-22) | T-08 | None | 3 | V-44 | Should | Accepted (owner, 12th November 2026) |
| SR-31 | The phone's photos and files are copied to the NAS at least once a day when the phone is on Wi-Fi and charging, with nothing sent to a cloud service (D-29, D-31) | T-09, T-10 | None | 3 | V-46, V-47 | Must | Accepted (owner, 15th November 2026) |
| SR-32 | A device's backup keys can only write to that device's own folders: no delete, no reading back, no shell, no forwarding, no other folder, and only from the device's Tailscale address (D-30) | T-05, T-08, T-12 | None | 3 | V-45 | Must | Accepted (owner, 15th November 2026) |
| SR-33 | A file overwritten from a device can be recovered on the NAS for 14 days (D-31) | T-05, T-09 | None | 3 | V-48 | Should | Accepted (owner, 15th November 2026) |
| SR-34 | WhatsApp's local backup and other app exports that matter are in the synced `Backups` or WhatsApp folder, and a list of installed apps is saved (D-29) | T-09, T-10 | None | 3 | V-50 | Should | Accepted (owner, 15th November 2026) |

## 4. Threats without a requirement yet

These threats are treated in later phases (document 02, section 8). Requirements are added before each phase starts. T-07, T-08, T-16 and T-18 moved to section 3 on 2nd November 2026 (SR-17 to SR-20).

| Threat | Phase | Note |
|---|---|---|
| T-05 Ransomware or deletion spreads from a client | 3 | Backup accounts and copies clients cannot delete |
| T-09 Accidental deletion or overwrite | 3 | Snapshots or versioning |
| T-10 SSD fails while the NAS holds the only copy | 3 | Second copy and restore test. Nothing stored on the NAS yet (V-15). SR-13 covers monitoring only |
| T-15 Backup keys lost or backups cannot be restored | 3 | |
| T-16 Tailscale account takeover | 2 | SR-19 covers Phase 1. The comparison with WireGuard is Phase 2 |
| T-17 VPN key mismanagement | 2 | |
| T-20 Backups stop unnoticed | 3 | |

## 5. Open questions

- [x] Which requirements are Must for Phase 1, and which can wait? (Priorities set, section 3)
- [x] SR-02: is HTTPS required for the admin interface, or only evaluated? (Should, D-04)
- [x] SR-06 and SR-10: threshold and number of days (D-07, D-08)
- [x] SR-13: how warnings should reach me (email, D-09)
- [x] SR-17 to SR-20: accepted with priorities (owner, 2nd November 2026)
- [x] Does each Phase 0 finding have a requirement? FND-01 to FND-09 are mapped in section 3. Two gaps are accepted risks instead of requirements: the SD card in FND-08 (D-06), and port 7547 on the router in FND-09 (document 05, section 5)

## 6. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.1 | 30th October 2026 | Outline created: SR-01 to SR-16 drafted from the document 02 treatment plan and the Phase 0 findings, all Proposed (drafted with AI assistance) | Prepare requirements while Phase 0 finishes |
| 0.2 | 31st October 2026 | Section 3: SR-12 linked to FND-08. Section 5: open check updated, SR-12 does not cover the SD card (drafted with AI assistance) | New finding from V-14 |
| 0.3 | 31st October 2026 | Section 3: SR-09 linked to FND-09. Section 5: open check updated (drafted with AI assistance) | New finding from V-08 |
| 0.4 | 2nd November 2026 | Sections 3 and 4: out-of-date notes on V-11 and V-15 replaced with the results | Phase 0 complete |
| 0.5 | 2nd November 2026 | Section 3: SR-01 to SR-16 accepted with priorities, thresholds and choices filled in from D-04 to D-09. Section 5: four questions answered (drafted with AI assistance) | Owner decisions for Phase 1 |
| 0.6 | 2nd November 2026 | Section 5: requirement check ticked. The SD card gap is an accepted risk (D-06), and the router port in FND-09 is an accepted risk (document 05, section 5) | Owner decisions |
| 0.7 | 2nd November 2026 | Section 3: SR-17 to SR-20 drafted for T-07, T-08, T-16 and T-18 and accepted by the owner, priorities to set. Section 4: those threats moved to section 3. Section 5: question added (drafted with AI assistance) | Phase 1 checklist, section 1 |
| 0.8 | 2nd November 2026 | Section 3: priorities set for SR-17 to SR-20: SR-17 and SR-19 Must, SR-18 and SR-20 Should (suggested with AI assistance) | Owner decision |
| 0.9 | 9th November 2026 | Section 3: SR-08 and SR-09 changed for Phase 2 to allow one WireGuard UDP port (D-19). SR-21 to SR-23 added for WireGuard: SR-21 and SR-22 Must, SR-23 Should (drafted with AI assistance, from phase2-plan.md, section 4) | Owner decision |
| 0.10 | 12th November 2026 | Section 3: SR-24 to SR-30 added for Phase 3 backups and accepted by the owner: SR-28 and SR-30 Should, the rest Must (drafted with AI assistance, from phase3-plan.md, section 4) | Phase 3 plan |
| 0.11 | 15th November 2026 | Section 3: SR-31 to SR-34 added for the phone backups and accepted by the owner: SR-31 and SR-32 Must, SR-33 and SR-34 Should (drafted with AI assistance, from phase3-phone-plan.md, section 4) | Phase 3 part 2 plan |
