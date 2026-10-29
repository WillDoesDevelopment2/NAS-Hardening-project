#!/usr/bin/env python3
"""sanitise.py – replace identifying details in raw evidence before it enters the repository

Usage:  python3 -I scripts/sanitise.py <raw-input> <output> --map <map-file> [--force]

- <raw-input>  a raw file from the raw evidence location (outside the repository)
- <output>     the sanitised copy, normally evidence/phase0/V-xx_name.txt
- <map-file>   real values and their placeholders. Must be OUTSIDE the repository, as it
               holds the real values. One entry per line, whitespace-separated, # for comments:

                   # real value          placeholder
                   <the NAS address>     <NAS-IP>
                   <the router address>  <ROUTER-IP>
                   <the NAS hostname>    nas.example
                   <the username>        <USER>
                   <the Wi-Fi name>      <WIFI-NAME>

What it replaces, in this order:
1. Private key blocks, Tailscale auth keys, WireGuard-style keys and SSH public keys
2. Every value in the map file (hostnames and usernames are matched case-insensitively)
3. Serial numbers and host IDs in labelled fields (smartctl, Lynis), and the host IDs and
   hostname hashes in the Lynis log
4. Filesystem UUIDs                    -> <UUID-n>, and FAT volume IDs in lsblk output -> <VOLID-n>
   MAC addresses                       -> <MAC-n>
5. Remaining IPv6 and IPv4 addresses   -> <IPV6-n> and <IP-n>
   Kept: 0.0.0.0, loopback, netmasks, multicast, documentation ranges, and four-part package
   version numbers (for example "version: 1.2.3.4-1" or "pkg,1.2.3.4+b1")

The same value always gets the same placeholder within one file. Afterwards the output is
re-checked with the repository's leak checks and anything suspicious is listed for manual
review. The script cannot know every sensitive value: always read the output before committing.
"""

import argparse
import ipaddress
import re
import subprocess
import sys
from pathlib import Path


def in_git_repo(path: Path) -> bool:
    d = path if path.is_dir() else path.parent
    try:
        r = subprocess.run(["git", "-C", str(d), "rev-parse", "--is-inside-work-tree"],
                           capture_output=True, text=True)
        return r.returncode == 0 and r.stdout.strip() == "true"
    except (FileNotFoundError, OSError):
        return False


def load_map(path: Path):
    entries = []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        line = re.split(r"\s+#", line.strip(), maxsplit=1)[0]
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 2:
            sys.exit(f"Map file line {n}: expected '<real value> <placeholder>', got {len(parts)} fields")
        entries.append((parts[0], parts[1]))
    # Longest first, so a full hostname is replaced before a shorter part of it
    return sorted(entries, key=lambda e: len(e[0]), reverse=True)


class Numberer:
    """Gives each distinct value a stable numbered placeholder, e.g. <IP-1>."""
    def __init__(self, label):
        self.label, self.seen = label, {}

    def __call__(self, value):
        key = value.lower()
        if key not in self.seen:
            self.seen[key] = f"<{self.label}-{len(self.seen) + 1}>"
        return self.seen[key]


KEEP_V4 = [ipaddress.ip_network(n) for n in (
    "0.0.0.0/32", "127.0.0.0/8", "224.0.0.0/4", "255.0.0.0/8",
    "192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")]
KEEP_V6 = [ipaddress.ip_network(n) for n in ("::/128", "::1/128", "ff00::/8", "2001:db8::/32")]

