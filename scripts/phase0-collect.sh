#!/usr/bin/env bash
# phase0-collect.sh – read-only collection of the Phase 0 tests that run on the NAS
#
# Covers V-04, V-05, V-06, V-09, V-10, V-12 and V-14 in docs/05-verification.md, section 4.
# The other tests are manual: see docs/phase0-checklist.md.
#
# Usage:  sudo ./phase0-collect.sh <output-dir>
#
# - Output is RAW and unsanitised. Keep <output-dir> outside the repository and never commit it
# - Installs nothing, updates nothing and changes no configuration. Exceptions: Lynis writes its
#   own log and report under /var/log, and the output directory is created
# - A missing tool is recorded as skipped, not installed
# - Override the SSD device with SSD_DEV=/dev/nvme0n1 if needed (default /dev/nvme0)

set -u

OUT="${1:-}"
SSD_DEV="${SSD_DEV:-/dev/nvme0}"

if [[ -z "$OUT" ]]; then
  echo "Usage: sudo $0 <output-dir>" >&2
  exit 1
fi

if [[ $EUID -ne 0 ]]; then
  echo "Run with sudo: several tests need root to read the full configuration." >&2
  exit 1
fi

mkdir -p "$OUT"
chmod 700 "$OUT"

# Refuse to write raw output inside a git working tree
if command -v git >/dev/null 2>&1 && git -C "$OUT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing: $OUT is inside a git repository. Raw output must stay outside the repository." >&2
  exit 1
fi

TS() { TZ=Europe/London date '+%Y-%m-%d %H:%M:%S %Z'; }

# run_test <test-id> <short-name> <command...>
run_test() {
  local id="$1" name="$2"; shift 2
  local file="$OUT/${id}_${name}.txt"
  {
    echo "Test ID: $id"
    echo "Date: $(TS)"
    echo "Command: $*"
    echo "Run from: The NAS"
    echo "Status: RAW - not sanitised"
    echo "----------------------------------------"
    bash -c "$*" 2>&1
    local rc=$?
    echo "----------------------------------------"
    echo "Exit code: $rc"
  } > "$file"
  echo "  $id -> $file"
}

# skip_test <test-id> <short-name> <reason>
skip_test() {
  local file="$OUT/${1}_${2}.txt"
  printf 'Test ID: %s\nDate: %s\nStatus: SKIPPED - %s\n' "$1" "$(TS)" "$3" > "$file"
  echo "  $1 skipped: $3"
}

have() { command -v "$1" >/dev/null 2>&1; }

echo "Phase 0 collection started $(TS)"
echo "Writing raw output to $OUT"

# V-04 Listening sockets, plus running services and SMB state to map each socket to a service
run_test V-04 listening-sockets "ss -tulpn"
run_test V-04 running-services "systemctl list-units --type=service --state=running --no-pager"
run_test V-04 smb-state "systemctl is-active smbd nmbd 2>&1; systemctl is-enabled smbd nmbd 2>&1"

# V-03 supplement: installed package versions, to cross-check the network version scan
run_test V-03 installed-versions "dpkg-query -W -f='\${Package} \${Version}\n' openmediavault openssh-server samba 2>&1"

# V-05 System audit
if have lynis; then
  run_test V-05 lynis "lynis audit system --quick --no-colors"
  for f in /var/log/lynis.log /var/log/lynis-report.dat; do
    [[ -f "$f" ]] && cp "$f" "$OUT/V-05_$(basename "$f")"
  done
else
  skip_test V-05 lynis "lynis not installed. Installing it is a change to the system: owner to decide and log it"
fi

# V-06 SSD health
if have smartctl; then
  run_test V-06 ssd-health "smartctl -a $SSD_DEV"
else
  skip_test V-06 ssd-health "smartctl not installed (package smartmontools)"
fi

# V-09 SSH effective configuration
if have sshd; then
  run_test V-09 sshd-config "sshd -T | grep -iE '^(permitrootlogin|passwordauthentication|pubkeyauthentication|kbdinteractiveauthentication|allowusers|allowgroups|port|listenaddress) '"
  run_test V-09 sshd-config-full "sshd -T"
else
  skip_test V-09 sshd-config "sshd not found"
fi

# V-10 Pending updates (uses the existing package lists; does not run apt update)
run_test V-10 package-list-age "ls -l --time-style=long-iso /var/lib/apt/lists/ | head -n 20"
run_test V-10 pending-updates "apt list --upgradable 2>/dev/null"
run_test V-10 pending-security-updates "apt list --upgradable 2>/dev/null | grep -i security || echo 'None listed'"

# V-12 Accounts and privileges
run_test V-12 login-accounts "getent passwd | awk -F: '\$7 !~ /(nologin|false|sync)\$/ {print \$1, \$3, \$7}'"
run_test V-12 privileged-groups "getent group sudo adm openmediavault-admin ssh _ssh 2>&1"
run_test V-12 sudoers "grep -vE '^\s*(#|$)' /etc/sudoers; for f in /etc/sudoers.d/*; do [ -f \"\$f\" ] && echo \"== \$f\" && grep -vE '^\s*(#|$)' \"\$f\"; done"

# V-14 Encryption status
run_test V-14 block-devices "lsblk -f"

# Checksums so the raw files can be shown to be unchanged later
( cd "$OUT" && sha256sum -- *.txt *.log *.dat 2>/dev/null > SHA256SUMS )

echo "Finished $(TS)"
echo
echo "Next: record the Lynis log and report writes in the Phase 0 log (docs/05-verification.md, section 7),"
echo "then sanitise each file before anything goes into evidence/phase0/."
