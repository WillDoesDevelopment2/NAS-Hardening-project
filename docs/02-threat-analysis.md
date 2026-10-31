# 02 – Threat Analysis

> **Status:** Draft v0.8 · Last updated: 31st October 2026
> **Author:** William Drummond
> **Related:** [01-scope-and-assets.md](01-scope-and-assets.md) (asset IDs, data flows, trust boundaries and phases used here) · 03-security-requirements.md (requirements derived from this analysis, not yet written) · [05-verification.md](05-verification.md) (tests that confirm each treatment)
> **Note:** This is a starting draft prepared with AI assistance. Every rating and treatment is a proposal. Review each one, change anything that does not match your setup or your own judgement, replace anything in **[TODO]** or square brackets, and record what you accepted, changed or rejected in `docs/ai-usage.md`. Record meaningful changes in the revision log at the end.

---

## 1. Purpose

This document identifies what could go wrong with the NAS, rates each threat, and decides how to treat it. It answers the second half of the central question in document 01:

> **How can I access my NAS remotely without exposing it to the internet, and what risks remain?**

The output of this document feeds the numbered requirements in `03-security-requirements.md`. Each requirement, control and test should trace back to a threat ID defined here.

## 2. Method

This is a simplified risk assessment structured after the ISO/IEC 27005 process: identify assets, identify threats, estimate likelihood and impact, evaluate the result against criteria, choose a treatment, and record what risk remains. Treatments are cross-referenced to ISO/IEC 27002:2022 control themes so that each decision can be explained against a recognised control catalogue.

The same loop (asset, threat, risk, treatment, verification) appears in the threat analysis and risk assessment (TARA) activity of ISO/SAE 21434. That standard is written for road vehicles, so the comparison is an analogy and not a method I am following.

This is **not** an ISO/IEC 27001 implementation, an ISMS or a compliance claim. It is a proportionate process for a single home system.

| Step | What happens | Where it is recorded |
|---|---|---|
| 1 | Identify and rate assets | Document 01, section 7 |
| 2 | Identify threat sources | Section 3 |
| 3 | Identify threats | Section 5 |
| 4 | Estimate likelihood and impact, and rate the risk | Sections 4 and 5 |
| 5 | Choose and plan a treatment | Section 8 |
| 6 | Verify each treatment with evidence | Document 05 |
| 7 | Record residual risk and what is knowingly accepted | Document 07 |

## 3. Threat sources

| ID | Source | Description | In scope |
|---|---|---|---|
| TS-1 | Opportunistic internet attacker | Automated scanning, credential stuffing and exploitation of known vulnerabilities. Only relevant if something is exposed | Yes |
| TS-2 | Untrusted device on the LAN | Smart devices, guest devices or any LAN device that is compromised | Yes |
| TS-3 | Malware or attacker on my phone or computer | Ransomware, credential theft or a stolen logged-in device | Yes |
| TS-4 | Myself | Configuration mistakes, accidental deletion, lost keys, leaked secrets | Yes |
| TS-5 | Hardware, power and environment | Disk failure, power loss, overheating | Yes |
| TS-6 | Third parties and supply chain | Tailscale, the identity provider, OMV, Debian, the case vendor | Yes |
| TS-7 | Opportunistic physical access | Theft or loss of the device | Partly. Building security is out of scope (document 01, section 5.2), but protecting the data on a stolen device is in scope |
| TS-8 | Well-resourced targeted attacker | State-level or dedicated adversary | No (document 01, section 5.2) |

## 4. Risk rating method

Ratings are qualitative. They are structured judgements, not measured probabilities.

### 4.1 Likelihood

| Rating | Meaning (for a home system, at the baseline state) |
|---|---|
| Low (L) | Would need an unusual event or several things going wrong. Not expected in a year |
| Medium (M) | Plausible within a year, or a known common failure for this kind of setup |
| High (H) | Expected to happen, or already happening |

### 4.2 Impact

Impact is the worst **realistic** outcome of that specific threat, guided by the C, I and A ratings of the affected assets in document 01, section 7. It is not automatically the highest rating among those assets, because a single event often affects only part of an asset.

