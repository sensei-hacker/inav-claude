#!/usr/bin/env python3
"""
Project Operations - Atomic project lifecycle operations

Prevents drift between INDEX.md, completed/INDEX.md, and directory structure
by performing all related changes in a single operation.

Commands:
    create <project>      Create new project (dir + files + INDEX entry)
    complete <project>    Move project to completed (dir + both indexes)
    block <project>       Move project to blocked (dir + index status)
    backburner <project>  Move project to backburner (dir + index status)
    resume <project>      Move project back to active (from blocked/backburner)
    cancel <project>      Move project to completed as cancelled
    audit                 Check for inconsistencies between dirs and indexes
    audit --fix            Fix simple inconsistencies automatically
    audit --fix --dry-run  Preview what --fix would do without changing anything
    audit --fix --force    Also delete a stale copy when a duplicate exists in
                            completed/ (without --force this is reported, not fixed)
"""

import re
import sys
import shutil
from pathlib import Path
from datetime import date


# Local project data lives in claude/projects/ (gitignored); this script is
# framework tooling under claude/manager/scripts/.
REPO_ROOT = Path(__file__).resolve().parents[3]
PROJECTS_DIR = REPO_ROOT / "claude" / "projects"
INDEX_PATH = PROJECTS_DIR / "INDEX.md"
COMPLETED_INDEX_PATH = PROJECTS_DIR / "completed" / "INDEX.md"
ACTIVE_DIR = PROJECTS_DIR / "active"
COMPLETED_DIR = PROJECTS_DIR / "completed"
BLOCKED_DIR = PROJECTS_DIR / "blocked"
BACKBURNER_DIR = PROJECTS_DIR / "backburner"

# Emoji used in INDEX.md headers
STATUS_EMOJI = {
    'TODO': '📋',
    'IN_PROGRESS': '🚧',
    'BLOCKED': '🚫',
    'BACKBURNER': '⏸️',
    'COMPLETED': '✅',
    'CANCELLED': '❌',
}

# Reverse map (emoji -> status); handle multi-byte emoji
EMOJI_STATUS = {}
for status, emoji in STATUS_EMOJI.items():
    EMOJI_STATUS[emoji] = status


def read_file(path):
    with open(path, 'r') as f:
        return f.read()


def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)


def find_entry_bounds(content, project_name):
    """Find the start and end of a project entry in INDEX.md.

    Returns (start, end) character positions, or (None, None) if not found.
    The range includes the entry header through the trailing '---' separator.

    Matches the project name immediately after the status emoji, followed by
    either end-of-line or whitespace + trailing annotation text (e.g. a
    manager-appended "— READY TO COMPLETE" note). Requires the character right
    after the name to be whitespace/EOL (not e.g. '-') so a name that is a
    hyphenated prefix of another project's name (e.g. "fix-gps-hwversion" vs.
    "fix-gps-hwversion-detection") can never match the wrong heading.
    """
    pattern = re.compile(
        r'^### (?:' + '|'.join(re.escape(e) for e in STATUS_EMOJI.values()) + r') '
        + re.escape(project_name) + r'(?:\s.*)?$',
        re.MULTILINE
    )
    match = pattern.search(content)
    if not match:
        return None, None

    start = match.start()

    # Find the next project header or end-of-section marker after this entry
    next_header = re.compile(
        r'^### (?:' + '|'.join(re.escape(e) for e in STATUS_EMOJI.values()) + r') ',
        re.MULTILINE
    )
    rest = content[match.end():]
    next_match = next_header.search(rest)

    if next_match:
        # End is just before the next header
        end = match.end() + next_match.start()
    else:
        # No next header — find the next '---' or section marker
        section_marker = re.search(r'^\*\*Note:\*\*|^## Completed|^---\s*\n\s*\n(?:## |\*\*)', rest, re.MULTILINE)
        if section_marker:
            end = match.end() + section_marker.start()
        else:
            end = len(content)

    # Trim trailing whitespace/separators
    chunk = content[start:end]
    # Remove trailing '---' and blank lines
    chunk = re.sub(r'\n---\s*\n*$', '\n', chunk)

    return start, start + len(chunk)


def remove_entry_from_index(index_path, project_name):
    """Remove a project entry from an INDEX.md file. Returns the removed text."""
    content = read_file(index_path)
    start, end = find_entry_bounds(content, project_name)
    if start is None:
        return None

    removed = content[start:end]

    # Remove the entry and its trailing separator
    # Look for the --- separator after the entry
    after_entry = content[end:]
    after_entry = re.sub(r'^\s*---\s*\n?', '', after_entry, count=1)

    new_content = content[:start] + after_entry
    # Clean up double blank lines
    new_content = re.sub(r'\n{3,}', '\n\n', new_content)

    write_file(index_path, new_content)
    return removed


def count_active_index_entries(content):
    """Count active-INDEX entries by status, straight from raw '### <emoji>'
    occurrences. This is the single source of truth for counting — both
    update_index_counts() (which writes the header) and cmd_audit() (which
    verifies it) call this, so the two can never independently drift the way
    they used to (one counted raw heading occurrences, the other counted
    unique dict keys built from parsed heading text — which silently
    under-counted whenever two headings shared exactly the same text, or
    over/under-counted on any other parsing difference between the two).
    """
    active = 0
    backburner = 0
    blocked = 0
    for emoji, status in EMOJI_STATUS.items():
        count = len(re.findall(r'^### ' + re.escape(emoji) + r' ', content, re.MULTILINE))
        if status in ('TODO', 'IN_PROGRESS'):
            active += count
        elif status == 'BACKBURNER':
            backburner += count
        elif status == 'BLOCKED':
            blocked += count
    return active, backburner, blocked


