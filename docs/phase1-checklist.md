# Phase 1 Checklist

> **Status:** Draft v0.2 · Last updated: 2nd November 2026
> **Author:** William Drummond
> **Related:** [phase0-checklist.md](phase0-checklist.md) · [03-security-requirements.md](03-security-requirements.md) (SR-01 to SR-16, all Proposed) · [04-design-decisions.md](04-design-decisions.md) · [05-verification.md](05-verification.md)
> **Note:** Working draft prepared with AI assistance while Phase 0 finishes. Every step depends on requirements and decisions that are still open, and may change once V-08 is complete. No step is approved until section 1 is complete. Placeholders such as `<NAS-IP>` stay as placeholders in this file.

---

## 1. Before any change

Do not change the NAS or the router until every item is ticked.

- [ ] Phase 0 closed in document 05, section 8
- [ ] Open ports from V-08 (FND-09) identified, and any action added to this checklist. Router remote administration is off and TR-069 is not shown. Next: `nmap -sV` and `curl` against the public address from mobile data with the VPN off, plus a control scan of a public test host
- [ ] SR-01 to SR-16 accepted, changed or rejected, with priorities (document 03)
- [ ] Requirements added for the Phase 1 threats that have none: T-07, T-08, T-16, T-18 (document 03, section 4)
- [ ] Gaps resolved: the SD card in FND-08 (SR-12 covers the SSD only), and ports answered by the router in FND-09 (SR-09 covers NAS services only)
- [ ] Phase 1 completion criterion written (document 05, section 8)
- [ ] New tests written, with expected results, before they are run: SR-06, SR-13, SR-14, and access control tests V-20 to V-24 and V-26 (document 05, section 9)
- [ ] Decisions below recorded in document 04
- [ ] New SD card image taken, with date and SHA-256 hash recorded

## 2. Decisions to record

- [ ] Admin interface: HTTP or HTTPS, and which networks may reach it (SR-02)
- [ ] File sharing protocol and version
- [ ] SSD encryption, and how it is unlocked after a reboot (SR-12)
- [ ] Whether the SD card is encrypted, or the risk is accepted (FND-08)
- [ ] Failed SSH login limit (SR-06)
- [ ] Number of days allowed to install security updates, and the update routine (SR-10)
- [ ] How SSD health warnings reach me (SR-13)
- [ ] Accept or reject D-03, and which account holds its key
- [ ] Update D-02 so the temporary Claude Code SSH key stays until the final checks are done, or run those checks without Claude Code. D-02 currently removes the key once Tailscale is in place. The 5th January 2027 limit still applies
- [ ] NAS connection: Wi-Fi or Ethernet, and which unused radios and interfaces are disabled
- [ ] Network isolation: VLAN or guest network if the router supports it, otherwise accept the risk (T-07)
- [ ] Whether a UPS is accepted as out of budget (T-18)
- [ ] Whether rpcbind, mDNS, LLMNR and the DHCPv6 client are needed (FND-04)
- [ ] Accept or reject D-02
- [ ] Review the T-11 likelihood (FND-08)
- [ ] Optional: whether snapshots or versioning are available (input for Phase 3), date of the last system update, NAS temperature, and `sudo ss -tulpn` compared with V-04

## 3. Router

- [ ] Disable UPnP and confirm the setting after a router restart (SR-08)
- [ ] Confirm no port forwards and no DMZ host (SR-08)
- [ ] Carry out any router action from FND-09
- [ ] Re-run V-07

## 4. Accounts and SSH

Keep a working SSH session open throughout this section, and test each change from a second session. Check that the direct Ethernet link or a local console works before starting, in case of lockout.

- [ ] Create a separate administration account (SR-03)
- [ ] Add an SSH key for that account and confirm the key login works (SR-05)
- [ ] Confirm the administration account can use sudo
- [ ] Remove sudo rights from the daily account (SR-03)
- [ ] Disable SSH root login (SR-04)
- [ ] Disable SSH password login, only after key login is confirmed (SR-05)
- [ ] Limit repeated failed SSH logins (SR-06)
- [ ] Confirm the default OMV admin password is not in use (SR-01)
- [ ] Re-run V-09, V-12 and V-13

## 5. Tailscale

- [ ] Check the Tailscale statements in document 02, section 7 against the current documentation
- [ ] Protect the Tailscale account, and decide whether to use Tailnet Lock (T-16)
- [ ] Add each approved device and confirm each one needs access (T-08)
- [ ] Write and test the device revocation procedure (T-08)
- [ ] Run V-20 and V-26

## 6. Services and admin interface

- [ ] Disable the services that are not needed, and update the service inventory in document 01, section 6.3 (SR-07)
- [ ] Restrict the OMV admin interface to the agreed networks and protocol (SR-02)
- [ ] Check third-party software before installing it (SR-15)
- [ ] Re-run V-01, V-02, V-03 and V-04

## 7. Updates and monitoring

- [ ] Write the update routine, including an image of the boot media before major upgrades (SR-10)
- [ ] Install pending updates, including the openmediavault update (FND-06)
- [ ] Re-run V-10
- [ ] Set up vulnerability monitoring, if D-03 is accepted (SR-14)
- [ ] Set up SSD health and temperature warnings, and test that a warning reaches me (SR-13, T-18)
- [ ] Write the safe shutdown routine (T-18)

## 8. Storage and shares

Do this before any data is stored on the NAS.

- [ ] Run the load test and filesystem check, if deferred from Phase 0
- [ ] Encrypt the SSD and record the unlock approach (SR-12)
- [ ] Test a reboot and unlock
- [ ] Create shares with access limited to the accounts that need them and guest access off (SR-11)
- [ ] Check whether creating a share starts SMB, and update the service inventory
- [ ] Re-run V-04, V-11 and V-14

## 9. Final checks

- [ ] Re-run V-01 to V-15 and compare them with the Phase 0 baseline
- [ ] Re-run V-08 from outside the home network, over IPv4 and IPv6
- [ ] Run access control tests V-20 to V-24 and V-26, repeating V-20 and V-26 now that the admin interface is restricted
- [ ] Sanitise evidence and copy it to `evidence/phase1/`
- [ ] Update findings, rating changes and the log in document 05, sections 5 to 7
- [ ] Update the traceability matrix and the risk register
- [ ] Take a new SD card image of the hardened system, with date and SHA-256 hash recorded
- [ ] Remove the temporary Claude Code SSH key, log the removal and confirm it with V-12 (D-02)
- [ ] Owner review, then close Phase 1 in document 05, section 8

## 10. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.1 | 1st November 2026 | Checklist drafted from documents 02 to 05, not yet reviewed (drafted with AI assistance) | Owner request to prepare Phase 1 while Phase 0 finishes |
| 0.2 | 2nd November 2026 | Sections 1 and 2: open items carried over from Phase 0, optional checks marked as optional | Phase 0 closed |
