#!/bin/bash
# pr-scorecard.sh - Gather merge-readiness data for a PR
#
# Collects signals used to score a PR's readiness to merge:
#   CI status, review quality, testing evidence, maturity, scope/risk
#
# Does NOT produce a score itself — outputs structured data for Claude to score.
# Once a PR has been scored (via pr-scorecard-record.sh), it will NOT be
# re-fetched for 14 days unless --force is passed.
#
# Usage:   pr-scorecard.sh <owner/repo> <PR_NUMBER> [--force]
# Example: pr-scorecard.sh iNavFlight/inav 11220
# Example: pr-scorecard.sh iNavFlight/inav-configurator 2500
# Example: pr-scorecard.sh iNavFlight/inav 11220 --force

set -euo pipefail

REPO="${1:?Usage: pr-scorecard.sh <owner/repo> <PR_NUMBER> [--force] [--output file]}"
PR_NUMBER="${2:?Usage: pr-scorecard.sh <owner/repo> <PR_NUMBER> [--force] [--output file]}"
FORCE=""
OUTPUT_FILE=""

# Parse remaining args (--force and --output can appear in any order after PR_NUMBER)
shift 2
while [[ $# -gt 0 ]]; do
    case "$1" in
        --force)  FORCE="--force"; shift ;;
        --output) OUTPUT_FILE="$2"; shift 2 ;;
        *)        shift ;;
    esac
done

# Redirect all output to file if requested (enables background prefetch)
if [[ -n "$OUTPUT_FILE" ]]; then
    exec > "$OUTPUT_FILE" 2>&1
fi

# ---------------------------------------------------------------------------
# Cache check — skip all API calls if this PR was scored recently
# ---------------------------------------------------------------------------
NOW_TS=$(date +%s)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CACHE_FILE="$(cd "$SCRIPT_DIR/../../../local-data/triage" 2>/dev/null && pwd)/pr-scorecard-history.json"
mkdir -p "$(dirname "$CACHE_FILE")"
CACHE_KEY="${REPO}/${PR_NUMBER}"

if [[ "$FORCE" != "--force" && -f "$CACHE_FILE" ]]; then
    CACHED=$(jq --arg k "$CACHE_KEY" '.[$k] // empty' "$CACHE_FILE" 2>/dev/null || true)
    if [[ -n "$CACHED" && "$CACHED" != "null" ]]; then
        EXPIRES=$(echo "$CACHED" | jq -r '.expires_at')
        EXPIRES_TS=$(date -d "$EXPIRES" +%s 2>/dev/null || echo "0")
        if [[ "$NOW_TS" -lt "$EXPIRES_TS" ]]; then
            CACHED_SCORE=$(echo "$CACHED" | jq -r '.score')
            CACHED_LABEL=$(echo "$CACHED" | jq -r '.label')
            CACHED_SCORED=$(echo "$CACHED" | jq -r '.scored_at')
            CACHED_TITLE=$(echo "$CACHED" | jq -r '.title')
            CACHED_URL=$(echo "$CACHED" | jq -r '.url')
            echo "============================================================"
            echo "PR SCORECARD: ${REPO} #${PR_NUMBER}  [CACHED]"
            echo "============================================================"
            echo "  Title:      $CACHED_TITLE"
            echo "  URL:        $CACHED_URL"
            echo "  Scored:     $CACHED_SCORED"
            echo "  Expires:    $EXPIRES  (use --force to refresh early)"
            echo ""
            echo "  Score:      $CACHED_SCORE / 100"
            echo "  Verdict:    $CACHED_LABEL"
            echo "============================================================"
            echo "CACHE_HIT=true"
            echo "CACHED_SCORE=$CACHED_SCORE"
            echo "CACHED_LABEL=$CACHED_LABEL"
            echo "PR_NUMBER=$PR_NUMBER"
            echo "REPO=$REPO"
            exit 0
        fi
    fi
fi

echo "============================================================"
echo "PR SCORECARD DATA: ${REPO} #${PR_NUMBER}"
echo "Fetching signals... (may take a few seconds)"
echo "============================================================"