| Rating | Meaning |
|---|---|
| Low (L) | Minor inconvenience, quickly recovered |
| Medium (M) | Some data or time lost, or partial exposure. Recoverable with effort |
| High (H) | Serious or irreversible loss, exposure of sensitive data, or loss of the only copy |

### 4.3 Risk matrix

| Likelihood ↓ / Impact → | Low | Medium | High |
|---|---|---|---|
| **High** | Medium | High | High |
| **Medium** | Low | Medium | High |
| **Low** | Low | Low | Medium |

### 4.4 Risk criteria

| Rating | Decision rule |
|---|---|
| High | Must be treated, with a test and recorded evidence, before the phase that depends on it |
| Medium | Treat where proportionate. If not treated, record the reason and accept it knowingly |
| Low | Accept, and review again in Phase 4 |

### 4.5 Which risk is rated

Ratings in this document describe the **baseline**: the current OMV setup on the home LAN, before hardening. Phase 0 evidence will confirm or change them. The residual risk after Phase 4 is recorded in `07-residual-risk.md`.

## 5. Threat register

Trust boundaries are numbered in the order they appear in document 01, section 9 (TB1 = Internet ↔ home network, TB2 = LAN ↔ NAS, TB3 = VPN ↔ NAS, TB4 = Tailscale coordination service, TB5 = client devices). Data flows (F-1 to F-7) are defined in document 01, section 8.

### 5.1 Register

| ID | Threat | Source | Assets | Flow or boundary | Likelihood | Impact | Draft rating |
|---|---|---|---|---|---|---|---|
| T-01 | OMV admin interface compromised through default or weak credentials | TS-1, TS-2, TS-3 | A-01, A-02, A-04, A-05 | F-3, TB2 | M | H | **High** |
| T-02 | Known vulnerability in OMV, Debian or an exposed service is exploited | TS-1, TS-2 | A-01, A-02, A-05 | F-1, F-3, F-4, TB1, TB2 | M | H | **High** |
| T-03 | Accidental internet exposure of a NAS service (port forward, UPnP, router misconfiguration) | TS-1, TS-4 | A-01, A-02, A-03, A-04, A-05, A-06 | TB1 | M | H | **High** |
| T-04 | Brute-force or credential-stuffing attack on SSH or SMB | TS-1, TS-2 | A-04, A-05 | F-1, F-4 | L | H | Medium |
| T-05 | Ransomware or mass deletion on a client spreads to the NAS through mounted shares or backup access | TS-3 | A-01, A-02, A-04 | F-1, F-2, F-6, TB5 | M | H | **High** |
| T-06 | Third-party software on the NAS (case control software, plugins) is vulnerable or malicious | TS-6 | A-04, A-05 | Supplier dependency | L | H | Medium |
| T-07 | Lateral movement between an untrusted LAN device and the NAS (attack on the NAS, credential sniffing, or the NAS used as a pivot) | TS-2 | A-04, A-06 | F-1, TB2 | M | M | Medium |
| T-08 | Lost, stolen or compromised phone or computer exposes VPN keys, saved share credentials or backup access | TS-3, TS-7 | A-01, A-02, A-04 | F-2, F-6, TB5 | L | H | Medium |
| T-09 | Accidental deletion, overwrite or sync error destroys or alters files | TS-4 | A-01, A-02, A-03 | F-1, F-6 | M | M | Medium |
| T-10 | SSD fails while the NAS holds the only copy | TS-5 | A-01, A-02, A-07 | Not applicable | M | H | **High** |
| T-11 | NAS or SSD is stolen or lost, exposing unencrypted data | TS-7 | A-01, A-02, A-03, A-07 | Not applicable | L | H | Medium |
| T-12 | Over-permissive shares or user permissions expose data to unintended accounts or devices | TS-2, TS-4 | A-01, A-02 | F-1, F-2 | M | M | Medium |
| T-13 | Unnecessary services and insecure defaults enlarge the attack surface (discovery services, cleartext HTTP admin access) | TS-2, TS-4 | A-05 | F-3 | M | M | Medium |
| T-14 | Missed or failed updates leave known fixes unapplied, or a bad update breaks the system | TS-4, TS-6 | A-05 | F-7 | M | M | Medium |
| T-15 | Backup repository keys or passwords are lost, or backups cannot be restored | TS-4 | A-02, A-04 | F-6 | L | H | Medium |
| T-16 | Tailscale account takeover or coordination service compromise lets an attacker join the tailnet | TS-1, TS-6 | A-01, A-02, A-03, A-04, A-05 | F-5, TB4 | L | H | Medium |
| T-17 | VPN key mismanagement (leaked, never rotated or revoked, or lockout caused by misconfiguration) | TS-3, TS-4 | A-04, A-08 | F-2, F-5 | L | M | Low |
| T-18 | Power loss, overheating or SD card failure corrupts the system or data | TS-5 | A-01, A-05, A-07 | Not applicable | M | M | Medium |
| T-19 | Router weakness (default credentials, UPnP enabled, firmware flaws) undermines network protections | TS-1, TS-2 | A-06 | TB1 | M | M | Medium |
| T-20 | Backups silently stop running or fail unnoticed | TS-4, TS-5 | A-02, A-08 | F-2, F-6 | M | M | Medium |
| T-21 | Sensitive details are published in this repository (IP addresses, keys, hostnames, scan output) | TS-4 | A-03, A-04 | This repository | L | H | Medium |

