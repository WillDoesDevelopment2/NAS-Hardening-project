#!/usr/bin/env bash
# phase0-collect.sh – read-only collection of the Phase 0 tests that run on the NAS
#
# Covers V-04, V-05, V-06, V-09, V-10, V-12 and V-14 in docs/05-verification.md, section 4.
# The other tests are manual: see docs/phase0-checklist.md.
#
# Usage:  sudo ./phase0-collect.sh [output-dir]
#
# - With no argument, output goes to a new folder ~/phase0-raw-<date>-<time> in the home folder
#   of the user who ran sudo
# - [output-dir] must not exist yet, and must be inside that user's home folder or /tmp. The script
#   only ever creates this one new folder. It refuses existing folders, so it can never change the
#   permissions of /, a system folder or any other existing folder
# - When finished (or interrupted), the output is handed back to the user who ran sudo: readable
#   by that user without sudo, and by nobody else
# - Output is RAW and unsanitised. Keep it outside the repository and never commit it
# - Installs nothing, updates nothing and changes no configuration. Exceptions: Lynis writes its
#   own log and report under /var/log, and the output folder is created
# - A missing tool is recorded as skipped, not installed
# - Override the SSD device with SSD_DEV=/dev/nvme0n1 if needed (default /dev/nvme0)

set -u
umask 077

SSD_DEV="${SSD_DEV:-/dev/nvme0}"

if [[ $EUID -ne 0 ]]; then
  echo "Run with sudo: several tests need root to read the full configuration." >&2
  exit 1
fi

# The user who ran sudo gets the output. Running directly as root (no sudo) is refused, so the
# output never ends up readable only by root
OWNER="${SUDO_USER:-}"
if [[ -z "$OWNER" || "$OWNER" == "root" ]]; then
  echo "Run this with sudo from your own account, not as root, so the output can be handed back to you." >&2
  exit 1
fi
OWNER_HOME="$(getent passwd "$OWNER" | cut -d: -f6)"
OWNER_GROUP="$(id -gn "$OWNER")"

OUT="${1:-$OWNER_HOME/phase0-raw-$(TZ=Europe/London date +%Y%m%d-%H%M)}"

# Resolve the folder the output would be created in, without creating anything yet
PARENT="$(realpath -e -- "$(dirname -- "$OUT")" 2>/dev/null)" || {
  echo "Refusing: the parent folder of $OUT does not exist." >&2
  exit 1
}
OUT="$PARENT/$(basename -- "$OUT")"

if [[ -e "$OUT" || -L "$OUT" ]]; then
  echo "Refusing: $OUT already exists. Give a new folder name; the script only creates new folders." >&2
  exit 1
fi

case "$PARENT/" in
  "$OWNER_HOME"/*|/tmp/*) ;;
  *)
    echo "Refusing: $OUT is not inside $OWNER_HOME or /tmp." >&2
    exit 1
    ;;
esac

# Refuse to write raw output inside a git working tree
if command -v git >/dev/null 2>&1 && git -C "$PARENT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Refusing: $OUT is inside a git repository. Raw output must stay outside the repository." >&2
  exit 1
fi

# Create only the new folder (no -p), private to its owner
mkdir -m 700 -- "$OUT" || exit 1

# Hand the output back to the user who ran sudo, even if the script is interrupted
hand_back() { chown -R -- "$OWNER:$OWNER_GROUP" "$OUT"; }
trap hand_back EXIT

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

hand_back
echo "Finished $(TS)"
echo "Output folder: $OUT (owned by $OWNER, no sudo needed to read or copy it)"
echo
echo "Next: record the Lynis log and report writes in the Phase 0 log (docs/05-verification.md, section 7),"
echo "then sanitise each file before anything goes into evidence/phase0/."
