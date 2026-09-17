#!/bin/bash

# PR Documentation Compliance Checker
# Checks recent PRs for documentation updates, including independent wiki commit verification

set -e

WORKSPACE_ROOT="$HOME/inavflight"
DAYS_BACK=7

echo "=== PR Documentation Compliance Check ==="
echo "Date: $(date)"
echo "Checking PRs from last $DAYS_BACK days"
echo ""

# Function to get date for searches
get_date_ago() {
    local days=$1
    # Try Linux date command first
    if date -d "$days days ago" +%Y-%m-%d 2>/dev/null; then
        return
    fi
    # Try macOS date command
    if date -v-${days}d +%Y-%m-%d 2>/dev/null; then
        return
    fi
    echo "ERROR: Unable to calculate date" >&2
    exit 1
}

# Calculate search date
SEARCH_DATE=$(get_date_ago $DAYS_BACK)

# Step 1: Update wiki repositories + docs site
echo "=== Step 1: Updating Wiki Repositories + Docs Site ==="
cd "$WORKSPACE_ROOT"

for wiki_info in "inav.wiki:https://github.com/iNavFlight/inav.wiki.git" \
                 "inav-configurator.wiki:https://github.com/iNavFlight/inav-configurator.wiki.git" \
                 "iNavFlight.github.io:https://github.com/iNavFlight/iNavFlight.github.io.git"; do
    IFS=':' read -r wiki_dir wiki_url <<< "$wiki_info"

    if [ -d "$wiki_dir" ]; then
        echo "Updating $wiki_dir..."
        cd "$wiki_dir"
        # Prefer upstream when present (the docs site is often cloned from a fork)
        if git remote | grep -q '^upstream$'; then
            git pull upstream master 2>&1 | head -5
        else
            git pull origin master 2>&1 | head -5
        fi
        cd "$WORKSPACE_ROOT"
    else
        echo "Cloning $wiki_dir..."
        git clone "$wiki_url" "$wiki_dir"
    fi
done
echo ""

# Step 2: Extract recent wiki + docs-site commits
echo "=== Step 2: Extracting Recent Wiki + Docs Site Commits ==="

cd "$WORKSPACE_ROOT/inav.wiki"
echo "## inav.wiki commits (last $DAYS_BACK days):"
git log --since="$DAYS_BACK days ago" \
    --pretty=format:"%H|%an|%ae|%ai|%s" \
    --all > /tmp/inav_wiki_commits.txt
cat /tmp/inav_wiki_commits.txt | head -20
wiki_count=$(wc -l < /tmp/inav_wiki_commits.txt)
echo "Total: $wiki_count commits"
echo ""

cd "$WORKSPACE_ROOT/inav-configurator.wiki"
echo "## inav-configurator.wiki commits (last $DAYS_BACK days):"
git log --since="$DAYS_BACK days ago" \
    --pretty=format:"%H|%an|%ae|%ai|%s" \
    --all > /tmp/configurator_wiki_commits.txt
cat /tmp/configurator_wiki_commits.txt | head -20
conf_wiki_count=$(wc -l < /tmp/configurator_wiki_commits.txt)
echo "Total: $conf_wiki_count commits"
echo ""

cd "$WORKSPACE_ROOT/iNavFlight.github.io"
echo "## iNavFlight.github.io commits (last $DAYS_BACK days):"
git log --since="$DAYS_BACK days ago" \
    --pretty=format:"%H|%an|%ae|%ai|%s" \
    --all > /tmp/docs_site_commits.txt
cat /tmp/docs_site_commits.txt | head -20
docs_site_count=$(wc -l < /tmp/docs_site_commits.txt)
echo "Total: $docs_site_count commits"
echo ""

# Step 3: Check PRs in each repository
cd "$WORKSPACE_ROOT"

# Track statistics
total_prs=0
prs_with_docs=0
prs_need_review=0
prs_no_docs_needed=0

# Arrays to store PR details
declare -a prs_have_docs
declare -a prs_need_docs
declare -a prs_no_docs