**Summary:** 5 High, 15 Medium, 1 Low. The five High threats match the snapshot in the README.

### 5.2 Rating rationale and Phase 0 evidence

Each rating below is a draft. The right-hand column states what the Phase 0 baseline should show so the rating can be confirmed or changed.

| ID | Why this draft rating | Phase 0 evidence to collect |
|---|---|---|
| T-01 | Default OMV administrator credentials are publicly documented, and the admin interface is reachable from the whole LAN over HTTP | Confirm whether the default password has been changed (done: it had not, see section 5.4). Nmap service scan and `ss -tulpn` for the admin interface |
| T-02 | OMV, Debian, Samba and OpenSSH all receive regular security fixes, and the patch level at baseline is unknown | Nmap version detection, `apt list --upgradable`, Lynis report |
| T-03 | UPnP and port forwarding are common causes of accidental exposure. CGNAT, if present, may reduce this | Router check for port forwards and UPnP. External scan from outside the LAN (for example from mobile data). Not behind CGNAT (V-07, 30th October 2026) |
| T-04 | Nothing is exposed at baseline and SSH is LAN only. Becomes Medium likelihood if T-03 occurs | `sshd -T`, `ss -tulpn`, check whether any lockout or rate limiting exists |
| T-05 | Writable SMB shares mounted on a client are reachable by ransomware, and any backup written to the same share can be overwritten | Share and permission review. Phase 3 restore test from a copy that clients cannot overwrite |
| T-06 | The case vendor software controls fan, display and lighting but runs on the NAS, possibly with elevated privileges | Inventory of vendor packages, their listening ports and the user they run as (done: not installed, see section 5.4) |
| T-07 | Other home devices share the LAN, and VLAN support is unknown | Router capability check. Nmap from a second LAN device. Decision recorded under document 01, section 5.3 |
| T-08 | Depends on the assumptions in document 01, section 10 (screen locks, device encryption and updates), confirmed on 27th October 2026 | Later, test revoking a device |
| T-09 | One person makes manual changes, and no versioned or snapshot copy exists at baseline | Check whether snapshots or versioning exist. Phase 3 restore test |
| T-10 | The SSD is second-hand with unknown wear, and the NAS is currently one copy, not a backup | SMART data (wear, reallocated sectors, power-on hours). Record whether any other copy of the data exists |
| T-11 | I am the only administrator, but not the only person with physical access (document 01, section 10). The device is at home, the data is likely unencrypted at baseline, and the boot SD card can be removed and read on another computer. **[TODO: owner to review the likelihood rating in light of this]** | Encryption status of the SSD (done, see section 5.4). Record of how the SSD was wiped before reuse (owner confirmed 31st October 2026 that it was wiped and reimaged, method not recorded) |
| T-12 | Default share settings may allow guest access or broad group access | Share and ACL review. Test access using an account that should be refused |
| T-13 | The OMV admin interface uses HTTP on port 80 (document 01, section 6.3), and other default services may be running | Compare `ss -tulpn` and Nmap output with the service inventory in document 01, section 6.3 |
| T-14 | One maintainer and no defined update routine yet | Date of last update, unattended-upgrades configuration, Lynis findings |
| T-15 | No backups exist at baseline, so likelihood is Low now. It rises when Phase 3 starts | Phase 3 restore test and a documented key storage procedure |
| T-16 | Tailscale moves the risk to the account and the vendor. Impact is High because tailnet membership gives network reachability to the NAS. Defence in depth (OMV and SSH authentication, access rules) limits what an intruder gains | See the trust analysis in section 7 |
| T-17 | A Phase 2 matter. WireGuard keys will sit on few devices. Impact is Medium because a key alone should not bypass OMV and SSH authentication | Key management procedure written in Phase 2 |
| T-18 | Hardware is a Pi 5 on a 60 W supply with a case kit and an SD card as boot media. Unclean shutdowns are possible | Temperature readings under load. Filesystem check after an unclean shutdown. SD card image backup status |
| T-19 | The router is outside hardening scope but is verified for exposure (document 01, section 5.3) | Sanitised record of router settings and firmware version |
| T-20 | Monitoring is still "to be decided" (document 01, section 6.2) | Phase 3 backup alerting design, tested by deliberately interrupting a backup |
| T-21 | Practice is defined in document 01, section 12. Impact is High because a committed key or address would be public | A review checklist before each commit, and a secret scanning tool such as gitleaks **[TODO: decide]** |

