# 03 – Security Requirements

> **Status:** Draft v0.2 · Last updated: 31st October 2026
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
- Priority: **[TODO]** (owner). Suggested scale: Must, Should, Could

## 3. Requirements

| ID | Requirement | Threats | Phase 0 finding | Phase | Verified by | Priority | Status |
|---|---|---|---|---|---|---|---|
| SR-01 | No account on the NAS uses a default or publicly documented password | T-01 | FND-01 (treated) | 1 | V-13 | **[TODO]** | Proposed |
| SR-02 | The OMV admin interface is reachable only from the LAN and the VPN, and is not served over plain HTTP **[TODO: owner to decide whether HTTPS is required or only evaluated (document 04, candidate decisions)]** | T-01, T-13 | Baseline: HTTP on all interfaces (V-01, V-04) | 1 | V-01, V-04 | **[TODO]** | Proposed |
| SR-03 | Administration uses a separate account from daily use, and only the administration account has sudo rights | T-01, T-12 | FND-05 | 1 | V-12 | **[TODO]** | Proposed |
| SR-04 | SSH does not allow root login | T-04 | FND-02 | 1 | V-09 | **[TODO]** | Proposed |
| SR-05 | SSH accepts key-based login only. Password login is disabled | T-04 | FND-03 | 1 | V-09 | **[TODO]** | Proposed |
| SR-06 | Repeated failed SSH logins are limited or blocked **[TODO: threshold]** | T-04 | Baseline: no fail2ban or similar service (V-04) | 1 | New test **[TODO]** | **[TODO]** | Proposed |
| SR-07 | Only services listed in the service inventory (document 01, section 6.3) listen on network interfaces. Services that are not needed are disabled | T-13, T-02 | FND-04 | 1 | V-01, V-02, V-04 | **[TODO]** | Proposed |
| SR-08 | The router has no port forwards to the NAS, no DMZ host and UPnP disabled | T-03, T-19 | FND-07 | 1 | V-07 | **[TODO]** | Proposed |
| SR-09 | No NAS service is reachable from the internet over IPv4 or IPv6 | T-03 | V-08 not yet run | 1 | V-08 | **[TODO]** | Proposed |
| SR-10 | Security updates for Debian and openmediavault are installed within **[TODO]** days of release, following a written update routine, with an image of the boot media taken before major upgrades | T-02, T-14 | FND-06 | 1 | V-10 | **[TODO]** | Proposed |
| SR-11 | Each share is accessible only to the accounts that need it, and guest access is disabled | T-12 | V-11 not yet run | 1 | V-11 | **[TODO]** | Proposed |
| SR-12 | Data on the SSD is encrypted at rest, with a recorded unlock approach | T-11 | FND-08 | 1 | V-14 | **[TODO]** | Proposed |
| SR-13 | SSD health is monitored, and a warning reaches me **[TODO: how]** | T-10, T-18 | Baseline: SSD healthy, not yet in use (V-06, V-14) | 1 | V-06, new alert test **[TODO]** | **[TODO]** | Proposed |
| SR-14 | Installed software is checked for known vulnerabilities at least every 12 hours, and the result is visible to me | T-02, T-06, T-14 | FND-06 | 1 | New test **[TODO]**. Design: D-03 | **[TODO]** | Proposed |
| SR-15 | Third-party software is reviewed for its privileges and network exposure before it is installed | T-06 | Baseline: no case software installed | 1 | V-04 | **[TODO]** | Proposed |
| SR-16 | Nothing that identifies the network, devices, accounts or keys is published in this repository | T-21 | None | All | Leak checks before every commit (document 05, section 2.4) | **[TODO]** | Proposed |

## 4. Threats without a requirement yet

These threats are treated in later phases (document 02, section 8). Requirements are added before each phase starts.

| Threat | Phase | Note |
|---|---|---|
| T-05 Ransomware or deletion spreads from a client | 3 | Backup accounts and copies clients cannot delete |
| T-07 Lateral movement on the LAN | 1 | Depends on router support for VLAN or guest isolation **[TODO: owner to check]** |
| T-08 Lost or compromised client device | 1, 2 | Per-device access and a revocation procedure |
| T-09 Accidental deletion or overwrite | 3 | Snapshots or versioning |
| T-10 SSD fails while the NAS holds the only copy | 3 | Second copy and restore test. V-15 not yet run. SR-13 covers monitoring only |
| T-15 Backup keys lost or backups cannot be restored | 3 | |
| T-16 Tailscale account takeover | 1, 2 | |
| T-17 VPN key mismanagement | 2 | |
| T-18 Power loss, overheating or SD card failure | 1 | Partly covered by SR-10 (boot media image) and SR-13 |
| T-20 Backups stop unnoticed | 3 | |

## 5. Open questions

- [ ] Which requirements are Must for Phase 1, and which can wait?
- [ ] SR-02: is HTTPS required for the admin interface, or only evaluated?
- [ ] SR-06 and SR-10: threshold and number of days
- [ ] SR-13: how warnings should reach me
- [ ] Does each Phase 0 finding have a requirement? (FND-01 to FND-08 are mapped above, but SR-12 covers the SSD only, not the SD card in FND-08 **[TODO]**. Once accepted, the SR IDs go into document 05, section 5, and the matrix)

## 6. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.1 | 30th October 2026 | Outline created: SR-01 to SR-16 drafted from the document 02 treatment plan and the Phase 0 findings, all Proposed (drafted with AI assistance) | Prepare requirements while Phase 0 finishes |
| 0.2 | 31st October 2026 | Section 3: SR-12 linked to FND-08. Section 5: open check updated, SR-12 does not cover the SD card (drafted with AI assistance) | New finding from V-14 |
