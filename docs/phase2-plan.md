# Phase 2 Plan

> **Status:** Draft v0.05 · Last updated: 9th November 2026
> **Author:** William Drummond
> **Related:** [01-scope-and-assets.md](01-scope-and-assets.md) (phase 2 goal, service inventory) · [02-threat-analysis.md](02-threat-analysis.md) (section 7.4 questions, T-16, T-17) · [03-security-requirements.md](03-security-requirements.md) · [04-design-decisions.md](04-design-decisions.md) (D-02, D-14) · [05-verification.md](05-verification.md)
> **Note:** Drafted with AI assistance on 8th November 2026, as proposals for the owner. Nothing here is decided. No change to the NAS or router for Phase 2 until Phase 1 is closed (document 05, section 8) and section 5 of this plan is complete. Placeholders such as `<WG-PORT>` stay as placeholders in this file.

---

## 1. Goal

Add self-hosted WireGuard as a remote access path, or replace Tailscale with it, and compare the two (document 01, objective O-6). Outputs: a comparison write-up and a key management procedure (T-17).

## 2. Questions for the owner

Answer these before the decisions in section 3 are recorded. Questions 2.1 to 2.3 come from document 02, section 7.4.

### 2.1 Trust and dependencies

1. What does self-hosted WireGuard remove from the Tailscale trust list (document 02, section 7.2): the coordination service, the identity provider, vendor logs, the relay servers?
2. What does it add: one UDP port open to the internet, key management by hand, no central device list, handling a change of the home public address?
3. Is the extra control worth the extra maintenance for a one-person home system?
4. How much weight does removing the identity provider dependency carry? (Owner, 4th November 2026: a strong reason to move to WireGuard if possible.)

### 2.2 Shape of the set-up

1. **Replace or run both?** Keep Tailscale as a fallback while WireGuard is tested, then decide. Running both for a while makes the comparison fair, but adds a second way in.
   - **Owner answer, 8th November 2026:** run WireGuard in parallel with Tailscale. The decision on which one to keep is deferred until later in Phase 2. When that decision is made still needs to be set (for example, after the comparison tests in section 6)
2. **Where does WireGuard run?** On the NAS (the kernel module, set up by hand or with an OMV plugin, which would need an SR-15 review), or on the router, if the ISP router supports it at all.
   - **Owner answer, 9th November 2026:** on the NAS, set up by hand (kernel module and `wg-quick`), not with an OMV plugin, so no SR-15 plugin review is needed
3. **What can a peer reach?** Only the NAS on 22, 443 and 445, as Tailscale allows now, or the whole home network? WireGuard has no access rules of its own: `AllowedIPs` controls routing, not which ports a peer may use. Limiting ports needs a firewall on the NAS. The Phase 1 host firewall was optional (phase1-changes.md, section 4), so this would make it required for the WireGuard interface.
   - **Owner answer, 9th November 2026:** only the NAS, on 22, 443 and 445, the same as the Tailscale access rules. A firewall on the NAS for the WireGuard interface becomes required
4. **Full or split tunnel on the clients?** Only NAS traffic through the tunnel (split), or all traffic (full)?
   - **Owner answer, 9th November 2026:** split tunnel. Only NAS traffic goes through the tunnel
5. **IPv4, IPv6 or both?** The router has no IPv6 pinholes (V-08). IPv6 access would need one, which is a second exception to SR-09.
   - **Owner answer, 9th November 2026:** IPv4 only. No IPv6 pinhole, so IPv6 stays closed as in V-08

### 2.3 Exposure and the router

1. A port forward for one UDP port to the NAS is needed. This changes SR-08 (no port forwards) and SR-09 (nothing reachable from the internet) into "one documented exception". Do you accept that, and how should the requirements be worded (section 4)?
   - **Owner answer, 9th November 2026:** accepted. One UDP port forward to the NAS, as a documented exception to SR-08 and SR-09, worded as drafted in section 4