### 5.3 Highest rating per asset

A check that every asset has at least one threat and that nothing is missing from document 01, section 7.

| Asset | Threats | Highest draft rating |
|---|---|---|
| A-01 Personal files | T-01, 02, 03, 05, 08, 09, 10, 11, 12, 16, 18 | High |
| A-02 Phone and computer backups | T-01, 02, 03, 05, 08, 09, 10, 11, 12, 15, 16, 20 | High |
| A-03 Project and portfolio material | T-03, 09, 11, 16, 21 | High |
| A-04 Credentials and keys | T-01, 03, 04, 05, 06, 07, 08, 15, 16, 17, 21 | High |
| A-05 NAS system | T-01, 02, 03, 04, 06, 13, 14, 16, 18 | High |
| A-06 Home network | T-03, 07, 19 | High |
| A-07 Physical hardware | T-10, 11, 18 | High |
| A-08 Availability of remote access | T-17, 20 | Medium |

### 5.4 Phase 0 results so far

What the Phase 0 tests in document 05, section 4, have shown for each threat. Ratings are not changed here: any change is the owner's decision and is recorded in document 05, section 6, and in the register above.

| ID | Tests run | What Phase 0 showed | Rating decision |
|---|---|---|---|
| T-01 | V-12, V-13 | The default OMV admin password was still in use and was changed on 28th October 2026 (FND-01). One account is used for administration and daily use, with sudo rights (FND-05). The admin interface is served over HTTP on all interfaces (V-01, V-04) | No change (owner decision, 28th October 2026) |
| T-02 | V-01, V-03, V-05, V-10 | SSH (OpenSSH 10.x) and nginx (version hidden) are reachable from the LAN. openmediavault has a pending update (FND-06). No updates pending from a security suite. Lynis hardening index 63 | **[TODO]** (owner) |
| T-04 | V-04, V-09 | Root login and password login are enabled (FND-02, FND-03). The root password is locked and root's `authorized_keys` file is empty (reviewed 30th October 2026), so root has no working login method today. No fail2ban or similar service is running | **[TODO]** (owner) |
| T-06 | V-01, V-04 | The case control software is not installed (owner confirmed 29th October 2026). No vendor service or port seen | **[TODO]** (owner). The likelihood could be reviewed while no third-party software is installed |
| T-10 | V-06, V-15 | SSD health within the expected limits (no media errors, 0% used), but the SSD is not yet in use (V-14). Personal files, project files, media and some identity documents have other copies. Other identity documents, financial documents, phone backups and computer backups have none, and none of these is on the NAS at baseline | **[TODO]** (owner) |
| T-11 | V-14 | No disk is encrypted. The system and any data are on the SD card (FND-08). The SSD holds no data yet, and was wiped and reimaged before reuse (owner confirmed 31st October 2026, method not recorded) | **[TODO]** (owner), together with the likelihood review in section 5.2 |
| T-12 | V-11, V-12 | One account with sudo rights (FND-05). No shares yet. SMB shows as enabled in OMV, minimum protocol SMB2, guest access not allowed | **[TODO]** (owner) |
| T-13 | V-01, V-02, V-04, V-05, V-11 | rpcbind, LLMNR and mDNS listen on all interfaces and are reachable from the LAN (FND-04). HTTP admin interface. SMB not running at V-01 and V-04, but shown as enabled in OMV on 31st October 2026 (V-11), not yet explained. Bluetooth running | **[TODO]** (owner) |
| T-14 | V-05, V-10 | 12 pending updates, none from a security suite. Unattended upgrades enabled, but none installed. openmediavault update pending (FND-06) | **[TODO]** (owner) |
| T-18 | V-05, V-06 | 179 unsafe shutdowns over the SSD's life, not attributable to the NAS as the SSD was used in a laptop before. Lynis reports a reboot is likely needed, not yet investigated | **[TODO]** (owner) |
| T-03, T-19 | V-07, V-08 | V-07: no port forwards, no DMZ host, DDNS off, not behind CGNAT. UPnP is on, with no mappings (FND-07). The NAS has public IPv6 addresses, so exposure depends on the router's IPv6 firewall. V-08 not yet run | Wait for V-08 |

