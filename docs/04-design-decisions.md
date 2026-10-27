# 04 – Design Decisions

> **Status:** Draft v0.7 · Last updated: 27th October 2026
> **Author:** William Drummond
> **Related:** [01-scope-and-assets.md](01-scope-and-assets.md) · [02-threat-analysis.md](02-threat-analysis.md) · 03-security-requirements.md (not yet written) · [05-verification.md](05-verification.md)
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
| D-02 | | | | |

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
  6. Case control software installed
  7. SSH used for administration, with password login
  8. No updates installed since setup
- **Evidence:** Phase 0 results in 05-verification.md. Include the SD card image date and hash
- **Review trigger:** The baseline is repeated, or the hardware changes

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

## 7. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.1 | [date] | Template created | Structure agreed before Phase 0 |
| 0.2 | 27th October 2026 | D-01: added option 3, draft recommendation, reasoning and trade-offs (drafted with AI assistance, decision still open) | Preparation for Phase 0 |
| 0.3 | 27th October 2026 | Header: link to document 05 and remove template note (drafted with AI assistance) | Out-of-date header |
| 0.4 | 27th October 2026 | D-01 accepted: option 3, with the list of known earlier changes | Owner decision before Phase 0 |
| 0.5 | 27th October 2026 | D-01: install option, network connection and case software confirmed in the list of known earlier changes | Owner answers |
| 0.6 | 27th October 2026 | D-01: SSH login method confirmed as password | Owner answer |
| 0.7 | 27th October 2026 | D-01: no updates installed since setup. List of known earlier changes complete | Owner answer |
