# Phase 1 Checklist

> **Status:** Draft v0.28 · Last updated: 9th November 2026
> **Author:** William Drummond
> **Related:** [phase0-checklist.md](phase0-checklist.md) · [03-security-requirements.md](03-security-requirements.md) (SR-01 to SR-20 accepted) · [04-design-decisions.md](04-design-decisions.md) · [05-verification.md](05-verification.md) · [phase1-changes.md](phase1-changes.md) (commands and OMV settings for sections 4, 6 and 7)
> **Note:** Prepared with AI assistance. Phase 0 is closed and decisions D-02 to D-13 are recorded. No change to the NAS or router until section 1 is complete. Each re-test is listed after the change it checks. Placeholders such as `<NAS-IP>` stay as placeholders in this file.

---

## 1. Before any change

Do not change the NAS or the router until every item is ticked.

- [x] Phase 0 closed in document 05, section 8 (2nd November 2026)
- [x] Open ports from V-08 (FND-09) identified, and any action added to this checklist. Only 7547 is open, on the router, most likely the ISP's TR-069 management. Risk accepted, no router action (document 05, section 5)
- [x] SR-01 to SR-16 accepted, changed or rejected, with priorities (document 03). All accepted
- [x] Requirements added for the Phase 1 threats that have none: T-07, T-08, T-16, T-18 (document 03, section 4). SR-17 to SR-20 accepted with priorities
- [x] Gaps resolved: the SD card in FND-08 (accepted risk, D-06), and ports answered by the router in FND-09 (port 7547, accepted risk)
- [x] Phase 1 completion criterion written (document 05, section 8)
- [x] New tests written, with expected results, before they are run: SR-06, SR-13, SR-14, and access control tests V-20 to V-24 and V-26 (document 05, sections 4.2 and 9: V-16 to V-19 and V-27 are new)
- [x] Decisions below recorded in document 04
- [x] If the D-02 sudo rule is accepted: add it on the NAS, test it and log it, before the new SD card image
- [x] New SD card image taken, with date and SHA-256 hash recorded (document 05, section 2.2)

## 2. Decisions to record

- [x] Admin interface: HTTP or HTTPS, and which networks may reach it (SR-02) (D-04)
- [x] File sharing protocol and version (D-05)
- [x] SSD encryption, and how it is unlocked after a reboot (SR-12) (D-06)
- [x] Whether the SD card is encrypted, or the risk is accepted (FND-08) (D-06, accepted)
- [x] Failed SSH login limit (SR-06) (D-07)
- [x] Number of days allowed to install security updates, and the update routine (SR-10) (D-08)
- [x] How SSD health warnings reach me (SR-13) (D-09)
- [x] Accept or reject D-03, and which account holds its key (accepted, separate account)
- [x] Update D-02 so the temporary Claude Code SSH key stays until the final checks are done, or run those checks without Claude Code. D-02 currently removes the key once Tailscale is in place. The 5th January 2027 limit still applies (done)
- [x] NAS connection: Wi-Fi or Ethernet, and which unused radios and interfaces are disabled (D-10)
- [x] Network isolation: VLAN or guest network if the router supports it, otherwise accept the risk (T-07) (D-11)
- [x] Whether a UPS is accepted as out of budget (T-18) (D-12)
- [x] Whether rpcbind, mDNS, LLMNR and the DHCPv6 client are needed (FND-04) (D-13)
- [x] Accept or reject D-02 (accepted)
- [x] Review the T-11 likelihood (FND-08) (stays Medium)
- [ ] Optional: whether snapshots or versioning are available (input for Phase 3), date of the last system update, NAS temperature, and `sudo ss -tulpn` compared with V-04

## 3. Router

- [x] Disable UPnP and confirm the setting after a router restart (SR-08). Done 3rd November 2026
- [x] Confirm no port forwards and no DMZ host (SR-08)
- [x] Carry out any router action from FND-09 (none, risk accepted)
- [x] Re-run V-07 (Pass, FND-07 treated)
- [x] Optional: check whether the router supports guest isolation or VLANs (D-11). If not, the risk stays accepted (not supported, risk accepted)

## 4. Accounts and SSH

Keep a working SSH session open throughout this section, and test each change from a second session. Check that the direct Ethernet link or a local console works before starting, in case of lockout. Make SSH, account and group changes in the OMV interface, as OMV overwrites hand edits. Steps: [phase1-changes.md](phase1-changes.md), section 2.

- [x] Create a separate administration account (SR-03). The account created at installation became the administration account, and a new daily account was created
- [x] Add an SSH key for that account and confirm the key login works (SR-05)
- [x] Confirm the administration account can use sudo
- [x] Remove sudo rights from the daily account (SR-03). The daily account has no sudo, no SSH and no login shell
- [x] Disable SSH root login (SR-04)
- [x] Disable SSH password login, only after key login is confirmed (SR-05)
- [x] Limit repeated failed SSH logins with fail2ban: 5 failures in 10 minutes blocks for 1 hour (SR-06, D-07)
- [x] Confirm the default OMV admin password is not in use (SR-01)
- [x] Re-run V-09, V-12, V-13, V-16 and V-24 (all Pass)