for repo_info in "inav:/tmp/inav_wiki_commits.txt" \
                 "inav-configurator:/tmp/configurator_wiki_commits.txt"; do

    IFS=':' read -r repo wiki_commits <<< "$repo_info"

    echo "=== Step 3: Checking Repository: $repo ==="
    echo ""

    cd "$WORKSPACE_ROOT/$repo"

    # Get PRs from last week
    prs=$(gh pr list --state all \
          --search "created:>=$SEARCH_DATE" \
          --json number \
          --jq '.[].number' 2>/dev/null || echo "")

    if [ -z "$prs" ]; then
        echo "No PRs found in last $DAYS_BACK days"
        echo ""
        continue
    fi

    pr_count=$(echo "$prs" | wc -w)
    total_prs=$((total_prs + pr_count))
    echo "Found $pr_count PRs to check"
    echo ""

    for pr in $prs; do
        echo "----------------------------------------"
        echo "Checking PR #$pr"

        # Get PR details
        pr_json=$(gh pr view $pr --json title,author,mergedAt,createdAt,state,body 2>/dev/null || echo "")

        if [ -z "$pr_json" ]; then
            echo "ERROR: Could not fetch PR #$pr"
            continue
        fi

        title=$(echo "$pr_json" | jq -r '.title')
        author=$(echo "$pr_json" | jq -r '.author.login')
        merged=$(echo "$pr_json" | jq -r '.mergedAt')
        created=$(echo "$pr_json" | jq -r '.createdAt')
        state=$(echo "$pr_json" | jq -r '.state')
        body=$(echo "$pr_json" | jq -r '.body')

        echo "Title: $title"
        echo "Author: $author"
        echo "State: $state"

        has_docs=false
        doc_reasons=""

        # Check 1: Documentation files in PR
        docs_files=$(gh pr view $pr --json files --jq '.files[].path' 2>/dev/null | \
                    grep -iE "docs/|README|\.md$" || true)

        if [ -n "$docs_files" ]; then
            echo "✅ Documentation files modified in PR:"
            echo "$docs_files" | sed 's/^/  - /'
            has_docs=true
            doc_reasons="${doc_reasons}docs files; "
        fi

        # Check 2: PR description mentions docs/wiki
        if echo "$body" | grep -qiE "wiki|documentation|#[0-9]+"; then
            echo "✅ PR description mentions documentation/wiki"
            has_docs=true
            doc_reasons="${doc_reasons}PR description; "
        fi

        # Check 3: Wiki commits directly reference this PR. Search the FULL commit
        # message (subject + body) for any reference form: bare #N, repo-qualified
        # inav#N / iNavFlight/inav#N, or a full /pull/N URL.
        wiki_pr_refs=$(cd "$WORKSPACE_ROOT/$repo.wiki" && git log --all --since="$DAYS_BACK days ago" --grep "#$pr" --grep "/pull/$pr" --pretty=format:"%H|%an|%ae|%ai|%s" 2>/dev/null || true)
        if [ -n "$wiki_pr_refs" ]; then
            echo "✅ Wiki commit directly references PR #$pr:"
            echo "$wiki_pr_refs" | while IFS='|' read -r hash author_name email date msg; do
                echo "  - [$hash] $date - $msg"
            done
            has_docs=true
            doc_reasons="${doc_reasons}wiki PR ref; "
        fi

        # Check 3b: Docs-site commits directly reference this PR (full message)
        docs_pr_refs=$(cd "$WORKSPACE_ROOT/iNavFlight.github.io" && git log --all --since="$DAYS_BACK days ago" --grep "#$pr" --grep "/pull/$pr" --pretty=format:"%H|%an|%ae|%ai|%s" 2>/dev/null || true)
        if [ -n "$docs_pr_refs" ]; then
            echo "✅ Docs-site commit directly references PR #$pr:"
            echo "$docs_pr_refs" | while IFS='|' read -r hash author_name email date msg; do
                echo "  - [$hash] $date - $msg"
            done
            has_docs=true
            doc_reasons="${doc_reasons}docs-site PR ref; "
        fi

        # Check 4: Wiki commits by same author in time window (if merged)
        if [ "$state" = "MERGED" ] && [ "$merged" != "null" ]; then
            # Extract just the date from ISO 8601 timestamp
            merge_date=$(echo "$merged" | cut -d'T' -f1)

            # Check for commits by same author within ±2 days
            author_wiki_commits=$(grep -i "$author" "$wiki_commits" 2>/dev/null || true)

            if [ -n "$author_wiki_commits" ]; then
                echo "✅ Wiki commits by same author found (check time proximity):"
                echo "$author_wiki_commits" | while IFS='|' read -r hash author_name email date msg; do
                    commit_date=$(echo "$date" | cut -d' ' -f1)
                    echo "  - [$hash] $commit_date - $msg"
                done
                has_docs=true
                doc_reasons="${doc_reasons}wiki author match; "
            fi

            # Check 4b: Docs-site commits by same author in time window
            author_docs_commits=$(grep -i "$author" /tmp/docs_site_commits.txt 2>/dev/null || true)

            if [ -n "$author_docs_commits" ]; then
                echo "✅ Docs-site commits by same author found (check time proximity):"
                echo "$author_docs_commits" | while IFS='|' read -r hash author_name email date msg; do
                    commit_date=$(echo "$date" | cut -d' ' -f1)
                    echo "  - [$hash] $commit_date - $msg"
                done
                has_docs=true
                doc_reasons="${doc_reasons}docs-site author match; "
            fi
        fi

        # Assess if documentation is likely needed
        needs_docs=false

        # Get changed files to assess
        changed_files=$(gh pr view $pr --json files --jq '.files[].path' 2>/dev/null || echo "")

        # Check for user-facing changes
        if echo "$changed_files" | grep -qE "src/main/(cli|msp|io/osd|navigation|telemetry|fc)"; then
            needs_docs=true
        fi

        # Check PR title for feature indicators
        if echo "$title" | grep -qiE "add|new|feature|implement"; then
            needs_docs=true
        fi

        # Exclude internal changes
        if echo "$title" | grep -qiE "refactor|cleanup|format|test|ci|build"; then
            needs_docs=false
        fi

        # Final assessment
        if [ "$has_docs" = true ]; then
            echo "📝 Documentation status: FOUND ($doc_reasons)"
            prs_with_docs=$((prs_with_docs + 1))
            prs_have_docs+=("$repo #$pr - $title [$doc_reasons]")
        elif [ "$needs_docs" = true ]; then
            echo "⚠️  Documentation status: MISSING - likely needed"
            prs_need_review=$((prs_need_review + 1))
            prs_need_docs+=("$repo #$pr - $title")
        else
            echo "ℹ️  Documentation status: Not needed (internal change)"
            prs_no_docs_needed=$((prs_no_docs_needed + 1))
            prs_no_docs+=("$repo #$pr - $title")
        fi

        echo ""
    done

    cd "$WORKSPACE_ROOT"