def update_index_counts(index_path):
    """Recount projects by status and update the header counts."""
    content = read_file(index_path)

    if index_path == INDEX_PATH:
        active, backburner, blocked = count_active_index_entries(content)

        # Update the counts line
        content = re.sub(
            r'\*\*Active:\*\* \d+ \| \*\*Backburner:\*\* \d+ \| \*\*Blocked:\*\* \d+',
            f'**Active:** {active} | **Backburner:** {backburner} | **Blocked:** {blocked}',
            content
        )
        # Update date
        content = re.sub(
            r'\*\*Last Updated:\*\* \d{4}-\d{2}-\d{2}',
            f'**Last Updated:** {date.today().isoformat()}',
            content
        )

    elif index_path == COMPLETED_INDEX_PATH:
        completed = len(re.findall(r'^### ✅', content, re.MULTILINE))
        cancelled = len(re.findall(r'^### ❌', content, re.MULTILINE))
        content = re.sub(
            r'\*\*Total Completed:\*\* \d+',
            f'**Total Completed:** {completed}',
            content
        )
        content = re.sub(
            r'\*\*Total Cancelled:\*\* \d+',
            f'**Total Cancelled:** {cancelled}',
            content
        )

    write_file(index_path, content)


def add_entry_to_completed_index(project_name, summary_line, project_type=None,
                                  priority=None, pr_info=None):
    """Add a concise entry to completed/INDEX.md."""
    content = read_file(COMPLETED_INDEX_PATH)

    # Build the entry
    today = date.today().isoformat()
    entry = f"\n### ✅ {project_name}\n\n"
    entry += f"**Status:** COMPLETED ({today})\n"
    if project_type:
        entry += f"**Type:** {project_type}\n"
    if priority:
        entry += f"**Priority:** {priority}\n"
    entry += f"\n{summary_line}\n\n---\n"

    # Insert after the header (after the first '---' line)
    first_sep = content.find('\n---\n')
    if first_sep != -1:
        insert_pos = first_sep + 5  # after '---\n'
        content = content[:insert_pos] + '\n' + entry + content[insert_pos:]
    else:
        content += '\n' + entry

    write_file(COMPLETED_INDEX_PATH, content)


def add_cancelled_to_completed_index(project_name, reason):
    """Add a cancelled entry to completed/INDEX.md."""
    content = read_file(COMPLETED_INDEX_PATH)

    today = date.today().isoformat()
    entry = f"\n### ❌ {project_name} ({today})\n\n"
    entry += f"**Cancelled:** {reason}\n\n---\n"

    first_sep = content.find('\n---\n')
    if first_sep != -1:
        insert_pos = first_sep + 5
        content = content[:insert_pos] + '\n' + entry + content[insert_pos:]
    else:
        content += '\n' + entry

    write_file(COMPLETED_INDEX_PATH, content)


def extract_metadata_from_entry(entry_text):
    """Extract type, priority, and summary from an INDEX entry."""
    project_type = None
    priority = None
    summary = None

    type_match = re.search(r'\*\*Type:\*\* ([^|*\n]+)', entry_text)
    if type_match:
        project_type = type_match.group(1).strip()

    prio_match = re.search(r'\*\*Priority:\*\* ([^|*\n]+)', entry_text)
    if prio_match:
        priority = prio_match.group(1).strip()

    # Summary is the first non-metadata, non-blank line
    for line in entry_text.split('\n'):
        line = line.strip()
        if (line and not line.startswith('#') and not line.startswith('**')
                and not line.startswith('---') and not line.startswith('|')):
            summary = line
            break

    return project_type, priority, summary


def _extract_section_paragraph(content, heading_pattern):
    """Grab a full paragraph following a '## Heading' line, collapsed to one
    line. Stops at the next blank line or '##' heading, whichever comes
    first. Using re.DOTALL + a non-greedy stop condition (instead of the old
    `(.+)` with no DOTALL) is what prevents multi-line paragraphs from being
    silently cut off after their first line.
    """
    match = re.search(
        heading_pattern + r'\s*\n+(.+?)(?:\n\s*\n|\n##|\Z)',
        content, re.DOTALL
    )
    if not match:
        return None
    return ' '.join(match.group(1).split())


def extract_summary_from_dir(project_dir):
    """Try to extract a one-line summary from a project's summary.md."""
    summary_path = project_dir / "summary.md"
    if not summary_path.exists():
        return None, None, None

    content = read_file(summary_path)
    project_type = None
    priority = None
    summary = None

    type_match = re.search(r'\*\*Type:\*\* (.+)', content)
    if type_match:
        project_type = type_match.group(1).strip()

    prio_match = re.search(r'\*\*Priority:\*\* (.+)', content)
    if prio_match:
        priority = prio_match.group(1).strip()

    # Prefer an explicit Resolution/Outcome section — it describes what
    # actually happened. Falling back to Overview (which only describes the
    # original problem/intent) is why merged work used to read as abandoned.
    summary = _extract_section_paragraph(content, r'## (?:Resolution|Outcome)')
    if summary is None:
        overview = _extract_section_paragraph(content, r'## Overview')
        if overview is not None:
            summary = f"{overview} (see summary.md for resolution/PR details)"

    if summary is None:
        # Fall back to first non-header, non-metadata line
        for line in content.split('\n'):
            line = line.strip()
            if (line and not line.startswith('#') and not line.startswith('**')
                    and not line.startswith('---') and not line.startswith('-')):
                summary = line
                break

    return project_type, priority, summary


