#!/bin/bash
# fetch-activity-prs.sh - Classify open PRs by comment/commit activity relative to our comments
#
# Helps prioritize which PRs need attention during review sessions. Unlike fetch-next-pr.sh
# (which finds unmilestoned PRs for initial triage), this script shows ALL open PRs and
# classifies them by how they relate to our previous engagement:
#
#   NEEDS-REVIEW   New activity (commits OR comments) after our last comment/review
#   WAITING        Our comment or review was the most recent activity — ball in their court
#   NO-COMMENT     We haven't commented or reviewed this PR yet
#   STALE          No activity in --stale-days days and we haven't commented
#
# Streaming mode: use --batch-size + --offset to process PRs in pages, prefetching
# the next batch while reviewing the current one (mirrors fetch-next-pr.sh workflow).
# When a batch ends, a MORE_PRS line is written so the caller knows the next offset.
#
# Usage: fetch-activity-prs.sh <owner/repo> [OPTIONS]
#
# Options:
#   --our-user USER      GitHub username to treat as "ours" (default: sensei-hacker)
#   --stale-days N       Days without any PR activity to consider stale (default: 30)
#   --months N           Only process PRs updated within the last N months; break early
#                        once the sorted list reaches older PRs (shorthand for --cutoff)
#   --cutoff DATE        ISO 8601 date; stop processing PRs updated before this date
#   --batch-size N       Process only N PRs then stop (default: 5)
#   --offset N           Skip the first N PRs in the sorted list; use with --batch-size
#                        to page through results (PRs are sorted updated_at desc)
#   --no-cache           Ignore the 5-minute PR list cache, fetch fresh
#   --output FILE        Write output to FILE instead of stdout
#
# Examples:
#   # First 5 PRs (default batch), last 6 months:
#   bash claude/developer/scripts/triage/fetch-activity-prs.sh iNavFlight/inav --months 6
#
#   # Prefetch next batch while user reviews the first:
#   bash claude/developer/scripts/triage/fetch-activity-prs.sh iNavFlight/inav --months 6 --offset 5 --output ./tmp/claude/prefetch-activity.txt
#
#   # Check for MORE_PRS at end of output file to know if another batch exists:
#   grep "^MORE_PRS:" ./tmp/claude/prefetch-activity.txt
#
#   # Larger batches for a longer review session:
#   bash claude/developer/scripts/triage/fetch-activity-prs.sh iNavFlight/inav --months 6 --batch-size 10

set -euo pipefail

REPO="${1:?Usage: fetch-activity-prs.sh <owner/repo> [OPTIONS]}"
OUR_USER="sensei-hacker"
STALE_DAYS=30
OUTPUT_FILE=""
NO_CACHE=false
BATCH_SIZE=5
OFFSET=0
CUTOFF_DATE=""

shift
while [[ $# -gt 0 ]]; do
    case "$1" in
        --our-user)   OUR_USER="$2";   shift 2 ;;
        --stale-days) STALE_DAYS="$2"; shift 2 ;;
        --output)     OUTPUT_FILE="$2"; shift 2 ;;
        --no-cache)   NO_CACHE=true;   shift ;;
        --batch-size) BATCH_SIZE="$2"; shift 2 ;;
        --offset)     OFFSET="$2";     shift 2 ;;
        --cutoff)     CUTOFF_DATE="$2"; shift 2 ;;
        --months)
            CUTOFF_DATE=$(date -d "-$2 months" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || \
                          date -v -${2}m      +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "")
            shift 2 ;;
        *) echo "Unknown option: $1" >&2; shift ;;
    esac
done

mkdir -p ./tmp/claude

if [[ -n "$OUTPUT_FILE" ]]; then
    exec > "$OUTPUT_FILE" 2>&1
fi

# ISO 8601 stale cutoff date (lexicographically comparable)
STALE_DATE=$(date -d "-${STALE_DAYS} days" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || \
             date -v -${STALE_DAYS}d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "")

REPO_SLUG=$(echo "$REPO" | tr '/' '-')
CACHE_FILE="./tmp/claude/activity-prs-${REPO_SLUG}.json"

# Fetch or reuse cached open PR list (5-minute TTL)
if [[ "$NO_CACHE" == "true" ]] || [[ ! -f "$CACHE_FILE" ]] || \
   [[ $(( $(date +%s) - $(stat -c %Y "$CACHE_FILE" 2>/dev/null || echo 0) )) -gt 300 ]]; then
    echo "Fetching open PRs from $REPO..." >&2
    gh api "repos/${REPO}/pulls?state=open&per_page=100&sort=updated&direction=desc" \
        --paginate \
        --jq '[.[] | select(.draft == false) | {
            number: .number,
            title: .title,
            url: .html_url,
            author: .user.login,
            updatedAt: .updated_at,
            createdAt: .created_at
        }]' | jq -s 'flatten' > "$CACHE_FILE"