2. Which UDP port? Not the WireGuard default, to cut scan noise, but this is not a security control. Recorded only as `<WG-PORT>` in the repository.
   - **Owner answer, 9th November 2026:** a non-default high port, recorded only as `<WG-PORT>` in the repository
3. Does the ISP router allow a UDP port forward to one address, and does it stay after a router restart or firmware update?
   - **Owner answer, 9th November 2026:** the router supports a UDP port forward to one address. Whether it stays after a restart or firmware update is checked when it is set up
4. The home public IPv4 address can change. Options: check by hand and update the clients, dynamic DNS (DDNS is off now, V-07, and a DDNS provider is a new third party), or a script on the NAS that reports the address. Which one, and does it bring back a dependency you wanted to remove?
   - **Owner answer, 9th November 2026:** a script on the NAS that tells the owner the new address. No DDNS provider

### 2.4 Keys (T-17)

1. Where are key pairs made: on each device, so private keys never move (recommended), or on the NAS?
   - **Owner answer, 9th November 2026:** on each device, so private keys never move
2. Where are private keys kept? On the device only. The NAS's private key is in `/etc/wireguard/`, readable by root only. Is a copy kept in Proton Pass for recovery, or is a new key made instead?
   - **Owner answer, 9th November 2026:** on the device only, no copy kept. A lost device's key is revoked and a new key made
3. Use a preshared key per peer as well? It adds a second secret per device and some protection against future quantum attacks.
   - **Owner answer, 9th November 2026:** yes, a preshared key per peer
4. How often are keys rotated: never, every 180 days (matching the Tailscale key expiry), or every 12 months?
   - **Owner answer, 9th November 2026:** every 180 days, matching the Tailscale key expiry
5. Revocation: remove the peer from the NAS configuration and reload. Target: within 5 minutes, as for Tailscale (SR-18, V-26).
   - **Owner answer, 9th November 2026:** within 5 minutes, as for Tailscale (SR-18)
6. Where is the list of peers and their public keys kept? Public keys are not secret, but they identify devices, so they stay out of the repository.
   - **Owner answer, 9th November 2026:** in Proton Pass, outside the repository

### 2.5 Monitoring and recovery

1. WireGuard writes no login log. `wg show` gives the last handshake time for each peer. Is that enough, or should handshakes be checked on a timer, like the vulnerability dashboard (D-03)?
   - **Owner answer, 9th November 2026:** `wg show` by hand during Phase 2. A timer check is optional and can come later
2. If the tunnel fails while you are away, what is the way back in: Tailscale while both run, or nothing until you are home?
   - **Owner answer, 9th November 2026:** follows from 2.2.1: Tailscale, while both run
3. Does the tunnel come up by itself after a reboot, given that the SSD is unlocked by hand (D-06)? WireGuard does not need the SSD, but SMB does.
   - **Owner answer, 9th November 2026:** yes, through the `wg-quick` service. SMB is available only after the SSD is unlocked (D-06)

### 2.6 Effect on Phase 1 set-up

1. D-02: Claude Code's key is limited to the laptop's Tailscale address. If Tailscale goes, the `from=` limit moves to the laptop's WireGuard address, and D-02 needs a change record.
   - **Owner answer, 9th November 2026:** follows from 2.2.1: while Tailscale stays, the key's `from=` limit stays on the laptop's Tailscale address, so D-02 needs no change yet
2. SR-02 says the admin interface is reachable from "the LAN and the VPN". Does "the VPN" now mean WireGuard, Tailscale or both?
   - **Owner answer, 9th November 2026:** both, while both run
3. D-14 (device approval) covers Tailscale only. WireGuard's equivalent is "a peer exists only if I add its public key".
   - **Owner answer, 9th November 2026:** accepted: a peer exists only if the owner adds its public key

## 3. Decisions to record (document 04)

To be written once section 2 is answered. Proposed numbers follow the last decision, D-15.