## 5. Tailscale

Steps: [phase1-changes.md](phase1-changes.md), section 5.

- [x] Check the Tailscale statements in document 02, section 7 against the current documentation (4th November 2026. A tailnet cannot be created with a passkey, so an identity provider is needed)
- [x] Protect the Tailscale account with multi-factor authentication or a passkey at the identity provider (SR-19). GitHub with an authenticator app, plus a backup admin with a passkey. Checked again in V-19
- [x] Choose device approval or Tailnet Lock (they cannot both be used) and record it in document 04 (SR-19, T-16). Device approval (D-14)
- [x] Write access rules that allow only approved devices to reach the NAS ports needed. The default policy allows everything (SR-19). Owner's devices to `tag:nas` on TCP 22 and 443 only
- [x] Add each approved device and confirm each one needs access (T-08). The NAS, the laptop and the phone (5th November 2026)
- [x] Write and test the device revocation procedure (T-08). phase1-changes.md, section 5.6, tested by V-26
- [x] Run V-19, V-20, V-22 and V-26 (all Pass, 5th November 2026)

## 6. Services and admin interface

Steps: [phase1-changes.md](phase1-changes.md), section 3.

- [x] Turn off rpcbind, LLMNR and mDNS. Keep the DHCPv6 client (SR-07, D-13)
- [x] Turn off Bluetooth. Move to Ethernet and turn off Wi-Fi if a cable reaches the router (D-10). No cable reaches at present, so Wi-Fi stays on
- [x] Turn on HTTPS with OMV's self-signed certificate, with plain HTTP redirected, and record the certificate fingerprint (SR-02, D-04)
- [x] Update the service inventory in document 01, section 6.3 (SR-07)
- [x] Check third-party software before installing it (SR-15). Tailscale checked and accepted (4th November 2026, phase1-changes.md, section 5.2). fail2ban checked in section 4
- [x] Re-run V-01, V-02, V-03, V-04 and V-21 (V-01, V-02, V-04 and V-21 Pass. V-03 stays open until V-10 in section 7)

## 7. Updates and monitoring

Steps: [phase1-changes.md](phase1-changes.md), section 4.

- [x] Write the update routine, including an image of the boot media before major upgrades (SR-10, D-08). phase1-changes.md, section 4.3, accepted by the owner (5th November 2026)
- [x] Check that automatic security updates are set up (SR-10, D-08). On, Debian security updates only. Summary email fails until D-09 (FND-10)
- [x] Install pending updates, including the openmediavault update (FND-06). omv-upgrade, 5th November 2026
- [x] Re-run V-10 (Pass, 5th November 2026. V-03 also Pass)
- [x] Set up vulnerability monitoring with the separate account and restricted key (SR-14, D-03), then run V-18. Set up 5th November 2026. V-18 Pass (owner, 6th November 2026)
- [ ] Set up SSD health and temperature warnings by email, and run V-17 (SR-13, D-09). Deferred out of Phase 1 (owner, 6th November 2026) until the alert method is chosen. SR-13 stays open
- [x] Write the safe shutdown routine and run V-27 (SR-20, D-12). Routine in phase1-changes.md, section 4.6, V-27 Pass (owner, 6th November 2026). Undervoltage warning at start (FND-12, Low)

## 8. Storage and shares

Steps: [phase1-changes.md](phase1-changes.md), section 6.

Do this before any data is stored on the NAS.

- [ ] Optional: temperature reading under load (T-18, document 02, section 5.3). Not part of the completion criterion
- [x] Check any plugin used for encryption before installing it (SR-15). `openmediavault-luksencryption`, accepted by the owner (5th November 2026, phase1-changes.md, section 6.2)
- [x] Encrypt the SSD and record the unlock approach: unlocked by hand after each reboot (SR-12, D-06). LUKS with the plugin, Btrfs on top (D-15), header backed up, 5th November 2026
- [x] Test a reboot and unlock. Full shutdown and power cycle, 6th November 2026: locked after start, unlocked by hand, Btrfs mounted by itself
- [x] Create shares with access limited to the accounts that need them and guest access off (SR-11). One media share for `<DAILY-USER>`, V-11 Pass (5th November 2026)
- [x] Check whether creating a share starts SMB, and update the service inventory. smbd started, and also WS-Discovery (FND-11). Document 01, section 6.3 updated
- [x] Re-run V-04, V-11 and V-14. V-11 Pass, V-14 Pass, V-04 Fail (FND-11), then Pass after the fix (6th November 2026)
- [x] Close FND-11 (phase1-changes.md, section 6.9), then re-run V-04. FND-11 Treated, V-04 Pass (owner, 6th November 2026)

## 9. Final checks