## 6. High-rated threats in detail

### T-01 – OMV admin interface compromised through default or weak credentials

- **Vector:** A device on the LAN, or malware on one of my own devices, reaches the admin interface and logs in with a default or guessed password.
- **Outcome:** Full control of the NAS. An attacker can read or change every share, create accounts and enable services.
- **Baseline protections:** LAN-only reachability. Nothing else is confirmed **[TODO]**.
- **Treatment direction:** Change default credentials, use a unique password from a password manager, separate administrator and daily accounts, restrict the interface to the LAN and VPN, and evaluate stronger authentication.

### T-02 – Known vulnerability in OMV, Debian or an exposed service is exploited

- **Vector:** An attacker uses a published exploit against an out-of-date service such as the web interface, Samba or SSH.
- **Outcome:** Remote code execution or data access, possibly with high privileges.
- **Baseline protections:** Not exposed to the internet. Patch level unknown.
- **Treatment direction:** Update the system, remove unneeded services, apply a deny-by-default firewall, and follow security advisories as part of a defined update routine.

### T-03 – Accidental internet exposure of a NAS service

- **Vector:** A port forward, a UPnP request from another device, or a router reset exposes a NAS service to the internet without my noticing.
- **Outcome:** Every other internet-facing threat (T-01, T-02, T-04) becomes much more likely.
- **Baseline protections:** Router state not yet recorded. CGNAT status unknown.
- **Treatment direction:** No port forwards, UPnP disabled, an external scan to prove it, and a repeat check after any router change. This is the main reason the design avoids exposing anything.

### T-05 – Ransomware or deletion on a client spreads to the NAS

- **Vector:** Ransomware on my computer encrypts files on a mounted share. Or a backup client with write and delete rights overwrites or removes its own backups.
- **Outcome:** Live files and backups are damaged together, so there is nothing clean to restore.
- **Baseline protections:** None specific.
- **Treatment direction:** Separate backup accounts with minimal rights, versioned or snapshot copies that clients cannot delete, and a restore test that proves the copy survives. This links to the success criterion in document 01, section 13.

### T-10 – SSD fails while the NAS holds the only copy

- **Vector:** Wear or a fault in the second-hand SSD, or an unclean shutdown, makes the disk unreadable.
- **Outcome:** Permanent loss of everything stored only on the NAS.
- **Baseline protections:** None. The NAS is one copy and not a backup.
- **Treatment direction:** SMART monitoring, a second copy that is not reachable in the same way as the first, and a tested restore.

## 7. Tailscale trust analysis

This section supports threat T-16 and the Phase 1 to Phase 2 comparison. Statements were checked against the Tailscale documentation on 27th October 2026 (sources in section 7.5). Features and defaults change, so check again before Phase 1 **[TODO]**.