| Proposed | Decision | Questions |
|---|---|---|
| D-16 | Replace Tailscale or run both, and for how long. Owner, 8th November 2026: run both, decision on which to keep deferred (2.2.1) | 2.1, 2.2.1 |
| D-17 | Where WireGuard runs, and how it is installed. Owner, 9th November 2026: on the NAS, by hand | 2.2.2 |
| D-18 | What peers can reach, and the NAS firewall for the WireGuard interface. Owner, 9th November 2026: NAS only on 22, 443 and 445, split tunnel, IPv4 only | 2.2.3, 2.2.4, 2.2.5 |
| D-19 | Port forward, port choice and handling a change of public address. Owner, 9th November 2026: one UDP port forward accepted, non-default high port. Router supports a UDP forward (restart check when set up), address changes reported by a script on the NAS | 2.3 |
| D-20 | WireGuard key management procedure. Owner, 9th November 2026: keys made on each device, no copies, preshared keys, 180-day rotation, revocation within 5 minutes, peer list in Proton Pass | 2.4, 2.5.1 |
| Change to D-02 | Claude Code's key limit, if Tailscale is removed | 2.6.1 |

## 4. Requirements to propose (document 03)

Drafts only. The owner accepts, changes or rejects each one and sets its priority. Accepted by the owner on 9th November 2026 and moved to document 03: SR-08 and SR-09 changed, SR-21 and SR-22 Must, SR-23 Should.

| Proposed ID | Requirement | Threats |
|---|---|---|
| SR-08 (change) | The router has no port forwards except one UDP port to the NAS for WireGuard, no DMZ host, and UPnP disabled | T-03, T-19 |
| SR-09 (change) | No NAS service is reachable from the internet over IPv4 or IPv6, except the WireGuard UDP port, which answers only peers with a known key | T-03 |
| SR-21 | A WireGuard peer can reach only the NAS services it needs (22, 443, 445), enforced by a firewall on the NAS | T-07, T-13 |
| SR-22 | WireGuard keys follow a written procedure: made on the device, private keys never copied off it, a list of peers kept outside the repository, rotation at a set interval | T-17 |
| SR-23 | A WireGuard peer can be revoked within 5 minutes, using the written procedure | T-08, T-17 |

## 5. Before any Phase 2 change

- [x] Phase 1 closed in document 05, section 8 (9th November 2026, with the SD card image postponed)
- [x] Questions in section 2 answered (9th November 2026). Section 2.1 is reasoning for the comparison write-up
- [x] Decisions in section 3 recorded in document 04 (D-16 to D-20 accepted, 9th November 2026)
- [x] Requirements in section 4 accepted, changed or rejected, with priorities (9th November 2026)
- [x] Phase 2 completion criterion written (document 05, section 8), agreed by the owner on 9th November 2026
- [x] Phase 2 tests written, with expected results, before they are run (section 6). Expected results confirmed by the owner on 9th November 2026
- [ ] New SD card image taken, with date and SHA-256 hash recorded. Postponed by the owner on 9th November 2026 (deviation): Phase 2 changes start without it. The most recent image is from 2nd November 2026

## 6. Draft test plan

New test IDs start at V-28 (V-25 is kept for Phase 3). Expected results to be confirmed by the owner before any test is run. Run-from entries follow D-02: Claude Code runs tests on the NAS only when the owner approves them by ID.

### 6.1 New tests

