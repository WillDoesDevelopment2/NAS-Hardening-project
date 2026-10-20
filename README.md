# Home NAS Hardening and Risk Analysis

**Status:** In progress (Phase 0: baseline) | **Started:** October 2026 | **Last updated:** [date]

A self-hosted NAS built to replace third-party cloud storage, used as a hands-on project in structured security work: define what needs protecting, analyse threats, set numbered requirements, harden the system, and verify every control with evidence.

The central design principle is that **no NAS service is exposed directly to the internet.** My phone and computer reach it through an encrypted VPN tunnel instead.

## At a Glance

- **Hardware:** Raspberry Pi 5 in a Pironman 5 kit, with a recycled 1 TB SSD, running OpenMediaVault
- **Remote access:** Tailscale first, then self-hosted WireGuard, with the two compared
- **Backups:** Automated backups from my phone and computer, finishing with a tested restore
- **Method:** Simplified threat analysis and risk assessment, inspired by ISO/SAE 21434 (not a compliance claim)

Full detail on the system, assets, trust boundaries and network design is in [`docs/01-scope-and-assets.md`](docs/01-scope-and-assets.md).

## Progress

- [x] Scope and assets defined
- [x] Initial threat analysis drafted
- [ ] Phase 0: Baseline measurements before any changes
- [ ] Security requirements written
- [ ] Phase 1: Hardening and Tailscale remote access
- [ ] Phase 2: Self-hosted WireGuard and comparison with Tailscale
- [ ] Phase 3: Automated phone and computer backups, with restore test
- [ ] Phase 4: Final verification, root cause analysis, residual risk and tutorial

Phase definitions are in the scope document.

## Key Decisions So Far

| Decision | Why |
|---|---|
| Do not expose OMV or any NAS service to the internet | Every exposed service adds attack surface |
| Use a private-network VPN, not a privacy VPN | A privacy VPN cannot connect me to my home network |
| Tailscale first, then compare with WireGuard | Trade-off between simplicity and third-party trust |
| Treat the NAS as one copy, not a backup | A second copy that clients cannot overwrite is required |

Reasoning is in [`docs/04-design-decisions.md`](docs/04-design-decisions.md).

## Top Risks So Far

A snapshot of the highest-rated threats. The ratings are drafts and will change as evidence is collected. The full register, treatment plan and Tailscale trust analysis are in [`docs/02-threat-analysis.md`](docs/02-threat-analysis.md).

| Risk | Draft rating |
|---|---|
| OMV admin interface compromised through default or weak credentials | High |
| Known vulnerability in OMV, Debian or an exposed service | High |
| Accidental internet exposure (port forward, UPnP) | High |
| Ransomware or deletion on a client spreading to the NAS | High |
| SSD failure while the NAS holds the only copy | High |

## How the Project Works

Every control follows the same chain: **threat → requirement → control → test → result.** The links between them are recorded in [`traceability/requirements-matrix.csv`](traceability/requirements-matrix.csv).

Planned tools include Nmap, Lynis, ufw or nftables, OpenSSH, fail2ban or CrowdSec, LUKS, Tailscale, WireGuard and Python. How each one is used is documented in [`docs/05-verification.md`](docs/05-verification.md).

## Repository Contents

```
nas-hardening/
├── README.md
├── docs/
│   ├── 01-scope-and-assets.md        # Scope, assets, trust boundaries, data flows
│   ├── 02-threat-analysis.md         # Threat register, treatments, Tailscale trust analysis
│   ├── 03-security-requirements.md   # Numbered requirements (SR-01...)
│   ├── 04-design-decisions.md        # Why each approach was chosen
│   ├── 05-verification.md            # Test plan, tools and results
│   ├── 06-root-cause-analysis.md     # 8D-style write-up of a real issue
│   ├── 07-residual-risk.md           # What is still not covered, and why
│   └── ai-usage.md                   # Where AI was used, and what was checked or rejected
├── traceability/                     # Requirement → control → test → result
├── config/                           # Sanitised configuration examples
├── scripts/                          # Python: config audit, scan parsing
├── evidence/                         # Sanitised scan outputs and screenshots
└── tutorial/                         # Step-by-step guide, written after hardening
```

Files appear as the project progresses, so check the progress list for what exists so far.

## Skills Demonstrated

**So far:** scoping a security project, structured threat analysis with risk rating, evaluating third-party trust, and technical documentation.

**Planned:** Linux hardening, network exposure verification, security auditing, encryption trade-offs, backup and restore testing, requirements traceability, root cause analysis and Python scripting.

## Disclaimer

This repository documents my own home setup and threat model for educational and portfolio purposes. It is not a universal guide, so adapt anything to your own risks. Real IP addresses, hostnames, usernames and keys are replaced with placeholders, and scan output and screenshots are reviewed before publishing. All testing is done on equipment I own, on my own network.

AI tools were used to review and challenge my work and to help with drafting. This is recorded in [`docs/ai-usage.md`](docs/ai-usage.md), including what I accepted, changed or rejected. The threat ratings and design decisions are my own.

## Contact

GitHub: @willdoesdevelopment2
Email: julianDelphinki01@pm.me

