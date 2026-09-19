#!/bin/bash
# scorecard-triage.sh - Fetch next PR for a scorecard review session
#
# Prioritizes PRs by merge-readiness so the most promising ones come first:
#   Priority 0: High score (>=66) — likely ready, review these first
#   Priority 1: Medium score (46-65) — promising, may need a nudge
#   Priority 2: Unscored — need evaluation
#   Priority 3: Low score (<46) — needs work, review last
#
# Uses a 2-minute PR list cache. Reads pr-scorecard-history.json for scores.
# Excludes drafts and PRs labeled "don't merge".
# Only includes PRs created after --after DATE (default: 6 months ago).
#
# Usage: scorecard-triage.sh <owner/repo> [skip-file] [--after DATE] [--before DATE] [--sort-oldest] [--offset N] [--output file]
# Example: scorecard-triage.sh iNavFlight/inav claude/local-data/triage/skip-scorecard-inav.txt
# Example: scorecard-triage.sh iNavFlight/inav claude/local-data/triage/skip-scorecard-inav.txt --after 2024-10-13 --sort-oldest
# Example: scorecard-triage.sh iNavFlight/inav claude/local-data/triage/skip-scorecard-inav.txt --offset 1 --output ./tmp/claude/prefetch-scorecard.txt

set -euo pipefail

REPO="${1:?Usage: scorecard-triage.sh <owner/repo> [skip-file] [--after DATE] [--before DATE] [--offset N] [--output file]}"
SKIP_FILE="${2:-}"
OFFSET=0
OUTPUT_FILE=""
AFTER_DATE=$(date -d "6 months ago" +%Y-%m-%d 2>/dev/null || echo "1970-01-01")
BEFORE_DATE=""
SORT_OLDEST=false

# Parse optional flags (after positional args)
shift
[[ -n "${1:-}" && "$1" != "--"* ]] && shift  # skip skip-file if present
while [[ $# -gt 0 ]]; do
    case "$1" in
        --after)       AFTER_DATE="$2"; shift 2 ;;
        --before)      BEFORE_DATE="$2"; shift 2 ;;
        --sort-oldest) SORT_OLDEST=true; shift ;;
        --offset)      OFFSET="$2"; shift 2 ;;
        --output)      OUTPUT_FILE="$2"; shift 2 ;;
        *)             shift ;;
    esac
done

# Create the workspace tmp dir before redirecting, so both the --output target and
# the PR-list cache below have a place to write. Use ./tmp (workspace tmp, shared
# with subagents) — never /tmp, which is ephemeral per command/subagent in this harness.
mkdir -p ./tmp/claude

# Redirect all output to file if requested (enables background prefetch)
if [[ -n "$OUTPUT_FILE" ]]; then
    exec > "$OUTPUT_FILE" 2>&1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCORE_CACHE="$(cd "$SCRIPT_DIR/../../../local-data/triage" 2>/dev/null && pwd)/pr-scorecard-history.json"
mkdir -p "$(dirname "$SCORE_CACHE")"

# ---------------------------------------------------------------------------
# Build skip list for jq
# ---------------------------------------------------------------------------
SKIP_JSON="[]"
if [[ -n "$SKIP_FILE" && -f "$SKIP_FILE" ]]; then
    SKIP_LINES=$(grep -v '^#' "$SKIP_FILE" | grep -v '^$' || true)
    if [[ -n "$SKIP_LINES" ]]; then
        SKIP_JSON=$(echo "$SKIP_LINES" | jq -R 'tonumber' | jq -s '.' 2>/dev/null || echo "[]")
    fi
fi

# ---------------------------------------------------------------------------
# Fetch PR list (cached for 2 minutes)
# ---------------------------------------------------------------------------
REPO_SLUG=$(echo "$REPO" | tr '/' '-')
CACHE_FILE="./tmp/claude/scorecard-pr-cache-${REPO_SLUG}.json"
USE_CACHE=false

if [[ -f "$CACHE_FILE" ]]; then
    CACHE_AGE=$(( $(date +%s) - $(stat -c %Y "$CACHE_FILE") ))
    [[ $CACHE_AGE -lt 120 ]] && USE_CACHE=true
fi

if [[ "$USE_CACHE" == "true" ]]; then
    PR_JSON=$(cat "$CACHE_FILE")
else
    BEFORE_FILTER=""
    [[ -n "$BEFORE_DATE" ]] && BEFORE_FILTER='select(.created_at < "'"${BEFORE_DATE}"'") |'
    PR_JSON=$(gh api "repos/${REPO}/pulls?state=open&per_page=100&sort=created&direction=asc" \
        --paginate \
        --jq '[.[] |
            select(.draft == false) |
            select(.created_at > "'"${AFTER_DATE}"'") |
            '"${BEFORE_FILTER}"'
            select((.labels | map(.name) | any(test("don.t merge"; "i"))) | not) |
            {
                number:     .number,
                title:      .title,
                createdAt:  .created_at,
                author:     .user.login,
                labels:     [.labels[].name],
                url:        .html_url,
                baseBranch: .base.ref
            }
        ]' \
        2>/dev/null | jq -s 'flatten')
    echo "$PR_JSON" > "$CACHE_FILE"
fi

if [[ -z "$PR_JSON" || "$PR_JSON" == "[]" || "$PR_JSON" == "null" ]]; then
    echo "NO_MORE_PRS"
    echo "No open PRs found for $REPO"
    exit 0
fi

