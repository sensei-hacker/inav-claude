#!/usr/bin/env python3
"""
Detect dead code using gcc -E preprocessor output.

Strategy:
1. For each target in a directory, run gcc -E
2. Extract which source line numbers appear in preprocessed output
3. Union all line numbers across all targets
4. Any source line NOT in union = dead code (never used by any target)
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Target groups
TARGET_GROUPS = {
    "DYSF4": ["DYSF4PRO", "DYSF4PROV2"],
    "OMNIBUSF4": ["OMNIBUSF4"],
    "OMNIBUSF4PRO": ["OMNIBUSF4PRO", "OMNIBUSF4V3", "OMNIBUSF4V3_ICM"],
    "OMNIBUSF4V3_SS": ["OMNIBUSF4V3_S6_SS", "OMNIBUSF4V3_S5S6_SS", "OMNIBUSF4V3_S5_S6_2SS"],
}

def run_preprocessor(target_name, source_file, inav_root):
    """Run gcc -E on a source file with target macro defined."""
    gcc_cmd = [
        "arm-none-eabi-gcc", "-E",
        f"-D{target_name}",
        "-DSTM32F405xx",
        f"-I{inav_root}",
        f"-I{inav_root}/lib/main/STM32F4/Drivers/CMSIS/Device/ST/STM32F4xx/Include",
        f"-I{inav_root}/lib/main/STM32F4/Drivers/CMSIS/Include",
        str(source_file)
    ]
    
    try:
        result = subprocess.run(gcc_cmd, capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        print(f"Error preprocessing {target_name}: {e}", file=sys.stderr)
        return None

def extract_included_lines(preprocessed_output, source_filename):
    """
    Extract source line numbers that appear in preprocessed output.
    
    gcc -E output has line markers like:
    # 129 "target.h"
    
    This tells us that subsequent lines come from source line 129.
    """
    included_lines = set()
    
    for line in preprocessed_output.split('\n'):
        # Match: # <line_num> "filename"
        match = re.match(r'^#\s+(\d+)\s+"([^"]+)"', line)
        if match:
            line_num = int(match.group(1))
            filename = match.group(2)
            
            # Check if this is our source file (basename match)
            if os.path.basename(filename) == source_filename:
                included_lines.add(line_num)
    
    return included_lines

def get_code_lines(source_file):
    """
    Get line numbers of actual code lines (not blank, not pure comments).
    
    We want to identify lines that SHOULD appear in preprocessed output.
    """
    code_lines = {}
    
    with open(source_file, 'r') as f:
        in_block_comment = False
        
        for line_num, line in enumerate(f, 1):
            stripped = line.strip()
            
            # Track block comments
            if '/*' in stripped:
                in_block_comment = True
            if '*/' in stripped:
                in_block_comment = False
                continue
            
            # Skip if in block comment
            if in_block_comment:
                continue
            
            # Skip blank lines
            if not stripped:
                continue
            
            # Skip pure single-line comments
            if stripped.startswith('//'):
                continue
            
            # This is a code line (includes preprocessor directives, which is what we want)
            code_lines[line_num] = line.rstrip()
    
    return code_lines

def check_file(source_file, directory_name, targets, inav_root):
    """Check a file for dead code."""
    source_filename = os.path.basename(source_file)
    
    # Get all code lines from source
    code_lines = get_code_lines(source_file)
    
    # Collect lines included by at least one target
    all_included_lines = set()
    
    print(f"  Preprocessing {source_filename} with {len(targets)} targets...", end="")
    
    for target in targets:
        preprocessed = run_preprocessor(target, source_file, inav_root)
        if preprocessed is None:
            print(f"\n    ⚠️  Failed to preprocess with {target}")
            continue
        
        included = extract_included_lines(preprocessed, source_filename)
        all_included_lines.update(included)
    
    print(f" done")
    
    # Find dead lines
    dead_lines = []
    for line_num in sorted(code_lines.keys()):
        if line_num not in all_included_lines:
            dead_lines.append((line_num, code_lines[line_num]))
    
    return dead_lines

def main():
    inav_root = Path(__file__).resolve().parents[3] / "inav"
    target_dir = inav_root / "src" / "main" / "target"
    
    print("=== Dead Code Detection via Preprocessor ===\n")
    print(f"INAV root: {inav_root}\n")
    
    found_dead_code = False
    
    for dir_name, targets in TARGET_GROUPS.items():
        dir_path = target_dir / dir_name
        
        if not dir_path.exists():
            print(f"⚠️  {dir_name}/ not found, skipping")
            continue
        
        print(f"{dir_name}/ (targets: {', '.join(targets)})")
        
        dir_has_dead_code = False
        
        for filename in ['target.h', 'target.c']:
            file_path = dir_path / filename
            if not file_path.exists():
                continue
            
            dead_lines = check_file(file_path, dir_name, targets, inav_root)
            
            if dead_lines:
                dir_has_dead_code = True
                found_dead_code = True
                print(f"\n  ❌ {filename}: {len(dead_lines)} dead lines found:")
                for line_num, line_text in dead_lines[:10]:  # Show first 10
                    print(f"    Line {line_num}: {line_text}")
                if len(dead_lines) > 10:
                    print(f"    ... and {len(dead_lines) - 10} more")
                print()
        
        if not dir_has_dead_code:
            print(f"  ✅ No dead code detected\n")
    
    print("=" * 70)
    if found_dead_code:
        print("❌ Dead code found in one or more directories")
        print("=" * 70)
        return 1
    else:
        print("✅ No dead code detected")
        print("=" * 70)
        return 0

if __name__ == "__main__":
    sys.exit(main())