# ---------------------------------------------------------------------------
# 1. PR metadata
# ---------------------------------------------------------------------------
PR_DATA=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}" \
    --jq '{
        title:            .title,
        state:            .state,
        draft:            .draft,
        created_at:       .created_at,
        updated_at:       .updated_at,
        merged_at:        .merged_at,
        user:             .user.login,
        author_assoc:     .author_association,
        labels:           [.labels[].name],
        changed_files:    .changed_files,
        additions:        .additions,
        deletions:        .deletions,
        commits:          .commits,
        body:             (.body // ""),
        mergeable:        .mergeable,
        mergeable_state:  .mergeable_state,
        head_sha:         .head.sha,
        base_ref:         .base.ref,
        url:              .html_url,
        milestone:        (.milestone.title // null)
    }' 2>/dev/null)

TITLE=$(echo "$PR_DATA"         | jq -r '.title')
STATE=$(echo "$PR_DATA"         | jq -r '.state')
DRAFT=$(echo "$PR_DATA"         | jq -r '.draft')
CREATED=$(echo "$PR_DATA"       | jq -r '.created_at[:10]')
UPDATED=$(echo "$PR_DATA"       | jq -r '.updated_at[:10]')
AUTHOR=$(echo "$PR_DATA"        | jq -r '.user')
AUTHOR_ASSOC=$(echo "$PR_DATA"  | jq -r '.author_assoc')
LABELS_RAW=$(echo "$PR_DATA"    | jq -r '[.labels[]] | join(", ")')
LABELS="${LABELS_RAW:-none}"
CHANGED_FILES=$(echo "$PR_DATA" | jq -r '.changed_files')
ADDITIONS=$(echo "$PR_DATA"     | jq -r '.additions')
DELETIONS=$(echo "$PR_DATA"     | jq -r '.deletions')
COMMITS=$(echo "$PR_DATA"       | jq -r '.commits')
BODY=$(echo "$PR_DATA"          | jq -r '.body')
MERGEABLE_STATE=$(echo "$PR_DATA" | jq -r '.mergeable_state')
HEAD_SHA=$(echo "$PR_DATA"      | jq -r '.head_sha')
BASE_REF=$(echo "$PR_DATA"      | jq -r '.base_ref')
URL=$(echo "$PR_DATA"           | jq -r '.url')
MILESTONE=$(echo "$PR_DATA"     | jq -r '.milestone // "none"')
LINES_CHANGED=$((ADDITIONS + DELETIONS))

# ---------------------------------------------------------------------------
# 2. CI check runs (using commit SHA for most accurate current state)
# ---------------------------------------------------------------------------
CHECKS=$(gh api "repos/${REPO}/commits/${HEAD_SHA}/check-runs?per_page=100" \
    --jq '[.check_runs[] | {name: .name, status: .status, conclusion: .conclusion}]' \
    2>/dev/null || echo "[]")

CHECKS_TOTAL=$(echo "$CHECKS"   | jq 'length')
CHECKS_SUCCESS=$(echo "$CHECKS" | jq '[.[] | select(.conclusion == "success")] | length')
CHECKS_FAILURE=$(echo "$CHECKS" | jq '[.[] | select(.conclusion == "failure")] | length')
CHECKS_PENDING=$(echo "$CHECKS" | jq '[.[] | select(.status == "in_progress" or .status == "queued")] | length')
CHECKS_SKIPPED=$(echo "$CHECKS" | jq '[.[] | select(.conclusion == "skipped" or .conclusion == "neutral")] | length')
CHECKS_CANCELLED=$(echo "$CHECKS" | jq '[.[] | select(.conclusion == "cancelled")] | length')

# ---------------------------------------------------------------------------
# 3. Reviews — track latest state per reviewer across all rounds
# ---------------------------------------------------------------------------
REVIEWS=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/reviews" \
    --jq '[.[] | {
        user:         .user.login,
        user_type:    .user.type,
        author_assoc: .author_association,
        state:        .state,
        submitted_at: .submitted_at[:10]
    }]' 2>/dev/null || echo "[]")

# Latest state per reviewer (last entry wins within a grouped sort)
APPROVALS=$(echo "$REVIEWS" | jq '[
    group_by(.user) | .[] |
    sort_by(.submitted_at) | last |
    select(.state == "APPROVED")
] | length')

CHANGES_REQUESTED=$(echo "$REVIEWS" | jq '[
    group_by(.user) | .[] |
    sort_by(.submitted_at) | last |
    select(.state == "CHANGES_REQUESTED")
] | length')

# Member/collaborator/owner approvals carry more weight
MEMBER_APPROVALS=$(echo "$REVIEWS" | jq '[
    group_by(.user) | .[] |
    sort_by(.submitted_at) | last |
    select(.state == "APPROVED") |
    select(.author_assoc == "MEMBER" or .author_assoc == "OWNER" or .author_assoc == "COLLABORATOR")
] | length')