def find_raw_heading_line(content, project_name):
    """Loosely check whether project_name appears in some '###' heading line,
    even if the strict pattern in find_entry_bounds() didn't match it.

    Used to tell "genuinely not present" apart from "present but our regex
    missed it" so callers can fail loudly instead of guessing — this is what
    let the March/July incidents corrupt INDEX.md silently.

    Requires project_name to appear as a whole token (not preceded/followed
    by a word or hyphen character), so a name that is a hyphenated prefix or
    suffix of another project's name (e.g. "fix-gps-hwversion" vs.
    "fix-gps-hwversion-detection") can't produce a false match — otherwise
    completing the shorter project would misreport the longer project's
    unrelated heading as a malformed match for itself.
    """
    token_pattern = re.compile(r'(?<![\w-])' + re.escape(project_name) + r'(?![\w-])')
    for line in content.split('\n'):
        if line.startswith('### ') and token_pattern.search(line):
            return line
    return None


def find_project_dir(project_name):
    """Find which directory a project lives in. Returns (path, location_type) or (None, None)."""
    for dirname, loc_type in [(ACTIVE_DIR, 'active'), (BLOCKED_DIR, 'blocked'),
                               (BACKBURNER_DIR, 'backburner'), (COMPLETED_DIR, 'completed')]:
        candidate = dirname / project_name
        if candidate.is_dir():
            return candidate, loc_type
    return None, None


def is_master_project(project_dir):
    """A master project contains a milestones/ subdir (e.g. port-inav-rp2350)."""
    return (project_dir / "milestones").is_dir()


def check_not_milestone(project_name):
    """Print an error and return False if project_name is actually a milestone
    subdir of some master project; return True (nothing printed) otherwise.

    Shared by all lifecycle commands so the guard message can't drift out of
    sync between them the way the 5 copy-pasted inline versions could.
    """
    milestone_owner = find_milestone_owner(project_name)
    if milestone_owner:
        print(f"  ERROR: '{project_name}' is a milestone of master project "
              f"'{milestone_owner}', not a standalone project.")
        print(f"  Milestones are tracked within the master project's own files, "
              f"not via project_ops.py lifecycle commands.")
        return False
    return True


def find_milestone_owner(project_name):
    """If project_name is actually a milestone subdir of some master project,
    return that master project's name. Otherwise return None.

    Guards lifecycle commands against being pointed at a milestone name
    (e.g. "M3") and fabricating a bogus top-level INDEX/completed entry for
    it, since find_project_dir() only looks one level deep and would
    otherwise report "no directory found" while still proceeding.
    """
    for dirname in (ACTIVE_DIR, BLOCKED_DIR, BACKBURNER_DIR, COMPLETED_DIR):
        if not dirname.is_dir():
            continue
        for candidate in dirname.iterdir():
            if candidate.is_dir() and is_master_project(candidate):
                if (candidate / "milestones" / project_name).is_dir():
                    return candidate.name
    return None


def move_project_dir(project_name, from_dir, to_dir):
    """Move a project directory. Returns True on success."""
    src = from_dir / project_name
    dst = to_dir / project_name

    if not src.is_dir():
        print(f"  ERROR: Source directory not found: {src}")
        return False

    if dst.exists():
        print(f"  ERROR: Destination already exists: {dst}")
        print(f"  This is a duplicate — resolve manually.")
        return False

    to_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return True


def update_directory_reference(index_path, project_name, new_location):
    """Update the Directory: reference in the specific project's INDEX entry only.

    Returns True if a matching entry was found and updated, False otherwise —
    callers must check this rather than assume success, since a silent no-op
    here is the same failure class as issues #5/#6 (directory moves, INDEX.md
    quietly doesn't).
    """
    content = read_file(index_path)
    start, end = find_entry_bounds(content, project_name)
    if start is None:
        return False
    entry = content[start:end]
    entry = re.sub(
        r'(\*\*(?:Directory|Project Directory|Location):\*\* `)([^`]+)(`)',
        lambda m: m.group(1) + new_location + m.group(3),
        entry
    )
    content = content[:start] + entry + content[end:]
    write_file(index_path, content)
    return True


def update_entry_status(index_path, project_name, new_emoji, new_status_text):
    """Update the status emoji and text in an INDEX entry header.

    Returns True if a matching entry's heading was found and updated, False
    otherwise. Callers must check this — writing the file back unconditionally
    regardless of whether the substitution actually matched anything is what
    let 'block'/'backburner'/'resume' silently leave INDEX.md unchanged after
    moving a project's directory (same failure class as issues #5/#6).
    """
    content = read_file(index_path)

    # Update the header line emoji (same trailing-annotation tolerance as find_entry_bounds)
    old_pattern = re.compile(
        r'^(### )(?:' + '|'.join(re.escape(e) for e in STATUS_EMOJI.values()) + r')( '
        + re.escape(project_name) + r')(?=\s|$)',
        re.MULTILINE
    )
    content, n = old_pattern.subn(f'\\g<1>{new_emoji}\\g<2>', content)
    if n == 0:
        return False

    # Update Status field
    start, end = find_entry_bounds(content, project_name)
    if start is not None:
        entry = content[start:end]
        entry = re.sub(
            r'(\*\*Status:\*\* )[^|*\n]+',
            f'\\g<1>{new_status_text}',
            entry, count=1
        )
        content = content[:start] + entry + content[end:]

    write_file(index_path, content)
    return True


def report_missing_index_entry(content, project_name, action="updated"):
    """Print a diagnostic for a failed INDEX.md entry match, distinguishing a
    genuinely absent entry from one present but unmatched by our patterns —
    the ambiguity that let stale/inconsistent entries silently survive past
    lifecycle operations (issues #5/#6). Always returns False so callers can
    write `return report_missing_index_entry(...)`.
    """
    stray_line = find_raw_heading_line(content, project_name)
    if stray_line:
        print(f"  ERROR: '{project_name}' appears in an INDEX.md heading but it did not "
              f"match the expected format — refusing to guess whether it was {action}.")
        print(f"  Heading found: {stray_line.strip()!r}")
        print(f"  Fix the heading manually and re-run.")
    else:
        print(f"  ERROR: '{project_name}' has no matching heading in INDEX.md — nothing was {action}.")
    return False


