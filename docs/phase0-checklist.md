# Phase 0 Checklist

> **Status:** Draft v0.10 · Last updated: 31st October 2026
> **Author:** William Drummond
> **Related:** [05-verification.md](05-verification.md) (test plan V-01 to V-15) · [04-design-decisions.md](04-design-decisions.md) (D-01 baseline definition) · [../scripts/phase0-collect.sh](../scripts/phase0-collect.sh) · [../evidence/phase0/README.md](../evidence/phase0/README.md)
> **Note:** Step-by-step procedure for running the Phase 0 tests. Phase 0 is observation only. Placeholders such as `<NAS-IP>` stay as placeholders in this file.

---

## 1. Purpose

This checklist turns the Phase 0 test plan in document 05, section 4, into steps. Seven tests are collected by `scripts/phase0-collect.sh` on the NAS. The other eight are run by hand from another device, the router or the OMV interface.

All raw output goes to a location outside the repository. Only sanitised files go into `evidence/phase0/`.

## 2. Before starting

Do not run any test until every item is ticked. These match document 05, section 3.

- [x] SD card image taken, date and SHA-256 hash recorded (document 05, section 2.2)
- [x] D-01 decided, including the list of known earlier changes
- [x] Expected results for V-01 to V-15 confirmed and the `[DRAFT]` marker removed
- [x] Raw output location chosen, outside the repository
- [x] Router admin access confirmed
- [x] Second LAN device with `nmap` available
- [x] Outside network available (for example a laptop tethered to mobile data)
- [x] No sensitive data on the NAS

## 3. Tests collected by script (on the NAS)

Covers V-04, V-05, V-06, V-09, V-10, V-12 and V-14, plus installed package versions for V-03.

- [x] Copy `scripts/phase0-collect.sh` to the NAS
- [x] Check whether `lynis` and `smartctl` are installed. The script skips a missing tool rather than installing it. Installing one is a change to the system: decide, then record it in the Phase 0 log
- [x] Decide whether to run `sudo apt update` before V-10. It refreshes the package lists only, but it is still a change. Record the decision in the Phase 0 log. The script records the age of the existing lists either way
- [x] Run `sudo ./phase0-collect.sh` from your own account. With no argument it creates a new folder `~/phase0-raw-<date>-<time>` and hands it back to you, so no sudo is needed to read or copy it. A folder name can be given instead, but it must be new and inside your home folder or `/tmp`. Never give `/` or a system folder. Use `SSD_DEV=/dev/nvme0n1` in front of the command if `/dev/nvme0` is not the SSD
- [x] Copy the output folder off the NAS to the raw output location, check it with `sha256sum -c SHA256SUMS`, then delete it from the NAS
- [x] Record in the Phase 0 log that Lynis wrote its log and report under `/var/log`

## 4. Manual tests

Save raw output to the raw output location using the same `V-xx_short-description` naming.

### V-01 Open TCP ports (second LAN device)

- [x] `sudo nmap -sS -p- <NAS-IP> -oN <RAW-DIR>/V-01_tcp-scan.txt` (run as `nmap -sT` without sudo on 29th October 2026, see document 05, section 7)

### V-02 Open UDP ports (second LAN device)

- [x] `sudo nmap -sU --top-ports 100 <NAS-IP> -oN <RAW-DIR>/V-02_udp-scan.txt`
- [x] Note that UDP scans are slow and often report `open|filtered`. Record that state as it is reported

### V-03 Service versions (second LAN device)

- [x] `sudo nmap -sV <NAS-IP> -oN <RAW-DIR>/V-03_service-versions.txt`
- [x] Compare with `V-03_installed-versions.txt` from the script

### V-07 Router exposure (router admin page)

- [x] Port forwarding rules: none to the NAS
- [x] DMZ host: not set
- [x] UPnP: off. Checked: on, with no mappings (FND-07)
- [x] ~~Take screenshots to the raw output location. Review them before any are sanitised (addresses, MAC addresses, network names)~~ Skipped (owner decision, 31st October 2026)

### V-08 External exposure (outside network)

