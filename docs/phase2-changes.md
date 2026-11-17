# Phase 2 Change Steps

> **Status:** Draft v0.5 · Last updated: 15th November 2026
> **Author:** William Drummond
> **Related:** [phase2-plan.md](phase2-plan.md) (sections 5 and 6) · [04-design-decisions.md](04-design-decisions.md) (D-02, D-06, D-16 to D-20) · [03-security-requirements.md](03-security-requirements.md) (SR-08, SR-09, SR-21 to SR-23) · [05-verification.md](05-verification.md) (section 8, Phase 2 log)
> **Note:** Drafted with AI assistance on 9th November 2026, for OMV 8 on Debian 13 and the Raspberry Pi kernel seen in V-05. Sections 2.1 to 5 have been run for the laptop, and section 4 for the phone without a working handshake (see the Phase 2 log). Sections 6 to 8 were not run: Phase 2 was closed on 12th November 2026 with Tailscale kept (D-16), so there is no port forward and no address script. Each change needs the owner's approval for that change, and is logged in document 05, section 7, with the time in UK time. Placeholders such as `<WG-PORT>`, `<NAS-WG-IP>` and `<PUBLIC-IP>` stay as placeholders in this file. Real values, keys and the peer list stay out of the repository (D-20)

---

## 1. Before starting

- Phase 2 plan, section 5 complete: Phase 1 closed, the SD card image taken and its SHA-256 hash recorded
- Add a Phase 2 log to document 05, section 7, and copy the Phase 2 tests from phase2-plan.md, section 6 into document 05, section 4, with their expected results
- Tailscale stays on throughout (D-16). It is the way back in if a WireGuard or firewall step goes wrong. Keep one SSH session open over Tailscale while changing the tunnel or the firewall, and test from a second session
- Recovery path if both remote paths fail: the home LAN, or a keyboard and screen on the NAS
- The NAS needs a fixed LAN address for the port forward. Check in the router whether the NAS has a DHCP reservation, or in OMV whether its address is static. If neither, set a reservation in the router first (a router change, approved and logged separately)
- **Claude Code's sudo rule (D-02)** does not cover the new checks. For Claude Code to run V-04, V-31 and V-34 parts on the NAS, the owner adds these read-only commands to `/etc/sudoers.d/claude-readonly`, after checking each path with `command -v`, and records the change in D-02:
  ```
  /usr/bin/wg show, \
  /usr/sbin/nft list table inet wg_nas, \
  /usr/bin/ls -l /etc/wireguard
  ```
  `wg show` prints peer public keys and their current public addresses, so its raw output stays outside the repository

## 2. WireGuard on the NAS (D-17)

### 2.1 Check before installing (SR-15)

`wireguard-tools` and `nftables` come from Debian's own repository, not a third party. The WireGuard module is part of the Raspberry Pi kernel. Check:
```
apt-cache policy wireguard-tools nftables
sudo modprobe wireguard && lsmod | grep wireguard
```
Both packages should come from `deb.debian.org`. If `modprobe` fails, stop and log it: the kernel lacks the module.

### 2.2 Install

```
sudo apt-get install wireguard-tools nftables
```
Do **not** enable the `nftables` service. Debian's `/etc/nftables.conf` starts with `flush ruleset`, which would delete Tailscale's own firewall rules every time the service starts. The WireGuard firewall in section 3 is loaded by the tunnel itself instead.

Rollback: `sudo apt-get remove wireguard-tools` (leave `nftables` if anything else already used it).

### 2.3 The NAS's keys (D-20)

The private key is made on the NAS and never leaves it:
```
sudo sh -c 'umask 077; wg genkey > /etc/wireguard/nas.key'
sudo sh -c 'wg pubkey < /etc/wireguard/nas.key > /etc/wireguard/nas.pub'
sudo ls -l /etc/wireguard
```
`nas.key` must be `-rw------- root root` (V-34). `nas.pub` is the public key that goes into each client. The SD card is not encrypted, so `nas.key` is readable from the card or an image of it (D-17). Keep SD card images somewhere only you can reach.

### 2.4 Tunnel addresses