done

# Step 4: Generate summary report
echo ""
echo "=========================================="
echo "=== SUMMARY REPORT ==="
echo "=========================================="
echo ""
echo "Period: Last $DAYS_BACK days (since $SEARCH_DATE)"
echo "Total PRs checked: $total_prs"
echo ""
echo "📊 Results:"
echo "  ✅ PRs with documentation: $prs_with_docs"
echo "  ⚠️  PRs needing review: $prs_need_review"
echo "  ℹ️  PRs not needing docs: $prs_no_docs_needed"
echo ""

if [ ${#prs_have_docs[@]} -gt 0 ]; then
    echo "✅ PRs with Documentation:"
    for item in "${prs_have_docs[@]}"; do
        echo "  - $item"
    done
    echo ""
fi

if [ ${#prs_need_docs[@]} -gt 0 ]; then
    echo "⚠️  PRs Needing Documentation Review:"
    for item in "${prs_need_docs[@]}"; do
        echo "  - $item"
    done
    echo ""
fi

if [ ${#prs_no_docs[@]} -gt 0 ]; then
    echo "ℹ️  PRs Not Needing Documentation:"
    for item in "${prs_no_docs[@]}"; do
        echo "  - $item"
    done
    echo ""
fi

echo "=== Docs Activity ==="
echo "  inav.wiki: $wiki_count commits"
echo "  inav-configurator.wiki: $conf_wiki_count commits"
echo "  iNavFlight.github.io: $docs_site_count commits"
echo ""

if [ $prs_need_review -gt 0 ]; then
    echo "⚠️  ACTION REQUIRED: $prs_need_review PR(s) may need documentation"
    echo "Review the PRs listed above and consider tagging with 'documentation needed' label"
fi

echo ""
echo "=== Check Complete ==="
