#!/usr/bin/env python3
"""Set a target milestone on merged PRs targeting a given base branch.

For each repo (default: iNavFlight/inav and iNavFlight/inav-configurator),
finds merged PRs whose base branch is --base (default maintenance-10.x):
  - No milestone set  -> sets milestone to --milestone (default 10.0), unless --dry-run
  - Milestone != target -> left untouched, reported as a possible error
    (never auto-changed - what to do with these may differ per PR)
  - Routine merges of the previous release line into the base
    -> skipped entirely, not reported (identified by head branch name,
    see is_merge_pr()); these aren't "release work" PRs

Usage:
  tag-maintenance-milestone.py [--repo owner/repo ...] [--base BRANCH] [--milestone TITLE] [--dry-run]

Examples:
  # Default: maintenance-10.x -> 10.0
  tag-maintenance-milestone.py

  # Future release cycle
  tag-maintenance-milestone.py --base maintenance-11.x --milestone 11.0

Requires: gh (authenticated), python3.
"""
import argparse
import json
import re
import subprocess
import sys

DEFAULT_REPOS = ["iNavFlight/inav", "iNavFlight/inav-configurator"]

# Head branch names used for routine "previous release line -> current base" merges.
# Currently encodes maintenance-9.x / release/9.1 flowing into maintenance-10.x.
# If --base/--milestone are used for a later release cycle, extend this pattern
# (and is_merge_pr below) to cover the new previous line, e.g. maintenance-10.x /
# release/10.0 flowing into maintenance-11.x.
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


def get_target_milestone_number(repo, milestone_title):
    milestones = gh_json(["api", f"repos/{repo}/milestones", "--paginate"])
    for m in milestones:
        if m["title"] == milestone_title:
            return m["number"]
    print(f"ERROR: repo {repo} has no milestone titled '{milestone_title}'", file=sys.stderr)
    sys.exit(1)


def get_merged_prs(repo, base_branch):
    return gh_json([
        "pr", "list", "--repo", repo,
        "--base", base_branch, "--state", "merged",
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
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo", action="append", dest="repos",
                        help="owner/repo to process (repeatable). Default: inav + inav-configurator")
    parser.add_argument("--base", default="maintenance-10.x",
                        help="base branch of merged PRs to tag (default: maintenance-10.x)")
    parser.add_argument("--milestone", default="10.0",
                        help="milestone title to set (default: 10.0)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would change without modifying anything")
    args = parser.parse_args()
    repos = args.repos or DEFAULT_REPOS
    base_branch = args.base
    milestone_title = args.milestone

    anomalies = []  # (repo, pr_number, title, milestone_title)
    tagged = []     # (repo, pr_number, title)
    failed = []     # (repo, pr_number, title, error)
    skipped_merges = 0

    for repo in repos:
        print(f"\n=== {repo} ===")
        target_milestone_number = get_target_milestone_number(repo, milestone_title)
        prs = get_merged_prs(repo, base_branch)
        print(f"Found {len(prs)} merged PR(s) targeting {base_branch}")

        for pr in prs:
            number = pr["number"]
            title = pr["title"]
            milestone = pr.get("milestone")

            if is_merge_pr(pr["headRefName"]):
                skipped_merges += 1
                continue

            if milestone is None:
                if args.dry_run:
                    print(f"  [dry-run] would set milestone {milestone_title} on #{number}: {title}")
                    tagged.append((repo, number, title))
                    continue
                ok, err = set_milestone(repo, number, target_milestone_number)
                if ok:
                    print(f"  OK: #{number} -> milestone {milestone_title} ({title})")
                    tagged.append((repo, number, title))
                else:
                    print(f"  FAIL: #{number} ({title}): {err}", file=sys.stderr)
                    failed.append((repo, number, title, err))
            elif milestone["title"] != milestone_title:
                print(f"  ANOMALY: #{number} already has milestone '{milestone['title']}' ({title})")
                anomalies.append((repo, number, title, milestone["title"]))
            # else: already correctly milestoned, nothing to do

    print("\n" + "=" * 60)
    print(f"Tagged with {milestone_title}: {len(tagged)}")
    print(f"Failed to tag: {len(failed)}")
    print(f"Anomalies (non-{milestone_title} milestone on a {base_branch} merge): {len(anomalies)}")
    print(f"Skipped (routine previous-line merge PRs): {skipped_merges}")

    if anomalies:
        print(f"\nPossible errors - merged PRs targeting {base_branch} with a different milestone:")
        for repo, number, title, ms_title in anomalies:
            print(f"  {repo}#{number} [{ms_title}] {title}")

    if failed:
        print("\nFailed updates:")
        for repo, number, title, err in failed:
            print(f"  {repo}#{number}: {title} - {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
