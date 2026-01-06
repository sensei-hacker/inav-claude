#!/usr/bin/env python3
"""
Bash command parser for Claude Code hooks.

Parses compound bash commands into individual subcommands,
extracting the command and arguments for each.
"""

import re
import shlex
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ParsedCommand:
    """Represents a parsed bash subcommand."""
    command: str
    arguments: str
    raw: str
    operator_before: Optional[str] = None  # The operator before this command (&&, ||, ;, |, etc.)


class BashCommandParser:
    """Parser for breaking down compound bash commands."""

    # Operators that separate commands
    COMMAND_SEPARATORS = [
        '&&',  # AND
        '||',  # OR
        ';;',  # Case statement terminator
        '|&',  # Pipe both stdout and stderr
        '&',   # Background (must come after |&)
        ';',   # Sequential
        '|',   # Pipe
        '\n',  # Newline
    ]

    def __init__(self):
        # Build regex pattern for splitting on operators
        # Escape special regex chars and sort by length (longest first)
        escaped_ops = [re.escape(op) for op in sorted(self.COMMAND_SEPARATORS, key=len, reverse=True)]
        self.separator_pattern = re.compile(f'({"|".join(escaped_ops)})')

    def parse(self, command: str) -> List[ParsedCommand]:
        """
        Parse a bash command into subcommands.

        Args:
            command: The full bash command string

        Returns:
            List of ParsedCommand objects
        """
        if not command or not command.strip():
            return []

        # Handle simple case: no operators
        if not self.separator_pattern.search(command):
            return self._parse_with_control_keywords(command, None)

        # Split by operators while preserving them, respecting quotes
        parts = self._split_respecting_quotes(command)

        parsed_commands = []
        current_operator = None

        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue

            # Check if this part is an operator
            if part in self.COMMAND_SEPARATORS:
                current_operator = part
            else:
                # This is a command - may contain control keywords to split
                split_cmds = self._parse_with_control_keywords(part, current_operator)
                parsed_commands.extend(split_cmds)
                current_operator = None

        return parsed_commands

    def _split_respecting_quotes(self, command: str) -> List[str]:
        """
        Split command by operators while respecting quoted strings, redirections, and parentheses.

        Args:
            command: The bash command string

        Returns:
            List of parts (commands and operators)
        """
        parts = []
        current_part = []
        in_single_quote = False
        in_double_quote = False
        paren_depth = 0  # Track parentheses nesting
        escaped = False
        i = 0

        while i < len(command):
            char = command[i]

            # Handle escape sequences
            if escaped:
                current_part.append(char)
                escaped = False
                i += 1
                continue

            if char == '\\':
                escaped = True
                current_part.append(char)
                i += 1
                continue

            # Handle quotes
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
                current_part.append(char)
                i += 1
                continue

            if char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
                current_part.append(char)
                i += 1
                continue

            # If we're inside quotes, just accumulate
            if in_single_quote or in_double_quote:
                current_part.append(char)
                i += 1
                continue

            # Track parentheses depth (when not in quotes)
            if char == '(':
                paren_depth += 1
                current_part.append(char)
                i += 1
                continue

            if char == ')':
                paren_depth -= 1
                current_part.append(char)
                i += 1
                continue

            # If we're inside parentheses, don't split
            if paren_depth > 0:
                current_part.append(char)
                i += 1
                continue

            # Check for redirections before operators
            # Patterns like: 2>&1, 1>&2, &>, 2>, 1>, >>, >&
            if self._is_redirection(command, i):
                # It's a redirection, not a separator - include it in current part
                current_part.append(char)
                i += 1
                continue

            # Check for operators (only when not in quotes or redirections)
            matched_op = None
            for op in sorted(self.COMMAND_SEPARATORS, key=len, reverse=True):
                if command[i:i+len(op)] == op:
                    matched_op = op
                    break

            if matched_op:
                # Save current part if not empty
                if current_part:
                    parts.append(''.join(current_part))
                    current_part = []
                # Save operator
                parts.append(matched_op)
                i += len(matched_op)
            else:
                current_part.append(char)
                i += 1

        # Add remaining part
        if current_part:
            parts.append(''.join(current_part))

        return parts

    def _is_redirection(self, command: str, pos: int) -> bool:
        """
        Check if the character at pos is part of a redirection operator.

        Common redirections: >, >>, <, <<, 2>, 2>>, 1>, &>, >&, 2>&1, 1>&2, etc.

        Args:
            command: Full command string
            pos: Current position in the string

        Returns:
            True if this is part of a redirection
        """
        char = command[pos]

        # Check for file descriptor number followed by redirection
        # e.g., 2>&1, 2>, 1>, etc.
        if char.isdigit():
            # Look ahead for > or <
            next_pos = pos + 1
            if next_pos < len(command) and command[next_pos] in '><':
                return True

        # Check for > or < followed by &, >, <, or digit
        # e.g., >&, >>, <<, >&1, etc.
        if char in '><':
            next_pos = pos + 1
            if next_pos < len(command) and command[next_pos] in '>&<0123456789':
                return True
            # Standalone > or < is also a redirection
            return True

        # Check for & that's part of a redirection (preceded by >)
        # e.g., >&1, >&2, &>
        if char == '&':
            # Look back for >
            if pos > 0 and command[pos - 1] == '>':
                return True
            # Look ahead for > (e.g., &>)
            next_pos = pos + 1
            if next_pos < len(command) and command[next_pos] == '>':
                return True

        return False

    def _parse_simple_command(self, cmd_str: str, operator: Optional[str]) -> ParsedCommand:
        """
        Parse a single simple command (no operators) into command and arguments.

        Args:
            cmd_str: Single command string
            operator: The operator that preceded this command

        Returns:
            ParsedCommand object
        """
        cmd_str = cmd_str.strip()

        # Handle special cases
        if cmd_str.startswith('for ') or cmd_str.startswith('while ') or cmd_str.startswith('if '):
            # Control structures - treat the whole thing as the command
            return ParsedCommand(
                command=cmd_str.split()[0],
                arguments=cmd_str[len(cmd_str.split()[0]):].strip(),
                raw=cmd_str,
                operator_before=operator
            )

        # Handle parentheses for subshells/command grouping
        # e.g., (make target) or (echo "test" && ls)
        # For permission checking, we just need the first command inside
        cmd_str_stripped = cmd_str.strip()
        if cmd_str_stripped.startswith('(') and cmd_str_stripped.endswith(')'):
            # Strip outer parentheses - the inner command will be parsed normally
            cmd_str = cmd_str_stripped[1:-1].strip()

        # Standalone control keywords (terminators that don't take commands)
        standalone_keywords = {'fi', 'done', 'esac'}
        first_word = cmd_str.split()[0] if cmd_str.split() else cmd_str
        if first_word in standalone_keywords:
            # These are standalone - return as-is
            return ParsedCommand(
                command=first_word,
                arguments='',
                raw=cmd_str,
                operator_before=operator
            )

        try:
            # Use shlex to split respecting quotes
            tokens = shlex.split(cmd_str)
        except ValueError:
            # Shlex can fail on malformed quotes, fall back to simple split
            tokens = cmd_str.split()

        if not tokens:
            return ParsedCommand(
                command='',
                arguments='',
                raw=cmd_str,
                operator_before=operator
            )

        # First token is the command
        command = tokens[0]
        # Rest are arguments
        arguments = ' '.join(tokens[1:]) if len(tokens) > 1 else ''

        return ParsedCommand(
            command=command,
            arguments=arguments,
            raw=cmd_str,
            operator_before=operator
        )

    def _parse_with_control_keywords(self, cmd_str: str, operator: Optional[str]) -> List[ParsedCommand]:
        """
        Parse a command that may start with a control keyword followed by another command.

        Handles cases like "do sleep 1" -> [ParsedCommand("do"), ParsedCommand("sleep", "1")]

        Args:
            cmd_str: Command string to parse
            operator: The operator that preceded this command

        Returns:
            List of ParsedCommand objects
        """
        cmd_str = cmd_str.strip()
        if not cmd_str:
            return []

        # Control keywords that can be followed by commands inline
        # (after ; separation by the main parser, these may still have commands after them)
        inline_control_keywords = {'do', 'then', 'else', 'elif'}

        tokens = cmd_str.split(None, 1)  # Split on first whitespace only
        if not tokens:
            return []

        first_word = tokens[0]

        if first_word in inline_control_keywords and len(tokens) > 1:
            # Control keyword followed by more content - split them
            rest = tokens[1]
            result = [
                ParsedCommand(
                    command=first_word,
                    arguments='',
                    raw=first_word,
                    operator_before=operator
                )
            ]
            # Recursively parse the rest (might have more control keywords)
            result.extend(self._parse_with_control_keywords(rest, None))
            return result
        else:
            # Not a control keyword with following content, parse normally
            return [self._parse_simple_command(cmd_str, operator)]

    def categorize_command(self, parsed_cmd: ParsedCommand) -> str:
        """
        Categorize a command as 'read', 'write', or 'other'.

        This is a heuristic categorization based on common command patterns.

        Args:
            parsed_cmd: ParsedCommand object

        Returns:
            Category string: 'read', 'write', or 'other'
        """
        cmd = parsed_cmd.command.lower()
        args = parsed_cmd.arguments.lower()

        # Read operations
        read_commands = {
            'cat', 'head', 'tail', 'less', 'more', 'grep', 'find', 'ls', 'stat',
            'file', 'wc', 'diff', 'cmp', 'test', 'command', 'which', 'type',
            'du', 'df', 'mount', 'lsof', 'ps', 'top', 'netstat', 'ss', 'lsblk',
            'jq', 'awk', 'sed', 'cut', 'sort', 'uniq', 'comm', 'paste', 'xxd',
            'pgrep', 'pkill', 'dmesg', 'journalctl', 'fdisk', 'lsusb', 'objdump',
            'nm', 'size', 'objcopy', 'readelf'
        }

        # Git read operations
        if cmd == 'git':
            git_read_subcmds = [
                'status', 'log', 'diff', 'show', 'branch', 'remote', 'describe',
                'rev-parse', 'rev-list', 'cat-file', 'ls-tree', 'ls-files',
                'grep', 'merge-base', 'blame', 'tag'
            ]
            first_arg = args.split()[0] if args else ''
            if first_arg in git_read_subcmds:
                return 'read'
            # Fetch is read-like (network read)
            if first_arg == 'fetch':
                return 'read'
            # Other git commands are write
            return 'write'

        # Check if command is in read list
        if cmd in read_commands:
            # Even read commands can write if they use redirection
            if '>' in args or '>>' in args:
                return 'write'
            return 'read'

        # Write operations
        write_commands = {
            'rm', 'mv', 'cp', 'mkdir', 'rmdir', 'touch', 'chmod', 'chown',
            'ln', 'dd', 'rsync', 'tar', 'unzip', 'zip', 'gzip', 'gunzip',
            'echo', 'printf', 'tee', 'write'
        }

        if cmd in write_commands:
            return 'write'

        # Build/compile operations (other category)
        build_commands = {
            'make', 'cmake', 'gcc', 'g++', 'clang', 'cc', 'ar', 'ld',
            'npm', 'yarn', 'pip', 'pip3', 'python', 'python3', 'node',
            'cargo', 'rustc', 'go', 'javac', 'java', 'mvn', 'gradle',
            'pio', 'platformio'
        }

        if cmd in build_commands:
            return 'other'

        # Default to 'other' for unknown commands
        return 'other'


def parse_bash_command(command: str) -> List[ParsedCommand]:
    """
    Convenience function to parse a bash command.

    Args:
        command: Bash command string

    Returns:
        List of ParsedCommand objects
    """
    parser = BashCommandParser()
    return parser.parse(command)


if __name__ == '__main__':
    # Test the parser
    import json

    test_commands = [
        "git status",
        "git add . && git commit -m 'message' && git push",
        "ls -la | grep foo",
        "make clean && make all",
        "cat file.txt > output.txt",
        "for i in 1 2 3; do echo $i; done",
        "if test -f foo; then rm foo; fi",
    ]

    parser = BashCommandParser()

    for cmd in test_commands:
        print(f"\n{'='*60}")
        print(f"Command: {cmd}")
        print(f"{'='*60}")

        parsed = parser.parse(cmd)
        for i, p in enumerate(parsed):
            print(f"\nSubcommand {i+1}:")
            print(f"  Operator before: {p.operator_before}")
            print(f"  Command: {p.command}")
            print(f"  Arguments: {p.arguments}")
            print(f"  Category: {parser.categorize_command(p)}")
            print(f"  Raw: {p.raw}")
