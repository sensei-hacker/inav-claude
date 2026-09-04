#!/usr/bin/env python3
"""
Deterministic pre-check for evaluator "ask" decisions.

Runs ahead of ClaudeEvaluator.evaluate_with_claude() in both pre_tool_use_hook.py
call sites (handle_bash_tool, handle_general_tool). Covers the one "ask"
trigger that's a pure state check: whether a lock file exists for the repo a
write targets, and if so, whether *this* session is the one holding it.

Build-command, push-target, and PR-target patterns were considered too (per
the original M5 brief) but dropped after checking tool_permissions.log: those
three are already resolved to allow/deny by existing bash_rules before ever
reaching "ask", so a precheck for them would be inert plumbing. Lock file
checks, by contrast, showed up repeatedly in the log (e.g. `rm -rf` under
inav/ while inav.lock was held) - see harness-m05-evaluator-hardening's
completion report for the log evidence.

Session-aware, not just existence-aware: an existence-only check would still
ask every single time even for the session that legitimately holds the lock -
just faster than today, not less annoying. Lock files now carry a SESSION_ID
(see claude/locks/README.md), captured from $CLAUDE_CODE_SESSION_ID at
acquisition time, so a matching session can skip the prompt entirely for
plain write-safety asks. This does NOT extend to asks with their own
independent risk rationale (recursive delete, find -exec, redirects) - lock
ownership answers "is this my repo to work in", not "is this specific
operation safe", so those keep going through the model/user regardless of
who holds the lock.

Conservative contract: this can only return ('allow', reason), ('ask_user',
reason), or None (escalate to the model - unlocked, or a named risk rule
independent of lock state). Any internal error is treated as a hit toward
ask_user, never allow - the same fail-safe bias as the rest of this evaluator.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple

# Repos with a claude/locks/<name>.lock file, per claude/locks/README.md.
_LOCKABLE_REPOS = ('inav-configurator', 'inav-configurator2', 'inav3', 'inav2', 'inav')

# rule_name values whose only concern is "this is a write" (no independent
# risk rationale) - the only ones a session-match lock check may override.
# None is the Bash category-default fallback (no rule matched); "Confirm file
# modifications" is the general-tool Write/Edit catch-all rule.
_GENERIC_WRITE_RULE_NAMES = frozenset({None, "Confirm file modifications"})


def _harness_root() -> str:
    hook_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(hook_dir))


def _repo_for_path(path: Optional[str]) -> Optional[str]:
    """Return the lockable repo name that `path` lives under, if any."""
    if not path:
        return None
    parts = Path(path).parts
    for repo in _LOCKABLE_REPOS:
        if repo in parts:
            return repo
    return None


def _parse_lock_file(lock_path: str) -> Dict[str, str]:
    info = {}
    with open(lock_path) as f:
        for line in f:
            if ':' in line:
                key, _, value = line.partition(':')
                info[key.strip()] = value.strip()
    return info


def lock_file_precheck(
    path: Optional[str],
    category: str,
    rule_name: Optional[str],
    current_session_id: Optional[str],
) -> Optional[Tuple[str, str]]:
    """Check whether `path` is a write into a currently-locked repo.

    Returns (decision, message) with decision 'allow' or 'ask_user', or None
    to escalate to the model as before - either the repo isn't locked, or
    this ask came from a rule with its own risk rationale independent of
    lock ownership (recursive delete, etc.), which lock-matching can't
    override.
    """
    try:
        if category != 'write':
            return None

        repo = _repo_for_path(path)
        if not repo:
            return None

        lock_path = os.path.join(_harness_root(), 'claude', 'locks', f'{repo}.lock')
        if not os.path.exists(lock_path):
            return None

        lock_info = _parse_lock_file(lock_path)
        lock_session = lock_info.get('SESSION_ID')

        if lock_session and current_session_id and lock_session == current_session_id:
            if rule_name in _GENERIC_WRITE_RULE_NAMES:
                return ('allow', f"this session holds {repo}.lock")
            # Session matches, but this ask has its own risk rationale
            # independent of lock ownership - let the model evaluate it.
            return None

        return ('ask_user', (
            f"{repo}/ is locked (claude/locks/{repo}.lock) by a different "
            "session. Please confirm this write is intentional."
        ))
    except Exception as e:
        return ('ask_user', f"pre-check error, failing safe to ask_user: {e}")
