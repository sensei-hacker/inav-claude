#!/usr/bin/env python3
"""Set milestone 10.0 on merged PRs targeting maintenance-10.x.

For each repo (default: iNavFlight/inav and iNavFlight/inav-configurator),
finds merged PRs whose base branch is maintenance-10.x:
  - No milestone set  -> sets milestone to 10.0 (unless --dry-run)
  - Milestone != 10.0 -> left untouched, reported as a possible error
    (never auto-changed - what to do with these may differ per PR)
  - Routine merges of maintenance-9.x/release-9.1 into maintenance-10.x
    -> skipped entirely, not reported (identified by head branch name,
    see is_merge_pr()); these aren't "release work" PRs

Usage:
  tag-maintenance-milestone.py [--repo owner/repo ...] [--dry-run]

Requires: gh (authenticated), python3.
"""
import argparse
import json
import re
import subprocess
import sys

DEFAULT_REPOS = ["iNavFlight/inav", "iNavFlight/inav-configurator"]
BASE_BRANCH = "maintenance-10.x"
TARGET_MILESTONE_TITLE = "10.0"

# Head branch names used for routine maintenance-9.x/release-9.1 -> maintenance-10.x
# merges, e.g. "maintenance-9.x", "release/9.1", "merge/9.1-into-10.x",
# "merge-9x-into-10x". Verified against every merged PR in both repos before use.
MERGE_HEAD_RE = re.compile(r"^(maintenance-9\.x|release/9\.1)$")


def is_merge_pr(head_ref_name):
    if MERGE_HEAD_RE.match(head_ref_name):
        return True
    return head_ref_name.startswith("merge") and re.search(r"9\.x|9\.1", head_ref_name)


def gh_json(args):
    result = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR running gh {' '.join(args)}: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def get_target_milestone_number(repo):
    milestones = gh_json(["api", f"repos/{repo}/milestones", "--paginate"])
    for m in milestones:
        if m["title"] == TARGET_MILESTONE_TITLE:
            return m["number"]
    print(f"ERROR: repo {repo} has no milestone titled '{TARGET_MILESTONE_TITLE}'", file=sys.stderr)
    sys.exit(1)


def get_merged_prs(repo):
    return gh_json([
        "pr", "list", "--repo", repo,
        "--base", BASE_BRANCH, "--state", "merged",
        "--json", "number,title,milestone,mergedAt,headRefName",
        "--limit", "1000",
    ])


def set_milestone(repo, pr_number, milestone_number):
    result = subprocess.run(
        ["gh", "api", "--method", "PATCH", f"repos/{repo}/issues/{pr_number}",
         "-f", f"milestone={milestone_number}", "--silent"],
        capture_output=True, text=True,
    )
    return result.returncode == 0, result.stderr.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", action="append", dest="repos",
                         help="owner/repo to process (repeatable). Default: inav + inav-configurator")
    parser.add_argument("--dry-run", action="store_true",
                         help="Report what would change without modifying anything")
    args = parser.parse_args()
    repos = args.repos or DEFAULT_REPOS

    anomalies = []  # (repo, pr_number, title, milestone_title)
    tagged = []     # (repo, pr_number, title)
    failed = []     # (repo, pr_number, title, error)
    skipped_merges = 0

    for repo in repos:
        print(f"\n=== {repo} ===")
        target_milestone_number = get_target_milestone_number(repo)
        prs = get_merged_prs(repo)
        print(f"Found {len(prs)} merged PR(s) targeting {BASE_BRANCH}")

        for pr in prs:
            number = pr["number"]
            title = pr["title"]
            milestone = pr.get("milestone")

            if is_merge_pr(pr["headRefName"]):
                skipped_merges += 1
                continue

            if milestone is None:
                if args.dry_run:
                    print(f"  [dry-run] would set milestone 10.0 on #{number}: {title}")
                    tagged.append((repo, number, title))
                    continue
                ok, err = set_milestone(repo, number, target_milestone_number)
                if ok:
                    print(f"  OK: #{number} -> milestone 10.0 ({title})")
                    tagged.append((repo, number, title))
                else:
                    print(f"  FAIL: #{number} ({title}): {err}", file=sys.stderr)
                    failed.append((repo, number, title, err))
            elif milestone["title"] != TARGET_MILESTONE_TITLE:
                print(f"  ANOMALY: #{number} already has milestone '{milestone['title']}' ({title})")
                anomalies.append((repo, number, title, milestone["title"]))
            # else: already correctly milestoned, nothing to do

    print("\n" + "=" * 60)
    print(f"Tagged with 10.0: {len(tagged)}")
    print(f"Failed to tag: {len(failed)}")
    print(f"Anomalies (non-10.0 milestone on a maintenance-10.x merge): {len(anomalies)}")
    print(f"Skipped (routine 9.x/9.1 merge PRs): {skipped_merges}")

    if anomalies:
        print("\nPossible errors - merged PRs targeting maintenance-10.x with a different milestone:")
        for repo, number, title, milestone_title in anomalies:
            print(f"  {repo}#{number} [{milestone_title}] {title}")

    if failed:
        print("\nFailed updates:")
        for repo, number, title, err in failed:
            print(f"  {repo}#{number}: {title} - {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
