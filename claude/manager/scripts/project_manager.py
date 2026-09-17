#!/usr/bin/env python3
"""
Project Manager - Query and manage INAV projects

This script helps manage the project index by:
- Listing projects by status
- Filtering projects by creation-date range
- Showing project details
- Generating compact summaries
- Querying by various criteria

Every command writes its output to a file (in addition to stdout) so results
can be copy-pasted without fighting the terminal's files-changed sidebar.
Default output path is /tmp/claude/project-manager-<command>.txt; override
with --output/-o.
"""

import argparse
import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, date

@dataclass
class Project:
    """Represents a project from INDEX.md"""
    name: str
    status: str  # TODO, IN_PROGRESS, COMPLETE, BACKBURNER, BLOCKED, CANCELLED
    emoji: str
    priority: Optional[str] = None
    assignee: Optional[str] = None
    created: Optional[str] = None
    completed: Optional[str] = None
    location: Optional[str] = None
    line_start: int = 0
    line_end: int = 0

    @property
    def is_active(self):
        return self.status in ('TODO', 'IN_PROGRESS', 'BACKBURNER', 'BLOCKED')

    @property
    def is_completed(self):
        return self.status in ('COMPLETE', 'CANCELLED')

    @property
    def created_date(self) -> Optional[date]:
        """Parse the Created field's leading YYYY-MM-DD, ignoring any trailing text."""
        if not self.created:
            return None
        match = re.match(r'(\d{4}-\d{2}-\d{2})', self.created)
        if not match:
            return None
        try:
            return datetime.strptime(match.group(1), '%Y-%m-%d').date()
        except ValueError:
            return None


STATUS_MAP = {
    '📋': 'TODO',
    '🚧': 'IN_PROGRESS',
    '✅': 'COMPLETE',
    '⏸️': 'BACKBURNER',
    '🚫': 'BLOCKED',
    '❌': 'CANCELLED',
}


def parse_index(index_path: Path) -> List[Project]:
    """Parse INDEX.md and extract all projects"""
    projects = []
    current_project = None

    with open(index_path) as f:
        lines = f.readlines()

    # Alternation, not a character class: some status emoji (e.g. ⏸️) are
    # multiple Unicode codepoints, which a [...] class would split apart and
    # fail to match as a unit.
    emoji_alt = '|'.join(re.escape(e) for e in STATUS_MAP.keys())
    header_re = re.compile(rf'^### ({emoji_alt}) (.+)$')

    for i, line in enumerate(lines, 1):
        match = header_re.match(line)
        if match:
            # Save previous project
            if current_project:
                current_project.line_end = i - 1
                projects.append(current_project)

            # Start new project
            emoji = match.group(1)
            name = match.group(2)

            current_project = Project(
                name=name,
                status=STATUS_MAP.get(emoji, 'UNKNOWN'),
                emoji=emoji,
                line_start=i
            )

        # Extract metadata. Fields are often packed multiple-per-line,
        # pipe-separated (e.g. "**Status:** ... | **Priority:** MEDIUM | ..."),
        # so scan the whole line rather than anchoring at line start.
        elif current_project:
            for m in re.finditer(r'\*\*([A-Za-z ]+):\*\*\s*([^|]*)', line):
                field = m.group(1).strip()
                value = m.group(2).strip()
                if field == 'Priority':
                    current_project.priority = value
                elif field == 'Assignee':
                    current_project.assignee = value
                elif field == 'Created':
                    current_project.created = value
                elif field == 'Completed':
                    current_project.completed = value
                elif field in ('Directory', 'Location'):
                    current_project.location = value.strip('`')

    # Add last project
    if current_project:
        current_project.line_end = len(lines)
        projects.append(current_project)

    return projects


def parse_date_arg(value: str) -> date:
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date '{value}', expected YYYY-MM-DD")