def build_active_entry_block(project_name, project_type, priority, summary, assignee):
    """Build a correctly-formatted active-INDEX entry (TODO status), ending in '---'."""
    today = date.today().isoformat()
    return (
        f"### {STATUS_EMOJI['TODO']} {project_name}\n\n"
        f"**Status:** TODO | **Type:** {project_type} | **Priority:** {priority}\n"
        f"**Created:** {today} | **Assignee:** {assignee}\n\n"
        f"{summary}\n\n"
        f"**Directory:** `active/{project_name}/`\n\n"
        f"---\n"
    )


def insert_active_entry(entry_block):
    """Insert a new entry right after the '## Active Projects' heading so the
    newest project sits at the top of the active section. Reads and writes
    INDEX.md here so callers never load the whole file into context."""
    content = read_file(INDEX_PATH)
    heading = re.search(r'## Active Projects\n', content)
    if heading:
        after = heading.end()
        first = re.search(r'^### ', content[after:], re.MULTILINE)
        pos = after + first.start() if first else len(content)
    else:
        pos = len(content)
    content = content[:pos] + entry_block.rstrip('\n') + "\n\n" + content[pos:]
    write_file(INDEX_PATH, content)


def build_summary_md(project_name, title, project_type, priority, summary, notes, effort):
    """Generate a summary.md skeleton matching the manager project template."""
    today = date.today().isoformat()
    lines = [
        f"# Project: {title}",
        "",
        f"**Status:** 📋 TODO",
        f"**Priority:** {priority}",
        f"**Type:** {project_type}",
        f"**Created:** {today}",
        f"**Estimated Effort:** {effort}",
        "",
        "## Overview",
        "",
        summary,
        "",
    ]
    if notes:
        lines += ["## Notes", ""]
        for n in notes:
            lines.append(f"- {n}")
        lines.append("")
    return "\n".join(lines)


def build_todo_md(title):
    """Generate a minimal todo.md skeleton."""
    return (
        f"# Todo: {title}\n\n"
        f"## Phase 1\n\n"
        f"- [ ] \n\n"
        f"## Completion\n\n"
        f"- [ ] Completion report to manager\n"
    )


# ============================================================
# Commands
# ============================================================

def cmd_complete(project_name):
    """Complete a project: move dir, remove from INDEX, add to completed/INDEX."""
    print(f"\nCompleting project: {project_name}")
    success = True

    if not check_not_milestone(project_name):
        return False

    # 1. Find the project directory
    proj_dir, loc_type = find_project_dir(project_name)
    if proj_dir is None:
        print(f"  WARNING: No directory found for '{project_name}'")
    elif loc_type == 'completed':
        print(f"  Directory already in completed/")
    else:
        # Move to completed
        print(f"  Moving directory: {loc_type}/ -> completed/")
        if not move_project_dir(project_name, proj_dir.parent, COMPLETED_DIR):
            print("  ABORTED: Could not move directory.")
            return False

    # 2. Get metadata from INDEX entry before removing
    content = read_file(INDEX_PATH)
    start, end = find_entry_bounds(content, project_name)
    if start is not None:
        entry_text = content[start:end]
        project_type, priority, summary = extract_metadata_from_entry(entry_text)
    else:
        # Try from summary.md
        completed_path = COMPLETED_DIR / project_name
        if completed_path.is_dir():
            project_type, priority, summary = extract_summary_from_dir(completed_path)
        else:
            project_type, priority, summary = None, None, None

    # 3. Remove from active INDEX
    removed = remove_entry_from_index(INDEX_PATH, project_name)
    if removed:
        print(f"  Removed from INDEX.md")
    elif find_raw_heading_line(content, project_name):
        # Present but our pattern didn't match it — refuse to guess, unlike a
        # genuinely absent entry (which is a legitimate idempotent re-run).
        success = report_missing_index_entry(content, project_name, action="removed")
    else:
        print(f"  Not found in INDEX.md (nothing to remove)")

    # 4. Check if already in completed INDEX
    completed_content = read_file(COMPLETED_INDEX_PATH)
    if re.search(r'^### ✅ ' + re.escape(project_name), completed_content, re.MULTILINE):
        print(f"  Already in completed/INDEX.md")
    else:
        summary = summary or f"Completed project: {project_name}"
        add_entry_to_completed_index(project_name, summary, project_type, priority)
        print(f"  Added to completed/INDEX.md")

    # 5. Update counts
    update_index_counts(INDEX_PATH)
    update_index_counts(COMPLETED_INDEX_PATH)
    print(f"  Updated counts in both indexes")

    if success:
        print(f"  DONE")
    else:
        print(f"  DONE WITH ERRORS — see above")
    return success


