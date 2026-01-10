#!/usr/bin/env python3
"""
Common functionality for Claude Code hooks.

Provides configuration loading, rule matching, logging, and output generation
for PreToolUse and PermissionRequest hooks.
"""

import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import yaml

from bash_parser import BashCommandParser, ParsedCommand


class HookConfig:
    """Manages hook configuration."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize hook configuration.

        Args:
            config_path: Path to YAML config file. If None, searches default locations.
        """
        self.config = self._load_config(config_path)
        self.bash_parser = BashCommandParser()

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        # Search order for config file
        search_paths = []

        if config_path:
            search_paths.append(config_path)

        # Default locations
        # Start with absolute path to project config
        hook_dir = os.path.dirname(os.path.abspath(__file__))
        project_config = os.path.join(hook_dir, "tool_permissions.yaml")

        search_paths.extend([
            project_config,  # Absolute path to project config (always checked first)
            os.path.expanduser("~/.claude/hooks/tool_permissions.yaml"),
            os.path.expanduser("~/.config/claude/tool_permissions.yaml"),
            "./tool_permissions.yaml",  # Same directory as the hook script
            "./.claude/hooks/tool_permissions.yaml",  # From project root
            "../../.claude/hooks/tool_permissions.yaml",  # From hooks directory
        ])

        for path in search_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                with open(expanded_path, 'r') as f:
                    return yaml.safe_load(f) or {}

        # Return default config if no file found
        return {
            'defaults': {
                'read': 'allow',
                'write': 'ask',
                'other': 'ask'
            },
            'rules': [],
            'bash_rules': [],
            'logging': {
                'enabled': True,
                'log_file': '~/.claude/hooks/tool_permissions.log',
                'log_inputs': True,
                'log_outputs': True,
            }
        }

    def get_default_decision(self, category: str) -> str:
        """Get default decision for a category."""
        defaults = self.config.get('defaults', {})
        return defaults.get(category, 'ask')

    def get_rules(self) -> List[Dict[str, Any]]:
        """Get general tool rules."""
        return self.config.get('rules', [])

    def get_bash_rules(self) -> List[Dict[str, Any]]:
        """Get Bash-specific rules."""
        return self.config.get('bash_rules', [])

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.config.get('logging', {
            'enabled': True,
            'log_file': '~/.claude/hooks/hook.log',
            'log_inputs': True,
            'log_outputs': True,
        })


class HookLogger:
    """Manages hook logging."""

    def __init__(self, config: HookConfig):
        """
        Initialize hook logger.

        Args:
            config: HookConfig object
        """
        self.config = config
        log_config = config.get_logging_config()

        self.enabled = log_config.get('enabled', True)
        self.log_inputs = log_config.get('log_inputs', True)
        self.log_outputs = log_config.get('log_outputs', True)

        if self.enabled:
            log_file = os.path.expanduser(log_config.get('log_file', '~/.claude/hooks/tool_permissions.log'))
            log_dir = os.path.dirname(log_file)
            os.makedirs(log_dir, exist_ok=True)

            # Rotate log if needed
            max_log_size_kb = log_config.get('max_log_size_kb', 200)
            self._rotate_log_if_needed(log_file, max_log_size_kb)

            # Set up logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file),
                ]
            )
            self.logger = logging.getLogger('hook')
        else:
            self.logger = None

    def _rotate_log_if_needed(self, log_file: str, max_size_kb: int):
        """
        Rotate log file if it exceeds max size.

        Moves current log to log_file.1, overwriting any existing .1 file.

        Args:
            log_file: Path to log file
            max_size_kb: Maximum log size in kilobytes
        """
        if not os.path.exists(log_file):
            return

        # Check file size
        file_size_kb = os.path.getsize(log_file) / 1024

        if file_size_kb >= max_size_kb:
            backup_file = f"{log_file}.1"
            # Remove old backup if it exists
            if os.path.exists(backup_file):
                os.remove(backup_file)
            # Move current log to backup
            os.rename(log_file, backup_file)

    def log(self, message: str, level: str = 'info'):
        """Log a message."""
        if not self.enabled or not self.logger:
            return

        level_fn = getattr(self.logger, level.lower(), self.logger.info)
        level_fn(message)

    def log_input(self, hook_event: str, input_data: Dict[str, Any]):
        """Log hook input."""
        if not self.log_inputs:
            return

        tool_name = input_data.get('tool_name', 'unknown')
        self.log(f"[{hook_event}] Tool: {tool_name}")

        if tool_name == 'Bash':
            command = input_data.get('tool_input', {}).get('command', '')
            self.log(f"  Command: {command}")
        else:
            tool_input = input_data.get('tool_input', {})
            self.log(f"  Input: {json.dumps(tool_input, indent=2)}")

    def log_output(self, decision: str, reason: Optional[str] = None, rule_name: Optional[str] = None):
        """Log hook output decision."""
        if not self.log_outputs:
            return

        msg = f"  Decision: {decision}"
        if rule_name:
            msg += f" (matched rule: {rule_name})"
        if reason:
            msg += f" - {reason}"

        self.log(msg)