# ---------------------------------------------------------------------------
# 4. Inline review comment threads (open threads = unresolved feedback)
#    We count root-thread comments (no in_reply_to_id) from humans as "threads"
# ---------------------------------------------------------------------------
INLINE_COMMENTS=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/comments?per_page=100" \
    --jq '[.[] | {
        user:            .user.login,
        user_type:       .user.type,
        in_reply_to_id:  .in_reply_to_id,
        created_at:      .created_at[:10]
    }]' 2>/dev/null || echo "[]")

# Human-started threads (root comments, non-bot)
OPEN_HUMAN_THREADS=$(echo "$INLINE_COMMENTS" | jq '[
    .[] | select(.in_reply_to_id == null) | select(.user_type != "Bot")
] | length')

# ---------------------------------------------------------------------------
# 4b. Review-thread RESOLUTION state — GraphQL only.
#     REST `pulls/{n}/comments` does NOT expose isResolved/isOutdated, so a Qodo
#     finding that has already been addressed still looks "open". A thread is a
#     LIVE blocker only when isResolved=false AND isOutdated=false. (2026-09-20:
#     configurator #2736 was mis-bucketed because REST showed its 2 findings as
#     present, but GraphQL showed 1 resolved + 1 still open.)
# ---------------------------------------------------------------------------
REPO_OWNER="${REPO%/*}"
REPO_NAME="${REPO#*/}"

REVIEW_THREADS_JSON=$(gh api graphql -f query="query { repository(owner: \"${REPO_OWNER}\", name: \"${REPO_NAME}\") { pullRequest(number: ${PR_NUMBER}) { reviewThreads(first: 100) { nodes { isResolved isOutdated comments(first: 1) { nodes { author { login __typename } } } } } } } }" \
    --jq '[.data.repository.pullRequest.reviewThreads.nodes[] | {
        isResolved: .isResolved,
        isOutdated: .isOutdated,
        login: (.comments.nodes[0].author.login // ""),
        bot: ((.comments.nodes[0].author.__typename // "") == "Bot" or
              (.comments.nodes[0].author.login // "" | test("qodo|copilot|dependabot|codecov|sonar|renovate"; "i")))
    }]' 2>/dev/null || echo "[]")

# Bot-authored review threads (Qodo, Copilot, SonarCloud, dependabot, etc.)
BOT_THREADS_TOTAL=$(echo "$REVIEW_THREADS_JSON" | jq '[.[] | select(.bot == true)] | length')
BOT_THREADS_RESOLVED=$(echo "$REVIEW_THREADS_JSON" | jq '[.[] | select(.bot == true) | select(.isResolved == true)] | length')
BOT_THREADS_OUTDATED=$(echo "$REVIEW_THREADS_JSON" | jq '[.[] | select(.bot == true) | select(.isOutdated == true)] | length')
# Live = neither resolved nor outdated (still requires action)
BOT_THREADS_OPEN=$(echo "$REVIEW_THREADS_JSON" | jq '[.[] | select(.bot == true) | select(.isResolved == false and .isOutdated == false)] | length')

# Human review threads still open (resolution-aware, unlike OPEN_HUMAN_THREADS above)
HUMAN_THREADS_OPEN=$(echo "$REVIEW_THREADS_JSON" | jq '[.[] | select(.bot == false) | select(.isResolved == false and .isOutdated == false)] | length')

# ---------------------------------------------------------------------------
# 5. Conversation comments — key for testing evidence
# ---------------------------------------------------------------------------
CONV_COMMENTS=$(gh api "repos/${REPO}/issues/${PR_NUMBER}/comments?per_page=100" \
    --jq '[.[] | {
        user:         .user.login,
        user_type:    .user.type,
        author_assoc: .author_association,
        created_at:   .created_at[:10],
        body:         (if (.body | length) > 600 then (.body[:600] + "...") else .body end)
    }]' 2>/dev/null || echo "[]")

NON_AUTHOR_HUMAN_COMMENTERS=$(echo "$CONV_COMMENTS" | jq --arg a "$AUTHOR" '[
    .[] | select(.user_type != "Bot") | select(.user != $a) | .user
] | unique | length')

TOTAL_HUMAN_COMMENTERS=$(echo "$CONV_COMMENTS" | jq '[
    .[] | select(.user_type != "Bot") | .user
] | unique | length')

# ---------------------------------------------------------------------------
# 6. Files changed — detect high-risk subsystem touches
# ---------------------------------------------------------------------------
FILES=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/files?per_page=100" \
    --jq '[.[] | .filename]' 2>/dev/null || echo "[]")

TOTAL_FILES=$(echo "$FILES" | jq 'length')

# Core firmware subsystems (attitude estimation, navigation, PID, sensors)
CORE_FIRMWARE=$(echo "$FILES" | jq '[.[] | select(
    test("src/main/flight/pid") or
    test("src/main/navigation/") or
    test("src/main/sensors/") or
    test("src/main/fc/") or
    test("src/main/flight/imu")
)] | length')

# MSP protocol — breaking change risk (older configurators may break)
MSP_PROTOCOL=$(echo "$FILES" | jq '[.[] | select(
    test("msp_protocol") or
    test("msp_serial") or
    test("msp\\.c$") or
    test("msp\\.h$")
)] | length')

