#!/usr/bin/env bash
# Deterministic branch creation for the INAV harness repos.
#
# This is the single authority for the {repo, change-type} -> base-branch
# decision table. If you're tempted to hardcode a base branch anywhere else,
# point at this script (or its mirrored table in
# .claude/skills/git-workflow/SKILL.md "Creating Branches") instead.
#
# Usage:
#   new-branch.sh <repo> <bugfix|feature|breaking> <branch-name> [--dry-run]
#
#   repo: inav | inav2 | inav3 | inav-configurator | inav-configurator2 | PrivacyLRS
#
#   inav2/inav3 are separate parallel checkouts of the same inav repo (used
#   when inav/ is locked by another task) and follow the same inav decision
#   table below. inav-configurator2 is likewise a separate parallel checkout
#   of inav-configurator and follows the same inav-configurator decision
#   table below.
#
# Examples:
#   new-branch.sh inav bugfix fix-gps-recovery
#   new-branch.sh inav2 feature shrink-ledstrip-dma-buffer
#   new-branch.sh inav-configurator feature add-battery-limit-ui --dry-run
#   new-branch.sh PrivacyLRS bugfix fix-counter-sync

set -euo pipefail

# TEMPORARY OVERRIDE — REVIEW-BY 2027-02
# inav's maintenance-9.x is currently damaged; do not branch from it.
# inav-configurator's maintenance-9.x is NOT damaged and is unaffected by
# this override. If you're reading this after Feb 2027, verify whether
# inav's maintenance-9.x has been repaired before deleting this block (and
# reverting inav bugfix/feature below to maintenance-9.x).
INAV_OVERRIDE_ACTIVE=1

usage() {
  cat <<'EOF'
Usage: new-branch.sh <repo> <bugfix|feature|breaking> <branch-name> [--dry-run]

  repo:        inav | inav2 | inav3 | inav-configurator | inav-configurator2 | PrivacyLRS
  change-type: bugfix | feature | breaking
  branch-name: kebab-case, no slashes (e.g. fix-gps-recovery)

  --dry-run    Print the decision and commands without running them.
EOF
}

if [[ $# -lt 3 ]]; then
  usage
  exit 1
fi

REPO="$1"
CHANGE_TYPE="$2"
BRANCH_NAME="$3"
DRY_RUN=0
if [[ "${4:-}" == "--dry-run" ]]; then
  DRY_RUN=1
fi

case "$REPO" in
  inav|inav2|inav3|inav-configurator|inav-configurator2|PrivacyLRS) ;;
  *)
    echo "ERROR: unknown repo '$REPO' (expected inav | inav2 | inav3 | inav-configurator | inav-configurator2 | PrivacyLRS)" >&2
    exit 1
    ;;
esac

# inav2/inav3 are separate checkouts of the same inav repo, and
# inav-configurator2 is a separate checkout of inav-configurator — same
# decision table, different directory.
DECISION_REPO="$REPO"
case "$REPO" in
  inav2|inav3) DECISION_REPO="inav" ;;
  inav-configurator2) DECISION_REPO="inav-configurator" ;;
esac

case "$CHANGE_TYPE" in
  bugfix|feature|breaking) ;;
  *)
    echo "ERROR: unknown change-type '$CHANGE_TYPE' (expected bugfix | feature | breaking)" >&2
    exit 1
    ;;
esac

if [[ -z "$BRANCH_NAME" ]]; then
  echo "ERROR: branch-name is required" >&2
  exit 1
fi

if [[ "$REPO" == "PrivacyLRS" && "$BRANCH_NAME" == */* ]]; then
  echo "ERROR: PrivacyLRS branch names must not contain slashes (got '$BRANCH_NAME')" >&2
  exit 1
fi

# --- Decision table -----------------------------------------------------
REMOTE=""
BASE=""
REASON=""

case "$DECISION_REPO" in
  PrivacyLRS)
    REMOTE="origin"
    BASE="secure_01"
    REASON="PrivacyLRS is a separate fork/derivative project; secure_01 is always the base."
    ;;
  inav)
    REMOTE="upstream"
    if [[ "$INAV_OVERRIDE_ACTIVE" == "1" ]]; then
      case "$CHANGE_TYPE" in
        bugfix)
          BASE="release/9.1"
          REASON="TEMPORARY OVERRIDE (REVIEW-BY 2027-02): inav's maintenance-9.x is damaged; bug fixes base on release/9.1 instead."
          ;;
        feature|breaking)
          BASE="maintenance-10.x"
          REASON="TEMPORARY OVERRIDE (REVIEW-BY 2027-02) for feature; normal rule for breaking: maintenance-10.x either way."
          ;;
      esac
    else
      case "$CHANGE_TYPE" in
        bugfix|feature) BASE="maintenance-9.x"; REASON="Current-version work (backward compatible)." ;;
        breaking)        BASE="maintenance-10.x"; REASON="Breaking change (MSP protocol/settings structure)." ;;
      esac
    fi
    ;;
  inav-configurator)
    REMOTE="upstream"
    # Not affected by the inav override — configurator's maintenance-9.x is fine.
    case "$CHANGE_TYPE" in
      bugfix|feature) BASE="maintenance-9.x"; REASON="Current-version work (backward compatible). Not affected by the inav-only override." ;;
      breaking)        BASE="maintenance-10.x"; REASON="Breaking change (MSP protocol/settings structure)." ;;
    esac
    ;;
esac

echo "Repo:        $REPO"
echo "Change type: $CHANGE_TYPE"
echo "Base branch: $REMOTE/$BASE"
echo "Reason:      $REASON"
echo "Branch name: $BRANCH_NAME"
echo

if [[ ! -d "$REPO" ]]; then
  echo "ERROR: directory '$REPO' not found (run this from the inavflight root)" >&2
  exit 1
fi

cd "$REPO"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: $REPO has a dirty working tree. Commit, stash, or discard changes first." >&2
  exit 1
fi

CMDS=(
  "git fetch $REMOTE"
  "git checkout -b $BRANCH_NAME $REMOTE/$BASE"
)

if [[ "$DRY_RUN" == "1" ]]; then
  echo "[dry-run] Would run in $REPO/:"
  for c in "${CMDS[@]}"; do echo "  $c"; done
  exit 0
fi

for c in "${CMDS[@]}"; do
  echo "+ $c"
  eval "$c"
done

echo
echo "Created '$BRANCH_NAME' from $REMOTE/$BASE in $REPO/."