def cmd_cancel(project_name, reason=None):
    """Cancel a project: move dir to completed, update indexes."""
    print(f"\nCancelling project: {project_name}")
    success = True

    if not check_not_milestone(project_name):
        return False

    reason = reason or "Cancelled"

    # 1. Find and move directory
    proj_dir, loc_type = find_project_dir(project_name)
    if proj_dir and loc_type != 'completed':
        print(f"  Moving directory: {loc_type}/ -> completed/")
        if not move_project_dir(project_name, proj_dir.parent, COMPLETED_DIR):
            print("  ABORTED: Could not move directory.")
            return False

    # 2. Remove from active INDEX
    content = read_file(INDEX_PATH)
    removed = remove_entry_from_index(INDEX_PATH, project_name)
    if removed:
        print(f"  Removed from INDEX.md")
    elif find_raw_heading_line(content, project_name):
        success = report_missing_index_entry(content, project_name, action="removed")
    else:
        print(f"  Not found in INDEX.md (nothing to remove)")

    # 3. Add to completed INDEX as cancelled
    completed_content = read_file(COMPLETED_INDEX_PATH)
    if re.search(r'^### ❌ ' + re.escape(project_name), completed_content, re.MULTILINE):
        print(f"  Already in completed/INDEX.md")
    else:
        add_cancelled_to_completed_index(project_name, reason)
        print(f"  Added to completed/INDEX.md as cancelled")

    # 4. Update counts
    update_index_counts(INDEX_PATH)
    update_index_counts(COMPLETED_INDEX_PATH)
    if success:
        print(f"  DONE")
    else:
        print(f"  DONE WITH ERRORS — see above")
    return success


def cmd_block(project_name, reason=None):
    """Block a project: move dir to blocked/, update INDEX status."""
    print(f"\nBlocking project: {project_name}")

    if not check_not_milestone(project_name):
        return False

    proj_dir, loc_type = find_project_dir(project_name)
    if proj_dir is None:
        print(f"  ERROR: No directory found for '{project_name}'")
        return False
    if loc_type == 'blocked':
        print(f"  Directory already in blocked/")
    elif loc_type in ('active', 'backburner'):
        print(f"  Moving directory: {loc_type}/ -> blocked/")
        if not move_project_dir(project_name, proj_dir.parent, BLOCKED_DIR):
            return False
    else:
        print(f"  ERROR: Cannot block from {loc_type}/")
        return False

    # Update INDEX entry
    if not update_entry_status(INDEX_PATH, project_name, STATUS_EMOJI['BLOCKED'], 'BLOCKED'):
        return report_missing_index_entry(read_file(INDEX_PATH), project_name, action="updated")
    update_directory_reference(INDEX_PATH, project_name, f'blocked/{project_name}/')

    if reason:
        # Add blocked since date and reason
        content = read_file(INDEX_PATH)
        start, end = find_entry_bounds(content, project_name)
        if start is not None:
            entry = content[start:end]
            today = date.today().isoformat()
            if '**Blocked Since:**' not in entry:
                # Add after Created line
                entry = re.sub(
                    r'(\*\*Created:\*\* [^\n]+)',
                    f'\\g<1>\n**Blocked Since:** {today}',
                    entry, count=1
                )
            if '**Blocking Issue:**' not in entry:
                entry += f"\n**Blocking Issue:** {reason}\n"
            content = content[:start] + entry + content[end:]
            write_file(INDEX_PATH, content)

    update_index_counts(INDEX_PATH)
    print(f"  DONE")
    return True


def cmd_backburner(project_name):
    """Move a project to backburner."""
    print(f"\nMoving to backburner: {project_name}")

    if not check_not_milestone(project_name):
        return False

    proj_dir, loc_type = find_project_dir(project_name)
    if proj_dir is None:
        print(f"  ERROR: No directory found for '{project_name}'")
        return False
    if loc_type == 'backburner':
        print(f"  Directory already in backburner/")
    elif loc_type in ('active', 'blocked'):
        print(f"  Moving directory: {loc_type}/ -> backburner/")
        if not move_project_dir(project_name, proj_dir.parent, BACKBURNER_DIR):
            return False
    else:
        print(f"  ERROR: Cannot backburner from {loc_type}/")
        return False

    if not update_entry_status(INDEX_PATH, project_name, STATUS_EMOJI['BACKBURNER'], 'BACKBURNER'):
        return report_missing_index_entry(read_file(INDEX_PATH), project_name, action="updated")
    update_directory_reference(INDEX_PATH, project_name, f'backburner/{project_name}/')
    update_index_counts(INDEX_PATH)
    print(f"  DONE")
    return True


def cmd_resume(project_name):
    """Resume a project from blocked or backburner back to active."""
    print(f"\nResuming project: {project_name}")

    if not check_not_milestone(project_name):
        return False

    proj_dir, loc_type = find_project_dir(project_name)
    if proj_dir is None:
        print(f"  ERROR: No directory found for '{project_name}'")
        return False
    if loc_type == 'active':
        print(f"  Directory already in active/")
    elif loc_type in ('blocked', 'backburner'):
        print(f"  Moving directory: {loc_type}/ -> active/")
        if not move_project_dir(project_name, proj_dir.parent, ACTIVE_DIR):
            return False
    else:
        print(f"  ERROR: Cannot resume from {loc_type}/")
        return False

    if not update_entry_status(INDEX_PATH, project_name, STATUS_EMOJI['IN_PROGRESS'], 'IN PROGRESS'):
        return report_missing_index_entry(read_file(INDEX_PATH), project_name, action="updated")
    update_directory_reference(INDEX_PATH, project_name, f'active/{project_name}/')
    update_index_counts(INDEX_PATH)
    print(f"  DONE")
    return True