# Settings/defaults — visible behavior changes for end users
SETTINGS_FILES=$(echo "$FILES" | jq '[.[] | select(
    test("settings\\.yaml") or
    test("settings\\.c$") or
    test("parameter_group") or
    test("config_master")
)] | length')

# Test files (positive signal — author wrote tests)
TEST_FILES=$(echo "$FILES" | jq '[.[] | select(
    test("test/") or test("_test\\.") or test("spec\\.") or test("__tests__/")
)] | length')

# ---------------------------------------------------------------------------
# 7. Age calculations  (NOW_TS already set at top)
# ---------------------------------------------------------------------------
CREATED_TS=$(date -d "$CREATED" +%s 2>/dev/null || echo "0")
UPDATED_TS=$(date -d "$UPDATED" +%s 2>/dev/null || echo "0")
AGE_DAYS=$(( (NOW_TS - CREATED_TS) / 86400 ))
DAYS_SINCE_UPDATE=$(( (NOW_TS - UPDATED_TS) / 86400 ))

# ---------------------------------------------------------------------------
# OUTPUT REPORT
# ---------------------------------------------------------------------------

echo ""
echo "=== PR OVERVIEW ==="
echo "  Title:              $TITLE"
echo "  URL:                $URL"
echo "  Author:             $AUTHOR (association: $AUTHOR_ASSOC)"
echo "  State:              $STATE  |  Draft: $DRAFT"
echo "  Base branch:        $BASE_REF"
echo "  Milestone:          $MILESTONE"
echo "  Labels:             $LABELS"
echo "  Created:            $CREATED  ($AGE_DAYS days ago)"
echo "  Last updated:       $UPDATED  ($DAYS_SINCE_UPDATE days ago)"
echo "  Commits:            $COMMITS"
echo ""

echo "=== HARD BLOCKERS (check these first) ==="
BLOCKED=false
if [[ "$DRAFT" == "true" ]]; then
    echo "  [BLOCK] PR is a DRAFT — not intended for merge yet"
    BLOCKED=true
fi
if echo "$LABELS" | grep -qiE "don.t merge|do not merge|\bhold\b|\bwip\b"; then
    echo "  [BLOCK] Blocking label present: $LABELS"
    BLOCKED=true
fi
if [[ "$MERGEABLE_STATE" == "dirty" ]]; then
    echo "  [BLOCK] MERGE CONFLICTS — branch needs rebasing"
    BLOCKED=true
fi
if [[ "$CHECKS_FAILURE" -gt 0 ]]; then
    echo "  [BLOCK] $CHECKS_FAILURE CI check(s) FAILING:"
    echo "$CHECKS" | jq -r '.[] | select(.conclusion == "failure") | "    - \(.name)"' 2>/dev/null
    BLOCKED=true
fi
if [[ "$CHANGES_REQUESTED" -gt 0 ]]; then
    echo "  [BLOCK] $CHANGES_REQUESTED reviewer(s) have UNRESOLVED 'Request Changes'"
    BLOCKED=true
fi
if [[ "$BLOCKED" == "false" ]]; then
    echo "  None detected"
fi
echo ""

echo "=== MILESTONE CHECK ==="
# Derive expected milestone from base branch
MILESTONE_OK=true
MILESTONE_NOTE=""
if [[ "$BASE_REF" == "maintenance-9.x" ]]; then
    if [[ "$MILESTONE" != "9.1" ]]; then
        MILESTONE_OK=false
        MILESTONE_NOTE="Expected 9.1 for maintenance-9.x (9.0.1 released Jan 2026; 9.1 target Jun/Jul 2026)"
    fi
elif [[ "$BASE_REF" == "maintenance-10.x" ]]; then
    if [[ "$MILESTONE" != "10.0" && "$MILESTONE" != "10.1" ]]; then
        MILESTONE_OK=false
        MILESTONE_NOTE="Expected 10.x milestone for maintenance-10.x"
    fi
fi

if [[ "$MILESTONE_OK" == "true" ]]; then
    echo "  ✓ Milestone '$MILESTONE' is correct for base '$BASE_REF'"