# ---------------------------------------------------------------------------
# Load scorecard cache and annotate each PR with a sort priority
# ---------------------------------------------------------------------------
SCORE_JSON="{}"
[[ -f "$SCORE_CACHE" ]] && SCORE_JSON=$(cat "$SCORE_CACHE")

NOW_TS=$(date +%s)

SORT_OLDEST_JSON=$( [[ "$SORT_OLDEST" == "true" ]] && echo "true" || echo "false" )
ANNOTATED=$(echo "$PR_JSON" | jq \
    --argjson skip        "$SKIP_JSON" \
    --argjson scores      "$SCORE_JSON" \
    --arg     repo        "$REPO" \
    --argjson now         "$NOW_TS" \
    --argjson sort_oldest "$SORT_OLDEST_JSON" \
    '
    map(
        select(.number as $n | $skip | index($n) | not) |
        . as $pr |
        ($repo + "/" + (.number | tostring)) as $key |
        ($scores[$key] // null) as $entry |
        (
            if $entry == null then
                {priority: 2, score: null, scoreLabel: "unscored", expiresAt: null, scoredAt: null, cacheStatus: "unscored"}
            else
                ($entry.score // 0) as $s |
                ($entry.expires_at | strptime("%Y-%m-%d") | mktime) as $exp |
                (if $exp <= $now then
                    {priority: 2, score: $s, scoreLabel: $entry.label, expiresAt: $entry.expires_at, scoredAt: $entry.scored_at, cacheStatus: "expired"}
                elif $s >= 66 then
                    {priority: 0, score: $s, scoreLabel: $entry.label, expiresAt: $entry.expires_at, scoredAt: $entry.scored_at, cacheStatus: "fresh"}
                elif $s >= 46 then
                    {priority: 1, score: $s, scoreLabel: $entry.label, expiresAt: $entry.expires_at, scoredAt: $entry.scored_at, cacheStatus: "fresh"}
                else
                    {priority: 3, score: $s, scoreLabel: $entry.label, expiresAt: $entry.expires_at, scoredAt: $entry.scored_at, cacheStatus: "fresh"}
                end)
            end
        ) as $scoreInfo |
        $pr + $scoreInfo
    ) |
    sort_by([if $sort_oldest then 0 else .priority end, .createdAt])
    ' 2>/dev/null)

REMAINING=$(echo "$ANNOTATED" | jq 'length')
NEXT=$(echo "$ANNOTATED" | jq --argjson idx "$OFFSET" '.[$idx] // empty')

if [[ -z "$NEXT" || "$NEXT" == "null" ]]; then
    echo "NO_MORE_PRS"
    echo "No more PRs in the review queue for $REPO"
    exit 0
fi

# ---------------------------------------------------------------------------
# Extract and output
# ---------------------------------------------------------------------------
NUMBER=$(echo "$NEXT"        | jq -r '.number')
TITLE=$(echo "$NEXT"         | jq -r '.title')
URL=$(echo "$NEXT"           | jq -r '.url')
AUTHOR=$(echo "$NEXT"        | jq -r '.author')
CREATED=$(echo "$NEXT"       | jq -r '.createdAt[:10]')
LABELS_RAW=$(echo "$NEXT"    | jq -r '[.labels[]] | join(", ")')
LABELS="${LABELS_RAW:-none}"
BASE=$(echo "$NEXT"          | jq -r '.baseBranch')
PRIORITY=$(echo "$NEXT"      | jq -r '.priority')
CACHED_SCORE=$(echo "$NEXT"  | jq -r '.score // "none"')
CACHED_LABEL=$(echo "$NEXT"  | jq -r '.scoreLabel')
SCORED_AT=$(echo "$NEXT"     | jq -r '.scoredAt // "never"')
EXPIRES_AT=$(echo "$NEXT"    | jq -r '.expiresAt // "n/a"')
CACHE_STATUS=$(echo "$NEXT"  | jq -r '.cacheStatus')

CREATED_TS=$(date -d "$CREATED" +%s 2>/dev/null || echo "0")
AGE_DAYS=$(( (NOW_TS - CREATED_TS) / 86400 ))

case "$PRIORITY" in
    0) QUEUE_NOTE="High score — likely ready to merge" ;;
    1) QUEUE_NOTE="Medium score — promising, may need a nudge" ;;
    2) QUEUE_NOTE="Unscored (or score expired) — needs evaluation" ;;
    3) QUEUE_NOTE="Low score — needs work" ;;
    *) QUEUE_NOTE="Unknown" ;;
esac

echo "============================================================"
echo "SCORECARD TRIAGE: $REPO"
echo "PR #$NUMBER: $TITLE"
echo "============================================================"
echo "URL:          $URL"
echo "Author:       $AUTHOR"
echo "Created:      $CREATED  ($AGE_DAYS days ago)"
echo "Base:         $BASE"
echo "Labels:       $LABELS"
echo "Remaining:    $REMAINING PRs in queue  (after $AFTER_DATE)"
echo ""
echo "--- Cached Scorecard ---"
echo "Score:        $CACHED_SCORE / 100  ($CACHED_LABEL)"
echo "Cache status: $CACHE_STATUS"
echo "Scored at:    $SCORED_AT  |  Expires: $EXPIRES_AT"
echo "Queue note:   $QUEUE_NOTE"
echo "============================================================"
echo "PR_NUMBER=$NUMBER"
echo "REPO=$REPO"
echo "CACHE_STATUS=$CACHE_STATUS"
echo "CACHED_SCORE=$CACHED_SCORE"
echo "CACHED_LABEL=$CACHED_LABEL"