def cmd_create(args):
    """Create a new active project: directory + summary.md/todo.md + INDEX entry.

    Usage: create <project-name> [--title T] [--type T] [--priority P]
           [--summary S] [--assignee A] [--effort E] [--note N ...]

    All file reads/writes (including locating the INDEX.md insertion point) happen
    here so the calling agent never loads INDEX.md into context, and the entry is
    generated with the exact format the other lifecycle commands parse.
    """
    if not args:
        print("Usage: project_ops.py create <project-name> [--title T] [--type T] "
              "[--priority P] [--summary S] [--assignee A] [--effort E] [--note N ...]")
        return False

    project_name = args[0]
    title = None
    ptype = 'Task'
    priority = 'MEDIUM'
    summary = None
    assignee = '📝 Planned'
    effort = 'TBD'
    notes = []

    i = 1
    while i < len(args):
        a = args[i]
        if a in ('--title', '--type', '--priority', '--summary', '--assignee', '--effort', '--note') and i + 1 < len(args):
            v = args[i + 1]
            if a == '--title':
                title = v
            elif a == '--type':
                ptype = v
            elif a == '--priority':
                priority = v.upper()
            elif a == '--summary':
                summary = v
            elif a == '--assignee':
                assignee = v
            elif a == '--effort':
                effort = v
            elif a == '--note':
                notes.append(v)
            i += 2
        else:
            print(f"  Unknown or incomplete flag: {a}")
            return False

    title = title or project_name.replace('-', ' ').title()
    summary = summary or project_name.replace('-', ' ')

    # Slug must be lowercase kebab-case so the regex matching used by every
    # other command stays unambiguous.
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', project_name):
        print(f"  ERROR: project name must be lowercase kebab-case (got {project_name!r})")
        return False

    existing_dir, _ = find_project_dir(project_name)
    if existing_dir is not None:
        print(f"  ERROR: a project directory already exists for '{project_name}'")
        return False
    content = read_file(INDEX_PATH)
    if find_raw_heading_line(content, project_name) or find_entry_bounds(content, project_name)[0] is not None:
        print(f"  ERROR: '{project_name}' already has an entry in INDEX.md")
        return False

    print(f"\nCreating project: {project_name}")

    proj_dir = ACTIVE_DIR / project_name
    proj_dir.mkdir(parents=True, exist_ok=False)
    write_file(proj_dir / "summary.md", build_summary_md(project_name, title, ptype, priority, summary, notes, effort))
    write_file(proj_dir / "todo.md", build_todo_md(title))
    print(f"  Created active/{project_name}/summary.md + todo.md")

    insert_active_entry(build_active_entry_block(project_name, ptype, priority, summary, assignee))
    print(f"  Added entry to INDEX.md")

    update_index_counts(INDEX_PATH)
    print(f"  Updated counts")
    print(f"  DONE")
    return True