else
    echo "  ✗ Milestone mismatch: has '$MILESTONE', $MILESTONE_NOTE"
fi
echo ""

echo "=== CI / BUILD ==="
echo "  Total checks:   $CHECKS_TOTAL"
echo "  Passing:        $CHECKS_SUCCESS"
echo "  Failing:        $CHECKS_FAILURE"
echo "  Pending:        $CHECKS_PENDING"
echo "  Skipped:        $CHECKS_SKIPPED"
echo "  Cancelled:      $CHECKS_CANCELLED"
if [[ "$CHECKS_FAILURE" -gt 0 ]]; then
    echo "  Failing checks:"
    echo "$CHECKS" | jq -r '.[] | select(.conclusion == "failure") | "    - \(.name)"' 2>/dev/null || true
fi
echo ""

echo "=== CODE REVIEW ==="
echo "  Approvals total:            $APPROVALS"
echo "  Member/collaborator approvals: $MEMBER_APPROVALS"
echo "  Unresolved changes-requested:  $CHANGES_REQUESTED"
echo "  Open human inline threads:     $OPEN_HUMAN_THREADS"
echo ""
echo "  Review threads (resolution-aware, GraphQL):"
echo "    Bot threads:  total=$BOT_THREADS_TOTAL resolved=$BOT_THREADS_RESOLVED outdated=$BOT_THREADS_OUTDATED OPEN=$BOT_THREADS_OPEN"
echo "    Human threads still open:     $HUMAN_THREADS_OPEN"
echo "  NOTE: a bot thread counts as a live blocker ONLY when OPEN>0 (not resolved, not outdated)."
echo ""
echo "  Reviewer list (latest state per reviewer):"
if [[ $(echo "$REVIEWS" | jq 'length') -eq 0 ]]; then
    echo "    No reviews submitted"
else
    echo "$REVIEWS" | jq -r '
        group_by(.user) | .[] |
        sort_by(.submitted_at) | last |
        "    \(.user) (\(.author_assoc)): \(.state)  on \(.submitted_at)"
    ' 2>/dev/null
fi
echo ""

echo "=== TESTING EVIDENCE ==="
echo "  Non-author human commenters: $NON_AUTHOR_HUMAN_COMMENTERS"
echo "  Total human commenters:      $TOTAL_HUMAN_COMMENTERS"
echo ""
echo "  Conversation comments (non-bot, all, newest first):"
echo "  Note: Look for phrases like 'tested', 'works', 'confirmed', 'flight test', 'verified'"
echo ""
if [[ $(echo "$CONV_COMMENTS" | jq 'length') -eq 0 ]]; then
    echo "  No conversation comments"
else
    echo "$CONV_COMMENTS" | jq -r '
        reverse |
        .[] | select(.user_type != "Bot") |
        "  [\(.created_at)] \(.user) (\(.author_assoc)):",
        "  \(.body)",
        ""
    ' 2>/dev/null
fi
echo ""

echo "=== MATURITY ==="
echo "  PR age:              $AGE_DAYS days"
echo "  Days since update:   $DAYS_SINCE_UPDATE days"
echo "  Commit count:        $COMMITS  (many small commits may indicate churn or responsiveness)"
echo ""

echo "=== SCOPE / RISK ==="
echo "  Files changed:            $CHANGED_FILES  (out of $TOTAL_FILES fetched)"
echo "  Lines added:              $ADDITIONS"
echo "  Lines deleted:            $DELETIONS"
echo "  Total lines touched:      $LINES_CHANGED"
echo "  Core subsystem files:     $CORE_FIRMWARE  (PID/nav/sensors/IMU/FC)"
echo "  MSP protocol files:       $MSP_PROTOCOL   (breaking-change risk)"
echo "  Settings/config files:    $SETTINGS_FILES (user-visible behavior)"
echo "  Test files included:      $TEST_FILES"
echo ""
echo "  Files changed (up to 30):"
echo "$FILES" | jq -r '.[] | "    \(.)"' 2>/dev/null | head -30 || true
if [[ "$TOTAL_FILES" -gt 30 ]]; then
    echo "    ... and $((TOTAL_FILES - 30)) more files"
fi
echo ""

echo "=== PR DESCRIPTION ==="
if [[ -z "$BODY" || "$BODY" == "null" ]]; then
    echo "  (No description provided)"
else
    echo "$BODY" | head -60
fi
echo ""

echo "============================================================"
echo "SCORECARD_DATA_END"
echo "PR_NUMBER=$PR_NUMBER"
echo "REPO=$REPO"