- [x] Re-run V-01 to V-14 and V-16 to V-19, and compare them with the Phase 0 baseline (V-15 is not repeated in Phase 1). Done 6th to 9th November 2026. V-17 deferred (owner, 6th November 2026)
- [x] Re-run V-08 from outside the home network, over IPv4 and IPv6. Pass (owner, 8th November 2026)
- [x] Run access control tests V-20 to V-24 and V-26, repeating V-20 and V-26 now that the admin interface is restricted. All Pass
- [x] Sanitise evidence and copy it to `evidence/phase1/`
- [x] Update findings, rating changes and the log in document 05, sections 5 to 7. FND-02 to FND-05 and FND-08 Treated, ratings stay as baseline (owner, 9th November 2026)
- [x] Update the traceability matrix, the risk register and the README status. Register ratings stay as baseline (owner, 9th November 2026)
- [ ] Take a new SD card image of the hardened system, with date and SHA-256 hash recorded. Postponed by the owner on 9th November 2026 (deviation, document 05, section 7). The most recent image is from 2nd November 2026
- [x] ~~Remove the temporary Claude Code SSH key, log the removal and confirm it with V-12 (D-02)~~ Not removed: the key is kept for Phase 2 (owner decision, 9th November 2026, D-02 change)
- [x] Owner review, then close Phase 1 in document 05, section 8. Closed 9th November 2026, with the SD card image postponed

## 10. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.1 | 1st November 2026 | Checklist drafted from documents 02 to 05, not yet reviewed (drafted with AI assistance) | Owner request to prepare Phase 1 while Phase 0 finishes |
| 0.2 | 2nd November 2026 | Sections 1 and 2: open items carried over from Phase 0, optional checks marked as optional | Phase 0 closed |
| 0.3 | 2nd November 2026 | Sections 1 and 2: requirements and decisions ticked, with decision IDs | Owner decisions |
| 0.4 | 2nd November 2026 | Section 1: step for the D-02 sudo rule added | Proposed Claude Code test access |
| 0.5 | 2nd November 2026 | Section 1: sudo rule step ticked | Rule added and tested |
| 0.6 | 2nd November 2026 | Section 1: completion criterion and new tests ticked | Drafted, owner to review |
| 0.7 | 2nd November 2026 | Sections 1 and 3: FND-09 and the requirement gaps ticked | FND-09 identified and accepted |
| 0.8 | 2nd November 2026 | Reviewed after Phase 0 closed: header and note updated, Phase 0 ticked, decision IDs and re-tests added to sections 3 to 9, steps linked to `phase1-changes.md`, Tailscale items split for SR-19, load test made optional as it was not deferred from Phase 0 (drafted with AI assistance) | Owner request |
| 0.9 | 2nd November 2026 | Section 1: priorities for SR-17 to SR-20 set | Owner decision |
| 0.10 | 3rd November 2026 | Section 1: SD card image ticked, section complete. Sections 3, 6 and 7: router isolation check ticked, Wi-Fi stays on, email alerts postponed | Owner checks |
| 0.11 | 3rd November 2026 | Section 3: UPnP turned off and V-07 re-run, section complete | First Phase 1 change |
| 0.12 | 4th November 2026 | Section 4 complete: account, SSH and fail2ban steps done, V-09, V-12, V-13, V-16 and V-24 Pass | Changes made |
| 0.13 | 4th November 2026 | Section 6: rpcbind, LLMNR, mDNS and Bluetooth turned off, HTTPS on, service inventory updated, re-tests run | Changes made |
| 0.14 | 4th November 2026 | Section 6: V-02 Pass, re-tests complete | Owner ran V-02 |
| 0.15 | 4th November 2026 | Section 5: Tailscale statements checked, device approval chosen (D-14), link to the change steps | Before the Tailscale set-up |
| 0.16 | 4th November 2026 | Section 6: SR-15 check done for Tailscale | Owner accepted the check |
| 0.17 | 4th November 2026 | Section 5: account protection and access rules done, NAS joined | Changes made |
| 0.18 | 5th November 2026 | Section 5: laptop and phone added and approved | Changes made |
| 0.19 | 5th November 2026 | Section 5 complete: revocation tested, V-19, V-20, V-22 and V-26 Pass | Owner results |
| 0.20 | 5th November 2026 | Section 7: automatic updates checked, pending updates installed, V-10 Pass | Owner checks and upgrade |
| 0.21 | 5th November 2026 | Section 7: update routine accepted | Owner decision |
| 0.22 | 5th November 2026 | Section 7: dashboard set up | Changes made |
| 0.23 | 5th November 2026 | Section 8: link to the change steps, encryption plugin check accepted, SSD encrypted, media share created, V-11 Pass | Start of section 8 |
| 0.24 | 6th November 2026 | Sections 7 and 8: shutdown and unlock tested, V-04, V-14 and V-27 run, FND-11 fix added | Owner tests at home |
| 0.25 | 6th November 2026 | Section 8: FND-11 Treated, V-04 Pass | FND-11 fix |
| 0.26 | 6th November 2026 | Section 7: V-18 Pass, V-17 deferred out of Phase 1 | Owner decisions |
