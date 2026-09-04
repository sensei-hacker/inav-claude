#!/usr/bin/env python3
"""Acquire, release, and inspect the repo checkout locks in claude/locks/.

Single authority for lock-file handling. Do not hand-write lock files or
`rm` them directly — use this script so the format stays exactly what
.claude/hooks/deterministic_checks.py expects (plain `KEY: value` lines,
SESSION_ID matching $CLAUDE_CODE_SESSION_ID) and so the
clean/dirty-checkout sanity check in
claude/developer/guides/CRITICAL-BEFORE-CODE.md always runs before a lock
is handed out.

See claude/locks/README.md for the full design (why three firmware
checkouts, lock file format, dirty-checkout policy). This file is
deliberately terse — usage only.

Usage:
  lock_manager.py acquire --task TASK --branch BRANCH [--type firmware|configurator] [--session ID]
  lock_manager.py release REPO [--force]
  lock_manager.py status
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Keep in sync with _LOCKABLE_REPOS in .claude/hooks/deterministic_checks.py.
FIRMWARE_REPOS = ("inav", "inav2", "inav3")
CONFIGURATOR_REPOS = ("inav-configurator", "inav-configurator2")
ALL_REPOS = FIRMWARE_REPOS + CONFIGURATOR_REPOS


def harness_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def lock_path(root: Path, repo: str) -> Path:
    return root / "claude" / "locks" / f"{repo}.lock"


def parse_lock_file(path: Path) -> dict:
    info = {}
    for line in path.read_text().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            info[key.strip()] = value.strip()
    return info


def check_clean(repo_dir: Path):
    """Return (is_clean, branch, status_preview) for a checkout.

    status_preview is '' when clean, otherwise a short rendering of `git
    status --porcelain` (capped at 10 lines). Callers phrase their own
    advice around it — what a dirty tree means differs for someone
    considering acquiring it vs. someone who just released it.
    """
    try:
        status = subprocess.run(
            ["git", "-C", str(repo_dir), "status", "--porcelain"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        branch = subprocess.run(
            ["git", "-C", str(repo_dir), "branch", "--show-current"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, "", f"git status failed: {e}"

    if not status:
        return True, branch, ""

    lines = status.splitlines()
    preview = "\n    ".join(lines[:10])
    more = f"\n    ... and {len(lines) - 10} more" if len(lines) > 10 else ""
    return False, branch, f"    {preview}{more}"


def cmd_acquire(args) -> int:
    root = harness_root()
    session_id = args.session or os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    if not session_id:
        print("ERROR: no $CLAUDE_CODE_SESSION_ID in environment and --session not given",
              file=sys.stderr)
        return 1

    candidates = FIRMWARE_REPOS if args.type == "firmware" else CONFIGURATOR_REPOS

    blocked = []
    for repo in candidates:
        repo_dir = root / repo
        if not repo_dir.is_dir():
            blocked.append(f"{repo}: checkout does not exist")
            continue

        lp = lock_path(root, repo)
        if lp.exists():
            info = parse_lock_file(lp)
            blocked.append(
                f"{repo}: LOCKED by task '{info.get('TASK', '?')}' "
                f"(session {info.get('SESSION_ID', '?')}, since {info.get('LOCKED_AT', '?')})"
            )
            continue

        is_clean, branch, preview = check_clean(repo_dir)
        if not is_clean:
            blocked.append(
                f"{repo}: unlocked but NOT clean — branch '{branch}' has "
                f"uncommitted changes:\n{preview}\n"
                "  Do not build on top of or discard this. Check "
                "claude/developer/email/sent/ for a completion report "
                "matching this branch/task before assuming it's abandoned."
            )
            continue

        # Found a usable checkout.
        lp.write_text(
            f"LOCKED_BY: Developer\n"
            f"TASK: {args.task}\n"
            f"LOCKED_AT: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"BRANCH: {args.branch}\n"
            f"SESSION_ID: {session_id}\n"
        )
        for b in blocked:
            print(f"  (skipped) {b}", file=sys.stderr)
        print(f"Acquired {repo}.lock — task '{args.task}', branch '{args.branch}'", file=sys.stderr)
        print(repo)  # stdout: the single line callers should capture
        return 0

    print("No usable checkout found:", file=sys.stderr)
    for b in blocked:
        print(f"  {b}", file=sys.stderr)
    print(
        "All candidates are locked by another session or have an unexplained "
        "dirty tree. Investigate before proceeding — do not force an "
        "acquisition. See CRITICAL-BEFORE-CODE.md step 1.",
        file=sys.stderr,
    )
    return 1


def cmd_release(args) -> int:
    root = harness_root()
    if args.repo not in ALL_REPOS:
        print(f"ERROR: unknown repo '{args.repo}' (expected one of {ALL_REPOS})", file=sys.stderr)
        return 1

    lp = lock_path(root, args.repo)
    if not lp.exists():
        print(f"{args.repo}: no lock held (nothing to do)")
        return 0

    info = parse_lock_file(lp)
    session_id = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    holder = info.get("SESSION_ID", "")

    if holder and session_id and holder != session_id and not args.force:
        print(
            f"ERROR: {args.repo}.lock is held by a different session "
            f"(task '{info.get('TASK', '?')}', session {holder}). "
            "Pass --force only if you've confirmed with the user/manager that "
            "it's safe to release someone else's lock.",
            file=sys.stderr,
        )
        return 1

    lp.unlink()
    print(f"Released {args.repo}.lock (was task '{info.get('TASK', '?')}')")

    repo_dir = root / args.repo
    if repo_dir.is_dir():
        is_clean, branch, preview = check_clean(repo_dir)
        if not is_clean:
            print(
                f"WARNING: {args.repo}/ still has uncommitted/untracked files "
                f"on branch '{branch}' — clean these up so the next task can "
                f"use this checkout automatically:\n{preview}",
                file=sys.stderr,
            )
    return 0


def cmd_status(_args) -> int:
    root = harness_root()
    for repo in ALL_REPOS:
        lp = lock_path(root, repo)
        repo_dir = root / repo
        if lp.exists():
            info = parse_lock_file(lp)
            print(f"{repo}: LOCKED — task '{info.get('TASK', '?')}', "
                  f"branch '{info.get('BRANCH', '?')}', "
                  f"since {info.get('LOCKED_AT', '?')}, "
                  f"session {info.get('SESSION_ID', '?')}")
        elif repo_dir.is_dir():
            is_clean, branch, preview = check_clean(repo_dir)
            if is_clean:
                print(f"{repo}: unlocked (clean) — branch '{branch}'")
            else:
                print(f"{repo}: unlocked (DIRTY) — branch '{branch}':\n{preview}")
        else:
            print(f"{repo}: checkout does not exist")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_acquire = sub.add_parser("acquire", help="Find and lock an unlocked, clean checkout")
    p_acquire.add_argument("--task", required=True, help="Task/project name from the assignment")
    p_acquire.add_argument("--branch", required=True, help="Branch name you'll create/use")
    p_acquire.add_argument("--type", choices=["firmware", "configurator"], default="firmware")
    p_acquire.add_argument("--session", default=None, help="Override $CLAUDE_CODE_SESSION_ID")
    p_acquire.set_defaults(func=cmd_acquire)

    p_release = sub.add_parser("release", help="Release a lock you hold")
    p_release.add_argument("repo", choices=ALL_REPOS)
    p_release.add_argument("--force", action="store_true",
                            help="Release even if held by a different session")
    p_release.set_defaults(func=cmd_release)

    p_status = sub.add_parser("status", help="Show lock state of all checkouts")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