RE_PRIVKEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S)
RE_TSKEY = re.compile(r"\btskey-[A-Za-z0-9_-]+")
RE_WGKEY = re.compile(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{42}[AEIMQUYcgkosw048]=(?![A-Za-z0-9+/=])")
RE_SSHPUB = re.compile(r"\b(ssh-(?:rsa|ed25519|dss)|ecdsa-sha2-[a-z0-9]+|sk-[a-z0-9@.-]+) AAAA[A-Za-z0-9+/=]+")
RE_LABELLED = re.compile(
    r"^(\s*(?:Namespace \d+\s+)?(?:Serial Number|Serial number|Serial|LU WWN Device Id|IEEE EUI-64|NGUID|"
    r"hostid2?|hostname|domainname|machine[-_]id|hardware_uuid)\s*[:=]\s*)(\S.*?)\s*$",
    re.M | re.I)
RE_HOSTID_LOG = re.compile(r"((?:HostID2?|Hash \([^)\n]*\))\s*:?\s*)[0-9A-Fa-f]{32,}", re.I)
RE_UUID = re.compile(r"(?<![0-9A-Fa-f-])[0-9A-Fa-f]{8}-(?:[0-9A-Fa-f]{4}-){3}[0-9A-Fa-f]{12}(?![0-9A-Fa-f-])")
RE_FAT_VOLID = re.compile(r"^(.*\b(?:vfat|exfat)\b.*?)(?<![\w-])([0-9A-Fa-f]{4}-[0-9A-Fa-f]{4})(?![\w-])", re.M)
RE_MAC = re.compile(r"(?<![0-9A-Fa-f:])(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}(?![0-9A-Fa-f:])")
RE_V6_CAND = re.compile(r"(?<![0-9A-Za-z:.])[0-9A-Fa-f]{0,4}(?::[0-9A-Fa-f]{0,4}){2,7}(?![0-9A-Za-z:.])")
RE_V4 = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d])")
# Package versions are recognised by what comes before them: "version: " or "(version: ", or a
# package name in a Lynis list ("|name,") followed by a Debian revision or suffix ("-3", "+b1").
# An address on its own, or in a range such as "192.0.2.5-10", is still replaced
RE_VERSION_HEAD = re.compile(r"version[:=]?\s*\(?\s*$", re.I)
RE_PKG_LIST_HEAD = re.compile(r"\|[a-z0-9][a-z0-9.+:-]*,$")
RE_VERSION_TAIL = re.compile(r"\d*(?:-\d|[+~][A-Za-z0-9])")


def is_package_version(text, start, end):
    """True if the dotted number at text[start:end] is a package version, not an address."""
    before = text[max(0, start - 60):start]
    return bool(RE_VERSION_HEAD.search(before)
                or (RE_PKG_LIST_HEAD.search(before) and RE_VERSION_TAIL.match(text, end)))


def sanitise(text, mapping, counts):
    def count(kind, n=1):
        counts[kind] = counts.get(kind, 0) + n

    text, n = RE_PRIVKEY.subn("<PRIVATE-KEY-REMOVED>", text); count("private key", n)
    text, n = RE_TSKEY.subn("<TS-AUTHKEY>", text); count("Tailscale key", n)
    text, n = RE_SSHPUB.subn(lambda m: f"{m.group(1)} <SSH-PUBKEY>", text); count("SSH public key", n)
    text, n = RE_WGKEY.subn("<WG-KEY>", text); count("WireGuard-style key", n)

    for real, placeholder in mapping:
        flags = 0 if re.fullmatch(r"[\d.:a-fA-F]+", real) else re.I
        pat = re.compile(r"(?<![A-Za-z0-9_.-])" + re.escape(real) + r"(?![A-Za-z0-9_-])", flags)
        text, n = pat.subn(placeholder, text); count(f"map: {placeholder}", n)

    text, n = RE_LABELLED.subn(lambda m: m.group(1) + "<REDACTED>", text); count("serial or host ID", n)
    text, n = RE_HOSTID_LOG.subn(lambda m: m.group(1) + "<REDACTED>", text); count("serial or host ID", n)

    uuid = Numberer("UUID")
    text, n = RE_UUID.subn(lambda m: uuid(m.group(0)), text); count("UUID", n)
    volid = Numberer("VOLID")
    text, n = RE_FAT_VOLID.subn(lambda m: m.group(1) + volid(m.group(2)), text); count("FAT volume ID", n)

    mac = Numberer("MAC")
    text, n = RE_MAC.subn(lambda m: mac(m.group(0)), text); count("MAC address", n)

    v6 = Numberer("IPV6")
    def repl_v6(m):
        s = m.group(0)
        try:
            addr = ipaddress.IPv6Address(s)
        except ValueError:
            return s
        if any(addr in net for net in KEEP_V6):
            return s
        count("IPv6 address")
        return v6(s)
    text = RE_V6_CAND.sub(repl_v6, text)

    v4 = Numberer("IP")
    def repl_v4(m):
        s = m.group(0)
        try:
            addr = ipaddress.IPv4Address(s)
        except ValueError:
            return s
        if any(addr in net for net in KEEP_V4) or is_package_version(m.string, m.start(), m.end()):
            return s
        count("IPv4 address")
        return v4(s)
    text = RE_V4.sub(repl_v4, text)

    # Mark the collection script's header as sanitised
    summary = ", ".join(f"{k} x{v}" for k, v in counts.items() if v) or "nothing replaced"
    text, n = re.subn(r"^Status: RAW - not sanitised$",
                      f"Status: Sanitised\nSanitised by: scripts/sanitise.py ({summary})", text, flags=re.M)
    return text