class Output:
    """Collects lines and emits them to stdout and a file."""

    def __init__(self):
        self.lines: List[str] = []

    def print(self, text: str = ""):
        print(text)
        self.lines.append(text)

    def write_to(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.write('\n'.join(self.lines) + '\n')
        print(f"\n(output also written to {path})")


def list_projects(out: Output, projects: List[Project], status: Optional[str] = None,
                   since: Optional[date] = None, until: Optional[date] = None):
    """List projects, optionally filtered by status and/or Created date range"""
    filtered = projects
    if status:
        filtered = [p for p in filtered if p.status == status]
    if since:
        filtered = [p for p in filtered if p.created_date and p.created_date >= since]
    if until:
        filtered = [p for p in filtered if p.created_date and p.created_date <= until]

    filtered = sorted(filtered, key=lambda p: p.created_date or date.min, reverse=True)

    out.print(f"\n{'Status':<15} {'Priority':<10} {'Project':<50} {'Created':<12}")
    out.print("=" * 100)

    for p in filtered:
        priority = p.priority or 'N/A'
        created = p.created or 'N/A'
        out.print(f"{p.emoji} {p.status:<12} {priority:<10} {p.name:<50} {created:<12}")

    out.print(f"\nTotal: {len(filtered)} projects")


def show_details(out: Output, projects: List[Project], name: str):
    """Show full details for a specific project"""
    matches = [p for p in projects if name.lower() in p.name.lower()]

    if not matches:
        out.print(f"No project found matching '{name}'")
        return

    if len(matches) > 1:
        out.print(f"Multiple matches found for '{name}':")
        for p in matches:
            out.print(f"  - {p.name}")
        return

    p = matches[0]
    out.print(f"\n{p.emoji} {p.name}")
    out.print("=" * 80)
    out.print(f"Status:    {p.status}")
    out.print(f"Priority:  {p.priority or 'N/A'}")
    out.print(f"Assignee:  {p.assignee or 'N/A'}")
    out.print(f"Created:   {p.created or 'N/A'}")
    out.print(f"Completed: {p.completed or 'N/A'}")
    out.print(f"Location:  {p.location or 'N/A'}")
    out.print(f"Lines:     {p.line_start}-{p.line_end} ({p.line_end - p.line_start + 1} lines)")


def stats(out: Output, projects: List[Project]):
    """Show project statistics"""
    by_status = {}
    for p in projects:
        by_status[p.status] = by_status.get(p.status, 0) + 1

    by_priority = {}
    for p in projects:
        if p.priority:
            by_priority[p.priority] = by_priority.get(p.priority, 0) + 1

    out.print("\n=== Project Statistics ===\n")

    out.print("By Status:")
    for status, count in sorted(by_status.items()):
        out.print(f"  {status:<15} {count:>3} projects")

    out.print(f"\nTotal Projects: {len(projects)}")
    out.print(f"Active Projects: {sum(1 for p in projects if p.is_active)}")
    out.print(f"Completed: {sum(1 for p in projects if p.is_completed)}")

    if by_priority:
        out.print("\nBy Priority:")
        for priority, count in sorted(by_priority.items()):
            out.print(f"  {priority:<15} {count:>3} projects")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Query claude/projects/INDEX.md",
        epilog="Status options: TODO, IN_PROGRESS, COMPLETE, BACKBURNER, BLOCKED, CANCELLED",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List projects, optionally filtered")
    p_list.add_argument("status", nargs="?", help="Filter by status (case-insensitive)")
    p_list.add_argument("--since", type=parse_date_arg, metavar="YYYY-MM-DD",
                         help="Only projects created on/after this date")
    p_list.add_argument("--until", type=parse_date_arg, metavar="YYYY-MM-DD",
                         help="Only projects created on/before this date")
    p_list.add_argument("--days", type=int, metavar="N",
                         help="Shortcut for --since <today minus N days>")
    p_list.add_argument("--output", "-o", metavar="PATH", help="Output file path")

    p_show = sub.add_parser("show", help="Show details for one project")
    p_show.add_argument("name", help="Project name or substring")
    p_show.add_argument("--output", "-o", metavar="PATH", help="Output file path")

    p_stats = sub.add_parser("stats", help="Show project statistics")
    p_stats.add_argument("--output", "-o", metavar="PATH", help="Output file path")

    return parser


def main():
    # Local project data lives in claude/projects/ (gitignored); this script is
    # framework tooling under claude/manager/scripts/.
    index_path = Path(__file__).resolve().parents[3] / "claude" / "projects" / "INDEX.md"

    if not index_path.exists():
        print(f"Error: INDEX.md not found at {index_path}")
        sys.exit(1)

    projects = parse_index(index_path)

    parser = build_parser()
    args = parser.parse_args()

    out = Output()
    default_output = Path(f"/tmp/claude/project-manager-{args.command}.txt")
    output_path = Path(args.output) if getattr(args, "output", None) else default_output

    if args.command == "list":
        status = args.status.upper() if args.status else None
        since = args.since
        if args.days is not None:
            from datetime import timedelta
            candidate = date.today() - timedelta(days=args.days)
            since = max(since, candidate) if since else candidate
        list_projects(out, projects, status, since, args.until)

    elif args.command == "show":
        show_details(out, projects, args.name)

    elif args.command == "stats":
        stats(out, projects)

    out.write_to(output_path)


if __name__ == "__main__":
    main()
