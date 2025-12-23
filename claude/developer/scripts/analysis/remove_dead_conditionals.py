#!/usr/bin/env python3
"""
Remove dead conditional branches from target files.

This script removes #if/#elif/#else branches that reference targets
not in the current directory.
"""

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

def get_allowed_targets(directory_name):
    """Get set of targets allowed in this directory."""
    return set(TARGET_GROUPS.get(directory_name, []))

def simplify_conditional(line, allowed_targets, all_targets):
    """
    Simplify a conditional expression by removing references to disallowed targets.
    
    Strategy:
    1. Remove negative checks for disallowed targets: !(defined(WRONG) || ...)
    2. Remove positive checks for disallowed targets: defined(WRONG) || ...
    3. Clean up resulting boolean expressions
    """
    original = line
    
    # Find all target macros in the line
    found_disallowed = []
    for target in all_targets:
        if target not in allowed_targets:
            if re.search(r'\b' + re.escape(target) + r'\b', line):
                found_disallowed.append(target)
    
    if not found_disallowed:
        return line  # No disallowed targets found
    
    # Remove negative checks: !(defined(WRONG) || defined(WRONG2) || ...)
    # Pattern: && !(defined(X) || defined(Y) || ...)
    pattern = r'\s*&&\s*!\((?:defined\([^)]+\)\s*\|\|\s*)*defined\([^)]+\)\)'
    line = re.sub(pattern, '', line)
    
    # If line still contains disallowed targets, it's probably not safe to auto-fix
    for target in found_disallowed:
        if re.search(r'\b' + re.escape(target) + r'\b', line):
            return None  # Can't safely simplify
    
    # Clean up double spaces
    line = re.sub(r'\s+', ' ', line)
    line = line.rstrip()
    
    return line if line != original else None

def should_keep_branch(condition_line, allowed_targets, all_targets):
    """
    Determine if a conditional branch should be kept.
    Returns: (keep: bool, simplified_line: str or None)
    """
    # Extract target macros from condition
    referenced_targets = set()
    for target in all_targets:
        if re.search(r'\bdefined\s*\(\s*' + re.escape(target) + r'\s*\)', condition_line):
            referenced_targets.add(target)
    
    # If no targets referenced, keep it
    if not referenced_targets:
        return True, None
    
    # If ANY referenced target is allowed, try to keep (may need simplification)
    if referenced_targets & allowed_targets:
        simplified = simplify_conditional(condition_line, allowed_targets, all_targets)
        return True, simplified
    
    # All referenced targets are disallowed - remove this branch
    return False, None

def process_file(file_path, directory_name, dry_run=True):
    """
    Process a file to remove dead conditional branches.
    Returns: (modified_lines, changes_made)
    """
    allowed_targets = get_allowed_targets(directory_name)
    all_targets = set()
    for targets in TARGET_GROUPS.values():
        all_targets.update(targets)
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    output_lines = []
    changes = []
    skip_until = None  # Line number to skip until (for removing blocks)
    i = 0
    
    while i < len(lines):
        line = lines[i]
        line_num = i + 1
        
        # If we're skipping a block, check for endif
        if skip_until:
            if re.match(r'^\s*#\s*endif', line):
                skip_until = None
                # Don't output this #endif (it matches the removed #if)
                changes.append(f"  Removed #endif at line {line_num}")
            i += 1
            continue
        
        # Check for conditional directives
        if re.match(r'^\s*#\s*(if|ifdef|ifndef|elif)', line):
            keep, simplified = should_keep_branch(line, allowed_targets, all_targets)
            
            if not keep:
                # Find the matching #endif and skip the entire block
                depth = 1
                block_start = line_num
                j = i + 1
                while j < len(lines) and depth > 0:
                    if re.match(r'^\s*#\s*if', lines[j]):
                        depth += 1
                    elif re.match(r'^\s*#\s*endif', lines[j]):
                        depth -= 1
                    j += 1
                
                changes.append(f"  Removed dead branch at lines {block_start}-{j}: {line.strip()}")
                i = j  # Skip past #endif
                continue
            elif simplified:
                output_lines.append(simplified + '\n')
                changes.append(f"  Simplified line {line_num}:\n    FROM: {line.rstrip()}\n    TO:   {simplified}")
            else:
                output_lines.append(line)
        else:
            output_lines.append(line)
        
        i += 1
    
    if changes and not dry_run:
        with open(file_path, 'w') as f:
            f.writelines(output_lines)
    
    return output_lines, changes

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Remove dead conditional branches from target files')
    parser.add_argument('--apply', action='store_true', help='Actually modify files (default is dry-run)')
    parser.add_argument('directory', nargs='?', help='Specific directory to process (e.g., OMNIBUSF4PRO)')
    args = parser.parse_args()
    
    inav_root = Path(__file__).resolve().parents[3] / "inav"
    target_dir = inav_root / "src" / "main" / "target"
    
    directories = [args.directory] if args.directory else TARGET_GROUPS.keys()
    
    mode = "APPLYING CHANGES" if args.apply else "DRY RUN (use --apply to modify files)"
    print(f"=== {mode} ===\n")
    
    total_changes = 0
    
    for dir_name in directories:
        dir_path = target_dir / dir_name
        if not dir_path.exists():
            continue
        
        print(f"{dir_name}/:")
        dir_changes = 0
        
        for filename in ['target.h', 'target.c']:
            file_path = dir_path / filename
            if not file_path.exists():
                continue
            
            output_lines, changes = process_file(file_path, dir_name, dry_run=not args.apply)
            
            if changes:
                print(f"  {filename}:")
                for change in changes:
                    print(change)
                dir_changes += len(changes)
        
        if dir_changes == 0:
            print(f"  No changes needed")
        
        total_changes += dir_changes
        print()
    
    if total_changes > 0 and not args.apply:
        print(f"\n⚠️  Found {total_changes} potential changes.")
        print("Run with --apply to actually modify files.")
        return 1
    elif total_changes > 0:
        print(f"✅ Applied {total_changes} changes.")
        return 0
    else:
        print("✅ No changes needed.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