def cmd_audit(fix=False, dry_run=False, force=False):
    """Check for inconsistencies between directories and indexes.

    fix:      apply automatic fixes where safe
    dry_run:  print what --fix would do without changing anything (implies fix)
    force:    also allow the one auto-fix that is destructive (deleting a
              stale active/blocked/backburner copy when a completed/ copy
              already exists) — without --force that case is only reported
    """
    if dry_run:
        fix = True
    print("\n=== Project Audit ===\n")
    if dry_run:
        print("(DRY RUN — no changes will be made)\n")
    issues = []

    # Parse active INDEX
    index_content = read_file(INDEX_PATH)
    index_projects = {}
    for match in re.finditer(
        r'^### (' + '|'.join(re.escape(e) for e in STATUS_EMOJI.values()) + r') (.+?)\s*$',
        index_content, re.MULTILINE
    ):
        emoji = match.group(1)
        name = match.group(2)
        status = EMOJI_STATUS.get(emoji, 'UNKNOWN')
        index_projects[name] = status

    # Parse completed INDEX
    completed_content = read_file(COMPLETED_INDEX_PATH)
    completed_indexed = set()
    for match in re.finditer(r'^### [✅❌] (.+?)(?:\s*\(.*\))?\s*$', completed_content, re.MULTILINE):
        completed_indexed.add(match.group(1))

    # Scan directories
    dir_locations = {}  # project_name -> set of locations
    for dirname, loc_type in [(ACTIVE_DIR, 'active'), (BLOCKED_DIR, 'blocked'),
                               (BACKBURNER_DIR, 'backburner'), (COMPLETED_DIR, 'completed')]:
        if dirname.is_dir():
            for d in dirname.iterdir():
                if d.is_dir() and d.name != '__pycache__':
                    dir_locations.setdefault(d.name, set()).add(loc_type)

    # Check 1: Projects in multiple directories (duplicates)
    duplicates = {name: locs for name, locs in dir_locations.items() if len(locs) > 1}
    if duplicates:
        print(f"DUPLICATES: {len(duplicates)} projects exist in multiple directories")
        for name, locs in sorted(duplicates.items()):
            print(f"  {name}: {', '.join(sorted(locs))}")
            if fix and 'completed' in locs:
                for loc in locs - {'completed'}:
                    loc_dir = {'active': ACTIVE_DIR, 'blocked': BLOCKED_DIR,
                               'backburner': BACKBURNER_DIR}[loc]
                    stale_dir = loc_dir / name
                    if not force:
                        print(f"    WARNING: '{name}' exists in both {loc}/ and completed/ — "
                              f"NOT auto-deleting the {loc}/ copy (it may be live work, as "
                              f"'feature-frskyf405-target' was). Resolve manually, or re-run "
                              f"audit --fix --force to delete the {loc}/ copy.")
                    elif dry_run:
                        print(f"    [DRY RUN] Would remove stale {loc}/{name}/ (completed copy exists) [--force]")
                    else:
                        print(f"    FIX: Removing stale {loc}/{name}/ (completed copy exists) [--force]")
                        shutil.rmtree(str(stale_dir))
        issues.append(('DUPLICATES', len(duplicates)))
    else:
        print("DUPLICATES: None found")

    # Check 2: Active INDEX entries pointing to completed projects
    completed_in_index = []
    for name, status in index_projects.items():
        if name in dir_locations and 'completed' in dir_locations[name]:
            if 'active' not in dir_locations.get(name, set()) and \
               'blocked' not in dir_locations.get(name, set()) and \
               'backburner' not in dir_locations.get(name, set()):
                completed_in_index.append(name)
    if completed_in_index:
        print(f"\nCOMPLETED IN ACTIVE INDEX: {len(completed_in_index)} entries should be removed")
        for name in sorted(completed_in_index):
            print(f"  {name}")
            if fix:
                if dry_run:
                    print(f"    [DRY RUN] Would remove from INDEX.md")
                else:
                    removed = remove_entry_from_index(INDEX_PATH, name)
                    if removed:
                        print(f"    FIX: Removed from INDEX.md")
        issues.append(('COMPLETED_IN_INDEX', len(completed_in_index)))
    else:
        print("\nCOMPLETED IN ACTIVE INDEX: None found")

    # Check 3: INDEX entries with no directory anywhere
    orphan_entries = []
    for name in index_projects:
        if name not in dir_locations:
            orphan_entries.append(name)
    if orphan_entries:
        print(f"\nORPHAN INDEX ENTRIES: {len(orphan_entries)} entries have no directory")
        for name in sorted(orphan_entries):
            status = index_projects[name]
            print(f"  {name} (status: {status})")
            if fix:
                expected_dir = ACTIVE_DIR / name
                if status == 'BLOCKED':
                    expected_dir = BLOCKED_DIR / name
                elif status == 'BACKBURNER':
                    expected_dir = BACKBURNER_DIR / name
                if dry_run:
                    print(f"    [DRY RUN] Would create {expected_dir.relative_to(PROJECTS_DIR)}/")
                else:
                    expected_dir.mkdir(parents=True, exist_ok=True)
                    print(f"    FIX: Created {expected_dir.relative_to(PROJECTS_DIR)}/")
        issues.append(('ORPHAN_ENTRIES', len(orphan_entries)))
    else:
        print("\nORPHAN INDEX ENTRIES: None found")

    # Check 4: Status/location mismatches
    status_dir_map = {
        'TODO': 'active', 'IN_PROGRESS': 'active',
        'BLOCKED': 'blocked', 'BACKBURNER': 'backburner'
    }
    mismatches = []
    for name, status in index_projects.items():
        expected_loc = status_dir_map.get(status)
        if expected_loc and name in dir_locations:
            actual_locs = dir_locations[name]
            if expected_loc not in actual_locs and len(actual_locs) == 1:
                actual = next(iter(actual_locs))
                if actual != 'completed':  # completed is handled separately
                    mismatches.append((name, status, expected_loc, actual))
    if mismatches:
        print(f"\nSTATUS/LOCATION MISMATCHES: {len(mismatches)} projects in wrong directory")
        for name, status, expected, actual in mismatches:
            print(f"  {name}: status={status} -> expected {expected}/, found in {actual}/")
            if fix:
                from_dir = {'active': ACTIVE_DIR, 'blocked': BLOCKED_DIR,
                            'backburner': BACKBURNER_DIR}[actual]
                to_dir = {'active': ACTIVE_DIR, 'blocked': BLOCKED_DIR,
                          'backburner': BACKBURNER_DIR}[expected]
                if dry_run:
                    print(f"    [DRY RUN] Would move {actual}/{name}/ -> {expected}/{name}/")
                elif move_project_dir(name, from_dir, to_dir):
                    update_directory_reference(INDEX_PATH, name, f'{expected}/{name}/')
                    print(f"    FIX: Moved {actual}/{name}/ -> {expected}/{name}/")
        issues.append(('MISMATCHES', len(mismatches)))
    else:
        print("\nSTATUS/LOCATION MISMATCHES: None found")

    # Check 5: Completed directories missing from completed/INDEX.md
    missing_completed = []
    for name in sorted(dir_locations):
        if 'completed' in dir_locations[name] and name not in completed_indexed:
            missing_completed.append(name)
    if missing_completed:
        print(f"\nMISSING FROM COMPLETED INDEX: {len(missing_completed)} directories not indexed")
        for name in missing_completed:
            print(f"  {name}")
            if fix:
                if dry_run:
                    print(f"    [DRY RUN] Would add to completed/INDEX.md")
                else:
                    proj_dir = COMPLETED_DIR / name
                    project_type, priority, summary = extract_summary_from_dir(proj_dir)
                    summary = summary or f"Completed project: {name}"
                    add_entry_to_completed_index(name, summary, project_type, priority)
                    print(f"    FIX: Added to completed/INDEX.md")
        issues.append(('MISSING_COMPLETED', len(missing_completed)))
    else:
        print("\nMISSING FROM COMPLETED INDEX: None found")

    # Check 6: Verify INDEX.md counts match reality
    # Uses count_active_index_entries() — the same function update_index_counts()
    # uses to WRITE the header — so verification can never diverge from the
    # writer's own counting logic (the old code re-derived counts from a
    # dict keyed by parsed heading text, a second code path that could
    # silently disagree with the writer, e.g. by collapsing two identical
    # heading strings into one dict entry).
    print(f"\nCOUNT VERIFICATION:")
    active_count, backburner_count, blocked_count = count_active_index_entries(index_content)

    count_match = re.search(
        r'\*\*Active:\*\* (\d+) \| \*\*Backburner:\*\* (\d+) \| \*\*Blocked:\*\* (\d+)',
        index_content
    )
    if count_match:
        stated_active = int(count_match.group(1))
        stated_backburner = int(count_match.group(2))
        stated_blocked = int(count_match.group(3))

        if (stated_active, stated_backburner, stated_blocked) == (active_count, backburner_count, blocked_count):
            print(f"  INDEX.md counts correct: Active={active_count}, Backburner={backburner_count}, Blocked={blocked_count}")
        else:
            print(f"  INDEX.md counts WRONG:")
            print(f"    Stated:  Active={stated_active}, Backburner={stated_backburner}, Blocked={stated_blocked}")
            print(f"    Actual:  Active={active_count}, Backburner={backburner_count}, Blocked={blocked_count}")
            if fix:
                if dry_run:
                    print(f"    [DRY RUN] Would update counts")
                else:
                    update_index_counts(INDEX_PATH)
                    print(f"    FIX: Updated counts")
            issues.append(('WRONG_COUNTS', 1))
    else:
        print(f"  Could not find counts in INDEX.md header (unparseable/missing — cannot verify)")
        issues.append(('UNPARSEABLE_COUNTS', 1))

    # Summary
    print(f"\n{'='*50}")
    if issues:
        total = sum(count for _, count in issues)
        print(f"TOTAL ISSUES: {total}")
        if dry_run:
            print(f"DRY RUN — no changes were made. Re-run without --dry-run to apply.")
        elif fix:
            print(f"Applied automatic fixes where possible.")
        else:
            print(f"Run with --fix to auto-fix simple issues.")
    else:
        print("ALL CLEAN - no inconsistencies found")

    return len(issues) == 0


