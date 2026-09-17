#!/usr/bin/env python3
"""
Interactive PR Documentation Tagger

After running check_pr_docs.sh, this script helps interactively tag PRs
that need documentation with the "documentation needed" label.
"""

import subprocess
import sys
import json
from typing import List, Dict, Tuple


def get_prs_needing_docs(repo: str, days_back: int = 7) -> List[Dict]:
    """
    Get list of PRs that might need documentation.
    Returns list of PR objects with metadata.
    """
    # Calculate search date
    try:
        date_cmd = subprocess.run(
            ["date", "-d", f"{days_back} days ago", "+%Y-%m-%d"],
            capture_output=True,
            text=True,
            check=True
        )
        search_date = date_cmd.stdout.strip()
    except subprocess.CalledProcessError:
        # Try macOS date command
        date_cmd = subprocess.run(
            ["date", "-v", f"-{days_back}d", "+%Y-%m-%d"],
            capture_output=True,
            text=True,
            check=True
        )
        search_date = date_cmd.stdout.strip()

    # Get PRs from GitHub
    cmd = [
        "gh", "pr", "list",
        "--state", "all",
        "--search", f"created:>={search_date}",
        "--json", "number,title,author,state,labels,files",
        "--repo", f"inavflight/{repo}"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    prs = json.loads(result.stdout)

    # Filter PRs that might need docs
    prs_needing_docs = []

    for pr in prs:
        # Skip if already has documentation label
        label_names = [label['name'].lower() for label in pr.get('labels', [])]
        if any('doc' in label for label in label_names):
            continue

        # Check if PR has docs files
        files = pr.get('files', [])
        has_docs_files = any(
            'docs/' in f['path'].lower() or
            'readme' in f['path'].lower() or
            f['path'].endswith('.md')
            for f in files
        )

        # Check if user-facing changes
        has_user_changes = any(
            'src/main/cli' in f['path'] or
            'src/main/msp' in f['path'] or
            'src/main/io/osd' in f['path'] or
            'src/main/navigation' in f['path'] or
            'src/main/telemetry' in f['path']
            for f in files
        )

        # Check title for feature indicators
        title_lower = pr['title'].lower()
        is_feature = any(word in title_lower for word in ['add', 'new', 'feature', 'implement'])
        is_internal = any(word in title_lower for word in ['refactor', 'cleanup', 'format', 'test', 'ci', 'build'])

        # If user-facing changes or feature, but no docs, flag it
        if (has_user_changes or is_feature) and not has_docs_files and not is_internal:
            prs_needing_docs.append(pr)

    return prs_needing_docs


def check_wiki_for_pr(repo: str, pr_number: int, author: str) -> Tuple[bool, str]:
    """
    Check if wiki has commits related to this PR.
    Returns (has_wiki_commit, reason)
    """
    wiki_path = f"inav.wiki" if repo == "inav" else "inav-configurator.wiki"

    try:
        # Check for PR reference — full message, any form (bare #N, repo-qualified, or /pull/N URL)
        cmd = ["git", "log", "--since=14 days ago", "--grep", f"#{pr_number}", "--grep", f"/pull/{pr_number}", "--pretty=format:%s"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=wiki_path)
        if result.stdout.strip():
            return True, f"Wiki commit references #{pr_number}"

        # Check for commits by same author
        cmd = ["git", "log", "--since=14 days ago", "--author", author, "--pretty=format:%s"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=wiki_path)
        if result.stdout.strip():
            commits = result.stdout.strip().split('\n')
            return True, f"Wiki has {len(commits)} commit(s) by same author"

    except Exception as e:
        return False, f"Error checking wiki: {e}"

    return False, "No wiki commits found"


def check_docs_site_for_pr(repo: str, pr_number: int, author: str) -> Tuple[bool, str]:
    """
    Check if the Docusaurus docs site has commits related to this PR.
    Returns (has_docs_commit, reason)
    """
    docs_path = "iNavFlight.github.io"

    try:
        # Check for PR reference — full message, any form (bare #N, repo-qualified, or /pull/N URL)
        cmd = ["git", "log", "--since=14 days ago", "--grep", f"#{pr_number}", "--grep", f"/pull/{pr_number}", "--pretty=format:%s"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=docs_path)
        if result.stdout.strip():
            return True, f"Docs-site commit references #{pr_number}"

        # Check for commits by same author
        cmd = ["git", "log", "--since=14 days ago", "--author", author, "--pretty=format:%s"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=docs_path)
        if result.stdout.strip():
            commits = result.stdout.strip().split('\n')
            return True, f"Docs site has {len(commits)} commit(s) by same author"

    except Exception as e:
        return False, f"Error checking docs site: {e}"

    return False, "No docs-site commits found"


def ask_user_to_tag(repo: str, pr: Dict, wiki_info: str) -> bool:
    """
    Ask user if they want to tag this PR.
    Returns True if user wants to tag.
    """
    print("\n" + "=" * 70)
    print(f"PR #{pr['number']} - {pr['title']}")
    print(f"Author: {pr['author']['login']}")
    print(f"State: {pr['state']}")
    print(f"Docs check: {wiki_info}")
    print("-" * 70)

    # Show some file changes
    print("Files changed:")
    for file in pr.get('files', [])[:10]:  # Show first 10 files
        print(f"  - {file['path']}")
    if len(pr.get('files', [])) > 10:
        print(f"  ... and {len(pr['files']) - 10} more")

    print("-" * 70)
    print("\nShould this PR be tagged with 'documentation needed' label?")
    print("  [y] Yes, tag it")
    print("  [n] No, skip")
    print("  [v] View PR in browser first")
    print("  [q] Quit")

    while True:
        choice = input("\nYour choice [y/n/v/q]: ").strip().lower()

        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        elif choice == 'v':
            # Open PR in browser
            subprocess.run(["gh", "pr", "view", str(pr['number']), "--web", "--repo", f"inavflight/{repo}"])
            print("\nOpened PR in browser. Now, should it be tagged?")
        elif choice == 'q':
            print("\nQuitting...")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter y, n, v, or q.")


def tag_pr(repo: str, pr_number: int, label: str = "documentation needed") -> bool:
    """
    Add label to PR.
    Returns True if successful.
    """
    try:
        cmd = [
            "gh", "pr", "edit", str(pr_number),
            "--add-label", label,
            "--repo", f"inavflight/{repo}"
        ]
        subprocess.run(cmd, check=True)
        print(f"✅ Tagged PR #{pr_number} with '{label}'")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to tag PR #{pr_number}: {e}")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print(__doc__)
        print("\nUsage:")
        print("  python3 tag_pr_docs.py [repo] [days_back]")
        print("\nExamples:")
        print("  python3 tag_pr_docs.py              # Check both repos, last 7 days")
        print("  python3 tag_pr_docs.py inav         # Check only inav repo")
        print("  python3 tag_pr_docs.py inav 14      # Check inav, last 14 days")
        sys.exit(0)

    # Determine which repos to check
    if len(sys.argv) > 1:
        repos = [sys.argv[1]]
    else:
        repos = ["inav", "inav-configurator"]

    days_back = int(sys.argv[2]) if len(sys.argv) > 2 else 7

    print(f"Checking PRs from last {days_back} days...")
    print()

    total_tagged = 0
    total_checked = 0

    for repo in repos:
        print(f"\n{'=' * 70}")
        print(f"Repository: {repo}")
        print('=' * 70)

        prs = get_prs_needing_docs(repo, days_back)

        if not prs:
            print(f"\nNo PRs needing documentation review found in {repo}")
            continue

        print(f"\nFound {len(prs)} PR(s) that may need documentation")

        for pr in prs:
            total_checked += 1

            # Check wiki and docs site
            has_wiki, wiki_info = check_wiki_for_pr(repo, pr['number'], pr['author']['login'])
            has_docs_site, docs_info = check_docs_site_for_pr(repo, pr['number'], pr['author']['login'])

            if has_wiki or has_docs_site:
                reasons = []
                if has_wiki:
                    reasons.append(wiki_info)
                if has_docs_site:
                    reasons.append(docs_info)
                print(f"\n✅ PR #{pr['number']} - {pr['title']}")
                print(f"   {'; '.join(reasons)} - Skipping")
                continue

            # Ask user
            combined_info = f"{wiki_info} | {docs_info}"
            if ask_user_to_tag(repo, pr, combined_info):
                if tag_pr(repo, pr['number']):
                    total_tagged += 1

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"PRs checked: {total_checked}")
    print(f"PRs tagged: {total_tagged}")
    print("\nDone!")


if __name__ == "__main__":
    main()
