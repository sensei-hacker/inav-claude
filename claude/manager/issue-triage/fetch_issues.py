#!/usr/bin/env python3
"""
Fetch and categorize GitHub issues from iNavFlight/inav repository.

Usage:
    ./fetch_issues.py                    # Fetch recent open issues
    ./fetch_issues.py --pages 3          # Fetch 3 pages (300 issues)
    ./fetch_issues.py --issue 11156      # View specific issue details
    ./fetch_issues.py --refresh          # Refresh issues.json cache
"""

import subprocess
import json
import sys
import os
from datetime import datetime
from pathlib import Path

REPO = "iNavFlight/inav"
SCRIPT_DIR = Path(__file__).parent
ISSUES_CACHE = SCRIPT_DIR / "issues.json"
TRIAGE_FILE = SCRIPT_DIR / "triage.md"

def run_gh_api(endpoint):
    """Run gh api command and return parsed JSON."""
    cmd = ["gh", "api", endpoint]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Failed to parse JSON from: {endpoint}", file=sys.stderr)
        return None

def fetch_issues(pages=2):
    """Fetch open issues (not PRs) from the repository."""
    all_issues = []

    for page in range(1, pages + 1):
        print(f"Fetching page {page}...", file=sys.stderr)
        endpoint = f"repos/{REPO}/issues?state=open&per_page=100&page={page}&sort=created&direction=desc"
        data = run_gh_api(endpoint)

        if not data:
            break

        # Filter out PRs
        issues = [i for i in data if 'pull_request' not in i]
        all_issues.extend(issues)

        if len(data) < 100:
            break  # No more pages

    return all_issues

def format_issue_summary(issue):
    """Format a single issue for display."""
    labels = ", ".join([l['name'] for l in issue.get('labels', [])])
    created = issue['created_at'][:10]
    comments = issue.get('comments', 0)

    title = issue['title']
    if len(title) > 70:
        title = title[:67] + "..."

    return f"#{issue['number']:5d} | {created} | {comments:2d}c | {title} [{labels}]"

def view_issue(issue_number):
    """View detailed information about a specific issue."""
    endpoint = f"repos/{REPO}/issues/{issue_number}"
    issue = run_gh_api(endpoint)

    if not issue:
        return

    print(f"\n{'='*80}")
    print(f"Issue #{issue['number']}: {issue['title']}")
    print(f"{'='*80}")
    print(f"URL: {issue['html_url']}")
    print(f"Created: {issue['created_at'][:10]} by {issue['user']['login']}")
    print(f"Comments: {issue.get('comments', 0)}")
    labels = ", ".join([l['name'] for l in issue.get('labels', [])])
    print(f"Labels: {labels or '(none)'}")
    print(f"\n--- Body ---\n")
    body = issue.get('body', '(no description)')
    if body and len(body) > 2000:
        print(body[:2000] + "\n\n... [truncated]")
    else:
        print(body)
    print(f"\n{'='*80}\n")

def save_issues(issues):
    """Save issues to cache file."""
    cache_data = {
        'fetched_at': datetime.now().isoformat(),
        'count': len(issues),
        'issues': issues
    }
    with open(ISSUES_CACHE, 'w') as f:
        json.dump(cache_data, f, indent=2)
    print(f"Saved {len(issues)} issues to {ISSUES_CACHE}", file=sys.stderr)

def load_cached_issues():
    """Load issues from cache if available."""
    if ISSUES_CACHE.exists():
        with open(ISSUES_CACHE) as f:
            data = json.load(f)
        print(f"Loaded {data['count']} issues from cache (fetched {data['fetched_at'][:10]})", file=sys.stderr)
        return data['issues']
    return None

def print_issues_list(issues):
    """Print formatted list of issues."""
    print(f"\n{'#':>6} | {'Created':10} | {'C':>3} | {'Title':<70}")
    print("-" * 100)
    for issue in issues:
        print(format_issue_summary(issue))

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Fetch and analyze GitHub issues')
    parser.add_argument('--pages', type=int, default=2, help='Number of pages to fetch (100 issues/page)')
    parser.add_argument('--issue', type=int, help='View specific issue number')
    parser.add_argument('--refresh', action='store_true', help='Force refresh from GitHub')
    parser.add_argument('--search', type=str, help='Search issues by keyword')
    args = parser.parse_args()

    if args.issue:
        view_issue(args.issue)
        return

    # Load or fetch issues
    if args.refresh or not ISSUES_CACHE.exists():
        issues = fetch_issues(args.pages)
        if issues:
            save_issues(issues)
    else:
        issues = load_cached_issues()

    if not issues:
        print("No issues found", file=sys.stderr)
        return

    # Filter by search if specified
    if args.search:
        keyword = args.search.lower()
        issues = [i for i in issues if keyword in i['title'].lower() or
                  (i.get('body') and keyword in i['body'].lower())]
        print(f"Found {len(issues)} issues matching '{args.search}'")

    print_issues_list(issues)
    print(f"\nTotal: {len(issues)} open issues")
    print(f"\nUse --issue NUMBER to view details")

if __name__ == '__main__':
    main()