- [ ] Find the public address from the router status page. Do not record it in the repository
- [ ] From the outside network: `sudo env TZ=Europe/London nmap -Pn -sS -p- <PUBLIC-IP> -oN <RAW-DIR>/V-08_external-scan.txt`. `-Pn` because routers usually do not answer ping, so Nmap would otherwise skip the scan
- [ ] IPv6: on the NAS, note each address from `ip -6 addr show scope global` in the raw output location, not in the repository
- [ ] IPv6: on the outside network, check it has IPv6 with `curl -6 -s https://ifconfig.me`. If nothing is printed, record that the IPv6 scan could not be run from there
- [ ] IPv6: for each NAS address, `sudo env TZ=Europe/London nmap -6 -Pn -sS -p- <NAS-IPV6> -oN <RAW-DIR>/V-08_external-scan-ipv6.txt` (number the files if there is more than one address)
- [ ] Hand the files back: `sudo chown "$USER": <RAW-DIR>/V-08_*`
- [ ] Record the router's IPv6 firewall setting from the router admin page
- [ ] Sanitise with `scripts/sanitise.py`. It replaces reverse DNS names, which often contain the address, and flags addresses written with dashes
- [x] Record whether the router's WAN address is a CGNAT address (`100.64.0.0/10`). If it is, note that the scan may not reach the router at all. Not behind CGNAT

### V-11 Share permissions (OMV interface)

- [x] Storage, Shared Folders: list each share and its permissions
- [x] Services, SMB/CIFS: whether enabled, and whether guest access is allowed on any share
- [x] If no shares exist, record that

### V-13 Default credentials (OMV interface)

- [x] Try to log in with the publicly documented default OMV admin credentials
- [x] Record only whether the login succeeded. If it did, this is a serious finding: record it first, then change the password and log the change with a timestamp (document 05, section 4)

### V-15 Existing copies of data (manual)

- [x] For each data type in document 01, section 7.1, record whether another copy exists and where, described in general terms (for example "external drive")

## 5. After the tests

- [ ] Write one Phase 0 log row per test in document 05, section 7
- [ ] Sanitise each raw file using document 05, section 2.4, and the header in `evidence/phase0/README.md`
- [ ] Copy sanitised files into `evidence/phase0/`
- [ ] Fill in the Actual result and Pass or fail columns in document 05, section 4
- [ ] Record findings as FND-xx in document 05, section 5, and any rating changes in section 6
- [ ] Fill in the Baseline observed column in document 01, section 6.3, and the Baseline result column in the matrix

## 6. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.1 | 27th October 2026 | Checklist created (drafted with AI assistance) | Procedure for running Phase 0 tests |
| 0.2 | 28th October 2026 | Section 2: SD card image, D-01 and expected results ticked | Prerequisites completed |
| 0.3 | 28th October 2026 | Section 2: raw output location and router access ticked | Owner confirmed |
| 0.4 | 28th October 2026 | Section 2: nmap, outside network and no sensitive data ticked. All prerequisites complete | Owner confirmed |
| 0.5 | 28th October 2026 | Section 3: run step updated for the safer collection script (default output folder, output handed back to the owner) and a delete step added (drafted with AI assistance) | The first run with `/` as the output folder locked the NAS root folder |
| 0.6 | 29th October 2026 | Section 3: completed steps ticked. Copy and delete step left open until deletion from the NAS is confirmed | Script-collected tests run |
| 0.7 | 29th October 2026 | Section 3: copy and delete step ticked. Section 4: V-01 to V-03 ticked, V-01 deviation noted | Owner confirmed deletion. Scans run |
| 0.8 | 30th October 2026 | Section 4: V-07 and the CGNAT check ticked | Owner results |
| 0.9 | 30th October 2026 | Section 4, V-08: `-Pn` and UK time added to the scan, IPv6 steps added (owner confirmed), hand-back, router IPv6 firewall and sanitising steps added (drafted with AI assistance) | NAS has public IPv6 addresses |
| 0.10 | 31st October 2026 | Section 4: V-11, V-13 and V-15 ticked, V-07 screenshots skipped | Owner results. V-13 was done on 28th October 2026 but not ticked |