fi

PR_COUNT=$(jq 'length' "$CACHE_FILE")
BATCH_DESC=""
[[ $BATCH_SIZE -gt 0 ]] && BATCH_DESC=" (batch: offset=$OFFSET size=$BATCH_SIZE)"
echo "Analyzing $PR_COUNT open non-draft PRs in $REPO (user: $OUR_USER)$BATCH_DESC..." >&2
echo "" >&2

# Temp files for each classification bucket
TMP_NEEDS=$(mktemp)
TMP_WAITING=$(mktemp)
TMP_NOCOMMENT=$(mktemp)
TMP_STALE=$(mktemp)
trap "rm -f $TMP_NEEDS $TMP_WAITING $TMP_NOCOMMENT $TMP_STALE" EXIT

SKIP=0
PROCESSED=0
STOPPED_EARLY=false
NEXT_OFFSET=0

while IFS= read -r pr; do
    UPDATED_AT=$(echo "$pr" | jq -r '.updatedAt')

    # Early exit on cutoff: list is sorted updated_at desc, so all remaining PRs are also old
    if [[ -n "$CUTOFF_DATE" && "$UPDATED_AT" < "$CUTOFF_DATE" ]]; then
        echo "Reached cutoff date (${CUTOFF_DATE:0:10}), stopping." >&2
        break
    fi

    # Skip first OFFSET entries without making any API calls
    if [[ $SKIP -lt $OFFSET ]]; then
        (( SKIP++ )) || true
        continue
    fi

    # Stop after BATCH_SIZE PRs processed
    if [[ $BATCH_SIZE -gt 0 && $PROCESSED -ge $BATCH_SIZE ]]; then
        STOPPED_EARLY=true
        NEXT_OFFSET=$(( OFFSET + PROCESSED ))
        break
    fi

    NUMBER=$(echo "$pr" | jq -r '.number')
    TITLE=$(echo "$pr" | jq -r '.title')
    AUTHOR=$(echo "$pr" | jq -r '.author')

    echo -n "  PR #$NUMBER..." >&2

    # Fetch last 100 issue comments, newest first.
    # This covers PRs with up to 100 substantive comments; for older comments see PR directly.
    # NOTE (2026-09-19): the list-issue-comments endpoint ignores sort=created&direction=desc,
    # returning oldest-first, so `first` below used to pick the OLDEST commenter/our-oldest-comment.
    # Sort in jq instead (matches the REVIEWS handling below).
    COMMENTS=$(gh api "repos/${REPO}/issues/${NUMBER}/comments?per_page=100" \
        --jq '[.[] | {author: .user.login, date: .created_at}] | sort_by(.date) | reverse' 2>/dev/null || echo "[]")

    # Fetch pull request reviews (any non-pending state), newest first
    REVIEWS=$(gh api "repos/${REPO}/pulls/${NUMBER}/reviews" \
        --jq '[.[] | select(.state != "PENDING") | {author: .user.login, date: .submitted_at}] | sort_by(.date) | reverse' \
        2>/dev/null || echo "[]")

    # Our most recent comment date and most recent review date
    OUR_LAST_COMMENT=$(echo "$COMMENTS" | jq -r --arg u "$OUR_USER" \
        '[.[] | select(.author == $u)] | first | .date // ""')
    OUR_LAST_REVIEW=$(echo "$REVIEWS" | jq -r --arg u "$OUR_USER" \
        '[.[] | select(.author == $u)] | first | .date // ""')

    # Most recent of our comment or review
    if   [[ -z "$OUR_LAST_COMMENT" && -z "$OUR_LAST_REVIEW" ]]; then OUR_LAST=""
    elif [[ -z "$OUR_LAST_COMMENT" ]]; then OUR_LAST="$OUR_LAST_REVIEW"
    elif [[ -z "$OUR_LAST_REVIEW"  ]]; then OUR_LAST="$OUR_LAST_COMMENT"
    elif [[ "$OUR_LAST_COMMENT" > "$OUR_LAST_REVIEW" ]]; then OUR_LAST="$OUR_LAST_COMMENT"
    else OUR_LAST="$OUR_LAST_REVIEW"
    fi

    # Most recent commenter and reviewer
    LAST_COMMENTER=$(echo "$COMMENTS" | jq -r 'first | .author // ""')
    LAST_COMMENT_DATE=$(echo "$COMMENTS" | jq -r 'first | .date // ""')
    LAST_REVIEWER=$(echo "$REVIEWS" | jq -r 'first | .author // ""')
    LAST_REVIEW_DATE=$(echo "$REVIEWS" | jq -r 'first | .date // ""')

    # Most recent actor across comments and reviews
    if   [[ -z "$LAST_COMMENT_DATE" && -z "$LAST_REVIEW_DATE" ]]; then LAST_ACTOR=""
    elif [[ "$LAST_COMMENT_DATE" > "$LAST_REVIEW_DATE" ]]; then LAST_ACTOR="$LAST_COMMENTER"
    else LAST_ACTOR="$LAST_REVIEWER"
    fi

    # Stale check: PR's updated_at reflects all activity (commits, comments, reviews, labels)
    IS_STALE=false
    if [[ -n "$STALE_DATE" && "$UPDATED_AT" < "$STALE_DATE" ]]; then
        IS_STALE=true
    fi

    # Short title for display (truncate to 60 chars)
    SHORT_TITLE="${TITLE:0:60}"
    [[ ${#TITLE} -gt 60 ]] && SHORT_TITLE="${SHORT_TITLE}…"

    if [[ -z "$OUR_LAST" ]]; then
        if [[ "$IS_STALE" == "true" ]]; then
            printf "PR #%-5s | %-62s | %-20s | last: %s\n" \
                "$NUMBER" "$SHORT_TITLE" "$AUTHOR" "${UPDATED_AT:0:10}" >> "$TMP_STALE"
            echo " STALE" >&2
        else
            printf "PR #%-5s | %-62s | %-20s | updated: %s\n" \
                "$NUMBER" "$SHORT_TITLE" "$AUTHOR" "${UPDATED_AT:0:10}" >> "$TMP_NOCOMMENT"
            echo " NO-COMMENT" >&2
        fi

    elif [[ "$UPDATED_AT" > "$OUR_LAST" ]]; then
        if [[ "$LAST_ACTOR" == "$OUR_USER" ]]; then
            ANNOTATION="new commit after our comment on ${OUR_LAST:0:10}"
        else
            ANNOTATION="new activity by ${LAST_ACTOR:-unknown} after our comment on ${OUR_LAST:0:10}"
        fi
        printf "PR #%-5s | %-62s | %-20s | %s\n" \
            "$NUMBER" "$SHORT_TITLE" "$AUTHOR" "$ANNOTATION" >> "$TMP_NEEDS"
        echo " NEEDS-REVIEW" >&2

    else
        printf "PR #%-5s | %-62s | %-20s | our comment: %s\n" \
            "$NUMBER" "$SHORT_TITLE" "$AUTHOR" "${OUR_LAST:0:10}" >> "$TMP_WAITING"
        echo " WAITING" >&2
    fi

    (( PROCESSED++ )) || true

done < <(jq -c '.[]' "$CACHE_FILE")

# Count lines in each bucket (handle empty files)
count() { [[ -s "$1" ]] && wc -l < "$1" || echo 0; }
N=$(count "$TMP_NEEDS")
W=$(count "$TMP_WAITING")
C=$(count "$TMP_NOCOMMENT")
S=$(count "$TMP_STALE")

echo "" >&2

# --- Report ---
RANGE_DESC=""
if [[ $BATCH_SIZE -gt 0 ]]; then
    RANGE_END=$(( OFFSET + PROCESSED - 1 ))
    RANGE_DESC=" | PRs $OFFSET–$RANGE_END of $PR_COUNT"
fi

echo "============================================================"
echo "PR ACTIVITY REPORT: $REPO"
echo "User: $OUR_USER  |  Stale threshold: ${STALE_DAYS} days${RANGE_DESC}"
[[ -n "$CUTOFF_DATE" ]] && echo "Cutoff: ${CUTOFF_DATE:0:10} (--months / --cutoff)"
echo "============================================================"
echo ""

echo "=== NEEDS REVIEW ($N) — New activity after your last comment ==="
echo "    New commits, comments, or reviews have arrived since you last spoke."
if [[ -s "$TMP_NEEDS" ]]; then
    cat "$TMP_NEEDS"
else
    echo "  (none)"
fi
echo ""

echo "=== NO COMMENT YET ($C) — You haven't weighed in ==="
if [[ -s "$TMP_NOCOMMENT" ]]; then
    cat "$TMP_NOCOMMENT"
else
    echo "  (none)"
fi
echo ""

echo "=== WAITING ON OTHERS ($W) — Your comment/review was the last activity ==="
echo "    Ball is in their court — safe to skip during this session."
if [[ -s "$TMP_WAITING" ]]; then
    cat "$TMP_WAITING"
else
    echo "  (none)"
fi
echo ""

if [[ -s "$TMP_STALE" ]]; then
    echo "=== STALE ($S) — No activity in ${STALE_DAYS}+ days, you never commented ==="
    cat "$TMP_STALE"
    echo ""
fi

echo "============================================================"
echo "SUMMARY: $N need review  |  $C no comment  |  $W waiting on others  |  $S stale"
echo "============================================================"

# Signal to caller that more PRs exist beyond this batch
if [[ "$STOPPED_EARLY" == "true" ]]; then
    echo "MORE_PRS: next_offset=$NEXT_OFFSET total=$PR_COUNT"
fi