def cmd_unsent():
    """List active projects (TODO/IN_PROGRESS) that have not been sent to the developer."""
    content = read_file(INDEX_PATH)

    # Parse active entries -> name + assignee
    active = {}
    for e in re.split(r'\n### ', content):
        m = re.match(r'(📋|🚧)\s+([^\n]+)', e)
        if not m:
            continue
        name = m.group(2).strip()
        am = re.search(r'\*\*Assignee:\*\*\s*([^\n]+)', e)
        asm = re.search(r'\*\*Assignment:\*\*\s*([^\n]+)', e)
        a = am.group(1).strip() if am else (asm.group(1).strip() if asm else '')
        active[name] = a

    # Projects explicitly referenced in sent task-assignment emails
    sent_names = set()
    sent_dir = REPO_ROOT / "claude" / "manager" / "email" / "sent"
    if sent_dir.is_dir():
        for f in sorted(sent_dir.glob("*-task-*.md")):
            txt = f.read_text(errors="replace")
            for m in re.finditer(r'\*\*(?:Directory|Project):\*\*\s*(.+)', txt):
                v = m.group(1).strip().strip('`').strip()
                dm = re.search(r'([a-z0-9][a-z0-9-]*)/?$', v)
                if dm and '-' in dm.group(1):
                    sent_names.add(dm.group(1))
                elif re.fullmatch(r'[a-z0-9][a-z0-9-]*', v) and '-' in v:
                    sent_names.add(v)

    unsent, manager_owned = [], []
    for name in sorted(active):
        a = active[name]
        al = a.lower()
        if al.startswith('manager'):
            manager_owned.append((name, a))
        elif name in sent_names:
            continue
        elif ('planned' in al) or ('unassigned' in al) or (a.strip() == ''):
            unsent.append((name, a))

    print(f"\nUnsent active projects ({len(unsent)}):")
    for name, a in unsent:
        print(f"  - {name}   [{a or 'no assignee'}]")
    if manager_owned:
        print(f"\nManager-owned / not a developer task ({len(manager_owned)}):")
        for name, a in manager_owned:
            print(f"  - {name}   [{a or 'no assignee'}]")
    print()


HELP_TEXT = """Project Operations - atomic project lifecycle operations.

Usage:
  project_ops.py create <project> [flags]    Create new project (dir + files + INDEX entry)
  project_ops.py complete <project>          Move project to completed (dir + both indexes)
  project_ops.py cancel <project> [reason]   Cancel project (to completed as cancelled)
  project_ops.py block <project> [reason]    Block project (active -> blocked)
  project_ops.py backburner <project>        Backburner project (active -> backburner)
  project_ops.py resume <project>            Resume blocked/backburner -> active
  project_ops.py audit [--fix] [--dry-run] [--force]   Check/fix index-dir consistency
  project_ops.py unsent                               List active projects not sent to the developer

Options:
  -h, --help   Show this help and exit
"""


def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        print(HELP_TEXT)
        sys.exit(0)

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == 'help':
        print(HELP_TEXT)
        sys.exit(0)

    if command == 'complete':
        if len(sys.argv) < 3:
            print("Usage: project_ops.py complete <project-name>")
            sys.exit(1)
        if not cmd_complete(sys.argv[2]):
            sys.exit(1)

    elif command == 'cancel':
        if len(sys.argv) < 3:
            print("Usage: project_ops.py cancel <project-name> [reason]")
            sys.exit(1)
        reason = ' '.join(sys.argv[3:]) if len(sys.argv) > 3 else None
        if not cmd_cancel(sys.argv[2], reason):
            sys.exit(1)

    elif command == 'block':
        if len(sys.argv) < 3:
            print("Usage: project_ops.py block <project-name> [reason]")
            sys.exit(1)
        reason = ' '.join(sys.argv[3:]) if len(sys.argv) > 3 else None
        if not cmd_block(sys.argv[2], reason):
            sys.exit(1)

    elif command == 'backburner':
        if len(sys.argv) < 3:
            print("Usage: project_ops.py backburner <project-name>")
            sys.exit(1)
        if not cmd_backburner(sys.argv[2]):
            sys.exit(1)

    elif command == 'resume':
        if len(sys.argv) < 3:
            print("Usage: project_ops.py resume <project-name>")
            sys.exit(1)
        if not cmd_resume(sys.argv[2]):
            sys.exit(1)

    elif command == 'audit':
        fix = '--fix' in sys.argv
        dry_run = '--dry-run' in sys.argv
        force = '--force' in sys.argv
        if not cmd_audit(fix=fix, dry_run=dry_run, force=force):
            sys.exit(1)

    elif command == 'create':
        if not cmd_create(sys.argv[2:]):
            sys.exit(1)

    elif command == 'unsent':
        cmd_unsent()

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
