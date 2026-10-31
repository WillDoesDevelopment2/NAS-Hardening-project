# 04 – Design Decisions

> **Status:** Draft v0.13 · Last updated: 31st October 2026
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
| D-02 | Temporary SSH access for Claude Code | Proposed | 0 | T-01, T-04, T-12 |
| D-03 | Vulnerability monitoring dashboard | Proposed | 1 | T-02, T-06, T-14 |

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
- **Status:** Proposed (drafted with AI assistance, owner to confirm)
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
- **Review trigger:** Tailscale is in place, or 5th January 2027, whichever comes first. The key is then removed and the removal logged

### D-03 – Vulnerability monitoring dashboard

- **Date:** 30th October 2026
- **Status:** Proposed (drafted with AI assistance, owner to confirm). Nothing is installed or scheduled until this is accepted. Creating the account and key is a change to the NAS, so it happens after Phase 0, or is logged as a deviation
- **Related:** T-02, T-06, T-14. V-03, V-10. FND-06. SR-14 (document 03, draft)
- **Context:** I want a local dashboard that checks the software on the NAS for known vulnerabilities every 12 hours, so I do not depend on remembering to look. Phase 0 showed a pending openmediavault update (FND-06) and that unattended upgrades are enabled but have installed nothing. Installing anything is a change, so this belongs to Phase 1 or later
- **Options considered:**
  1. **Run on the NAS.** A timer runs `debsecan` and `apt list --upgradable` and writes a page. Most accurate, needs no remote access. Adds a package and a timer to the NAS, and serving the page would add a service to protect (T-13)
  2. **Run on the laptop, using the temporary Claude Code key (D-02).** Nothing to set up. But D-02 and my working rules allow that key only for sessions I approve one by one, with the commands listed, so an unattended job every 12 hours would break that rule. The NAS logs would show the Claude Code account logging in when Claude Code is not working. The key is removed when Tailscale is in place or on 5th January 2027, so the dashboard would then stop
  3. **Run on the laptop, using a dedicated monitoring key.** A separate key in `authorized_keys`, limited with `restrict`, `from=` (laptop only) and `command=` to the one read-only command, so it cannot open a shell or forward anything. Adds nothing to the NAS except one key line. Needs a change on the NAS after Phase 0, which is logged. Only runs while the laptop is on
- **Decision:** Option 3 (owner, 30th October 2026, by messaging app). My first preference was option 2. Claude Code pointed out the conflict with D-02 and my working rules, and I chose a dedicated key instead. Which account holds the key is **[TODO]** (owner): a separate unprivileged account is suggested, so the logs show the dashboard as itself and it does not end with D-02
- **Reasoning:** The dashboard only needs to read the installed software and versions, so a key limited to that one read-only command is enough, and it can run unattended without using the Claude Code access
- **Trade-offs and residual risk:** For options 2 and 3, package names and versions are sent to OSV (a public API run by Google). No hostnames, addresses or usernames are sent. The dashboard output lists unfixed vulnerabilities and exact versions, so it stays in the raw evidence location and is never published. Packages from openmediavault and Raspberry Pi repositories are not covered by the Debian data and stay as manual checks. The dashboard shows only publicly known issues
- **Evidence:** Draft script `scripts/vuln-dashboard/`, tested on 30th October 2026 with made-up package data only. Not run against the NAS
- **Review trigger:** Tailscale is in place (the access path may change), D-02 ends, or the dashboard misses an update that V-10 finds

## 6. Candidate decisions to expect

These are not decisions yet. They are placeholders so that each one is recorded when it is made.

- Remote access: Tailscale first, then self-hosted WireGuard, and how they are compared (Phase 1 and 2)
- File sharing protocol and version (document 01, section 6.2 still says to be decided)
- Admin interface: HTTP or HTTPS, and which networks may reach it
- SSD encryption, and how it is unlocked after a reboot
- Backup tool for phone and computer, and how clients are prevented from deleting their own backups
- Monitoring and alerting approach
- Network isolation: VLAN or guest network if the router supports it, otherwise accept the risk
- Update routine, including unattended security updates
- Case vendor software: keep, restrict or remove
- NAS network connection: Wi-Fi or Ethernet to the router, and which unused radios and interfaces are disabled (Bluetooth, Wi-Fi if Ethernet is chosen, the direct troubleshooting link to the laptop). Related: T-07, T-13, T-18 (Phase 1)
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
