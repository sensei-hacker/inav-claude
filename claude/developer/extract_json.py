#!/usr/bin/env python3
"""
Extract JSON objects from script_versions.txt and pretty-print them.
"""

import json
import sys
import re

def extract_json_from_file(filepath):
    """Extract and pretty-print JSON objects from the file."""
    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            # Skip empty lines
            line = line.strip()
            if not line:
                continue

            # Check if line contains JSON (starts with { after any prefix)
            json_match = re.search(r'(\{.*\})\s*$', line)
            if json_match:
                json_str = json_match.group(1)
                try:
                    data = json.loads(json_str)
                    print(f"\n{'='*60}")
                    print(f"Line {line_num}:")
                    print('='*60)
                    print(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    # Not valid JSON, skip
                    pass
            else:
                # Print non-JSON lines as-is (like file paths)
                if ':' in line and not line.startswith('{'):
                    # Looks like a file reference line
                    print(f"\n--- {line[:100]}..." if len(line) > 100 else f"\n--- {line}")

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'claude/developer/script_versions.txt'
    extract_json_from_file(filepath)