Choose a small private range for the tunnel, recorded only as `<WG-SUBNET>`. It must not overlap the home LAN or Tailscale's `100.64.0.0/10`. The NAS takes one address in it (`<NAS-WG-IP>`), and each peer another (`<PEER-WG-IP>`). Keep the real values in Proton Pass with the peer list.

`<NAS-WG-IP>` and `<PEER-WG-IP>` are single host addresses, written without a `/` suffix. The NAS takes the address ending `.1`, and each peer the next free one (`.2`, `.3` and so on). Do not use the range's own address ending `.0`. The suffix is added in the configuration files: `/24` on the NAS's `Address`, `/32` everywhere else.

### 2.5 Tunnel configuration

Create `/etc/wireguard/wg0.conf` as root, mode 600:
```
[Interface]
Address = <NAS-WG-IP>/24
ListenPort = <WG-PORT>
PostUp = wg set %i private-key /etc/wireguard/nas.key
PreUp = nft -f /etc/wireguard/wg0-firewall.nft
PostDown = nft delete table inet wg_nas

# One block per peer, added in section 4
```
`PreUp` loads the firewall (section 3) before the interface exists, so the tunnel never runs without it. `PostDown` removes it with the tunnel. The private key stays in its own file instead of in this one.

Check that the NAS does not route between networks, so peers cannot reach other devices even if a rule is wrong:
```
sysctl net.ipv4.ip_forward
```
It should be `0`. If it is `1`, find out what set it (Tailscale does not need it unless it is a subnet router) before going on.

## 3. Firewall for the WireGuard interface (SR-21, D-18)

Create `/etc/wireguard/wg0-firewall.nft` as root, mode 600:
```
table inet wg_nas {}
delete table inet wg_nas
table inet wg_nas {
    chain input {
        type filter hook input priority filter; policy accept;
        iifname "wg0" ct state established,related accept
        iifname "wg0" ct state invalid drop
        iifname "wg0" tcp dport { 22, 443, 445 } accept
        iifname "wg0" drop
    }
    chain forward {
        type filter hook forward priority filter; policy accept;
        iifname "wg0" drop
        oifname "wg0" drop
    }
}
```
- The first two lines let the file be loaded again without an error
- Every rule matches only traffic on `wg0`. LAN and Tailscale traffic pass through this table unchanged (policy accept), so Tailscale's own rules keep working
- A peer can open only SSH, HTTPS and SMB on the NAS. Everything else from the tunnel is dropped, and nothing is forwarded to or from it

Check the file before first use:
```
sudo nft -c -f /etc/wireguard/wg0-firewall.nft
```
**Samba:** if OMV's SMB settings include `hosts allow` (Services, SMB/CIFS, Settings, extra options), add `<WG-SUBNET>`, or SMB is refused over the tunnel.

Rollback: `sudo nft delete table inet wg_nas`.

## 4. Peers (D-20)

### 4.1 Making a peer

For each device, on the device itself:

