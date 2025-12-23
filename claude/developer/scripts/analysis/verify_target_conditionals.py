#!/usr/bin/env python3
"""
Verify that target directories don't contain conditionals for targets
that belong in other directories.
"""

import os
import re
import sys
from pathlib import Path

# Define which targets belong in which directories
TARGET_GROUPS = {
    "DYSF4": ["DYSF4PRO", "DYSF4PROV2"],
    "OMNIBUSF4": ["OMNIBUSF4"],
    "OMNIBUSF4PRO": ["OMNIBUSF4PRO", "OMNIBUSF4V3", "OMNIBUSF4V3_ICM", "OMNIBUSF4PRO_LEDSTRIPM5"],
    "OMNIBUSF4V3_SS": ["OMNIBUSF4V3_S6_SS", "OMNIBUSF4V3_S5S6_SS", "OMNIBUSF4V3_S5_S6_2SS"],
}

# Flatten to get all valid targets
ALL_TARGETS = set()
for targets in TARGET_GROUPS.values():
    ALL_TARGETS.update(targets)

def find_conditional_macros(file_path):
    """
    Find all target macros used in #if/#ifdef/#elif conditionals.
    Returns list of (line_num, macro_name) tuples.
    """
    conditionals = []
    
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            # Match #if, #ifdef, #ifndef, #elif with target macros
            if re.match(r'^\s*#\s*(if|ifdef|ifndef|elif)\b', line):
                # Find all target macros in this line
                for target in ALL_TARGETS:
                    if re.search(r'\b' + re.escape(target) + r'\b', line):
                        conditionals.append((line_num, target, line.strip()))
    
    return conditionals

def check_directory(dir_path, allowed_targets):
    """
    Check a target directory for inappropriate conditionals.
    Returns list of violations.
    """
    violations = []
    
    for filename in ['target.h', 'target.c']:
        file_path = os.path.join(dir_path, filename)
        if not os.path.exists(file_path):
            continue
            
        conditionals = find_conditional_macros(file_path)
        
        for line_num, macro, line_text in conditionals:
            if macro not in allowed_targets:
                violations.append({
                    'file': filename,
                    'line': line_num,
                    'macro': macro,
                    'text': line_text
                })
    
    return violations

def main():
    # Base path
    inav_root = Path(__file__).resolve().parents[3] / "inav"
    target_dir = inav_root / "src" / "main" / "target"
    
    print(f"Checking target directories in: {target_dir}\n")
    
    all_violations = {}
    
    for dir_name, allowed_targets in TARGET_GROUPS.items():
        dir_path = target_dir / dir_name
        
        if not dir_path.exists():
            print(f"⚠️  Directory not found: {dir_name}")
            continue
        
        violations = check_directory(dir_path, set(allowed_targets))
        
        if violations:
            all_violations[dir_name] = violations
        else:
            print(f"✅ {dir_name}/ - No inappropriate conditionals")
    
    # Report violations
    if all_violations:
        print("\n" + "=" * 70)
        print("❌ VIOLATIONS FOUND")
        print("=" * 70)
        
        for dir_name, violations in all_violations.items():
            print(f"\n{dir_name}/:")
            allowed = TARGET_GROUPS[dir_name]
            print(f"  Allowed targets: {', '.join(allowed)}")
            print(f"  Found {len(violations)} inappropriate conditional(s):\n")
            
            for v in violations:
                print(f"  {v['file']}:{v['line']}")
                print(f"    Macro: {v['macro']} (not allowed in this directory)")
                print(f"    Line: {v['text']}")
                print()
        
        return 1
    else:
        print("\n" + "=" * 70)
        print("✅ SUCCESS - All directories are clean")
        print("=" * 70)
        return 0

if __name__ == "__main__":
    sys.exit(main())