| Test ID | Requirement | What it checks | Tool and command | Run from | Expected result |
|---|---|---|---|---|---|
| V-28 | SR-09 (changed) | External exposure with WireGuard on | `nmap -Pn -sS -p- <PUBLIC-IP>`, then `sudo nmap -Pn -sU -p <WG-PORT> <PUBLIC-IP>`, plus IPv6 as in V-08, with a control scan first | Outside network (owner) | TCP: same as the Phase 1 V-08 result. UDP `<WG-PORT>`: `open\|filtered`, no reply to Nmap's probes, the same as a closed, filtered port. WireGuard does not answer packets without a valid key |
| V-29 | SR-09 (changed) | Unknown key is ignored | A WireGuard client with a new key pair that is not configured on the NAS tries to connect. `sudo wg show` on the NAS | Owner's device, outside network. Claude Code for `wg show` when approved | No handshake on the client. No new peer or handshake shown on the NAS |
| V-30 | SR-21 | Approved peer, allowed services | From an approved peer: OMV over HTTPS, SSH with a key, SMB share | Phone on mobile data, Wi-Fi off | All three work, as in V-20 |
| V-31 | SR-21 | Approved peer, everything else | `nmap -Pn -sS -p- <NAS-WG-IP>` from the peer, and a connection attempt to another LAN device | Laptop as a peer, outside network | Only 22, 443 and 445 open on the NAS's WireGuard address. Other LAN devices not reachable (D-18) |
| V-32 | SR-23 | Revocation | Remove a peer using the procedure, then try to connect from it | Owner | Refused within 5 minutes. `wg show` no longer lists the peer |
| V-33 | SR-22 | Key rotation | Rotate one peer's key using the procedure, then try the old key | Owner | New key connects. Old key gets no handshake |
| V-34 | SR-22 | Key storage | `sudo ls -l /etc/wireguard/` and `sudo stat` on the private key file | Claude Code over SSH, when approved | Private key owned by root, mode 600. No private keys in the repository or in `~/NAS-Evidence/` |
| V-35 | D-17 | Restart | Reboot the NAS, then connect from a peer before the SSD is unlocked | Owner | Tunnel comes up by itself. SSH and OMV reachable. SMB share available only after the unlock (D-06) |
| V-36 | D-19 | Public address change | If the router can renew its address on demand: renew it, then connect from a peer | Owner | The address script finds the new address within 15 minutes and writes it to its file on the NAS. The owner reads it over Tailscale and updates the client. The peer reconnects within 30 minutes of the change (D-19) |

### 6.2 Phase 1 tests to repeat, with new expected results

| Test ID | Change to the expected result |
|---|---|
| V-01 | 22, 443 and 445 open on the LAN address, as in Phase 1. No new TCP port |
| V-02 | `<WG-PORT>`/UDP shows as `open\|filtered`. No other new UDP port |
| V-04 | One new listener, WireGuard on `<WG-PORT>`/UDP, matching the updated service inventory (document 01, section 6.3) |
| V-07 | One UDP port forward to the NAS, for `<WG-PORT>` only. No DMZ host. UPnP off |
| V-08 | Replaced by V-28 |
| V-20 | Unchanged: OMV over HTTPS and SSH reachable over Tailscale from an approved device, with the WireGuard firewall in place (document 05, section 8) |
| V-26 | If Tailscale is kept: unchanged. If removed: replaced by V-32 |

### 6.3 Comparison measures

Not pass or fail tests. Recorded for both Tailscale and WireGuard for the comparison write-up.

| Measure | How it is recorded |
|---|---|
| Third parties trusted | List from document 02, section 7.2, and the equivalent for WireGuard |
| Ports open to the internet | From V-08 and V-28 |
| Time to add a device | Timed by the owner |
| Time to revoke a device | From V-26 and V-32 |
| Ongoing maintenance | Tasks per month, estimated by the owner |
| What still works when away if the vendor or the home address changes | Owner's assessment |
| Visibility of who connected | Tailscale admin console compared with `wg show` |

## 7. Draft completion criterion (document 05, section 8)

Phase 2 is complete when: the decisions in section 3 are recorded; the requirements in section 4 are verified by the tests in section 6, with evidence in `evidence/phase2/`; the key management procedure is written and V-32 and V-33 pass using it; the comparison write-up is done; and an SD card image of the Phase 2 system is recorded.

## 8. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.01 | 8th November 2026 | First draft: questions, decisions, requirements, test plan and completion criterion (drafted with AI assistance) | Owner request, while the Phase 1 V-08 scans run |