def review(text):
    """Leak checks from CLAUDE.md, plus a few extra hints. Returns (line number, reason, line)."""
    ipv4_like = re.compile(r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}")

    def unexpected_ipv4(line):
        for m in ipv4_like.finditer(line):
            if is_package_version(line, m.start(), m.end()):
                continue
            try:
                addr = ipaddress.IPv4Address(m.group(0))
            except ValueError:
                return True          # not a valid address, so a person should look at it
            if not any(addr in net for net in KEEP_V4):
                return True
        return False

    checks = [
        (unexpected_ipv4, "IPv4-like value not replaced"),
        (re.compile(r"([0-9a-f]{2}:){5}[0-9a-f]{2}", re.I).search, "MAC-like"),
        (re.compile(r"password|passwd|secret|token|private key", re.I).search, "sensitive word"),
        (lambda l: re.search(r"\b\d+\.\d+\.\d+[\w.+~-]*", ipv4_like.sub("", l)),
         "exact version (reduce to major version if unfixed)"),
        (re.compile(r"/home/(?!<USER>)[^/\s]+").search, "home directory path"),
        (re.compile(r"(?=[A-Za-z0-9+]*\d)(?=[A-Za-z0-9+]*[A-Za-z])[A-Za-z0-9+]{32,}={0,2}").search,
         "long encoded string"),
    ]
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if line.startswith("Sanitised by: "):
            continue
        for check, why in checks:
            if check(line):
                hits.append((i, why, line.strip()[:120]))
    return hits


def main():
    ap = argparse.ArgumentParser(description="Sanitise a raw evidence file.")
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--map", required=True, type=Path, help="map file of real values, outside the repository")
    ap.add_argument("--force", action="store_true", help="overwrite an existing output file")
    a = ap.parse_args()

    if not a.input.is_file():
        sys.exit(f"Input not found: {a.input}")
    if not a.map.is_file():
        sys.exit(f"Map file not found: {a.map}")
    if in_git_repo(a.map.resolve()):
        sys.exit("Refusing: the map file is inside a git repository. It holds real values and must stay outside.")
    if in_git_repo(a.input.resolve()):
        print("Warning: the input is inside a git repository. Raw output should stay outside it.", file=sys.stderr)
    if a.output.resolve() == a.input.resolve():
        sys.exit("Refusing: output would overwrite the raw input.")
    if a.output.exists() and not a.force:
        sys.exit(f"Output exists: {a.output} (use --force to overwrite)")

    counts = {}
    text = sanitise(a.input.read_text(errors="replace"), load_map(a.map), counts)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(text)

    print(f"Wrote {a.output}")
    for k, v in counts.items():
        if v:
            print(f"  replaced {k}: {v}")
    hits = review(text)
    if hits:
        print(f"\nCheck these {len(hits)} line(s) by hand before committing:")
        for i, why, line in hits:
            print(f"  line {i} [{why}]: {line}")
    else:
        print("\nNo leak-check matches. Still read the file before committing.")


if __name__ == "__main__":
    main()