### 7.1 What Tailscale does

- **Data plane:** Devices connect to each other through WireGuard tunnels. Traffic between my devices is encrypted end to end, and the private keys stay on the devices.
- **Control plane:** A coordination service run by Tailscale handles login, distributes public keys, network configuration and access rules, and helps devices find each other. It carries no user traffic.
- **Relays:** If a direct connection fails, traffic can pass through a relay: a peer relay (another device in the tailnet) or a Tailscale DERP relay server. Relays forward traffic that is already encrypted and cannot decrypt it.

### 7.2 What I am trusting

| Item | Trust placed in the vendor or provider | Impact if that trust fails |
|---|---|---|
| Coordination service | To distribute only the correct public keys and not add devices to my network | An attacker or a malicious operator could add a device that I did not approve |
| Identity provider account | To authenticate me correctly | Account takeover lets an attacker add devices to my tailnet |
| Relay servers | To pass traffic without being able to read it | Metadata exposure (who connects, when). Content stays encrypted. The DERP documentation does not say what metadata a relay can see |
| Tailscale client software | To behave correctly on my NAS and clients | A flaw in the client could affect the device it runs on |
| Metadata held by the vendor | By default each client sends its logs to Tailscale, including open and close events for connections. Client logging can be turned off per device (`--no-logs-no-support`), but Tailscale may then not be able to give support | Privacy exposure, not data exposure |

### 7.3 Risks and mitigations

| Risk | Mitigation to evaluate | Residual position |
|---|---|---|
| Identity provider account takeover | Tailscale has no passwords of its own, so login depends on the identity provider. Strong unique password and multi-factor authentication there, or a passkey. Device approval or Tailnet Lock for new devices (they cannot both be enabled, see below) | Reduced, depends on one account |
| Unwanted device added to the tailnet | Device approval or Tailnet Lock, key expiry (180 days by default, can be turned off per device), and access rules that allow only the NAS ports I need from the devices I choose. The default policy allows all traffic between devices, so rules must be written | Reduced |
| Compromised or malicious coordination service | Evaluate Tailnet Lock: new devices must be signed by trusted keys held on my own devices, so the coordination service cannot add devices by itself. It needs at least two signing devices, its disablement secrets must be stored safely (without them the tailnet may not be recoverable), and it cannot be used together with device approval **[TODO: decide between device approval and Tailnet Lock]**. Keep OMV and SSH authentication in place, so a tailnet device alone is not enough | Partly accepted. This is the main reason to compare against self-hosted WireGuard in Phase 2 |
| Metadata exposure | Neutral device names. Accept the remainder | Accepted |
| Vendor outage or account lockout | LAN access still works. During a coordination service outage, existing tailnet connections mostly keep working, as access rules are cached on each device, but new devices cannot be added and keys cannot be refreshed, so access is gradually lost as keys expire. Self-hosted WireGuard as an alternative path in Phase 2 | Accepted, linked to T-17 and A-08 |
| Extra features widening the attack surface | Do not enable features I do not need. Keep SSH as OpenSSH with keys unless there is a reason to change **[TODO: decide]** | Reduced |

### 7.4 Questions for the Phase 2 comparison

- What does self-hosted WireGuard remove from the trust list above, and what new work does it add (key management, one open UDP port, CGNAT handling)?
- Is the extra control worth the extra maintenance for a single-person home system?

### 7.5 Sources

Checked on 27th October 2026. Pages from the Tailscale website only.

