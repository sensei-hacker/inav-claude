#!/usr/bin/env python3
"""
Detect dead code by checking which #if/#elif/#else branches are never taken.

Strategy:
1. Parse conditional directives (#if/#elif/#else) in source
2. For each target, run gcc -E and see which branches produce output
3. Mark branches that are NEVER taken by any target as dead code
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TARGET_GROUPS = {
    "DYSF4": ["DYSF4PRO", "DYSF4PROV2"],
    "OMNIBUSF4": ["OMNIBUSF4"],
    "OMNIBUSF4PRO": ["OMNIBUSF4PRO", "OMNIBUSF4V3", "OMNIBUSF4V3_ICM"],
    "OMNIBUSF4V3_SS": ["OMNIBUSF4V3_S6_SS", "OMNIBUSF4V3_S5S6_SS", "OMNIBUSF4V3_S5_S6_2SS"],
}

def run_preprocessor(target_name, source_file, inav_root):
    """Run gcc -E via a wrapper .c file to avoid #pragma once issues."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as tmp:
        # Create wrapper that includes the target file
        tmp.write(f'#include "{source_file}"\n')
        tmp_path = tmp.name
    
    try:
        gcc_cmd = [
            "arm-none-eabi-gcc", "-E",
            f"-D{target_name}",
            "-DSTM32F405xx",
            f"-I{inav_root}",
            f"-I{inav_root}/lib/main/STM32F4/Drivers/CMSIS/Device/ST/STM32F4xx/Include",
            f"-I{inav_root}/lib/main/STM32F4/Drivers/CMSIS/Include",
            tmp_path
        ]
        
        result = subprocess.run(gcc_cmd, capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        print(f"Error preprocessing {target_name}: {e}", file=sys.stderr)
        return None
    finally:
        os.unlink(tmp_path)

def find_conditional_blocks(source_file):
    """
    Find all conditional blocks (#if/#elif/#else) and their line ranges.
    Returns list of {type, line_start, line_end, condition}
    """
    blocks = []
    
    with open(source_file, 'r') as f:
        lines = f.readlines()
    
    stack = []  # Stack of {type, line_num, condition}
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if re.match(r'^\s*#\s*if\b', stripped):
            # Start of new conditional block
            stack.append({
                'type': 'if',
                'line': line_num,
                'condition': stripped,
                'branches': []
            })
        elif re.match(r'^\s*#\s*elif\b', stripped) and stack:
            # New branch in current conditional
            # Close previous branch
            if stack[-1]['branches']:
                stack[-1]['branches'][-1]['end'] = line_num - 1
            # Start new branch
            stack[-1]['branches'].append({
                'type': 'elif',
                'start': line_num,
                'end': None,
                'condition': stripped
            })
        elif re.match(r'^\s*#\s*else\b', stripped) and stack:
            # Else branch
            if stack[-1]['branches']:
                stack[-1]['branches'][-1]['end'] = line_num - 1
            stack[-1]['branches'].append({
                'type': 'else',
                'start': line_num,
                'end': None,
                'condition': stripped
            })
        elif re.match(r'^\s*#\s*endif\b', stripped) and stack:
            # End of conditional block
            block = stack.pop()
            if block['branches']:
                block['branches'][-1]['end'] = line_num - 1
            blocks.append(block)
    
    return blocks

def check_branch_used(branch, preprocessed_output, source_filename):
    """
    Check if a branch appears in preprocessed output.
    
    Look for line markers showing we're in that range of source file.
    """
    for line in preprocessed_output.split('\n'):
        match = re.match(r'^#\s+(\d+)\s+"([^"]+)"', line)
        if match:
            line_num = int(match.group(1))
            filename = match.group(2)
            
            if os.path.basename(filename) == source_filename:
                if branch['start'] <= line_num <= (branch['end'] or branch['start']):
                    return True
    
    return False

def check_file(source_file, directory_name, targets, inav_root):
    """Check a file for dead conditional branches."""
    source_filename = os.path.basename(source_file)
    
    # Find all conditional blocks in source
    blocks = find_conditional_blocks(source_file)
    
    if not blocks:
        return []
    
    print(f"  Analyzing {source_filename}: found {len(blocks)} conditional blocks...", end="")
    
    # For each target, get preprocessed output
    preprocessed_outputs = {}
    for target in targets:
        output = run_preprocessor(target, source_file, inav_root)
        if output:
            preprocessed_outputs[target] = output
    
    # Check each branch to see if it was used by ANY target
    dead_branches = []
    
    for block in blocks:
        for branch in block.get('branches', []):
            used_by_any = False
            
            for target, output in preprocessed_outputs.items():
                if check_branch_used(branch, output, source_filename):
                    used_by_any = True
                    break
            
            if not used_by_any and branch['type'] == 'else':
                # This #else branch was never taken
                dead_branches.append(branch)
    
    print(f" done")
    return dead_branches

def main():
    inav_root = Path(__file__).resolve().parents[3] / "inav"
    target_dir = inav_root / "src" / "main" / "target"
    
    print("=== Dead Code Detection (Conditional Branches) ===\n")
    
    found_dead = False
    
    for dir_name, targets in TARGET_GROUPS.items():
        dir_path = target_dir / dir_name
        
        if not dir_path.exists():
            continue
        
        print(f"{dir_name}/ ({len(targets)} targets)")
        
        dir_dead = False
        
        for filename in ['target.h', 'target.c']:
            file_path = dir_path / filename
            if not file_path.exists():
                continue
            
            dead_branches = check_file(file_path, dir_name, targets, inav_root)
            
            if dead_branches:
                dir_dead = True
                found_dead = True
                print(f"\n  ❌ {filename}: {len(dead_branches)} dead #else branch(es):")
                for branch in dead_branches:
                    print(f"    Line {branch['start']}: {branch['condition']}")
                    with open(file_path) as f:
                        lines = f.readlines()
                        if branch['end']:
                            print(f"      (lines {branch['start']}-{branch['end']})")
                print()
        
        if not dir_dead:
            print(f"  ✅ No dead branches\n")
    
    print("=" * 70)
    if found_dead:
        print("❌ Dead code branches found")
        return 1
    else:
        print("✅ No dead code detected")
        return 0

if __name__ == "__main__":
    sys.exit(main())