- **Phone:** install the official WireGuard app from Google Play, checking the publisher is WireGuard Development Team. It is no longer on F-Droid (owner, 10th November 2026). Not a Termux package or a third-party client. In the app, add a tunnel, **Create from scratch**, and let the app generate the key pair. Copy only its public key
- **Laptop:** first `sudo apt-get install wireguard-tools` (the same package as on the NAS, from the laptop's own distribution; it creates `/etc/wireguard`). Then `sudo sh -c 'umask 077; wg genkey > /etc/wireguard/nas-peer.key'` and `sudo sh -c 'wg pubkey < /etc/wireguard/nas-peer.key'`

Then, on the NAS, make the preshared key for that peer:
```
wg genpsk
```
The preshared key is shared by design: it goes into the NAS's peer block and into the device, typed or pasted over an SSH session through Tailscale. It is not stored anywhere else: not in Proton Pass, the repository, Telegram or notes.

### 4.2 Adding the peer on the NAS

Add a block to `/etc/wireguard/wg0.conf`:
```
[Peer]
# <PEER-NAME>
PublicKey = <PEER-PUBLIC-KEY>
PresharedKey = <PSK>
AllowedIPs = <PEER-WG-IP>/32
```
Then load the new peer without dropping the others, and check it is listed:
```
sudo bash -c 'wg syncconf wg0 <(wg-quick strip wg0)'
sudo wg show wg0 allowed-ips
```
Add the device's name, public key, tunnel address and the date to the peer list in Proton Pass.

### 4.3 The device's tunnel

```
[Interface]
PrivateKey = (made on the device in 4.1)
Address = <PEER-WG-IP>/32

[Peer]
PublicKey = <NAS-PUBLIC-KEY>
PresharedKey = <PSK>
Endpoint = <PUBLIC-IP>:<WG-PORT>
AllowedIPs = <NAS-WG-IP>/32
PersistentKeepalive = 25
```
On the laptop, the file is `/etc/wireguard/nas.conf`, made with `install -m 600`, and `PrivateKey` is replaced by `PostUp = wg set %i private-key /etc/wireguard/nas-peer.key`, as on the NAS. Until section 6 is done, the laptop's `Endpoint` is the NAS's LAN address, so the first tests run from home; change it to `<PUBLIC-IP>` after section 6.

`AllowedIPs` holds only the NAS's tunnel address, so only NAS traffic uses the tunnel (split tunnel, D-18). No `DNS` line: the NAS is reached by `<NAS-WG-IP>`. `PersistentKeepalive` keeps the connection open through mobile networks, and can be removed if not needed.

## 5. Starting the tunnel (D-17)

```
sudo systemctl enable --now wg-quick@wg0
sudo wg show
sudo nft list table inet wg_nas
```
`wg show` lists the interface, its port and each peer. The `nft` output shows the table from section 3.

Rollback: `sudo systemctl disable --now wg-quick@wg0`. This also removes the firewall table (PostDown).

If the start fails, `sudo journalctl -u wg-quick@wg0 -n 30 --no-pager` shows the command that failed. A failed start removes `wg0` but leaves the firewall table loaded, because `PostDown` only runs when a running tunnel is stopped. The table matches only `wg0`, so it changes nothing, and the file reloads it without an error on the next start. To remove it: `sudo nft delete table inet wg_nas`.

`wg-quick` reads `wg0.conf` only when the tunnel starts. After editing the file, run `sudo systemctl stop wg-quick@wg0`, check with `ip -br addr show wg0` that `wg0` has gone, then run `sudo systemctl start wg-quick@wg0`.

Check from the laptop, at home:
```
sudo wg-quick up nas
nc -zv -w 3 <NAS-WG-IP> 22
nc -zv -w 3 <NAS-WG-IP> 443
sudo wg show
sudo wg-quick down nas
```
Both `nc` checks should succeed, and `wg show` should show a recent handshake and data both ways. `ping` gets no reply: the section 3 firewall drops everything from the tunnel except TCP 22, 443 and 445, ICMP included, so a ping that stalls is expected.

### 5.1 After sections 2 to 5

Before the router is changed, nothing outside the home network can reach the tunnel. Run:
- V-04 (Claude Code, when approved): one new listener, UDP `<WG-PORT>`
- V-01 and V-02 from the laptop on the LAN: no new TCP port, `<WG-PORT>`/UDP `open|filtered`
- V-34 (Claude Code, when approved): key and configuration files root-only, mode 600
- V-20: Tailscale access still works with the WireGuard firewall loaded

## 6. Router port forward (SR-08, D-19)

A router change: approved by the owner and logged separately.

1. In the router admin page, add one port forward: UDP only, external port `<WG-PORT>`, to the NAS's LAN address, internal port `<WG-PORT>`
2. Leave UPnP off and the DMZ unset
3. Restart the router and check the forward is still there (the open point in D-19)
4. Update document 01, section 6.3 (service inventory): WireGuard running, one UDP port from the internet

Rollback: delete the forward.

### 6.1 After section 6

From outside the home network. The router may not loop the public address back to the LAN, so test from mobile data with Wi-Fi off, not from home:
- V-07 (owner): one UDP forward for `<WG-PORT>`, no DMZ, UPnP off
- V-30: phone connects, then OMV over HTTPS, SSH with a key and the SMB share all work
- V-31: laptop as a peer, outside the home network. Only 22, 443 and 445 open on `<NAS-WG-IP>`. No other home device reachable
- V-29: a client with a new, unregistered key gets no handshake
- V-28 (owner): external scan. TCP as in Phase 1 V-08, `<WG-PORT>`/UDP `open|filtered`
- V-35: reboot the NAS, connect before unlocking the SSD. Tunnel up, SSH and OMV work, SMB only after the unlock

## 7. Public address script (D-19)

### 7.1 Choice to make first

Finding the home public address from inside the network means asking something outside it. Options:
1. **A DNS lookup to a public resolver**, such as `dig +short -4 txt ch whoami.cloudflare @1.1.1.1`. Sends only the question. Needs `bind9-dnsutils`
2. **An HTTPS "what is my IP" service.** The same idea over HTTPS, with `curl`
3. **The router's own status page.** No outside party, but the ISP router has no supported way for a script to read it

D-19's "no third party" means no outside service keeps or forwards the address. Options 1 and 2 still contact one each time they run. Decide which, and record it in D-19, before section 7.2. The script below uses option 1.

### 7.2 The script

`/usr/local/bin/wg-public-ip`, owned by root, mode 755:
```
#!/bin/sh
# Writes the home public IPv4 address to a file only the owner can read (D-19)
set -eu
dir="$HOME/wg-public-ip"
new=$(dig +short -4 txt ch whoami.cloudflare @1.1.1.1 | tr -d '"')
case "$new" in
    ''|*[!0-9.]*) echo "lookup failed" >&2; exit 1 ;;
esac
umask 077
mkdir -p "$dir"
old=$(cat "$dir/current" 2>/dev/null || true)
if [ "$new" != "$old" ]; then
    printf '%s\n' "$new" > "$dir/current.tmp" && mv "$dir/current.tmp" "$dir/current"
    printf '%s %s\n' "$(date -u +%FT%TZ)" "$new" >> "$dir/history"
    logger -t wg-public-ip "public address changed"
fi
```
The system log records only that the address changed, not the address.

### 7.3 Timer

`/etc/systemd/system/wg-public-ip.service`:
```
[Unit]
Description=Record the home public address (D-19)
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
User=<ADMIN-USER>
ExecStart=/usr/local/bin/wg-public-ip
```
`/etc/systemd/system/wg-public-ip.timer`:
```
[Unit]
Description=Check the home public address every 15 minutes (D-19)

[Timer]
OnBootSec=2min
OnUnitActiveSec=15min

[Install]
WantedBy=timers.target
```
```
sudo systemctl daemon-reload
sudo systemctl enable --now wg-public-ip.timer
```
The script runs as the administration account, so the file is in that account's home folder, mode 600. It does not use sudo.

### 7.4 Reading the address

Over Tailscale, from the laptop:
```
ssh <ADMIN-USER>@nas cat wg-public-ip/current
```
If it has changed, update `Endpoint` on each device. Do not send the address through Telegram or store it in the repository.

Rollback: `sudo systemctl disable --now wg-public-ip.timer`, then delete the two unit files and the script.

### 7.5 After section 7

V-36: if the router can renew its public address on demand, renew it and time the reconnection. The target is within 30 minutes of the change.

## 8. Removing and rotating peers (SR-23, D-20)

### 8.1 Removing a peer

1. On the NAS, cut the peer off straight away:
   ```
   sudo wg set wg0 peer <PEER-PUBLIC-KEY> remove
   ```
2. Delete its `[Peer]` block from `/etc/wireguard/wg0.conf`, so it does not come back when the tunnel restarts
3. Check `sudo wg show` no longer lists it
4. Remove it from the peer list in Proton Pass
5. If the device was lost or stolen, also remove it from Tailscale (section 5.6 of phase1-changes.md), as it has both paths (D-16)
6. Log the removal in document 05, section 7

V-32 tests this. The target is within 5 minutes.

### 8.2 Rotating a peer's keys (every 180 days)

1. On the device, make a new key pair (4.1). On the NAS, make a new preshared key
2. On the NAS, replace the peer's `PublicKey` and `PresharedKey` in `wg0.conf`, then reload without dropping other peers:
   ```
   sudo bash -c 'wg syncconf wg0 <(wg-quick strip wg0)'
   ```
3. Update the device's tunnel and the peer list (date of rotation)
4. Check the old key no longer gets a handshake (V-33)

Rotating the NAS's own key means updating every device at once. It is done only if the key may have leaked.

## 9. After all sections

- Re-run V-01, V-02, V-04 and V-20 if anything changed since 5.1
- Record the comparison measures (phase2-plan.md, section 6.3)
- Write the key management procedure (SR-22) from sections 4 and 8 into its own short document
- Update the traceability matrix and README, then check document 05, section 8

## 10. Turning WireGuard off (D-16 change, 15th November 2026)

The NAS is reachable only over Tailscale, so the tunnel can no longer be used. These steps stop it and keep the files, so it can be turned back on. Each step is a change approved by the owner and logged in document 05, section 7.

### 10.1 On the NAS

```
sudo systemctl disable --now wg-quick@wg0
```
Check:
```
systemctl is-enabled wg-quick@wg0; systemctl is-active wg-quick@wg0
ip -br link show wg0
sudo nft list tables
sudo ss -ulpn | grep -c ':<WG-PORT> '
```
Expected: `disabled` and `inactive`, `Device "wg0" does not exist`, no `inet wg_nas` in the table list (`PostDown` removed it), and `0`. If `inet wg_nas` is still listed, remove it with `sudo nft delete table inet wg_nas`.

The files in `/etc/wireguard` stay as they are, root-only. The public address timer (section 7) was never installed, so there is nothing else to stop.

### 10.2 On the laptop

```
sudo wg-quick down nas 2>/dev/null; sudo systemctl disable --now wg-quick@nas 2>/dev/null
ip -br link show nas
```
Expected: `Device "nas" does not exist`. `/etc/wireguard/nas.conf` and the key stay, root-only.

### 10.3 On the phone

In the WireGuard app, turn the tunnel off and delete it, then uninstall the app if it is no longer wanted. The phone's private key lived only in the app, so deleting the tunnel removes it.

### 10.4 Afterwards

- V-04 (Claude Code, when approved): the WireGuard UDP port is gone and nothing else has changed
- Document 01, section 6.3: WireGuard row marked as turned off

Rollback: `sudo systemctl enable --now wg-quick@wg0` on the NAS, and `sudo wg-quick up nas` on the laptop.

## 11. Revision log

| Version | Date | Change | Reason |
|---|---|---|---|
| 0.1 | 9th November 2026 | Steps drafted for the WireGuard set-up, firewall, peers, router port forward, address script, and peer removal and rotation, not yet reviewed (drafted with AI assistance) | Owner request to start Phase 2 |
| 0.2 | 9th November 2026 | Section 4.1: laptop installs `wireguard-tools` before making its keys. Note updated: sections 2.1 to 2.3 run | Owner asked whether the laptop needs the tools too |
| 0.3 | 10th November 2026 | Section 4.1: phone uses the official app from Google Play or F-Droid. Section 4.3: laptop file name, `PostUp` for its key, and LAN endpoint until section 6. Section 2.4: tunnel addresses are host addresses without a suffix, the NAS takes `.1`. Section 5: what a failed start leaves behind, stop and start after editing, and a laptop check with `nc` instead of `ping`. Note updated: sections 2.1 to 5 run | Owner questions while following sections 4 and 5 |
| 0.4 | 12th November 2026 | Section 4.1: phone app from Google Play only, as it is no longer on F-Droid. Section 4.2: `syncconf` step to load a new peer. Note updated: phone peer added without a handshake, sections 6 to 8 not run, Phase 2 closed with Tailscale kept (D-16) | Owner decision |
| 0.5 | 15th November 2026 | Section 10: steps to turn WireGuard off on the NAS, the laptop and the phone, keeping the files for a rollback (drafted with AI assistance) | Owner decision, the NAS is reachable only over Tailscale |
