#!/usr/bin/env bash
# Checks new-branch.sh --dry-run against the base-branch decision table in
# .claude/skills/git-workflow/SKILL.md ("Creating Branches").
# Update the EXPECTED rows whenever that table changes.
#
# Usage (from the inavflight root): claude/developer/scripts/git/test-new-branch.sh

set -uo pipefail

SCRIPT="$(dirname "$0")/new-branch.sh"

EXPECTED=(
  "inav bugfix upstream/release/9.1"
  "inav bugfix-10.0 upstream/maintenance-10.x"
  "inav feature upstream/next-10.1"
  "inav breaking upstream/maintenance-11.x"
  "inav2 feature upstream/next-10.1"
  "inav3 bugfix upstream/release/9.1"
  "inav-configurator bugfix upstream/maintenance-9.x"
  "inav-configurator bugfix-10.0 upstream/maintenance-10.x"
  "inav-configurator feature upstream/maintenance-9.x"
  "inav-configurator breaking upstream/maintenance-11.x"
  "inav-configurator2 breaking upstream/maintenance-11.x"
  "PrivacyLRS bugfix origin/secure_01"
  "PrivacyLRS feature origin/secure_01"
)

fail=0
for row in "${EXPECTED[@]}"; do
  read -r repo type want <<<"$row"
  out=$("$SCRIPT" "$repo" "$type" test-branch-name --dry-run 2>&1)
  rc=$?
  got=$(sed -n 's/^Base branch: *//p' <<<"$out")
  if [[ $rc -ne 0 || "$got" != "$want" ]]; then
    echo "FAIL: $repo $type -> got '${got:-<none>}' (exit $rc), want '$want'"
    fail=1
  else
    echo "ok:   $repo $type -> $got"
  fi
done

exit $fail