class RuleMatcher:
    """Matches tool calls against configured rules."""

    def __init__(self, config: HookConfig, logger: HookLogger):
        """
        Initialize rule matcher.

        Args:
            config: HookConfig object
            logger: HookLogger object
        """
        self.config = config
        self.logger = logger
        self.bash_parser = BashCommandParser()

    def match_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Match a tool call against general rules.

        Args:
            tool_name: Name of the tool being called
            tool_input: Tool input parameters

        Returns:
            Tuple of (decision, message, rule_name)
            decision is "allow", "deny", "ask", or None (use category default)
        """
        rules = self.config.get_rules()

        for rule in rules:
            if self._matches_rule(tool_name, tool_input, rule):
                decision = rule.get('decision')
                message = rule.get('message')
                rule_name = rule.get('name', 'unnamed')

                # If no decision specified, use category default
                if not decision:
                    category = rule.get('category', 'other')
                    decision = self.config.get_default_decision(category)

                return decision, message, rule_name

        # No rule matched, use category default
        return None, None, None

    def match_bash(self, command: str, cwd: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Match a Bash command against Bash-specific rules.

        Parses the command into subcommands and matches each against rules.

        Args:
            command: Bash command string

        Returns:
            List of dicts with keys: subcommand, decision, message, rule_name, category
        """
        parsed_cmds = self.bash_parser.parse(command)
        bash_rules = self.config.get_bash_rules()
        results = []

        for parsed_cmd in parsed_cmds:
            matched = False

            for rule in bash_rules:
                if self._matches_bash_rule(parsed_cmd, rule):
                    # Check if rule has a precondition script
                    precondition_script = rule.get('precondition_script')

                    if precondition_script:
                        # Evaluate precondition - it returns a decision directly
                        precondition_result = self._evaluate_precondition(parsed_cmd, precondition_script, cwd)

                        if precondition_result:
                            # Precondition returned a valid decision, use it
                            decision = precondition_result
                            message = rule.get('message')
                            rule_name = rule.get('name', 'unnamed')
                            category = rule.get('category', 'other')

                            results.append({
                                'subcommand': parsed_cmd.raw,
                                'parsed_command': parsed_cmd.command,
                                'decision': decision,
                                'message': message,
                                'rule_name': f"{rule_name} (precondition: {decision})",
                                'category': category
                            })
                            matched = True
                            break
                        else:
                            # Precondition failed/errored, skip this rule and try next
                            continue

                    # No precondition or precondition not used, apply rule normally
                    decision = rule.get('decision')
                    message = rule.get('message')
                    rule_name = rule.get('name', 'unnamed')
                    category = rule.get('category', 'other')

                    # If no decision specified, use category default
                    if not decision:
                        decision = self.config.get_default_decision(category)

                    results.append({
                        'subcommand': parsed_cmd.raw,
                        'parsed_command': parsed_cmd.command,
                        'decision': decision,
                        'message': message,
                        'rule_name': rule_name,
                        'category': category
                    })
                    matched = True
                    break

            if not matched:
                # No rule matched, use category default
                category = self.bash_parser.categorize_command(parsed_cmd)
                decision = self.config.get_default_decision(category)

                results.append({
                    'subcommand': parsed_cmd.raw,
                    'parsed_command': parsed_cmd.command,
                    'decision': decision,
                    'message': None,
                    'rule_name': None,
                    'category': category
                })

        return results

    def _matches_rule(self, tool_name: str, tool_input: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Check if a tool call matches a rule."""
        # Check tool name pattern
        tool_name_pattern = rule.get('tool_name_pattern')
        if tool_name_pattern and not re.match(tool_name_pattern, tool_name):
            return False

        # Check tool input patterns
        tool_input_patterns = rule.get('tool_input_patterns', {})
        for field, pattern in tool_input_patterns.items():
            field_value = str(tool_input.get(field, ''))
            if not re.search(pattern, field_value):
                return False

        return True

    def _matches_bash_rule(self, parsed_cmd: ParsedCommand, rule: Dict[str, Any]) -> bool:
        """Check if a parsed bash command matches a rule."""
        # Check command pattern
        command_pattern = rule.get('command_pattern')
        if command_pattern and not re.match(command_pattern, parsed_cmd.command):
            return False

        # Check argument pattern (optional)
        argument_pattern = rule.get('argument_pattern')
        if argument_pattern and not re.search(argument_pattern, parsed_cmd.arguments):
            return False

        return True

    def _evaluate_precondition(self, parsed_cmd: ParsedCommand, precondition_script: str, cwd: Optional[str] = None) -> Optional[str]:
        """
        Evaluate a bash precondition script.

        Args:
            parsed_cmd: Parsed command
            precondition_script: Bash script to execute
            cwd: Working directory where the tool would execute (for path resolution)

        Returns:
            "allow", "deny", "ask", or None if script fails/returns invalid value
        """
        import subprocess
        import tempfile

        # Substitute variables in the script
        script = precondition_script.replace('{COMMAND}', parsed_cmd.command)
        script = script.replace('{ARGS}', parsed_cmd.arguments)
        script = script.replace('{FULL_COMMAND}', parsed_cmd.raw)

        try:
            # Execute the script in the same working directory as where the tool would run
            result = subprocess.run(
                ['bash', '-c', script],
                capture_output=True,
                text=True,
                timeout=2,  # 2 second timeout for safety
                cwd=cwd  # Run in Claude's working directory
            )

            output = result.stdout.strip().lower()

            # Validate output
            if output in ['allow', 'deny', 'ask']:
                return output
            else:
                self.logger.log(f"Precondition script returned invalid value: {output}", 'warning')
                return None

        except subprocess.TimeoutExpired:
            self.logger.log("Precondition script timed out", 'warning')
            return None
        except Exception as e:
            self.logger.log(f"Precondition script error: {e}", 'error')
            return None


class HookOutputGenerator:
    """Generates hook output JSON."""

    @staticmethod
    def generate_pretooluse_output(
        decision: str,
        reason: Optional[str] = None,
        updated_input: Optional[Dict[str, Any]] = None,
        additional_context: Optional[str] = None,
        system_message: Optional[str] = None,
        continue_processing: bool = True,
        stop_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate PreToolUse hook output.

        Args:
            decision: "allow", "deny", or "ask"
            reason: Reason for the decision
            updated_input: Modified tool input (for "allow" with modifications)
            additional_context: Additional context for Claude
            system_message: Warning message shown to user
            continue_processing: Whether Claude should continue
            stop_reason: Reason for stopping (when continue_processing is False)

        Returns:
            Hook output dict
        """
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": decision
            }
        }

        if reason:
            output["hookSpecificOutput"]["permissionDecisionReason"] = reason

        if updated_input:
            output["hookSpecificOutput"]["updatedInput"] = updated_input

        if additional_context:
            output["additionalContext"] = additional_context

        if system_message:
            output["systemMessage"] = system_message

        if not continue_processing:
            output["continue"] = False
            if stop_reason:
                output["stopReason"] = stop_reason

        return output

    @staticmethod
    def generate_permissionrequest_output(
        behavior: str,
        updated_input: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        interrupt: bool = False,
        system_message: Optional[str] = None,
        continue_processing: bool = True,
        stop_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate PermissionRequest hook output.

        Args:
            behavior: "allow" or "deny"
            updated_input: Modified tool input (for "allow")
            message: Message explaining the decision
            interrupt: Stop Claude (for "deny")
            system_message: Warning message shown to user
            continue_processing: Whether Claude should continue
            stop_reason: Reason for stopping

        Returns:
            Hook output dict
        """
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {
                    "behavior": behavior
                }
            }
        }

        if behavior == "allow" and updated_input:
            output["hookSpecificOutput"]["decision"]["updatedInput"] = updated_input

        if behavior == "deny":
            if message:
                output["hookSpecificOutput"]["decision"]["message"] = message
            if interrupt:
                output["hookSpecificOutput"]["decision"]["interrupt"] = True

        if system_message:
            output["systemMessage"] = system_message

        if not continue_processing:
            output["continue"] = False
            if stop_reason:
                output["stopReason"] = stop_reason

        return output


def read_hook_input() -> Dict[str, Any]:
    """Read hook input from stdin."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse input JSON: {e}"}


def write_hook_output(output: Dict[str, Any]):
    """Write hook output to stdout."""
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    # Test the module
    print("Testing HookConfig...")
    config = HookConfig()
    print(f"Defaults: {config.config.get('defaults')}")
    print(f"Number of rules: {len(config.get_rules())}")
    print(f"Number of bash rules: {len(config.get_bash_rules())}")

    print("\nTesting RuleMatcher with Bash commands...")
    logger = HookLogger(config)
    matcher = RuleMatcher(config, logger)

    test_commands = [
        "git status",
        "git add -A",
        "git push origin master",
        "git push --force",
        "git commit -m 'test'",
        "rm -rf /tmp/test",
    ]

    for cmd in test_commands:
        print(f"\nCommand: {cmd}")
        results = matcher.match_bash(cmd)
        for result in results:
            print(f"  Subcommand: {result['subcommand']}")
            print(f"  Decision: {result['decision']}")
            print(f"  Rule: {result['rule_name']}")
            if result['message']:
                print(f"  Message: {result['message']}")