| Topic | Source |
|---|---|
| Keys stay on devices, control plane and data plane | [How Tailscale works](https://tailscale.com/blog/how-tailscale-works) |
| Relays cannot decrypt traffic, peer relays | [DERP servers](https://tailscale.com/docs/reference/derp-servers) |
| Coordination service outage | [What happens if the coordination server is down?](https://tailscale.com/kb/1091/what-happens-if-the-coordination-server-is-down) |
| Tailnet Lock, and that it cannot be used with device approval | [Tailnet Lock](https://tailscale.com/kb/1226/tailnet-lock) |
| Device approval | [Device approval](https://tailscale.com/kb/1099/device-approval) |
| Key expiry | [Key expiry](https://tailscale.com/kb/1028/key-expiry) |
| Default allow-all policy, rules enforced on each device | [Access control lists](https://tailscale.com/kb/1018/acls) |
| No Tailscale passwords, MFA and passkeys | [Identity providers](https://tailscale.com/kb/1013/sso-providers) |
| Client logging and opt-out | [Logging](https://tailscale.com/kb/1011/log-mgmt) |

## 8. Treatment plan

Treatment options are **Reduce** (add a control), **Avoid** (remove the cause), **Accept** (record and live with it) and **Transfer** (rely on a third party). The ISO/IEC 27002:2022 references are indicative themes. **[TODO: check each reference against the standard text before claiming a clause-level mapping. If I do not have access to the text, reference themes only.]**

| ID | Option | Planned treatment (summary) | Phase | ISO/IEC 27002:2022 theme |
|---|---|---|---|---|
| T-01 | Reduce | Change default credentials, unique strong passwords, separate admin and daily accounts, restrict the interface to LAN and VPN, evaluate stronger authentication | 1 | 5.15, 5.17, 8.2, 8.5 |
| T-02 | Reduce | Update OS and OMV, remove unneeded services, deny-by-default firewall, follow advisories | 1 | 8.8, 8.9, 8.20 |
| T-03 | Avoid, Reduce | No port forwards, UPnP disabled, external scan as evidence, re-check after router changes | 1, 2 | 8.9, 8.20, 8.21 |
| T-04 | Reduce | Key-based SSH, password login disabled, rate limiting or banning (fail2ban or CrowdSec), SMB restricted to LAN and VPN | 1 | 5.17, 8.5, 8.16, 8.20 |
| T-05 | Reduce | Backup accounts with minimal rights, snapshot or versioned copies clients cannot delete, restore test | 3 | 5.15, 8.7, 8.13 |
| T-06 | Reduce | Review vendor software, run with least privilege, block network exposure, remove if not needed | 1 | 5.19, 5.21, 8.19 |
| T-07 | Reduce, Accept | Allow only approved devices to reach NAS services. VLAN or guest isolation if the router supports it, otherwise accept and record | 1 | 8.20, 8.22 |
| T-08 | Reduce | Screen lock and device encryption, per-device access, written revocation procedure, remove unused devices | 1, 2 | 5.17, 7.9, 8.1 |
| T-09 | Reduce | Snapshots or versioning, recycle bin if suitable, restore test | 3 | 8.10, 8.13 |
| T-10 | Reduce | SMART monitoring, a second copy that clients cannot overwrite, restore test | 0, 3 | 7.13, 8.13 |
| T-11 | Reduce | Encrypt the SSD, decide the unlock approach, record how the SSD was wiped | 1 | 7.8, 7.14, 8.24 |
| T-12 | Reduce | Least-privilege shares, no guest access, periodic permission review | 1 | 5.15, 5.18, 8.3 |
| T-13 | Reduce | Disable unneeded services, evaluate HTTPS for admin access, compare listening ports with the inventory | 1 | 8.9, 8.20, 8.24 |
| T-14 | Reduce | Defined update routine, evaluate unattended security updates, image the boot media before major upgrades | 1 | 8.8, 8.32 |
| T-15 | Reduce | Keep backup keys in two separate places, document the restore procedure, test it | 3 | 5.17, 8.13, 8.24 |
| T-16 | Reduce, Accept | Multi-factor authentication on the identity provider, device approval, access rules, key expiry, evaluate Tailnet Lock, compare with WireGuard | 1, 2 | 5.19, 5.23, 8.5 |
| T-17 | Reduce | Key management procedure covering generation, storage, rotation and revocation, with a revocation test | 2 | 5.17, 8.24 |
| T-18 | Reduce, Accept | Adequate power supply, temperature monitoring, safe shutdown routine, image of boot media. A UPS is accepted as out of budget **[TODO: confirm]** | 1 | 7.11, 7.13, 8.13 |
| T-19 | Reduce (verify only) | Disable UPnP, change default router credentials, record firmware version, no port forwards | 1 | 8.9, 8.20 |
| T-20 | Reduce | Backup success and failure notifications, periodic restore tests | 3 | 8.13, 8.15, 8.16 |
| T-21 | Reduce | Placeholder values, a pre-commit review checklist, secret scanning, rotate any secret that is ever exposed | All | 8.12 |

## 9. Assumptions and limitations

- Ratings are qualitative judgements and are not measured probabilities
- Baseline ratings assume the current state: default OMV setup on the LAN, with nothing exposed to the internet
- The assumptions in document 01, section 10 were confirmed or corrected on 27th October 2026. Others also have physical access to the NAS, which affects T-11
- Targeted attacks by a well-resourced adversary are out of scope, so ratings do not reflect that
- Router and other-device security are verified only for their effect on the NAS
- This register is not exhaustive. Threats found during Phase 0 and later phases will be added with new IDs, and existing IDs will not be reused
- Ratings will be reviewed after Phase 0 evidence and again in Phase 4

## 10. Link to later documents

Each treatment becomes one or more numbered requirements (SR-01 onwards) in `03-security-requirements.md`. The traceability matrix records the chain:

| Threat ID | Requirement ID | Control | Test ID | Result |
|---|---|---|---|---|
| T-xx | SR-xx | What was implemented | What proves it works | Evidence reference |

Residual risk after Phase 4, and any risk accepted knowingly, is recorded in `07-residual-risk.md`.

## 11. Open questions

- [x] Have the default OMV admin credentials been changed at baseline? No. They were still in use and were changed on 28th October 2026 (V-13, FND-01)
- [ ] What are the router's UPnP, port forwarding and firmware states? UPnP on with no mappings (FND-07), no port forwards (V-07). Firmware not yet recorded
- [x] Is my connection behind CGNAT? No (V-07, 30th October 2026)
- [x] Does the NAS currently hold the only copy of any data? No (V-14, V-15, 31st October 2026)
- [x] Is the SSD encrypted, and how was it wiped before reuse? Not encrypted and not yet in use (V-14). Wiped and reimaged before reuse (owner confirmed 31st October 2026, method not recorded). V-14 showed no partitions or file system on 28th October 2026
- [ ] Which identity provider will be used for Tailscale, and which multi-factor options does it support?
- [ ] Will Tailnet Lock be used, and what does it cost in extra maintenance?
- [ ] Does OMV offer multi-factor authentication for the admin interface, or will the VPN act as the gate?
- [x] Does the case vendor software need root access or network access? Not installed at baseline (owner confirmed 29th October 2026). Revisit only if it is installed
- [ ] Which secret-scanning approach will protect the repository?

## 12. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.1 | 24 October 2026 | Initial draft: method, threat sources, rating method, register T-01 to T-21, Tailscale trust analysis, treatment plan | Threat IDs follow the asset mapping in document 01, section 7 |
| 0.2 | 27th October 2026 | Header: link to document 05, which now exists (drafted with AI assistance) | Out-of-date reference |
| 0.3 | 27th October 2026 | T-08 and section 9: assumptions confirmed. T-11 rationale updated for physical access, likelihood flagged for owner review. T-03: CGNAT check inconclusive (drafted with AI assistance) | Owner answers on document 01, section 10 |
| 0.4 | 28th October 2026 | Section 7: Tailscale statements checked against the Tailscale documentation, corrections added, sources added as section 7.5 (drafted with AI assistance) | Resolve the verification TODO in section 7 |
| 0.5 | 29th October 2026 | Section 5.4 added: Phase 0 results so far, per threat, ratings unchanged and left for the owner. Section 5.2 and 11: answered items marked (drafted with AI assistance) | Phase 0 results |
| 0.6 | 30th October 2026 | Section 5.4, T-04: root `authorized_keys` review result added (drafted with AI assistance) | Phase 0 results |
| 0.7 | 30th October 2026 | Section 5.4, T-03 and T-19: V-07 result added (drafted with AI assistance) | Phase 0 results |
| 0.8 | 31st October 2026 | Section 5.2: CGNAT and SSD wipe items updated. Section 5.4: V-11, V-14 and V-15 results added for T-10 to T-13. Section 11: CGNAT, only-copy and SSD answered, router item updated (drafted with AI assistance) | Owner results |
